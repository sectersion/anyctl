#!/usr/bin/env python
"""Watch a Centauri Carbon print; print one line per meaningful change; exit on finish.
  python watch.py            # exit 0 = complete, exit 2 = paused/stopped/lost
"""
import asyncio, json, secrets, sys, time, websockets
HOST = "192.168.0.120"
def env(cmd, data):
    return json.dumps({"Id":"","Data":{"Cmd":cmd,"Data":data,
        "RequestID":secrets.token_hex(16),"MainboardID":"","TimeStamp":int(time.time()),"From":1}})
async def main():
    last = None
    seen_printing = False
    while True:
        try:
            ws = await websockets.connect(f"ws://{HOST}:3030/websocket",
                                          origin=f"http://{HOST}", open_timeout=5)
            break
        except Exception as e:
            print(f"(connect: {e})", file=sys.stderr); await asyncio.sleep(10)
    async def beat():
        while True:
            await asyncio.sleep(15)
            await ws.send("ping")
    hb = asyncio.create_task(beat())
    try:
        while True:
            try:
                m = json.loads(await asyncio.wait_for(ws.recv(), 30))
            except asyncio.TimeoutError:
                await ws.send(env(0, {})); continue
            except Exception:
                return 2
            if "Status" not in m: continue
            s = m["Status"]; pi = s["PrintInfo"]
            key = (tuple(s["CurrentStatus"]), pi["Filename"],
                   pi["CurrentLayer"] // 10, int(pi["Progress"] // 10))
            if key == last: continue
            last = key
            line = (f"{time.strftime('%H:%M:%S')} state={list(s['CurrentStatus'])} "
                    f"L{pi['CurrentLayer']}/{pi['TotalLayer']} prog={pi['Progress']} "
                    f"nozzle={s['TempOfNozzle']:.0f}/{s['TempTargetNozzle']:.0f} "
                    f"bed={s['TempOfHotbed']:.0f}/{s['TempTargetHotbed']:.0f} file={pi['Filename']!r}")
            print(line, flush=True)
            if 13 in s["CurrentStatus"] or pi["Status"] == 13:
                seen_printing = True
            if pi["Progress"] >= 100 or (seen_printing and 9 in s["CurrentStatus"]):
                print("COMPLETE"); return 0
            if any(x in s["CurrentStatus"] for x in (5, 6, 8, 14)):
                print("PAUSED/STOPPED"); return 2
    finally:
        hb.cancel()
sys.exit(asyncio.run(main()))
