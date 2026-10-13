# src/replay_bag.py
"""녹화된 bag을 다시 처리해 검출 화면, 보정 오차, 연동 로그를 만든다.

입력 bag 토픽: /camera/camera/color/image_raw, /target, /tracking_status, /motor_cmd
  /target (PointStamped): x = ex, y = ey (-1~+1), z = area_ratio, header = 원본 영상 시각

출력 (lv2_module03/ 기준)
  data/frames/<bag>/            대표 입력 프레임 (보정용 원본, BGR PNG)
  results/detection/<bag>/      검출 화면 (원본 | 마스크, 후보 contour, bbox, 중심)
  results/calibration_error/<bag>.csv   프레임별 Python 검출 vs 녹화된 /target 오차
  results/logs/<bag>_link.log   영상 -> /target -> /tracking_status -> /motor_cmd 시간순 연동 로그
  results/summary.csv           bag별 요약 (한 줄씩 갱신)

실행
  source /opt/ros/lyrical/setup.bash
  python3 src/replay_bag.py <bag 폴더> [--params config/realsense_tuned.yaml] [--every 30]
"""
import argparse
import csv
import math
from pathlib import Path

import cv2
import numpy as np
import rosbag2_py
from rclpy.serialization import deserialize_message
from rosidl_runtime_py.utilities import get_message

from color_detector import (DEFAULT_CAMERA_INFO, DEFAULT_PARAMS, MODULE_DIR, CameraInfo,
                            DetectorConfig, Undistorter, detect, draw, make_mask)

IMAGE = "/camera/camera/color/image_raw"
TARGET = "/target"
STATUS = "/tracking_status"
MOTOR = "/motor_cmd"


def stamp_ns(header):
    return header.stamp.sec * 1_000_000_000 + header.stamp.nanosec


def to_bgr(msg):
    img = np.frombuffer(msg.data, np.uint8).reshape(msg.height, msg.step)[:, : msg.width * 3]
    img = img.reshape(msg.height, msg.width, 3)
    if msg.encoding == "rgb8":
        return cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
    if msg.encoding == "bgr8":
        return img.copy()
    raise ValueError(f"지원하지 않는 encoding: {msg.encoding}")


