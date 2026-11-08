#!/usr/bin/env python
"""Centauri Carbon file ops — 258 list, 259 delete, 257 rename, 260 detail.
  python files.py ls
  python files.py rm <name substring>
  python files.py mv <path> <newpath>
  python files.py detail <path>
"""
import asyncio, json, sys, websockets
from centauri import HOST, ask

async def main():
    op = sys.argv[1] if len(sys.argv) > 1 else "ls"
    async with websockets.connect(f"ws://{HOST}:3030/websocket",
                                  origin=f"http://{HOST}", open_timeout=5) as ws:
        if op == "ls":
            r = await ask(ws, 258, {"Url": "/local"}, "258")
            print(json.dumps(r, ensure_ascii=False)[:3000])
        elif op == "rm":
            r = await ask(ws, 258, {"Url": "/local"}, "258")
            cands = [e for e in (r or {}).get("FileList", [])
                     if sys.argv[2].lower() in json.dumps(e).lower()]
            print(json.dumps(cands, ensure_ascii=False)[:1500])
            if not cands:
                print("no match"); return 1
            if "--yes" not in sys.argv:
                print(f"refusing: {len(cands)} match(es) — re-run with --yes"); return 2
            paths = [e["name"] for e in cands]
            ack = await ask(ws, 259, {"FileList": paths}, "259")
            print("259:", json.dumps(ack, ensure_ascii=False)[:200])
            after = await ask(ws, 258, {"Url": "/local"}, "258")
            gone = all(e["name"] not in str(after) for e in cands)
            print("verified removed" if gone else "STILL PRESENT?", )
        elif op == "mv":
            print("257:", json.dumps(await ask(ws, 257, {"SrcPath": sys.argv[2],
                  "TargetPath": sys.argv[3]}, "257"), ensure_ascii=False)[:200])
        elif op == "detail":
            print(json.dumps(await ask(ws, 260, {"Url": sys.argv[2]}, "260"),
                             ensure_ascii=False)[:2000])

sys.exit(asyncio.run(main()) or 0)
