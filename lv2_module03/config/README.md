# config — 사용한 설정

PDF: "설정이 패키지 안에 있으면 중복 복사하지 않고 경로를 연결합니다." 아래가 실제로 쓰는 설정 파일입니다.
시험에 쓴 설정을 바꿔 돌렸다면 그 사본을 `config/<패키지>_<설명>.yaml`로 남기고 보고서에서 링크합니다.

| 영역 | 파일 | 주요 값 |
|---|---|---|
| 인지 (HSV 범위) | [../ros2_ws/src/realsense/config/realsense.yaml](../ros2_ws/src/realsense/config/realsense.yaml) | 범위 1 `hsv_lower` [103, 220, 20] ~ `hsv_upper` [130, 255, 255]<br>범위 2 `hsv_bright_lower` [103, 150, 130] ~ `hsv_bright_upper` [130, 255, 255] (두 범위 OR, H 0~179) |
| 인지 (면적·필터·QoS) | [../ros2_ws/src/realsense/config/realsense.yaml](../ros2_ws/src/realsense/config/realsense.yaml) | min/max_area_ratio, open/close_kernel, aspect_max, fill_min, image_reliable |
| 카메라 (해상도·FPS) | [../ros2_ws/src/realsense/launch/realsense.launch.py](../ros2_ws/src/realsense/launch/realsense.launch.py) | color_profile 640x480x30 |
| 카메라 내부 파라미터·왜곡 계수 | [camera_info_d435.yaml](camera_info_d435.yaml) | fx 607.32, fy 607.19, cx 328.45, cy 256.01 (640x480)<br>plumb_bob, D = [0, 0, 0, 0, 0] (D435 공장 캘리브레이션, `/camera/camera/color/camera_info` 실측) |
| 제어 (게인·제한·타임아웃) | [../ros2_ws/src/dynamixel/config/dynamixel.yaml](../ros2_ws/src/dynamixel/config/dynamixel.yaml) | pan/tilt_gain, deadband, max_*_command, lost_timeout, serial_port, baud_rate |
| 장치 (모터 ID·baud·범위) | [../firmware/opencr_pan_tilt/config.h](../firmware/opencr_pan_tilt/config.h) | PAN_ID 11, TILT_ID 12, DXL_BAUD 1000000, MIN/MAX_TARGET_DEG |
| 시험 조건 | TODO(검증): 시험 설정 파일 또는 [../report.md](../report.md) 1.4 | Kp 2종, 이동 순서, 거리 |
