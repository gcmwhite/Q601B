#!/usr/bin/env python3
import os
"""Enable FLauncher and make it the default HOME."""
import subprocess
S = os.environ.get("BOX_IP", "<box-ip>") + ":5555"
SU = "/system/xbin/su 0"

def r(c, timeout=60):
    x = subprocess.run(["adb", "-s", S, "shell", SU + " sh -c " + repr(c)], capture_output=True, timeout=timeout)
    return (x.stdout or b"").decode("utf-8", "ignore") + (x.stderr or b"").decode("utf-8", "ignore")

print("=== enable flauncher ===")
print(r("pm enable me.efesser.flauncher"))
print(r("pm dump me.efesser.flauncher | grep -m1 'User 0:'"))

print("\n=== set HOME ===")
print(r("cmd package set-home-activity me.efesser.flauncher/.MainActivity"))

print("\n=== resolve ===")
print(r("cmd package resolve-activity --brief -a android.intent.action.MAIN -c android.intent.category.HOME"))

print("\n=== clear stopped state / launch ===")
print(r("am start -n me.efesser.flauncher/.MainActivity"))
