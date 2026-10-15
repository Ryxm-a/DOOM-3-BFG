// SPDX-License-Identifier: GPL-3.0-or-later
#include "IdlibCore.h"

bool AssertFailed(const char *file, int line, const char *expression) {
    fprintf(stderr, "Assertion failed: %s:%d: %s\n", file, line, expression);
    abort();
}
