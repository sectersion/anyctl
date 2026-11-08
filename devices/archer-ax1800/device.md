# TP-Link Archer AX1800 — Ver 4.6

**Target:** read-only console on **stock firmware** (owner's call — no flashing this
session). Interface: on-board UART, 3.3 V TTL via USB-UART adapter.
**Status: ON THE WIRE** — full boot log captured 2026-11-08 (COM4 @115200, 122 KB,
`Downloads\ax1800_boot1.log`). Wire truth overrode the research: the SoC is **not**
MT7981B, it's **MT7621A** (see below).

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
- UNVERIFIED (search-prose) — MT7981B claim **REFUTED by boot log 2026-11-08**:
  U-Boot banner reads `ASIC MT7621A DualCore (MAC to MT7530 Mode)`, Ralink UBoot
  5.0.0.0, U-Boot 1.1.3 (Feb 16 2022), DRAM 128 MB DDR3, SPI flash,
  `flash manufacture id: 20, device id 40 18` → "un-recognized chip ID, please
  update bootloader" (MXIC-family NOR). Kernel `3.10.108`, built by
  `jenkins@sohoicilinux4` (Buildroot gcc 4.6.3). `bad CRC, using default
  environment` — U-Boot env is at defaults on this unit.
- CONFIRMED from our own boot log: **bootloader break key = `4` or `t`**
  ("Press '4' or 't' to break the booting process"). 115200 8N1 CONFIRMED (clean
  ASCII, no garble). Userspace logs verbosely to serial through full boot
  (hyfi bridging, smart_home_schedule, `DEBUG_LEVEL:1`) — console is NOT
  firmware-disabled on Ver 4.6.
- OpenWrt TOH blocked for bots (Anubis proof-of-work wall at openwrt.org; GitHub
  mirror path 404, gitweb path 404). TODO: human browser visit to
  `openwrt.org/toh/tp-link/archer_ax1800` — check serial pinout photo + whether
  newer revisions disabled the console.
- TP-Link console folklore (fleet-wide pattern, NOT this device): 115200 8N1;
  bootloader countdown key is Ctrl-C on some models, hold-`4` on others; pads
  silkscreened with a 3.3V pin — **never wire VCC**, adapter is powered from the PC.

## Adapter: RP2040 "Pico" clone + MicroPython bridge — CONFIRMED 2026-11-08

Pico running MicroPython v1.29.0 (UF2 from micropython.org, dragged onto RPI-RP2)
with `bridge.py` (this dir) copied over as `main.py` via
`python -m mpremote connect COM3 fs cp bridge.py :main.py` then `reset`.
Bridge = transparent USB-CDC ⇄ UART0 at 115200: **GP0 = TX → wire to router RX**,
**GP1 = RX ← wire to router TX**, GND ↔ GND. **Never wire VBUS/5V to the router.**
COM3. Verified by loopback: jumper GP0→GP1, sent `echo123` from host, got
`b'echo123'` back — full chain (driver, select loop, both pins, baud) proven.
Note: MicroPython mounts NO filesystem drive (that was CircuitPython thinking) —
push files with mpremote, not drag.

- **Freenove ESP32-S3 board: demoted, partially exonerated.** Identical Code-43
  `VID_0000&PID_0002` on both sockets ~10 trials; but the RP2040 saga showed a
  half-seated USB-C reproduces that exact flapping (one good enum, then descriptor
  failures). The Freenove was never retested with a firm cable. Low priority —
  the Pico works.
- Bench lesson, written as law-adjacent: **descriptor-request flapping ⇒ check
  connector seating FIRST**, before theorizing about chips, drivers, or cursed
  ports. The tell is nondeterminism; stateless silicon can only flap through
  marginal metal.

## Bench state (2026-11-08, photographed via /snap)

- Case open. **Three wires on the unlabeled header beside the shield can — NOW
  NAMED (CONFIRMED 2026-11-08):** **red = GND** (continuity to shield can),
  **yellow = TX** (boot log appeared wired yellow→silk `TX`, red→GND),
  **brown/orange = RX or VCC** — not yet needed; meter saw 3.3 V on it (idle-high
  RX fits). Router stays powered with red+yellow on the bridge; EN→GND keeps the
  S3 silent. (Freenove silk names follow ESP32 convention: silk `TX` = bridge
  INPUT = where router TX lands. Labels name the owner's output.)

## Wire-naming protocol (run BEFORE powering router)

Meter route: continuity to shield can → GND wire; then per-wire DC vs shield while
router boots: steady 3.30 V = VCC (never connects to dev board GND — short),
jittering-while-booting = TX, quiet/floating = RX.
No-meter route: for each wire pair, one on bridge GP1 (RX input,
high-Z, safe to touch anything), one on bridge GND; power router ~10 s; the combo that
shows boot spam names TX+GND; third wire = RX by elimination. Brief VCC→GND contact
= USB brownout, tolerable, not repeatable.

## First-contact plan (next actions)

1. ~~Get the bridge COM~~ DONE — Pico bridge on COM3, loopback-verified.
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

- 2026-11-08: adapter chain (COM3 ⇄ GP0/GP1 @115200) by GP0→GP1 loopback echo.
- 2026-11-08: **FULL BOOT LOG** on COM4 (CH343, 115200) — 122 KB clean ASCII,
  yellow=TX/red=GND proven by the log itself. Bootloader break key `4`/`t`
  CONFIRMED (read from log text; interrupt trial pending). MT7621A / kernel
  3.10.108 recorded above. Login-prompt + Ctrl-C-vs-shell state: untested.
