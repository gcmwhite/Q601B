#!/usr/bin/env python3
import os
"""Install patched services.jar safely. Does NOT touch provision or any APK."""
import subprocess
S = os.environ.get("BOX_IP", "<box-ip>") + ":5555"
SU = "/system/xbin/su 0"
LOCAL = "f:/work/jiguang/services_root.jar"
JAR = "/system/framework/services.jar"
OAT = "/system/framework/oat/arm"

def sh(c, su=True, timeout=90):
    cmd=["adb","-s",S,"shell"] + (["/system/xbin/su","0","sh","-c",repr(c)] if su else [c])
    x=subprocess.run(cmd,capture_output=True,timeout=timeout)
    return (x.stdout or b"").decode("utf-8","ignore") + (x.stderr or b"").decode("utf-8","ignore")

print("=== remount rw ===")
print(sh("mount -o rw,remount /"))

print("\n=== backup current jar on device ===")
print(sh(f"cp {JAR} /data/local/tmp/services.jar.stock; md5sum /data/local/tmp/services.jar.stock"))

print("\n=== push patched jar ===")
subprocess.run(["adb","-s",S,"push",LOCAL,"/data/local/tmp/services_root.jar"], check=True)
print(sh(f"cp /data/local/tmp/services_root.jar {JAR}; chmod 644 {JAR}; chown root:root {JAR}; md5sum {JAR}"))

print("\n=== remove odex/vdex/art (force rebuild) ===")
print(sh(f"rm -f {OAT}/services.odex {OAT}/services.vdex {OAT}/services.art"))
print(sh(f"ls -la {OAT}/services.* 2>&1"))

print("\n=== verify provision untouched ===")
print(sh("pm list packages com.android.provision"))
print("\nReady to reboot.")
