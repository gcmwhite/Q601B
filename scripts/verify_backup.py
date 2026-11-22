#!/usr/bin/env python3
"""Verify the downloaded backup image and write MANIFEST / BACKUP_RECORD."""
import os
import gzip
import hashlib
import time

BACKUP_DIR = "f:/work/jiguang/backup"
LOCAL_GZ = os.path.join(BACKUP_DIR, "full_emmc.img.gz")
CHUNK = 4 * 1024 * 1024

if not os.path.exists(LOCAL_GZ):
    raise SystemExit("image not found: " + LOCAL_GZ)

size = os.path.getsize(LOCAL_GZ)
print(f"image size: {size} bytes ({size/1e9:.2f} GB)", flush=True)
if size != 14688891802:
    print(f"WARNING: expected 14688891802 bytes, got {size} — download may be incomplete!", flush=True)

print("verifying gzip stream ...", flush=True)
h = hashlib.sha256()
total = 0
t0 = time.time()
with open(LOCAL_GZ, "rb") as f:
    for c in iter(lambda: f.read(CHUNK), b""):
        h.update(c)
with gzip.open(LOCAL_GZ, "rb") as f:
    while True:
        c = f.read(CHUNK)
        if not c:
            break
        total += len(c)
sha = h.hexdigest()
print(f"gzip OK: raw {total} bytes ({total/1e9:.2f} GB) in {(time.time()-t0)/60:.1f} min", flush=True)
print(f"SHA256: {sha}", flush=True)

with open(os.path.join(BACKUP_DIR, "MANIFEST.txt"), "w", encoding="utf-8") as mf:
    mf.write("TencentBox Q601B Full System Backup\n")
    mf.write("Device: <BOX_IP_ETHERNET>:5555\n")
    mf.write(f"Created: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
    mf.write("Image: full_emmc.img.gz (gzip raw eMMC, source 31268536320 bytes)\n")
    mf.write(f"Compressed: {size} bytes\n")
    mf.write(f"Decompressed: {total} bytes\n")
    mf.write(f"SHA256: {sha}\n\nFiles:\n")
    for name in sorted(os.listdir(BACKUP_DIR)):
        p = os.path.join(BACKUP_DIR, name)
        if os.path.isfile(p):
            mf.write(f"  {name}  {os.path.getsize(p)} bytes\n")

with open("f:/work/jiguang/docs/BACKUP_RECORD.md", "a", encoding="utf-8") as bf:
    bf.write(f"\n## Full backup {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
    bf.write(f"- Image: f:/work/jiguang/backup/full_emmc.img.gz ({size/1e9:.2f} GB gz)\n")
    bf.write(f"- Raw: {total} bytes\n")
    bf.write(f"- SHA256: {sha}\n")

print("MANIFEST.txt and BACKUP_RECORD.md written.", flush=True)
