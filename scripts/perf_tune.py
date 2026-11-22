#!/usr/bin/env python3
import os
"""Performance tuning for 1GB RAM TV box: animations, zram, background limits."""
import subprocess
S = os.environ.get("BOX_IP", "<box-ip>") + ":5555"
SU="/system/xbin/su 0"

def sh(c, timeout=40):
    return subprocess.run(["adb","-s",S,"shell",SU+" sh -c "+repr(c)],capture_output=True,timeout=timeout).stdout.decode("utf-8","ignore")

def adbsh(c, timeout=40):
    return subprocess.run(["adb","-s",S,"shell",c],capture_output=True,timeout=timeout).stdout.decode("utf-8","ignore")

print("=== animation scales (0.5x = snappier) ===")
for k in ["window_animation_scale","transition_animation_scale","animator_duration_scale"]:
    adbsh(f"settings put global {k} 0.5")
    print(f"  {k} = {adbsh(f'settings get global {k}').strip()}")

print("\n=== zram tuning (already 753MB, set swappiness) ===")
sh("sysctl vm.swappiness=60 2>/dev/null || echo 60 > /proc/sys/vm/swappiness")
print("  swappiness:", sh("cat /proc/sys/vm/swappiness").strip())

print("\n=== background process limit ===")
sh("settings put global background_process_limit 12")
print("  limit:", adbsh("settings get global background_process_limit").strip())

print("\n=== disable sentient / unused animations ===")
adbsh("settings put global always_finish_activities 0")

print("\n=== summary ===")
print("  mem available:", sh("grep MemAvailable /proc/meminfo").strip())
