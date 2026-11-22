#!/usr/bin/env python3
"""Download and install FLauncher (armeabi-v7a) on TencentBox Q601B."""
import urllib.request
import ssl
import os
import subprocess

URL = "https://github.com/osrosal/flauncher/releases/download/v2025.07.001/flauncher-armeabi-v7a-release.apk"
LOCAL = "f:/work/jiguang/flauncher-armeabi-v7a-release.apk"
SERIAL = os.environ.get("BOX_IP", "<box-ip>") + ":5555"

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

if not os.path.exists(LOCAL):
    print(f"Downloading {URL} ...")
    req = urllib.request.Request(URL, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=120, context=ctx) as r:
        data = r.read()
    with open(LOCAL, "wb") as f:
        f.write(data)
    print(f"Downloaded {len(data)/1e6:.1f} MB")
else:
    print(f"Using existing {LOCAL} ({os.path.getsize(LOCAL)/1e6:.1f} MB)")

print("\nPushing to device ...")
subprocess.run(["adb", "-s", SERIAL, "push", LOCAL, "/data/local/tmp/flauncher.apk"], check=True)

print("\nInstalling ...")
r = subprocess.run(["adb", "-s", SERIAL, "shell", "pm", "install", "-r", "/data/local/tmp/flauncher.apk"],
                   capture_output=True, text=True, timeout=120)
print(r.stdout, r.stderr)
print("\nPackage check:")
print(subprocess.run(["adb", "-s", SERIAL, "shell", "pm", "path", "me.efesser.flauncher"],
                     capture_output=True, text=True).stdout)
