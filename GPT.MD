# DOOM 3 BFG iOS port: session contract and delivery plan

## Objective and current state

Deliver the BFG engine, DOOM 3 campaign, Resurrection of Evil, Lost Mission,
and included classic DOOM content as an iOS application, with an IPA produced
by GitHub Actions on macOS. An SDK probe, empty application, diagnostic renderer,
ZIP named `.ipa`, or unsigned archive is not the final deliverable.

Date: 2026-10-15 (Asia/Karachi). Branch: `codex/ios-port`.
Preserved upstream: `1caba1979589971b5ed44e315d9ead30b278d8b4`.
Phases 01 through 03 are complete within their stated scopes. Phase 02 has actual
macOS CI evidence for SDK compilation and native harness launch on iPhone/iPad.
Phase 03 compiles/tests selected real idlib utilities for both Apple targets.
Current work: Phase 04. Complete engine linkage, signing, IPA export, and gameplay
have **not** been verified.

User override (2026-10-15): continue all phases sequentially in this chat without
stopping after one phase. This supersedes the one-phase-per-session limit below;
all implementation/verification gates, source preservation, and credential/asset
requirements still apply. Update the handoff after each phase and proceed to the
next eligible phase. Unavailable external inputs cannot be invented or bypassed.

## Rules for every session

1. Read this file, `docs/ios/AUDIT.md`, and the latest phase evidence before editing.
   Inspect branch, working tree, and any applicable repository instructions.
2. Complete exactly one next eligible phase per session, then update this file
   with changes, commands/results, CI run/artifact links where available, and
   the next phase. Do not silently skip a failed gate or substitute a placeholder.
3. Work autonomously on `codex/ios-port`; preserve Windows targets, licenses,
   existing user changes, and upstream history. Make platform-specific changes
   conditional and keep replacements in separate Apple files where practical.
4. Each phase includes implementation and its stated verification. Fix failures
   before closing it. Use immutable dependency revisions/checksums, pinned action
   commits, and explicit Xcode versions. Never use `macos-latest` or silently
   select another Xcode. Hosted runner images themselves are mutable; record them.
5. Maintain the full-file inventory. Mechanical screening is not semantic review;
   review files in the subsystem being ported and record coverage/exclusions.
6. No assets, private keys, profiles, tokens, or asset download URLs in Git or
   public logs/artifacts. Use private inputs and isolated signing jobs. Preserve
   GPL and bundled library notices and include corresponding port source.
7. Ask only for genuinely unavailable assets/credentials/access. Automate remote
   creation, secrets setup, CI dispatch, signing setup, and diagnostics when
   authorized credentials permit it. Do not push to id Software's repository.
8. If an external gate cannot be satisfied, record the actual blocker and keep
   doing independent work within the phase. Do not mark the phase complete simply
   because a session must end. Replan an oversized phase into smaller numbered
   phases **before** attempting it, keeping its acceptance criteria intact.

## Technical decisions

- Native UIKit/Objective-C++ application; iPhone and iPad, landscape, ARM64 device.
  Minimum deployment target iOS 15.0. Simulator is an explicit separate build.
- Metal/MetalKit backend, retaining upstream GL for Windows. Port engine shader
  parameter conventions and DXT/YCoCg/normal-map semantics. Use a CPU BC1/BC3
  decode fallback where hardware texture support cannot be established.
- POSIX/pthread services and portable atomics; generic SIMD first, optional NEON
  only after correctness checks. Do not alias Windows ABI types onto Apple types.
- AVAudioEngine/AudioToolbox with PCM and Microsoft ADPCM decoding; GameController
  plus touch controls. No dependency on DirectX, XAudio2, WGL, or Windows libraries.
- Static game linkage on iOS, preserving dynamic Windows paths. Runtime assets in
  Application Support, saves/config in a separate writable sandbox location;
  compiled shaders and open-source configuration may live in the app bundle.
- Deterministically generate/check in an Xcode project with standard-library Python
  and explicit source manifests. No CocoaPods/XcodeGen dependency for the initial
  target. Retain bundled JPEG/zlib/TiMidity with needed portability patches.
