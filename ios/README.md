# Native iOS harness

`DoomBFGHarness` began in Phase 02 as a UIKit/Objective-C++ application for iPhone
and iPad. Phase 03 adds selected upstream idlib core utilities and runtime
fixtures. The complete engine, gameplay, game assets, renderer and audio remain
unintegrated. The screen explicitly identifies this scope. Bundled `COPYING.txt`
retains the upstream GPL notice; corresponding source is in this repository.

`toolchain.json` pins Xcode 16.4 (16F6), SDK/runtime 18.5, ARM64 device and
simulator, and iOS deployment target 15.0. There is no toolchain fallback.
The GitHub runner label is `macos-15`; its actual image is recorded per run.

Generate the checked-in project using only Python's standard library:

```text
python scripts/ios/generate_project.py
python scripts/ios/generate_project.py --check
```

`harness/sources.json` lists every source/resource/framework input explicitly.
The generated shared scheme is `DoomBFGHarness`. Open
`ios/DoomBFGHarness.xcodeproj` in the pinned Xcode to inspect it.

On an ARM64 macOS runner with that Xcode and iOS 18.5 simulator runtime:

```text
python3 scripts/ios/audit_repository.py --check
python3 scripts/ios/preflight.py
python3 scripts/ios/verify_harness.py
```

Verification builds separate device/simulator products with signing disabled,
records binary architectures and load commands, then creates dedicated iPhone 16
and iPad (10th generation) simulators. It installs and launches the simulator app,
passes a fresh nonce, checks the app's receipt written from `viewDidAppear`,
and captures screenshots. It terminates the app and deletes only the simulators
it created. A launch request alone cannot pass the receipt gate.

Reports and screenshots live under `artifacts/ios-preflight` and
`artifacts/ios-harness`; build products live under `build/ios-harness`.
Both directories are ignored. Use a fresh output directory when rerunning
Xcode verification (`-resultBundlePath` must not already exist).
The Actions workflow uploads reports on failure as well as success.

For the Phase 03 fixture gate, CI uses `--families iPhone`. The default still
runs both simulator families. The receipt includes a `core_tests` result for
the current selected idlib source group, in addition to the launch nonce.
Fixture diagnostics in `ios/tests/IdlibDiagnostics.cpp` are test support and
must be replaced by actual Lib.cpp/framework services during engine integration.

`xcodebuild -help` from the actual pinned Xcode records archive/export options
in the reports. This phase does not archive, export an IPA, sign an app, or
prove installation on a physical device. Device build products are unsigned.
Only the simulator app is executed. Later phases integrate the engine.
