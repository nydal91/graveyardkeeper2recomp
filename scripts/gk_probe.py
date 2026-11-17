#!/usr/bin/env python3
"""Probe the Graveyard Keeper dump: module build ids, and the Unity wide-screen hook sites.

Usage: scripts/gk_probe.py [exefs]   (default: <repo>/exefs)
Prints each module's build id, then scans main for the three functions gen.py POST_HOOKS
hooks (GetScreenResolution, Matrix4x4f::SetOrtho, Matrix4x4f::SetPerspective), matched by
the same instruction words the Nine Sols / Terminator 2D builds use, at eh_frame entries.
"""
import os
import struct
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# appended, not prepended: that folder also holds the Android builds of capstone / unicorn,
# which would shadow this Python's own (as scripts/build_gamelib_host.sh notes)
sys.path.append(os.path.join(ROOT, 'app', 'src', 'main', 'python'))
from nso import Nso, header  # noqa: E402
from analyze import eh_frame_extents  # noqa: E402

BASE = 0x7000000000

# (name, words at entry+0, +0x14, +0x18) - gen.py POST_HOOKS
HOOKS = [
    ('rt_unity_screen_resolution', (0xA9BC7BFD, 0x5280A017, 0x52805A16)),
    ('rt_unity_ortho', (0x1E203830, 0xB9002C1F, 0x1E2438B2)),
    ('rt_unity_persp', (0xFC1C0FEC, 0x9100A3FD, 0x1E20402A)),
]


def main():
    exefs = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, 'exefs')
    for n in ('main', 'rtld', 'sdk', 'subsdk0'):
        p = os.path.join(exefs, n)
        if os.path.exists(p):
            h = header(p)
            print(f'{n}: build id {h["build_id"][:16]}  text {h["text"][1] / 1e6:.1f} MB')

    n = Nso(os.path.join(exefs, 'main'))
    lo, size = n.text
    words = struct.unpack_from(f'<{size // 4}I', n.image, lo)
    fdes = sorted((a, b) for a, b in eh_frame_extents(n) if b > a)
    starts = {a for a, _ in fdes}
    print(f'main: {len(fdes)} eh_frame functions')
    for name, (w0, w1, w2) in HOOKS:
        hits = []
        for i in range(len(words) - 6):
            if words[i] == w0 and words[i + 5] == w1 and words[i + 6] == w2:
                a = lo + i * 4
                hits.append((BASE + a, a in starts))
        print(f'{name}:')
        for a, is_entry in hits:
            print(f'    {a:#x}  {"FUNCTION ENTRY" if is_entry else "not an entry"}')
        if not hits:
            print('    no match')


if __name__ == '__main__':
    main()
