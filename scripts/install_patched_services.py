#!/usr/bin/env python3
import os
"""Install patched services.jar to remove HOME app block."""
import subprocess
S = os.environ.get("BOX_IP", "<box-ip>") + ":5555"
SU = "/system/xbin/su 0"
LOCAL = "f:/work/jiguang/services_patched2.jar"
DEVICE_JAR = "/system/framework/services.jar"

def r(c, timeout=60):
    x = subprocess.run(["adb", "-s", S, "shell", SU + " sh -c " + repr(c)], capture_output=True, timeout=timeout)
    return (x.stdout or b"").decode("utf-8", "ignore") + (x.stderr or b"").decode("utf-8", "ignore")

print("=== checking current jar ===")
print(r(f"ls -l {DEVICE_JAR}"))

print("\n=== backup original on device ===")
print(r(f"cp {DEVICE_JAR} {DEVICE_JAR}.bak 2>&1; ls -l {DEVICE_JAR}.bak"))

print("\n=== mount rw ===")
print(r("mount -o rw,remount /"))

print("\n=== push patched jar ===")
subprocess.run(["adb", "-s", S, "push", LOCAL, "/data/local/tmp/services_patched.jar"], check=True)
print(r(f"cp /data/local/tmp/services_patched.jar {DEVICE_JAR} 2>&1; chmod 644 {DEVICE_JAR}; chown root:root {DEVICE_JAR}; ls -l {DEVICE_JAR}"))

print("\n=== verify patch in installed jar (string check) ===")
print(r(f"md5sum {DEVICE_JAR} {DEVICE_JAR}.bak"))
