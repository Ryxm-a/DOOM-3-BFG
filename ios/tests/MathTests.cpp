// SPDX-License-Identifier: GPL-3.0-or-later
#include <type_traits>
#include "../../neo/sys/ios/IdlibCore.h"

#define RequireMath(value) ((value) ? (void)0 : (void)AssertFailed(__FILE__, __LINE__, #value))

static bool Near(float value, float expected, float epsilon = 0.0001f) {
    return fabsf(value - expected) <= epsilon;
}

static void ConstantDerivative(float time, const void *user, const float *state, float *derivatives) {
    (void)time; (void)user; (void)state;
    derivatives[0] = 2.0f;
    derivatives[1] = -1.0f;
}

extern "C" const char *BFG_RunMathTests() {
    static_assert(sizeof(idVec3) == 12 && sizeof(idMat3) == 36, "Serialized vector/matrix widths");
    static_assert(sizeof(idQuat) == 16 && sizeof(idPlane) == 16, "Serialized quaternion/plane widths");
    static_assert(offsetof(idVec3, y) == 4 && offsetof(idVec3, z) == 8, "Vector component layout");
    static_assert(!std::is_copy_constructible<idODE_RK4>::value, "ODE owns its working buffers");
    idMath::Init();
    RequireMath(Near(idMath::Sqrt(25.0f), 5.0f));
    RequireMath(Near(idMath::Sin(idMath::HALF_PI), 1.0f));
    RequireMath(Near(idMath::Cos(idMath::PI), -1.0f));
    RequireMath(idMath::Ftoi(3.9f) == 3 && idMath::Ftoi(-3.9f) == -3);
    idVec3 vector(3.0f, 4.0f, 0.0f);
    RequireMath(Near(vector.Normalize(), 5.0f) && Near(vector.Length(), 1.0f));
    const idVec3 cross = idVec3(1, 0, 0).Cross(idVec3(0, 1, 0));
    RequireMath(cross.Compare(idVec3(0, 0, 1), 0.00001f));
    const idMat3 scale(2, 0, 0, 0, 3, 0, 0, 0, 4);
    RequireMath(Near(scale.Determinant(), 24.0f));
    idMat3 inverse = scale;
    RequireMath(inverse.InverseSelf());
    RequireMath((scale * inverse).Compare(mat3_identity, 0.00001f));
    const idMat3 rotation = idAngles(0, 90, 0).ToMat3();
    RequireMath((rotation * idVec3(1, 0, 0)).Compare(idVec3(0, 1, 0), 0.0001f));
    const idQuat quaternion = idAngles(0, 90, 0).ToQuat();
    RequireMath(quaternion.ToMat3().Compare(rotation, 0.0001f));
    RequireMath(Near(quaternion.Length(), 1.0f));
    const idPlane plane(idVec3(0, 0, 1), 2.0f);
    RequireMath(Near(plane.Distance(idVec3(1, 2, 5)), 3.0f));

    idPolynomial polynomial(2.0f, -5.0f, 2.0f);
    float roots[4] = {};
    RequireMath(polynomial.GetRoots(roots) == 2);
    idSort_QuickDefault<float>().Sort(roots, 2);
    RequireMath(Near(roots[0], 0.5f) && Near(roots[1], 2.0f));
    idPolynomial copiedPolynomial = polynomial;
    polynomial[0] = 999.0f;
    RequireMath(Near(copiedPolynomial.GetValue(0.5f), 0.0f));
    idPolynomial assignedPolynomial;
    assignedPolynomial = copiedPolynomial;
    copiedPolynomial[0] = 888.0f;
    RequireMath(Near(assignedPolynomial.GetValue(0.5f), 0.0f));
    const idPolynomial derivative = assignedPolynomial.GetDerivative();
    RequireMath(Near(derivative.GetValue(2.0f), 3.0f));
    const idComplex complex = idComplex(1, 2) * idComplex(3, -4);
    RequireMath(Near(complex.r, 11.0f) && Near(complex.i, 2.0f));
    idODE_RK4 integrator(2, ConstantDerivative, nullptr);
    idODE_Euler euler(2, ConstantDerivative, nullptr);
    idODE_Midpoint midpoint(2, ConstantDerivative, nullptr);
    idODE_RK4Adaptive adaptive(2, ConstantDerivative, nullptr);
    const float state[2] = {1.0f, 3.0f};
    float next[2] = {};
    idODE *integrators[] = {&euler, &midpoint, &integrator, &adaptive};
    for (idODE *method : integrators) {
        method->Evaluate(state, next, 0.0f, 0.5f);
        RequireMath(Near(next[0], 2.0f) && Near(next[1], 2.5f));
    }

    // Exact little-endian IEEE-754 bytes, independent of pointer/long width.
    const idVec3 serialized(1.0f, -2.0f, 0.5f);
    const byte expected[12] = {0,0,0x80,0x3f, 0,0,0,0xc0, 0,0,0,0x3f};
    byte bytes[12];
    memcpy(bytes, serialized.ToFloatPtr(), sizeof(bytes));
    RequireMath(memcmp(bytes, expected, sizeof(bytes)) == 0);
    idVec3 decoded;
    memcpy(decoded.ToFloatPtr(), expected, sizeof(expected));
    RequireMath(decoded.Compare(serialized));
    uint32 fields[3];
    memcpy(fields, bytes, sizeof(fields));
    idSwap::BigArray(fields, 3);
    const byte bigExpected[12] = {0x3f,0x80,0,0, 0xc0,0,0,0, 0x3f,0,0,0};
    RequireMath(memcmp(fields, bigExpected, 12) == 0);
    idSwap::BigArray(fields, 3);
    RequireMath(memcmp(fields, expected, 12) == 0);
    return "{\"phase\":\"04a\",\"status\":\"passed\",\"checks\":[\"scalar-math\",\"vector-matrix\",\"quat-plane\",\"polynomial-ode\",\"serialization\"]}";
}
