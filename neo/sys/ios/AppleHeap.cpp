// SPDX-License-Identifier: GPL-3.0-or-later
#include "IdlibCore.h"
#include <limits>

static void *AllocateAligned(size_t size, size_t alignment) {
    void *result = nullptr;
    if (posix_memalign(&result, alignment, size == 0 ? 1 : size) != 0) {
        throw std::bad_alloc();
    }
    return result;
}

void *Mem_Alloc16(const int size, const memTag_t tag) {
    (void)tag;
    if (size < 0) { std::abort(); }
    return size == 0 ? nullptr : AllocateAligned(static_cast<size_t>(size), 16);
}
void Mem_Free16(void *ptr) { free(ptr); }
void *Mem_ClearedAlloc(const int size, const memTag_t tag) {
    void *result = Mem_Alloc16(size, tag);
    if (result != nullptr) { memset(result, 0, static_cast<size_t>(size)); }
    return result;
}
char *Mem_CopyString(const char *input) {
    const size_t size = strlen(input) + 1;
    if (size > static_cast<size_t>(std::numeric_limits<int>::max())) { throw std::bad_alloc(); }
    char *result = static_cast<char *>(Mem_Alloc16(static_cast<int>(size), TAG_STRING));
    memcpy(result, input, size);
    return result;
}

// Out-of-line replacements keep libc++ declarations and exception specifications.
void *operator new(size_t size) { return AllocateAligned(size, 16); }
void *operator new[](size_t size) { return AllocateAligned(size, 16); }
void operator delete(void *ptr) noexcept { free(ptr); }
void operator delete[](void *ptr) noexcept { free(ptr); }
void operator delete(void *ptr, size_t) noexcept { free(ptr); }
void operator delete[](void *ptr, size_t) noexcept { free(ptr); }
void *operator new(size_t size, std::align_val_t alignment) { return AllocateAligned(size, static_cast<size_t>(alignment)); }
void *operator new[](size_t size, std::align_val_t alignment) { return AllocateAligned(size, static_cast<size_t>(alignment)); }
void operator delete(void *ptr, std::align_val_t) noexcept { free(ptr); }
void operator delete[](void *ptr, std::align_val_t) noexcept { free(ptr); }
void operator delete(void *ptr, size_t, std::align_val_t) noexcept { free(ptr); }
void operator delete[](void *ptr, size_t, std::align_val_t) noexcept { free(ptr); }
