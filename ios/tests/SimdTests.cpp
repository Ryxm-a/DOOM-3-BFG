// SPDX-License-Identifier: GPL-3.0-or-later
// Include the actual minimal job header first to verify its standalone boundary.
#include "../../neo/idlib/ParallelJobList_JobHeaders.h"
#include "../../neo/sys/ios/IdlibCore.h"

#define RequireSimd(value) ((value) ? (void)0 : (void)AssertFailed(__FILE__, __LINE__, #value))
static bool NearSimd(float a, float b) { return fabsf(a - b) < 0.0001f; }

extern "C" const char *BFG_RunSimdTests() {
    static_assert(sizeof(idDrawVert) == 32 && sizeof(idJointMat) == 48 && sizeof(idJointQuat) == 32, "GPU input layouts");
    static_assert(sizeof(jobRun_t) == 8 && sizeof(idParallelJobList) == 16 && MAX_JOBLISTS == 32, "ARM64 job interface layout");
    static_assert(sizeof(idRandom2) == 4, "The LCG state is 32-bit on LP64");
    idSIMD::Init();
    RequireSimd(SIMDProcessor != nullptr && idStr::Cmp(SIMDProcessor->GetName(), "generic code") == 0);
    const int expectedRandom[] = {13162, 3555, 9672, 26921, 19158};
    const int expectedRandom2[] = {8712, 24007, 122, 5521, 20924};
    idRandom random(13);
    idRandom2 random2(13);
    for (int i = 0; i < 5; ++i) {
        RequireSimd(random.RandomInt() == expectedRandom[i]);
        RequireSimd(random2.RandomInt() == expectedRandom2[i]);
    }
    random2.SetSeed(13);
    const float randomFloat = random2.RandomFloat();
    RequireSimd(randomFloat >= 0.0f && randomFloat < 1.0f && random2.GetSeed() <= 0xffffffffUL);

    byte input[257], storage[259];
    float values[257];
    for (int i = 0; i < 257; ++i) { input[i] = static_cast<byte>(i); values[i] = static_cast<float>((i * 17) % 61 - 30); }
    const int counts[] = {1, 2, 3, 7, 15, 16, 17, 31, 33, 257};
    for (int count : counts) {
        memset(storage, 0xdd, sizeof(storage));
        SIMDProcessor->Memcpy(storage + 1, input, count);
        RequireSimd(memcmp(storage + 1, input, count) == 0 && storage[0] == 0xdd && storage[count + 1] == 0xdd);
        SIMDProcessor->Memset(storage + 1, 0x5a, count);
        for (int i = 1; i <= count; ++i) { RequireSimd(storage[i] == 0x5a); }
        RequireSimd(storage[0] == 0xdd && storage[count + 1] == 0xdd);
        float minimum, maximum;
        SIMDProcessor->MinMax(minimum, maximum, values, count);
        float referenceMin = values[0], referenceMax = values[0];
        for (int i = 1; i < count; ++i) { if (values[i] < referenceMin) referenceMin = values[i]; if (values[i] > referenceMax) referenceMax = values[i]; }
        RequireSimd(minimum == referenceMin && maximum == referenceMax);
    }
    const idVec3 points[] = {idVec3(1,2,3), idVec3(-4,5,0), idVec3(3,-2,9), idVec3(0,10,-1), idVec3(2,0,4)};
    idVec3 minimum, maximum;
    SIMDProcessor->MinMax(minimum, maximum, points, 5);
    RequireSimd(minimum.Compare(idVec3(-4,-2,-1)) && maximum.Compare(idVec3(3,10,9)));
    idVec2 points2[5];
    for (int i = 0; i < 5; ++i) { points2[i].Set(points[i].x, points[i].y); }
    idVec2 minimum2, maximum2;
    SIMDProcessor->MinMax(minimum2, maximum2, points2, 5);
    RequireSimd(minimum2.Compare(idVec2(-4,-2)) && maximum2.Compare(idVec2(3,10)));
    idBounds bounds;
    bounds.FromPoints(points, 5);
    RequireSimd(bounds[0].Compare(minimum) && bounds[1].Compare(maximum));

    alignas(16) idDrawVert vertices[5], copiedVertices[5];
    for (int i = 0; i < 5; ++i) {
        vertices[i].Clear(); vertices[i].xyz = points[i];
        vertices[i].SetTexCoord(1.0f, 0.5f);
        vertices[i].SetNormal(0,0,1); vertices[i].SetTangent(1,0,0);
        vertices[i].SetBiTangentSign(-1.0f);
        vertices[i].SetColor(0x44332211u); vertices[i].SetColor2(0x88776655u);
    }
    SIMDProcessor->MinMax(minimum, maximum, vertices, 5);
    RequireSimd(minimum.Compare(idVec3(-4,-2,-1)) && maximum.Compare(idVec3(3,10,9)));
    const triIndex_t indexes[] = {4, 1, 3};
    SIMDProcessor->MinMax(minimum, maximum, vertices, indexes, 3);
    RequireSimd(minimum.Compare(idVec3(-4,0,-1)) && maximum.Compare(idVec3(2,10,4)));
    WriteDrawVerts16(copiedVertices, vertices, 5);
    RequireSimd(memcmp(vertices, copiedVertices, sizeof(vertices)) == 0);
    RequireSimd(vertices[0].st[0] == 0x3c00 && vertices[0].st[1] == 0x3800);
    RequireSimd(vertices[0].normal[0] == 128 && vertices[0].normal[1] == 128 && vertices[0].normal[2] == 255);
    RequireSimd(vertices[0].color[0] == 0x11 && vertices[0].color[3] == 0x44 && vertices[0].GetBiTangentSign() == -1.0f);
    RequireSimd(F16toF32(0x3c00) == 1.0f && F32toF16(-2.0f) == 0xc000);
    idSwap::Big(copiedVertices[0]); idSwap::Big(copiedVertices[0]);
    RequireSimd(memcmp(vertices, copiedVertices, sizeof(vertices)) == 0);
    idShadowVert shadows[10];
    RequireSimd(idShadowVert::CreateShadowCache(shadows, vertices, 5) == 10);
    for (int i = 0; i < 5; ++i) {
        RequireSimd(shadows[2*i].xyzw.ToVec3().Compare(points[i]) && shadows[2*i].xyzw[3] == 1.0f);
        RequireSimd(shadows[2*i+1].xyzw.ToVec3().Compare(points[i]) && shadows[2*i+1].xyzw[3] == 0.0f);
    }

    idJointQuat start, end;
    start.q = idQuat(0,0,0,1); start.t = idVec3(0,0,0); start.w = 0;
    end.q = idAngles(0,90,0).ToQuat(); end.t = idVec3(4,8,12); end.w = 0;
    const int jointIndex[] = {0};
    idJointQuat blended = start;
    SIMDProcessor->BlendJoints(&blended, &end, 0.5f, jointIndex, 1);
    RequireSimd(blended.t.Compare(idVec3(2,4,6)));
    RequireSimd((blended.q.ToMat3() * idVec3(1,0,0)).Compare(idVec3(0.70710678f,0.70710678f,0), 0.0001f));
    blended = start;
    SIMDProcessor->BlendJointsFast(&blended, &end, 0.5f, jointIndex, 1);
    RequireSimd((blended.q.ToMat3() * idVec3(1,0,0)).Compare(idVec3(0.70710678f,0.70710678f,0), 0.0001f));
    idJointQuat joints[2];
    joints[0] = end; joints[0].t = idVec3(10,0,0);
    joints[1] = start; joints[1].t = idVec3(1,0,0);
    idJointMat matrices[2];
    SIMDProcessor->ConvertJointQuatsToJointMats(matrices, joints, 2);
    idJointQuat roundTrip[2];
    SIMDProcessor->ConvertJointMatsToJointQuats(roundTrip, matrices, 2);
    RequireSimd(roundTrip[0].t.Compare(joints[0].t) && roundTrip[0].q.ToMat3().Compare(joints[0].q.ToMat3(), 0.0001f));
    const int parents[] = {-1,0};
    SIMDProcessor->TransformJoints(matrices, parents, 1, 1);
    RequireSimd(matrices[1].GetTranslation().Compare(idVec3(10,1,0), 0.0001f));
    SIMDProcessor->UntransformJoints(matrices, parents, 1, 1);
    RequireSimd(matrices[1].GetTranslation().Compare(idVec3(1,0,0), 0.0001f));

    idVecX vector(4);
    for (int i = 0; i < 4; ++i) vector[i] = static_cast<float>(i+1);
    idVecX copiedVector = vector;
    vector[0] = 100;
    RequireSimd(copiedVector[0] == 1);
    idMatX matrix;
    matrix.Zero(4,4);
    matrix[0][0]=4; matrix[0][1]=matrix[1][0]=1; matrix[0][2]=matrix[2][0]=1;
    matrix[1][1]=3; matrix[2][2]=2; matrix[3][3]=5;
    idVecX rhs(4), solution(4);
    rhs[0]=9; rhs[1]=7; rhs[2]=7; rhs[3]=20;
    idMatX factor = matrix;
    RequireSimd(factor.Cholesky_Factor());
    factor.Cholesky_Solve(solution, rhs);
    for (int i = 0; i < 4; ++i) RequireSimd(NearSimd(solution[i], static_cast<float>(i+1)));
    idMatX inverse = matrix;
    RequireSimd(inverse.InverseSelf());
    const idMatX identity = matrix * inverse;
    RequireSimd(identity.IsIdentity(0.0001f));
    idVecX low(4), high(4);
    for (int i = 0; i < 4; ++i) { low[i]=-idMath::INFINITY; high[i]=idMath::INFINITY; }
    idLCP::SetShowFailures(false);
    for (int kind = 0; kind < 2; ++kind) {
        idLCP *solver = kind == 0 ? idLCP::AllocSquare() : idLCP::AllocSymmetric();
        RequireSimd(solver->Solve(matrix, solution, rhs, low, high));
        for (int i = 0; i < 4; ++i) RequireSimd(NearSimd(solution[i], static_cast<float>(i+1)));
        high[3] = 3;
        RequireSimd(solver->Solve(matrix, solution, rhs, low, high));
        RequireSimd(NearSimd(solution[3], 3));
        high[3] = idMath::INFINITY;
        delete solver;
    }
    idRenderMatrix product;
    idRenderMatrix::Multiply(renderMatrix_identity, renderMatrix_flipToOpenGL, product);
    idVec3 transformed;
    product.TransformPoint(idVec3(1,2,3), transformed);
    RequireSimd(transformed.Compare(idVec3(-2,3,-1)));
    idSIMD::Shutdown();
    RequireSimd(SIMDProcessor == nullptr);
    return "{\"phase\":\"04b\",\"status\":\"passed\",\"checks\":[\"generic-memory-minmax\",\"joint-reference\",\"dynamic-math-lcp\",\"vertex-layout\",\"rng-32\",\"job-data\"]}";
}