- Initial compiler baseline: macOS 15 runner, Xcode 16.4 build 16F6, SDK 18.5.
  `ios/toolchain.json` is authoritative; verify actual runner availability.
  App Store submission is not assumed or part of initial delivery.
- Preferred final export: manually signed registered-device distribution. Select
  actual export method supported by the pinned Xcode once credentials are known.
  Simulator builds require no distribution credentials. A raw unsigned package,
  if technically verified later, is diagnostic only and not installable proof.

## Phases (one completed phase per session)

Every later phase requires the previous gate unless a blocker explicitly permits
an independent subphase. macOS build evidence is required from Phase 02 onward.

| Phase | Implementation boundary | Gate to close the phase | State |
| --- | --- | --- | --- |
| 01 | Immutable inventory, dependency/platform triage, asset/signing requirements, phase plan, pinned SDK preflight workflow | Every upstream blob covered; audit regenerates identically; local tooling checks; all unavailable validation labelled | COMPLETE |
| 02 | Obtain GitHub access, create/use writable fork, push branch, run preflight; native Xcode app harness and simulator launch | macOS CI probes pass, device harness links, simulator launches; archive/export help recorded; distinguish harness from engine | COMPLETE |
| 03 | Apple platform defines/includes/types/asserts/allocators and core string/container/hash utilities | Selected idlib files compile for device/simulator; width/alignment/endian and allocation tests pass | COMPLETE |
| 04 | Remaining idlib math, generic SIMD, jobs data and ARM64 compatibility | idlib static library builds; representative SIMD/reference and serialization checks pass | CURRENT |
| 05 | POSIX threads, signals, timing, atomics, TLS and CPU detection | Job/thread lifecycle, wakeup, and atomic stress checks in simulator; device compile passes | Pending |
| 06 | Bundled JPEG, zlib, amplitude and TiMidity source lists/portability | Static dependencies compile/link in both targets; decompression and image/audio fixture checks; notice manifest | Pending |
| 07 | Apple file paths, resource container IO, directory enumeration, endian formats, save/config writes | Synthetic resource reads and sandbox round trips; no asset dependency | Pending |
| 08 | BSD networking, local users, session/save/profile services and offline defaults | Offline session initializes; save round trips and local socket checks; unavailable online services documented | Pending |
| 09 | Framework, SWF, UI, collision/AAS source compatibility | These source groups compile to static libraries for both targets with explicit exclusions | Pending |
| 10 | d3xp gameplay integration, static game linkage, engine entry/frame/lifecycle wiring | Complete engine links with clearly labelled temporary diagnostic backend; no Windows symbols; graceful no-assets screen | Pending |
| 11 | Metal surface/device/command lifecycle, buffers, vertex/index cache and render states | Deterministic indexed draw readback; resize/background handling; GPU validation | Pending |
| 12 | Shader conversion, uniform layouts, vertex variants and built-in programs | Required renderprogs compile to metallib in CI; layout and shader-family fixture checks | Pending |
| 13 | Texture upload, samplers, mipmaps, BC1/BC3 decoding, YCoCg/normal formats | Known compressed fixtures match expected pixels; cube/depth targets; memory lifetime checks | Pending |
| 14 | Backend depth, ambient/material and GUI/SWF passes | Synthetic multi-pass material/UI scene readback and transparency/depth checks | Pending |
| 15 | Light interactions, skinning and stencil shadows | Animated mesh + light/shadow fixture; stencil/depth parity; GPU validation | Pending |
| 16 | Subviews, postprocessing, resolution scaling and classic framebuffer composition | Render-to-texture, gamma/postprocess fixtures; complete renderer coverage ledger | Pending |
| 17 | Apple audio hardware/voices, PCM and ADPCM, streaming and interruption support | Decoder fixtures, loop/mixing checks, simulator audio evidence; route handling compiled | Pending |
| 18 | Touch HUD, controller events, menu navigation and lifecycle pause/resume | Automated menu/movement/fire events and synthetic input traces; both device layouts | Pending |
| 19 | Classic DOOM/DOOM II/TiMidity runtime integration | Classic engine compiles/links, palette framebuffer and MIDI fixtures; graceful absent WADs | Pending |
| 20 | Private PC asset inventory/import, resource-contained data validation, texture/sound compatibility and asset transport | Hash manifest; all selected campaign/menu/classic data resolve; private asset CI integration without public leakage | Pending (assets here) |
| 21 | Gameplay regressions, campaign/classic smoke runs, save/load, cinematic fallback and performance/memory fixes | Recorded automated representative map/classic runs, restart/save/load and memory evidence; limitations explicit | Pending |
| 22 | Signing preflight, ephemeral keychain/profile import, archive/export workflow and IPA inspection | Actual credential/profile checks, device archive, successful Xcode export, ARM64/signature/entitlements/profile/IPA layout checks; downloadable CI IPA | Pending (credentials here) |
| 23 | Clean-run reproducibility, install/launch acceptance and delivery documentation | Fresh CI run reproduces build inputs; IPA/source/notice hashes, simulator acceptance, real-device evidence if authorized device access exists; untested device behavior explicit | Pending |

