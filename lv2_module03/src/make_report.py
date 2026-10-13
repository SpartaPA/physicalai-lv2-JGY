# src/make_report.py
"""results/ 의 결과를 읽어 report.md 에 올린다.

report.md 의 <!-- AUTO:BEGIN --> ~ <!-- AUTO:END --> 사이만 새로 쓰고, 그 밖에 직접 쓴 내용은 그대로 둔다.
report.md 가 없으면 새로 만든다.

실행 (lv2_module03/ 에서)
  python3 src/make_report.py
"""
import csv
import re
import subprocess
from datetime import date
from pathlib import Path

import cv2

from color_detector import (DEFAULT_CAMERA_INFO, DEFAULT_PARAMS, MODULE_DIR, CameraInfo,
                            DetectorConfig, detect)

REPORT = MODULE_DIR / "report.md"
RESULTS = MODULE_DIR / "results"
REAL_DIR = MODULE_DIR / "ros2_ws/src/realsense/test/data"
BEGIN, END = "<!-- AUTO:BEGIN -->", "<!-- AUTO:END -->"

# C++ 테스트(test_detector.cpp)의 실제 장면 기대 범위: (x, y, w, h) 각각 (최소, 최대), None 은 검사 안 함
EXPECTED = {
    "dim_backlit_20261002": ((285, 300), (330, 345), (40, 60), (85, 110)),
    "panel_and_pillar_20261002": ((435, 455), (275, 290), None, None),
}


def section_overview():
    cfg = DetectorConfig.load(DEFAULT_PARAMS)
    info = CameraInfo.load(DEFAULT_CAMERA_INFO)
    commit = subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=MODULE_DIR,
                            capture_output=True, text=True).stdout.strip() or "unknown"
    return [
        "[개요]",
        "",
        f"- 생성일 {date.today()}, 기준 커밋 `{commit}`, `python3 src/make_report.py` 로 자동 생성했다.",
        f"- HSV 범위 1은 {cfg.hsv_lower} ~ {cfg.hsv_upper}, 범위 2(밝은 면)는 "
        f"{cfg.hsv_bright_lower} ~ {cfg.hsv_bright_upper} 이고 두 범위를 OR로 합친다.",
        f"- 면적비 {cfg.min_area_ratio} ~ {cfg.max_area_ratio}, 종횡비 {cfg.aspect_max} 이하, "
        f"채움비 {cfg.fill_min} 이상인 후보 중 면적이 가장 큰 것을 목표로 고른다.",
        f"- 카메라 내부 파라미터는 fx {info.K[0, 0]}, fy {info.K[1, 1]}, cx {info.K[0, 2]}, "
        f"cy {info.K[1, 2]} ({info.width}x{info.height}), 왜곡 계수는 {info.D.tolist()} 이다.",
        "- 내부 파라미터는 D435 공장값이고 체커보드 캘리브레이션은 하지 않아 재투영 오차는 없다.",
        "",
    ]


def section_real_images():
    cfg = DetectorConfig.load(DEFAULT_PARAMS)
    lines = ["[실제 D435 영상 검출]", ""]
    for path in sorted(REAL_DIR.glob("*.png")):
        r = detect(cv2.imread(str(path)), cfg)
        name = path.stem
        if not r["detected"]:
            lines.append(f"- {name}: 검출 실패.")
            continue
        x, y, w, h = r["bbox"]
        exp = EXPECTED.get(name)
        if exp is None:
            verdict = "기대 범위 없음"
        else:
            ok = all(rng is None or rng[0] <= v <= rng[1] for v, rng in zip((x, y, w, h), exp))
            verdict = "C++ 테스트 기대 범위 통과" if ok else "C++ 테스트 기대 범위 벗어남"
        lines.append(f"- {name}: 중심 ({r['cx']:.1f}, {r['cy']:.1f}), bbox ({x}, {y}, {w}, {h}), "
                     f"면적비 {r['area_ratio']:.4f}, {verdict}.")
    lines += ["- 검출 화면은 `results/detection/real_d435/` 에 있다.", ""]
    return lines


def section_bags():
    path = RESULTS / "summary.csv"
    if not path.exists():
        return ["[bag 재처리 보정 오차]", "", "- results/summary.csv 가 없다. replay_bag.py 를 먼저 실행한다.", ""]
    rows = list(csv.DictReader(open(path)))
    lines = ["[bag 재처리 보정 오차]", "",
             "- 같은 영상을 Python 검출기로 다시 돌려 노드가 발행한 /target 과 프레임마다 비교했다.",
             "- bag 영상은 가상 카메라 영상이다."]
    for r in rows:
        lines.append(
            f"- {r['bag']}: {r['frames']} 프레임, 검출률 Python {r['py_detect_rate']} / 노드 "
            f"{r['node_detect_rate']}, 검출 일치율 {r['detect_agreement']}, 중심 오차 평균 "
            f"{r['err_px_mean']} px / 최대 {r['err_px_max']} px, 상태 {r['status_values']}.")
    lines += ["- 프레임별 값은 `results/calibration_error/<bag>.csv` 에 있다.", ""]
    return lines


def section_link():
    link = RESULTS / "logs/link_scene8_link.log"
    launch = RESULTS / "logs/link_scene8_launch.log"
    if not link.exists():
        return ["[연동 시험]", "", "- link_test.sh 결과가 없다.", ""]
    lines = ["[연동 시험]", "",
             "- `src/link_test.sh` 로 bag 영상을 perception_node, dynamixel_move_node 에 흘려 실제 노드 연동을 기록했다.",
             "- 카메라와 모터는 쓰지 않았다 (use_motor:=false)."]
    prev = None
    for line in open(link):
        m = re.match(r"\s*([\d.]+) status\s+(\S+)", line)
        if m and m.group(2) != prev:
            lines.append(f"- {float(m.group(1)):.3f} s: {prev or '시작'} -> {m.group(2)}")
            prev = m.group(2)
    counts = {}
    for line in open(link):
        m = re.match(r"\s*[\d.]+ (\w+)", line)
        if m:
            counts[m.group(1)] = counts.get(m.group(1), 0) + 1
    lines.append("- 메시지 수: " + ", ".join(f"{k} {v}" for k, v in counts.items()) + ".")
    if launch.exists():
        procs = [float(x) for x in re.findall(r"proc ([\d.]+) ms", launch.read_text())]
        if procs:
            procs.sort()
            lines.append(f"- 인지 처리 시간 중앙값 {procs[len(procs) // 2]} ms, 최대 {procs[-1]} ms/프레임 "
                         f"(1초마다 찍힌 {len(procs)}개 평균값 기준).")
    lines += ["- 마지막 LOST 는 bag 재생이 끝나 영상이 끊겼기 때문이다.",
              "- 로그는 `results/logs/link_scene8_link.log`, `results/logs/link_scene8_launch.log` 에 있다.", ""]
    return lines


def main():
    body = "\n".join([BEGIN, ""] + section_overview() + section_real_images() + section_bags()
                     + section_link() + [END])
    if REPORT.exists():
        text = REPORT.read_text()
        if BEGIN in text and END in text:
            text = text[: text.index(BEGIN)] + body + text[text.index(END) + len(END):]
        else:
            text = text.rstrip() + "\n\n" + body + "\n"
    else:
        text = "[모듈 3 보고서 HSV 색 검출과 인지 제어 연동]\n\n" + body + "\n"
    REPORT.write_text(text)
    print(f"갱신: {REPORT}")


if __name__ == "__main__":
    main()
