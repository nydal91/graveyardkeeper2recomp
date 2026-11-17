#!/usr/bin/env bash
# install_driver.sh <AdrenoTools driver.zip> [more.zip ...]: push driver zips into the app's drivers folder and make
# them readable by the app. Files created over adb belong to shell with group-only modes, and Android's FUSE view of
# Android/data/<pkg> hides them from the app (listFiles() -> null, fopen -> EACCES), so the ownership is fixed here.
# The app unpacks each zip at its next start; choose it with `gpu_driver = <zip name without .zip>` in savagewind.ini
# (or Video > GPU driver in the menu). Needs root for the chown (adb shell su).
set -eu
P=io.github.graveyardkeeperrecomp
D=/storage/emulated/0/Android/data/$P/files
[ $# -ge 1 ] || { echo "usage: $0 <driver.zip> ..." >&2; exit 1; }
adb shell mkdir -p "$D/drivers"
for z in "$@"; do
    adb push "$z" "$D/drivers/" >/dev/null
done
OWN=$(adb shell su -c "stat -c %u:%g $D")  # the app's uid:gid, from its own files folder
adb shell su -c "chown -R $OWN $D/drivers"
# a hand-written ini has the same problem; fix it too when it is shell-owned
adb shell su -c "chown $OWN $D/savagewind.ini" 2>/dev/null || true
echo "installed: $* - start the app again; it unpacks and (with gpu_driver set) loads them"
