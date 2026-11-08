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

## What this is

Not a smarter smart-home hub, not a firmware fork — an agent that can read a
protocol, respect the physical world, and *remember* what it learned in files
you can diff. Imagine yourself in one of these:

**You run prints — one loud printer or a farm of them.** Drop a sliced file in
a folder; Claude's scripts upload it, start the job, and watch the layer
counter while you sleep. The chamber cam catches spaghetti at layer 20 instead
of you catching it at layer 200, and when the job finishes the printer's own
history archive — thumbnail, runtime, timelapse — lands in chat. *Real: a
3DBenchy, 160% speed, printed and verified end-to-end this way.*

**You do low-level hardware work.** A mystery module appears on the desk: you
hold it to the webcam and the agent reads the markings, pulls the pinout, and
answers "which pin is TX?" before you burn anything. The analog bench PSU?
Glue a $2 servo to its dial, let the camera read the meter, and it is now
programmable — no firmware, just servo angles and pixels. *Eyes are real
(`/snap`); the servo tier is the roadmap.*

**You run a home lab.** The router's serial console is already on your bench —
the agent drives it, interrupts boot, gets a shell. Then that same rooted box
becomes the network bridge for every UART device you own, so each one ends up
reachable as `socket://host:port`, one line of Python away.

**You're on the bands.** Frequency, mode, and meter readings from a script
while you work; the radio becomes addressable like anything else. Transmitting
stays behind an explicit human gate, because the callsign — and the spectrum —
belongs to a person. *(tr)uSDX client shipped, pending wire verification.*

**You collect weird machines.** SDCP WebSocket printers, CAT radios, chunked
upload endpoints, MJPEG cams: every closed device yields to the same procedure
— listen first, diff against the vendor UI's own traffic, verify against
reality, write the notes down. `devices/` in this repo is that down payment,
made from the one device nobody documented properly.

Through-line: anyctl gives agents **hands** (scripts that act on devices),
**eyes** (cameras that read the world), and **memory** (device caches that
outlive the session that discovered them).


## What's inside

| Skill | What it does |
|-------|--------------|
| `/anyctl` | the method: five laws (listen before write, wire truth beats docs, …), discovery ladder, device-cache template |
| `/snap` | take a picture of the physical setup — because an ack proves the wire, not the machine |
| `/rig` | amateur radio via Kenwood CAT (verified target: (tr)uSDX), with a human gate on TX |

| Device notes + drivers | Interface |
|------------------------|-----------|
| `devices/centauri-carbon/` | Elegoo Centauri Carbon — WebSocket SDCP, MJPEG cam, upload + print + history, **wire-verified** |
| `devices/trusdx/` | (tr)uSDX (TS-480-compatible CAT) over USB serial — derived from hamlib, **pending wire** |

Drivers live beside their device notes; generic tools live inside skills
(`.claude/skills/snap/snap.py`). Plain stdlib plus at most one pip dependency per
script — a fleet is a pile of scripts, not a daemon.

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
