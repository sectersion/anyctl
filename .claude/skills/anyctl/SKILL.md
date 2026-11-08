---
name: anyctl
description: Bring a new, closed, or undocumented hardware device under Claude's control — discover its interface, verify commands against physical reality, and record findings in a device cache. Use when asked to connect/control/talk-to a machine, appliance, board, or protocol.
allowed-tools: Bash(python *), Bash(ffmpeg *), Read, Write, Edit
---

# anyctl — control anything

The method. Devices live in `devices/*.md` next to this repo's scripts; use
those first, this skill second. Nothing here is clever — it is the order that
worked, in the order to repeat it.

## Five laws

1. **Listen before write.** First contact on any interface is passive: dump
   traffic (WebSocket frames, serial bytes, UDP) for 10+ seconds before sending
   anything. Devices advertise themselves; unsolicited telemetry is free ground
   truth and free test data.
2. **Show bytes before actuation.** Anything that moves metal, keys a
   transmitter, or deletes storage gets its wire message displayed (and ideally
   dry-run captured from the vendor's own UI) before it goes out. TX especially:
   the callsign/license is the human's.
3. **Wire truth beats documentation.** Status enums lie in docs, ack codes are
   language files, search summaries hallucinate ("it runs Moonraker"). When a
   claim and a capture disagree, the capture wins — and fix the doc.
4. **Verify physically.** An ack proves the wire, not the machine. Confirm with
   eyes, or with a camera (`/snap`). A light that "didn't move" was already on.
5. **Ship your notes, never their bundles.** Vendor firmware/apps are not
   yours to redistribute. What you may ship: your observations, your extracted
   knowledge, your own scripts.

## Discovery ladder

Work down it; each rung is cheaper than the next:

1. **Ask the device** — `GET_ATTR`-style reads, banners, `*IDN?`, USB descriptors.
2. **Its web UI is an oracle** — open DevTools on the vendor page, watch the
   actual WebSocket/HTTP frames while a human clicks the button. Diffing one
   real frame against your guessed one found a nesting bug no doc would tell
   you (metadata inside `Data`, not beside it).
3. **Bundle archaeology** — minified JS preserves vocabulary: TS enums survive
   as `t.NAME=128`, i18n files decode numeric ack codes into English. `grep`
   the app bundle for `Cmd` tables before assuming the protocol is opaque.
4. **Existing OSS** — someone's usually halfway there (hamlib for rigs,
   printer communities). Read their source *comments* — they're bug reports
   turned into prose (TS-480: "RX; should return RX0; but it doesn't").
5. **Brute, carefully** — port-map (`:80/:3030/:3031` pattern), scan command
   integers only on devices you own, and read replies — many "silent" protocols
   are one wrong envelope away from chatty.

## The device cache (the deliverable)

Every verified session ends by writing/patching `devices/<name>.md`:

- interface + ports + framing, with an exact sample envelope
- command table with payload shapes, one "CONFIRMED" line per command proven
  physically, "untested on wire" for the rest — mark the truth of every claim
- status field semantics as observed (with "wire truth" notes where docs lied)
- gotchas section — single-client slots, heartbeats, flaky acks, terminator
  settings
- `## Verified` footer: date, firmware, what was confirmed how

Confidence decays: a note without a verification date is a hypothesis.

## One-shot scripts, not frameworks

Each capability is a standalone `python thing.py` using stdlib + at most one
pip dep (`websockets`, `pyserial`), that opens, does, prints, exits. Fleet
scale is a pile of scripts plus a watcher — no daemon, no config system.
`serial_for_url("socket://host:port")` turns every UART device behind an
ESP32 TCP bridge into a one-liner; put a bridge on a rooted router and the
whole bench is LAN-addressable.

## Patterns already proven here

- **WS JSON control + MJPEG video** (Centauri Carbon): see `devices/centauri-carbon.md`
- **Chunked multipart upload, no auth** (same printer): `upload.py`
- **UVC webcam via ffmpeg dshow** — see `/snap`
- **ASCII serial CAT** (Kenwood-style, (tr)uSDX): see `/rig`
