#!/usr/bin/env python3
"""Extract a partition image from full_emmc.img.gz using its GPT table.

Usage:
    python extract_partition.py boot
    python extract_partition.py --list
"""
import sys
import os
import gzip
import struct

IMG = "f:/work/jiguang/backup/full_emmc.img.gz"
OUT_DIR = "f:/work/jiguang/backup/extracted"
SECTOR = 512


def read_gpt(f):
    f.seek(SECTOR)
    hdr = f.read(92)
    if hdr[:8] != b"EFI PART":
        raise RuntimeError("no GPT found in image")
    entries_lba = struct.unpack_from("<Q", hdr, 72)[0]
    num = struct.unpack_from("<I", hdr, 80)[0]
    size = struct.unpack_from("<I", hdr, 84)[0]
    f.seek(entries_lba * SECTOR)
    table = f.read(num * size)
    parts = {}
    for i in range(num):
        e = table[i*size:(i+1)*size]
        if e[:16] == b"\x00" * 16:
            continue
        name = e[56:128].decode("utf-16-le", "ignore").rstrip("\x00")
        start = struct.unpack_from("<Q", e, 32)[0]
        end = struct.unpack_from("<Q", e, 40)[0]
        parts[name] = (start, end)
    return parts


def main():
    if not os.path.exists(IMG):
        raise SystemExit("image not found: " + IMG)
    with gzip.open(IMG, "rb") as f:
        parts = read_gpt(f)
        if len(sys.argv) < 2 or sys.argv[1] == "--list":
            print(f"{'name':16s} {'start LBA':>12s} {'size':>10s}")
            for n, (s, e) in parts.items():
                print(f"{n:16s} {s:12d} {(e-s+1)*SECTOR/1e6:8.1f}MB")
            return
        name = sys.argv[1]
        if name not in parts:
            raise SystemExit(f"unknown partition '{name}'. Use --list to see names.")
        start, end = parts[name]
        os.makedirs(OUT_DIR, exist_ok=True)
        out = os.path.join(OUT_DIR, name + ".img")
        total = (end - start + 1) * SECTOR
        print(f"extracting '{name}': LBA {start}-{end}, {total/1e6:.1f}MB ...")
        f.seek(start * SECTOR)
        remaining = total
        written = 0
        with open(out, "wb") as o:
            while remaining > 0:
                c = f.read(min(4 * 1024 * 1024, remaining))
                if not c:
                    break
                o.write(c)
                written += len(c)
                remaining -= len(c)
        print(f"done: {out} ({written} bytes)")


if __name__ == "__main__":
    main()
