#!/usr/bin/env bash
# 모듈 1 실측 순서를 한 번에 진행한다. 라즈베리파이(PuTTY)에서 실행.
#   bash ~/pa/run_module1.sh          전체 순서
#   bash ~/pa/run_module1.sh <단계>   setup | env | upload | ready | runA | runB | tables | pack
# 결과는 ~/lv2_module1/results/ 에 쌓인다.
set -u -o pipefail

PA="$HOME/pa"
OUT="$HOME/lv2_module1/results"
mkdir -p "$OUT"
cd "$OUT" || exit 1

say()  { printf '\n==== %s ====\n' "$*"; }
fail() { printf '\n[중단] %s\n' "$*"; exit 1; }
ask()  { read -r -p "$* [Enter=계속, Ctrl+C=중단] " _; }

find_port() {
  PORT=$(ls /dev/ttyACM* 2>/dev/null | head -1)
  [ -n "$PORT" ] || fail "/dev/ttyACM* 가 없다. OpenCR USB가 라즈베리파이에 꽂혔는지 확인."
  export PORT
  echo "사용 포트: $PORT"
}

find_uploader() {
  for u in "$PA/opencr_ld/opencr_ld" \
           "$HOME/pa-opencr-build/uploader-src/arduino/opencr_develop/opencr_ld/opencr_ld" \
           "$HOME/opencr-uploader-src/arduino/opencr_develop/opencr_ld/opencr_ld"; do
    [ -x "$u" ] && file "$u" | grep -q aarch64 && { UPLOADER="$u"; return 0; }
  done
  return 1
}

step_setup() {
  say "0. 준비: 묶음 풀기, pyserial, 업로더"
  if [ ! -f "$PA/dxl_log.py" ]; then
    [ -f "$HOME/pa_bundle.tgz" ] || fail "~/pa_bundle.tgz 가 없다. PC에서 scp로 먼저 보낼 것."
    mkdir -p "$PA" && tar xzf "$HOME/pa_bundle.tgz" -C "$PA"
  fi
  (cd "$PA" && sha256sum -c SHA256SUMS) || fail "펌웨어 체크섬 불일치"
  if ! python3 -c "import serial" 2>/dev/null; then
    export PYTHONPATH="$PA/pyserial-3.5-py2.py3-none-any.whl"
    grep -q pyserial-3.5 ~/.bashrc || echo "export PYTHONPATH=$PYTHONPATH" >> ~/.bashrc
  fi
  python3 -c "import serial; print('pyserial', serial.VERSION)" || fail "pyserial import 실패"
  if find_uploader; then
    echo "기존 업로더 사용: $UPLOADER"
  else
    command -v gcc >/dev/null && command -v make >/dev/null \
      || fail "gcc/make 가 없다. 인터넷이 되면 sudo apt install -y build-essential"
    make -C "$PA/opencr_ld" >"$PA/opencr_ld_build.log" 2>&1 || fail "업로더 빌드 실패: $PA/opencr_ld_build.log"
    find_uploader || fail "업로더가 aarch64 실행 파일이 아니다"
    echo "업로더 빌드 완료: $UPLOADER"
  fi
  id -nG | grep -qw dialout || fail "dialout 그룹 없음: sudo usermod -aG dialout \$USER 후 SSH 재접속"
}

step_env() {
  say "1. 환경 확인 → 환경확인.txt"
  find_port
  find_uploader || fail "업로더 없음. setup 단계부터."
  { echo "## 기록 시각 (라즈베리파이 시계, NTP 미동기 가능)"; date
    echo "## host";  hostname; grep PRETTY /etc/os-release; uname -r; uname -m
    echo "## user";  whoami; id -nG
    echo "## usb";   lsusb
    echo "## port";  ls -l /dev/ttyACM*
    udevadm info --query=property --name="$PORT" | grep -E 'ID_VENDOR=|ID_MODEL=|ID_SERIAL=' || true
    test -r "$PORT" && test -w "$PORT" && echo "Port access OK: $PORT"
    echo "## uploader"; echo "$UPLOADER"; file "$UPLOADER"
    echo "## firmware"; sha256sum "$PA/opencr_position_p.ino.bin"; } 2>&1 | tee 환경확인.txt
}

