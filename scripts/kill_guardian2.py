#!/usr/bin/env python3
import os
"""Permanently remove guardian by renaming APKs, then re-disable bloat.

System is clean this time (FLauncher is HOME role holder), so no boot risk.
"""
import subprocess
S = os.environ.get("BOX_IP", "<box-ip>") + ":5555"
SU="/system/xbin/su 0"
def sh(c,timeout=60):
    return subprocess.run(["adb","-s",S,"shell",SU+" sh -c "+repr(c)],capture_output=True,timeout=timeout).stdout.decode("utf-8","ignore")

# Guardian + its re-enabled packages (in /data/app - writable)
REENABLED = [
    "com.skyworthdigital.skycommonpropertymanager",
    "com.skyworthdigital.skyappupdate",
    "com.skyworthdigital.ott.advert.app",
    "com.skyworthdigital.ottstatsv2",
    "com.skyworthdigital.logcollector",
]

print("=== force-stop first ===")
for p in REENABLED:
    sh(f"am force-stop {p}")

print("\n=== rename APKs in /data/app ===")
sh("mount -o rw,remount /data")
for p in REENABLED:
    path=sh(f"pm path {p}").strip().replace("package:","")
    if path.endswith("base.apk"):
        bak=path[:-4]+".apk.bak"
        out=sh(f'mv -f "{path}" "{bak}" 2>&1; ls -l "{bak}" 2>&1')
        print(f"  {p}: {out.strip()[-100:]}")

print("\n=== reboot ===")
print(sh("reboot"))
