#!/usr/bin/env python3
"""Cleanly patch filterHomeApp in services.jar to disable HOME filtering.

Correct method: insert 'return-void' AFTER .local p1 (first real instruction),
NOT in the .param/.annotation block (apktool drops it there).
"""
import subprocess, os, shutil

BASE = "f:/work/jiguang"
ORIG = BASE + "/backup/tools/services.jar"
APKTOOL = BASE + "/backup/tools/apktool.jar"
WORK = BASE + "/patch_work"
OUT = BASE + "/services_root.jar"

def run(cmd, timeout=300):
    r = subprocess.run(cmd, capture_output=True, timeout=timeout)
    return (r.stdout or b"").decode("utf-8", "ignore"), (r.stderr or b"").decode("utf-8", "ignore"), r.returncode

# 1. fresh decompile from ORIGINAL jar
if os.path.exists(WORK):
    shutil.rmtree(WORK)
print("[1/5] decompiling original services.jar ...")
out, err, rc = run(["java", "-jar", APKTOOL, "d", ORIG, "-o", WORK, "-f"])
if rc != 0:
    print("DECOMPILE FAILED:", out[-500:], err[-500:]); raise SystemExit(1)

# 2. find smali file and method
smali = None
for root, dirs, files in os.walk(WORK):
    if "PackageManagerService.smali" in files:
        smali = os.path.join(root, "PackageManagerService.smali")
        break
if not smali:
    print("smali not found"); raise SystemExit(1)
print(f"  smali: {smali}")

t = open(smali, encoding="utf-8").read()
i = t.find(".method private filterHomeApp")
if i < 0:
    print("filterHomeApp not found"); raise SystemExit(1)
j = t.find(".end method", i)
method = t[i:j]

# 3. insert return-void after the .local p1 line (first real instruction)
needle = '    .local p1, "lst":Ljava/util/List;, "Ljava/util/List<Landroid/content/pm/ResolveInfo;>;"\n'
if needle not in method:
    print("anchor .local p1 not found in method"); raise SystemExit(1)
patched_method = method.replace(needle, needle + "    return-void\n", 1)
t2 = t[:i] + patched_method + t[j:]
open(smali, "w", encoding="utf-8").write(t2)
print("[2/5] inserted return-void after .local p1")

# 4. rebuild
print("[3/5] rebuilding jar ...")
if os.path.exists(OUT):
    os.remove(OUT)
out, err, rc = run(["java", "-jar", APKTOOL, "b", WORK, "-o", OUT, "-f"])
if rc != 0:
    print("BUILD FAILED:", out[-800:], err[-800:]); raise SystemExit(1)
print(f"  built {OUT} ({os.path.getsize(OUT)} bytes)")

# 5. verify by re-decompiling the built jar
print("[4/5] verifying patch survived rebuild ...")
vdir = BASE + "/verify_work"
if os.path.exists(vdir):
    shutil.rmtree(vdir)
run(["java", "-jar", APKTOOL, "d", OUT, "-o", vdir, "-f"])
vs = None
for root, dirs, files in os.walk(vdir):
    if "PackageManagerService.smali" in files:
        vs = os.path.join(root, "PackageManagerService.smali"); break
vt = open(vs, encoding="utf-8").read()
vi = vt.find(".method private filterHomeApp")
vj = vt.find(".end method", vi)
vm = vt[vi:vj]
# check return-void appears right after .local p1 and before first invoke
has_ret = "return-void" in vm
ok = needle in vm and vm.split(needle)[1].strip().startswith("return-void")
print(f"  return-void present: {has_ret}")
print(f"  position correct: {ok}")
if not ok:
    print("PATCH VERIFICATION FAILED:\n", vm[:600]); raise SystemExit(1)
print("[5/5] PATCH OK")
