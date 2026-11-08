"""Shared bits for Centauri Carbon drivers.
Env overrides: CENTAURI_HOST, CENTAURI_ID (board serial), CENTAURI_MB (mainboard ID)."""
import asyncio, json, os, secrets, time

HOST = os.environ.get("CENTAURI_HOST", "192.168.0.120")
ID = os.environ.get("CENTAURI_ID", "979d4C788A4a78bC777A870F1A02867A")
MB = os.environ.get("CENTAURI_MB", "448e195701045b4000000c0000000000")

def env(cmd, data, rid=False):
    """SDCP envelope: metadata lives INSIDE Data or the printer silently drops it."""
    return json.dumps({"Id": ID if rid else "", "Data": {
        "Cmd": cmd, "Data": data, "RequestID": secrets.token_hex(16),
        "MainboardID": MB if rid else "", "TimeStamp": int(time.time()), "From": 1}})

async def ask(ws, cmd, data, label="", timeout=8, rid=True):
    """One command, wait for its reply frame (matching Cmd); ping to stay alive."""
    await ws.send(env(cmd, data, rid))
    end = time.time() + timeout
    while time.time() < end:
        try:
            m = json.loads(await asyncio.wait_for(
                ws.recv(), min(5, max(0.1, end - time.time()))))
        except asyncio.TimeoutError:
            await ws.send("ping")
            continue
        d = m.get("Data", {})
        if d.get("Cmd") == cmd:
            return d.get("Data")
    if label:
        print(f"{label}: NO REPLY")
    return None
