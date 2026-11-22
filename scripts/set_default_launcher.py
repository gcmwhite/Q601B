#!/usr/bin/env python3
import os
"""Set FLauncher as the default HOME app on TencentBox Q601B."""
import subprocess
SERIAL = os.environ.get("BOX_IP", "<box-ip>") + ":5555"
SU = "/system/xbin/su 0"

def adb(args, timeout=40):
    r = subprocess.run(["adb", "-s", SERIAL] + args, capture_output=True, timeout=timeout)
    return (r.stdout or b"").decode("utf-8", "ignore") + (r.stderr or b"").decode("utf-8", "ignore")

def root(cmd, timeout=40):
    return adb(["shell", SU + " sh -c " + repr(cmd)], timeout)

PKG = "me.efesser.flauncher"
ACT = PKG + "/.MainActivity"

# 1. clear preferred activities for HOME category
print("Clearing HOME preferred ...")
print(root("cmd package clear-pREFERRED-activities 2>&1") if False else "")

# 2. Disable other launchers so there's only one HOME candidate
OTHER_LAUNCHERS = [
    "com.ktcp.launcher",
    "com.dangbei.tvlauncher",
    "com.xiaopaitech.plauncher",
]
print("Disabling other launchers ...")
for p in OTHER_LAUNCHERS:
    out = root(f"pm disable-user {p}")
    print(f"  {p}: {out.strip()}")

# 3. Set FLauncher preferred via 'cmd package set-home-activity' if available
print("\nTrying cmd package set-home-activity ...")
print(root(f"cmd package set-home-activity {ACT} 2>&1").strip())

# 4. fallback: use 'pm set-home-activity'
print("\nTrying pm set-home-activity ...")
print(root(f"pm set-home-activity {ACT} 2>&1").strip())

# 5. verify
print("\n=== current HOME activity ===")
print(root("cmd package resolve-activity --brief -a android.intent.action.MAIN -c android.intent.category.HOME 2>&1").strip())
