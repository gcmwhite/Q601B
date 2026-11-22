#!/usr/bin/env python3
import os
"""Final verification of Projectivy desktop setup."""
import subprocess
S = os.environ.get("BOX_IP", "<box-ip>") + ":5555"
SU="/system/xbin/su 0"
def sh(c,su=False,t=40):
    cmd=["adb","-s",S,"shell"]+(["/system/xbin/su","0","sh","-c",repr(c)] if su else [c])
    return subprocess.run(cmd,capture_output=True,timeout=t).stdout.decode("utf-8","ignore")

print("=== DESKTOP ===")
print("default HOME:", sh("cmd package resolve-activity --brief -a android.intent.action.MAIN -c android.intent.category.HOME").strip().splitlines()[-1])
print("foreground:", sh("dumpsys activity activities | grep -m1 -i ResumedActivity",su=True).strip()[:100])
print("proc:", sh("ps -A | grep projengmenu | grep -v grep",su=True).strip()[:80])

print("\n=== A11Y ===")
print("service:", sh("settings get secure enabled_accessibility_services",su=True).strip())
print("enabled:", sh("settings get secure accessibility_enabled",su=True).strip())

print("\n=== APPS ===")
for pkg,label in [("com.spocky.projengmenu","Projectivy"),("com.hongguotv.nativeapp","红果TV"),
                  ("xyz.nb9.xptv","观屿TV"),("com.tv.qx","千寻直播"),
                  ("com.skyworthdigital.mediarender","投屏")]:
    print(f"  {label}: {'OK' if sh(f'pm path {pkg}').strip() else 'MISS'}")
print("  全民K歌:", "GONE (user removed)" if not sh("pm path com.tencent.karaoketv").strip() else "STILL THERE")
print("  FLauncher:", sh("pm list packages -d | grep flauncher || echo enabled",su=True).strip())

print("\n=== SYSTEM ===")
print("boot:", sh("getprop sys.boot_completed").strip(), "root:", sh("id",su=True).strip().split()[0])
print("mem:", sh("grep MemAvailable /proc/meminfo",su=True).strip())
print("adb:", sh("getprop service.adb.tcp.port",su=True).strip())
