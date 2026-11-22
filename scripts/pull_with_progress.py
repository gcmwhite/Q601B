#!/usr/bin/env python3
"""Pull the compressed eMMC image with progress heartbeat to avoid tool idle timeout."""
import subprocess
import time
import os
import gzip
import hashlib
import threading

SERIAL = os.environ.get("BOX_IP", "<box-ip>") + ":5555"
DEVICE_TMP = "/data/local/tmp/full_emmc.img.gz"
BACKUP_DIR = "f:/work/jiguang/backup"
LOCAL_GZ = os.path.join(BACKUP_DIR, "full_emmc.img.gz")
CHUNK = 4 * 1024 * 1024


def heartbeat(proc, stop_event):
    while not stop_event.is_set():
        size = os.path.getsize(LOCAL_GZ) / 1e9 if os.path.exists(LOCAL_GZ) else 0
        print(f"  [pulling] {size:.2f} GB ...", flush=True)
        stop_event.wait(10)


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while True:
            c = f.read(CHUNK)
            if not c:
                break
            h.update(c)
    return h.hexdigest()


print("[1/3] Pulling image (device file is complete, 14.7GB) ...", flush=True)
if os.path.exists(LOCAL_GZ):
    os.remove(LOCAL_GZ)
stop = threading.Event()
t0 = time.time()
p = subprocess.Popen(["adb", "-s", SERIAL, "pull", DEVICE_TMP, LOCAL_GZ],
                     stdout=subprocess.PIPE, stderr=subprocess.PIPE)
hb = threading.Thread(target=heartbeat, args=(p, stop), daemon=True)
hb.start()
out, err = p.communicate()
stop.set()
hb.join(timeout=2)
dt = time.time() - t0
print("pull output:", out.decode("utf-8", "ignore").strip(), flush=True)
if p.returncode != 0 or not os.path.exists(LOCAL_GZ):
    print("PULL FAILED:", err.decode("utf-8", "ignore")[:500], flush=True)
    raise SystemExit(1)
size_gb = os.path.getsize(LOCAL_GZ) / 1e9
print(f"pulled {size_gb:.2f} GB in {dt/60:.1f} min", flush=True)

print("\n[2/3] Verifying gzip + computing SHA256 ...", flush=True)
total = 0
t0 = time.time()
with gzip.open(LOCAL_GZ, "rb") as f:
    while True:
        c = f.read(CHUNK)
        if not c:
            break
        total += len(c)
print(f"gzip OK: {total/1e9:.2f} GB raw in {(time.time()-t0)/60:.1f} min", flush=True)
sha = sha256_file(LOCAL_GZ)
print(f"SHA256: {sha}", flush=True)

with open(os.path.join(BACKUP_DIR, "MANIFEST.txt"), "w", encoding="utf-8") as f:
    f.write("TencentBox Q601B Full System Backup\n")
    f.write("Device: <BOX_IP_WIFI>:5555\n")
    f.write(f"Created: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
    f.write("Image: full_emmc.img.gz (gzip raw eMMC, 31268536320 bytes)\n")
    f.write(f"Decompressed: {total} bytes\n")
    f.write(f"SHA256: {sha}\n\nFiles:\n")
    for name in sorted(os.listdir(BACKUP_DIR)):
        fp = os.path.join(BACKUP_DIR, name)
        if os.path.isfile(fp):
            f.write(f"  {name}  {os.path.getsize(fp)} bytes\n")

with open("f:/work/jiguang/docs/BACKUP_RECORD.md", "a", encoding="utf-8") as f:
    f.write(f"\n## Full backup {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
    f.write(f"- Image: f:/work/jiguang/backup/full_emmc.img.gz ({size_gb:.2f} GB gz)\n")
    f.write(f"- Raw: {total} bytes\n")
    f.write(f"- SHA256: {sha}\n")

print("\n[3/3] Cleaning device temp ...", flush=True)
subprocess.run(["adb", "-s", SERIAL, "shell", "/system/xbin/su 0 sh -c " + repr("rm -f " + DEVICE_TMP)], capture_output=True)
print("=== BACKUP COMPLETE ===", flush=True)
