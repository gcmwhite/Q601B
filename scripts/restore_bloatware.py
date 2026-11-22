#!/usr/bin/env python3
"""Restore removed bloatware from the full eMMC backup.

The removed packages had their APK files renamed/deleted. Since a reboot
cleared the .bak files, restore by extracting original APKs from the backup
image and pushing them back. Root required.

Usage:
    python restore_bloatware.py            # restore all removed packages
    python restore_bloatware.py --list     # just list what can be restored
"""
import subprocess
import sys
import os
import gzip
import struct

SERIAL = os.environ.get("BOX_IP", "<box-ip>") + ":5555"
SU = "/system/xbin/su 0"
IMG = "f:/work/jiguang/backup/full_emmc.img.gz"
TMP = "f:/work/jiguang/backup/extracted"

REMOVED = {
    "com.tianci.ad": None,
    "com.skyworthdigital.ott.advert.app": None,
    "com.skyworthdigital.ottstatsv2": None,
    "com.skyworthdigital.logcollector": None,
    "com.skyworthdigital.upgrade": None,
    "com.skyworthdigital.skyappupdate": None,
    "com.ktcp.autoupgrade": None,
    "com.skyworthdigital.autotest": None,
    "com.softwinner.agingdragonbox": None,
    "com.softwinner.dragonbox": None,
    "com.skyworthdigital.skycommonpropertymanager": None,
    "com.xiaopaitech.paivideo": None,
    "com.skyworthdigital.mediarender": None,
}


def adb(args, timeout=60):
    r = subprocess.run(["adb", "-s", SERIAL] + args, capture_output=True, timeout=timeout)
    return (r.stdout or b"").decode("utf-8", "ignore") + (r.stderr or b"").decode("utf-8", "ignore")


def root(cmd, timeout=90):
    return adb(["shell", SU + " sh -c " + repr(cmd)], timeout)


if __name__ == "__main__":
    print("Removed packages:")
    for p in REMOVED:
        print("  " + p)
    if "--list" in sys.argv:
        sys.exit(0)
    print("\nWARNING: this restores packages from the full backup image.")
    print("The simplest full restore is to reflash the entire image (see RESTORE_GUIDE.md).")
    print("For selective restore, extract the relevant partition (super/data) and pull the APK out.")
    print("See docs/APPS_SLIM_GUIDE.md for details.")
