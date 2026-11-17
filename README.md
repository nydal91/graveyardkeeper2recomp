# Graveyard Keeper Recomp — Android

A static recompilation of the Nintendo Switch release of *Graveyard Keeper* (Unity 6000.3.9f1, IL2CPP) to
native Android (arm64-v8a). It is built on the same runtime as the Nine Sols Recomp and the Terminator 2D: NO FATE
Recomp (SavageWindRecomp / MvDK Recomp lineage): the game's ARM64 NSO modules are lifted to C
(`app/src/main/python/gen.py`), compiled into `swgame.so`, and run against an HLE Horizon kernel and services, with
NVN translated to Vulkan.

> [!IMPORTANT]
> No game files are included. You need your own dump of the game (decrypted ExeFS + RomFS). Nothing is decrypted by
> this project.

## Status

Bring-up on a Snapdragon 8 Gen 2 phone (RedMagic 8 Pro, Adreno 740, Android 15) with Mesa Turnip v27.0.0-R1.

| Part | State |
|---|---|
| Lifting (gen.py) | main build id `2d29e899e84e1854`, ~449k functions (95.6 MB of ARM64 code); rtld / sdk / subsdk0 lifted with HLE |
| Version check | `runtime/game_versions.h`: main `2d29e899e84e1854`, Unity IL2CPP RomFS (25297 files; no System/Version.txt in this RomFS) |
| Wide screens | Unity's Matrix4x4f::SetOrtho / SetPerspective are byte-for-byte the same code as in Nine Sols / T2D, so the same hooks apply (gen.py `POST_HOOKS`, main `0x700095d730`, `0x700095d610`). GetScreenResolution takes its out-pointers in x1/x2 here, so it is left unhooked: the wide view comes from the two camera hooks and the renderer's widened 16:9 targets. Verified on the 2480x1116 phone: title, menus and gameplay fill the screen with correct proportions; with `wide_view = 0` the same screens fall back to a centred 16:9 picture with bars (`scripts/ini_set.sh wide_view 0`). Gameplay verified past the opening: dialogue advance, movement and camera follow, pause menu, HUD anchoring, full-width dim overlays. The opening's first dialogue lines render over a fade-from-black and input stays locked until ~44 advances incl. its choice menus (`scripts/intro_skip.sh`) - both are the game's own intro, not faults |
| Present crop | GK renders a 1280x720 display into 1920x1080 window textures and presents a crop (`nvnWindowSetCrop`). The viewport mapping of draws into the presented texture and the present's source rectangle follow that crop (`nvn_window_crop`, exec.c / device.c); without it the image lands letterboxed in a corner of the wide window |
| Scene targets | `SCENE_LINES` (`nvn/output_scale.c`) is 540: k=2 for GK's 640x360 pixel-art world, which the game blits 2x into its 1280x720 display (the present crop). At k=2 the world's backing size equals the crop's, so that blit is 1:1 and sprites keep their edges (verified against k=1 crops on the phone); at k=1 the world is filtered twice and smears. No measurable fill-rate cost on the Adreno 740 (same 44-62 ms worst frames, 30 fps). `SAVAGEWIND_LOG_RS=1` logs the render-target sizes the game makes (`[rs]` lines) for tuning other games |
| Unity 6 fixes | inherited from the T2D port: `svcGetInfo` 23/24 (IsApplication, FreeThreadCount); `nn::hid::Set/GetNpadJoyHoldType` HLE; `nvnCommandBufferBindProgram(NULL, stages)` only clears unused stages |
| GPU driver | Turnip v27.0.0-R1 verified loading and rendering (Mesa 27.0.0-devel, ASTC by the GPU). AdrenoTools zip in `Android/data/<pkg>/files/drivers`, chosen in Settings or `gpu_driver =` in `savagewind.ini`. Push zips with `scripts/install_driver.sh` (adb-created files are shell-owned and invisible to the app until their ownership is fixed) |

## Building

```sh
python3 -m venv .venv && .venv/bin/pip install lz4 capstone unicorn
export JAVA_HOME=~/Android/jdk-17.0.13+11
./gradlew assembleRelease
adb install -r app/build/outputs/apk/release/app-release.apk
scripts/build_gamelib_host.sh --push    # game code on this PC with the NDK, then exefs/romfs/swgame.so to the phone
```

Put your dump as `exefs/` and `romfs/` in the repository root (both git-ignored). The native dependencies
(`app/src/main/cpp/deps`, `jniLibs`, the bundled clang assets) come from `scripts/build_deps_android.sh`. A rebuilt APK
can change the GAMELIB_ID. If it does, run `build_gamelib_host.sh --push` again; it only relinks.

On the device the game files live in `/storage/emulated/0/Android/data/io.github.graveyardkeeperrecomp/files/extracted/`,
and the runtime log is `savagewind.log` one level up. To boot past the launcher (tests):
`adb shell am start -n io.github.graveyardkeeperrecomp/com.deivid22srk.savagewind.MainActivity --es SAVAGEWIND_NO_LAUNCHER 1`.
`scripts/devrun.sh` and `scripts/ctl.sh` (control socket on 7777: `press a 6`, `stick l 1 0 60`, `shot <name>`) work
as in the Nine Sols / T2D ports, plus `debugframe` (dump the next frame's passes as `build/pass_<frame>_NNN.png`;
needs `SAVAGEWIND_GPU_OVERLAP=0`, range filters `SAVAGEWIND_DEBUG_PASS_FROM/TO`, `SAVAGEWIND_DEBUG_MAIN_ONLY`).
`scripts/ini_set.sh key value` edits the device's `savagewind.ini` keeping the app's ownership of the inode
(a replaced inode on FUSE storage becomes invisible to the app); `scripts/intro_skip.sh` advances the opening
dialogue. The wide-view fallback is `wide_view = 0` (centred 16:9 with bars). `SAVAGEWIND_UNITY_ASPECT` /
`SAVAGEWIND_DISPLAY_W` override only the camera hooks / the display-resolution query here, not the renderer's
window scale, so synthetic aspects squeeze the image - test shapes on a real window or with `wide_view` instead.

The app icon and the launcher background are original art (`docs/icon/make_icon.py`,
`runtime/ui/splash.mm: keeper_art`): a moonlit graveyard, nothing of the game's own files.

## Credits

[SavageWindRecomp](https://github.com/Revivedx/SavageWindRecomp), [LAS Recomp](https://github.com/peiikai/LASRecomp)
(MIT), the SavageWindRecomp-Android / MvDK Recomp ports, the Nine Sols Recomp and the T2D NO FATE Recomp. See LICENSE
and the third-party notices of the original project.
