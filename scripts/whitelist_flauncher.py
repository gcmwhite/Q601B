#!/usr/bin/env python3
import os
"""Add FLauncher to the system's HOME whitelist (enable_launcher_components)."""
import subprocess
S = os.environ.get("BOX_IP", "<box-ip>") + ":5555"
SU = "/system/xbin/su 0"

def r(c, timeout=40):
    x = subprocess.run(["adb", "-s", S, "shell", SU + " sh -c " + repr(c)], capture_output=True, timeout=timeout)
    return (x.stdout or b"").decode("utf-8", "ignore") + (x.stderr or b"").decode("utf-8", "ignore")

print("=== current whitelist ===")
cur = r("settings get global enable_launcher_components").strip()
print(cur)

if "me.efesser.flauncher" not in cur:
    new = cur + "/me.efesser.flauncher"
    print("\n=== new whitelist ===")
    print(new)
    print(r(f'settings put global enable_launcher_components "{new}"'))
else:
    print("\nAlready whitelisted")

print("\n=== verify ===")
print(r("settings get global enable_launcher_components"))

print("\n=== set as home ===")
print(r("cmd package set-home-activity me.efesser.flauncher/.MainActivity"))
print("resolve:", r("cmd package resolve-activity --brief -a android.intent.action.MAIN -c android.intent.category.HOME").strip())

print("\n=== launch ===")
print(r("am start -n me.efesser.flauncher/.MainActivity"))
