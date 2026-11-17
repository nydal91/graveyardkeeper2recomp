#!/bin/bash
# Advance the new game's opening dialogue until the intro script releases input (~44 A presses:
# the tree includes choice menus, and A selects the highlighted choice there).
# The first lines render over a fade-from-black: that black is the game's own fade, not a
# rendering fault - the world appears behind the dialogue after a few advances. Movement and
# the pause menu stay locked until the script ends, so press on even while nothing seems to move.
cd "$(dirname "$0")/.."
for i in $(seq 1 44); do
  scripts/ctl.sh press a 6 >/dev/null
  sleep 2
done
echo intro-advanced