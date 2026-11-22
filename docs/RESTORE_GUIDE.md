# TencentBox Q601B 系统恢复清单

## 备份文件

| 项目 | 值 |
|---|---|
| 镜像 | `f:/work/jiguang/backup/full_emmc.img.gz` |
| 格式 | 整块 eMMC 原始镜像（含 GPT + 全部 17 个分区），gzip 压缩 |
| 压缩后 | 14,688,918,802 字节（14.69 GB） |
| 解压后 | 31,268,536,320 字节（29.1 GiB，与 `/dev/block/mmcblk0` 一致） |
| SHA-256 | `5287ba5febfca3d204ba0c9311973e06c7304cde20839d153ee86c45f981c0c4` |

恢复前务必校验：

```powershell
python f:/work/jiguang/scripts/verify_backup.py
```

## 分区表（GPT，LBA=512B）

| 分区 | 起始 LBA | 结束 LBA | 大小 | 说明 |
|---|---|---|---|---|
| bootloader | 73728 | 139263 | 32MB | Bootloader |
| env | 139264 | 172031 | 16MB | 环境变量 |
| boot | 172032 | 237567 | 32MB | 内核 + ramdisk |
| super | 237568 | 3383295 | 1.5GB | 动态分区（system/vendor/product/odm） |
| misc | 3383296 | 3416063 | 16MB | 恢复/引导控制 |
| recovery | 3416064 | 3547135 | 64MB | Recovery |
| cache | 3547136 | 5119999 | 768MB | 缓存 |
| vbmeta | 5120000 | 5152767 | 16MB | AVB 校验 |
| vbmeta_system | 5152768 | 5185535 | 16MB | AVB |
| vbmeta_vendor | 5185536 | 5218303 | 16MB | AVB |
| metadata | 5218304 | 5251071 | 16MB | 元数据 |
| private | 5251072 | 5283839 | 16MB | 私钥 |
| frp | 5283840 | 5284863 | 256KB | 工厂重置保护 |
| empty | 5284864 | 5316607 | 15.5MB | 空 |
| media_data | 5316608 | 5349375 | 16MB | 媒体数据 |
| Reserve0 | 5349376 | 5382143 | 16MB | 保留 |
| UDISK | 5382144 | 61071326 | 26.6GB | `/data` 用户数据 |

## 恢复前置条件

1. 盒子能进系统且 root 有效（`/system/xbin/su`），或能进 Fastboot / Recovery。
2. PC 上有 `adb`、`python`，镜像通过校验。
3. 恢复会覆盖数据，**先确认备份可解压**。

## 场景一：整机恢复（整盘 dd 写回）

风险最高，仅在变砖/系统彻底损坏时使用。注意：目标 eMMC 必须与备份同源（32GB）。

**方法 A：在已 root 的系统里写回（需能开机）**

```powershell
# 1. 把镜像推到设备（/data 需有 15GB 空间）
adb -s <BOX_IP_ETHERNET>:5555 push f:/work/jiguang/backup/full_emmc.img.gz /data/local/tmp/full_emmc.img.gz

# 2. 解压并写回整块 eMMC（危险！确认目标为 /dev/block/mmcblk0）
adb -s <BOX_IP_ETHERNET>:5555 shell '/system/xbin/su 0 sh -c "gzip -dc /data/local/tmp/full_emmc.img.gz > /dev/block/mmcblk0"'

# 3. 重启
adb -s <BOX_IP_ETHERNET>:5555 shell '/system/xbin/su 0 reboot'
```

**方法 B：通过 Fastboot 刷关键分区（推荐用于救砖）**

```powershell
# 进入 fastboot：关机状态下按住音量+插电，或 root 下执行：
adb -s <BOX_IP_ETHERNET>:5555 shell '/system/xbin/su 0 reboot bootloader'

# 从镜像提取分区后在 fastboot 下刷写（见场景二提取方法）
fastboot flash boot boot.img
fastboot flash recovery recovery.img
fastboot flash vbmeta vbmeta.img
fastboot reboot
```

## 场景二：单分区恢复（常用，安全）

先在本地从完整镜像提取需要的分区（以 boot 为例）：

```powershell
python f:/work/jiguang/scripts/extract_partition.py boot
# 生成 f:/work/jiguang/backup/extracted/boot.img
```

可用分区名见上表：`bootloader`、`env`、`boot`、`super`、`recovery`、`cache`、`vbmeta`、`vbmeta_system`、`vbmeta_vendor`、`metadata`、`private`、`frp`、`media_data`、`Reserve0`、`UDISK`。

然后写回设备（以 boot 为例）：

```powershell
adb -s <BOX_IP_ETHERNET>:5555 push f:/work/jiguang/backup/extracted/boot.img /data/local/tmp/boot.img
adb -s <BOX_IP_ETHERNET>:5555 shell '/system/xbin/su 0 sh -c "dd if=/data/local/tmp/boot.img of=/dev/block/by-name/boot bs=1M && sync"'
adb -s <BOX_IP_ETHERNET>:5555 shell '/system/xbin/su 0 reboot'
```

写回 `super`（system/vendor/product）时需特别注意：动态分区，建议整块 super 写回：

```powershell
python f:/work/jiguang/scripts/extract_partition.py super
adb -s <BOX_IP_ETHERNET>:5555 push f:/work/jiguang/backup/extracted/super.img /data/local/tmp/super.img
adb -s <BOX_IP_ETHERNET>:5555 shell '/system/xbin/su 0 sh -c "dd if=/data/local/tmp/super.img of=/dev/block/by-name/super bs=1M && sync"'
```

## 场景三：仅恢复应用数据（/data）

如果只是想恢复用户数据而不动系统：

```powershell
python f:/work/jiguang/scripts/extract_partition.py UDISK
# 得到 UDISK.img（26.6GB ext4 镜像）
# 可挂载查看：
#   WSL: sudo mount -o loop,offset=$((5382144*512)) UDISK.img /mnt/data
```

写回：

```powershell
adb -s <BOX_IP_ETHERNET>:5555 push .../UDISK.img /data/local/tmp/UDISK.img   # 需足够空间
adb -s <BOX_IP_ETHERNET>:5555 shell '/system/xbin/su 0 sh -c "dd if=/data/local/tmp/UDISK.img of=/dev/block/by-name/UDISK bs=1M && sync"'
```

更安全的做法是**不要覆盖正在运行的 /data**，而是进入 Recovery 后操作，或只 pull 出需要的文件夹。

## 注意事项

1. **root 后门是系统自带的**：`/system/xbin/usrchan` 是 setuid-root 的 `su`，恢复系统分区后它仍在（因为它在原始镜像里），root 不会丢。若被删除，可从镜像提取 `super` 恢复，或重新建立符号链接：
   ```
   /system/xbin/su -> /system/xbin/usrchan
   ```
2. **AVB 校验**：`vbmeta` 等分区已备份，若修改分区导致校验失败，可写回原 `vbmeta`。
3. **写回后权限**：`dd` 写回后分区权限保持，无需 chmod。
4. **网络 ADB 恢复**：恢复后 `service.adb.tcp.port=5555` 仍在 `build.prop`/`default.prop` 中，IP 以实际网络为准（WiFi `<BOX_IP_WIFI>`，以太网 `<BOX_IP_ETHERNET>`）。
5. **空间不足时的整盘恢复**：设备 `/data` 只有 26GB，装不下 14.7GB 镜像 + 解压缓冲时，改用 Fastboot 或 Recovery 下的 USB 写回。
