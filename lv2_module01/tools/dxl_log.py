#!/usr/bin/env python3
# 사용: python3 ~/dxl_log.py <출력파일> <기록초> ["명령"]
# 명령이 있으면 끝나거나 Ctrl+C 시 x(정지)를 자동 전송한다.
import os, sys, time, serial
out, secs = sys.argv[1], float(sys.argv[2])
cmd = sys.argv[3] if len(sys.argv) > 3 else ""
PORT = os.environ.get("PORT", "/dev/ttyACM0")
def open_port():
    while True:
        try: return serial.Serial(PORT, 115200, timeout=0.1)
        except serial.SerialException: time.sleep(0.2)
f = open(out, "w")
def log(s): print(s, flush=True); f.write(s + "\n"); f.flush()
log("# %s host=%s port=%s cmd=%r" % (time.strftime("%F %T"), os.uname().nodename, PORT, cmd))
s = open_port(); time.sleep(0.3); s.reset_input_buffer()
if cmd: s.write((cmd + "\n").encode())
t0 = time.time()
try:
    while time.time() - t0 < secs:
        try: line = s.readline()
        except serial.SerialException: s.close(); s = open_port(); continue
        if line: log(line.decode(errors="replace").rstrip())
finally:
    if cmd:
        s.write(b"x"); t1 = time.time()
        while time.time() - t1 < 1.5:
            line = s.readline()
            if line: log(line.decode(errors="replace").rstrip())
    f.close()
