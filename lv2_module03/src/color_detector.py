# src/color_detector.py
"""HSV 색 검출 — ros2_ws/src/realsense/src/detector.cpp 와 같은 처리 (Python 판).

처리 순서: 왜곡 보정 → BGR→HSV → inRange(범위 1 OR 범위 2) → 열림 → 닫힘
          → 컨투어 → 면적비·종횡비·채움비 필터 → 통과한 것 중 면적 최대 → 모멘트 중심

설정 파일
  HSV·필터: ros2_ws/src/realsense/config/realsense.yaml (perception_node: ros__parameters:)
  내부 파라미터·왜곡: config/camera_info_d435.yaml (camera_calibration_parsers 형식)
"""
from dataclasses import dataclass, field, asdict
from pathlib import Path

import cv2
import numpy as np
import yaml

MODULE_DIR = Path(__file__).resolve().parent.parent          # lv2_module03/
DEFAULT_PARAMS = MODULE_DIR / "ros2_ws/src/realsense/config/realsense.yaml"
DEFAULT_CAMERA_INFO = MODULE_DIR / "config/camera_info_d435.yaml"
NODE = "perception_node"


@dataclass
class DetectorConfig:
    hsv_lower: list = field(default_factory=lambda: [103, 220, 20])   # H 0~179, S·V 0~255
    hsv_upper: list = field(default_factory=lambda: [130, 255, 255])
    hsv_bright_enabled: bool = True
    hsv_bright_lower: list = field(default_factory=lambda: [103, 150, 130])
    hsv_bright_upper: list = field(default_factory=lambda: [130, 255, 255])
    open_kernel: int = 3          # 작은 점 제거 커널(px), 0이면 생략
    close_kernel: int = 5         # 작은 구멍 메우기 커널(px), 0이면 생략
    min_area_ratio: float = 0.0006  # contour_area / (W×H)
    max_area_ratio: float = 0.15
    aspect_max: float = 4.0       # 긴 변 / 짧은 변 (minAreaRect)
    fill_min: float = 0.6         # 컨투어 면적 / 회전 사각형 면적

    @classmethod
    def load(cls, path=DEFAULT_PARAMS, node=NODE):
        params = yaml.safe_load(Path(path).read_text())[node]["ros__parameters"]
        keys = cls.__dataclass_fields__.keys()
        return cls(**{k: v for k, v in params.items() if k in keys})  # 노드 전용 키(토픽 등)는 무시

    def save(self, path, node=NODE):
        """perception_node 파라미터 파일 형식으로 저장 → --params-file 로 바로 쓸 수 있다."""
        Path(path).write_text(yaml.safe_dump(
            {node: {"ros__parameters": asdict(self)}}, sort_keys=False, default_flow_style=None))


@dataclass
class CameraInfo:
    K: np.ndarray       # 3x3 내부 파라미터
    D: np.ndarray       # 왜곡 계수 (plumb_bob: k1 k2 p1 p2 k3)
    width: int
    height: int

    @classmethod
    def load(cls, path=DEFAULT_CAMERA_INFO):
        c = yaml.safe_load(Path(path).read_text())
        return cls(np.array(c["camera_matrix"]["data"], dtype=np.float64).reshape(3, 3),
                   np.array(c["distortion_coefficients"]["data"], dtype=np.float64),
                   c["image_width"], c["image_height"])


class Undistorter:
    """왜곡 보정. 맵을 한 번만 계산해 두고 remap 한다. D가 모두 0이면 입력을 그대로 돌려준다."""

    def __init__(self, info: CameraInfo):
        self.info = info
        self.identity = not np.any(info.D)
        if not self.identity:
            self.map1, self.map2 = cv2.initUndistortRectifyMap(
                info.K, info.D, None, info.K, (info.width, info.height), cv2.CV_16SC2)

    def __call__(self, bgr):
        if self.identity:
            return bgr
        if bgr.shape[1] != self.info.width or bgr.shape[0] != self.info.height:
            raise ValueError(f"영상 {bgr.shape[1]}x{bgr.shape[0]} ≠ 캘리브레이션 "
                             f"{self.info.width}x{self.info.height}")
        return cv2.remap(bgr, self.map1, self.map2, cv2.INTER_LINEAR)


def make_mask(bgr, cfg: DetectorConfig):
    hsv = cv2.cvtColor(bgr, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv, np.array(cfg.hsv_lower), np.array(cfg.hsv_upper))
    if cfg.hsv_bright_enabled:
        mask |= cv2.inRange(hsv, np.array(cfg.hsv_bright_lower), np.array(cfg.hsv_bright_upper))
    if cfg.open_kernel > 0:
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, np.ones((cfg.open_kernel,) * 2, np.uint8))
    if cfg.close_kernel > 0:
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, np.ones((cfg.close_kernel,) * 2, np.uint8))
    return mask


def detect(bgr, cfg: DetectorConfig, mask=None):
    """반환: dict(detected, cx, cy, ex, ey, area_px, area_ratio, bbox, aspect, fill, candidates)."""
    h, w = bgr.shape[:2]
    frame_area = float(w * h)
    if mask is None:
        mask = make_mask(bgr, cfg)
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    candidates = []
    for c in contours:
        area = cv2.contourArea(c)
        if area < 20:                          # 점 수준 잡음은 후보에서도 뺀다
            continue
        (_, _), (rw, rh), _ = cv2.minAreaRect(c)
        short, long_ = min(rw, rh), max(rw, rh)
        aspect = long_ / short if short > 0 else float("inf")
        fill = area / (rw * rh) if rw * rh > 0 else 0.0
        ratio = area / frame_area
        if ratio < cfg.min_area_ratio:
            reason = "small"
        elif ratio > cfg.max_area_ratio:
            reason = "large"
        elif aspect > cfg.aspect_max:
            reason = "aspect"
        elif fill < cfg.fill_min:
            reason = "fill"
        else:
            reason = "ok"
        candidates.append({"contour": c, "area_px": area, "aspect": aspect, "fill": fill,
                           "reason": reason})

    result = {"detected": False, "width": w, "height": h, "candidates": candidates}
    ok = [c for c in candidates if c["reason"] == "ok"]
    if not ok:
        return result
    sel = max(ok, key=lambda c: c["area_px"])  # 동률이면 먼저 찾은 것 (max는 첫 최댓값)
    m = cv2.moments(sel["contour"])
    if m["m00"] == 0:
        return result
    cx, cy = m["m10"] / m["m00"], m["m01"] / m["m00"]
    result.update(detected=True, selected=sel, cx=cx, cy=cy,
                  ex=(cx - w / 2) / (w / 2), ey=(cy - h / 2) / (h / 2),
                  area_px=sel["area_px"], area_ratio=sel["area_px"] / frame_area,
                  bbox=cv2.boundingRect(sel["contour"]), aspect=sel["aspect"], fill=sel["fill"])
    return result


def draw(bgr, r):
    out = bgr.copy()
    for c in r["candidates"]:
        color = (0, 255, 0) if c["reason"] == "ok" else (0, 0, 255)
        cv2.drawContours(out, [c["contour"]], -1, color, 1)
    if r["detected"]:
        x, y, w, h = r["bbox"]
        cv2.rectangle(out, (x, y), (x + w, y + h), (0, 255, 0), 2)
        cv2.circle(out, (int(r["cx"]), int(r["cy"])), 5, (0, 255, 255), -1)
        cv2.putText(out, f"e=({r['ex']:+.2f},{r['ey']:+.2f}) a={r['area_ratio']:.4f}",
                    (x, max(y - 6, 12)), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 1)
    return out
