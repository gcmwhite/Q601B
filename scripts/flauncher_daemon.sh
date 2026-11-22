#!/system/bin/sh
# Keep FLauncher as the active HOME on TencentBox Q601B
# Only intercepts the provision wizard / old launchers, does not disturb user apps.
COMP="me.efesser.flauncher/me.efesser.flauncher.MainActivity"

# Wait for boot complete
while [ "$(getprop sys.boot_completed)" != "1" ]; do
    sleep 2
done
sleep 4

# Initial: clear wizard and show FLauncher
am force-stop com.android.provision
am start -n $COMP >/dev/null 2>&1

while true; do
    top=$(dumpsys activity activities 2>/dev/null | grep -m1 'mResumedActivity')
    case "$top" in
        *com.android.provision/*|*com.ktcp.launcher/*|*com.xiaopaitech.plauncher/*)
            am force-stop com.android.provision 2>/dev/null
            am force-stop com.ktcp.launcher 2>/dev/null
            am force-stop com.xiaopaitech.plauncher 2>/dev/null
            am start -n $COMP >/dev/null 2>&1
            ;;
    esac
    sleep 4
done
