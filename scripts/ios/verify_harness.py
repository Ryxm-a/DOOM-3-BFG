"""Build the native harness for ARM64 device/simulator and prove UIKit launches.

Requires the pinned macOS/Xcode environment. No engine, assets, signing or IPA.
Evidence includes full commands, simulator receipts and screenshots, even on failure.
"""
import argparse
import json
import os
from pathlib import Path
import platform
import shutil
import subprocess
import sys
import time
import uuid

ROOT = Path(__file__).resolve().parents[2]


def verify(output, families=("iPhone", "iPad")):
    config = json.loads((ROOT / "ios/toolchain.json").read_text())
    manifest = json.loads((ROOT / "ios/harness/sources.json").read_text())
    output.mkdir(parents=True, exist_ok=True)
    report = {"schema": 1, "status": "failed", "host": platform.system(), "machine": platform.machine(),
              "config": config, "commands": [], "launches": [], "engine_linked": False,
              "signing": "disabled for harness", "ipa_export": "not attempted"}
    env = dict(os.environ, DEVELOPER_DIR=config["developer_dir"])
    created = []

    def run(argv, timeout=180, command_env=None):
        argv = [str(x) for x in argv]
        record = {"argv": argv}
        report["commands"].append(record)
        print("RUN: " + " ".join(argv), flush=True)
        try:
            result = subprocess.run(argv, cwd=ROOT, env=command_env or env, text=True,
                                    stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=timeout)
        except subprocess.TimeoutExpired as exc:
            record.update(exit_code=None, output=str(exc.output), timeout_seconds=timeout)
            raise RuntimeError(f"Command timed out: {argv[0]}") from None
        record.update(exit_code=result.returncode, output=result.stdout)
        if result.returncode:
            raise RuntimeError(f"Command failed: {' '.join(argv[:4])} (see harness.json)")
        return result.stdout.strip()

    try:
        if platform.system() != "Darwin":
            raise RuntimeError("Harness verification requires a macOS runner with full Xcode")
        if platform.machine() != config["simulator_arch"]:
            raise RuntimeError("Runner architecture must match the explicit simulator architecture; no silent fallback")
        if not Path(config["developer_dir"]).is_dir():
            raise RuntimeError("Pinned Xcode directory is unavailable")
        version = run(["xcodebuild", "-version"])
        if version.splitlines() != ["Xcode " + config["xcode_version"], "Build version " + config["xcode_build"]]:
            raise RuntimeError("Xcode version/build mismatch")
        for sdk in ("iphoneos", "iphonesimulator"):
            if run(["xcrun", "--sdk", sdk, "--show-sdk-version"]) != config["sdk_version"]:
                raise RuntimeError(f"{sdk} SDK version mismatch")
        run([sys.executable, ROOT / "scripts/ios/generate_project.py", "--check"])
        run(["plutil", "-lint", ROOT / "ios/DoomBFGHarness.xcodeproj/project.pbxproj", ROOT / "ios/harness/Info.plist"])
        run(["xcodebuild", "-help"])
        run(["xcrun", "simctl", "help", "launch"])
        project = ROOT / "ios/DoomBFGHarness.xcodeproj"
        run(["xcodebuild", "-list", "-json", "-project", project])
        derived = ROOT / "build/ios-harness"
        for sdk, destination in (("iphoneos", "generic/platform=iOS"), ("iphonesimulator", "generic/platform=iOS Simulator")):
            run(["xcodebuild", "-project", project, "-scheme", manifest["name"], "-configuration", "Debug",
                 "-sdk", sdk, "-destination", destination, "-derivedDataPath", derived / sdk,
                 "-resultBundlePath", output / (sdk + ".xcresult"), "CODE_SIGNING_ALLOWED=NO", "build"], timeout=600)
            app = derived / sdk / "Build/Products" / ("Debug-" + sdk) / (manifest["name"] + ".app")
            binary = app / manifest["name"]
            arch = config["device_arch"] if sdk == "iphoneos" else config["simulator_arch"]
            if run(["xcrun", "lipo", "-archs", binary]) != arch:
                raise RuntimeError(f"Unexpected architecture for {sdk}")
            run(["xcrun", "otool", "-L", binary])
            run(["xcrun", "vtool", "-show-build", binary])
            run(["plutil", "-p", app / "Info.plist"])
        runtimes = json.loads(run(["xcrun", "simctl", "list", "runtimes", "--json"]))["runtimes"]
        runtime_id = "com.apple.CoreSimulator.SimRuntime.iOS-" + config["sdk_version"].replace(".", "-")
        if not any(r["identifier"] == runtime_id and r.get("isAvailable") for r in runtimes):
            raise RuntimeError(f"Pinned simulator runtime unavailable: {runtime_id}")
        simulator_app = derived / "iphonesimulator/Build/Products/Debug-iphonesimulator" / (manifest["name"] + ".app")
        for family, device_type in (("iPhone", "iPhone-16"), ("iPad", "iPad-10th-generation")):
            if family not in families:
                continue
            udid = run(["xcrun", "simctl", "create", "BFG-Phase02-" + family,
                        "com.apple.CoreSimulator.SimDeviceType." + device_type, runtime_id])
            created.append(udid)
            run(["xcrun", "simctl", "boot", udid])
            run(["xcrun", "simctl", "bootstatus", udid, "-b"], timeout=300)
            run(["xcrun", "simctl", "install", udid, simulator_app])
            nonce = uuid.uuid4().hex
            run(["xcrun", "simctl", "launch", "--stdout=" + str(output / (family + ".stdout.log")),
                 "--stderr=" + str(output / (family + ".stderr.log")), udid, manifest["bundle_id"]],
                command_env=dict(env, SIMCTL_CHILD_BFG_HARNESS_NONCE=nonce))
            container = Path(run(["xcrun", "simctl", "get_app_container", udid, manifest["bundle_id"], "data"]))
            receipt_path = container / "Documents/phase02-launch.json"
            deadline = time.monotonic() + 45
            while not receipt_path.is_file() and time.monotonic() < deadline:
                time.sleep(0.5)
            if not receipt_path.is_file():
                try:
                    run(["xcrun", "simctl", "spawn", udid, "log", "show", "--last", "3m", "--style", "compact",
                         "--predicate", 'process == "' + manifest["name"] + '"'], timeout=60)
                except (OSError, RuntimeError):
                    pass
                for crash in (Path.home() / "Library/Logs/DiagnosticReports").glob(manifest["name"] + "*.ips"):
                    shutil.copyfile(crash, output / crash.name)
                raise RuntimeError(f"{family} did not produce a viewDidAppear receipt")
            receipt = json.loads(receipt_path.read_text())
            expected = {"schema": 1, "phase": 2, "nonce": nonce, "event": "viewDidAppear", "engine_linked": False,
                        "pointer_bits": 64, "bundle_id": manifest["bundle_id"], "system_version": config["sdk_version"], "device_family": family}
            expected["core_tests"] = {"phase": "03b", "status": "passed", "checks": ["abi", "endian", "allocation", "list-sort", "crc32", "md4-rfc1320", "md5-rfc1321", "strings", "bounded-format", "hash-index"]}
            if receipt != expected:
                raise RuntimeError(f"{family} launch receipt mismatch")
            shutil.copyfile(receipt_path, output / (family + "-launch.json"))
            run(["xcrun", "simctl", "io", udid, "screenshot", output / (family + ".png")])
            run(["xcrun", "simctl", "terminate", udid, manifest["bundle_id"]])
            report["launches"].append({"family": family, "udid": udid, "runtime": runtime_id, "receipt": receipt})
            run(["xcrun", "simctl", "shutdown", udid])
        report["status"] = "passed"
        report["scope"] = "Selected idlib core utilities: ARM64 device/simulator links; launch/fixture receipts for " + ", ".join(families)
    except (OSError, RuntimeError, ValueError, KeyError) as exc:
        report["error"] = str(exc)
    finally:
        for udid in created:
            for action in ("shutdown", "delete"):
                try:
                    run(["xcrun", "simctl", action, udid])
                except (OSError, RuntimeError):
                    pass
        (output / "harness.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(f'{report["status"].upper()}: {output / "harness.json"}')
    if "error" in report:
        print(report["error"], file=sys.stderr)
    return 0 if report["status"] == "passed" else 1


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=ROOT / "artifacts/ios-harness")
    parser.add_argument("--families", nargs="+", choices=("iPhone", "iPad"), default=["iPhone", "iPad"])
    args = parser.parse_args()
    raise SystemExit(verify(args.output.resolve(), args.families))
