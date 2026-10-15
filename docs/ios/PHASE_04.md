# Phase 04 evidence — in progress

Phase 04 remains **OPEN**. Its decomposition was recorded in GPT.MD before
implementation: 04a scalar static library and serialization, then 04b generic
SIMD/bounds/dynamic math/geometry/jobs-data compatibility. Real threading/job
runtime stress remains Phase 05. The complete engine is not linked.

## 04a implementation and review

The deterministic project now has a real `DoomIdlib` static-library target,
`libDoomIdlib.a`, and an app target dependency/link. Explicit `library_sources`
separate actual engine core/math sources from app/fixture/diagnostic sources.
No test diagnostics enter the static archive. Original Windows projects remain
unchanged. Project/source manifests regenerate with Python's standard library.

The library contains the seven Phase 03 sources and eleven additional actual
scalar math sources: Math, Vector, Matrix, Angles, Quat, Rotation, Plane,
Pluecker, Complex, Polynomial, Ode. Their real headers are imported at the
standalone boundary. Bounds, generic SIMD, dynamic matrices/vectors and geometry
are 04b scope. x86 SIMD is not selected in the Apple manifest.

Legacy float/type reinterpretation needs strict aliasing disabled; the project
sets `GCC_STRICT_ALIASING=NO` and `GCC_FAST_MATH=NO`. Actual compiler flags must
be inspected in CI. No fast-math or NEON correctness claim is made.

Semantic review covers scalar initialisation/bit conversions, vector and matrix
layout and selected transformations, quaternion/plane conventions, polynomial
root paths, complex arithmetic and all ODE lifecycles. Review found Midpoint,
RK4 and RK4Adaptive using scalar deletion for float arrays. The Apple branch
now uses `delete[]`; original Windows branches are retained. These are real
upstream algorithms, with no substitute math implementations.

Ownership review also found Polynomial had a coefficient allocation but no
destructor or copy constructor. Apple now has explicit deep-copy construction
and destruction, retaining existing deep-copy assignment. Fixtures mutate copied
and assigned sources to prove independence, then exercise derivative temporaries.
Apple ODE integrators are noncopyable to prevent buffer aliasing; their existing
base API and all Windows branches remain intact.

The new runtime fixtures check square root/trigonometry/truncation; normalising
3-4-5, cross products, diagonal matrix determinant/inverse, yaw rotation and
quaternion/matrix agreement, plane distance, quadratic roots, complex multiply,
all four ODE integrators, and exact little/big-endian IEEE-754 vector bytes.
ABI assertions cover actual vector/matrix/quaternion/plane sizes and components.
Phase 03's ten fixture groups remain enabled as regressions. Receipts retain
separate `core_tests` and `math_tests` results. Verification records each static
archive's architecture, member list and load commands in addition to app metadata.

Local generation/audit/Python syntax/whitespace and Windows guard/stale-project
checks pass. Actual macOS evidence is pending for the current source. No phase
completion, complete idlib/SIMD, engine, renderer, signing or IPA is claimed.
