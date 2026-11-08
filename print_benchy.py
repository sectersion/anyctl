#!/usr/bin/env python
"""anyctl print — home, set speed, start a gcode already on the Centauri Carbon.
  python print_benchy.py [--speed 160] [--no-home] [filename-on-device]
"""
import argparse, asyncio, json, secrets, time, websockets

HOST = "192.168.0.120"
ID = "979d4C788A4a78bC777A870F1A02867A"
MB = "448e195701045b4000000c0000000000"

def env(cmd, data, rid=False):
    return json.dumps({"Id": ID if rid else "", "Data": {"Cmd": cmd, "Data": data,
        "RequestID": secrets.token_hex(16), "MainboardID": MB if rid else "",
        "TimeStamp": int(time.time()), "From": 1}})

async def send(ws, cmd, data, rid=False, label="", timeout=8):
    await ws.send(env(cmd, data, rid))
    end = time.time() + timeout
    while time.time() < end:
        try:
            m = json.loads(await asyncio.wait_for(ws.recv(), max(0.1, end - time.time())))
        except asyncio.TimeoutError:
            print(f"{label}: NO ACK"); return None
        d = m.get("Data", {})
        if d.get("Cmd") == cmd:
            print(f"{label}: {d.get('Data')}"); return d.get("Data")

async def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("filename", nargs="?",
                    default="/local/ECC_0.4_3DBenchy_Elegoo PLA _0.2_39m56s.gcode")
    ap.add_argument("--speed", type=int, default=100)
    ap.add_argument("--no-home", action="store_true")
    a = ap.parse_args()
    async with websockets.connect(f"ws://{HOST}:3030/websocket",
                                  origin=f"http://{HOST}", open_timeout=5) as ws:
        if not a.no_home:
            for ax in "ZXY":
                await send(ws, 402, {"Axis": ax}, True, f"home {ax}")
        if a.speed != 100:
            await send(ws, 403, {"PrintSpeedPct": a.speed}, False, f"speed {a.speed}%")
        r = await send(ws, 128, {"Filename": a.filename, "StartLayer": 0,
            "Calibration_switch": 1, "PrintPlatformType": 0, "Tlp_Switch": 1},
            True, "START")
        if r and r.get("Ack") == 0:
            print("print started:", a.filename)
            await asyncio.sleep(4)
            await send(ws, 0, {}, False, "status")

asyncio.run(main())
