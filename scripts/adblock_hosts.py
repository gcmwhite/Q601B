#!/usr/bin/env python3
import os
"""Install ad-blocking hosts file on the TV box.

Targets: 创维/腾讯广告、统计上报、OTT 广告 SDK 常见域名.
Conservative list - only advertising/telemetry domains, nothing that would
break video apps. Original hosts backed up on device.
"""
import subprocess, os
S = os.environ.get("BOX_IP", "<box-ip>") + ":5555"
SU="/system/xbin/su 0"
LOCAL="f:/work/jiguang/temp/hosts_adblock"

HOSTS = """127.0.0.1       localhost
::1             ip6-localhost

# === 创维/腾讯 OTT 广告与统计 ===
127.0.0.1 ad.skyworth.com
127.0.0.1 ads.skyworth.com
127.0.0.1 adver.skyworth.com
127.0.0.1 stat.skyworth.com
127.0.0.1 stats.skyworth.com
127.0.0.1 log.skyworth.com
127.0.0.1 report.skyworth.com
127.0.0.1 upgrade.skyworth.com
127.0.0.1 ota.skyworth.com
127.0.0.1 appupgrade.skyworth.com
127.0.0.1 ad.skyworthtv.com
127.0.0.1 ads.skyworthtv.com
127.0.0.1 skyworthbox.com
127.0.0.1 www.skyworthbox.com
127.0.0.1 appupgrade.skyworthbox.com
127.0.0.1 upgrade.skyworthbox.com
127.0.0.1 ota.skyworthbox.com

# === 腾讯视频/极光广告 ===
127.0.0.1 ad.qq.com
127.0.0.1 ads.qq.com
127.0.0.1 ad.qqlive.com
127.0.0.1 adtv.qq.com
127.0.0.1 vpic.qq.com
127.0.0.1 puui.qpic.cn
127.0.0.1 ppmy.qpic.cn
127.0.0.1 ad.qpic.cn
127.0.0.1 video.qpic.cn
127.0.0.1 stat.qqlive.com
127.0.0.1 report.qqlive.com
127.0.0.1 beacon.qq.com
127.0.0.1 ping.qq.com
127.0.0.1 sdc.qq.com
127.0.0.1 othersdt.qq.com
127.0.0.1 pgdt.qq.com

# === 当贝/乐播/广告 SDK ===
127.0.0.1 ad.dangbei.com
127.0.0.1 ads.dangbei.com
127.0.0.1 stat.dangbei.com
127.0.0.1 api.dangbei.com
127.0.0.1 ad.hpplay.com.cn
127.0.0.1 stats.hpplay.com.cn

# === 常见移动广告联盟 ===
127.0.0.1 ad.doubleclick.net
127.0.0.1 googleads.g.doubleclick.net
127.0.0.1 pagead2.googlesyndication.com
127.0.0.1 admob.com
127.0.0.1 ad.baidu.com
127.0.0.1 dup.baidustatic.com
127.0.0.1 cpro.baidu.com
127.0.0.1 ad.cctv.com
127.0.0.1 pos.baidu.com
127.0.0.1 e.1400.com.cn
127.0.0.1 m.1400.com.cn

# === 统计/埋点 ===
127.0.0.1 umeng.com
127.0.0.1 log.umeng.com
127.0.0.1 mobile.umeng.com
127.0.0.1 sensorsdata.cn
127.0.0.1 sa.sensorsdata.cn
127.0.0.1 talkingdata.com
127.0.0.1 log.tendcloud.com
127.0.0.1 analytics.oplus.com
"""

def sh(c, timeout=40):
    return subprocess.run(["adb","-s",S,"shell",SU+" sh -c "+repr(c)],capture_output=True,timeout=timeout).stdout.decode("utf-8","ignore")

os.makedirs(os.path.dirname(LOCAL),exist_ok=True)
open(LOCAL,"w").write(HOSTS)
print(f"local hosts: {len(HOSTS.splitlines())} lines")

print("=== backup original on device ===")
print(sh("cp /system/etc/hosts /system/etc/hosts.bak 2>&1; ls -l /system/etc/hosts.bak").strip())

print("=== push hosts ===")
subprocess.run(["adb","-s",S,"push",LOCAL,"/data/local/tmp/hosts_ad"],check=True)
print(sh("mount -o rw,remount /; cp /data/local/tmp/hosts_ad /system/etc/hosts; chmod 644 /system/etc/hosts; chown root:root /system/etc/hosts; ls -l /system/etc/hosts").strip())

print("=== verify ===")
print("lines:", sh("wc -l /system/etc/hosts").strip())
print("sample:", sh("grep -E 'skyworth|doubleclick|umeng' /system/etc/hosts | head -3").strip())

print("=== clear DNS cache ===")
print(sh("setprop net.dnschange 1; echo cleared").strip())
