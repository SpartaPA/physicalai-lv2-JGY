[Data:Overview]
- HSV 보정과 검출 재현에 쓴 입력 영상, 파일 목록, 접근 방법
- 결과: [../results/README.md](../results/README.md)
- 모든 명령은 `lv2_module03/` 에서 실행

[Data:RealImages]
- 실제 D435 정지 영상 3장, `realsense.yaml` 의 HSV 범위를 정한 실측 장면
- 패키지 테스트 데이터에 있으므로 복사하지 않고 링크
- 카메라: RealSense D435 (시리얼 261322072019), 컬러 640x480x30, BGR
- 내부 파라미터, 왜곡 계수: [../config/camera_info_d435.yaml](../config/camera_info_d435.yaml)

[Data:RealImages:dim_backlit]
- 파일: [dim_backlit_20261002.png](../ros2_ws/src/realsense/test/data/dim_backlit_20261002.png)
- 장면: 파란 기둥, 어두운 역광 (V 37~46) -> 범위 1의 V 하한 20 근거
- SHA256: `fb53716c0e0baa34edc436694d789c05c96e86cfaa3166d24726265c00f9e948`

[Data:RealImages:lit_pillar]
- 파일: [lit_pillar_20261002.png](../ros2_ws/src/realsense/test/data/lit_pillar_20261002.png)
- 장면: 조명 받은 기둥 (S 170~202) -> 범위 2(밝은 면) 근거
- SHA256: `3a4b56695023ab3f4f227e998e270292f13342a484701339e335a08a2e72f15c`

[Data:RealImages:panel_and_pillar]
- 파일: [panel_and_pillar_20261002.png](../ros2_ws/src/realsense/test/data/panel_and_pillar_20261002.png)
- 장면: 하늘색 반투명 판 옆의 기둥 -> H 하한 103 근거 (판 제외)
- SHA256: `f7300f3f9178f62a2d5095447b9d54418de72b9d7c38fee779ea79dd1bbbc520`

[Data:Bags]
- 인지(`/target`) -> 제어(`/tracking_status`, `/motor_cmd`) 연동을 기록한 ROS 2 bag(mcap), 압축해서 `bags/` 에 저장
- 주의: 영상은 가상 카메라(sim_gui virtual world, 화면 하단 `VIRTUAL` 표시), 실제 D435 영상이 아님
- 녹화: `Lv2_noon_Assignment/lv2_module5/recordings`, 2026-10-06
- 전체 해시: [bags/SHA256SUMS](bags/SHA256SUMS)
- 메시지 수 순서: image / target / motor_cmd / status

[Data:Bags:scene1]
- 파일: [bags/scene1.tar.gz](bags/scene1.tar.gz), 1.2 MB
- 기간 11.3 s, 메시지 170 / 170 / 170 / 11
- 장면: 계속 추적
- SHA256: `845ff0258907574299d21ce03500d7a47b39fd1a23e2fd68f7a1ffa4c386c5bc`

[Data:Bags:scene5]
- 파일: [bags/scene5.tar.gz](bags/scene5.tar.gz), 580 KB
- 기간 5.7 s, 메시지 85 / 87 / 87 / 6
- 장면: 계속 추적
- SHA256: `5559f860a2f3e5e89c2e6ccf3b3a19fd6ee0f147be9f6665845c31ccb43f60c4`

[Data:Bags:scene6]
- 파일: [bags/scene6.tar.gz](bags/scene6.tar.gz), 208 KB
- 기간 2.1 s, 메시지 30 / 32 / 32 / 2
- 장면: 계속 추적
- SHA256: `0804782af2d8db8c74a1bb43e9f70d376b6d1620047bb5daaec8223acd8ded4f`

[Data:Bags:scene7]
- 파일: [bags/scene7.tar.gz](bags/scene7.tar.gz), 1.5 MB
- 기간 15.5 s, 메시지 226 / 218 / 219 / 17
- 장면: 추적 -> 소실
- SHA256: `5c62ea716ec7d1c6b583d9b319b041ce4d0ee5c67eec627c626d53e5e7dbed43`

[Data:Bags:scene8]
- 파일: [bags/scene8.tar.gz](bags/scene8.tar.gz), 2.7 MB
- 기간 27.1 s, 메시지 406 / 407 / 336 / 29
- 장면: 추적 -> 소실 -> 복귀
- SHA256: `403a9572e48be788f438ba03042d404fda4bcf0e08af014286a9c0bcc8257e75`

[Data:Topics]
- `/camera/camera/color/image_raw` (sensor_msgs/Image): 640x480 rgb8, OpenCV 처리 전 BGR로 변환 필요
- `/target` (geometry_msgs/PointStamped): x = ex, y = ey (-1~+1, 오른쪽/아래가 +), z = 면적비 (0이면 미검출), header = 원본 영상 시각
- `/tracking_status` (std_msgs/String): IDLE / TRACKING / LOST
- `/motor_cmd` (sensor_msgs/JointState): pan_joint, tilt_joint, position = 변화량(rad)

[Data:Frames]
- bag마다 처음부터 끝까지 고르게 5장을 BGR PNG로 추출해 `frames/<bag>/` 에 저장
- bag을 풀지 않고 `hsv_calibrate.py` 에 바로 넣을 수 있음
- 파일 이름의 숫자 = bag 안의 영상 순번 (예: `frames/scene1/scene1_0169.png`)
- 생성: [../src/replay_bag.py](../src/replay_bag.py)

[Access:Check]
- 무결성 확인: `(cd data/bags && sha256sum -c SHA256SUMS)`
- bag 풀기: `tar xzf data/bags/scene8.tar.gz -C data/bags` -> `data/bags/scene8/` 생성, 풀린 폴더는 git에 넣지 않음
- bag 정보: `source /opt/ros/lyrical/setup.bash` 후 `ros2 bag info data/bags/scene8`

[Access:Use]
- 정지 영상으로 HSV 보정: `python3 src/hsv_calibrate.py --source ros2_ws/src/realsense/test/data/lit_pillar_20261002.png --name lit`
- 보정 창 조작: 드래그 -> HSV 백분위 출력, `s` -> `config/realsense_<name>.yaml` 저장
- bag 재처리 -> results/ (검출 화면, 보정 오차, 연동 로그): `python3 src/replay_bag.py data/bags/scene8`
- ROS 노드 연동 시험 (모터 출력 없음): `src/link_test.sh data/bags/scene8 link_scene8`
- bag 영상만 ROS 토픽으로 재생: `ros2 bag play data/bags/scene8 --topics /camera/camera/color/image_raw`

[Access:AddNew]
- 실제 D435로 새 장면을 기록할 때 사용
- 다른 터미널에서 카메라 + 인지 + 제어 실행: `cd ros2_ws && source install/setup.bash && ros2 launch bringup bringup.launch.py`
- 실행 ID: `RUN_ID=$(date +%Y%m%d_%H%M%S)_<장면>`
- 녹화: `ros2 bag record -s mcap -o data/bags/$RUN_ID --topics /camera/camera/color/image_raw /camera/camera/color/camera_info /target /tracking_status /motor_cmd`
- 압축: `tar czf data/bags/$RUN_ID.tar.gz -C data/bags $RUN_ID && rm -rf data/bags/$RUN_ID`
- 해시 등록: `(cd data/bags && sha256sum $RUN_ID.tar.gz >> SHA256SUMS)`
- 위 [Data:Bags] 형식으로 항목 추가
- 압축 후 수십 MB를 넘으면 저장소 대신 공유 드라이브에 올리고 링크와 SHA256만 기록
