# 蓝牙遥控器深度分析与启用尝试

日期：2026-11-22

## 结论

经过逐层剥离，确认这台盒子的蓝牙**理论上可用**，但最终卡在固件下载阶段（芯片无响应）。已实现的部分让 `com.android.bluetooth` 服务能够启动，但 HCI 仍无法初始化。

## 逐层发现与突破

### 第 1 层：PMS 硬编码黑名单（已解决）✅

反编译 `services.jar` 的 `PackageManagerService.smali` 发现（约 71725 行）：
```smali
const-string v14, "com.android.bluetooth"
invoke-static {v13, v14}, TextUtils;->equals(...)
if-nez v13, :cond_35    # 不等则跳过
# 相等则走到拒绝："The system does not allow the application to be installed"
```
厂商在 PMS 里**硬编码禁止 `com.android.bluetooth` 这个包名**。

**解决**：patch services.jar，把该 const-string 改成 `com.android.bluetootX`（长度不变）。重启后 `com.android.bluetooth` 成功注册（`pm list packages` 可见）。

（此 patch 叠加在之前的 filterHomeApp patch 之上，当前 services.jar 含两个 patch。）

### 第 2 层：串口权限（已解决）✅

`/dev/ttyS1` 和 `/sys/class/rfkill/rfkill0/state` 被 rc 脚本错误配置成 root-only，bluetooth 用户无法访问：
```
bt_upio: set_bluetooth_power: open(/sys/class/rfkill/rfkill0/state) failed: Permission denied
```
**解决**：
```
chown bluetooth:net_bt_admin /dev/ttyS1; chmod 660 /dev/ttyS1
chown bluetooth:net_bt_admin /sys/class/rfkill/rfkill0/state; chmod 660 /sys/class/rfkill/rfkill0/state
```

### 第 3 层：缺失的厂商库 libbt-xradio.so（已解决）✅

HAL 日志：
```
Open, get libbt name: libbt-xradio.so.
Open unable to open libbt-xradio.so (dlopen failed: library not found)
```
系统里有 `libbt-realtek.so` / `libbt-sprd.so` / `libbt-mtk.so`，但没有 xradio 库。HAL 根据 `persist.vendor.overlay.module_info=xradio:xr819:0x12281` 推断出 xradio 名字（设 `bluetooth_vendor=realtek` 无效）。

**解决**：软链 `libbt-xradio.so -> libbt-realtek.so`。重启后库成功加载：
```
Open vendor library loaded
bt_hwcfg_uart: Realtek libbt-vendor_uart Version 5.1.1
```

### 第 4 层：芯片类型矛盾（部分确认）

日志里出现两条线索：
- Realtek 库识别到 `rtl8723bs/cs/ds` 的 WiFi 型号
- 但 `/vendor/etc/bt_configure_pskey.ini` 和 `bt_configure_rf.ini` 标注 `[Marlin3]`（紫光展锐芯片）

测试 `libbt-sprd.so`：它试图打开 `/dev/ttyBT0`（不存在），建软链后直接 SIGSEGV 崩溃。

最终采用 Realtek 库（串口路径 `/dev/ttyS1` 正确，能通信）。

### 第 5 层：固件下载失败（未解决）❌

Realtek 库最终停在：
```
bt_hwcfg_uart: hw_config_start, transtype = 0x11    # H5 协议
（3.5 秒后）
bt_hwcfg_uart: hw_config_cback, status = 3          # 失败
FATAL: hci_layer_android.cc(88) Check failed: status == Status::SUCCESS
```
`status=3` = 固件下载超时，芯片在串口上无响应。尝试过：
- H4 协议（改 rtkbt.conf）→ 串口路径解析失败，已还原
- 修复所有权限 → 仍然 status=3

**判断**：芯片可能未真正焊接/未接线，或需要特定的上电时序（`/proc/bluetooth/sleep/lpm` 不存在，wake 控制缺失），或需要特定波特率固件。这一层需要硬件原理图/示波器才能继续，投入产出比很低。

## 当前状态（最终）

| 项目 | 状态 |
|---|---|
| `com.android.bluetooth` 包 | ✅ 已注册（PMS 黑名单已 patch） |
| 蓝牙 HAL 服务 | ✅ running |
| `/dev/ttyS1` 权限 | ✅ bluetooth 用户可访问 |
| `libbt-xradio.so` | ✅ 软链 → libbt-realtek.so |
| `bluetooth_support=1` / `vendor=realtek` | ✅ 已设，重启保持 |
| `sky_check.sh` 开机解锁 rfkill | ✅ 已注入 |
| HCI 设备 | ❌ 无（固件下载 status=3） |
| 蓝牙功能 | ❌ 不可用 |

为避免 crash loop，`bluetooth_on=0`、`com.android.bluetooth` 已 force-stop。系统其余部分正常（boot=1、FLauncher 桌面、root、内存 310MB）。

## 相关 patch 文件

- `services_bt_patch.jar` / `backup/tools/services_root.jar` —— 含 filterHomeApp + 蓝牙黑名单两个 patch
- 设备上 `/data/local/tmp/services_homepatch.jar` —— 只有 filterHomeApp patch 的版本（回滚点）
- 回滚：`cp /data/local/tmp/services.jar.stock /system/framework/services.jar`（原始，两个 patch 都无）

## 创维蓝牙设置 App 打不开的原因（补充）

`com.skyworthdigital.bluetooth.settings`：
- 没有 LAUNCHER category Activity，所以系统应用列表点击无反应
- 主界面 `SkyworthControllerActivity` 用 action `com.skyworthdigital.app.SKYWORTH_CONTROLLER` 可启动
- 但它依赖 `com.android.bluetooth`（已 patch 可用），界面上开启蓝牙会触发上述 HAL 崩溃链
