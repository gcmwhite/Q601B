# HOME 锁死根治记录（services.jar patch）

完成日期：2026-11-22

## 结果：根治成功，watchdog 已移除

通过 patch `services.jar` 的 `filterHomeApp()` 彻底移除创维的 HOME 过滤，不再需要 sky_check watchdog。

| 验证项 | 结果 |
|---|---|
| `sys.boot_completed` | 1（正常开机） |
| HOME resolve | `me.efesser.flauncher/.MainActivity` (isDefault=true) |
| 开机前台 | 直接是 FLauncher |
| HOME 键 | 2 秒内直接回 FLauncher（无 5 秒轮询延迟） |
| `block home apk` 日志 | 无 |
| watchdog | 已移除（`sky_check.sh` 恢复原始，无 FLauncher 字样） |
| root | 有效 |
| 可用内存 | ~298MB |

## Patch 内容

文件：`PackageManagerService.smali` 的 `filterHomeApp(Ljava/util/List;Landroid/content/Intent;)V`

在 `.local p1` 之后、第一条真实指令之前插入 `return-void`，使方法直接返回，不做任何过滤。

**关键：return-void 的位置**
- 必须放在 `.local p1, "lst":...` 之后
- 不能放在 `.param`/`.annotation` 区——apktool 重打包时会丢弃
- 重打包后必须反编译验证 return-void 仍在且位置正确

## 操作步骤（脚本）

1. `scripts/patch_services_clean.py` —— 从原始 `backup/tools/services.jar` 干净解包、插入 return-void、重打包成 `services_root.jar`、反编译验证
2. `scripts/install_root_patch.py` —— remount rw、设备端备份原 jar 到 `/data/local/tmp/services.jar.stock`、push 新 jar、删除 `services.odex/.vdex/.art`
3. 重启（首次启动会重新 dexopt framework）
4. `scripts/remove_watchdog.py` —— 恢复原始 `sky_check.sh`、删除无用的 daemon 文件、重启

## 为什么这次成功（之前的教训）

之前 patch 失败是因为**同时删除了 provision + 所有桌面**，导致 `sys.boot_completed=0` 卡开机——那是删 provision 的锅，不是 patch 的锅。这次：
- 只替换 services.jar，**完全不动 provision 和任何 APK**
- 正确放置 return-void
- 清除 odex 强制重建

## 回滚方法

如果出问题：
```powershell
# 方法1：恢复设备上的原 jar 备份
python f:/work/jiguang/scripts/rootadb.py "mount -o rw,remount /; cp /data/local/tmp/services.jar.stock /system/framework/services.jar; rm -f /system/framework/oat/arm/services.odex /system/framework/oat/arm/services.vdex /system/framework/oat/arm/services.art; reboot"

# 方法2：从全盘备份写回整个 super 分区
python f:/work/jiguang/scripts/restore_super.py
```

## 相关

- 逆向分析详见 `docs/HOME_LOCK_ANALYSIS.md`
- watchdog 方案（已弃用）记录见 `docs/FLAUNCHER_RECORD.md`
- 本地产物：`services_root.jar`（patch 后）、`backup/tools/services.jar`（原始）
