#!/system/bin/sh
Tag="SKYLOGS"
sleep 5;

# FLauncher watchdog (user added)
while [ "$(getprop sys.boot_completed)" != "1" ]; do sleep 2; done
sleep 3
am force-stop com.android.provision 2>/dev/null
am start -n me.efesser.flauncher/.MainActivity >/dev/null 2>&1

system_process_pid=
get_system_pid()
{
    system_pid=$(ps | grep system_server)
    system_pid=${system_pid// /,}
    system_pid=${system_pid:14:4}
    system_process_pid=$system_pid
}

check_system_process()
{
    system_cur_pid=$(ps | grep system_server)
    system_cur_pid=${system_cur_pid// /,}
    system_cur_pid=${system_cur_pid:14:4}
    if [ "$system_cur_pid" != "$system_process_pid" ]
    then
        log -p d -t $Tag "01001,system restarted"
        system_process_pid=$system_cur_pid
    fi
}

check_ddr_cached_size()
{
    ddr_cached_base=62112
    ddr_cached_cmd=$(cat /proc/meminfo | grep -w "Cached:")
    ddr_cached_str=${ddr_cached_cmd// /,}
    ddr_cached=${ddr_cached_str%,*}
    ddr_cached_size=${ddr_cached##*,}
    if [ "$ddr_cached_size" -lt "$ddr_cached_base" ] 2>/dev/null
    then
        log -p d -t $Tag "01015,low memory"
    fi
}

check_cpu_temp()
{
    cpu_temp_base=85000
    cpu_temp=$(cat /sys/devices/virtual/thermal/thermal_zone0/temp)
    if [ "$cpu_temp" -gt "$cpu_temp_base" ] 2>/dev/null
    then
        log -p d -t $Tag "01016,cpu hot"
    fi
}

check_data_ro()
{
    data_ro=$(mount | grep " /data " | grep "ro," | wc -l)
    if [ "$data_ro" = 1 ]
    then
        log -p d -t $Tag "01013,data ro"
    fi
}

check_cache_ro()
{
    cache_ro=$(mount | grep " /cache " | grep "ro," | wc -l)
    if [ "$cache_ro" = 1 ]
    then
        log -p d -t $Tag "01014,cache ro"
    fi
}

check_bootvideo_exist()
{
    bootvideo=$(ps | grep bootplayer | wc -l)
    if [ "$bootvideo" = 1 ]
    then
        log -p d -t $Tag "01005,stuck bootvideo"
    fi
}

check_bootanima_exist()
{
    bootanimation=$(ps | grep bootanimation | wc -l)
    if [ "$bootanimation" = 1 ]
    then
        log -p d -t $Tag "01004,stuck bootanim"
    fi
}

check_bootvideo_exist
check_bootanima_exist
get_system_pid
while true
do
    check_data_ro
    check_cache_ro
    check_cpu_temp
    check_ddr_cached_size
    check_system_process
    top=$(dumpsys activity activities 2>/dev/null | grep -m1 'mResumedActivity')
    case "$top" in
        *com.android.provision/*|*com.ktcp.launcher/*|*com.xiaopaitech.plauncher/*)
            am force-stop com.android.provision 2>/dev/null
            am force-stop com.ktcp.launcher 2>/dev/null
            am start -n me.efesser.flauncher/.MainActivity >/dev/null 2>&1
            ;;
    esac
    sleep 5
done
