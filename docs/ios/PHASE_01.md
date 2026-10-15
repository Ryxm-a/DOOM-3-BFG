# Phase 01 evidence — 2026-10-15

Scope: repository inventory/triage, phased implementation plan, asset/signing
requirements, and Apple SDK CI preflight preparation. This phase does not port
engine code or establish an iOS build. All existing upstream blobs are unchanged.

## Produced

- `GPT.MD`: 23 phases, one completion per session, acceptance criteria, blockers,
  technical decisions and handoff; `AGENTS.md` requires future sessions to read it.
- `docs/ios/upstream-audit.json`: every upstream blob hashed and classified, all
  text mechanically screened, eight Windows project source/reference inventories.
- `scripts/ios/audit_repository.py`: deterministic, standard-library-only baseline
  inventory and check mode, reading Git blobs rather than converted checkout bytes.
- `ios/toolchain.json`, `scripts/ios/preflight.py`, and
  `.github/workflows/ios-preflight.yml`: explicit Xcode/SDK selection, ARM64
  device/simulator compile/link probes and Metal compilation, failed-run evidence.
- Asset intake, SDK/build/signing requirements and researched primary references
  in `ASSETS.md`, `BUILD_REQUIREMENTS.md` and `AUDIT.md`.
- Ignore rules for existing IDE state, generated output and private inputs. No
  existing `.vs` file was deleted or added to Git.

## Executed validation

Environment: Windows / PowerShell, Python 3.12.

| Check | Result |
| --- | --- |
| `python scripts/ios/audit_repository.py` | PASS: inventory generated from upstream revision |
| `python scripts/ios/audit_repository.py --check` | PASS: byte-for-byte regenerated JSON |
| Independent `git ls-tree` path comparison | PASS: exact coverage of all 1,115 upstream files |
| Missing-project invariant | PASS: 68 missing source declarations, all in stale `neo/game.vcxproj` |
| Check mode against a deliberately invalid temporary audit | PASS: rejected with nonzero exit and `Audit differs` message |
| `python -m py_compile scripts/ios/audit_repository.py scripts/ios/preflight.py` | PASS |
| `python scripts/ios/preflight.py` on Windows | Expected FAIL: full Xcode/macOS required; JSON report generated |
| Non-macOS guard with subprocess invocation forbidden | PASS: no SDK command executed, report says failed and IPA unverified |
| `git diff <upstream> --name-only` before staging | Empty: existing tracked files unchanged |
| `git diff --check` | PASS |

Temporary audit/guard verification files were scoped to `artifacts/` and cleaned
by Python TemporaryDirectory. Persistent Windows guard report is ignored at
`artifacts/ios-preflight/preflight.json`. Report failures are intentional guard
evidence and must not be presented as successful Apple SDK validation.

Workflow action commit identities were checked against GitHub's action repositories:
[checkout v4.2.2](https://github.com/actions/checkout/commit/11bd71901bbe5b1630ceea73d27597364c9af683),
[upload-artifact pin](https://github.com/actions/upload-artifact/commit/ea165f8d65b6e75b540449e92b4886f43607fa02).
Workflow structure was reviewed locally; no local YAML parser/actionlint was
available. Actual GitHub workflow acceptance/execution remains Phase 02 work.

## Unverified and next session

No workflow was pushed/dispatched. No writable remote/authenticated GitHub access
was established. No Xcode project, engine Apple build, app archive, IPA or physical
device test exists yet. Apple framework/Metal probe compilation will be validated
on the runner, not inferred from documentation. No signed or unsigned IPA
generation capability is claimed.

Phase 02 starts by establishing authorized GitHub access, creating/using a writable
fork, running the preflight and fixing real macOS errors. It then adds the native
app build harness with device/simulator evidence. Assets and Apple signing
credentials are not needed for that phase. Preserve this baseline and all original
Windows code while adding Apple sources conditionally in subsequent phases.
