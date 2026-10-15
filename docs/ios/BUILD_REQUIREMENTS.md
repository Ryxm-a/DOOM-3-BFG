# macOS CI, archives, signing and IPA requirements

## What is verified now

The Windows host can run the standard-library Python audit. No Apple SDK,
engine iOS build, archive, signature, export, or install has been executed.
There is only an upstream Git remote; no writable GitHub remote or authenticated
GitHub tool/CLI was discovered. Phase 02 needs authorized GitHub access to create
or use a fork and dispatch/inspect Actions. Avoid requesting Apple credentials
before the engine can reach a signing/export gate.

The initial workflow is an **SDK preflight only**, not an IPA workflow.
It checks pinned Xcode/version/build and SDK versions, compiles and links ARM64
device/simulator probes against Apple frameworks and zlib, compiles Metal shaders,
and records SDKs, simulator devices, Xcode export help, Mach-O load commands and
runner version. Failures still upload evidence. It needs no proprietary assets
or signing credentials. No simulated build success is accepted.

`ios/toolchain.json` pins macOS runner/Xcode/SDK/deployment target. If the runner
removes that Xcode, explicitly verify and review a toolchain update; no fallback.
Actions are pinned to commits and no packages are installed during preflight.
The hosted image is mutable, so record its version; source/toolchain reproduction
is the goal, not bit-for-bit signed artifacts.

## Future build/export stages

1. Verify source/dependency manifests and SDK; generate the deterministic Xcode
   project; build tests and simulator target without distribution credentials.
2. Build device engine and inspect ARM64 Mach-O/deployment target/frameworks.
3. If credentials are present in an authorized trusted job, validate certificate
   identity/private key, profile signature/expiry/team/app identifier, export
   method, entitlements and device eligibility **before** archiving.
4. Import identity into an ephemeral keychain and install the matching profile.
   Archive using explicit manual signing and a real application scheme/Info.plist.
5. Export using `xcodebuild -exportArchive` and an ExportOptions.plist generated
   for that verified Xcode/profile. Do not guess deprecated export-method strings.
6. Inspect extracted IPA `Payload/*.app`, executable architecture/load commands,
   embedded profile, signature and entitlements; verify bundle/team consistency.
   Publish IPA, dSYM, build-input checksums and corresponding source/notices.
7. Delete temporary signing material on success/failure. Never expose keys in
   diagnostics. Secrets only in a trusted manual/restricted-branch signing job,
   never an untrusted pull-request build. No proprietary data in public artifacts.

These stages are the Phase 22 implementation contract; an engine IPA workflow
does not exist yet. A simulator application cannot be exported as a device IPA.
An unsigned archive and manually zipped Payload cannot prove an installable IPA.
If raw unsigned packaging is later demonstrated, label it diagnostic and verify
it separately; it does not satisfy the signed delivery acceptance gate.

## Signing options and proposed credentials

Preferred route: manual registered-device distribution using an Apple signing
identity, its private key and a matching provisioning profile. Account membership,
available certificate types and registered devices must be verified. A profile
and certificate can expire or mismatch; merely populating secrets is insufficient.

| Proposed GitHub secret/variable | Meaning |
| --- | --- |
| `IOS_CERTIFICATE_P12_BASE64` (secret) | Signing certificate **and private key**, PKCS#12 encoded as base64 |
| `IOS_CERTIFICATE_PASSWORD` (secret) | PKCS#12 import password |
| `IOS_PROVISIONING_PROFILE_BASE64` (secret) | Apple-issued profile matching selected app/team/export route |
| `IOS_TEAM_ID` (variable) | Actual Apple team identifier, validated against profile/identity |
| `IOS_BUNDLE_ID` (variable) | Registered app identifier matching the profile; no placeholder at export |
| `IOS_EXPORT_METHOD` (variable) | Method obtained from pinned Xcode help and matched to profile type |

An authorized Apple API/account connection may permit automation of identifiers,
certificate/profile creation and renewal. API key permissions and private signing
key availability must be verified; an API key alone is not assumed sufficient.
TestFlight/App Store submission is a separate optional path requiring account,
policy/license compatibility and current SDK requirements; do not claim approval.
No user Apple credential is requested in Phase 01.

## Primary references checked 2026-10-15

- [Apple command-line build/archive/export](https://developer.apple.com/library/archive/technotes/tn2339/_index.html)
- [Apple distribution to registered devices](https://developer.apple.com/documentation/xcode/distributing-your-app-to-registered-devices)
- [Apple manual signing](https://help.apple.com/xcode/mac/current/en.lproj/dev1bf96f17e.html)
- [Apple distribution signing](https://help.apple.com/xcode/mac/current/en.lproj/devcac6ab5b3.html)
- [Apple signing identity/private key sharing](https://developer.apple.com/documentation/xcode/sharing-your-teams-signing-certificates)
- [GitHub secrets](https://docs.github.com/en/actions/how-tos/write-workflows/choose-what-workflows-do/use-secrets)
- [GitHub macOS runner software](https://github.com/actions/runner-images/blob/main/images/macos/macos-15-Readme.md)
