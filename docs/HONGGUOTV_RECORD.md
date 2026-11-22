# 红果TV 安装记录

安装日期：2026-11-22

## 结果

红果TV 0.16.13 已成功安装并正常运行。

| 项目 | 值 |
|---|---|
| 包名 | `com.hongguotv.nativeapp` |
| 版本 | 0.16.13 (versionCode=34) |
| minSdk / targetSdk | 23 / 36（设备 SDK 29，兼容） |
| 来源 | `https://github.com/N3urda/hongguoTV/releases/tag/kotlin-v0.16.13` |
| 选用 APK | `hongguotv-kotlin-0.16.13-android6-arm32-v7a.apk`（设备是 armeabi-v7a 32位） |
| 本地文件 | `f:/work/jiguang/downloads/hongguotv-kotlin-0.16.13-android6-arm32-v7a.apk` |
| SHA256 | `9d95782a2a34f913c887f68413472f0aabe85d0c86c49e18d19a3ce0ca42f544`（与官方 SHA256SUMS 一致） |
| Launcher Activity | `.MainActivity` |

## 安装步骤

```powershell
adb -s <BOX_IP_ETHERNET>:5555 push downloads/hongguotv-kotlin-0.16.13-android6-arm32-v7a.apk /data/local/tmp/hongguo.apk
adb -s <BOX_IP_ETHERNET>:5555 shell '/system/xbin/su 0 pm install -r -g /data/local/tmp/hongguo.apk'
```

## 验证

- 安装 Success，包路径 `/data/app/com.hongguotv.nativeapp-.../base.apk`
- 启动后 `ResumedActivity: com.hongguotv.nativeapp/.MainActivity`，进程稳定，~29MB 内存
- 无崩溃日志

## 备注

- release 提供 4 个 APK：android5 / android6 / android6-arm32-v7a / android6-arm64-v8a。后三者 SHA256 相同（同一包不同命名）。设备是 32 位，选 arm32-v7a 版。
- 这台盒子内存 1GB，targetSdk 36 略高但运行正常。
- 之前 M18C（API19）需要源码移植红果TV，这台 Q601B（Android 10）可直接装官方包，无需移植。
