# ELEGOO Centauri Carbon

**Interface:** LAN. Plain WebSocket `ws://<ip>:3030/websocket` (control), HTTP on `:80`
(Angular UI, static files), MJPEG video `http://<ip>:3031/video`. Protocol brand: **SDCP**
("Smart Device Connect Protocol"), `ProtocolVersion: V3.0.0` per GET_PRINTER_ATTR.
No auth, no TLS on LAN. **Single-client**: the printer silently ignores a second WebSocket —
close the browser tab before scripting.

**Layout:** drivers live beside this note and share `centauri.py` (envelope builder +
`CENTAURI_HOST/ID/MB` env-overridable constants): `send.py` (one raw packet),
`watch.py` (print watcher), `upload.py`, `shot.py` (chamber cam), `print_benchy.py`,
`history.py` (cmds 320/321, `--video` pulls the timelapse mp4 via 323), `files.py`
(cmds 258/259/257/260 — `rm` needs `--yes`).

## Envelope (all metadata nested INSIDE `Data`, top level is only `{Id, Data, Topic?}`)

```json
{"Id":"", "Data":{"Cmd":<int>, "Data":{...}, "RequestID":"<32 hex>",
                   "MainboardID":"", "TimeStamp":<unix seconds>, "From":1}}
```

Replies arrive as topics: `sdcp/response/<MainboardID>` (ack: `Data.Data.Ack == 0` = OK),
`sdcp/status/<MainboardID>` (full status push), `sdcp/attributes`, `sdcp/error`.
Heartbeat every 30s: send text frame `ping`. Acks echo our `RequestID`; responses carry
`Id` = board serial. Server also **pushes Status and Attributes unsolicited** — a
listen-only client gets telemetry for free.
On page open the UI bursts, in order: `258 {Url:"/local"}`, `386 {Enable:1}`, `0`, `1`,
`320`, `134` — canonical wake sequence.

## Command table (from webapp bundle enum)

| Cmd | Name | Notes |
|-----|------|-------|
| 0 | GET_PRINTER_STATUS | triggers `sdcp/status` push |
| 1 | GET_PRINTER_ATTR | name, FW ver, MAC, capabilities |
| 64 | SEND_PRINTER_DISCONNECT | |
| 128 | SEND_PRINTER_START_PRINT | payload from file detail; needs file Id |
| 129 | SEND_PRINTER_SUSPEND_PRINT | |
| 130 | SEND_PRINTER_STOP_PRINT | |
| 131 | SEND_PRINTER_RESTORE_PRINT | resume |
| 134 | GET_BLACKOUT_STATUS | |
| 135 | SEND_BLACKOUT_ACTION | `{action: 1|0}` power-loss recovery |
| 192 | SEND_PRINTER_EDIT_NAME | `{Name:"…"}` → Ack 0 CONFIRMED (name round-trips via Cmd 1) |
| 255 | SEND_PRINTER_SEND_FILE_END | end of gcode upload |
| 257 | EDIT_PRINTER_FILE_NAME | |
| 258 | GET_PRINTER_FILE_LIST | `{Url:"/local"}` → `FileList[{name:"/local/…", CreateTime, FileSize, LayerHeight, TotalLayers, EstFilamentLength}]` — note lowercase `name` |
| 259 | DELETE_PRINTER_FILE_LIST | `{FileList:["/local/…",…]}` → Ack 0 CONFIRMED (re-list proves removal) |
| 260 | GET_PRINTER_FILE_DETAIL | |
| 320 | GET_PRINTER_HISTORY_ID | → `HistoryData: [uuid,...]` — **newest first** |
| 321 | GET_PRINTER_TASK_DETAIL | `{Id:[uuid,…]}` → `HistoryDetailList`: Thumbnail (full http PNG), TaskName, Begin/EndTime, TaskStatus (1=OK,3=fail), MD5, AlreadyPrintLayer/total, TimeLapseVideoStatus (1=ready?)/Url `/local/aic_tlp/<name>-<date>…` |
| 322 | DELETE_PRINTER_HISTORY | |
| 323 | GET_PRINTER_HISTORY_VIDEO | `{Url:[device path,…]}` (**array** — a bare string gets Ack 1). Slow: UI waits 30 s; reply `Data.Data.Data = [url,…]` → download `http://<ip>:80` + `quote(url)` (UI encodes only the basename; full path works too). |
| 386 | EDIT_PRINTER_VIDEO_STREAMING | `{Enable:1}` → ack carries `VideoUrl` (`:3031/video` MJPEG) |
| 387 | EDIT_PRINTER_TIME_LAPSE_STATUS | `{}` or `{Tlp_Switch:1}` → **Ack 1 while idle** — likely only valid mid-print (Attributes show TLP* = 0 at rest). Untested active. |
| 401 | EDIT_PRINTER_AXIS_NUMBER | jog: `{Axis:"X"\|"Y"\|"Z", Step:±mm}` (UI steps .1/1/10/100; sign = direction). **CONFIRMED**: `{"Axis":"X","Step":0.1}` → Ack 0, coord +0.10. Needs a fresh home first — Ack **3** = "Please zero the moving axis before moving" (axisError i18n: 1 busy, 2 param, 3 unzeroed, 4/5 zero-failed). UI guards: refuses while `CurrentStatus` includes 1. |
| 402 | EDIT_PRINTER_AXIS_ZERO | home: `{Axis:"X"\|"Y"\|"Z"}` — **string, not number**; pass real `Id`+`MainboardID`. Autohome = send Z, then X, then Y. CONFIRMED: all acked 0. Z alone runs the **full** level sequence (corners + Z probe) under state **9**; ack 0 arrives immediately, motion follows. |
| 403 | EDIT_PRINTER_STATUS_DATA | generic patch — `{"LightStatus":{"SecondLight":true,"RgbLight":[0,0,0]}}` = light ON, **exact UI frame, confirmed**. `false` = off. RgbLight stays [0,0,0] even when on. |

