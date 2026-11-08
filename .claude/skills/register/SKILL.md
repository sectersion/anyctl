---
name: register
description: Onboard a new or unknown device into the anyctl fleet — interview, research existing OSS, probe the wire, reverse-engineer a web UI if needed, then scaffold devices/<name>/ with a verified device.md and a read-only driver. Use when asked to register/add/connect a new machine, or "I have this weird thing".
allowed-tools: Bash(python *), Bash(curl *), Bash(gh *), Read, Write, Edit, WebSearch, WebFetch
---

# register — device onboarding, start to finish

The method and the five laws live in the `/anyctl` skill; this is the running
procedure. Follow the steps in order, don't skip the interview, and stop at
every gate. Expect one device per session; expect to update the notes at the end.

## 1. Interview the human (all at once)

- Exact model/brand, firmware version if shown. **Whose device is it** — only
  user-owned machines get probed or poked.
- What's physically there: USB cable type? UART adapter? Ethernet + IP? Does it
  have a mobile app or web UI?
- What capability is wanted: watch-only, read state, or actuate? (Sets the gate
  level and which commands matter first.)

## 2. Research before touching anything

Cheapest protocol is one someone already decoded:

- WebSearch `"<model>" (api OR protocol OR "serial commands") github`
- `gh api "search/code?q=<model+name>"` — code search beats web summaries.
- Check the OSS registries first: hamlib (radios), Home Assistant core
  integrations (the biggest device-protocol database that exists — read its
  `homeassistant/components/<vendor>/`), Klipper/Moonraker (printers),
  python-* device libraries.
- Read their **source comments** — they are bug reports turned into prose.

Found OSS? Skim it, then skip to step 4 with its framing. No docs but a web UI?
Step 3. Neither? Port-map brute force via step 4, carefully, user-owned only.

## 3. Reverse-engineer the web UI (when it's closed)

Scratch dir OUTSIDE the repo — vendor bundles never get committed (law 5):

1. `curl` the page, list `<script src>` assets, fetch them into the scratch dir.
2. **Vocabulary survives minification.** Extract command enums:
   `grep -ohE '[A-Z_]{3,}=[0-9]{1,4}\b' *.js | sort -u`
3. **Ack codes are language files.** Fetch the i18n JSON and grep the error
   keys — a mystery `Ack: 3` decoded to "please home before moving" this way.
4. **Payload shapes live at call sites.** Grep ±300 chars around the enum name
   used in a send (`.{60}CMD_NAME.{200}`) to see the real JSON body, including
   array-vs-string mistakes a guessed payload would never reveal.
5. DevTools oracle when a human can click: watch the live WS/HTTP frames for
   one button press and diff against your guessed frame. One diff found the
   "metadata nested INSIDE Data" bug on the Centauri.

## 4. First contact — listen (law 1)

`${CLAUDE_SKILL_DIR}/probe.py`:

```
python probe.py serial                      # what COM ports exist?
python probe.py tcp  <ip> 21,22,23,80,443,3030,8080   # banners
python probe.py http http://<ip>/           # API hints in Server header / HTML
python probe.py ws   ws://<ip>:<port>/websocket 15     # 15s, send NOTHING
```

Unsolicited frames = free ground truth and free test data. For serial: open the
port, read bytes for 10s at the device's nominal baud before writing. Try
`*IDN?` if it claims SCPI.

For boot windows and bootloader countdowns, use the interactive console in this
directory — `${CLAUDE_SKILL_DIR}/console.py COM3 115200 --log boot.log` forwards
Ctrl-C to the device instead of dying, holds-a-key spams through the countdown,
and raw-logs everything.

## 5. Write commands, one at a time, with markers

Send the smallest read-only command first. Then per law 2, before anything that
moves metal or deletes storage: print the exact outgoing bytes, get human OK.
Confirm physically when possible (eyes or `/snap`) — an ack proves the wire,
not the machine. Wire truth beats docs; when they disagree, the capture wins.

## 6. Cache the device (the deliverable)

Create `devices/<name>/` beside the existing ones:

- `device.md` — copy the structure of `devices/centauri-carbon/device.md`:
  interface+framing+exact sample envelope; command table where **every row is
  marked** CONFIRMED / untested-on-wire / rejected-while-idle; status-field
  semantics as observed; gotchas (heartbeats, single-client slots, terminators);
  `## Verified` footer with date, firmware, and how each thing was proven.
- The driver: one-shot stdlib script, default to read-only, destructive ops
  behind `--yes`. `python -m py_compile` it, run the read path live.
- If commands remain untested because they need an active machine state
  (mid-print etc.), write the queue into the notes, not into your memory.

## 7. Close out

Commit the device dir + README table row; push if the repo is a plugin (users
pull from git). A note without a verification date is a hypothesis — date it.

## Gates

- New device probe = user present, device confirmed theirs.
- Actuation/deletion/TX = show bytes, explicit per-action human OK.
- Never commit vendor firmware, app bundles, or personal photos.
