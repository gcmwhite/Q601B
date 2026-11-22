#!/usr/bin/env python3
import os
"""Clear provision wizard and set FLauncher as HOME properly."""
import subprocess
S = os.environ.get("BOX_IP", "<box-ip>") + ":5555"
SU = "/system/xbin/su 0"

def r(c, timeout=60):
    x = subprocess.run(["adb", "-s", S, "shell", SU + " sh -c " + repr(c)], capture_output=True, timeout=timeout)
    return (x.stdout or b"").decode("utf-8", "ignore") + (x.stderr or b"").decode("utf-8", "ignore")

print("=== setting device_provisioned ===")
print(r("settings put global device_provisioned 1"))
print(r("settings put secure user_setup_complete 1"))
print(r("settings get global device_provisioned"))

print("\n=== disabling Provision app ===")
print(r("pm disable-user com.android.provision"))

print("\n=== setting FLauncher home ===")
print(r("cmd package set-home-activity me.efesser.flauncher/.MainActivity"))

print("\n=== clearing Home resolver choices ===")
print(r("cmd package clear-pREFERRED-activities 2>&1 || echo 'cmd not available'"))

print("\n=== resolve check ===")
print(r("cmd package resolve-activity --brief -a android.intent.action.MAIN -c android.intent.category.HOME"))
