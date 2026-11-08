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

## First-contact plan (when the power cable is found)

1. Open case (screws usually under rubber feet/pads). Locate 4-pin silkscreened
   UART pads near the SoC. **`/snap` the board** into the notes for the pinout.
2. Wire GND↔GND, board-TX↔adapter-RX, board-RX↔adapter-TX. Skip VCC.
3. Law 1 — listen before write: `console.py COMx 115200 --log boot.log`, power the
   router. Boot log = pinout + baud proven in one shot. Garbled → try 9600/57600;
   silence → swap candidate TX pads.
4. Bootloader window: hold Ctrl-C (and separately try `4`) during the 1–3 s
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
