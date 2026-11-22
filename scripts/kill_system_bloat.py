#!/usr/bin/env python3
import os
"""Remove remaining bloat APKs from /system (guardian etc)."""
import subprocess
S = os.environ.get("BOX_IP", "<box-ip>") + ":5555"
SU="/system/xbin/su 0"
def sh(c,timeout=60):
    return subprocess.run(["adb","-s",S,"shell",SU+" sh -c "+repr(c)],capture_output=True,timeout=timeout).stdout.decode("utf-8","ignore")

TARGETS=[
    "com.skyworthdigital.skycommonpropertymanager",
    "com.skyworthdigital.skyappupdate",
    "com.skyworthdigital.ott.advert.app",
    "com.skyworthdigital.upgrade",
    "com.skyworthdigital.autotest",
    "com.softwinner.agingdragonbox",
    "com.softwinner.dragonbox",
    "com.ktcp.autoupgrade",
]
print("=== remount / rw ===")
print(sh("mount -o rw,remount /").strip())

print("\n=== rename system APKs ===")
for p in TARGETS:
    path=sh(f"pm path {p}").strip().replace("package:","")
    if not path:
        print(f"  {p}: not installed, skip")
        continue
    if path.endswith(".apk") and path.startswith("/system"):
        bak=path+".bak"
        out=sh(f'mv -f "{path}" "{bak}" 2>&1; ls -l "{bak}" 2>&1')
        print(f"  {p}: {'OK' if '.bak' in out else out.strip()[-80:]}")
    else:
        print(f"  {p}: path={path} (not system apk, skip)")

print("\n=== also remove /data copies if any ===")
for p in TARGETS:
    sh(f"am force-stop {p}")

print("\n=== reboot ===")
print(sh("reboot"))
