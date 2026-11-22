#!/usr/bin/env python3
import os
"""Storage cleanup: clear caches, tombstones, logs; remove data of deleted apps."""
import subprocess
S = os.environ.get("BOX_IP", "<box-ip>") + ":5555"
SU="/system/xbin/su 0"
def sh(c,timeout=90):
    return subprocess.run(["adb","-s",S,"shell",SU+" sh -c "+repr(c)],capture_output=True,timeout=timeout).stdout.decode("utf-8","ignore")

print("=== before ===")
print(sh("df -h /data /cache | tail -2").strip())

print("\n=== clear caches of unused apps (mipt/dangbei already disabled) ===")
for p in ["com.mipt.store","com.dangbeimarket","com.dangbei.tvlauncher","com.xiaopaitech.paivideo","com.android.noticewidget","com.android.syswidget"]:
    out=sh(f"rm -rf /data/data/{p}/cache /sdcard/Android/data/{p}/cache 2>&1")
    print(f"  {p}: cleaned")

print("\n=== clear crash tombstones ===")
print(sh("rm -rf /data/tombstones/* 2>&1; du -sm /data/tombstones").strip())

print("\n=== clear old logs ===")
print(sh("rm -rf /data/log/* /data/misc/logd/* 2>/dev/null; du -sm /data/log /data/misc/logd 2>/dev/null").strip())

print("\n=== clear removed apps' data dirs ===")
for p in ["com.tianci.ad","com.skyworthdigital.ott.advert.app","com.skyworthdigital.ottstatsv2",
          "com.skyworthdigital.logcollector","com.skyworthdigital.skycommonpropertymanager",
          "com.dangbei.lerad.videoposter","com.sohu.inputmethod.sogou.tv","tv.newtv.loginservice"]:
    sh(f"rm -rf /data/data/{p} /sdcard/Android/data/{p} 2>/dev/null")
print("  done")

print("\n=== trim caches (pm trim-caches) ===")
print(sh("pm trim-caches 200M 2>&1 | tail -2").strip())

print("\n=== after ===")
print(sh("df -h /data /cache | tail -2").strip())
print("mem:", sh("grep MemAvailable /proc/meminfo").strip())
