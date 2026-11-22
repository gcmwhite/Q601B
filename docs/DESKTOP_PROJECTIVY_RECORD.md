# 桌面更换为 Projectivy Launcher 记录

日期：2026-11-22

## 结果

FLauncher 换成 **Projectivy Launcher 4.72**，支持自由管理应用显示/隐藏。

| 项目 | 值 |
|---|---|
| 包名 | `com.spocky.projengmenu` |
| 版本 | 4.72 (versionCode=97, minSdk 23, targetSdk 37) |
| 来源 | `https://github.com/spocky/miproja1/releases/download/4.72/ProjectivyLauncher-4.72-c97-xda-release.apk`（2026-10 实测源，来自 `wangrongding/tv-fresh` 清单） |
| SHA256 | `a312935837b7cf32...` |
| 本地 APK | `f:/work/jiguang/downloads/ProjectivyLauncher-4.72.apk` |
| ABI | universal（含 armeabi-v7a，兼容设备） |

## 为什么换

FLauncher 精简但**无法管理显示哪些应用**——这版 fork 的配置里只有背景/动画设置，没有应用隐藏/分类功能。Projectivy 是 Android TV 社区公认功能最强的桌面：
- 自由隐藏/显示应用、自定义分类、图标排序
- 无广告、轻量
- 支持添加 HDMI 输入快捷方式、开机自启应用、家长控制
- 手机远程控制

## 安装与设置步骤

1. 下载 4.72 APK（校验 zip + SHA256）
2. `pm install -r -g`
3. `cmd package set-home-activity com.spocky.projengmenu/.ui.home.MainActivity`
4. `pm disable-user me.efesser.flauncher`（保留包作备用）
5. **启用无障碍服务**（Projectivy 需要它来捕获按键/管理应用）：
   ```
   settings put secure enabled_accessibility_services com.spocky.projengmenu/.services.ProjectivyAccessibilityService
   settings put secure accessibility_enabled 1
   ```
6. **持久化**：无障碍设置重启会被重置，已把上述两条命令注入 `/system/bin/sky_check.sh`（开机自启脚本），重启后验证依然生效 ✅

## 验证

- 默认 HOME：`Projectivy/.ui.home.MainActivity` ✅
- 开机前台：Projectivy 主界面 ✅
- 无障碍服务：重启后 `enabled=1` ✅
- 系统正常 boot=1、root、内存 389MB ✅

## 用户偏好

- 全民K歌是用户自己删的，已从设备彻底卸载（不再重装）
- ADB 保持开启（`service.adb.tcp.port=5555`），用户明确要求不能禁用

## 后续（在 Projectivy 界面上手动做）

Projectivy 的应用管理、分类、隐藏等操作需要在 GUI 上用遥控器完成：
- 进入设置 → 应用 → 选择要显示/隐藏的应用
- 可自定义分类行、调整图标顺序

## 相关文件

- `scripts/verify_projectivy.py` —— 验证脚本
- `f:/work/jiguang/sky_check_projivy.sh` —— 注入无障碍持久化的 sky_check.sh 副本
