#!/usr/bin/env python3
import os
"""Set FLauncher as default HOME on the clean system."""
import subprocess
S = os.environ.get("BOX_IP", "<box-ip>") + ":5555"
SU = "/system/xbin/su 0"

def sh(c, su=False):
    cmd=["adb","-s",S,"shell"]+(["/system/xbin/su","0","sh","-c",repr(c)] if su else [c])
    x=subprocess.run(cmd,capture_output=True,timeout=40)
    return (x.stdout or b"").decode("utf-8","ignore")+(x.stderr or b"").decode("utf-8","ignore")

print("=== set HOME ===")
print(sh("cmd package set-home-activity me.efesser.flauncher/.MainActivity", su=True))
print("=== verify resolve ===")
print(sh("cmd package resolve-activity --brief -a android.intent.action.MAIN -c android.intent.category.HOME"))
print("=== flauncher is HOME role holder? ===")
print(sh("dumpsys role | grep -i -A3 'HOME' | head -10", su=True))