Reproducibility means pinned source/toolchain/dependencies and traceable outputs;
Apple signing timestamps/profile changes preclude promising byte-identical IPAs.
Final acceptance must identify whether real-device installation was tested.

## Requirements that may need user input

GitHub access was established in Phase 02 using the existing Git Credential Manager
account `Ryxm-a` (no credential is stored in the repository). The writable remote
`fork` is `https://github.com/Ryxm-a/DOOM-3-BFG.git`; `origin` remains upstream
and must not receive pushes. `codex/ios-port` tracks `fork/codex/ios-port`.
GitHub CLI/connector are not installed; authenticated API requests were used for
CI status and evidence downloads. Assets/signing credentials are still not needed
for the early phases.

At Phase 20, supply the entire patched **BFG Edition** PC installation `base`
directory at `private-assets/pc/base/`, or authorize a private, authenticated
asset location. See `docs/ios/ASSETS.md`. No need to supply it now.

At Phase 22, require an Apple signing identity with private key and matching
provisioning profile, or sufficient authorized Apple account/API access to create
them. Registered-device delivery also requires device registration. Request actual
values only then; never assume a personal account or API key grants distribution.
See `docs/ios/BUILD_REQUIREMENTS.md` for the proposed secret contract.

## Phase 01 evidence and handoff

- 1,115 immutable upstream blobs, 18,227,637 bytes, SHA-256 and Git object IDs,
  subsystem ownership and line-level risk flags in `docs/ios/upstream-audit.json`.
- Eight vcxproj inventories; seven active solution projects have existing declared
  source files. Stale `neo/game.vcxproj` names 68 missing `neo/game/` sources and
  is not in `neo/doom3.sln`. Use `neo/d3xp`, not invented replacement files.
- `python scripts/ios/audit_repository.py --check`: PASS on Windows, Python 3.12.
- `python scripts/ios/preflight.py`: expected FAIL on Windows, with explicit macOS
  requirement and JSON evidence. This is a guard check, not Apple SDK validation.
- `.github/workflows/ios-preflight.yml` exists, but has not been pushed or run.
- Upstream source remains unchanged. Existing `.vs/` content is preserved/ignored.
- Additional local verification and exact results are recorded in
  `docs/ios/PHASE_01.md`; review it before Phase 02.

## Phase 02 evidence and handoff

- Created the user-owned writable fork and pushed only to `fork/codex/ios-port`.
- Native UIKit/Objective-C++ harness, explicit source manifest, standard-library
  deterministic Xcode project generator, device/simulator build and nonce-verified
  iPhone/iPad launch checks. The harness does not link engine sources.
- Passing macOS run at `b41cd12cc35afe96c9c95b59b15d558d67dc3e08`:
  https://github.com/Ryxm-a/DOOM-3-BFG/actions/runs/38660266257
- Xcode 16.4 / 16F6, both SDKs 18.5, ARM64, deployment target 15.0;
  runner `macos-15-arm64`, image `20260907.0337.1`, macOS 15.7.9 / 24G830.
