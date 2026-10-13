[Results:Overview]
- 검출 화면, 보정 오차, 연동 로그
- 입력: [../data/README.md](../data/README.md)
- 설정: HSV, 필터 [realsense.yaml](../ros2_ws/src/realsense/config/realsense.yaml) / 내부 파라미터 [camera_info_d435.yaml](../config/camera_info_d435.yaml)
- 생성일 2026-10-13, ROS 2 Lyrical, OpenCV 4.6.0

[Results:Layout]
- `detection/`: 검출 화면 (왼쪽 원본 + 검출 표시, 오른쪽 HSV 마스크)
- `detection/real_d435/`: 실제 D435 정지 영상 3장
- `detection/scene1/` ~ `detection/scene8/`: bag 재처리, 30프레임마다 + 검출/소실 전환 프레임(`*_change.jpg`)
- `detection/link_scene8/`: ROS 노드 연동 시험
- `calibration_error/`: 프레임별 오차 CSV (Python 재검출 vs 노드가 발행한 /target)
- `logs/<bag>_link.log`: 영상 -> /target -> /tracking_status -> /motor_cmd 시간순 로그
- `logs/link_scene8_launch.log`: 연동 시험의 노드 실행 로그 (perception fps, 검출, FSM 전이)
- `summary.csv`: bag별 요약

[Results:Legend]
- 초록 contour: 조건을 통과한 후보
- 빨강 contour: 탈락 후보
- 초록 사각형, 노란 점: 선택된 목표의 bbox, 중심
- `e=(ex,ey)`: 정규화 중심 오차
- `a`: 면적비

[Detection:RealD435]
- 폴더: [detection/real_d435/](detection/real_d435/)
- 기대 범위 출처: [test_detector.cpp](../ros2_ws/src/realsense/test/test_detector.cpp) 의 `RealDimBacklitScene`, `RealPanelAndPillarScene`
- bbox 표기: (x, y, w, h)

[Detection:RealD435:dim_backlit]
- 화면: [dim_backlit_20261002_0001.jpg](detection/real_d435/dim_backlit_20261002_0001.jpg)
- 결과: 검출, 중심 (317.4, 388.2), bbox (295, 340, 47, 97)
- 면적비 0.0132, 종횡비 2.09, 채움비 0.92
- C++ 테스트 기대 범위: x 285~300, y 330~345, w 40~60, h 85~110 -> 통과

[Detection:RealD435:lit_pillar]
- 화면: [lit_pillar_20261002_0001.jpg](detection/real_d435/lit_pillar_20261002_0001.jpg)
- 결과: 검출 (채움비 탈락 후보 1개), 중심 (442.7, 369.0), bbox (412, 312, 60, 115)
- 면적비 0.0189, 종횡비 2.01, 채움비 0.90
- C++ 테스트 기대 범위: 없음

[Detection:RealD435:panel_and_pillar]
- 화면: [panel_and_pillar_20261002_0001.jpg](detection/real_d435/panel_and_pillar_20261002_0001.jpg)
- 결과: 검출, 하늘색 판 제외, 중심 (477.7, 338.6), bbox (444, 282, 66, 114)
- 면적비 0.0190, 종횡비 1.95, 채움비 0.88
- C++ 테스트 기대 범위: x 435~455, y 275~290 -> 통과

[Detection:Bags]
- 연동 bag (가상 카메라) 재처리 화면: [detection/](detection/)
- scene8 #221 소실: [0221_change.jpg](detection/scene8/0221_change.jpg)
- scene8 #266 복귀: [0266_change.jpg](detection/scene8/0266_change.jpg)
- scene7 #212 소실: [0212_change.jpg](detection/scene7/0212_change.jpg)

[CalibrationError:HSV:Method]
- 같은 영상을 `src/color_detector.py` (Python 재구현, 보정한 설정 사용)로 다시 검출해 노드가 발행한 `/target` 과 프레임별 비교
- `/target` 의 ex, ey를 픽셀로 변환 (cx = W/2 + ex * W/2) 후 중심 차이 계산
- 프레임별 값: [calibration_error/](calibration_error/)
- 항목 순서: 프레임 수 / 검출 일치율 / 검출률 (Python, 노드) / 중심 오차 평균, 최대 (px) / 면적비 오차

[CalibrationError:HSV:Values]
- scene1 녹화본: 170 / 1.000 / 1.000, 1.000 / 0.00, 0.00 / -0.00037
- scene5 녹화본: 85 / 1.000 / 1.000, 1.000 / 0.00, 0.00 / -0.00037
- scene6 녹화본: 30 / 1.000 / 1.000, 1.000 / 0.00, 0.00 / -0.00037
- scene7 녹화본: 226 (짝 218) / 1.000 / 0.938, 0.936 / 0.00, 0.00 / -0.00037
- scene8 녹화본: 406 / 1.000 / 0.889, 0.889 / 0.00, 0.00 / -0.00037
- link_scene8 (현재 C++ 노드): 405 / 1.000 / 0.889, 0.889 / 0.00, 0.00 / 0

