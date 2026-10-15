// SPDX-License-Identifier: GPL-3.0-or-later
// Actual generic CPU dispatch. No SSE emulation or NEON backend is selected.
#include "IdlibCore.h"
#include "../../idlib/math/Simd_Generic.h"

static idSIMD_Generic *genericProcessor = nullptr;
idSIMDProcessor *SIMDProcessor = nullptr;

void idSIMD::Init() {
    if (genericProcessor == nullptr) {
        genericProcessor = new (TAG_MATH) idSIMD_Generic;
        genericProcessor->cpuid = CPUID_GENERIC;
    }
    SIMDProcessor = genericProcessor;
}

void idSIMD::InitProcessor(const char *module, bool forceGeneric) {
    (void)forceGeneric; // Generic is the only validated Apple implementation.
    Init();
    idLib::Printf("%s using %s for SIMD processing\n", module, SIMDProcessor->GetName());
}

void idSIMD::Shutdown() {
    delete genericProcessor;
    genericProcessor = nullptr;
    SIMDProcessor = nullptr;
}

void idSIMD::Test_f(const idCmdArgs &args) {
    (void)args;
    Init();
    const float values[] = {-2.0f, 0.0f, 3.0f};
    float minimum, maximum;
    SIMDProcessor->MinMax(minimum, maximum, values, 3);
    release_assert(minimum == -2.0f && maximum == 3.0f);
    idLib::Printf("Apple generic SIMD MinMax check passed\n");
}
