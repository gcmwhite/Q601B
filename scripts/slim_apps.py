#!/usr/bin/env python3
import os
"""Disable bloatware on TencentBox Q601B (reversible via restore_apps.py)."""
import subprocess
import sys

SERIAL = os.environ.get("BOX_IP", "<box-ip>") + ":5555"

BATCH1 = [
    "com.tianci.ad",
    "com.skyworthdigital.ott.advert.app",
    "com.dangbei.lerad.videoposter",
    "com.skyworthdigital.ottstatsv2",
    "com.skyworthdigital.logcollector",
    "com.skyworthdigital.upgrade",
    "com.skyworthdigital.skyappupdate",
    "com.ktcp.autoupgrade",
    "com.skyworthdigital.autotest",
    "com.softwinner.agingdragonbox",
    "com.softwinner.dragonbox",
]

SU = "/system/xbin/su 0"

def adb(args):
    r = subprocess.run(["adb", "-s", SERIAL] + args, capture_output=True, text=True, timeout=30)
    return (r.stdout or "").strip() + (r.stderr or "").strip()

def rootpm(*args):
    cmd = SU + " pm " + " ".join(args)
    return adb(["shell", cmd])

print("=== Batch 1: disabling bloatware (as root) ===")
for pkg in BATCH1:
    out = rootpm("disable-user", pkg)
    ok = "disabled" in out.lower() or out == ""
    print(f"  [{'OK' if ok else 'FAIL'}] {pkg}: {out[:80]}")

print("\n=== Currently disabled packages ===")
print(rootpm("list", "packages", "-d"))
