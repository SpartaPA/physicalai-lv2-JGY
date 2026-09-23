[lv2_module01 OpenCR · 다이나믹셀 통합 과제]

- 모듈 1 임베디드 제어 기초 과제(4문제) 제출 폴더다.
- 과제 원문은 [과제_발제_OpenCR_다이나믹셀_4문제.md](https://github.com/SpartaPA/physicalai-lv2-assignments/blob/main/모듈1_임베디드제어기초/과제_발제_OpenCR_다이나믹셀_4문제.md)이다.
- 문제별 설정·기록·해석과 작업 경과는 [report.md](report.md)에 정리했다.

[폴더 구성]

- `README.md`: 환경과 실행 방법을 적은 이 파일이다.
- `report.md`: 작업 경과와 문제 1~4의 설정, 기록, 해석을 적는다.
- `tools/dxl_log.py`: 라즈베리파이에서 OpenCR에 명령 한 줄을 보내고 출력을 파일로 저장하는 스크립트다. 기록 시간이 끝나거나 Ctrl+C를 누르면 정지 명령 `x`를 자동으로 보낸다.
- `tools/dxltable.py`: 실행 로그에서 문제 2의 세 시점 오차 표와 문제 3의 A·B 비교표를 Markdown으로 뽑는 스크립트다.
- `tools/run_module1.sh`: 아래 준비부터 결과 묶기까지의 순서를 단계마다 확인을 받으며 한 번에 진행하는 스크립트다. `bash ~/pa/run_module1.sh`로 전체를, `bash ~/pa/run_module1.sh runA`처럼 단계 이름을 주면 그 단계만 실행한다.
- `results/`: 환경 확인, 업로드, 실행 A·B 기록을 모아 두는 곳이다.

[장비와 환경]

- 라즈베리파이는 호스트명 `pa16`, wlan0 주소 10.2.12.74이고, Ubuntu 22.04.5 LTS(커널 5.15.0-1061-raspi, aarch64)가 설치되어 있다.
- PC는 10.2.12.62이고 PuTTY로 SSH 접속과 파일 복사에만 쓴다.
- 제어기는 OpenCR 1.0이며 라즈베리파이 USB에 연결한다. 실제로 `/dev/ttyACM0`(USB ID `0483:5740`, ROBOTIS OpenCR Virtual ComPort)으로 잡혔다.
- 모터는 다이나믹셀 XM430-W350(모델 1020), ID 12, 1 Mbps, Protocol 2.0이다.
- 예제는 제공 P 제어 예제 `opencr_position_p`를 쓴다.
- 업로더는 ROBOTIS `opencr_ld`(commit `68ec75d`)다. ARM64용 배포본이 없어서 라즈베리파이에서 `gcc`로 빌드한다.
- 시리얼 통신은 pyserial 3.5로 115200 bps를 쓴다.
- 펌웨어는 컴파일하지 않았다. 과제 저장소의 [firmware/opencr_position_p.ino.bin](https://github.com/SpartaPA/physicalai-lv2-assignments/tree/main/모듈1_임베디드제어기초/firmware)(SHA-256 `c68eddf221d60cfc61767d1937120db2f3d74445dcc5d30b851d5be850df4f7f`)을 그대로 올린다. 수정하지 않은 제공 파일이라 이 폴더에는 복사하지 않았다.
- 아래 준비 단계의 `make`는 펌웨어가 아니라, 이 .bin을 OpenCR에 써 넣는 업로드 도구를 만드는 단계다.
- 과제 규칙대로 업로드, 시리얼 송수신, 로그 저장은 모두 라즈베리파이에서 한다.
- 라즈베리파이 로그인 화면에 `Failed to connect to changelogs.ubuntu.com`이 떴고 시스템 시각도 2024-09-11로 맞지 않았다. 인터넷이 안 될 수 있어서 필요한 파일을 PC에서 묶어 `scp`로 넘기는 방식으로 준비했다.

[파일 옮기기 (PC)]

- PC 터미널에서 `scp ~/pa_bundle.tgz pa16@10.2.12.74:~/`로 묶음 파일을 라즈베리파이에 보낸다.
- `pa_bundle.tgz`에는 제공 펌웨어 .bin과 `SHA256SUMS`, `tools/`의 세 스크립트, `opencr_ld` 소스, `pyserial-3.5-py2.py3-none-any.whl`이 들어 있다.
- 외부 소스가 섞여 있어서 묶음 파일은 PC 홈 폴더에만 두고 저장소에는 올리지 않았다.

[한 번에 실행 (PuTTY)]

- `bash ~/pa/run_module1.sh`를 실행하면 준비, 환경 확인, 업로드, 준비 상태, 실행 A, 복귀와 실행 B, 표 만들기, 결과 묶기를 순서대로 진행한다. 묶음을 처음 풀 때는 `mkdir -p ~/pa && tar xzf ~/pa_bundle.tgz -C ~/pa`를 먼저 한다.
- 모터가 움직이기 전마다 Enter 확인을 받고, 업로드 성공 문구가 없거나 FAULT가 나면 그 자리에서 멈춘다.
- 실행이 끝날 때마다 측정 행 수와 `STOP: user`를 검사하고, 육안 정지 확인 결과를 로그 끝에 한 줄 남긴다.
- 결과는 `~/lv2_module1_results.tgz`로 묶이며, PC에서 `scp pa16@10.2.12.74:~/lv2_module1_results.tgz ~/`로 가져온다.
- 아래 항목들은 이 스크립트가 하는 일을 단계별로 풀어 쓴 것이다.

[라즈베리파이 준비 (PuTTY)]

- `mkdir -p ~/pa && tar xzf ~/pa_bundle.tgz -C ~/pa && cd ~/pa && sha256sum -c SHA256SUMS`로 압축을 풀고 펌웨어 체크섬을 확인한다.
- pyserial이 없으면 `export PYTHONPATH=$HOME/pa/pyserial-3.5-py2.py3-none-any.whl`로 wheel 경로를 추가한다. pip 없이도 import된다. 매번 쓰려면 같은 줄을 `~/.bashrc`에 넣는다.
- `make -C ~/pa/opencr_ld && file ~/pa/opencr_ld/opencr_ld`로 업로더를 빌드하고, 결과가 ARM aarch64 실행 파일인지 확인한다.
- `id -nG`에 `dialout`이 없으면 `sudo usermod -aG dialout $USER`를 실행한 뒤 SSH로 다시 접속한다.

[환경 확인 기록]

- `mkdir -p ~/lv2_module1/results && cd ~/lv2_module1/results`로 결과 폴더를 만든다.
- `{ hostname; grep PRETTY /etc/os-release; uname -m; id -nG; lsusb; ls -l /dev/ttyACM*; test -r /dev/ttyACM0 && test -w /dev/ttyACM0 && echo "Port access OK"; } 2>&1 | tee 환경확인.txt`로 호스트명, OS, 아키텍처, 그룹, 포트, 권한을 한 파일에 남긴다.

[펌웨어 업로드]

- `~/pa/opencr_ld/opencr_ld /dev/ttyACM0 115200 ~/pa/opencr_position_p.ino.bin 1 2>&1 | tee upload.log`로 업로드한다.
- `grep -E "CRC OK|\[OK\] Download" upload.log`의 결과에 두 줄이 모두 나와야 업로드 성공이다. 이 업로더는 오류가 있어도 종료 코드가 성공으로 보일 수 있어서 출력으로 판단한다.
- `python3 ~/pa/dxl_log.py ready.log 8`을 실행한 뒤 8초 안에 OpenCR RESET을 눌러 `READY` 줄을 기록한다.
- `python3 ~/pa/dxl_log.py ready2.log 2 "k 0.5"`로 `P SET Kp=0.5000` 응답이 오는지 확인한다. `FAULT`가 나오면 모델, ID, 통신 속도, 전원을 확인한다.
- 업로더가 멈추면 SW2를 누른 채 RESET을 눌렀다 놓고 SW2를 놓아 복구 모드로 들어간 뒤 다시 올린다.

[실행 A, 복귀, 실행 B]

- 펌웨어 명령 형식은 `s <Kp> <속도상한 deg/s|max> <상대각 deg>`다. 시작 위치를 0°로 잡고 2초 뒤에 목표각으로 바꾸며, `x`를 보내면 즉시 정지한다.
- 실행 A는 `python3 ~/pa/dxl_log.py 실행A.log 15 "s 0.5 20 30"`이다. Kp 0.5, 속도 상한 20 °/s, 목표 +30°로 돌린다.
- 복귀는 `python3 ~/pa/dxl_log.py 복귀.log 15 "s 0.5 20 -30"`이다. 실행 B를 A와 같은 자세에서 시작하려고 되돌린다.
- 실행 B는 `python3 ~/pa/dxl_log.py 실행B.log 15 "s 2 20 30"`이다. Kp만 2로 바꾸고 나머지는 A와 같다.
- 로그 끝의 `STOP: user` 줄로 정지를 확인하고, 모터가 실제로 멈췄는지 눈으로도 확인한다. SSH 창을 닫는 것은 정지가 아니다.

[표 만들기]

- `python3 ~/pa/dxltable.py 실행A.log`로 문제 2의 초기, 중간, 마지막 시점 오차 표를 만든다.
- `python3 ~/pa/dxltable.py 실행A.log 실행B.log`로 문제 3의 같은 시각 비교표를 만든다.

[결과 파일]

- `results/01_ssh_login_pa16.png`는 PuTTY 로그인 화면으로 호스트, OS, 아키텍처를 보여 준다.
- `results/환경확인.txt`에는 호스트명, Ubuntu 버전, 아키텍처, dialout 그룹, OpenCR 포트(`/dev/ttyACM0`)와 권한, 업로더 아키텍처, 펌웨어 체크섬이 들어 있다.
- `results/upload.log`에는 라즈베리파이에서 한 업로드 출력이 있고 `CRC OK`와 `[OK] Download`가 찍혀 있다.
- `results/ready.log`는 RESET 뒤 READY 줄을 놓쳐 헤더만 남았다. `results/ready2.log`에 FAULT 없는 `P SET` 응답이 있어 이것을 준비 상태 증거로 쓴다.
- `results/실행A.log`는 Kp 0.5 실행 기록이고, `results/복귀.log`는 시작 자세로 되돌린 기록, `results/실행B.log`는 Kp 2 실행 기록이다. 세 파일 모두 끝에 `STOP: user`와 육안 정지 확인이 있다.
- `results/문제2_표.md`와 `results/문제3_표.md`는 라즈베리파이에서 `dxltable.py`가 만든 출력을 그대로 둔 것이다. report.md에는 같은 내용을 글로 옮겼다.
- 라즈베리파이 시계가 맞지 않아 로그 안 시각은 2024-09-12로 찍혀 있다. 실제 수행일은 2026-09-23이다.
