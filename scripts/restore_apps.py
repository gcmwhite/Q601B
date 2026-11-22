#!/usr/bin/env python3
import os
"""Re-enable all packages disabled by slim_apps.py."""
import subprocess

SERIAL = os.environ.get("BOX_IP", "<box-ip>") + ":5555"

SU = "/system/xbin/su 0"

def adb(args):
    r = subprocess.run(["adb", "-s", SERIAL] + args, capture_output=True, text=True, timeout=30)
    return (r.stdout or "").strip() + (r.stderr or "").strip()

def rootpm(*args):
    return adb(["shell", SU + " pm " + " ".join(args)])

print("=== Re-enabling all disabled packages (as root) ===")
disabled = rootpm("list", "packages", "-d")
for line in disabled.splitlines():
    line = line.strip()
    if line.startswith("package:"):
        pkg = line[len("package:"):]
        out = rootpm("enable", pkg)
        print(f"  [OK] {pkg}: {out[:80]}")

print("\n=== Remaining disabled ===")
print(rootpm("list", "packages", "-d") or "(none)")