def read_bag(path):
    reader = rosbag2_py.SequentialReader()
    reader.open(rosbag2_py.StorageOptions(uri=str(path), storage_id="mcap"),
                rosbag2_py.ConverterOptions("cdr", "cdr"))
    types = {t.name: get_message(t.type) for t in reader.get_all_topics_and_types()}
    while reader.has_next():
        topic, data, t = reader.read_next()
        if topic in types:
            yield topic, deserialize_message(data, types[topic]), t


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawTextHelpFormatter)
    ap.add_argument("bag")
    ap.add_argument("--params", default=str(DEFAULT_PARAMS))
    ap.add_argument("--camera-info", default=str(DEFAULT_CAMERA_INFO))
    ap.add_argument("--every", type=int, default=30, help="검출 화면 저장 간격(프레임)")
    ap.add_argument("--frames", type=int, default=5, help="data/frames 에 남길 입력 프레임 수")
    args = ap.parse_args()

    bag = Path(args.bag).resolve()
    name = bag.name
    cfg = DetectorConfig.load(args.params)
    undistort = Undistorter(CameraInfo.load(args.camera_info))

    det_dir = MODULE_DIR / "results/detection" / name
    frame_dir = MODULE_DIR / "data/frames" / name
    err_dir = MODULE_DIR / "results/calibration_error"
    log_dir = MODULE_DIR / "results/logs"
    for d in (det_dir, frame_dir, err_dir, log_dir):
        d.mkdir(parents=True, exist_ok=True)

    # 1) bag 전체를 읽어 토픽별로 모은다 (bag 하나는 수백 프레임 수준이라 메모리에 충분)
    images, targets, events = [], {}, []
    for topic, msg, t in read_bag(bag):
        if topic == IMAGE:
            images.append((t, msg))
        elif topic == TARGET:
            targets[stamp_ns(msg.header)] = (t, msg)
        if topic in (IMAGE, TARGET, STATUS, MOTOR):
            events.append((t, topic, msg))
    if not images:
        raise SystemExit(f"{bag}: {IMAGE} 메시지가 없다")
    t_first = events[0][0]

    # 2) 프레임별 재검출 + 녹화된 /target 과 비교
    rows = []
    save_idx = set(np.linspace(0, len(images) - 1, args.frames, dtype=int).tolist())
    prev_detected = None
    for i, (t, msg) in enumerate(images):
        bgr = undistort(to_bgr(msg))
        mask = make_mask(bgr, cfg)
        r = detect(bgr, cfg, mask)
        w, h = r["width"], r["height"]
        rec = targets.get(stamp_ns(msg.header))
        row = {"frame": i, "time_s": f"{(t - t_first) / 1e9:.3f}",
               "py_detected": int(r["detected"]),
               "py_cx": f"{r['cx']:.2f}" if r["detected"] else "",
               "py_cy": f"{r['cy']:.2f}" if r["detected"] else "",
               "py_area_ratio": f"{r['area_ratio']:.5f}" if r["detected"] else "0"}
        if rec is not None:
            p = rec[1].point
            node_detected = p.z > 0
            row.update(node_detected=int(node_detected),
                       node_cx=f"{w / 2 + p.x * w / 2:.2f}" if node_detected else "",
                       node_cy=f"{h / 2 + p.y * h / 2:.2f}" if node_detected else "",
                       node_latency_ms=f"{(rec[0] - t) / 1e6:.1f}")
            if node_detected and r["detected"]:
                dx = r["cx"] - (w / 2 + p.x * w / 2)
                dy = r["cy"] - (h / 2 + p.y * h / 2)
                row.update(err_x_px=f"{dx:.2f}", err_y_px=f"{dy:.2f}",
                           err_px=f"{math.hypot(dx, dy):.2f}",
                           err_area_ratio=f"{r['area_ratio'] - p.z:.5f}")
        rows.append(row)

        if i in save_idx:
            cv2.imwrite(str(frame_dir / f"{name}_{i:04d}.png"), bgr)
        changed = prev_detected is not None and prev_detected != r["detected"]
        if i % args.every == 0 or changed:
            vis = draw(bgr, r)
            label = f"{name} #{i} t={row['time_s']}s {'DETECTED' if r['detected'] else 'LOST'}"
            cv2.putText(vis, label, (8, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (255, 255, 255), 2)
            out = np.hstack([vis, cv2.cvtColor(mask, cv2.COLOR_GRAY2BGR)])
            tag = "_change" if changed else ""
            cv2.imwrite(str(det_dir / f"{i:04d}{tag}.jpg"), out, [cv2.IMWRITE_JPEG_QUALITY, 85])
        prev_detected = r["detected"]

    fields = ["frame", "time_s", "py_detected", "py_cx", "py_cy", "py_area_ratio",
              "node_detected", "node_cx", "node_cy", "node_latency_ms",
              "err_x_px", "err_y_px", "err_px", "err_area_ratio"]
    with open(err_dir / f"{name}.csv", "w", newline="") as f:
        wr = csv.DictWriter(f, fieldnames=fields)
        wr.writeheader()
        wr.writerows(rows)

    # 3) 연동 로그: 영상 -> /target -> /tracking_status -> /motor_cmd 시간순
    with open(log_dir / f"{name}_link.log", "w") as f:
        f.write(f"# bag: {name}  (시간 = bag 기록 시각 기준 초)\n")
        f.write("# image: 원본 영상 stamp | target: ex ey area | status: 상태 | motor: 이름=변화량(rad)\n")
        for t, topic, msg in events:
            ts = f"{(t - t_first) / 1e9:9.3f}"
            if topic == IMAGE:
                f.write(f"{ts} image   stamp={stamp_ns(msg.header) / 1e9:.3f} "
                        f"{msg.width}x{msg.height} {msg.encoding}\n")
            elif topic == TARGET:
                p = msg.point
                f.write(f"{ts} target  stamp={stamp_ns(msg.header) / 1e9:.3f} "
                        f"ex={p.x:+.3f} ey={p.y:+.3f} area={p.z:.4f}\n")
            elif topic == STATUS:
                f.write(f"{ts} status  {msg.data}\n")
            elif topic == MOTOR:
                cmd = " ".join(f"{n}={v:+.4f}" for n, v in zip(msg.name, msg.position))
                f.write(f"{ts} motor   {cmd}\n")

    # 4) 요약
    n = len(rows)
    paired = [r for r in rows if "node_detected" in r]
    both = [r for r in rows if "err_px" in r]
    agree = sum(r["py_detected"] == r["node_detected"] for r in paired)
    errs = np.array([float(r["err_px"]) for r in both]) if both else np.array([np.nan])
    lat = np.array([float(r["node_latency_ms"]) for r in paired]) if paired else np.array([np.nan])
    statuses = [m.data for _, tp, m in events if tp == STATUS]
    summary = {
        "bag": name, "frames": n,
        "py_detect_rate": f"{sum(r['py_detected'] for r in rows) / n:.3f}",
        "node_detect_rate": (f"{sum(r['node_detected'] for r in paired) / len(paired):.3f}"
                             if paired else ""),
        "paired_frames": len(paired),
        "detect_agreement": f"{agree / len(paired):.3f}" if paired else "",
        "err_px_mean": f"{np.nanmean(errs):.2f}", "err_px_median": f"{np.nanmedian(errs):.2f}",
        "err_px_max": f"{np.nanmax(errs):.2f}",
        "node_latency_ms_median": f"{np.nanmedian(lat):.1f}",
        "motor_cmds": sum(1 for _, tp, _ in events if tp == MOTOR),
        "status_values": "/".join(sorted(set(statuses))),
        "params": Path(args.params).name,
    }
    summary_path = MODULE_DIR / "results/summary.csv"
    old = []
    if summary_path.exists():
        with open(summary_path) as f:
            old = [r for r in csv.DictReader(f) if r["bag"] != name]
    with open(summary_path, "w", newline="") as f:
        wr = csv.DictWriter(f, fieldnames=list(summary))
        wr.writeheader()
        wr.writerows(old + [summary])
    for k, v in summary.items():
        print(f"{k:24s} {v}")


if __name__ == "__main__":
    main()
