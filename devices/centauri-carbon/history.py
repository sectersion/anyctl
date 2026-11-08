#!/usr/bin/env python
"""Centauri Carbon print history: list recent jobs, grab the newest thumbnail.
  python history.py [n]   # n entries (default 3); newest thumbnail -> history_thumb.jpg
"""
import asyncio, json, sys, time, urllib.parse, urllib.request, websockets
from centauri import HOST, ask

async def send(ws, cmd, data, label="", timeout=8):
    return await ask(ws, cmd, data, label, timeout)

async def main():
    a_video = "--video" in sys.argv
    args = [x for x in sys.argv[1:] if not x.startswith("--")]
    n = int(args[0]) if args else 3
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
            if a_video and e.get("TimeLapseVideoUrl"):
                print("TLP URL:", e["TimeLapseVideoUrl"])
                # wire truth (590.js): 323 takes {Url:[<device path>,…]}, replies
                # Data.Data.Data = [downloadable items]
                r = await send(ws, 323, {"Url": [e["TimeLapseVideoUrl"]]}, "323", 30)
                print("323 raw:", json.dumps(r, ensure_ascii=False))
                items = (r or {}).get("Data") or []
                for k, it in enumerate(items if isinstance(items, list) else [items]):
                    u = it if isinstance(it, str) else (it or {}).get("Url", "")
                    if not u: continue
                    u = u if u.startswith("http") else (
                        f"http://{HOST}" + urllib.parse.quote(u))  # UI encodes basename
                    try:
                        data = urllib.request.urlopen(
                            urllib.request.Request(u, headers={"User-Agent": "anyctl"}),
                            timeout=60).read()
                        open(f"tl_{k}.mp4", "wb").write(data)
                        print(f"tl_{k}.mp4: {len(data)} bytes ({u})")
                    except Exception as ex:
                        print("fetch failed:", ex, u)
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
