#!/usr/bin/env python3
import os
"""Install 全民K歌 / 观屿TV / 千寻直播."""
import subprocess, os
S = os.environ.get("BOX_IP", "<box-ip>") + ":5555"
SU="/system/xbin/su 0"
OUT="f:/work/jiguang/downloads"

def sh(c, su=False, timeout=120):
    cmd=["adb","-s",S,"shell"]+(["/system/xbin/su","0","sh","-c",repr(c)] if su else [c])
    r=subprocess.run(cmd,capture_output=True,timeout=timeout)
    return (r.stdout or b"").decode("utf-8","ignore")+(r.stderr or b"").decode("utf-8","ignore")

apps = [
    ("quanminKtv.apk", "全民K歌"),
    ("voyatv.apk", "观屿TV"),
    ("qianxun.apk", "千寻直播"),
]
for i,(fn,label) in enumerate(apps):
    local=os.path.join(OUT,fn)
    remote=f"/data/local/tmp/app{i}.apk"
    print(f"\n=== {label} ({fn}) ===")
    subprocess.run(["adb","-s",S,"push",local,remote],check=True)
    out=sh(f"pm install -r -g {remote}", su=True, timeout=180).strip()
    print(f"  install: {out}")
    sh(f"rm -f {remote}", su=True)

print("\n=== installed packages ===")
print(sh("pm list packages | grep -iE 'ktv|voya|nb9|xun|qianxun|全民'").strip())