step_upload() {
  say "2. 펌웨어 업로드 → upload.log"
  find_port
  find_uploader || fail "업로더 없음. setup 단계부터."
  ask "모터 고정, 전원 차단 위치 확인. 업로드를 시작할까?"
  "$UPLOADER" "$PORT" 115200 "$PA/opencr_position_p.ino.bin" 1 2>&1 | tee upload.log
  if grep -q "CRC OK" upload.log && grep -q "\[OK\] Download" upload.log; then
    echo "업로드 성공 확인: CRC OK, [OK] Download"
  else
    fail "업로드 성공 문구가 없다. SW2를 누른 채 RESET → 놓고 → SW2 놓기(복구 모드) 후 upload 단계 재실행."
  fi
  sleep 3
}

step_ready() {
  say "3. 준비 상태 → ready.log, ready2.log"
  find_port
  echo "아래가 시작되면 8초 안에 OpenCR RESET 버튼을 한 번 누른다."
  ask "준비됐나?"
  python3 "$PA/dxl_log.py" ready.log 8
  sleep 2; find_port
  python3 "$PA/dxl_log.py" ready2.log 3 "k 0.5"
  grep -q "FAULT" ready.log ready2.log && fail "FAULT 발생. 모델/ID 12/1 Mbps/전원/케이블 확인 후 RESET."
  grep -q "READY" ready.log || echo "(READY 줄을 놓쳤다. 필요하면 ready 단계만 다시 실행)"
  grep -q "P SET Kp=0.5000" ready2.log && echo "펌웨어 응답 정상 (P SET)" || fail "P SET 응답 없음"
}

check_run() {  # $1=로그 파일
  local n
  n=$(grep -c '^target_deg:' "$1")
  echo "측정 행 수: $n"
  [ "$n" -ge 5 ] || echo "(주의) 측정 행이 5개 미만"
  grep -q "STOP: user" "$1" && echo "정지 기록 확인: STOP: user" || echo "(주의) STOP 기록 없음. 모터를 직접 확인."
  grep -E "FAULT|DXL lib_error" "$1" && fail "실행 중 FAULT"
  read -r -p "모터가 실제로 멈췄나? (y/n) " seen
  echo "# 육안 정지 확인: $seen ($(date +%T))" >> "$1"
}

step_runA() {
  say "4. 실행 A: Kp 0.5, 20 deg/s, +30 deg → 실행A.log"
  find_port
  ask "혼에 테이프 표시, +30° 범위 비움, 모터 고정 확인. 실행 A 시작?"
  python3 "$PA/dxl_log.py" 실행A.log 15 "s 0.5 20 30"
  check_run 실행A.log
}

step_runB() {
  say "5. 복귀 후 실행 B: Kp 2 (나머지 A와 동일) → 복귀.log, 실행B.log"
  find_port
  ask "시작 자세로 되돌린다 (-30°). 시작?"
  python3 "$PA/dxl_log.py" 복귀.log 15 "s 0.5 20 -30"
  check_run 복귀.log
  ask "테이프 표시가 처음 자리로 왔는지 확인. 실행 B 시작?"
  python3 "$PA/dxl_log.py" 실행B.log 15 "s 2 20 30"
  check_run 실행B.log
}

step_tables() {
  say "6. 표 만들기 → 문제2_표.md, 문제3_표.md"
  [ -f 실행A.log ] && python3 "$PA/dxltable.py" 실행A.log | tee 문제2_표.md
  [ -f 실행A.log ] && [ -f 실행B.log ] && python3 "$PA/dxltable.py" 실행A.log 실행B.log | tee 문제3_표.md
}

step_pack() {
  say "7. 결과 묶기 → ~/lv2_module1_results.tgz"
  tar czf "$HOME/lv2_module1_results.tgz" -C "$HOME/lv2_module1" results
  ls -l "$HOME/lv2_module1_results.tgz"; ls -l "$OUT"
  echo "PC에서: scp pa16@$(hostname -I | awk '{print $1}'):~/lv2_module1_results.tgz ~/"
}

case "${1:-all}" in
  all)    step_setup; step_env; step_upload; step_ready; step_runA; step_runB; step_tables; step_pack ;;
  setup|env|upload|ready|runA|runB|tables|pack) "step_$1" ;;
  *) fail "알 수 없는 단계: $1" ;;
esac
