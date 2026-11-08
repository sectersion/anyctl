#!/usr/bin/env python
"""anyctl send — one packet, one WebSocket exchange, print the reply.

  python anyctl/send.py 192.168.0.120 '{"Cmd":403,"Data":{"LightStatus":{"SecondLight":true}}}'
"""
import asyncio, json, secrets, sys, time
import websockets

async def talk(ip, payload, secs=5.0):
    url = f"ws://{ip}:3030/websocket"
    body = {"Id": "", "Data": {
            "Cmd": payload["Cmd"], "Data": payload.get("Data", {}),
            "RequestID": secrets.token_hex(16), "MainboardID": "",
            "TimeStamp": int(time.time()), "From": 1}}
    async with websockets.connect(url, open_timeout=5) as ws:
        got = []
        if payload:
            await ws.send(json.dumps(body))
        try:
            while True:
                msg = await asyncio.wait_for(ws.recv(), timeout=secs)
                got.append(msg if isinstance(msg, str) else msg.decode("utf-8", "replace"))
        except (asyncio.TimeoutError, websockets.ConnectionClosed):
            pass
        return got

if __name__ == "__main__":
    ip = sys.argv[1]
    payload = None if sys.argv[2] == "-" else json.loads(sys.argv[2])
    for m in asyncio.run(talk(ip, payload)):
        print(m)