[CalibrationError:HSV:Notes]
- 중심 오차: 모든 프레임에서 0px, Python 재구현과 C++ 인지 노드는 같은 설정에서 같은 목표를 같은 위치로 검출
- 면적비 차이: 녹화본(2026-10-06)과는 항상 0.00037(약 4%) 차이, 같은 영상을 현재 C++ 노드로 다시 돌린 link_scene8에서는 0
- 면적비 차이 원인: 녹화 당시 노드 버전의 면적 계산이 지금과 달랐던 것으로 추정, 중심과 검출 여부에는 영향 없음
- 검출률이 1보다 낮은 이유: scene7, scene8에서 목표가 화면 밖으로 나간 구간, 오검출 아님
- 실제 D435 영상: 정답 라벨이 없어 프레임별 오차 대신 [Detection:RealD435] 의 C++ 테스트 기대 범위로 확인

[CalibrationError:Camera]
- fx, fy, cx, cy: 607.32, 607.19, 328.45, 256.01 -> 오차 측정 안 함
- 왜곡 (plumb_bob): [0, 0, 0, 0, 0]
- 출처: D435 공장 캘리브레이션 (`/camera/camera/color/camera_info`)
- 체커보드 캘리브레이션을 하지 않았으므로 재투영 오차 없음
- 측정 방법: D435 연결 후 `ros2 run camera_calibration cameracalibrator --size 8x6 --square 0.025 --ros-args -r image:=/camera/camera/color/image_raw`
- 측정 후 재투영 오차와 K, D를 이 항목과 [camera_info_d435.yaml](../config/camera_info_d435.yaml) 에 기록

[Link:Test]
- [../src/link_test.sh](../src/link_test.sh) 로 scene8 영상만 재생하고 인지, 제어 노드를 실제로 실행해 새로 기록
- 카메라와 모터는 사용 안 함
- 흐름: bag 영상 -> perception_node -> /target -> dynamixel_move_node -> /motor_cmd -> dynamixel_controller (use_motor:=false)
- dynamixel_move_node 는 /tracking_status 도 발행

[Link:Test:FSM]
- 0.000 s: IDLE, 첫 목표 대기
- 3.837 s: IDLE -> TRACKING, 첫 /target 수신
- 19.013 s: TRACKING -> LOST, 목표가 화면 밖으로 나감 (perception `detected 0/15`)
- 21.568 s: LOST -> TRACKING, 2.56 s 뒤 복귀
- 31.313 s: TRACKING -> LOST, bag 재생이 끝나 영상이 끊김 (원본 scene8은 TRACKING으로 끝남)

[Link:Test:Numbers]
- 녹화: image 405, /target 405, /motor_cmd 334, /tracking_status 38
- 인지 처리 시간 1.0~1.3 ms/프레임, 입력 15 fps를 모두 처리 (`detected 15/15`)
- 영상 -> /target 지연 중앙값 1.5 ms (bag 기록 시각 기준)
- 토픽 시간순 로그: [logs/link_scene8_link.log](logs/link_scene8_link.log)
- 노드 출력 로그: [logs/link_scene8_launch.log](logs/link_scene8_launch.log)

[Link:Test:ReadingNotes]
- `launch.log` 의 `age 579... ms` 는 bag 영상의 원래 시각(10/6)과 재생 시각의 차이, bag 재생 때문에 생긴 값이며 지연이 아님
- `serial open /dev/opencr` 오류는 모터 보드를 연결하지 않았기 때문 (use_motor:=false)

[Link:Recorded]
- [logs/scene1_link.log](logs/scene1_link.log) ~ [logs/scene8_link.log](logs/scene8_link.log): 녹화 당시 노드들이 주고받은 토픽을 시간순으로 풀어 쓴 로그
- `<시각> image stamp=... 640x480 rgb8`: 입력 영상
- `<시각> target stamp=... ex=-0.167 ey=-0.058 area=0.0093`: 같은 stamp 영상의 검출 결과
- `<시각> motor pan_joint=+0.0050 tilt_joint=-0.0035`: 그 /target에 대한 명령 (변화량 rad)
- `<시각> status TRACKING`: 추적 상태

[Regenerate]
- 준비: `cd lv2_module03 && source /opt/ros/lyrical/setup.bash`
- bag 재처리: `for s in scene1 scene5 scene6 scene7 scene8; do tar xzf data/bags/$s.tar.gz -C data/bags && python3 src/replay_bag.py data/bags/$s; done`
- 연동 시험: `src/link_test.sh data/bags/scene8 link_scene8`
- 실제 D435 영상: `for f in ros2_ws/src/realsense/test/data/*.png; do python3 src/run_detector.py --source $f --no-gui --save results/detection/real_d435; done`
