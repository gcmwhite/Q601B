#!/usr/bin/env python3
"""Wait for on-device eMMC compression to finish, then pull and verify."""
import subprocess
import time
import os
import gzip
import hashlib

SERIAL = os.environ.get("BOX_IP", "<box-ip>") + ":5555"
DEVICE_TMP = "/data/local/tmp/full_emmc.img.gz"
BACKUP_DIR = "f:/work/jiguang/backup"
LOCAL_GZ = os.path.join(BACKUP_DIR, "full_emmc.img.gz")
CHUNK = 4 * 1024 * 1024


def adb(args, timeout=120):
    return subprocess.run(["adb", "-s", SERIAL] + args, capture_output=True, timeout=timeout)


def root(cmd, timeout=120):
    return adb(["shell", "/system/xbin/su 0 sh -c " + repr(cmd)], timeout=timeout)


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while True:
            c = f.read(CHUNK)
            if not c:
                break
            h.update(c)
    return h.hexdigest()


print("[1/4] Waiting for on-device compression ...")
last_size = 0
stalled = 0
while True:
    r = root(f"ls -l {DEVICE_TMP} 2>/dev/null; pgrep -x gzip >/dev/null && echo RUNNING || echo DONE")
    out = r.stdout.decode("utf-8", "ignore")
    size_line = next((l for l in out.splitlines() if l.strip().startswith("-")), "")
    parts = size_line.split()
    size = int(parts[4]) if len(parts) >= 5 else 0
    done = "DONE" in out
    print(f"  size={size/1e9:.2f}GB status={'DONE' if done else 'RUNNING'}", flush=True)
    if done and size == last_size:
        break
    if size == last_size:
        stalled += 1
        if stalled > 20:
            print("  stalled, checking processes ...", flush=True)
            break
    else:
        stalled = 0
    last_size = size
    time.sleep(15)

r = root(f"gzip -t {DEVICE_TMP} 2>&1; echo GZIP_TEST_RC=$?")
print("  device gzip test:", r.stdout.decode("utf-8", "ignore").strip(), flush=True)

print("\n[2/4] Pulling to PC ...")
t0 = time.time()
r = adb(["pull", DEVICE_TMP, LOCAL_GZ], timeout=7200)
print("  ", r.stdout.decode("utf-8", "ignore").strip(), flush=True)
if not os.path.exists(LOCAL_GZ):
    print("  PULL FAILED", r.stderr.decode("utf-8", "ignore")[:500])
    raise SystemExit(1)
dt = time.time() - t0
size_gb = os.path.getsize(LOCAL_GZ) / 1e9
print(f"  pulled {size_gb:.2f}GB in {dt/60:.1f}min ({size_gb*1000/dt:.2f}MB/s)", flush=True)

print("\n[3/4] Verifying gzip integrity + SHA256 ...")
total = 0
t0 = time.time()
with gzip.open(LOCAL_GZ, "rb") as f:
    while True:
        c = f.read(CHUNK)
        if not c:
            break
        total += len(c)
        if total % (1024**3) < CHUNK:
            print(f"  decompressed {total/1e9:.1f}GB ...", flush=True)
dt = time.time() - t0
print(f"  gzip OK: {total/1e9:.2f}GB raw in {dt/60:.1f}min", flush=True)
sha = sha256_file(LOCAL_GZ)
print(f"  SHA256: {sha}", flush=True)

with open(os.path.join(BACKUP_DIR, "MANIFEST.txt"), "w", encoding="utf-8") as f:
    f.write("TencentBox Q601B Full System Backup\n")
    f.write("Device: <BOX_IP_WIFI>:5555\n")
    f.write(f"Created: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
    f.write(f"Image: full_emmc.img.gz (gzip raw eMMC, source 31268536320 bytes)\n")
    f.write(f"Decompressed: {total} bytes\n")
    f.write(f"SHA256: {sha}\n\nFiles:\n")
    for name in sorted(os.listdir(BACKUP_DIR)):
        p = os.path.join(BACKUP_DIR, name)
        if os.path.isfile(p):
            f.write(f"  {name}  {os.path.getsize(p)} bytes\n")

with open("f:/work/jiguang/docs/BACKUP_RECORD.md", "a", encoding="utf-8") as f:
    f.write(f"\n## Full backup {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
    f.write(f"- Image: f:/work/jiguang/backup/full_emmc.img.gz ({size_gb:.2f} GB gz)\n")
    f.write(f"- Raw: {total} bytes\n")
    f.write(f"- SHA256: {sha}\n")

print("\n[4/4] Cleaning device temp ...")
root(f"rm -f {DEVICE_TMP}")
print("  done", flush=True)
print("\n=== BACKUP COMPLETE ===", flush=True)
