#!/usr/bin/env python3
import os
"""Make FLauncher the only HOME app so no resolver dialog appears."""
import subprocess
SERIAL = os.environ.get("BOX_IP", "<box-ip>") + ":5555"
SU = "/system/xbin/su 0"

def root(cmd, timeout=40):
    r = subprocess.run(["adb", "-s", SERIAL, "shell", SU + " sh -c " + repr(cmd)], capture_output=True, timeout=timeout)
    return (r.stdout or b"").decode("utf-8", "ignore") + (r.stderr or b"").decode("utf-8", "ignore")

OTHER_LAUNCHERS = [
    "com.ktcp.launcher",
    "com.dangbei.tvlauncher",
    "com.xiaopaitech.plauncher",
]

print("Disabling other launchers ...")
for p in OTHER_LAUNCHERS:
    out = root(f"pm disable-user {p}")
    print(f"  {p}: {out.strip()}")

print("\nSetting FLauncher as preferred home ...")
print(root("cmd package set-home-activity me.efesser.flauncher/.MainActivity").strip())

print("\nVerifying HOME resolution ...")
for p in ["me.efesser.flauncher"] + OTHER_LAUNCHERS:
    res = root(f"pm dump {p} 2>/dev/null | grep -m1 -A1 'enabled='")
    state = "enabled" if "enabled=true" in res or ("enabled=" in res and "enabled=false" not in res) else "DISABLED"
    print(f"  {p}: {state}")

print("\nResolving HOME intent ...")
print(root("cmd package resolve-activity --brief -a android.intent.action.MAIN -c android.intent.category.HOME").strip())
