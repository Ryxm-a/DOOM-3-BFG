// SPDX-License-Identifier: GPL-3.0-or-later
#include "../../neo/sys/ios/IdlibCore.h"

static void Require(bool value) {
    if (!value) { AssertFailed(__FILE__, __LINE__, "core fixture failed"); }
}

extern "C" const char *BFG_RunCoreTests() {
    static_assert(sizeof(void *) == 8 && sizeof(uint32) == 4 && sizeof(int64) == 8, "ABI widths");
    static_assert(sizeof(long) == 8, "Apple LP64 must not masquerade as Windows LLP64");
    static_assert(alignof(max_align_t) <= 16, "Default allocator alignment");
    const uint32 endian = 0x12345678;
    Require(reinterpret_cast<const byte *>(&endian)[0] == 0x78);
    uint32 swapped = endian;
    idSwap::Big(swapped);
    Require(swapped == 0x78563412);
    idSwap::Big(swapped);
    Require(swapped == endian);
    idSwap::Little(swapped);
    Require(swapped == endian);
    uint64 wide = 0x0123456789abcdefULL;
    idSwap::Big(wide);
    Require(wide == 0xefcdab8967452301ULL);
    Require((reinterpret_cast<uintptr_t>(_alloca16(77)) & 15) == 0);
    Require((reinterpret_cast<uintptr_t>(_alloca128(129)) & 127) == 0);

    Require(Mem_Alloc16(0, TAG_TEMP) == nullptr);
    Mem_Free16(nullptr);
    for (int size = 1; size <= 4097; size += 17) {
        byte *bytes = static_cast<byte *>(Mem_ClearedAlloc(size, TAG_TEMP));
        Require((reinterpret_cast<uintptr_t>(bytes) & 15) == 0);
        for (int i = 0; i < size; ++i) { Require(bytes[i] == 0); bytes[i] = static_cast<byte>(i); }
        Mem_Free16(bytes);
    }
    struct alignas(128) Wide { byte bytes[128]; };
    Wide *aligned = new Wide;
    Require((reinterpret_cast<uintptr_t>(aligned) & 127) == 0);
    delete aligned;
    int *tagged = new (TAG_TEMP) int[513];
    tagged[512] = 4711;
    Require(tagged[512] == 4711 && (reinterpret_cast<uintptr_t>(tagged) & 15) == 0);
    delete[] tagged;
    char *copy = Mem_CopyString("BFG core");
    Require(strlen(copy) == 8 && memcmp(copy, "BFG core", 9) == 0);
    Mem_Free16(copy);

    idList<int> list;
    for (int i = 255; i >= 0; --i) { list.Append(i); }
    Require(list.Num() == 256);
    list.SortWithTemplate(idSort_QuickDefault<int>());
    for (int i = 0; i < list.Num(); ++i) { Require(list[i] == i); }
    list.RemoveIndex(17);
    Require(list.Num() == 255 && list[17] == 18);
    idList<int> duplicate = list;
    list.Clear();
    Require(duplicate.Num() == 255 && duplicate[254] == 255);

    Require(CRC32_BlockChecksum("123456789", 9) == 0xcbf43926UL);
    unsigned long crc;
    CRC32_InitChecksum(crc);
    CRC32_UpdateChecksum(crc, "1234", 4);
    CRC32_UpdateChecksum(crc, "56789", 5);
    CRC32_FinishChecksum(crc);
    Require(crc == 0xcbf43926UL);
    // RFC 1320 digests, folded as the engine's four little-endian 32-bit words.
    struct MD4Vector { const char *text; uint32 words[4]; };
    const MD4Vector md4[] = {
        {"", {0xe0cfd631, 0x31e96ad1, 0xd7593cb7, 0xc089c0e0}},
        {"a", {0xb32ce5bd, 0x463ee31d, 0xfb055e24, 0x24fbd6db}},
        {"abc", {0x7a0148a4, 0x52d821af, 0xe80ac15f, 0x9d72a67a}}
    };
    for (const auto &vector : md4) {
        const uint32 expected = vector.words[0] ^ vector.words[1] ^ vector.words[2] ^ vector.words[3];
        Require(MD4_BlockChecksum(vector.text, static_cast<int>(strlen(vector.text))) == expected);
    }
    // RFC 1321 digest of abc; also verify incremental update across block boundaries.
    const byte expectedMD5[16] = {0x90,0x01,0x50,0x98,0x3c,0xd2,0x4f,0xb0,0xd6,0x96,0x3f,0x7d,0x28,0xe1,0x7f,0x72};
    MD5_CTX ctx;
    MD5_Init(&ctx);
    MD5_Update(&ctx, reinterpret_cast<const byte *>("a"), 1);
    MD5_Update(&ctx, reinterpret_cast<const byte *>("bc"), 2);
    byte digest[16];
    MD5_Final(&ctx, digest);
    Require(memcmp(digest, expectedMD5, 16) == 0);
    byte block[257];
    for (int i = 0; i < 257; ++i) { block[i] = static_cast<byte>(i); }
    MD5_Init(&ctx);
    MD5_Update(&ctx, block, 257);
    MD5_Final(&ctx, digest);
    byte splitDigest[16];
    MD5_Init(&ctx);
    for (int i = 0; i < 257; ++i) { MD5_Update(&ctx, block + i, 1); }
    MD5_Final(&ctx, splitDigest);
    Require(memcmp(digest, splitDigest, 16) == 0);
    return "{\"phase\":\"03a\",\"status\":\"passed\",\"checks\":[\"abi\",\"endian\",\"allocation\",\"list-sort\",\"crc32\",\"md4-rfc1320\",\"md5-rfc1321\"]}";
}
