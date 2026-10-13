# data — 입력 보정 영상·파일 목록과 접근 방법

HSV 보정과 검출 재현에 쓴 입력입니다. 결과는 [../results/README.md](../results/README.md)에 있습니다.

## 1. 파일 목록

### 1.1 실제 D435 정지 영상 (HSV 범위 보정 근거)

`realsense.yaml`의 HSV 범위를 정한 실측 장면입니다. 패키지 테스트 데이터에 있으므로 복사하지 않고 링크합니다.

| 파일 | 장면 | 크기 | SHA256 |
|---|---|---|---|
| [dim_backlit_20261002.png](../ros2_ws/src/realsense/test/data/dim_backlit_20261002.png) | 파란 기둥, 어두운 역광 (V 37~46) → 범위 1의 V 하한 20 근거 | 640×480 BGR | `fb53716c0e0baa34edc436694d789c05c96e86cfaa3166d24726265c00f9e948` |
| [lit_pillar_20261002.png](../ros2_ws/src/realsense/test/data/lit_pillar_20261002.png) | 조명 받은 기둥 (S 170~202) → 범위 2(밝은 면) 근거 | 640×480 BGR | `3a4b56695023ab3f4f227e998e270292f13342a484701339e335a08a2e72f15c` |
| [panel_and_pillar_20261002.png](../ros2_ws/src/realsense/test/data/panel_and_pillar_20261002.png) | 하늘색 반투명 판 옆의 기둥 → H 하한 103 근거 (판 제외) | 640×480 BGR | `f7300f3f9178f62a2d5095447b9d54418de72b9d7c38fee779ea79dd1bbbc520` |

- 카메라: RealSense D435 (시리얼 261322072019), 컬러 640×480×30
- 내부 파라미터·왜곡 계수: [../config/camera_info_d435.yaml](../config/camera_info_d435.yaml)

### 1.2 연동 녹화 bag (`bags/`)

인지(`/target`) → 제어(`/tracking_status`, `/motor_cmd`) 연동을 기록한 ROS 2 bag(mcap)입니다. 압축해서 저장소에 넣었습니다.

> ⚠️ 이 bag들의 영상은 **가상 카메라**(sim_gui의 virtual world, 화면 하단 `VIRTUAL` 표시)입니다. 실제 D435 영상이 아닙니다.
> 녹화: `Lv2_noon_Assignment/lv2_module5/recordings`, 2026-10-06.

| 파일 | 기간 | 메시지 수 (image / target / motor_cmd / status) | 장면 | 압축 크기 | SHA256 |
|---|---|---|---|---|---|
| [bags/scene1.tar.gz](bags/scene1.tar.gz) | 11.3 s | 170 / 170 / 170 / 11 | 계속 추적 | 1.2 MB | `845ff02589075742…` |
| [bags/scene5.tar.gz](bags/scene5.tar.gz) | 5.7 s | 85 / 87 / 87 / 6 | 계속 추적 | 580 KB | `5559f860a2f3e5e8…` |
| [bags/scene6.tar.gz](bags/scene6.tar.gz) | 2.1 s | 30 / 32 / 32 / 2 | 계속 추적 | 208 KB | `0804782af2d8db8c…` |
| [bags/scene7.tar.gz](bags/scene7.tar.gz) | 15.5 s | 226 / 218 / 219 / 17 | 추적 → 소실 | 1.5 MB | `5c62ea716ec7d1c6…` |
| [bags/scene8.tar.gz](bags/scene8.tar.gz) | 27.1 s | 406 / 407 / 336 / 29 | 추적 → 소실 → 복귀 | 2.7 MB | `403a9572e48be788…` |

전체 해시는 [bags/SHA256SUMS](bags/SHA256SUMS)에 있습니다.

토픽

| 토픽 | 타입 | 내용 |
|---|---|---|
| `/camera/camera/color/image_raw` | sensor_msgs/Image | 640×480 **rgb8** (OpenCV 처리 전 BGR로 변환 필요) |
| `/target` | geometry_msgs/PointStamped | x = ex, y = ey (-1~+1, 오른쪽·아래 +), z = 면적비 (0이면 미검출). header = 원본 영상 시각 |
| `/tracking_status` | std_msgs/String | IDLE / TRACKING / LOST |
| `/motor_cmd` | sensor_msgs/JointState | pan_joint, tilt_joint, position = Δrad |

### 1.3 대표 프레임 (`frames/`)

bag마다 처음부터 끝까지 고르게 5장을 BGR PNG로 뽑았습니다. bag을 풀지 않고 `hsv_calibrate.py`에 바로 넣을 수 있습니다. [../src/replay_bag.py](../src/replay_bag.py)가 생성합니다.

```
frames/scene1/scene1_0000.png … scene1_0169.png
frames/scene5/ … frames/scene8/   (파일 이름의 숫자 = bag 안의 영상 순번)
```

## 2. 접근 방법

모든 명령은 `lv2_module03/`에서 실행합니다.

```bash
# 무결성 확인
(cd data/bags && sha256sum -c SHA256SUMS)

# bag 풀기 (bags/<scene>/ 폴더가 생긴다. 풀린 폴더는 git에 넣지 않는다)
tar xzf data/bags/scene8.tar.gz -C data/bags

# bag 정보
source /opt/ros/lyrical/setup.bash
ros2 bag info data/bags/scene8

# 정지 영상으로 HSV 보정 (창에서 드래그 → HSV 백분위, s → config/realsense_<name>.yaml 저장)
python3 src/hsv_calibrate.py --source ros2_ws/src/realsense/test/data/lit_pillar_20261002.png --name lit

# bag 재처리 → results/ (검출 화면·보정 오차·연동 로그)
python3 src/replay_bag.py data/bags/scene8

# 실제 ROS 노드 연동 시험 (bag 영상 재생 → perception_node → dynamixel_move_node, 모터 출력 없음)
src/link_test.sh data/bags/scene8 link_scene8

# bag 영상을 ROS 토픽으로만 재생 (다른 노드와 직접 연동할 때)
ros2 bag play data/bags/scene8 --topics /camera/camera/color/image_raw
```

## 3. 새 입력 추가 방법

실제 D435로 새 장면을 기록할 때:

```bash
# 카메라 + 인지 + 제어 실행 (다른 터미널)
cd ros2_ws && source install/setup.bash && ros2 launch bringup bringup.launch.py

# 녹화 → 압축 → 해시 등록
RUN_ID=$(date +%Y%m%d_%H%M%S)_<장면>
ros2 bag record -s mcap -o data/bags/$RUN_ID --topics \
  /camera/camera/color/image_raw /camera/camera/color/camera_info /target /tracking_status /motor_cmd
tar czf data/bags/$RUN_ID.tar.gz -C data/bags $RUN_ID && rm -rf data/bags/$RUN_ID
(cd data/bags && sha256sum $RUN_ID.tar.gz >> SHA256SUMS)
```

그리고 위 1.2 표에 한 줄을 추가합니다. 압축 후 수십 MB를 넘으면 저장소 대신 공유 드라이브에 올리고 링크와 SHA256만 적습니다.
