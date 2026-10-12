# scripts/run_detector.py
import cv2
import time
from color_detector import ColorDetector

det = ColorDetector(config["red"])           # make_mask + detect + EMA를 클래스로
cap = cv2.VideoCapture(0)
t0, n = time.time(), 0
while True:
    ret, frame = cap.read()
    if not ret:
        break
    r = det.step(frame)
    if r:
        cv2.circle(frame, (int(r["cx"]), int(r["cy"])), 6, (0, 255, 0), -1)
        cv2.rectangle(frame, r["bbox"][:2],
                      (r["bbox"][0]+r["bbox"][2], r["bbox"][1]+r["bbox"][3]),
                      (0, 255, 0), 2)
    n += 1
    if n % 30 == 0:
        print(f"FPS: {30 / (time.time() - t0):.1f}"); t0 = time.time()
    cv2.imshow("detector", frame)
    if cv2.waitKey(1) == 27:
        break