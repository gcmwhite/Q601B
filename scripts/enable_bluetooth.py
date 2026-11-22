#!/usr/bin/env python3
import os
"""Enable Bluetooth on Q601B: set vendor overlay props, unblock rfkill, restart BT HAL."""
import subprocess, time
S = os.environ.get("BOX_IP", "<box-ip>") + ":5555"
SU="/system/xbin/su 0"

def sh(c, timeout=40):
    return subprocess.run(["adb","-s",S,"shell",SU+" sh -c "+repr(c)],capture_output=True,timeout=timeout).stdout.decode("utf-8","ignore")

def adbsh(c, timeout=40):
    return subprocess.run(["adb","-s",S,"shell",c],capture_output=True,timeout=timeout).stdout.decode("utf-8","ignore")

print("=== set BT props ===")
sh("setprop persist.vendor.overlay.bluetooth_support 1")
sh("setprop persist.vendor.overlay.bluetooth_vendor realtek")
print("support:", sh("getprop persist.vendor.overlay.bluetooth_support"), "vendor:", sh("getprop persist.vendor.overlay.bluetooth_vendor"))

print("\n=== unblock rfkill + power on ===")
sh("echo 1 > /sys/class/rfkill/rfkill0/state 2>/dev/null")
print("rfkill state:", sh("cat /sys/class/rfkill/rfkill0/state"))

print("\n=== restart BT HAL ===")
sh("setprop ctl.restart vendor.bluetooth-1-0")
time.sleep(3)
print("HAL:", sh("getprop init.svc.vendor.bluetooth-1-0"))

print("\n=== check HCI ===")
print("bluetooth class:", sh("ls /sys/class/bluetooth/"))
print("rfkill:", sh("cat /sys/class/rfkill/rfkill0/name /sys/class/rfkill/rfkill0/state"))
