#!/usr/bin/env python3
# 문제 2: python3 ~/pa/dxltable.py 실행A.log
#   -> 목표 변경 이후 초기·중간·마지막 시점의 목표/현재/오차 표 (Markdown)
# 문제 3: python3 ~/pa/dxltable.py 실행A.log 실행B.log
#   -> 같은 경과 시간에서 A·B 현재각과 목표 초과 여부 비교표 (Markdown)
import sys


def rows(path):
    out = []
    for line in open(path, encoding="utf-8", errors="replace"):
        if not line.startswith("target_deg:"):
            continue
        d = {}
        for kv in line.strip().split("\t"):
            k, _, v = kv.partition(":")
            try:
                d[k] = float(v)
            except ValueError:
                pass
        out.append(d)
    return out


def after_goal(r):
    return [d for d in r if d["t_s"] >= 2.0]  # 펌웨어는 2초 후 목표를 바꾼다


def three_points(path):
    r = after_goal(rows(path))
    if not r:
        sys.exit("목표 변경 이후 행이 없습니다")
    print("| 시점 | t_s [s] | 목표각 [°] | 현재각 [°] | 오차=목표-현재 [°] | 출력 u [°/s] |")
    print("|---|---|---|---|---|---|")
    for name, d in (("초기", r[0]), ("중간", r[len(r) // 2]), ("마지막", r[-1])):
        e = d["target_deg"] - d["position_deg"]
        print(f"| {name} | {d['t_s']:.3f} | {d['target_deg']:.3f} | {d['position_deg']:.3f} "
              f"| {e:.3f} | {d['u_deg_s']:.3f} |")
    dt = [d["dt_ms"] for d in r]
    print(f"\n목표 변경 이후 행 수: {len(r)}, dt_ms 평균 {sum(dt) / len(dt):.3f} "
          f"(최소 {min(dt):.3f}, 최대 {max(dt):.3f})")


def compare(path_a, path_b):
    A, B = rows(path_a), rows(path_b)
    goal = A[-1]["target_deg"]
    s = 1 if goal > 0 else -1

    def at(r, t):
        return min(r, key=lambda d: abs(d["t_s"] - t))

    def over(p):
        return "예" if s * (p - goal) > 0.2 else "아니오"

    print("| 경과 t [s] | A 현재각 [°] | A 초과 | B 현재각 [°] | B 초과 |")
    print("|---|---|---|---|---|")
    for t in (2.5, 3.0, 3.5, 4.0, 5.0, 6.0, 8.0, 10.0):
        a, b = at(A, t)["position_deg"], at(B, t)["position_deg"]
        print(f"| {t:.1f} | {a:.2f} | {over(a)} | {b:.2f} | {over(b)} |")
    print()
    for name, r in (("A", A), ("B", B)):
        g = after_goal(r)
        peak = max(g, key=lambda d: s * d["position_deg"])
        reach = next((d["t_s"] for d in g
                      if abs(goal - d["position_deg"]) <= 0.1 * abs(goal)), None)
        print(f"- {name}: Kp={r[-1]['kp']}, 속도상한={r[-1]['v_limit_deg_s']} °/s, "
              f"최대 {peak['position_deg']:.2f}° (t={peak['t_s']:.1f}s), "
              f"최대 초과 {max(0.0, s * (peak['position_deg'] - goal)):.2f}°, "
              f"목표 90% 도달 t={reach} s, 마지막 오차 {goal - g[-1]['position_deg']:.2f}°")


if __name__ == "__main__":
    if len(sys.argv) == 2:
        three_points(sys.argv[1])
    elif len(sys.argv) == 3:
        compare(sys.argv[1], sys.argv[2])
    else:
        sys.exit(__doc__ or "사용: dxltable.py 실행A.log [실행B.log]")
