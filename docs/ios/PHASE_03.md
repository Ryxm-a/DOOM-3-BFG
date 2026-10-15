# Phase 03 evidence — 2026-10-15

Phase 03 is **COMPLETE**: both 03a and 03b passed actual macOS CI.
The user authorized continuous phases in this chat on 2026-10-15.

## 03a implementation and review

Conditional Apple platform branch: `sys_defines.h`, `sys_includes.h`,
`sys_assert.h`, `sys_types.h`; ARM64 iOS device/simulator only, Metal platform
selection, portable alignment/inlining/stack allocation, standard native nullptr,
Clang unreachable and assertions without MSVC analysis intrinsics. There are no
aliases that pretend Windows ABI types have Apple representations.

Standalone compile boundary in `IdlibCore.h` selected by
`ID_IOS_CORE_LIBRARY` in `precompiled.h`. It imports no engine framework,
renderer, audio or threading backend. `AppleHeap.cpp` supplies POSIX aligned
allocation and out-of-line global C++ new/delete, including C++17 over-alignment.
`AppleAssertions.cpp` reports failed assertions and aborts instead of silently
ignoring them. `Heap.h` retains Windows inline new/delete under its original path.

Reviewed actual checksum implementations: CRC32's public `unsigned long` API
is retained (its 32-bit values are zero-extended on LP64); MD5 already uses
32-bit words; MD4 required an Apple conditional 32-bit word and digest-buffer
fix. Windows MD4 types remain unchanged. Original bundled notices are retained.
MD4 is derived from the RSA Data Security, Inc. MD4 Message-Digest Algorithm.

