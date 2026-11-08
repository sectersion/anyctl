# anyctl

**Claude skills for controlling real hardware.** A method for taking any
device — documented or not — from "mystery box" to "addressable", a growing
cache of verified device notes, and the one-shot Python scripts that prove it.

It started with a 3D printer that wasn't supposed to be scriptable. One
session of listening, diffing the vendor web UI's own WebSocket frames against
our guesses, and reading their minified JS like tea leaves: lights on/off,
autohome over LAN, a 3 MB gcode uploaded by reverse-engineered chunked
multipart, and a 3DBenchy printed at "Ludicrous" speed — commanded entirely by
an agent that had never seen the protocol before. That loop is the product.

## What's inside

| Skill | What it does |
|-------|--------------|
| `/anyctl` | the method: five laws (listen before write, wire truth beats docs, …), discovery ladder, device-cache template |
| `/snap` | take a picture of the physical setup — because an ack proves the wire, not the machine |
| `/rig` | amateur radio via Kenwood CAT (verified target: (tr)uSDX), with a human gate on TX |

| Device notes | Interface |
|--------------|-----------|
| `devices/centauri-carbon.md` | Elegoo Centauri Carbon — WebSocket SDCP, MJPEG cam, upload + print, **wire-verified** |
| `devices/ts-480.md` | (tr)uSDX / TS-480-compatible CAT over USB serial — derived from hamlib, **pending wire** |

Scripts are plain stdlib-plus-one-dependency one-shots (`send.py`, `watch.py`,
`upload.py`, `shot.py`, `snap.py`, `cat.py`) — a fleet is a pile of scripts,
not a daemon.

## Install

```
claude plugin marketplace add <you>/anyctl
claude plugin install anyctl@anyctl
```

Or clone this repo; skills load automatically from `.claude/skills/` when you
work in it.

## Adding a device

Copy any `devices/*.md` as a template. Every claim needs a date and a method
("physically confirmed", "NO ACK"); unverified notes are marked as
hypotheses. **Ship your notes, never vendor bundles** — no firmware, no app
sources, only your observations and your scripts.

## License & safety

MIT. Devices are physical: anything that moves metal, keys a transmitter, or
deletes storage is gated behind explicit human confirmation — regulation and
reality don't care that the agent was confident.
