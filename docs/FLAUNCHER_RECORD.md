# FLauncher 桌面安装记录

安装日期：2026-11-22

## 结果

FLauncher 已成功安装并设为实际桌面，开机自动进入，HOME 键被 watchdog 守护切回。

| 项目 | 值 |
|---|---|
| 包名 | `me.efesser.flauncher` |
| 版本 | 2025.07.001 (osrosal fork) |
| ABI | armeabi-v7a（设备是 32 位） |
| APK 本地 | `f:/work/jiguang/flauncher-armeabi-v7a-release.apk`、`flauncher-universal.apk` |
| 下载地址 | `https://github.com/osrosal/flauncher/releases/download/v2025.07.001/flauncher-armeabi-v7a-release.apk` |
| Activity | `me.efesser.flauncher/.MainActivity` |

## 创维系统的桌面锁（关键难点）

这台创维/腾讯盒子的桌面被多重机制锁定，普通 `pm set-home-activity` 无效：

1. **HOME 黑名单机制**：`PackageManagerService.filterHomeApp()` 会 block 非白名单的 HOME 应用（日志 `PackageManager: block home apk:`）。配置在 `SkyworthConfig`，key 为 `com.forestdata.*`（存在 secure settings，值是 SHA 校验），守护进程会从云端 `read server list` 刷新。
2. **开机向导 provision**：`com.android.provision/.DefaultActivity` 是 `isDefault=true` 的 HOME，开机抢占前台。它是开机完成的必要环节——删除它会导致 `sys.boot_completed` 永远为 0，系统卡在开机（无桌面、resolve 全空）。disable 会被守护复活。
3. **KTCP launcher 隐私协议页**：开机也会抢占前台。

## 踩坑记录（重要教训）

- 曾尝试 patch `services.jar` 的 `filterHomeApp` 加 `return-void`，**失败且危险**：
  - apktool 重打包时，若 `return-void` 放在 `.param`/`.annotation` 前会被丢弃
  - 更严重的是：同时删除 provision + 所有桌面 + patch jar 导致系统 `sys.boot_completed=0`，整个 resolve 机制失效（连 Settings 都启动不了）
  - **恢复方法**：从全盘备份写回 `super` 分区（`scripts/restore_super.py`，1.5GB，约 30 秒写回），系统完全恢复，root 保留（usrchan setuid su 在 system 里）
- **结论**：不要删除 provision，不要 patch framework jar。用 watchdog 方案最稳妥。

## 最终方案：挂载 sky_check.sh watchdog

系统自带 `/system/bin/sky_check.sh`（`sky_check` 服务，开机自启的健康监控脚本，每 300 秒循环）。把 FLauncher 守护逻辑注入其中：

1. 开机 boot_completed 后 force-stop provision + `am start` FLauncher
2. 循环里检测前台：若是 `provision`/`ktcp.launcher`/`plauncher` 则切回 FLauncher
3. 不干扰用户打开的其他 App

注入脚本：`f:/work/jiguang/sky_check_clean.sh`（LF 行尾，语法已验证）

注意：
- `/system` 分区几乎满（962M 用 959M），注入前删除了几个无用系统 APK 腾出 41MB（测试/升级/统计工具，见 `scripts/free_system_space.py` 逻辑）
- 原 `sky_check.sh` 备份在设备 `/data/local/tmp/sky_check.sh.orig`
- 行尾必须是 LF，CRLF 会导致 shell 语法错误

## 验证结果

- 开机后前台自动是 FLauncher ✅
- 按 HOME 键跳到 provision 后，watchdog 在几秒内切回 FLauncher ✅
- 系统正常开机 `sys.boot_completed=1` ✅
- root 依然有效 ✅

## 相关脚本

- `scripts/restore_super.py` —— 从全盘备份恢复 super 分区（救砖用）
- `scripts/sky_check_clean.sh` —— 注入的 watchdog 脚本
- `scripts/setup_flauncher_daemon.py` / `hook_skycheck2.py` —— 注入过程脚本（temp）
