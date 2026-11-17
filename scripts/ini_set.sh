#!/bin/bash
# Set keys in the device's savagewind.ini without losing the app's ownership of the file.
#   scripts/ini_set.sh wide_view 1 [gpu_driver Turnip_v27.0.0-R1 ...]
# The file is read and written through one inode (cat over it): a replaced inode on Android's
# FUSE storage ends up owned by whoever created it, and the app (a different uid) can no longer
# read it. Nested quotes do not survive adb shell + su -c, so the edit happens here, locally,
# and only a plain `cat path > path` runs on the device.
set -e
cd "$(dirname "$0")/.."
P=io.github.graveyardkeeperrecomp
D=/storage/emulated/0/Android/data/$P/files
[ $# -ge 2 ] && [ $(($# % 2)) -eq 0 ] || { echo "usage: $0 key value [key value ...]" >&2; exit 1; }
adb shell su -c "cat $D/savagewind.ini" > .tmp/ini_cur 2>/dev/null || : > .tmp/ini_cur
python3 -I - "$@" <<'EOF'
import sys
kv = dict(zip(sys.argv[1::2], sys.argv[2::2]))
lines = open('.tmp/ini_cur').read().splitlines()
out, seen = [], set()
for ln in lines:
    k = ln.split('=')[0].strip()
    if k in kv:
        out.append('%s = %s' % (k, kv[k])); seen.add(k)
    else:
        out.append(ln)
for k, v in kv.items():
    if k not in seen: out.append('%s = %s' % (k, v))
open('.tmp/ini_new', 'w').write('\n'.join(out) + '\n')
EOF
adb push .tmp/ini_new /data/local/tmp/ini_new >/dev/null
adb shell su -c "cat /data/local/tmp/ini_new > $D/savagewind.ini; rm -f /data/local/tmp/ini_new"
adb shell su -c "cat $D/savagewind.ini"