#!/usr/bin/env bash
# newgame.sh [ENV=val...]: boot with the control socket, Play -> New game (slot 1): a fresh save into the intro
P=io.github.graveyardkeeperrecomp; D=/storage/emulated/0/Android/data/$P/files
adb shell am force-stop $P; adb shell rm -f $D/savagewind.log
ex=(); for kv in "$@"; do ex+=(--es "${kv%%=*}" "${kv#*=}"); done
adb shell am start -n $P/com.deivid22srk.savagewind.MainActivity --es SAVAGEWIND_NO_LAUNCHER 1 --es SAVAGEWIND_CONTROL 7777 "${ex[@]}" >/dev/null
sleep 60  # (the title takes ~55 s to load and accept input)
"$(dirname "$0")"/ctl.sh press a 6 >/dev/null; sleep 4  # Play -> Saves
"$(dirname "$0")"/ctl.sh press a 6 >/dev/null          # New game (slot 1) -> intro
