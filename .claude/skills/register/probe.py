#!/usr/bin/env python
"""First-contact probes for an unknown device. stdlib; optional pyserial/websockets.
  python probe.py serial                       # list COM ports
  python probe.py tcp 192.168.1.1 22,23,80     # connect + banner-grab per port
  python probe.py http http://192.168.1.1/     # GET: status, content-type, head
  python probe.py ws ws://192.168.1.1:3030/websocket [secs]   # LISTEN only (law 1)
"""
import socket, sys, time, urllib.request

def serial():
    try:
        from serial.tools import list_ports
    except ImportError:
        sys.exit("no pyserial — pip install pyserial, or PowerShell: "
                 "Get-PnpDevice -Class Ports,USB | ? FriendlyName")
    for p in list_ports.comports():
        print(f"{p.device:8} {p.description}")

def tcp(host, ports):
    for pt in ports.split(","):
        s = socket.socket(); s.settimeout(2)
        try:
            s.connect((host, int(pt)))
            try:
                data = s.recv(4096)
            except socket.timeout:
                data = b""
            print(f"{pt:>6}/open   banner: {data[:200]!r}")
        except Exception as e:
            print(f"{pt:>6}/closed ({e.__class__.__name__})")
        finally:
            s.close()

def http(url):
    req = urllib.request.Request(url, headers={"User-Agent": "anyctl-probe"})
    try:
        r = urllib.request.urlopen(req, timeout=5)
        body = r.read(2000)
        print(r.status, r.headers.get("Content-Type"), r.headers.get("Server"))
        print(body[:500].decode("utf-8", "replace"))
    except Exception as e:
        print("fail:", e)

def ws(url, secs=10):
    try:
        import asyncio, websockets
    except ImportError:
        sys.exit("no websockets — pip install websockets")
    async def listen():
        async with websockets.connect(url, open_timeout=5) as w:
            end = time.time() + int(secs)
            while time.time() < end:
                try:
                    f = await asyncio.wait_for(w.recv(), max(0.1, end - time.time()))
                    print(str(f)[:400])
                except asyncio.TimeoutError:
                    break
    print(f"# listening {secs}s, sending nothing — unsolicited traffic = free ground truth")
    try:
        asyncio.run(listen())
    except Exception as e:
        print("fail:", e)

cmds = {"serial": serial, "tcp": tcp, "http": http, "ws": ws}
if __name__ == "__main__":
    if len(sys.argv) < 2 or sys.argv[1] not in cmds:
        print(__doc__); sys.exit(1)
    cmds[sys.argv[1]](*sys.argv[2:])
