# 应用安装、性能优化与自启管理记录

日期：2026-11-22

## 安装的应用

| 应用 | 包名 | 版本 | 来源 | 状态 |
|---|---|---|---|---|
| 红果TV | `com.hongguotv.nativeapp` | 0.16.13 | N3urda/hongguoTV release | ✅ 正常 |
| FLauncher | `me.efesser.flauncher` | 2025.07.001 | osrosal/flauncher | ✅ 默认桌面（已 patch services.jar 解除 HOME 锁） |
| 全民K歌TV版 | `com.tencent.karaoketv` | 5.9.0.1 免登录 | youhunwl/TVAPP | ✅ 正常 |
| 观屿TV (VoyaTV) | `xyz.nb9.xptv` | 0.5.3 | xptv.nb9.xyz 官方 | ✅ 已 patch（见下） |
| 千寻直播 | `com.tv.qx` | 1.1.5 | youhunwl/TVAPP | ✅ 正常 |

APK 本地位置：`f:/work/jiguang/downloads/`

## 观屿TV 兼容性修复（重要）

官方 APK 在 Android 10 上启动崩溃：
```
java.lang.NoSuchMethodError: No virtual method setTranslucent(Z)Z in class Landroid/app/Activity;
```
`Activity.setTranslucent(boolean)` 是 **Android 12 (API 31)** 才有的方法，设备是 API 29。

修复步骤（脚本在临时目录，已清理，产物保留）：
1. apktool 反编译 `voyatv.apk`
2. 在 `MainActivity.smali` 找到唯一一处 `invoke-virtual {v2, v15}, Landroid/app/Activity;->setTranslucent(Z)Z`（返回值未被使用），替换为 `nop`
3. **只重新 smali 出 classes.dex**（apktool 的 aapt2 重编译资源会失败，不要全量 rebuild）
4. 用 Python zipfile 把新 dex 替换进原 APK：**必须保留每个条目的原始 `compress_type`**（so 库是 STORED/未压缩）
5. 用 `zipalign -f -p 4` 重新对齐（关键！否则 `INSTALL_FAILED_INVALID_APK: Failed to extract native libraries, res=-2`）
6. 用 apksigner 签名（keystore: `f:/work/jiguang/voyatv.keystore`, alias `voyatv`, 密码 `voyatv123456`）

产物：`f:/work/jiguang/voyatv-aligned.apk`（已安装到设备）

NoLauncher 版同样有此问题，也需 patch。

## 性能优化（已应用，重启后仍有效）

| 项目 | 值 | 说明 |
|---|---|---|
| `window_animation_scale` | 0.5 | 窗口动画加速 |
| `transition_animation_scale` | 0.5 | 切换动画加速 |
| `animator_duration_scale` | 0.5 | 属性动画加速 |
| `background_process_limit` | 12 | 限制后台进程数（省内存） |
| `vm.swappiness` | 60 | zram 交换倾向（zram 753MB 已启用） |

注意：`settings put` 必须用 root（`su 0`）执行，普通 shell 写不进 global 表。

## 自启管理（已应用）

禁用了：
- `com.mipt.store`（应用市场自启推送）

保留（必要）：
- `com.android.documentsui`、`com.android.providers.contacts/tv`（系统 provider）
- `com.skyworthdigital.mediarender`（投屏，需要）
- `com.android.provision`（开机完成必需，不能删）

## 投屏功能

**无需恢复** —— 之前为腾空间删的是 `/data/app` 里的副本，但 `/system/app/SkyMediaRender-origin/SkyMediaRender-origin.apk` 一直在（super 恢复时回来了）。实测 `com.skyworthdigital.mediarender` 正常运行，乐播投屏 `com.hpplay.happyplay.aw.new` 也在。

## 蓝牙：已知限制（未能启用）

硬件和底层都在：
- `rfkill0` = `sunxi-bt`，`/dev/ttyS1`，BT MAC `<BT_MAC>` 已烧录
- HAL `android.hardware.bluetooth@1.0-service` 运行
- `vendor.bluetooth-1-0` 服务运行
- `persist.vendor.overlay.bluetooth_support=1`、`vendor=realtek`（已设，重启保持）
- 通过 `sky_check.sh` 注入了开机 `echo 1 > /sys/class/rfkill/rfkill0/state`（rfkill 开机为 1）

**但无法真正启用**，根因：
```
W PackageManager: Failed to scan /system/app/Bluetooth: The system does not allow the application to be installed
```
`/system/app/Bluetooth/Bluetooth.apk` 存在，但用了 `android:sharedUserId="android.uid.bluetooth"`，签名与本机平台签名不匹配，PMS 开机扫描时拒绝注册 → `com.android.bluetooth` 不存在 → `BluetoothManagerService: Fail to bind to: Intent { act=android.bluetooth.IBluetooth }` → 无 hci0。

尝试过去掉 sharedUserId 重装，但 apktool 的 aapt2 重编译资源失败（framework 不兼容），无法生成有效 APK。

**结论**：这是厂商出厂裁剪/签名问题，蓝牙在这台盒子上实际不可用，除非后续找到签名匹配的 Bluetooth.apk 或解决 aapt2 重编译问题。

副作用（无害）：`sky_check.sh` 里多了开机解锁 rfkill 的一行；属性 `bluetooth_support=1`/`vendor=realtek` 已设。

## 相关脚本位置

- `scripts/enable_bluetooth.py`、`temp/bt_via_skycheck.py`（蓝牙尝试）
- `scripts/perf_tune.py`（性能优化）
- `scripts/autostart_manage.py`（自启管理）
- `scripts/install_apps.py`（三应用安装）
- `docs/HONGGUOTV_RECORD.md`（红果TV）
