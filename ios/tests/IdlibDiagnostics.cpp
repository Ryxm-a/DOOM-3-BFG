// SPDX-License-Identifier: GPL-3.0-or-later
// Fixture-only idLib diagnostic provider. Engine builds use Lib.cpp/common.
// Selected algorithms remain the real upstream implementations.
#include "../../neo/sys/ios/IdlibCore.h"

void idLib::Printf(const char *format, ...) {
    va_list args;
    va_start(args, format);
    vfprintf(stdout, format, args);
    va_end(args);
}
void idLib::Warning(const char *format, ...) {
    va_list args;
    va_start(args, format);
    vfprintf(stderr, format, args);
    va_end(args);
}
void idLib::Error(const char *format, ...) {
    va_list args;
    va_start(args, format);
    vfprintf(stderr, format, args);
    va_end(args);
    abort();
}
void idLib::FatalError(const char *format, ...) {
    va_list args;
    va_start(args, format);
    vfprintf(stderr, format, args);
    va_end(args);
    abort();
}
