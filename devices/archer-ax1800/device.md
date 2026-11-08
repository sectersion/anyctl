# TP-Link Archer AX1800 — Ver 4.6

**Target:** read-only console on **stock firmware** (owner's call — no flashing this
session). Interface: on-board UART, 3.3 V TTL via USB-UART adapter.
**Status: NOT YET ON THE WIRE** — everything below is research + plan, nothing verified.

## Interview facts (2026-11-08)

- Label: **Archer AX1800 Ver: 4.6**. Device is off; power cable being located.
- USB-UART adapter available. Admin password unknown; **factory reset OK** per owner
  (web-UI fallback if the console path locks out).

## Research findings (each row marked)

- Vendor page CONFIRMED — TP-Link US downloads list hardware **V1 / V1.20 / V2 /
  V5.60**, newest V5.60 firmware Build 20250814 (2025-09-05), note: "cannot be
  degraded". No V4 shown in US region.
- Vendor page CONFIRMED — TP-Link mapping note "**Vx.0 = Vx.6/Vx.8/Vx.9**" ⇒ Ver 4.6
  belongs to the V4 hardware family. EU page renders V1 only; regional SKU lists
  differ — **the label is the truth**, not the website.
- UNVERIFIED (search-prose, no primary source — law 3): claims that AX1800 revs use
  a **MediaTek MT7981B (Filogic)** SoC, UART @115200, 4-pin pads GND/RX/TX/VCC.
  Plausible but nothing was fetched from a real teardown or OpenWrt TOH.
- OpenWrt TOH blocked for bots (Anubis proof-of-work wall at openwrt.org; GitHub
  mirror path 404, gitweb path 404). TODO: human browser visit to
  `openwrt.org/toh/tp-link/archer_ax1800` — check serial pinout photo + whether
  newer revisions disabled the console.
- TP-Link console folklore (fleet-wide pattern, NOT this device): 115200 8N1;
  bootloader countdown key is Ctrl-C on some models, hold-`4` on others; pads
  silkscreened with a 3.3V pin — **never wire VCC**, adapter is powered from the PC.

## Adapter: FREENOVE ESP32-S3-WROOM-1 dev board (two USB-C ports)

- `USB-UART` = on-board bridge chip. **This is the console adapter.** The bridge is
  a 16-pin package ⇒ CH340-family or CH9102 (exact part = read marking; both need a
  driver on clean Windows). Serial header = the TX/RX pins silkscreened beside the
  USB-UART socket, independent of ESP32 firmware state. Header names follow the
  ESP32 side, so they read BACKWARDS for piggyback use: silk `TX` = net ESP32-TX =
  **bridge RX input** (listen here); silk `RX` = **bridge TX output** (drive here).
  These nets are shared with the S3's GPIO43/44 — an unflashed S3 may spit boot-loop
  noise on them (wire-verify); the router's log is distinct at 115200 anyway.
- `USB-OTG` = ESP32-S3 native USB. **Never use for console** unless firmware
  implements CDC — an S3 with blank firmware attaches (D+ pull-up) but never answers
  a descriptor request, so Windows shows Code 43 "Device Descriptor Request Failed"
  with `VID_0000&PID_0002`. Observed live 2026-11-08. Not a cable, driver, or
  hardware fault — wrong port.
- No EN→GND strap was ever fitted (owner corrected). ESP32 side is irrelevant to
  the USB-UART port; do not hold the S3 in reset as a "piggyback" trick.
- Gate: EN-low/reset tricks and any flashing of the S3 need owner's OK — reflashing
  the dev board is a separate project from reading the router.

## Bench state (2026-11-08, photographed via /snap)

- Case open. **Three wires (red/yellow/orange ribbon) are soldered to an UNLABELED
  header beside the shield can** — owner knows it's the UART, not the assignment.
  Router-side pins unknown: {GND, TX, RX} or include a VCC wire — must name before
  anything touches the dev board.
- COM state: on `USB-UART`, bridge not yet seen in the port list — next check is
  Device Manager for a CH340/CH9102 entry needing a driver (see adapter section).

## Wire-naming protocol (run BEFORE powering router)

Meter route: continuity to shield can → GND wire; then per-wire DC vs shield while
router boots: steady 3.30 V = VCC (never connects to dev board GND — short),
jittering-while-booting = TX, quiet/floating = RX.
No-meter route: for each wire pair, one on dev silk `TX` (= bridge RX input,
high-Z, safe to touch anything), one on dev GND; power router ~10 s; the combo that
shows boot spam names TX+GND; third wire = RX by elimination. Brief VCC→GND contact
= USB brownout, tolerable, not repeatable.

## First-contact plan (next actions)

1. On `USB-UART` + known-data cable: get the bridge's COM in `probe.py serial`.
   Descriptor failure again on this port (not USB-OTG) ⇒ driver-less under "Other
   devices" → install WCH driver; hard fail on both hosts → bridge-side hardware.
2. Run the wire-naming protocol above → know GND/TX/RX before any boot.
3. Law 1 — listen before write: `console.py COMx 115200 --log boot.log`, wire
   router-TX→dev silk `TX` (bridge input), router-GND→dev GND, then power the
   router. Boot spam = pinout proven. Garbled → wrong baud; silence → TX/RX call
   was backwards.
4. Bootloader window: hold Ctrl-C (and separately try `4`) during the 1-3 s
   countdown; whichever interrupts, record it here as CONFIRMED.
5. If a Linux login appears: do NOT attempt serial-password guessing; stock TP-Link
   serial shells are commonly locked — stop and report, fallback = factory reset +
   web UI (owner approved).

## Gates

- Physical probing with owner present; no VCC; no reflashing; no password brute.
- Vendor firmware images never enter this repo (law 5). Boot logs are ours — fine
  to keep, raw captures gitignored here anyway.

## Verified

_none yet — this file flips on first boot log._