## Status fields (Cmd 0 push)

`TempOfHotbed/Nozzle/Box`, `TempTarget*`, `CurrenCoord:"x,y,z"`, `CurrentFanSpeed{ModelFan,
AuxiliaryFan,BoxFan}`, `ZOffset`, `LightStatus{SecondLight,RgbLight}`,
`PrintInfo{Status,CurrentLayer,TotalLayer,Filename,Progress,PrintSpeedPct}`, `Status.CurrentStatus`
(state enum — wire-truth beats i18n: **1 = printing/active** (UI's jog guard is
`CurrentStatus.includes(1)`), 0 = standby, **9 = homing/levelling** (seen live during a 402
cycle; a completed print goes 1 → 0 without ever showing 9). Documented from bundle:
5/6 suspending/paused, 8/14 stopped, 10 file-detect, 12 recovery, 13 "printing" — but live
prints report 1, not 13. Trust the wire.)

## Gotchas

- Envelope metadata inside `Data` or the message is **silently dropped** (no error frame).
- One WS client at a time; second connections open but get nothing.
- `RgbLight:[0,0,0]` in captures = off; `[255,255,255]` = on.
## File upload (no WS involved)

Sequential 1 MB chunks, `POST http://<ip>/uploadFile/upload`, multipart form:
`TotalSize` (bytes), `Uuid` (32-hex, one per upload), `Offset` (chunk start), `Check`("1"),
`S-File-MD5` (md5 of the WHOLE file), `File` (the chunk; part filename = target gcode name).
Last chunk completes the file — UI then just re-requests Cmd 258; Cmd 255 appears unused.
See `upload.py`.

## Start print

`128 {Filename:"x.gcode", StartLayer:0, Calibration_switch:0|1 (auto bed level),
PrintPlatformType:0, Tlp_Switch:0|1 (timelapse)}` — Filename comes from Cmd 260 file detail.
`129` suspend, `130` stop, `131` restore — all `{}`, pass real `Id`+`MainboardID` like 402.

## Verified

2026-11-07 against FW V1.1.40 @ 192.168.0.120: status/attr reads, 403 LightStatus write
(physically confirmed both directions), 402 autohome Z,X,Y (physically confirmed gantry
homed). FULL LIFECYCLE proven: upload benchy (3 chunks) → 128 START Ack 0 → watch to
completion → 320/321 history + thumbnail. Completion transition on the wire is
state 1 → 0 with Progress 99 → 0 (never reports 100; never the documented 9 — watch for
`1 then 0` + Filename cleared). First agent-driven print on this machine (Claude's debut):
3DBenchy 240/240, 40m08s @160%, TaskStatus 1.
2026-11-08 sweep (idle machine): timelapse retrieval end-to-end — 323 array payload → Ack 0
after ~30 s → 1.88 MB valid mp4 (`ftypisom`) via `:80` + quoted path; 259 deleted
`/local/test_transport.gcode`, re-list proved it; 192 rename Ack 0; Cmd 1 full attribute
dump; 401/402 jog+home closed the loop — home first (state 9 full-level cycle observed on
the wire), then X jog 0.1 mm Ack 0, `CurrenCoord` 130.00→130.10 (physically verified).
Still open: 387 mid-print, 129/130/131 mid-print, 257, 322, 135, 64, 403 temps/fan.
