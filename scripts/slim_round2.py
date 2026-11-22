#!/usr/bin/env python3
import os
"""Round 2 slimming: remove ad/stats/upgrade/test bloat that came back after super restore.

Uses disable first; if guardian re-enables, rename APK. Records everything.
"""
import subprocess
S = os.environ.get("BOX_IP", "<box-ip>") + ":5555"
SU="/system/xbin/su 0"
def sh(c,timeout=60):
    return subprocess.run(["adb","-s",S,"shell",SU+" sh -c "+repr(c)],capture_output=True,timeout=timeout).stdout.decode("utf-8","ignore")

# Bloat that came back
TARGETS = [
    "com.tianci.ad",                                   # 广告
    "com.skyworthdigital.ott.advert.app",              # 广告
    "com.skyworthdigital.ottstatsv2",                  # 统计
    "com.skyworthdigital.logcollector",                # 日志
    "com.skyworthdigital.upgrade",                     # OTA（注意：system分区的之前的备份没在）
    "com.skyworthdigital.skyappupdate",                # 应用升级
    "com.ktcp.autoupgrade",                            # KTCP升级
    "com.skyworthdigital.autotest",                    # 测试
    "com.softwinner.agingdragonbox",                   # 老化测试
    "com.softwinner.dragonbox",                        # 龙盒测试
    "com.skyworthdigital.skycommonpropertymanager",    # 守护者
    "com.dangbei.lerad.videoposter",                   # 当贝广告
]
# Additional: unused vendor apps (safe to disable)
MORE = [
    "com.sohu.inputmethod.sogou.tv",    # 搜狗输入法（有FLauncher内置输入足够）
    "tv.newtv.loginservice",            # 运营商登录
    "cn.lezhi.speedtest_tv",            # 测速
    "com.skyworthdigital.skywechatclient", # 微信互联
]

print("=== currently disabled ===")
print(sh("pm list packages -d").strip())

print("\n=== disable bloat (batch1) ===")
for p in TARGETS:
    out=sh(f"pm disable-user {p}").strip()
    print(f"  {p}: {out[:60]}")

print("\n=== disable optional (batch2) ===")
for p in MORE:
    out=sh(f"pm disable-user {p}").strip()
    print(f"  {p}: {out[:60]}")

print("\n=== force-stop all ===")
for p in TARGETS+MORE:
    sh(f"am force-stop {p}")

print("\n=== disabled count ===")
print(sh("pm list packages -d | wc -l").strip())
