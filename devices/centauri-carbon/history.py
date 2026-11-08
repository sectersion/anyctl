#!/usr/bin/env python
"""Centauri Carbon print history: list recent jobs, grab the newest thumbnail.
  python history.py [n]   # n entries (default 3); newest thumbnail -> history_thumb.jpg
"""
import asyncio, json, sys, time, urllib.request, websockets
from centauri import HOST, env

async def send(ws, cmd, data, label="", timeout=8):
    await ws.send(env(cmd, data, True))
    end = time.time() + timeout
    while time.time() < end:
        try:
            m = json.loads(await asyncio.wait_for(ws.recv(), max(0.1, end-time.time())))
        except asyncio.TimeoutError:
            print(f"{label}: NO REPLY"); return None
        d = m.get("Data", {})
        if d.get("Cmd") == cmd:
            return d.get("Data")

async def main():
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 3
    async with websockets.connect(f"ws://{HOST}:3030/websocket",
                                  origin=f"http://{HOST}", open_timeout=5) as ws:
        h = await send(ws, 320, {}, "320")
        ids = (h or {}).get("HistoryData") or []
        print(f"{len(ids)} history entries")
        if not ids: return
        d = await send(ws, 321, {"Id": ids[:n]}, "321")   # newest first on the wire
        det = (d or {}).get("HistoryDetailList") or []
        for e in det:                      # dump real field names — verify pass
            print(json.dumps(e, ensure_ascii=False)[:600], "\n---")
        for e in det:                      # newest = first entry
            t = e.get("Thumbnail") or ""
            if t:
                url = t if t.startswith("http") else f"http://{HOST}{t}"
                try:
                    req = urllib.request.Request(url, headers={"User-Agent": "anyctl"})
                    data = urllib.request.urlopen(req, timeout=10).read()
                    open("history_thumb.jpg", "wb").write(data)
                    print(f"history_thumb.jpg: {len(data)} bytes ({url})")
                except Exception as ex:
                    print("thumb fetch failed:", ex, url)
                break

asyncio.run(main())
