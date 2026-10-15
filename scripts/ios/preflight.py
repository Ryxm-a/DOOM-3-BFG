"""Verify the pinned Apple SDK by compiling device/simulator and Metal probes.

Does not build the engine, sign an application, or establish IPA exportability.
Always writes a report, including failures, for CI diagnostics.
"""
import argparse
import json
import os
from pathlib import Path
import platform
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]

PROBE = r'''#import <UIKit/UIKit.h>
#import <MetalKit/MetalKit.h>
#import <AVFoundation/AVFoundation.h>
#import <AudioToolbox/AudioToolbox.h>
#import <GameController/GameController.h>
#import <Security/Security.h>
#include <zlib.h>
int main(void) {
    @autoreleasepool {
        id<MTLDevice> gpu = MTLCreateSystemDefaultDevice();
        (void)[MTKView class]; (void)[UIView class];
        (void)[AVAudioEngine class]; (void)[GCController class];
        (void)AudioComponentFindNext(NULL, NULL);
        (void)SecRandomCopyBytes(kSecRandomDefault, 0, NULL);
        return gpu == nil || zlibVersion() == NULL;
    }
}
'''
METAL = '''#include <metal_stdlib>
using namespace metal;
kernel void probe(device uint *out [[buffer(0)]], uint i [[thread_position_in_grid]]) {
    out[i] = i;
}
'''


def run(command, env, report):
    result = subprocess.run(command, env=env, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    report["commands"].append({"argv": [str(x) for x in command], "exit_code": result.returncode,
                               "output": result.stdout})
    if result.returncode:
        raise RuntimeError(f"Command failed: {command[0]} (see report)")
    return result.stdout.strip()


def verify(output):
    config = json.loads((ROOT / "ios/toolchain.json").read_text())
    report = {"schema": 1, "status": "failed", "host": platform.system(), "config": config,
              "commands": [], "engine_build": "not attempted", "ipa_export": "not verified",
              "signing": "not attempted; credentials are not needed for SDK probes"}
    output.mkdir(parents=True, exist_ok=True)
    try:
        if platform.system() != "Darwin":
            raise RuntimeError("Apple SDK verification requires a macOS runner with full Xcode")
        developer = Path(config["developer_dir"])
        if not developer.is_dir():
            raise RuntimeError(f"Pinned Xcode is unavailable: {developer}; no silent fallback")
        env = dict(os.environ, DEVELOPER_DIR=str(developer))
        version = run(["xcodebuild", "-version"], env, report)
        if version.splitlines() != ["Xcode " + config["xcode_version"], "Build version " + config["xcode_build"]]:
            raise RuntimeError("Xcode version/build does not match ios/toolchain.json")
        run(["xcodebuild", "-showsdks"], env, report)
        run(["xcodebuild", "-help"], env, report)  # Export options from this actual Xcode.
        run(["xcrun", "simctl", "list", "devices", "available", "--json"], env, report)
        source = output / "sdk-probe.m"
        source.write_text(PROBE, encoding="utf-8")
        shader = output / "probe.metal"
        shader.write_text(METAL, encoding="utf-8")
        for sdk, archkey, suffix in (("iphoneos", "device_arch", ""),
                                      ("iphonesimulator", "simulator_arch", "-simulator")):
            sdkpath = run(["xcrun", "--sdk", sdk, "--show-sdk-path"], env, report)
            sdkversion = run(["xcrun", "--sdk", sdk, "--show-sdk-version"], env, report)
            if sdkversion != config["sdk_version"]:
                raise RuntimeError(f"{sdk} SDK version mismatch: {sdkversion}")
            target = f'{config[archkey]}-apple-ios{config["deployment_target"]}{suffix}'
            binary = output / f"sdk-probe-{sdk}"
            command = ["xcrun", "--sdk", sdk, "clang", "-target", target,
                       "-isysroot", sdkpath, "-fobjc-arc", str(source), "-o", str(binary), "-lz"]
            for framework in config["frameworks"]:
                command.extend(["-framework", framework])
            run(command, env, report)
            run(["xcrun", "lipo", "-info", str(binary)], env, report)
            run(["xcrun", "otool", "-l", str(binary)], env, report)
            air = output / f"probe-{sdk}.air"
            run(["xcrun", "--sdk", sdk, "metal", "-c", str(shader), "-o", str(air)], env, report)
            run(["xcrun", "--sdk", sdk, "metallib", str(air), "-o", str(output / f"probe-{sdk}.metallib")], env, report)
        report["status"] = "passed"
        report["scope"] = "SDK compile/link and Metal compilation only; probes not executed"
    except (RuntimeError, OSError) as exc:
        report["error"] = str(exc)
    (output / "preflight.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(f'{report["status"].upper()}: {output / "preflight.json"}')
    if "error" in report:
        print(report["error"], file=sys.stderr)
    return 0 if report["status"] == "passed" else 1


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=ROOT / "artifacts/ios-preflight")
    raise SystemExit(verify(parser.parse_args().output.resolve()))
