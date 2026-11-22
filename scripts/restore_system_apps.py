#!/usr/bin/env python3
import os
"""Restore the system APKs that were deleted to free /system space.

Only needed if you want the original (ad/test/upgrade) apps back.
FLauncher stays installed regardless.
"""
import subprocess
S = os.environ.get("BOX_IP", "<box-ip>") + ":5555"
SU = "/system/xbin/su 0"

def sh(c, timeout=60):
    x = subprocess.run(["adb","-s",S,"shell",SU+" sh -c "+repr(c)], capture_output=True, timeout=timeout)
    return (x.stdout or b"").decode("utf-8","ignore") + (x.stderr or b"").decode("utf-8","ignore")

print("Restoring system APKs from the full backup requires extracting the")
print("'super' partition and copying individual APKs. Simplest: reflash super")
print("with scripts/restore_super.py, then re-disable bloat with scripts/slim_apps.py.")
print("\nCurrently removed to free space:")
for p in [
    "SkyworthAutoTest", "DragonBox", "DragonAgingTV",
    "SkyUpdateV2-origin", "AppAutoUpgrade", "SkyOttstats-origin", "SkyLogCollector-origin",
]:
    print("  /system/app/" + p)
