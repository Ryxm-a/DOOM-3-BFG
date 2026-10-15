"""Inventory and mechanically screen EVERY upstream blob; no third-party packages.

This is a reproducible triage, not a claim that regex proves source portability.
Reads the immutable upstream revision, so generated files cannot alter the baseline.
"""
import argparse
import collections
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import subprocess
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[2]
UPSTREAM = "1caba1979589971b5ed44e315d9ead30b278d8b4"
PATTERNS = {
    "windows_api": r"\b(?:windows\.h|winsock2\.h|HANDLE|DWORD|CRITICAL_SECTION|CreateThread|VirtualAlloc|Interlocked\w*|LoadLibrary\w*|GetProcAddress)\b",
    "msvc_x86": r"\b(?:__declspec|__forceinline|__asm|_mm_\w+|__m128\w*|intrin\.h|UINT_PTR|_alloca)\b",
    "desktop_gl": r"\b(?:wgl\w+|qgl\w+|GL_TEXTURE_RECTANGLE\w*|GL_COMPRESSED_\w+|gl/gl\.h)\b",
    "directx_audio_input": r"\b(?:XAudio2\w*|XAUDIO2\w*|IXAudio2\w*|X3DAudio\w*|XInput\w*|DirectInput\w*|dsound\.h|dinput\.h|xaudio2\.h)\b",
    "filesystem_process": r"\b(?:fopen|mkdir|_mkdir|_findfirst|_findnext|system|WinExec|ShellExecute\w*)\s*\(",
    "asset_formats": r"\.(?:resources|bimage|bsound|bik|wad|pk4)\b",
}
RX = {key: re.compile(value, re.IGNORECASE) for key, value in PATTERNS.items()}


def git(*args):
    return subprocess.check_output(["git", *args], cwd=ROOT)


def subsystem(path):
    if path.startswith("base/"):
        return "shaders-and-config"
    if path.startswith("neo/sys/win32/"):
        return "windows-platform-replace"
    if path.startswith("neo/sound/XAudio2/"):
        return "xaudio-replace"
    if "/jpeg-6/" in path or "/zlib/" in path or path.startswith("doomclassic/timidity/"):
        return "bundled-dependency"
    if path.endswith((".vcxproj", ".filters", ".props", ".sln", ".vcxproj.user")):
        return "windows-build-preserve"
    return "/".join(path.split("/")[:2]) if "/" in path else "root-metadata"


def make_audit(revision=UPSTREAM):
    entries = []
    for item in git("ls-tree", "-r", "-z", revision).split(b"\0"):
        if item:
            meta, path = item.split(b"\t", 1)
            mode, kind, oid = meta.decode().split()
            if kind != "blob":
                raise ValueError("Non-blob upstream entry needs explicit handling")
            entries.append((path.decode("utf-8"), mode, oid))
    # One batch reads every byte from Git, with no checkout newline conversion.
    data = subprocess.check_output(
        ["git", "cat-file", "--batch"], input=("\n".join(e[2] for e in entries) + "\n").encode(), cwd=ROOT)
    offset = 0
    files, texts = [], {}
    for path, mode, oid in entries:
        end = data.index(b"\n", offset)
        header = data[offset:end].decode().split()
        if header[:2] != [oid, "blob"]:
            raise ValueError("Unexpected cat-file response")
        size = int(header[2])
        raw = data[end + 1:end + 1 + size]
        offset = end + size + 2
        binary = b"\0" in raw
        flags = {}
        if not binary:
            contents = raw.decode("utf-8", errors="replace")
            texts[path] = contents
            for name, rx in RX.items():
                lines = [i for i, line in enumerate(contents.splitlines(), 1) if rx.search(line)]
                if lines:
                    flags[name] = lines
        files.append({"path": path, "mode": mode, "git_blob": oid,
                      "sha256": hashlib.sha256(raw).hexdigest(), "bytes": size,
                      "binary": binary, "subsystem": subsystem(path), "risk_lines": flags})
    projects = []
    known = {entry[0].lower() for entry in entries}
    for path, contents in sorted(texts.items()):
        if not path.endswith(".vcxproj"):
            continue
        tree = ET.fromstring(contents)
        sources, missing, references = [], [], []
        for node in tree.iter():
            tag = node.tag.rsplit("}", 1)[-1]
            value = node.attrib.get("Include", "")
            if tag not in ("ClCompile", "ProjectReference") or not value:
                continue
            # Normalize Windows-relative paths on every host OS.
            parts = list(PurePosixPath(path).parent.parts)
            for part in value.replace("\\", "/").split("/"):
                if part == "..":
                    parts.pop()
                elif part != ".":
                    parts.append(part)
            target = "/".join(parts)
            (sources if tag == "ClCompile" else references).append(target)
            if target.lower() not in known:
                missing.append(target)
        projects.append({"path": path, "sources": sorted(sources),
                         "project_references": sorted(references), "missing": sorted(missing)})
    return {"schema": 1, "upstream_revision": revision,
            "coverage": "all upstream blobs inventoried and mechanically screened; semantic review remains phase-specific",
            "file_count": len(files), "total_bytes": sum(f["bytes"] for f in files),
            "subsystems": dict(sorted(collections.Counter(f["subsystem"] for f in files).items())),
            "risk_file_counts": {name: sum(name in f["risk_lines"] for f in files) for name in RX},
            "patterns": PATTERNS, "projects": projects, "files": files}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=ROOT / "docs/ios/upstream-audit.json")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    encoded = json.dumps(make_audit(), indent=2, sort_keys=True) + "\n"
    if args.check:
        if args.output.read_text(encoding="utf-8") != encoded:
            raise SystemExit("Audit differs from upstream baseline; regenerate and review")
        print("PASS: every upstream blob matches the recorded audit")
    else:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(encoded, encoding="utf-8", newline="\n")
        print(f"Wrote {args.output}")


if __name__ == "__main__":
    main()
