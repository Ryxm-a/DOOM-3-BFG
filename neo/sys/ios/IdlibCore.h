// SPDX-License-Identifier: GPL-3.0-or-later
// Standalone idlib compile boundary. No framework/renderer/thread substitutes.
#ifndef ID_IOS_IDLIB_CORE_H
#define ID_IOS_IDLIB_CORE_H
#include "../../idlib/sys/sys_defines.h"
#include "../../idlib/sys/sys_includes.h"
#include "../../idlib/sys/sys_assert.h"
#include "../../idlib/sys/sys_types.h"
#include "../../idlib/Lib.h"
#include "../../idlib/Heap.h"
#include "../../idlib/containers/Sort.h"
#include "../../idlib/containers/List.h"
#include "../../idlib/math/Math.h"
#include "../../idlib/math/Vector.h"
class idCmdArgs;
#include "../../idlib/Str.h"
#include "../../idlib/containers/HashIndex.h"
#include "../../idlib/hashing/CRC32.h"
#include "../../idlib/hashing/MD4.h"
#include "../../idlib/hashing/MD5.h"
#define ID_SWAP_LITE
#include "../../idlib/Swap.h"
#endif
