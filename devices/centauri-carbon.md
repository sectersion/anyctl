# ELEGOO Centauri Carbon

**Interface:** LAN. Plain WebSocket `ws://<ip>:3030/websocket` (control), HTTP on `:80`
(Angular UI, static files), MJPEG video `http://<ip>:3031/video`. Protocol brand: **SDCP**
("Smart Device Connect Protocol"), `ProtocolVersion: V3.0.0` per GET_PRINTER_ATTR.
No auth, no TLS on LAN. **Single-client**: the printer silently ignores a second WebSocket —
close the browser tab before scripting.

## Envelope (all metadata nested INSIDE `Data`, top level is only `{Id, Data, Topic?}`)

```json
{"Id":"", "Data":{"Cmd":<int>, "Data":{...}, "RequestID":"<32 hex>",
                   "MainboardID":"", "TimeStamp":<unix seconds>, "From":1}}
```

Replies arrive as topics: `sdcp/response/<MainboardID>` (ack: `Data.Data.Ack == 0` = OK),
`sdcp/status/<MainboardID>` (full status push), `sdcp/attributes`, `sdcp/error`.
Heartbeat every 30s: send text frame `ping`.

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
| 192 | SEND_PRINTER_EDIT_NAME | |
| 255 | SEND_PRINTER_SEND_FILE_END | end of gcode upload |
| 257 | EDIT_PRINTER_FILE_NAME | |
| 258 | GET_PRINTER_FILE_LIST | `{Url:"/local"}` |
| 259 | DELETE_PRINTER_FILE_LIST | |
| 260 | GET_PRINTER_FILE_DETAIL | |
| 320 | GET_PRINTER_HISTORY_ID | |
| 321 | GET_PRINTER_TASK_DETAIL | `{Id: historyId}` |
| 322 | DELETE_PRINTER_HISTORY | |
| 323 | GET_PRINTER_HISTORY_VIDEO | |
| 386 | EDIT_PRINTER_VIDEO_STREAMING | |
| 387 | EDIT_PRINTER_TIME_LAPSE_STATUS | |
| 401 | EDIT_PRINTER_AXIS_NUMBER | jog (payload TBD) |
| 402 | EDIT_PRINTER_AXIS_ZERO | home (payload TBD) |
| 403 | EDIT_PRINTER_STATUS_DATA | generic patch — `{"LightStatus":{"SecondLight":bool,"RgbLight":[r,g,b]}}` CONFIRMED ack'd; temps/other fields untested |

## Status fields (Cmd 0 push)

`TempOfHotbed/Nozzle/Box`, `TempTarget*`, `CurrenCoord:"x,y,z"`, `CurrentFanSpeed{ModelFan,
AuxiliaryFan,BoxFan}`, `ZOffset`, `LightStatus{SecondLight,RgbLight}`,
`PrintInfo{Status,CurrentLayer,TotalLayer,Filename,Progress,PrintSpeedPct}`, `Status.CurrentStatus`
(state enum: 0=idle, 13=printing, 5/6=suspending/p, 8/14=stopped, 9=complete, 12=recovery, 10=file detect)

## Gotchas

- Envelope metadata inside `Data` or the message is **silently dropped** (no error frame).
- One WS client at a time; second connections open but get nothing.
- `RgbLight:[0,0,0]` in captures = off; `[255,255,255]` = on.
- File upload path not yet reversed (255 = "send file end" implies streaming somewhere).

## Verified

2026-11-07 against FW V1.1.40 @ 192.168.0.120: status/attr reads, 403 LightStatus write (Ack 0).
