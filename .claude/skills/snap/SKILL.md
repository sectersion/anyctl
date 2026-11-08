---
name: snap
description: Take a picture of the physical setup to see what's actually happening. Use when a machine isn't behaving as commanded, when a protocol ack says OK but the mechanism didn't move, or when the user asks "what does it look like".
---

# Snap — look at the real world

A command succeeding proves the wire worked, not the machine. When reality and
telemetry disagree, take a picture before debugging further.

## Desk / room webcam (USB, DirectShow)

```
python snap.py                     # list video devices
python snap.py "Web Camera" out.jpg
```

Then **Read out.jpg** — the image renders inline. ffmpeg-based (`-f dshow`),
no OpenCV needed.

- It records 3 s and keeps the last frame: the first frames of any UVC cam are
  pre-auto-exposure black. Never conclude "camera broken" from frame one.
- **All-black check**: if stretching gain still shows nothing
  (`signalstats` YAVG ≈ 0), it's not lighting — it's a privacy slider, a sensor
  disconnect switch, Windows camera privacy, or another app holding the device
  exclusively. Ask the user to check the shutter.
- A mislabeled device name means nothing; match loosely or list first.

## Device-mounted cameras

Some devices expose their own stream (e.g. the Centauri Carbon prints an MJPEG
server). Use that device's snapshot script if its `devices/*.md` mentions one —
it'll know the enable-sequence and port. `shot.py` is the Centauri example:
`--warm` sends the enable command over WS, then pulls one JPEG frame.

## Loop, if it's live action

Re-run the snapshot every N seconds while actuating something, and diff by eye
between shots. Don't build a streaming UI; you want one frame at a time.
