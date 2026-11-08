#!/usr/bin/env python
"""Snap one frame from a DirectShow device (webcam, capture card, whatever).
  python snap.py                 # list video devices
  python snap.py "name" out.jpg  # grab a frame; name substring match is fine
"""
import re, subprocess, sys

def devices():
    r = subprocess.run(["ffmpeg", "-hide_banner", "-f", "dshow",
                        "-list_devices", "true", "-i", "dummy"],
                       capture_output=True, text=True)
    return re.findall(r'"([^"]+)" \(video\)', r.stderr)

def snap(pattern, out):
    for d in devices():
        if pattern.lower() in d.lower():
            r = subprocess.run(["ffmpeg", "-y", "-f", "dshow", "-i", f'video={d}',
                                "-t", "3", "-update", "1", out],   # 3s of frames, keep last:
                               capture_output=True, text=True,     # first frames are pre-AE black
                               timeout=30)
            print(f"{d} -> {out}" if r.returncode == 0 else r.stderr[-400:])
            return
    print("no device matching", pattern, "| available:", devices())

if __name__ == "__main__":
    if len(sys.argv) < 2:
        for d in devices(): print(d)
    else:
        snap(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else "snap.jpg")
