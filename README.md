# TencentBox Q601B 折腾记录

针对一台腾讯/创维 Q601B 电视盒子（Allwinner H616 / Android 10 / 1GB RAM / 32GB eMMC）的完整折腾记录：获取 root、全盘备份、恢复方案、系统精简、桌面更换、应用安装等。

## 设备信息

| 项目 | 值 |
|---|---|
| 型号 | TencentBox **Q601B**（另有 Q6033 / 京东 H4S01 等别名；device `cupid-p2`） |
| 芯片 | Allwinner **H616**（`sun50iw9p1`），4× Cortex-A53 |
| 系统 | Android 10（SDK 29），userdebug / release-keys |
| 内存/存储 | 1GB RAM / 32GB eMMC |
| IP | 因隐私原因不再公开，脚本通过环境变量 `BOX_IP` 提供 |
| ADB | 网络 ADB 端口 5555，`ro.adb.secure=0`（免密，用户要求保持开启） |

> **隐私说明**：所有设备标识（IP、MAC、序列号、stb_id）均已用 `<...>` 占位符替换。
> 运行脚本前请设置环境变量：`$env:BOX_IP = "你的盒子IP"`，或直接在脚本里把占位符换成实际值。

## 已实现的功能

- **Root 权限**：利用系统自带的 setuid-root 后门 `/system/xbin/usrchan`（伪装成普通工具的 `su`），已建立 `/system/xbin/su` 软链。重启持久有效。
- **HOME 桌面锁根治**：patch `services.jar` 的 `filterHomeApp()`，移除创维的桌面白名单过滤和 `com.android.bluetooth` 硬编码黑名单。
- **桌面**：Projectivy Launcher 4.72（支持应用分类/隐藏/排序），已设为默认。
- **全盘备份**：14.7GB 压缩镜像（见下方"大文件"说明）。
- **网络广告屏蔽**：`/system/etc/hosts` 拦截 59 个广告/统计域名。
- **应用**：红果TV、观屿TV（已 patch Android 12 API 兼容）、千寻直播、投屏等。
- **性能优化**：动画 0.5x、后台进程上限 12、zram、自启管理、存储清理。

## 目录结构

```
.
├── README.md             本文件
├── docs/                 完整记录文档（12 篇）
├── scripts/              所有脚本（root/备份/精简/安装/验证等）
├── downloads/            下载的 APK 与校验文件
├── backup/               备份元数据与工具
│   ├── MANIFEST.txt      全盘镜像清单与 SHA-256
│   ├── *.txt             设备属性/分区表/包列表
│   └── tools/            apktool、patch 后的 jar、第三方 APK 等
└── temp/                 临时目录（空，不纳入版本控制）
```

## 文档索引

| 文档 | 内容 |
|---|---|
| `docs/ROOT_RECORD.md` | Root 获取方法与设备信息 |
| `docs/BACKUP_RECORD.md` | 全盘备份信息 |
| `docs/RESTORE_GUIDE.md` | 从备份恢复系统/分区的完整指南 |
| `docs/HOME_LOCK_ANALYSIS.md` | 创维 HOME 桌面锁的逆向分析 |
| `docs/HOME_ROOT_PATCH_RECORD.md` | 根治 HOME 锁的 services.jar patch |
| `docs/BLUETOOTH_DEEP_ANALYSIS.md` | 蓝牙逐层分析与启用尝试（最终为硬件层限制） |
| `docs/FLAUNCHER_RECORD.md` | FLauncher 安装与 watchdog 方案（历史） |
| `docs/DESKTOP_PROJECTIVY_RECORD.md` | Projectivy 桌面安装与设置 |
| `docs/HONGGUOTV_RECORD.md` | 红果TV 安装 |
| `docs/SESSION_APPS_PERF_RECORD.md` | 观屿TV patch、性能优化、自启管理 |
| `docs/APPS_SLIM_GUIDE.md` | 应用精简清单 |
| `docs/CLEANUP_ROUND3_RECORD.md` | 广告屏蔽/应用精简/存储清理 |

## 大文件说明

以下大文件**未纳入 Git 仓库**（GitHub 单文件 100MiB 限制 / LFS 免费额度 10GiB 限制）：

| 文件 | 大小 | 说明 |
|---|---|---|
| `backup/full_emmc.img.gz` | 14.7 GB | 完整 eMMC 镜像（gzip），含 17 个分区，SHA-256 见 `backup/MANIFEST.txt` |
| `backup/tools/super_restore.img` | 1.5 GB | super 分区镜像（用于救砖） |

这些文件保留在本地 `f:/work/jiguang/backup/` 下。如需分享，可切分成 <2GiB 分卷作为 GitHub Release 附件（免费、不计仓库大小），或使用外部网盘。

## 常用操作

通过 ADB 连接设备（保持开启）：

```powershell
adb connect <BOX_IP_ETHERNET>:5555
python scripts/rootadb.py "id"                      # root 命令
python scripts/rootadb.py                            # root shell
```

验证系统状态：

```powershell
python scripts/verify_projectivy.py                  # 桌面/应用/系统状态
python scripts/verify_backup.py                      # 校验备份镜像
```

备份与恢复：

```powershell
python scripts/full_backup.py                        # 全盘备份
python scripts/restore_super.py                      # 恢复 super 分区（救砖）
python scripts/extract_partition.py --list           # 列出可提取分区
```

## 注意事项

- 修改 `/system` / `/vendor` 前先 `mount -o rw,remount /`；这些是动态分区，恢复 super 会还原所有系统级修改。
- 删除 provision（`com.android.provision`）会导致 `sys.boot_completed=0` 卡开机——**不要删除它**。
- `pm disable-user` 对部分创维应用无效（有守护进程会重新 enable）——需删除 APK 文件。
- 所有 `settings put` 需用 root 执行；普通 shell 写不进 global 表。
- 无障碍服务（Projectivy 所需）会被重启重置，已在 `/system/bin/sky_check.sh` 中注入持久化。
