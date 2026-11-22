#!/usr/bin/env python3
import os
"""Remove the FLauncher watchdog from sky_check.sh (no longer needed after root patch)."""
import subprocess
S = os.environ.get("BOX_IP", "<box-ip>") + ":5555"
SU="/system/xbin/su 0"
def sh(c, timeout=40):
    return subprocess.run(["adb","-s",S,"shell",SU+" sh -c "+repr(c)],capture_output=True,timeout=timeout).stdout.decode("utf-8","ignore")

print("=== restore original sky_check.sh ===")
print(sh("mount -o rw,remount /"))
# original backup was made during watchdog setup
print(sh("cp /data/local/tmp/sky_check.sh.orig /system/bin/sky_check.sh 2>&1; chmod 755 /system/bin/sky_check.sh"))
print(sh("grep -c FLauncher /system/bin/sky_check.sh 2>&1; echo '(0 = removed)'"))
print("\n=== also remove the unused daemon files ===")
print(sh("rm -f /system/bin/flauncher_daemon.sh /system/etc/init/flauncher_daemon.rc 2>&1"))
print("\nReady to reboot and verify without watchdog.")