Fixtures in `ios/tests/CoreTests.cpp` use the actual engine implementations:
ABI widths; native endian and 32/64-bit swaps; 16/128-byte stack alignment;
zero-size/null-free semantics, 241 zeroed allocation sizes, tagged allocation,
over-aligned C++ allocation; deep-copy/list growth/sort/removal; CRC32 known and
incremental vectors; three [RFC 1320](https://www.rfc-editor.org/rfc/rfc1320.html)
MD4 folded checksums; [RFC 1321](https://www.rfc-editor.org/rfc/rfc1321.html)
MD5 abc digest and 257-byte whole-vs-bytewise updates.

Container review covers the exercised List allocation/growth/copy/remove and
QuickDefault sorting paths, Heap tagged allocation operators and actual Apple
heap backend. Heap's other dynamic/block allocator templates are parsed but are
not yet claimed as semantically verified; BTree is a transitive dependency.
Math/SIMD, strings/hash-index, threads, and engine lifecycle are excluded from
03a. The immutable full-file inventory remains checked against the original
upstream revision; platform edits do not rewrite that historical inventory.

The diagnostic app now links selected idlib utilities, calls fixtures before
writing its simulator launch receipt, and reports explicit fixture results.
The complete engine remains unlinked. Its source manifest remains explicit.
Phase 02's immutable two-device run remains evidence for its original scope;
03a requests iPhone runtime fixtures and ARM64 device/simulator compilation.

## 03a verification — PASS

Windows generation check, upstream audit regeneration check, Python syntax,
and diff whitespace checks passed before commit `6366dd0`.
Actual macOS run:
[38661613413](https://github.com/Ryxm-a/DOOM-3-BFG/actions/runs/38661613413).
The run completed successfully. Downloaded `harness.json` confirms ARM64 device
and simulator builds and an iPhone iOS 18.5 launch receipt whose `core_tests`
reports passed ABI, endian, allocation, list-sort, CRC32, MD4-RFC1320 and
MD5-RFC1321 fixtures. `preflight.json` also passes. The full Phase 03 gate
remains open pending 03b.

03a harness artifact: [11939930318](https://github.com/Ryxm-a/DOOM-3-BFG/actions/runs/38661613413/artifacts/11939930318),
SHA-256 `9bca1841bbbc96fec0e6b43a75df109f23b681eac7527a6d229b0a6e02b11ba8`.
SDK artifact: [11939915427](https://github.com/Ryxm-a/DOOM-3-BFG/actions/runs/38661613413/artifacts/11939915427),
SHA-256 `f304f603ea5bbcab2296a383f93af6d4f96bd2ac98f5293f4d2d6f28e73e6589`.
Actual source: `6366dd0ff7d8ec297a1d7b711a8db4dbbc5e69dd`; Xcode 16.4/16F6,
both SDKs/runtime 18.5, macos-15-arm64 image 20260907.0337.1, OS 15.7.9/24G830.

03b follows after the 03a gate: core strings and hash-index fixtures, with
framework diagnostics separated only as necessary for a standalone core build.

## 03b implementation — verification pending

The manifest now compiles upstream `Str.cpp` and `containers/HashIndex.cpp`.
The core boundary imports the actual `idLib` declarations from `Lib.h` while
conditionally omitting its avalanche of unrelated headers. Selected original
Math/Vector headers supply the real types required by string colours and
vector hash keys; this does not compile or verify the full math library yet.
Apple `ID_TLS` uses C++ `thread_local ptrdiff_t`; only declarations are used in
this phase, and TLS/thread lifecycle stress remains Phase 05.

String diagnostics call existing `idLib` wrappers to avoid depending directly
on the `idCommon` class. `ios/tests/IdlibDiagnostics.cpp` is an explicit fixture
provider for those diagnostics, logging to stdio and aborting on fatal/error.
It is not a production engine service and must be excluded when `Lib.cpp` and
the framework are integrated. The framework-only `testStrId` console/localization
command is explicitly excluded from the core build; all string algorithms and
the hash-index implementation are real upstream code.

Apple formatting uses bounded C99 `vsnprintf` with the engine's -1-on-truncation
contract for `vsnPrintf`, including size 0/null and size 1 guards. `snPrintf`'s
temporary buffer and `va` are bounded on Apple. Windows-specific formatting
branches remain intact. `va`'s rotating static buffers are still not thread-safe;
concurrency review remains Phase 05.

Added fixtures: 404-byte string growth/deep copy/alias assignment; searches and
case comparisons/hash; path joining/extensions/basename; varargs formatting;
exact-fit/truncation/size-one/size-zero/null with destination guard bytes;
400 hash-index entries exercising growth/collisions, traversal, removal and copy.
The core fixture assertions now print the exact failing expression and line.

Local generation/audit/Python syntax/whitespace checks pass. Actual run at
`9e24730c8d3583c8d35b16e745450fae39dc9ee5`:
[38662472580](https://github.com/Ryxm-a/DOOM-3-BFG/actions/runs/38662472580).
No compile/runtime success is claimed here until its evidence is inspected.

Run 38662472580 failed the runtime gate: both ARM64 builds and metadata checks
passed, simulator boot/install/launch returned success, but no fixture receipt
was written. Phase 03 remains OPEN. Its report did not capture app stdio; added
explicit stdout/stderr redirection and app-filtered simulator/crash diagnostics
on missing receipts to identify and repair the actual runtime failure. No tests
were weakened or removed.

Source inspection then found a concrete ownership defect in the exercised path:
`idHashIndex` has deep-copy assignment but no copy constructor, so copy
construction aliases both owning buffers. The fixture frees the original and
later destroys the copy, exposing use-after-free/double-free. Added an Apple-only
copy constructor that initializes an empty index and invokes existing deep-copy
assignment; Windows's original constructor path is preserved. The unchanged
fixture plus new diagnostics must pass a fresh CI run before 03b closes.

Corrective run at `fe5505e95c610cab72a55f2aebb6fc52c27f7184`:
[38663205426](https://github.com/Ryxm-a/DOOM-3-BFG/actions/runs/38663205426).
This run includes the unchanged fixtures and diagnostic capture; result pending.

Run 38663205426 compiled successfully but timed out inside simctl launch with
`--stdout/--stderr` before creating console files. Replaced that capture method
with a managed, blocking `--console` process whose host stdio files are opened
by Python. Receipt wait is bounded at 120 seconds for cold simulator startup;
the full nonce/fixture/terminate requirements remain. Failure diagnostics now
also cover launch-time errors. No passing runtime gate is inferred from this run.

Managed-console run at `47c8b944ddd1058a576c82109532e2a6036aa3e1`:
[38664303363](https://github.com/Ryxm-a/DOOM-3-BFG/actions/runs/38664303363), pending.

## Final 03b gate — PASS

Run [38664303363](https://github.com/Ryxm-a/DOOM-3-BFG/actions/runs/38664303363)
at `47c8b944ddd1058a576c82109532e2a6036aa3e1` completed successfully.
Downloaded reports confirm both ARM64 products, IOS/IOSSIMULATOR metadata,
minimum deployment 15.0, and an iPhone iOS 18.5 nonce receipt with all ten groups
passed: ABI, endian, allocation, list-sort, CRC32, MD4-RFC1320, MD5-RFC1321,
strings, bounded-format, hash-index. Console capture is retained; stderr is empty.
Xcode 16.4/16F6, SDK/runtime 18.5; runner macos-15-arm64 image 20260907.0337.1,
macOS 15.7.9/24G830. Local generation/guard checks also pass.

- [Harness artifact 11940741360](https://github.com/Ryxm-a/DOOM-3-BFG/actions/runs/38664303363/artifacts/11940741360):
  SHA-256 `1ed6576414650d4950ed2e54fb3d91d95d304543f8b159343356417e1f884d17`.
- [SDK artifact 11940751418](https://github.com/Ryxm-a/DOOM-3-BFG/actions/runs/38664303363/artifacts/11940751418):
  SHA-256 `47cc7dfcbb37c1f705f8d0ea6b26a1ad987e126afabe5c4b1c8da4bb2812265a`.

Both downloaded ZIP digests match GitHub metadata. Retention is 14 days; local
evidence is under ignored `artifacts/phase02/38664303363/`. Earlier failure and
correction history above is retained as evidence, superseded by this final pass.
The diagnostic-only run 38663102270 was cancelled when the ownership fix was
pushed; it is not passing evidence. No fixture was weakened or removed.

Reviewed Str allocation/copy/aliasing, searches/comparison/path helpers,
formatting and UTF-8 routines; HashIndex allocation/resizing/chains/removal and
ownership. Runtime coverage is the explicit fixture list, not exhaustive Unicode,
concurrency, allocator-template or engine validation. Windows targets were not
built here. Fixture diagnostics and the excluded localization console command
must be integrated with real framework services in later phases.

Proceed directly to Phase 04 under the continuous-work authorization. No complete
engine, renderer, asset-dependent execution, signing or IPA has been verified.
