# 广告屏蔽 / 应用管理 / 存储清理 记录

日期：2026-11-22

## 1. 网络广告屏蔽（已完成）

`/system/etc/hosts` 写入 70 行（59 个屏蔽域名），覆盖：
- 创维/腾讯 OTT 广告与统计（ad.skyworth.com、upgrade.skyworthbox.com、ad.qq.com 等）
- 当贝/乐播广告 SDK
- 常见广告联盟（doubleclick、百度推广）
- 统计埋点（umeng、sensorsdata、talkingdata）

验证：`ping ad.skyworth.com` → `unknown host`（解析被拦截）✓

原始 hosts 只有 localhost 两行，恢复时写回即可。

## 2. 应用管理（已完成）

**背景**：之前写回 super 分区恢复系统时，广告 App 和守护者又全部复活了。这次彻底删除。

**删除的 APK**（`/data/app` 和 `/system/app` 里的 base.apk 重命名为 .bak，重启后包管理器自动清除注册）：
- `com.skyworthdigital.skycommonpropertymanager` —— 守护者（会自动 enable 其他广告包）
- `com.skyworthdigital.ott.advert.app` —— 广告
- `com.skyworthdigital.ottstatsv2` —— 统计
- `com.skyworthdigital.logcollector` —— 日志上传
- `com.skyworthdigital.skyappupdate` —— 应用升级
- `com.tianci.ad` —— 广告（disabled + 删 /data APK，system 副本残留但已禁用）

**稳定禁用的包**（8 个，重启保持）：
```
com.sohu.inputmethod.sogou.tv      搜狗输入法
com.ktcp.launcher                  KTCP 桌面
com.xiaopaitech.plauncher          派桌面
tv.newtv.loginservice              运营商登录
cn.lezhi.speedtest_tv              测速
com.mipt.store                     应用市场
com.skyworthdigital.skywechatclient 微信互联
com.tianci.ad                      广告
```

**注意**：`disable-user` 对广告包无效——守护者会在开机时把它们 enable 回来。必须先删除守护者 APK。

## 3. 存储清理（已完成）

- 清除无用应用缓存：mipt.store（41MB）、dangbeimarket（37MB）等 → 约 80MB
- 清除崩溃日志 `/data/tombstones/*`、旧日志
- 删除已移除应用的数据目录
- `/data` 使用从 3.0G → 2.9G（23GB 空闲）

**可用内存**：从 ~310MB 提升到 ~357-383MB。

## 4. 意外与修复

- 全民K歌 `com.tencent.karaoketv` 在重启后 APK 消失（/data/app 目录被清），从 `downloads/quanminKtv.apk` 重装恢复 ✓

## 5. 最终状态

- ADB 保持开启：`service.adb.tcp.port=5555`、`ro.adb.secure=0`（未改动，可正常连接）✓
- 系统正常开机 `sys.boot_completed=1` ✓
- 桌面 FLauncher ✓
- 应用：红果TV、FLauncher、全民K歌、观屿TV、千寻直播、投屏(mediarender) 全在 ✓
- root 有效 ✓

## 相关脚本

- `scripts/adblock_hosts.py` —— hosts 广告屏蔽
- `scripts/slim_round2.py` —— 批量禁用
- `scripts/kill_guardian2.py`、`scripts/kill_system_bloat.py` —— 删除守护者/广告 APK
- `scripts/storage_cleanup.py` —— 存储清理
- `scripts/verify_round3.py` —— 验证
