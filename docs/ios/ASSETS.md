# Private BFG game assets

## When and where

Assets are needed at Phase 20, after synthetic fixtures validate most subsystems.
Earlier asset-dependent runtime experiments may be deferred without stopping
source/SDK/build work. Do not upload assets to Git or public workflow artifacts.

Copy the **entire `base` folder from a fully patched PC DOOM 3 BFG Edition
installation**, preserving names, case and subdirectories, to:

`C:\Users\basam\Desktop\DOOM 3\DOOM-3-BFG\private-assets\pc\base\`

Keep the repository's existing `base` directory intact. A private downloadable
archive with a top-level `base/` is an alternative once authenticated asset CI
transport is configured. That workflow must verify a provided SHA-256 and must
not print authenticated URLs. Game data will normally be imported after install,
keeping the public engine IPA separate from proprietary PC data.

## Required content and limits of the current evidence

- BFG `.resources` containers at the `base` root and recursively under maps;
  retain **all** of them, including shared/ordered, PC sound/language, campaign
  map and startup content. The source loads these dynamically; a filename-only
  minimal list cannot be proved without inspecting the supplied installation.
- All accompanying generated image/sound/model/SWF data, materials, maps,
  scripts, definitions, fonts and localization files, whether packed or loose.
  Do not extract only loose files: critical resources may be inside containers.
- Classic content: `base/wads/DOOM.WAD`, `base/wads/DOOM2.WAD`, and
  `base/wads/NERVE.WAD` for the BFG classic games/No Rest for the Living.
  Source references uppercase names; importer must normalize/resolve actual
  case without losing data. WADs packed inside resources must also be accounted for.
- Keep `default.cfg`, `renderprogs` and any supporting files supplied in the PC
  base tree. The engine requires `default.cfg`, which may resolve from a resource
  container; the repository also supplies open-source config/shaders.
- Retain videos if present for inventory. This upstream release cannot decode
  Bink, so initial gameplay must work with an explicit cinematic fallback.

Original DOOM 3 `.pk4` packs are not a substitute for BFG `.resources` data.
PC executables, Steam DLLs, DirectX redistributables, saves, and personal account
files are not required. TNT/Plutonia/Master Levels are optional additional classic
expansions, not required BFG assets.

The full base folder is the exact acquisition boundary for this port. An exact
per-file/runtime-required manifest remains unverified until assets are supplied.
Phase 20 will hash every file, inspect resource indexes and WAD headers, identify
language/campaign coverage, validate endian/compression/audio formats, detect case
collisions and truncation, and produce a private manifest. Public build evidence
must contain no game data. Retain the installation unmodified; conversion outputs
belong in a separate private staging directory.
