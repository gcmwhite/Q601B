#!/usr/bin/env python3
import os
"""Manage autostart apps: disable BOOT_COMPLETED receivers for unneeded apps via pm disable-user.

Keeps: mediarender (投屏, will restore), core Android providers, systemui.
"""
import subprocess
S = os.environ.get("BOX_IP", "<box-ip>") + ":5555"
SU="/system/xbin/su 0"

def sh(c, timeout=40):
    return subprocess.run(["adb","-s",S,"shell",SU+" sh -c "+repr(c)],capture_output=True,timeout=timeout).stdout.decode("utf-8","ignore")

# Apps with BOOT_COMPLETED that are safe to disable autostart for (not the app itself,
# but we use pm disable-user which disables entirely - only for truly unneeded ones)
DISABLE = [
    "com.duokan.duokanplayer",       # 多看书城/播放器自启
    "com.mipt.store",                 # 应用市场自启推送
]
# keep com.android.* providers, mediarender (投屏), provision

print("=== current disabled ===")
print(sh("pm list packages -d").strip())

print("\n=== disable unneeded autostart apps ===")
for p in DISABLE:
    out = sh(f"pm disable-user {p}").strip()
    print(f"  {p}: {out}")

print("\n=== verify BOOT_COMPLETED receivers remaining ===")
print(sh("dumpsys package | grep -B3 'BOOT_COMPLETED' | grep -oE 'com\\.[a-zA-Z0-9.]+' | sort -u").strip())
