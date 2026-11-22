#!/usr/bin/env python3
"""Full system backup of TencentBox Q601B to f:/work/jiguang/backup.

Strategy: compress the entire eMMC (/dev/block/mmcblk0) on-device with gzip,
then pull via adb (binary-safe). Also saves partition table, build props,
installed package list, and a SHA-256 manifest.
"""
import subprocess
import time
import os
import hashlib
import sys

SERIAL = os.environ.get("BOX_IP", "<box-ip>") + ":5555"
BACKUP_DIR = "f:/work/jiguang/backup"
DEVICE_TMP = "/data/local/tmp/full_emmc.img.gz"
LOCAL_GZ = os.path.join(BACKUP_DIR, "full_emmc.img.gz")
CHUNK = 4 * 1024 * 1024


def adb(args, timeout=120):
    return subprocess.run(["adb", "-s", SERIAL] + args, capture_output=True, timeout=timeout)


def root(cmd, timeout=120):
    full = "/system/xbin/su 0 sh -c " + repr(cmd)
    return adb(["shell", full], timeout=timeout)


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while True:
            c = f.read(CHUNK)
            if not c:
                break
            h.update(c)
    return h.hexdigest()


def main():
    os.makedirs(BACKUP_DIR, exist_ok=True)

    print("[1/5] Saving device metadata ...")
    meta = {}
    for name, cmd in [
        ("getprop.txt", "getprop"),
        ("partitions.txt", "cat /proc/partitions"),
        ("mounts.txt", "cat /proc/mounts"),
        ("build_prop.txt", "cat /system/build.prop"),
        ("packages.txt", "pm list packages -f"),
        ("cmdline.txt", "cat /proc/cmdline"),
    ]:
        r = root(cmd)
        meta[name] = (r.stdout or b"").decode("utf-8", "ignore")
        with open(os.path.join(BACKUP_DIR, name), "w", encoding="utf-8") as f:
            f.write(meta[name])
        print(f"  saved {name} ({len(meta[name])} chars)")

    print("\n[2/5] Compressing full eMMC on device ...")
    # Check free space on device /data first
    r = root("df -h /data | tail -1")
    print("  device /data:", r.stdout.decode("utf-8", "ignore").strip())

    r = root(f"rm -f {DEVICE_TMP}")
    t0 = time.time()
    r = root(f"dd if=/dev/block/mmcblk0 bs=1M 2>/dev/null | gzip -1 > {DEVICE_TMP}", timeout=7200)
    if r.returncode != 0:
        print("  compression failed:", r.stderr.decode("utf-8", "ignore")[:500])
        sys.exit(1)
    dt = time.time() - t0
    print(f"  compression done in {dt/60:.1f} min")

    r = root(f"ls -l {DEVICE_TMP}")
    print("  ", r.stdout.decode("utf-8", "ignore").strip())

    print("\n[3/5] Pulling image to PC ...")
    t0 = time.time()
    r = adb(["pull", DEVICE_TMP, LOCAL_GZ], timeout=7200)
    print("  ", r.stdout.decode("utf-8", "ignore").strip(), r.stderr.decode("utf-8", "ignore").strip())
    if not os.path.exists(LOCAL_GZ):
        print("  PULL FAILED")
        sys.exit(1)
    dt = time.time() - t0
    size_gb = os.path.getsize(LOCAL_GZ) / 1e9
    print(f"  pulled {size_gb:.2f} GB in {dt/60:.1f} min ({size_gb*1000/dt:.2f} MB/s)")

    print("\n[4/5] Verifying ...")
    # verify gzip integrity on PC
    import gzip
    t0 = time.time()
    total = 0
    with gzip.open(LOCAL_GZ, "rb") as f:
        while True:
            c = f.read(CHUNK)
            if not c:
                break
            total += len(c)
    dt = time.time() - t0
    print(f"  gzip decompress OK: {total/1e9:.2f} GB raw in {dt/60:.1f} min")
    sha = sha256_file(LOCAL_GZ)
    print(f"  SHA256: {sha}")

    with open(os.path.join(BACKUP_DIR, "MANIFEST.txt"), "w", encoding="utf-8") as f:
        f.write("TencentBox Q601B Full System Backup\n")
        f.write("Device: <BOX_IP_WIFI>:5555\n")
        f.write(f"Created: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Image: full_emmc.img.gz (gzip-compressed raw eMMC, 31268536320 bytes)\n")
        f.write(f"Decompressed size: {total} bytes\n")
        f.write(f"SHA256: {sha}\n")
        f.write("\nFiles:\n")
        for name in sorted(os.listdir(BACKUP_DIR)):
            p = os.path.join(BACKUP_DIR, name)
            if os.path.isfile(p):
                f.write(f"  {name}  {os.path.getsize(p)} bytes\n")

    print("\n[5/5] Cleaning up device temp file ...")
    root(f"rm -f {DEVICE_TMP}")
    print("  done.")

    with open("f:/work/jiguang/docs/BACKUP_RECORD.md", "a", encoding="utf-8") as f:
        f.write(f"\n## Full backup {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"- Image: f:/work/jiguang/backup/full_emmc.img.gz ({size_gb:.2f} GB)\n")
        f.write(f"- Raw size: {total} bytes\n")
        f.write(f"- SHA256: {sha}\n")
    print("\n=== BACKUP COMPLETE ===")


if __name__ == "__main__":
    main()
