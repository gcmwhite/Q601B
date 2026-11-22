#!/usr/bin/env python3
import os
"""Remove the system-copy of KTCP launcher (/system/app/launcher)."""
import subprocess
S = os.environ.get("BOX_IP", "<box-ip>") + ":5555"
SU = "/system/xbin/su 0"

def r(c, timeout=60):
    x = subprocess.run(["adb", "-s", S, "shell", SU + " sh -c " + repr(c)], capture_output=True, timeout=timeout)
    return (x.stdout or b"").decode("utf-8", "ignore") + (x.stderr or b"").decode("utf-8", "ignore")

print("=== mount rw ===")
print(r("mount -o rw,remount /"))

print("=== force-stop ktcp ===")
print(r("am force-stop com.ktcp.launcher"))

print("=== delete system launcher APK ===")
print(r("ls -la /system/app/launcher/"))
print(r("rm -f /system/app/launcher/launcher.apk; ls -la /system/app/launcher/"))

print("=== delete homepage dir if recreated ===")
print(r("rm -rf /system/app/homepage; ls -ld /system/app/homepage 2>&1"))

print("=== disable + set default ===")
print(r("pm disable-user com.ktcp.launcher"))
print(r("cmd package set-home-activity me.efesser.flauncher/.MainActivity"))
