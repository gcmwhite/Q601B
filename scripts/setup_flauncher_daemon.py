#!/usr/bin/env python3
import os
"""Setup a root daemon that keeps FLauncher as the foreground HOME.

Similar to the M18C ras-daemon approach: on boot, wait for boot_completed,
then force-stop provision and launch FLauncher. Watchdog checks every 5s;
if provision/other launcher comes to front, switch back to FLauncher.
"""
import subprocess, os
S = os.environ.get("BOX_IP", "<box-ip>") + ":5555"
SU = "/system/xbin/su 0"
SCRIPT_LOCAL = "f:/work/jiguang/scripts/flauncher_daemon.sh"
RC_LOCAL = "f:/work/jiguang/scripts/flauncher_daemon.rc"

def sh(c, su=True, timeout=40):
    cmd=["adb","-s",S,"shell"]+(["/system/xbin/su","0","sh","-c",repr(c)] if su else [c])
    x=subprocess.run(cmd,capture_output=True,timeout=timeout)
    return (x.stdout or b"").decode("utf-8","ignore")+(x.stderr or b"").decode("utf-8","ignore")

daemon_script = '''#!/system/bin/sh
# Keep FLauncher as the active HOME on TencentBox Q601B
# Only intercepts the provision wizard / old launchers, does not disturb user apps.
COMP="me.efesser.flauncher/me.efesser.flauncher.MainActivity"

# Wait for boot complete
while [ "$(getprop sys.boot_completed)" != "1" ]; do
    sleep 2
done
sleep 4

# Initial: clear wizard and show FLauncher
am force-stop com.android.provision
am start -n $COMP >/dev/null 2>&1

while true; do
    top=$(dumpsys activity activities 2>/dev/null | grep -m1 'mResumedActivity')
    case "$top" in
        *com.android.provision/*|*com.ktcp.launcher/*|*com.xiaopaitech.plauncher/*)
            am force-stop com.android.provision 2>/dev/null
            am force-stop com.ktcp.launcher 2>/dev/null
            am force-stop com.xiaopaitech.plauncher 2>/dev/null
            am start -n $COMP >/dev/null 2>&1
            ;;
    esac
    sleep 4
done
'''

rc_content = '''service flauncher_daemon /system/bin/flauncher_daemon.sh
    class main
    user root
    group root
    oneshot
'''

open(SCRIPT_LOCAL,"w").write(daemon_script)
open(RC_LOCAL,"w").write(rc_content)
print("created local daemon scripts")

print("\n=== push daemon ===")
subprocess.run(["adb","-s",S,"push",SCRIPT_LOCAL,"/data/local/tmp/flauncher_daemon.sh"],check=True)
print(sh("mount -o rw,remount /"))
print(sh("cp /data/local/tmp/flauncher_daemon.sh /system/bin/flauncher_daemon.sh; chmod 755 /system/bin/flauncher_daemon.sh"))
subprocess.run(["adb","-s",S,"push",RC_LOCAL,"/data/local/tmp/flauncher_daemon.rc"],check=True)
print(sh("cp /data/local/tmp/flauncher_daemon.rc /system/etc/init/flauncher_daemon.rc; chmod 644 /system/etc/init/flauncher_daemon.rc"))

print("\n=== test run daemon manually (background) ===")
print(sh("/system/bin/flauncher_daemon.sh >/dev/null 2>&1 &"))
