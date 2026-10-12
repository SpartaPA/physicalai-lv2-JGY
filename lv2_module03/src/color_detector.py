# src/color_detector.py
import cv2
import numpy as np

def make_mask(frame_bgr, lo, hi, lo2=None, hi2=None):
    """블러 → HSV → inRange(범위 1~2개) → 열림 → 닫힘."""
    blur = cv2.GaussianBlur(frame_bgr, (5, 5), 0)
    hsv = cv2.cvtColor(blur, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv, lo, hi)
    if lo2 is not None:                       # 빨강: H가 감기는 두 조각
        mask |= cv2.inRange(hsv, lo2, hi2)
    k = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, k)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, k)
    return mask

def detect(mask, min_area=300):
    cnts, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    best = None
    for c in cnts:
        area = cv2.contourArea(c)
        if area < min_area:
            continue                          # ① 면적 필터: 점 노이즈 제거
        peri = cv2.arcLength(c, True)
        circularity = 4 * np.pi * area / (peri * peri + 1e-9)
        if circularity < 0.6:
            continue                          # ② 형상 필터: 공이면 원형도
        if best is None or area > best[0]:
            best = (area, c)
    if best is None:
        return None
    M = cv2.moments(best[1])                  # ③ 모멘트로 중심
    cx, cy = M["m10"] / M["m00"], M["m01"] / M["m00"]
    x, y, w, h = cv2.boundingRect(best[1])
    return {"center": (cx, cy), "bbox": (x, y, w, h), "area": best[0]}