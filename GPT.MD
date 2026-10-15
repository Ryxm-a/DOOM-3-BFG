# DOOM 3 BFG iOS port: session contract and delivery plan

## Objective and current state

Deliver the BFG engine, DOOM 3 campaign, Resurrection of Evil, Lost Mission,
and included classic DOOM content as an iOS application, with an IPA produced
by GitHub Actions on macOS. An SDK probe, empty application, diagnostic renderer,
ZIP named `.ipa`, or unsigned archive is not the final deliverable.

Date: 2026-10-15 (Asia/Karachi). Branch: `codex/ios-port`.
Preserved upstream: `1caba1979589971b5ed44e315d9ead30b278d8b4`.
Phase 01 is complete within its **local audit and CI preparation scope**.
Next session: Phase 02. Engine compilation, Apple SDK execution, signing,
IPA export, and gameplay have **not** been verified.

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
| 02 | Obtain GitHub access, create/use writable fork, push branch, run preflight; native Xcode app harness and simulator launch | macOS CI probes pass, device harness links, simulator launches; archive/export help recorded; distinguish harness from engine | NEXT |
| 03 | Apple platform defines/includes/types/asserts/allocators and core string/container/hash utilities | Selected idlib files compile for device/simulator; width/alignment/endian and allocation tests pass | Pending |
| 04 | Remaining idlib math, generic SIMD, jobs data and ARM64 compatibility | idlib static library builds; representative SIMD/reference and serialization checks pass | Pending |
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

No game assets or Apple credentials are needed for Phase 01. GitHub write/Actions
access is needed for Phase 02: only `origin` (id-Software/DOOM-3-BFG) exists;
no writable fork, GitHub CLI, or authenticated GitHub connector was discovered.
Request an authorized GitHub credential/connection when publishing/running CI;
create/configure the writable repository automatically if that access permits it.

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
