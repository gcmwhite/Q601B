# 创维 Q601B HOME 锁死机制逆向分析

分析日期：2026-11-22。基于 `services.jar` 反编译（apktool）+ 设备实测。

## 锁死的实现链路

### 1. 入口：`PackageManagerService.filterHomeApp(List, Intent)`

只在 intent 为 `android.intent.action.MAIN` + `android.intent.category.HOME` 时触发。流程：

```
homeAppBlackListEnable = SkyworthConfig.isBlackListEnable("com.forestdata.type")
for each ResolveInfo:
    if homeAppBlackListEnable:   # 黑名单模式
        if !isInNameBlackList("com.skyworthdigital.homeblacklist", pkg):
            allow
        else:
            block
    else:                        # 白名单模式（本机实际走的）
        if isInNameList("enable_launcher_components", pkg) OR
           isInNameList("com.skyworthdigital.homewhitelist", pkg):
            allow
        else:
            block   # 日志: PackageManager: block home apk: ResolveInfo{...}
```

### 2. 校验：`SkyworthConfig.checkList(key, value)`

所有配置值都是签名保护的：

```java
readAuthKey = getString(key)                      // settings 里存的哈希
mListValue  = Base64.encode(value, NO_WRAP)
legal       = CryptUtils.requestIsLegal(readAuthKey, mListValue)
```

`CryptUtils.requestIsLegal(key, value)`：

```java
stbId     = SystemProperties.get("persist.sys.hwconfig.stb_id")  // 本机 = <STB_ID>
serverKey = HMAC-SHA1(key=stbId, data=value)      // 即 HMAC(stb_id, Base64(明文))
return serverKey.equals(key)
```

**签名算法完全公开，可在 PC 上自行计算。**

### 3. 关键配置（实测值）

| settings key | 表 | 值 |
|---|---|---|
| `com.forestdata.type` | secure | `9085b3a1733541dba7ac156837d7a6dadddd2738`（= 加密的 "true"，黑名单开关） |
| `com.forestdata.key` | secure | `7e06c914...`（homewhitelist 的签名） |
| `com.skyworthdigital.homewhitelist` | system | `com.xiaopaitech.supportsdk,com.xiaopaitech.wallpaperlauncher`（逗号分隔） |
| `enable_launcher_components` | global/system/secure | `com.skyworthdigital.sky2dlauncher/com.ktcp.launcher/com.android.provision/com.xiaopaitech.plauncher`（斜杠分隔） |

`initAuthMap()` 里硬编码了 authkey↔白名单映射：
- `com.forestdata.key` → `com.skyworthdigital.homewhitelist`
- `com.forestdata.box` → `com.skyworthdigital.backgroundwhitelist`
- `com.forestdata.setup` → `com.skyworthdigital.startupwhitelist`

### 4. 为什么改 settings 白名单无效（实测）

1. 把 FLauncher 加进 `enable_launcher_components` → 仍 `block home apk`
2. 伪造 HMAC 签名写入 `com.forestdata.key` → 仍 block，原因：
   - 原始 `enable_launcher_components` 算出的 HMAC 与存储值不符（说明该值不是 `com.forestdata.key` 校验的明文，或取自多用户隔离的另一份 settings）
   - **root/shell 看到的 settings 值与 system_server(uid 1000) 看到的不同**——实测 root 写入的 marker，shell 读为空；`SkyworthConfig` 运行在 system_server，读的是它自己的那份
3. 守护进程会从云端 `read server list` 刷新配置，覆盖手工修改（这是之前 disable 被复活的原因）

## 可行方案评估

### 方案 A：patch `services.jar` 的 `filterHomeApp`（根本解决，可行）

把方法开头改成直接 `return-void`，彻底移除 HOME 过滤。

- 可行性：**高**。算法层面简单，一条指令。
- 之前的失败原因（重要）：
  1. 第一次 patch 把 `return-void` 放在 `.param`/`.annotation` 前，apktool 重打包时丢弃 → 无效
  2. 第二次 patch 位置对了，但**同时删除了 provision + 所有桌面** → `sys.boot_completed=0`，系统卡开机（不是 patch 本身导致）
  3. 恢复 jar 后未清 `services.odex`，ART 缓存不一致
- 正确做法：
  1. 只 patch jar，**绝不动 provision/桌面**
  2. `return-void` 放在 `.local p1` 之后、第一条真实指令之前
  3. 替换后删除 `/system/framework/oat/arm/services.odex|.vdex|.art` 让系统重建
  4. 重启验证 `sys.boot_completed=1`
- 风险：中。有全盘备份 + `scripts/restore_super.py` 可回滚（30 秒写回）。
- 效果：FLauncher 成为真正的 HOME，HOME 键直接回 FLauncher，可移除 watchdog。

### 方案 B：伪装包名（用户提到的"改包名"）

把 FLauncher 改包名为白名单内的包名（如 `com.xiaopaitech.wallpaperlauncher`）。

- 可行性：**低**。需要重签名、改所有引用；且 `homewhitelist` 校验可能涉及签名；白名单项还是云端下发的，随时可能变。
- 不灵活，不推荐。

### 方案 C：patch `Provision.apk`

让 `DefaultActivity` 直接 finish 并启动 HOME，不再抢占。

- 可行性：中。但 provision 是 boot_completed 的必要环节，改坏了会卡开机。
- 且绕过了 `filterHomeApp`——FLauncher 仍被 block，只是不再有 provision 抢占，需要配合方案 A。

### 方案 D：当前 watchdog（已生效）

在 `sky_check.sh` 注入守护，检测前台是 provision/旧桌面就切回 FLauncher。

- 可行性：**已验证有效**。
- 缺点：按 HOME 键有 1~5 秒闪烁（跳到 provision 再被切回）；不是"根治"。

## 结论与建议

**能改。** 真正干净的方案是 **A：patch services.jar**，且已定位到之前失败的原因（删除 provision 才是卡开机的元凶，不是 patch 本身）。建议保留全盘备份和 `restore_super.py` 作为后悔药，然后单独做 A，成功后即可去掉 watchdog。

当前 watchdog 方案作为保底已经稳定运行，不影响日常使用。
