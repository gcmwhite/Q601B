#!/usr/bin/env python3
"""Merge downloaded parts into full_emmc.img.gz, verify, write manifest."""
import os
import glob
import gzip
import hashlib
import time

BACKUP_DIR = "f:/work/jiguang/backup"
PARTS_DIR = os.path.join(BACKUP_DIR, "parts")
OUT = os.path.join(BACKUP_DIR, "full_emmc.img.gz")
CHUNK = 4 * 1024 * 1024

parts = sorted(glob.glob(os.path.join(PARTS_DIR, "part_*")))
if not parts:
    raise SystemExit("no parts found in " + PARTS_DIR)
print(f"merging {len(parts)} parts ...", flush=True)
h = hashlib.sha256()
total_written = 0
with open(OUT, "wb") as out:
    for p in parts:
        with open(p, "rb") as f:
            while True:
                c = f.read(CHUNK)
                if not c:
                    break
                out.write(c)
                h.update(c)
                total_written += len(c)
        print(f"  {os.path.basename(p)} done, total {total_written/1e9:.2f}GB", flush=True)
sha = h.hexdigest()
print(f"merged size: {total_written} bytes ({total_written/1e9:.2f} GB)", flush=True)
print(f"SHA256: {sha}", flush=True)

print("verifying gzip ...", flush=True)
raw = 0
t0 = time.time()
with gzip.open(OUT, "rb") as f:
    while True:
        c = f.read(CHUNK)
        if not c:
            break
        raw += len(c)
print(f"gzip OK: raw {raw} bytes ({raw/1e9:.2f} GB) in {(time.time()-t0)/60:.1f} min", flush=True)

with open(os.path.join(BACKUP_DIR, "MANIFEST.txt"), "w", encoding="utf-8") as mf:
    mf.write("TencentBox Q601B Full System Backup (merged from parts)\n")
    mf.write("Device: <BOX_IP_WIFI>:5555\n")
    mf.write(f"Created: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
    mf.write(f"Compressed: {total_written} bytes\n")
    mf.write(f"Decompressed: {raw} bytes\n")
    mf.write(f"SHA256: {sha}\n")
print("MANIFEST.txt written.", flush=True)
