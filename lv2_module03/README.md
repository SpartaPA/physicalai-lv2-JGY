[Overview]
- HSV 색 검출로 파란 기둥을 찾고, 인지(/target) -> 제어(/motor_cmd) 연동을 확인하는 모듈
- 환경: Ubuntu, ROS 2 Lyrical, OpenCV 4.6, RealSense D435
- 모든 명령은 `lv2_module03/` 에서 실행

[Layout]
- `config/`: HSV 범위, 카메라 내부 파라미터, 왜곡 계수 ([config/README.md](config/README.md))
- `src/`: HSV 보정, 검출, bag 재처리, 연동 시험 코드
- `data/`: 입력 영상, bag 목록과 접근 방법 ([data/README.md](data/README.md))
- `results/`: 검출 화면(detection), 보정 오차(calibration_error), 연동 로그(logs), 요약(summary.csv)
- `ros2_ws/`: ROS 2 패키지 (realsense, dynamixel, bringup, fake_camera_bringup)

[Setup]
- 의존성: `sudo apt install rapidjson-dev`
- 빌드: `cd ros2_ws && source /opt/ros/lyrical/setup.bash && colcon build --symlink-install && cd ..`
- 환경 적용: `source ros2_ws/install/setup.bash`
- bag 풀기: `for s in scene1 scene5 scene6 scene7 scene8; do tar xzf data/bags/$s.tar.gz -C data/bags; done`

[Run:HSV Calibrate]
- 카메라: `python3 src/hsv_calibrate.py --source 0 --name lab`
- 이미지: `python3 src/hsv_calibrate.py --source ros2_ws/src/realsense/test/data/lit_pillar_20261002.png --name lit`
- 조작: 드래그 = 영역 HSV 측정, `a` = 범위 1에 적용, `s` = `config/realsense_<name>.yaml` 저장, `q` = 종료

[Run:Detect]
- 기본 설정: `python3 src/run_detector.py --source 0`
- 보정한 설정: `python3 src/run_detector.py --params config/realsense_lab.yaml`
- 화면 저장: `python3 src/run_detector.py --source <이미지> --no-gui --save results/detection/real_d435`

[Run:Replay Bag]
- `python3 src/replay_bag.py data/bags/scene8`
- 출력: 검출 화면, 프레임별 오차 CSV, 연동 로그, `results/summary.csv`

[Run:Link Test]
- `src/link_test.sh data/bags/scene8 link_scene8`
- bag 영상 -> perception_node -> dynamixel_move_node, 카메라와 모터 없이 실행

[Run:Real Robot]
- 전체 실행: `ros2 launch bringup bringup.launch.py`
- 모터 없이: `ros2 launch bringup bringup.launch.py use_motor:=false`

[Result Summary]
- 실제 D435 영상 3장 모두 검출, 기대 범위가 있는 2장은 C++ 테스트 범위 통과
- Python 검출과 노드 /target 중심 오차: 전 프레임 0 px, 검출 일치율 1.000
- 연동 시험: IDLE -> TRACKING -> LOST -> TRACKING, 소실 후 2.56 s 만에 복귀
- 인지 처리 1.0~1.3 ms/프레임, 영상 -> /target 지연 중앙값 1.5 ms
- 상세 값: [results/summary.csv](results/summary.csv), [results/calibration_error/](results/calibration_error/), [results/logs/](results/logs/)

[Notes]
- bag 영상은 가상 카메라 영상, 실제 D435 영상은 정지 영상 3장
- 카메라 내부 파라미터는 공장값, 체커보드 재투영 오차는 측정 안 함
