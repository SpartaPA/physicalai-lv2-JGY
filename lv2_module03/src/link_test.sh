#!/usr/bin/env bash
# src/link_test.sh - 인지, 제어 노드 연동 시험 (카메라, 모터 없이)
#
# bag의 영상만 재생 -> perception_node(/target) -> dynamixel_move_node(/tracking_status, /motor_cmd)
# 를 실제 ROS 노드로 돌리고, 새로 나온 토픽을 녹화한 뒤 replay_bag.py로 결과를 만든다.
#
# 사용 (lv2_module03/ 에서):
#   src/link_test.sh <입력 bag 폴더> [RUN_ID]
# 출력:
#   results/logs/<RUN_ID>_launch.log      노드 실행 로그 (perception fps, 검출, FSM 전이)
#   results/logs/<RUN_ID>_link.log        영상 -> /target -> /tracking_status -> /motor_cmd 시간순
#   results/calibration_error/<RUN_ID>.csv, results/detection/<RUN_ID>/, results/summary.csv
set -eo pipefail

IN_BAG=$(realpath "${1:?입력 bag 폴더}")
RUN_ID=${2:-link_$(basename "$IN_BAG")_$(date +%Y%m%d_%H%M%S)}
MOD=$(cd "$(dirname "$0")/.." && pwd)
OUT_BAG=${TMPDIR:-/tmp}/$RUN_ID        # 녹화 bag은 크므로 저장소 밖에 둔다
LOGS=$MOD/results/logs
mkdir -p "$LOGS"

set +u
source /opt/ros/lyrical/setup.bash
source "$MOD/ros2_ws/install/setup.bash"
export ROS_DOMAIN_ID=${ROS_DOMAIN_ID:-77} ROS_LOCALHOST_ONLY=1   # 다른 로봇, PC 토픽과 섞이지 않게

cleanup() {
  [[ -n $REC_PID ]] && kill -TERM "$REC_PID" 2>/dev/null || true
  [[ -n $LAUNCH_PID ]] && kill -TERM "$LAUNCH_PID" 2>/dev/null || true
  sleep 3
  pkill -f "$MOD/ros2_ws/install/.*/(perception_node|dynamixel_move_node|dynamixel_controller)" 2>/dev/null || true
}
trap cleanup EXIT

# use_motor:=false -> 시리얼 없이 명령만 계산 (dynamixel_controller는 /dev/opencr 없음 오류를 남긴다)
ros2 launch bringup bringup.launch.py use_camera:=false use_motor:=false > "$LOGS/${RUN_ID}_launch.log" 2>&1 &
LAUNCH_PID=$!
sleep 4

rm -rf "$OUT_BAG"
ros2 bag record -s mcap -o "$OUT_BAG" \
  --topics /camera/camera/color/image_raw /target /tracking_status /motor_cmd > /dev/null 2>&1 &
REC_PID=$!
sleep 3

ros2 bag play "$IN_BAG" --topics /camera/camera/color/image_raw > /dev/null 2>&1
sleep 2
cleanup
REC_PID= LAUNCH_PID=

ros2 bag info "$OUT_BAG" | grep -E "Duration|Topic:" | tee -a "$LOGS/${RUN_ID}_launch.log"
python3 -W ignore "$MOD/src/replay_bag.py" "$OUT_BAG"
echo "녹화 bag: $OUT_BAG"
