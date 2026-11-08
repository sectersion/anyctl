#!/usr/bin/env python
"""Kenwood CAT client (TS-480 family). ASCII commands ending ';'.
  python cat.py COM9                 # status (IF; + ID;)
  python cat.py COM9 --listen 5      # dump raw traffic N seconds (listen first!)
  python cat.py COM9 --cmd "MD2;"    # send any raw command
  python cat.py COM9 --freq 14.250   # FA<11-digit Hz>;
  python cat.py COM9 --tx | --rx     # PTT — TX asks first (it's your callsign)
"""
import argparse, sys, time
import serial

def parse_if(s):
    """IF; reply: 'IF' + VFO(1) + freq(11) + mode(2) + passband(3) + ... 35 chars."""
    f = s.strip().split(";", 1)[0]
    if not f.startswith("IF") or len(f) < 19: return None
    return {"vfo": "AB"[int(f[2])] if f[2] in "01" else f[2],
            "freq": int(f[3:14]) / 1e6, "mode": f[14:16], "pbf": f[16:19]}

def talk(ser, cmd, wait=1.0):
    ser.reset_input_buffer()
    ser.write(cmd.encode())
    buf, end = b"", time.time() + wait
    while time.time() < end:
        if ser.in_waiting:
            buf += ser.read(ser.in_waiting); end = time.time() + 0.3
        elif buf.rstrip().endswith(b";"):
            break
    return buf.decode(errors="replace").strip()

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("port"); ap.add_argument("--baud", type=int, default=9600)
    ap.add_argument("--cmd"); ap.add_argument("--freq", type=float)
    ap.add_argument("--tx", action="store_true"); ap.add_argument("--rx", action="store_true")
    ap.add_argument("--listen", type=float)
    a = ap.parse_args()
    ser = serial.Serial(a.port, a.baud, timeout=0.2)
    try:
        if a.listen:
            end = time.time() + a.listen
            while time.time() < end:
                line = ser.readline().decode(errors="replace").strip()
                if line: print(line, flush=True)
        elif a.cmd:  print(talk(ser, a.cmd))
        elif a.freq: print(talk(ser, f"FA{int(round(a.freq*1e6)):011d};"))
        elif a.tx or a.rx:
            if a.tx and "--yes" not in sys.argv:
                input("TRANSMIT — type yes to key the radio: ") or sys.exit("aborted")
            print(talk(ser, "TX;" if a.tx else "RX;"))
        else:
            raw = talk(ser, "IF;")
            st = parse_if(raw)
            print(raw)
            if st: print(f"-> VFO {st['vfo']}  {st['freq']:.6f} MHz  mode {st['mode']}  pbf {st['pbf']}")
            print(talk(ser, "ID;"))
    finally:
        ser.close()

main()
