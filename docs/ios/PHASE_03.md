# Phase 03 evidence — in progress

Phase 03 remains **OPEN** until both 03a and 03b pass actual macOS CI.
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

03b follows after the 03a gate: core strings and hash-index fixtures, with
framework diagnostics separated only as necessary for a standalone core build.
