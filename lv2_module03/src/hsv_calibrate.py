# src/hsv_calibrate.py
"""HSV 범위 보정 도구 — 트랙바로 범위를 조정하고, 드래그한 영역의 HSV 분포를 측정해 저장한다.

실행 (lv2_module03/ 에서)
  python3 src/hsv_calibrate.py                     # 카메라 0번
  python3 src/hsv_calibrate.py --source 4          # 다른 카메라 번호
  python3 src/hsv_calibrate.py --source ros2_ws/src/realsense/test/data/lit_pillar_20261002.png

조작
  마우스 드래그   목표 영역 선택 → H/S/V 5~95 백분위 출력 (realsense.yaml 주석과 같은 측정법)
  a              선택 영역 백분위로 범위 1을 맞춘다
  s              config/realsense_<--name>.yaml 로 저장 (perception_node --params-file 형식)
  space          일시정지 / 재개 (카메라·영상)
  q / ESC        종료
"""
import argparse
import time
from pathlib import Path

import cv2
import numpy as np

from color_detector import (DEFAULT_CAMERA_INFO, DEFAULT_PARAMS, MODULE_DIR, CameraInfo,
                            DetectorConfig, Undistorter, detect, draw, make_mask)

WIN = "hsv_calibrate"
CTRL = "hsv_calibrate controls"
# (트랙바 이름, 최댓값, 설정 필드, 인덱스) — 인덱스 None 은 스칼라 필드
BARS = [
    ("H lo", 179, "hsv_lower", 0), ("H hi", 179, "hsv_upper", 0),
    ("S lo", 255, "hsv_lower", 1), ("S hi", 255, "hsv_upper", 1),
    ("V lo", 255, "hsv_lower", 2), ("V hi", 255, "hsv_upper", 2),
    ("bright on", 1, "hsv_bright_enabled", None),
    ("bH lo", 179, "hsv_bright_lower", 0), ("bH hi", 179, "hsv_bright_upper", 0),
    ("bS lo", 255, "hsv_bright_lower", 1), ("bS hi", 255, "hsv_bright_upper", 1),
    ("bV lo", 255, "hsv_bright_lower", 2), ("bV hi", 255, "hsv_bright_upper", 2),
    ("open k", 15, "open_kernel", None), ("close k", 15, "close_kernel", None),
]


def get_field(cfg, name, idx):
    v = getattr(cfg, name)
    return int(v if idx is None else v[idx])


def set_field(cfg, name, idx, value):
    if idx is None:
        setattr(cfg, name, bool(value) if name == "hsv_bright_enabled" else value)
    else:
        getattr(cfg, name)[idx] = value


def hsv_percentiles(bgr, roi):
    x0, y0, x1, y1 = roi
    hsv = cv2.cvtColor(bgr[y0:y1, x0:x1], cv2.COLOR_BGR2HSV).reshape(-1, 3)
    lo, hi = np.percentile(hsv, 5, axis=0).astype(int), np.percentile(hsv, 95, axis=0).astype(int)
    return lo.tolist(), hi.tolist()


def open_source(src):
    if src.isdigit():
        cap = cv2.VideoCapture(int(src))
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        return cap, None
    if Path(src).suffix.lower() in (".png", ".jpg", ".jpeg", ".bmp"):
        img = cv2.imread(src)
        if img is None:
            raise SystemExit(f"이미지를 읽을 수 없다: {src}")
        return None, img
    return cv2.VideoCapture(src), None


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawTextHelpFormatter)
    ap.add_argument("--source", default="0", help="카메라 번호, 영상 파일 또는 이미지 파일")
    ap.add_argument("--params", default=str(DEFAULT_PARAMS), help="시작 HSV·필터 설정")
    ap.add_argument("--camera-info", default=str(DEFAULT_CAMERA_INFO), help="내부 파라미터·왜곡")
    ap.add_argument("--name", default="tuned", help="저장 파일 이름: config/realsense_<name>.yaml")
    args = ap.parse_args()

    cfg = DetectorConfig.load(args.params)
    undistort = Undistorter(CameraInfo.load(args.camera_info))
    cap, still = open_source(args.source)

    cv2.namedWindow(WIN)
    cv2.namedWindow(CTRL, cv2.WINDOW_NORMAL)
    for name, mx, f, i in BARS:
        def on_change(v, f=f, i=i):
            set_field(cfg, f, i, v)
        cv2.createTrackbar(name, CTRL, get_field(cfg, f, i), mx, on_change)

    drag = {"start": None, "roi": None}

    def on_mouse(event, x, y, flags, _):
        if event == cv2.EVENT_LBUTTONDOWN:
            drag["start"], drag["roi"] = (x, y), None
        elif event == cv2.EVENT_LBUTTONUP and drag["start"]:
            (x0, y0), drag["start"] = drag["start"], None
            x0, x1, y0, y1 = min(x0, x), max(x0, x), min(y0, y), max(y0, y)
            if x1 - x0 >= 2 and y1 - y0 >= 2:
                drag["roi"], drag["new"] = (x0, y0, x1, y1), True
    cv2.setMouseCallback(WIN, on_mouse)

    paused, frame, t0, n, fps = False, None, time.time(), 0, 0.0
    while True:
        if still is not None:
            frame = still
        elif not paused or frame is None:
            ok, raw = cap.read()
            if not ok:
                break
            frame = raw
            n += 1
            if time.time() - t0 >= 1.0:
                fps, t0, n = n / (time.time() - t0), time.time(), 0
        img = undistort(frame)

        mask = make_mask(img, cfg)
        r = detect(img, cfg, mask)
        vis = draw(img, r)
        if drag["roi"]:
            x0, y0, x1, y1 = drag["roi"]
            cv2.rectangle(vis, (x0, y0), (x1, y1), (255, 255, 0), 1)
        status = f"{'DETECTED' if r['detected'] else 'none'}  fps {fps:.1f}"
        cv2.putText(vis, status, (8, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        cv2.imshow(WIN, np.hstack([vis, cv2.cvtColor(mask, cv2.COLOR_GRAY2BGR)]))

        if drag.pop("new", False):
            lo, hi = hsv_percentiles(img, drag["roi"])
            print(f"ROI {drag['roi']}  H {lo[0]}~{hi[0]} / S {lo[1]}~{hi[1]} / V {lo[2]}~{hi[2]}"
                  " (5~95 백분위)")

        key = cv2.waitKey(30 if still is not None else 1) & 0xFF
        if key == ord("a") and drag["roi"]:
            lo, hi = hsv_percentiles(img, drag["roi"])
            cfg.hsv_lower, cfg.hsv_upper = lo, hi
            for name, _, f, i in BARS:
                cv2.setTrackbarPos(name, CTRL, get_field(cfg, f, i))
            print(f"범위 1 ← {lo} ~ {hi}")
        elif key == ord("s"):
            out = MODULE_DIR / "config" / f"realsense_{args.name}.yaml"
            cfg.save(out)
            print(f"저장: {out}")
        elif key == ord(" "):
            paused = not paused
        elif key in (ord("q"), 27):
            break

    if cap is not None:
        cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
