# Upstream audit and iOS work map

Baseline: `1caba1979589971b5ed44e315d9ead30b278d8b4`.
`upstream-audit.json` inventories every one of the 1,115 upstream blobs (18,227,637
bytes), including non-source files. Binary blobs are hashed/classified; every
text blob is mechanically screened. This does not establish compile readiness
or complete semantic review. Each port phase must review its actual subsystem.

Regenerate with `python scripts/ios/audit_repository.py`; verify with `--check`.
The input is immutable Git objects, avoiding host newline conversion and excluding
local IDE state, generated files, credentials, and private assets. Risk patterns
and exact hit lines are included, so findings can be reviewed and improved.

## Findings verified in source

| Area | Evidence | Required work |
| --- | --- | --- |
| Build | `neo/doom3.sln`, eight `.vcxproj` files, `_PCLibs.props` | New Apple project; preserve Windows projects. Seven solution projects reference existing source declarations. The extra `game.vcxproj` is stale (68 missing files). Inventory declarations are not resolved per-configuration build lists. |
| Platform | `neo/idlib/sys/sys_defines.h` errors for non-Windows; `sys_includes.h` unconditionally includes Windows/DirectX/intrinsics | Add conditional Apple platform layer and portable compiler/ABI definitions |
| Concurrency | `sys_threading.h` uses HANDLE/CRITICAL_SECTION and Windows TLS | pthread services, atomics/TLS with lifecycle tests |
| Renderer | `OpenGL/qgl.h` imports desktop GL; `RenderProgs_GLSL.cpp`, `tr_backend_draw.cpp`, `BufferObject.cpp` | Metal backend; shader/parameter translation; complete render-pass coverage |
| Textures | `Image_load.cpp`, `BinaryImageData.h`, DXT sources | Big-endian binary image parsing, BC1/BC3 fallback, YCoCg/normal-map preservation |
| Audio | `snd_local.h` imports DirectX/XAudio2/X3DAudio; `sound/XAudio2/` implements voices/samples | Apple audio backend and Microsoft ADPCM decode; no XMA requirement assumed for PC assets |
| Content | `FileSystem.cpp` enumerates `.resources`; `Common.cpp` opens `_startup` level resources; filesystem verifies `default.cfg` | Complete private BFG base directory, resource-aware validation and iOS sandbox paths |
| Classic | `doomclassic/doom/doomlib.cpp` lists BFG WADs and additional expansion names | BFG DOOM/DOOM II/NERVE integration; TNT/Plutonia/Master Levels require separate assets and are not BFG deliverables |
| Cinematics | README and `Cinematic.cpp` confirm video decoder is absent | Explicit no-video fallback initially; evaluate an optional licensed decoder/conversion only if needed, never claim Bink playback |
| Gameplay | `neo/d3xp` is the active game source tree | Port static gameplay linkage; preserve all BFG campaigns |
| Licensing | `COPYING.txt`, `README.txt`, bundled dependency notices | Retain notices and source; game assets excluded from public repository/artifacts |

Mechanical flags: Windows API tokens in 201 files; MSVC/x86 tokens in 48;
desktop GL in 26; DirectX audio/input in 16; filesystem/process calls in 20;
asset-format literals in 9. Counts overlap and include comments/vendor headers;
they are a triage map, not a defect count. Absence of a flag is not proof of portability.

## Dependency decisions

Retain bundled JPEG (modified C++), zlib, amplitude and TiMidity initially, with
isolated Apple compile fixes and license notices. Their MSVC settings cannot be
copied verbatim. SDL/ANGLE/OpenAL/FFmpeg are not yet added: native Apple APIs keep
the initial dependency graph smaller. No Win32 `.lib` may enter the Apple target.
Audit external imports, calling conventions, packing, pointer width, serialization,
and shader layouts when each source group is activated. Do not enable x86 SSE on
ARM64 or change on-disk formats merely to accommodate Apple native structure sizes.

## Research baseline (checked 2026-10-15)

Apple documents deprecated OpenGL ES and provides Metal migration guidance:
[Metal migration](https://developer.apple.com/documentation/metal/migrating-opengl-code-to-metal),
[OpenGL ES](https://developer.apple.com/documentation/opengles).
The inspected [macOS 15 runner manifest](https://github.com/actions/runner-images/blob/main/images/macos/macos-15-Readme.md)
lists Xcode 16.4/16F6 and iOS 18.5. Availability is still subject to actual preflight.
No local Apple build tools are available on this Windows host.

## Phase 02 review boundary

Reviewed the added UIKit lifecycle/launch receipt in `ios/harness/main.mm`,
the explicit harness manifest/Info.plist, deterministic project generator and
generated scheme/project, SDK probe script, harness verification script, and
Actions checkout/evidence steps. The harness source manifest includes exactly
one Objective-C++ source and the upstream GPL notice; it includes no engine,
bundled dependency or game-asset source. No upstream blob is changed in this
phase. The full-file inventory continues to verify against the same baseline.

This is semantic review of the new app/build harness only. Upstream engine
subsystems remain mechanically screened and await their assigned port phases.
CI results and exact toolchain/runner evidence are in `PHASE_02.md`.
