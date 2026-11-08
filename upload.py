#!/usr/bin/env python
"""Upload a gcode file to an Elegoo Centauri Carbon over its LAN API.

Chunked multipart to http://<ip>/uploadFile/upload; 1 MB pieces, sequential offsets.
  python upload.py 192.168.0.120 /path/to/file.gcode
"""
import hashlib, mimetypes, sys, urllib.request, uuid

CHUNK = 1048576

def post_chunk(url, name, piece, total, u, md5, offset):
    b = uuid.uuid4().hex
    fields = {"TotalSize": str(total), "Uuid": u, "Offset": str(offset),
              "Check": "1", "S-File-MD5": md5}
    body = b""
    for k, v in fields.items():
        body += f'--{b}\r\nContent-Disposition: form-data; name="{k}"\r\n\r\n{v}\r\n'.encode()
    body += (f'--{b}\r\nContent-Disposition: form-data; name="File"; '
             f'filename="{name}"\r\nContent-Type: application/octet-stream\r\n\r\n').encode()
    body += piece + b"\r\n" + f"--{b}--\r\n".encode()
    req = urllib.request.Request(url, data=body, headers={
        "Content-Type": f"multipart/form-data; boundary={b}"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read()

if __name__ == "__main__":
    ip, path = sys.argv[1], sys.argv[2]
    data = open(path, "rb").read()
    name = path.replace("\\", "/").split("/")[-1]
    md5 = hashlib.md5(data).hexdigest()
    u = uuid.uuid4().hex
    url = f"http://{ip}/uploadFile/upload"
    for off in range(0, len(data), CHUNK):
        piece = data[off:off + CHUNK]
        resp = post_chunk(url, name, piece, len(data), u, md5, off)
        print(f"{off + len(piece)}/{len(data)} -> {resp[:120]!r}")
    print("uploaded", name, "md5", md5, "uuid", u)
