[Overview]
- HSV 색 검출로 파란 기둥을 찾고, 인지(/target) -> 제어(/motor_cmd) 연동을 확인하는 모듈
- 환경: Ubuntu, ROS 2 Lyrical, OpenCV 4.6, RealSense D435
- 모든 명령은 `lv2_module03/` 에서 실행

[Pipeline]
- 전체 과정: 빌드 -> HSV 보정 -> 검출 -> bag 재처리 -> 연동 시험 -> report.md 갱신
- 1 빌드: `sudo apt install rapidjson-dev && (cd ros2_ws && source /opt/ros/lyrical/setup.bash && colcon build --symlink-install) && source ros2_ws/install/setup.bash`
- 2 HSV 보정: `python3 src/hsv_calibrate.py --source 0 --name lab` -> `config/realsense_lab.yaml`
- 3 검출: `for f in ros2_ws/src/realsense/test/data/*.png; do python3 src/run_detector.py --source $f --no-gui --save results/detection/real_d435; done`
- 4 bag 재처리: `for s in scene1 scene5 scene6 scene7 scene8; do tar xzf data/bags/$s.tar.gz -C data/bags && python3 src/replay_bag.py data/bags/$s; done`
- 5 연동 시험: `src/link_test.sh data/bags/scene8 link_scene8`
- 6 보고서: `python3 src/make_report.py` -> `report.md` 의 AUTO 구간에 결과가 올라감

[Layout]
- `config/`: HSV 범위, 카메라 내부 파라미터, 왜곡 계수 ([config/README.md](config/README.md))
- `src/`: HSV 보정, 검출, bag 재처리, 연동 시험, 보고서 생성 코드
- `data/`: 입력 영상, bag 목록과 접근 방법 ([data/README.md](data/README.md))
- `results/`: 검출 화면(detection), 보정 오차(calibration_error), 연동 로그(logs), 요약(summary.csv)
- `ros2_ws/`: ROS 2 패키지 (realsense, dynamixel, bringup, fake_camera_bringup)
- `report.md`: 결과 보고서, `src/make_report.py` 가 갱신

[Step:HSV Calibrate]
- 이미지로 보정: `python3 src/hsv_calibrate.py --source ros2_ws/src/realsense/test/data/lit_pillar_20261002.png --name lit`
- 조작: 드래그 = 영역 HSV 측정, `a` = 범위 1에 적용, `s` = `config/realsense_<name>.yaml` 저장, `q` = 종료
- 보정한 설정으로 검출: `python3 src/run_detector.py --params config/realsense_lab.yaml`

[Step:Replay Bag]
- 출력: `results/detection/<bag>/`, `results/calibration_error/<bag>.csv`, `results/logs/<bag>_link.log`, `results/summary.csv`

[Step:Link Test]
- bag 영상 -> perception_node -> dynamixel_move_node, 카메라와 모터 없이 실행
- 실제 로봇: `ros2 launch bringup bringup.launch.py` (모터 없이: `use_motor:=false`)

[Step:Report]
- `report.md` 의 `<!-- AUTO:BEGIN -->` ~ `<!-- AUTO:END -->` 사이만 새로 씀, 그 밖에 직접 쓴 내용은 유지
- 올라가는 내용: HSV 설정, 내부 파라미터, 실제 영상 검출, bag별 보정 오차, 연동 FSM 전이와 처리 시간
- 결과 파일을 다시 만든 뒤 항상 마지막에 실행

[Result Summary]
- 실제 D435 영상 3장 모두 검출, 기대 범위가 있는 2장은 C++ 테스트 범위 통과
- Python 검출과 노드 /target 중심 오차: 전 프레임 0 px, 검출 일치율 1.000
- 연동 시험: IDLE -> TRACKING -> LOST -> TRACKING, 소실 후 2.56 s 만에 복귀
- 인지 처리 중앙값 1.2 ms/프레임, 영상 -> /target 지연 중앙값 1.5 ms
- 상세: [report.md](report.md)

[Notes]
- bag 영상은 가상 카메라 영상, 실제 D435 영상은 정지 영상 3장
- 카메라 내부 파라미터는 공장값, 체커보드 재투영 오차는 측정 안 함
