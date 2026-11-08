#!/usr/bin/env python
"""anyctl send — one packet, one WebSocket exchange, print the reply.

  python anyctl/send.py 192.168.0.120 '{"Cmd":403,"Data":{"LightStatus":{"SecondLight":true}}}'
"""
import asyncio, json, sys
import websockets
from centauri import HOST, env

async def talk(ip, payload, secs=5.0):
    url = f"ws://{ip}:3030/websocket"
    body = env(payload["Cmd"], payload.get("Data", {})) if payload else None
    async with websockets.connect(url, open_timeout=5) as ws:
        got = []
        if body:
            await ws.send(body)
        try:
            while True:
                msg = await asyncio.wait_for(ws.recv(), timeout=secs)
                got.append(msg if isinstance(msg, str) else msg.decode("utf-8", "replace"))
        except (asyncio.TimeoutError, websockets.ConnectionClosed):
            pass
        return got

if __name__ == "__main__":
    ip = sys.argv[1] if len(sys.argv) > 2 else HOST
    payload = None if sys.argv[-1] == "-" else json.loads(sys.argv[-1])
    for m in asyncio.run(talk(ip, payload)):
        print(m)
