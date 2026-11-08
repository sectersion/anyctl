# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repo is

`anyctl` is a **published Claude Code plugin** (marketplace: `sectersion/anyctl` on GitHub). The repo root doubles as the plugin root, and pushes to `main` publish it immediately — installed users pull from git. The full method lives in `.claude/skills/anyctl/SKILL.md` (the five laws and discovery ladder); the README's persona section is the human-facing pitch. Keep the two consistent when changing either.

## Packaging constraints (non-obvious, will bite)

- Files **outside the plugin root do not ship** — that's why drivers live in `devices/<name>/` and generic tools inside their skill folder, not at repo root.
- `.claude-plugin/plugin.json` deliberately has **no `version`**: pinning a version freezes git-source installs. Don't "helpfully" add one.
- `claude plugin validate .` should pass; `--strict` fails on the intentional missing version and directory-only icon. Validate with the former.
- Skill bodies reference scripts via `${CLAUDE_SKILL_DIR}` (files inside the skill) or `${CLAUDE_PLUGIN_ROOT}` (device drivers under `devices/`). Test locally with `claude --plugin-dir .`.
- **Never commit vendor content**: no firmware, no app bundles, no `.pyc`/`__pycache__`, no photos (`*.jpg` is gitignored for a reason — device images are personal). Reverse-engineering scratch from vendor bundles lives *outside* the repo, in `C:\Users\Oliver\centauri-probe\`; cite findings into `device.md` notes, never copy the artifacts in.

## Commands

No build system, no test framework. Scripts are standalone one-shots: stdlib plus at most one pip dep (`websockets` for the printer, `pyserial` for the radio); `snap.py` shells out to `ffmpeg` (must be on PATH).

- Compile-check everything: `python -m py_compile devices/*/*.py .claude/skills/*/*.py`
- Safe live smoke test (read-only against the real printer): `python devices/centauri-carbon/history.py`
- Passive listen on the printer WebSocket: `python devices/centauri-carbon/send.py -`
- Run drivers from any cwd — sibling imports resolve from the script's directory; run them by full path (`python devices/trusdx/cat.py COM9 --listen 10`), don't import them from elsewhere.

## Architecture: notes are the product, scripts are the proofs

Each device is a directory: `device.md` (protocol notes) beside its drivers. **`device.md` is the source of truth about the protocol**; scripts encode its claims. Every claim in a device note must carry its verification status ("CONFIRMED", "untested on wire", "NOT YET ON THE WIRE") and the `## Verified` footer records date + firmware + method.

Centauri Carbon (`devices/centauri-carbon/`): shared `centauri.py` holds the SDCP envelope builder and host/board identity constants, env-overridable (`CENTAURI_HOST`, `CENTAURI_ID`, `CENTAURI_MB`) — new scripts import from it rather than re-inlining the envelope. Key hazards documented in its device.md: envelope metadata nested **inside** `Data` or the printer silently drops messages; the printer serves **one WebSocket client at a time** (a second connection is accepted but ignored — kill running watchers before sending, and remember `watch.py` holds the slot); wire status truth beats the docs (print state is `1`, completion is `1 → 0` with `Filename` cleared, never `100`).

(tr)uSDX (`devices/trusdx/`): ASCII CAT commands (`;`-terminated) over USB serial; driver `cat.py`. Notes derived from hamlib source, **not yet wire-verified** — first session is `--listen` + `ID;`, then update the notes before anything else.

Safety posture is architectural, not cosmetic: TX (`cat.py --tx`) and destructive/physical commands (PTT, deletes, jog during print) require explicit human confirmation — the callsign and the machinery belong to the user.

## Device-cache growth

New device discovered → new `devices/<name>/` dir with `device.md` (copy an existing one as the template) + its scripts; skills only exist for capabilities, and a device skill is usually just a pointer to the driver + the gate rules. The fleet roadmap (router serial root, ESP32 TCP-UART bridge firmware, servo/IR hands tier) is tracked in README vignettes and conversation, not code — check before assuming something is implemented.
