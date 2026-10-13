[모듈 3 보고서 HSV 색 검출과 인지 제어 연동]

<!-- AUTO:BEGIN -->

[개요]

- 생성일 2026-10-13, 기준 커밋 `3819060`, `python3 src/make_report.py` 로 자동 생성했다.
- HSV 범위 1은 [103, 220, 20] ~ [130, 255, 255], 범위 2(밝은 면)는 [103, 150, 130] ~ [130, 255, 255] 이고 두 범위를 OR로 합친다.
- 면적비 0.0006 ~ 0.15, 종횡비 4.0 이하, 채움비 0.6 이상인 후보 중 면적이 가장 큰 것을 목표로 고른다.
- 카메라 내부 파라미터는 fx 607.32, fy 607.19, cx 328.45, cy 256.01 (640x480), 왜곡 계수는 [0.0, 0.0, 0.0, 0.0, 0.0] 이다.
- 내부 파라미터는 D435 공장값이고 체커보드 캘리브레이션은 하지 않아 재투영 오차는 없다.

[실제 D435 영상 검출]

- dim_backlit_20261002: 중심 (317.4, 388.2), bbox (295, 340, 47, 97), 면적비 0.0132, C++ 테스트 기대 범위 통과.
- lit_pillar_20261002: 중심 (442.7, 369.0), bbox (412, 312, 60, 115), 면적비 0.0189, 기대 범위 없음.
- panel_and_pillar_20261002: 중심 (477.7, 338.6), bbox (444, 282, 66, 114), 면적비 0.0190, C++ 테스트 기대 범위 통과.
- 검출 화면은 `results/detection/real_d435/` 에 있다.

[bag 재처리 보정 오차]

- 같은 영상을 Python 검출기로 다시 돌려 노드가 발행한 /target 과 프레임마다 비교했다.
- bag 영상은 가상 카메라 영상이다.
- scene6: 30 프레임, 검출률 Python 1.000 / 노드 1.000, 검출 일치율 1.000, 중심 오차 평균 0.00 px / 최대 0.00 px, 상태 TRACKING.
- scene1: 170 프레임, 검출률 Python 1.000 / 노드 1.000, 검출 일치율 1.000, 중심 오차 평균 0.00 px / 최대 0.00 px, 상태 TRACKING.
- scene5: 85 프레임, 검출률 Python 1.000 / 노드 1.000, 검출 일치율 1.000, 중심 오차 평균 0.00 px / 최대 0.00 px, 상태 TRACKING.
- scene7: 226 프레임, 검출률 Python 0.938 / 노드 0.936, 검출 일치율 1.000, 중심 오차 평균 0.00 px / 최대 0.00 px, 상태 LOST/TRACKING.
- scene8: 406 프레임, 검출률 Python 0.889 / 노드 0.889, 검출 일치율 1.000, 중심 오차 평균 0.00 px / 최대 0.00 px, 상태 LOST/TRACKING.
- link_scene8: 405 프레임, 검출률 Python 0.889 / 노드 0.889, 검출 일치율 1.000, 중심 오차 평균 0.00 px / 최대 0.00 px, 상태 IDLE/LOST/TRACKING.
- 프레임별 값은 `results/calibration_error/<bag>.csv` 에 있다.

[연동 시험]

- `src/link_test.sh` 로 bag 영상을 perception_node, dynamixel_move_node 에 흘려 실제 노드 연동을 기록했다.
- 카메라와 모터는 쓰지 않았다 (use_motor:=false).
- 0.000 s: 시작 -> IDLE
- 3.837 s: IDLE -> TRACKING
- 19.013 s: TRACKING -> LOST
- 21.568 s: LOST -> TRACKING
- 31.313 s: TRACKING -> LOST
- 메시지 수: status 38, image 405, target 405, motor 334.
- 인지 처리 시간 중앙값 1.2 ms, 최대 2.1 ms/프레임 (1초마다 찍힌 28개 평균값 기준).
- 마지막 LOST 는 bag 재생이 끝나 영상이 끊겼기 때문이다.
- 로그는 `results/logs/link_scene8_link.log`, `results/logs/link_scene8_launch.log` 에 있다.

<!-- AUTO:END -->
