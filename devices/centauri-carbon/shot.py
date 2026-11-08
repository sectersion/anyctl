#!/usr/bin/env python
"""Shot the Centauri Carbon webcam to a JPEG.  python shot.py [out.jpg]
  - python shot.py out.jpg            # fast path: one MJPEG frame from :3031/video
  - python shot.py --warm out.jpg     # also enable streaming via WS Cmd 386 and keep it on
"""
import argparse, asyncio, sys, time
import urllib.request
from centauri import HOST, env

def grab(host, port=3031, path="/video", secs=8.0):
    """Pull the MJPEG stream; save bytes from the first JPEG SOI marker past the next."""
    req = urllib.request.Request(f"http://{host}:{port}{path}",
                                 headers={"User-Agent": "curl/8"})
    buf, start = b"", time.time()
    with urllib.request.urlopen(req, timeout=10) as r:
        while time.time() - start < secs:
            buf += r.read(8192)
            a = buf.find(b"\xff\xd8\xff")                    # JPEG start
            if a >= 0:
                b2 = buf.find(b"\xff\xd8\xff", a + 3)        # next frame = boundary
                if b2 > a:
                    open(sys.argv[-1] if sys.argv[-1].endswith(".jpg") else "shot.jpg",
                         "wb").write(buf[a:b2])
                    return b2 - a
                if len(buf) > 800_000:                        # stream end marker never came
                    open("shot.jpg", "wb").write(buf[a:])
                    return len(buf) - a
    raise RuntimeError("no JPEG frame seen in stream")

async def enable_video(host, on=True):
    import websockets
    msg = env(386, {"Enable": 1 if on else 0})
    try:
        async with websockets.connect(f"ws://{host}:3030/websocket",
                                      origin=f"http://{host}", open_timeout=5) as ws:
            await ws.send(msg)
            await asyncio.wait_for(ws.recv(), 5)
    except Exception as e:
        print("ws enable failed:", e, file=sys.stderr)

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--warm", action="store_true", help="enable streaming via WS first")
    ap.add_argument("--host", default=HOST)
    ap.add_argument("out", nargs="?", default="shot.jpg")
    a = ap.parse_args()
    sys.argv[-1] = a.out
    if a.warm:
        asyncio.run(enable_video(a.host))
        time.sleep(1.5)
    n = grab(a.host)
    print(f"{a.out}: {n} bytes")
