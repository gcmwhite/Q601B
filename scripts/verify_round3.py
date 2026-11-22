#!/usr/bin/env python3
import os
"""Final verification of adblock/slim/cleanup round."""
import subprocess
S = os.environ.get("BOX_IP", "<box-ip>") + ":5555"
SU="/system/xbin/su 0"
def sh(c,su=False,timeout=40):
    cmd=["adb","-s",S,"shell"]+(["/system/xbin/su","0","sh","-c",repr(c)] if su else [c])
    return subprocess.run(cmd,capture_output=True,timeout=timeout).stdout.decode("utf-8","ignore")

print("=== ADB ===")
print(sh("getprop service.adb.tcp.port",True).strip(), sh("getprop ro.adb.secure",True).strip())

print("=== BOOT ===")
print(sh("getprop sys.boot_completed").strip(), sh("getprop dev.bootcomplete").strip())

print("=== HOME ===")
print(sh("cmd package resolve-activity --brief -a android.intent.action.MAIN -c android.intent.category.HOME").strip().splitlines()[-1])
print("top:", sh("dumpsys activity activities | grep -m1 -i ResumedActivity").strip()[:80])

print("=== ADBLOCK ===")
print("hosts lines:", sh("wc -l /system/etc/hosts",True).strip())
print("ad domains:", sh("grep -c '^127.0.0.1' /system/etc/hosts",True).strip())
# test DNS resolution of an ad domain
print("resolve ad.skyworth.com:", sh("ping -c 1 -W 1 ad.skyworth.com 2>&1 | head -1",True).strip()[:80])

print("=== APPS ===")
for pkg in ["com.hongguotv.nativeapp","me.efesser.flauncher","com.tencent.karaoketv","xyz.nb9.xptv","com.tv.qx","com.skyworthdigital.mediarender"]:
    print(f"  {'OK' if sh(f'pm path {pkg}').strip() else 'MISS'} {pkg}")
print("bloat:", sh("pm list packages | grep -iE 'skycommonprop|ottstats|logcollector|tianci.ad|ott.advert' || echo CLEAN",True).strip())

print("=== STORAGE ===")
print(sh("df -h /data | tail -1",True).strip())
print("mem:", sh("grep MemAvailable /proc/meminfo",True).strip())
