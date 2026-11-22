# TencentBox Q601B 系统应用精简清单

扫描日期：2026-11-22。共 85 个包（系统 73 + 第三方 12）。

## 执行结果（2026-11-22 14:06）

已彻底删除 13 个包（重命名 APK 后重启，包管理器自动清除）。**重启后验证全部消失，无残留进程，桌面和核心系统正常，可用内存从 ~236MB 提升到 ~294MB。**

已删除清单：

```
com.tianci.ad                                  广告
com.skyworthdigital.ott.advert.app             广告
com.skyworthdigital.ottstatsv2                 统计
com.skyworthdigital.logcollector               日志上传
com.skyworthdigital.upgrade                    OTA 升级
com.skyworthdigital.skyappupdate               应用升级
com.ktcp.autoupgrade                           KTCP 升级
com.skyworthdigital.autotest                   工厂测试
com.softwinner.agingdragonbox                  老化测试
com.softwinner.dragonbox                       龙盒测试
com.skyworthdigital.skycommonpropertymanager   守护者（会自动 re-enable 其他包）
com.xiaopaitech.paivideo                       派视频（含守护代码）
com.skyworthdigital.mediarender                媒体渲染（DLNA）
com.dangbei.lerad.videoposter                  当贝广告海报（之前 disable 已生效）
```

**为什么用删除而非禁用**：`pm disable-user` 对 5 个包无效——开机时 `skycommonpropertymanager`（及 `paivideo`）会调用 `setApplicationEnabledSetting` 把它们重新启用。删除 APK 文件后守护者无从恢复。

**恢复方法**：全盘备份在 `backup/full_emmc.img.gz`，可按 `RESTORE_GUIDE.md` 整盘恢复，或从 `super`/`data` 分区提取对应 APK 重新 push。脚本 `scripts/restore_bloatware.py --list` 可查看清单。

---

## 精简原则

1. **优先用 `pm disable-user`（禁用）而不是删除**，随时可恢复：`pm enable <pkg>`。
2. 只有确认无依赖才删除 APK 文件；删前已做全盘备份（`backup/full_emmc.img.gz`）。
3. 分三批操作，每批后重启验证，避免一次禁用太多导致无法开机或桌面起不来。

## 第一批：可以放心禁用（广告/统计/升级/测试，强烈建议）

这些是厂商和广告 SDK，禁用后不影响系统基本功能，反而提升流畅度和隐私：

```powershell
# 广告
adb shell pm disable-user com.tianci.ad
adb shell pm disable-user com.skyworthdigital.ott.advert.app
adb shell pm disable-user com.dangbei.lerad.videoposter

# 统计/日志上传
adb shell pm disable-user com.skyworthdigital.ottstatsv2
adb shell pm disable-user com.skyworthdigital.logcollector

# 自动升级（禁用后可避免被 OTA 覆盖 root/配置）
adb shell pm disable-user com.skyworthdigital.upgrade
adb shell pm disable-user com.skyworthdigital.skyappupdate
adb shell pm disable-user com.ktcp.autoupgrade

# 工厂测试/老化（普通用户完全无用）
adb shell pm disable-user com.skyworthdigital.autotest
adb shell pm disable-user com.softwinner.agingdragonbox
adb shell pm disable-user com.softwinner.dragonbox
```

预计释放后台内存 100MB+，减少大量开机自启服务。

## 第二批：大概率可禁用（厂商定制，按你的使用情况选）

```powershell
# 如果你不用 PPPOE 拨号
adb shell pm disable-user com.skyworthdigital.PPPoE

# 如果你不用微信互联/手机投屏
adb shell pm disable-user com.skyworthdigital.skywechatclient

# 如果你不用创维自带的应用市场/媒体中心
adb shell pm disable-user com.skyworthdigital.skymediacenter
adb shell pm disable-user com.mipt.store
adb shell pm disable-user com.dangbeimarket

# 如果你不用搜狗电视输入法（避开广告弹窗）
adb shell pm disable-user com.sohu.inputmethod.sogou.tv

# 运营商登录服务（如果你不用运营商 IPTV 账号）
adb shell pm disable-user tv.newtv.loginservice

# 乐视测速（无用）
adb shell pm disable-user cn.lezhi.speedtest_tv
```

**注意**：`com.skyworthdigital.settings`（创维设置）和 `com.android.tv.settings`（原生 TV 设置）建议**至少留一个**。你之前是通过系统设置打开开发者选项的，如果删了创维设置可能失去那个入口。

## 第三批：可精简但需谨慎（第三方预装 App）

这些在 `/data/app`，可直接卸载（等价于 `pm uninstall`）：

```powershell
# 不用的视频/直播 App
adb uninstall com.fengyun.live
adb uninstall com.xiaopaitech.paivideo
adb uninstall com.xiaodianshi.tv.yst
adb uninstall com.hpplay.happyplay.aw.new

# 如果你用 TVBox 或当贝桌面，另一个可卸
adb uninstall com.github.tvbox.osc
adb uninstall com.github.tvbox.osc.tk
adb uninstall com.dangbei.tvlauncher
```

**保留建议**：`com.github.tvbox.osc`（TVBox，你装的）和 `com.hezi.remoteinstaller`（远程安装，方便后续装软件）。

## 不要动（核心系统，删了会出问题）

以下为 Android 框架和电视核心服务，**严禁禁用/删除**：

```
android (framework-res)
com.android.systemui
com.android.tv.settings
com.android.providers.settings / tv / downloads / contacts
com.android.permissioncontroller
com.android.packageinstaller
com.android.networkstack (+ permissionconfig)
com.android.shell
com.android.webview
com.android.bluetoothmidiservice
com.skyworthdigital.providers      (SkyMediaProvider，媒体数据库)
com.skyworthdigital.settings        (创维设置，开发者选项入口)
com.ktcp.launcher                   (如果你还在用当前桌面)
com.xiaopaitech.plauncher           (homepage，另一个桌面)
com.allwinnertech.packageoverride
```

## 推荐的最终精简流程

1. **先备份**（已完成：`backup/full_emmc.img.gz`）。
2. 执行第一批，重启，确认桌面正常、WiFi 正常。
3. 执行第二批中你确认不需要的，重启验证。
4. 第三批按需卸载。
5. 全部完成后可再执行一次 `pm list packages -d` 确认禁用状态。

## 快速一键脚本（第一批）

我把第一批命令写成脚本 `scripts/slim_apps.py`，运行后自动禁用并列出结果，可随时用 `scripts/restore_apps.py` 恢复。
