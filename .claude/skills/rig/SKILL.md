---
name: rig
description: Control a Kenwood CAT amateur radio (TS-480 family) — read frequency/mode, tune, set mode, PTT. Use when the user mentions the radio, rig, CAT, band activity, or asks to listen/transmit.
---

# Rig — TS-480 on the wire

Client is `${CLAUDE_PLUGIN_ROOT}/devices/trusdx/cat.py`; protocol notes in
`devices/trusdx/device.md`.
Find the COM port: `python -m serial.tools.list_ports` (or ask the user which
port the rig's USB/serial shows up on).

```
python ${CLAUDE_PLUGIN_ROOT}/devices/trusdx/cat.py COM9                      # status: IF; parsed + ID;
python ${CLAUDE_PLUGIN_ROOT}/devices/trusdx/cat.py COM9 --listen 10          # raw traffic — do this FIRST
python ${CLAUDE_PLUGIN_ROOT}/devices/trusdx/cat.py COM9 --freq 14.074        # set frequency
python ${CLAUDE_PLUGIN_ROOT}/devices/trusdx/cat.py COM9 --cmd "MD3;"         # any raw CAT command
python ${CLAUDE_PLUGIN_ROOT}/devices/trusdx/cat.py COM9 --tx --yes           # PTT — see gate below
```

## Rules

- **TX is a broadcast.** Transmitting keys the user's callsign — legally theirs,
  anywhere it's heard. Never `--tx --yes` without the user explicitly approving
  that specific transmission. RX/tune are free.
- **Listen before write**: new rig or weird behavior → `--listen 10` first; the
  radio tells you its quirks.
- `--cmd` is raw ASCII; the `;` terminator is part of the string. If replies
  look garbled, wrong baud; if none appear, check `AI0;` (auto-info can flood
  or starve the port) and the rig's CAT/terminator menu.
- TS-480 acks are flaky by design (`RX;` returns `?`/nothing; some replies are
  a bare `;`). Read state with `IF;`, never from an ack.
- Device notes are **not yet wire-verified** — on first successful session,
  update `devices/trusdx/device.md` with the real `IF;` field positions and correct
  the doc, then move it out of "NOT YET".
