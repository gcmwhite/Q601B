#!/usr/bin/env python3
import os
"""Remove non-FLauncher HOME apps so FLauncher becomes the only launcher.

Reversible from the full backup. After removal, set FLauncher as default.
"""
import subprocess
SERIAL = os.environ.get("BOX_IP", "<box-ip>") + ":5555"
SU = "/system/xbin/su 0"

def root(cmd, timeout=60):
    r = subprocess.run(["adb", "-s", SERIAL, "shell", SU + " sh -c " + repr(cmd)], capture_output=True, timeout=timeout)
    return (r.stdout or b"").decode("utf-8", "ignore") + (r.stderr or b"").decode("utf-8", "ignore")

LAUNCHERS = [
    "com.ktcp.launcher",
    "com.dangbei.tvlauncher",
    "com.xiaopaitech.plauncher",
]

print("=== current APK paths ===")
paths = {}
for p in LAUNCHERS:
    path = root(f"pm path {p}").strip().replace("package:", "")
    paths[p] = path
    print(f"  {p}: {path}")

print("\n=== force-stopping ===")
for p in LAUNCHERS:
    root(f"am force-stop {p}")

print("\n=== deleting APKs (and odex dirs) ===")
root("mount -o rw,remount /")
for p, path in paths.items():
    if not path.endswith(".apk"):
        print(f"  SKIP {p}: no apk path")
        continue
    # /data/app/<pkg>-xxxx/base.apk  -> remove whole dir
    # /system/app/<name>/<name>.apk -> remove apk file
    if "/data/app/" in path:
        d = path.rsplit("/", 1)[0]
        out = root(f'rm -rf "{d}" 2>&1; ls -d "{d}" 2>&1')
        print(f"  {p}: removed dir {d} -> {out.strip()[:60]}")
    else:
        out = root(f'rm -f "{path}" 2>&1; ls "{path}" 2>&1')
        print(f"  {p}: removed {path} -> {out.strip()[:60]}")

print("\n=== set FLauncher as default ===")
print(root("cmd package set-home-activity me.efesser.flauncher/.MainActivity").strip())