- SDK framework and Metal compilation pass; harness links for IOS and
  IOSSIMULATOR; both simulator families emit `viewDidAppear` receipts on iOS 18.5.
  Downloaded screenshots were visually inspected. Archive/export help is captured.
  No archive/signing/IPA or engine/gameplay claim is made.
- Fixed the real initial CI failure by fetching history (`fetch-depth: 0`).
  Local generation/stale-output/Windows-guard checks pass. All 1,115 upstream
  blobs remain unchanged through Phase 02. See `docs/ios/PHASE_02.md`.
- Continue Phase 03 under the user's continuous-work override above.

## Phase 03 decomposition (before implementation)

Header review shows the upstream precompiled header imports the whole framework,
renderer, gameplay and Windows threading even for checksum sources. Keep Phase 03's
full gate, with two sequential subphases to isolate those dependencies:

- 03a: Apple platform defines/includes/types/asserts, real Apple heap allocation,
  basic list/sort containers and CRC32/MD4/MD5. Gate: real ARM64 device/simulator
  compilation; simulator width/alignment/endian/allocation and known hash vectors.
- 03b: core string utilities and hash-index containers, removing framework coupling
  needed for their standalone build. Gate: actual device/simulator compile and
  string/container fixtures. Phase 03 is COMPLETE only after both subgates pass.

No renderer, math/SIMD library or concurrency completion is inferred from 03a.

03a gate PASS at `6366dd0`, macOS run
https://github.com/Ryxm-a/DOOM-3-BFG/actions/runs/38661613413 .
Downloaded reports confirm both ARM64 builds and an iPhone iOS 18.5 receipt
with passed ABI, endian, allocation, list/sort, CRC32, MD4 and MD5 fixtures.
03b has now passed; see the final evidence below and `docs/ios/PHASE_03.md`.

03b first CI run 38662472580 compiled both ARM64 products but failed its runtime
receipt gate. Added app console/crash diagnostics and found/fixed Apple's shallow
`idHashIndex` copy construction (deep-copy assignment existed but no copy ctor).
Run 38663205426 built both products but hit a simctl file-redirection launch
timeout. Managed `--console` capture now retains app output and launch diagnostics.
The unchanged fixtures are being rerun at `47c8b944ddd1058a576c82109532e2a6036aa3e1`:
https://github.com/Ryxm-a/DOOM-3-BFG/actions/runs/38664303363 .
The runtime gate PASSED on run 38664303363. Downloaded reports and artifact
SHA-256 checks confirm ARM64 device/simulator builds and all ten fixture groups:
ABI, endian, allocation, list/sort, CRC32, MD4, MD5, strings, bounded formatting,
and hash-index ownership. No test was removed to pass the gate. Source
`47c8b944ddd1058a576c82109532e2a6036aa3e1`, Xcode 16.4/16F6, SDK/runtime18.5,
macos-15-arm64 image 20260907.0337.1. Phase 03 COMPLETE; continue Phase 04.

## Phase 04 decomposition (before implementation)

04a builds an actual idlib static-library target with foundational scalar math,
vectors/matrices/quaternions and fixed-layout serialization fixtures for
both ARM64 platforms, retaining the Phase 03 regressions.
04b adds generic SIMD, bounds, remaining dynamic math/geometry and jobs data compatibility.
It must pass representative SIMD/scalar references and compile the job data
interfaces; real thread/job lifecycle stress remains Phase 05. Phase 04 closes
only after both subgates pass. x86-only SIMD/benchmark implementations are kept
for Windows and excluded from the Apple source manifest, with real scalar Apple
dispatch supplied separately. No NEON backend is claimed.

04a current source `a210540bed160c79944b646c4748ff03e3c93648`, run
https://github.com/Ryxm-a/DOOM-3-BFG/actions/runs/38666120871 is pending verification.
The project builds a real DoomIdlib static archive, links the fixture app, and
checks scalar transforms, all ODE integrators, polynomial ownership and exact
serialization bytes. Earlier 04a commits were superseded by ownership review
fixes; no 04a pass is claimed yet. See `docs/ios/PHASE_04.md`.
