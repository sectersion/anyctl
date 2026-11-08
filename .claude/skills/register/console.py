#!/usr/bin/env python
"""Interactive serial console — raw both ways, and Ctrl-C goes to the DEVICE.
  python console.py COM3 [baud=115200] [--log boot.log]
Boot countdowns are 1-3 seconds and Ctrl-C must reach the bootloader, so this
script never treats Ctrl-C as interrupt: it forwards byte 0x03. Quit is Ctrl-] .
Hold a key (e.g. '4') during power-on to spam it through the U-Boot window;
Enter sends \\r — if a Linux shell ignores it, press Ctrl-J for \\n.
RX/TX log is raw bytes to --log file (pipe to xxd if you need it printable).
"""
import sys, threading, time

def main():
    a = sys.argv[1:]
    if not a or a[0].startswith("--"):
        print(__doc__); return 1
    port = a[0]
    baud = int(a[1]) if len(a) > 1 and not a[1].startswith("--") else 115200
    log = a[a.index("--log") + 1] if "--log" in a else None
    try:
        import serial
    except ImportError:
        print("pip install pyserial"); return 1
    s = serial.Serial(port, baud, timeout=0.05)
    f = open(log, "ab", buffering=0) if log else None
    print(f"# {port} @ {baud} 8N1 — listening; keystrokes are forwarded raw. "
          f"Ctrl-C -> device, Ctrl-] quits.", flush=True)
    stop = threading.Event()

    def rx():
        while not stop.is_set():
            d = s.read(2048)
            if d:
                sys.stdout.write(d.decode("utf-8", "replace")); sys.stdout.flush()
                if f: f.write(d)
    threading.Thread(target=rx, daemon=True).start()

    restore = None
    try:
        import msvcrt
        get = msvcrt.getwch
    except ImportError:
        import tty, termios
        fd = sys.stdin.fileno(); old = termios.tcgetattr(fd)
        tty.setraw(fd); restore = lambda: termios.tcsetattr(fd, termios.TCSADRAIN, old)
        get = lambda: sys.stdin.read(1)
    try:
        while not stop.is_set():
            ch = get()
            if ch == "\x03":            # Ctrl-C: interrupt the DEVICE, not us
                s.write(b"\x03")
            elif ch == "\x1d":          # Ctrl-]: quit
                stop.set()
            elif ch in ("\r", "\n"):
                s.write(b"\r")
            elif ch:
                s.write(ch.encode("latin-1", "ignore"))
    finally:
        if restore: restore()
        if f: f.close(); print(f"# logged to {log}")
        s.close()
    return 0

if __name__ == "__main__":
    sys.exit(main())
