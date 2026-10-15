# Phase 02 evidence — 2026-10-15

Status: **COMPLETE**, native app harness and SDK validation only.
No engine is linked; no archive, signing, IPA, or gameplay was attempted.

## Remote and actual CI evidence

Authenticated through the existing Git Credential Manager account `Ryxm-a`.
Created [Ryxm-a/DOOM-3-BFG](https://github.com/Ryxm-a/DOOM-3-BFG), added the
`fork` remote, and pushed `codex/ios-port`. Upstream `origin` is unchanged.
No credentials, assets, or authenticated download URLs were committed.

Passing run: [38660266257](https://github.com/Ryxm-a/DOOM-3-BFG/actions/runs/38660266257)
at `b41cd12cc35afe96c9c95b59b15d558d67dc3e08`.

| Actual check | Result |
| --- | --- |
| Immutable upstream inventory and generated project | PASS |
| Xcode / build | 16.4 / 16F6 |
| Device and simulator SDK | 18.5 / 18.5 |
| Actual runner | macos-15-arm64, image 20260907.0337.1 |
| Actual OS | macOS 15.7.9 / 24G830 |
| Framework probes and Metal compile/metallib | PASS, both SDKs |
| Unsigned device harness compile/link | PASS, arm64, LC_BUILD_VERSION IOS, minos 15.0 |
| Simulator harness compile/link | PASS, arm64, IOSSIMULATOR, minos 15.0 |
| iPhone 16 / iOS 18.5 | PASS, fresh nonce receipt from viewDidAppear, screenshot, terminate |
| iPad 10th generation / iOS 18.5 | PASS, fresh nonce receipt from viewDidAppear, screenshot, terminate |
| Actual xcodebuild archive/export help | Recorded, including -archivePath, -exportArchive, -exportOptionsPlist |

Both receipts report 64-bit pointers and `engine_linked: false`. Both screenshots
were downloaded and visually inspected: legible centred harness text, landscape
app orientation (PNG retains the simulator's native portrait pixel axes).
Reports record full commands, framework references and binary metadata.
Final cleanup repeats shutdown on already-shut-down simulators (exit 149), which
is tolerated; both dedicated simulators were successfully deleted. These cleanup
messages are separate from the successful build/launch gates.

Uploaded artifacts (14-day retention; source and this handoff persist):

- [SDK evidence, artifact 11938872157](https://github.com/Ryxm-a/DOOM-3-BFG/actions/runs/38660266257/artifacts/11938872157),
  `ios-preflight-b41cd12cc35afe96c9c95b59b15d558d67dc3e08`, 31,614 bytes,
  GitHub SHA-256 `013b70d389d5174361d1967dea1ff979c7cd70ba585721cd48b21e714fc846f6`.
- [Harness evidence, artifact 11937973973](https://github.com/Ryxm-a/DOOM-3-BFG/actions/runs/38660266257/artifacts/11937973973),
  `ios-harness-b41cd12cc35afe96c9c95b59b15d558d67dc3e08`, 225,229 bytes,
  GitHub SHA-256 `6d4861846ecb3a0a8a77e097ee66788caa58ad23c9964c6e0859de9bde65992a`.

Evidence was downloaded under ignored `artifacts/phase02/38660266257/`.

## Implementation and local validation

Reviewed `ios/harness/main.mm`, Info.plist/manifest, project/scheme,
`generate_project.py`, `verify_harness.py`, preflight and Actions workflow.
App inputs: one Objective-C++ source and the GPL notice. See `ios/README.md`.
No external dependencies added. Full upstream audit remains unchanged.

| Windows check | Result |
| --- | --- |
| python scripts/ios/audit_repository.py --check | PASS |
| python scripts/ios/generate_project.py --check | PASS |
| Repeat generation | PASS, identical output |
| Deliberately stale generated project | PASS, --check rejects it |
| Python py_compile for new scripts | PASS |
| Non-macOS guard with SDK subprocess calls forbidden | PASS, failed report, no commands, no engine/IPA claims |
| Changed-path intersection with all upstream paths | PASS, zero changed upstream blobs |
| git diff --check | PASS |

Initial runs [38660148460](https://github.com/Ryxm-a/DOOM-3-BFG/actions/runs/38660148460)
and [38660179180](https://github.com/Ryxm-a/DOOM-3-BFG/actions/runs/38660179180)
failed because checkout's depth 1 omitted the audit revision (`not a tree object`).
Fixed with `fetch-depth: 0`; passing run above verifies the fix. No gate bypassed.

## Handoff

Proceed to Phase 03: conditional Apple platform headers/types, assertions,
allocation and selected core idlib utilities, with actual device/simulator
compilation and runtime fixture evidence. The user authorized continuous phases
in this chat, superseding the initial one-phase limit. No assets/signing needed.
Physical-device installation, iOS 15 execution, engine linkage, renderer and
gameplay remain untested.
