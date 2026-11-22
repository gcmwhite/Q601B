#!/usr/bin/env python3
import os
"""Run commands as root on the TencentBox Q601B (<BOX_IP_WIFI>) via ADB.

Usage:
    python rootadb.py                    # interactive root shell
    python rootadb.py "id"               # run one command as root
    python rootadb.py "ls -l /data"      # run one command as root
"""
import subprocess
import sys

SERIAL = os.environ.get("BOX_IP", "<box-ip>") + ":5555"
SU = "/system/xbin/su 0"


def ensure_adb():
    subprocess.run(["adb", "connect", SERIAL], capture_output=True)


def root_cmd(cmd, timeout=120):
    ensure_adb()
    wrapped = SU + " sh -c " + repr(cmd)
    r = subprocess.run(["adb", "-s", SERIAL, "shell", wrapped], timeout=timeout)
    return r.returncode


def root_shell():
    ensure_adb()
    subprocess.run(["adb", "-s", SERIAL, "shell", f"{SU} sh"])


if __name__ == "__main__":
    if len(sys.argv) == 1:
        root_shell()
    else:
        sys.exit(root_cmd(" ".join(sys.argv[1:])))
