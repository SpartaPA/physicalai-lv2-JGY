[Config:Overview]
- 실제로 쓰는 설정 파일 목록
- PDF 기준: 설정이 패키지 안에 있으면 중복 복사하지 않고 경로를 연결
- 시험에 쓴 설정을 바꿔 돌렸다면 그 사본을 `config/<패키지>_<설명>.yaml`로 남기고 보고서에서 링크

[Config:HSV]
- 파일: [../ros2_ws/src/realsense/config/realsense.yaml](../ros2_ws/src/realsense/config/realsense.yaml)
- 범위 1: `hsv_lower` [103, 220, 20] ~ `hsv_upper` [130, 255, 255]
- 범위 2 (밝은 면): `hsv_bright_lower` [103, 150, 130] ~ `hsv_bright_upper` [130, 255, 255]
- 두 범위를 OR로 합침, H 0~179 / S, V 0~255

[Config:Perception]
- 파일: [../ros2_ws/src/realsense/config/realsense.yaml](../ros2_ws/src/realsense/config/realsense.yaml)
- 면적, 필터, QoS: min/max_area_ratio, open/close_kernel, aspect_max, fill_min, image_reliable

[Config:Camera]
- 해상도, FPS: [../ros2_ws/src/realsense/launch/realsense.launch.py](../ros2_ws/src/realsense/launch/realsense.launch.py) 의 color_profile 640x480x30
- 내부 파라미터, 왜곡 계수: [camera_info_d435.yaml](camera_info_d435.yaml)
- fx 607.32, fy 607.19, cx 328.45, cy 256.01 (640x480)
- 왜곡: plumb_bob, D = [0, 0, 0, 0, 0]
- 출처: D435 공장 캘리브레이션, `/camera/camera/color/camera_info` 실측

[Config:Control]
- 파일: [../ros2_ws/src/dynamixel/config/dynamixel.yaml](../ros2_ws/src/dynamixel/config/dynamixel.yaml)
- 게인, 제한, 타임아웃: pan/tilt_gain, deadband, max_*_command, lost_timeout, serial_port, baud_rate

[Config:Device]
- 파일: [../firmware/opencr_pan_tilt/config.h](../firmware/opencr_pan_tilt/config.h)
- 모터 ID, baud, 범위: PAN_ID 11, TILT_ID 12, DXL_BAUD 1000000, MIN/MAX_TARGET_DEG

[Config:TestCondition]
- TODO(검증): 시험 설정 파일 또는 [../report.md](../report.md) 1.4
- Kp 2종, 이동 순서, 거리
