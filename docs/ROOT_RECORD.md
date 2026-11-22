# TencentBox Q601B Root 记录

## 设备信息

| 项目 | 值 |
|---|---|
| 品牌/型号 | TencentBox Q601B (product `cupid_p2`, device `cupid-p2`) |
| 制造商 | SkyworthDigitalRT |
| 芯片 | Allwinner sun50iw9p1 (ARMv8, 32-bit userspace) |
| 系统 | Android 10, userdebug / release-keys |
| 内核 | Linux 4.9.170 (Android@Skyworth, 2023-07-17) |
| 安全补丁 | 2019-12-05 |
| SELinux | Permissive (`ro.boot.selinux=permissive`) |
| ADB | `service.adb.tcp.port=5555`, `ro.adb.secure=0`（无需授权） |
| 串口号 | `<SERIAL>` |
| MAC | `<MAC_WIFI>`（WiFi）, `<MAC_ETH>`（以太网） |
| IP | 初始 `<BOX_IP_WIFI>`（WiFi）；接网线后变为 `<BOX_IP_ETHERNET>`（以太网，速度约 7MB/s） |

## Root 方法

设备出厂系统里自带一个伪装的 setuid-root `su`：`/system/xbin/usrchan`

```
-rwsr-x--- 1 root shell 15676 /system/xbin/usrchan
```

它的实际行为就是 `su`（`usage: su [WHO [COMMAND...]]`），shell 组可执行。提权命令：

```
adb -s <BOX_IP_WIFI>:5555 shell '/system/xbin/usrchan 0 sh -c "id"'
# uid=0(root) gid=0(root) ... context=u:r:su:s0
```

已建立符号链接以便使用标准命令：

```
/system/xbin/su -> /system/xbin/usrchan
```

`/` 可通过 `mount -o rw,remount /` 改为可写（dynamic partitions / dm-2）。

**重启后已验证 root 依然有效，为永久 root。**

## 使用方式

便捷脚本：`f:/work/jiguang/scripts/rootadb.py`

```powershell
python f:/work/jiguang/scripts/rootadb.py "id"
python f:/work/jiguang/scripts/rootadb.py                    # 交互式 root shell
```

直接 adb：

```powershell
adb connect <BOX_IP_WIFI>:5555
adb -s <BOX_IP_WIFI>:5555 shell '/system/xbin/su 0 sh -c "命令"'
```

## 关键分区表

| 分区 | 块设备 |
|---|---|
| bootloader | mmcblk0p1 |
| env | mmcblk0p2 |
| boot | mmcblk0p3 |
| super (system/vendor/product/odm 动态分区) | mmcblk0p4 |
| misc | mmcblk0p5 |
| recovery | mmcblk0p6 |
| cache | mmcblk0p7 |
| vbmeta | mmcblk0p8 |
| vbmeta_system | mmcblk0p9 |
| vbmeta_vendor | mmcblk0p10 |
| metadata | mmcblk0p11 |
| private | mmcblk0p12 |
| frp | mmcblk0p13 |
| UDISK (/data) | mmcblk0p17 |

## 探测过程

- 开放端口：5555（ADB）、11111（Java-WebSocket，乐播投屏）、9958（UPnP）、49152（DLNA）等
- UPnP friendlyName：`客厅盒子F3`
- `find / -perm -4000` 发现 `/system/xbin/usrchan` 为唯一 setuid-root 二进制
