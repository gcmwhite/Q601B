#!/usr/bin/env python3
import os
"""Restore super partition (system/product/vendor) from full backup.

This returns the device to the state right after root was obtained (before
app removal and services.jar patching). /data is NOT touched, so FLauncher
installation and root su symlink persist (su symlink is in /system though,
so it will be restored to original - usrchan setuid su is still there).
"""
import subprocess, gzip, struct, os, time

S = os.environ.get("BOX_IP", "<box-ip>") + ":5555"
SU = "/system/xbin/su 0"
IMG = "f:/work/jiguang/backup/full_emmc.img.gz"

def r(c, timeout=120):
    x = subprocess.run(["adb","-s",S,"shell",SU+" sh -c "+repr(c)], capture_output=True, timeout=timeout)
    return (x.stdout or b"").decode("utf-8","ignore") + (x.stderr or b"").decode("utf-8","ignore")

def read_gpt(f):
    f.seek(512); hdr=f.read(92)
    e=struct.unpack_from("<Q",hdr,72)[0]; n=struct.unpack_from("<I",hdr,80)[0]; sz=struct.unpack_from("<I",hdr,84)[0]
    f.seek(e*512); table=f.read(n*sz); parts={}
    for i in range(n):
        x=table[i*sz:(i+1)*sz]
        if x[:16]==b"\0"*16: continue
        name=x[56:128].decode("utf-16-le","ignore").rstrip("\0")
        parts[name]=(struct.unpack_from("<Q",x,32)[0], struct.unpack_from("<Q",x,40)[0])
    return parts

print("=== extracting super partition from backup ===")
with gzip.open(IMG,"rb") as f:
    parts=read_gpt(f)
    s,e=parts["super"]
    out="f:/work/jiguang/super_restore.img"
    if not os.path.exists(out) or os.path.getsize(out)!=(e-s+1)*512:
        f.seek(s*512); rem=(e-s+1)*512; t0=time.time()
        with open(out,"wb") as o:
            while rem>0:
                c=f.read(min(4*1024*1024,rem)); o.write(c); rem-=len(c)
        print(f"extracted {(e-s+1)*512/1e6:.0f}MB in {time.time()-t0:.0f}s")
    print(f"super img: {os.path.getsize(out)/1e6:.0f}MB")

print("\n=== pushing to device ===")
subprocess.run(["adb","-s",S,"push",out,"/data/local/tmp/super_restore.img"], check=True)
print("pushed")

print("\n=== writing super partition ===")
t0=time.time()
print(r("dd if=/data/local/tmp/super_restore.img of=/dev/block/by-name/super bs=1M 2>&1 && sync && echo WRITE_OK", timeout=600))
print(f"write took {time.time()-t0:.0f}s")

print("\n=== cleanup + reboot ===")
print(r("rm -f /data/local/tmp/super_restore.img"))
print(r("reboot"))
