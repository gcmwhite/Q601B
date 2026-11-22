#!/usr/bin/env python3
import os
"""Disable other launchers so FLauncher is the only HOME."""
import subprocess
S = os.environ.get("BOX_IP", "<box-ip>") + ":5555"
SU = "/system/xbin/su 0"

def sh(c):
    x=subprocess.run(["adb","-s",S,"shell",SU+" sh -c "+repr(c)],capture_output=True,timeout=40)
    return (x.stdout or b"").decode("utf-8","ignore")+(x.stderr or b"").decode("utf-8","ignore")

LAUNCHERS = ["com.ktcp.launcher", "com.dangbei.tvlauncher", "com.xiaopaitech.plauncher"]
print("=== disabling ===")
for p in LAUNCHERS:
    print(f"  {p}: {sh('pm disable-user '+p).strip()}")

print("\n=== ensure FLauncher enabled + home ===")
print(sh("pm enable me.efesser.flauncher"))
print(sh("cmd package set-home-activity me.efesser.flauncher/.MainActivity"))

print("\n=== HOME resolve now ===")
print(sh("cmd package resolve-activity --brief -a android.intent.action.MAIN -c android.intent.category.HOME"))
