# src/run_detector.py
"""보정한 HSV 설정으로 검출을 실행한다 (카메라·영상·이미지).

실행 (lv2_module03/ 에서)
  python3 src/run_detector.py                                   # 카메라 0번, realsense.yaml
  python3 src/run_detector.py --params config/realsense_tuned.yaml
  python3 src/run_detector.py --source ros2_ws/src/realsense/test/data/dim_backlit_20261002.png --no-gui
"""
import argparse
import time
from pathlib import Path

import cv2
import numpy as np

from color_detector import (DEFAULT_CAMERA_INFO, DEFAULT_PARAMS, CameraInfo, DetectorConfig,
                            Undistorter, detect, draw, make_mask)


def frames(src):
    if Path(src).suffix.lower() in (".png", ".jpg", ".jpeg", ".bmp"):
        img = cv2.imread(src)
        if img is None:
            raise SystemExit(f"이미지를 읽을 수 없다: {src}")
        yield img
        return
    cap = cv2.VideoCapture(int(src) if src.isdigit() else src)
    if src.isdigit():
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    try:
        while True:
            ok, img = cap.read()
            if not ok:
                return
            yield img
    finally:
        cap.release()


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawTextHelpFormatter)
    ap.add_argument("--source", default="0", help="카메라 번호, 영상 파일 또는 이미지 파일")
    ap.add_argument("--params", default=str(DEFAULT_PARAMS))
    ap.add_argument("--camera-info", default=str(DEFAULT_CAMERA_INFO))
    ap.add_argument("--no-gui", action="store_true", help="창 없이 결과만 출력")
    args = ap.parse_args()

    cfg = DetectorConfig.load(args.params)
    undistort = Undistorter(CameraInfo.load(args.camera_info))
    print(f"설정: {cfg}")

    t0, n = time.time(), 0
    for raw in frames(args.source):
        img = undistort(raw)
        mask = make_mask(img, cfg)
        r = detect(img, cfg, mask)
        rejected = {}
        for c in r["candidates"]:
            if c["reason"] != "ok":
                rejected[c["reason"]] = rejected.get(c["reason"], 0) + 1
        if r["detected"]:
            print(f"detected  c=({r['cx']:.1f},{r['cy']:.1f})  e=({r['ex']:+.3f},{r['ey']:+.3f})"
                  f"  area={r['area_ratio']:.4f}  aspect={r['aspect']:.2f}  fill={r['fill']:.2f}"
                  f"  rejected={rejected}")
        else:
            print(f"none  rejected={rejected}")

        n += 1
        if n % 30 == 0:
            print(f"FPS: {30 / (time.time() - t0):.1f}")
            t0 = time.time()
        if args.no_gui:
            continue
        cv2.imshow("detector", np.hstack([draw(img, r), cv2.cvtColor(mask, cv2.COLOR_GRAY2BGR)]))
        still = Path(args.source).suffix.lower() in (".png", ".jpg", ".jpeg", ".bmp")
        if cv2.waitKey(0 if still else 1) & 0xFF in (ord("q"), 27):
            break
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
