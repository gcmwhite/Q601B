#! /system/bin/sh 
Tag="SKYLOGS"
sleep 5;
# Keep Projectivy accessibility enabled (user added)
settings put secure enabled_accessibility_services com.spocky.projengmenu/.services.ProjectivyAccessibilityService
settings put secure accessibility_enabled 1
# Enable Bluetooth at boot (user added)
echo 1 > /sys/class/rfkill/rfkill0/state 2>/dev/null
system_process_pid=
function get_system_pid()
{
    system_pid=$(ps | grep system_server)
    system_pid=${system_pid//\ /,}
    system_pid=${system_pid:14:4}
    system_process_pid=$system_pid
}

function check_system_process()
{
    system_cur_pid=$(ps | grep system_server)
    system_cur_pid=${system_cur_pid//\ /,}
    system_cur_pid=${system_cur_pid:14:4}
    if [ $system_cur_pid -ne $system_process_pid ]
    then
        log -p d -t $Tag "01001,ϵͳ,Androidϵͳ"
        system_process_pid=$system_cur_pid
    fi

}

function check_ddr_cached_size()
{
    ddr_cached_base=62112
    ddr_cached_cmd=$(cat /proc/meminfo  | grep -w "Cached:")
    ddr_cached_str=${ddr_cached_cmd//\ /,}
    ddr_cached=${ddr_cached_str%,*}
    ddr_cached_size=${ddr_cached##*,}
    if [ $ddr_cached_size -lt $ddr_cached_base ]
    then
	log -p d -t $Tag "01015,ϵͳ,ڴ澯"
    fi
}

function check_cpu_temp()
{
    cpu_temp_base=85000
    cpu_temp=$(cat /sys/devices/virtual/thermal/thermal_zone0/temp)
    if [ $cpu_temp -gt $cpu_temp_base ]
    then
    	log -p d -t $Tag "01016,ϵͳ,cpu¶ȹ"
    fi
}

function check_data_ro()
{
    data_ro=$(mount | grep " /data " | grep "ro," | wc -l)
    if [ $data_ro == 1 ]
    then
    	log -p d -t $Tag "01013,ϵͳ,dataֻ"
    fi
}

function check_cache_ro()
{
    cache_ro=$(mount | grep " /cache " | grep "ro," | wc -l)
    if [ $cache_ro == 1 ]
    then
    	log -p d -t $Tag "01014,ϵͳ,cacheֻ"
    fi
}

function check_bootvideo_exist()
{
    bootvideo=$(ps | grep bootplayer | wc -l)
    if [ $bootvideo == 1 ]
    then
	log -p d -t $Tag "01005,ϵͳ,ڿƵ"
    fi
}

function check_bootanima_exist()
{
    bootanimation=$(ps | grep bootanimation | wc -l)
    if [ $bootanimation == 1 ]
    then
	log -p d -t $Tag "01004,ϵͳ,ڿ"
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
sleep 300
done
