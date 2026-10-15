"""Deterministically generate the Phase 02 Xcode harness (standard library only)."""
import argparse
import hashlib
import json
from pathlib import Path
import plistlib
import sys
from xml.sax.saxutils import escape

ROOT = Path(__file__).resolve().parents[2]
PROJECT = ROOT / "ios/DoomBFGHarness.xcodeproj"


def identifier(label):
    return hashlib.sha256(label.encode()).hexdigest()[:24].upper()


def openstep(value, level=0):
    if isinstance(value, dict):
        entries = ["\t" * (level + 1) + json.dumps(k) + " = " + openstep(v, level + 1) + ";" for k, v in value.items()]
        return "{\n" + "\n".join(entries) + "\n" + "\t" * level + "}"
    if isinstance(value, list):
        return "(" + ", ".join(openstep(v, level) for v in value) + ")"
    return str(value) if isinstance(value, int) else json.dumps(value)


def generate():
    manifest = json.loads((ROOT / "ios/harness/sources.json").read_text())
    toolchain = json.loads((ROOT / "ios/toolchain.json").read_text())
    base = ROOT / "ios/harness"
    for path in manifest["sources"] + manifest["resources"] + [manifest["info_plist"]]:
        resolved = (base / path).resolve()
        if not resolved.is_relative_to(ROOT) or not resolved.is_file():
            raise ValueError(f"Missing or out-of-repository manifest input: {path}")
    plistlib.loads((base / manifest["info_plist"]).read_bytes())
    objects = {}

    def add(label, isa, **values):
        key = identifier(label)
        if key in objects:
            raise ValueError(f"Duplicate project object: {label}")
        objects[key] = dict(isa=isa, **values)
        return key

    product = add("product", "PBXFileReference", explicitFileType="wrapper.application", includeInIndex=0,
                  path=manifest["name"] + ".app", sourceTree="BUILT_PRODUCTS_DIR")
    sources, resources, frameworks, files = [], [], [], []
    for category, paths, builds in (("source", manifest["sources"], sources), ("resource", manifest["resources"], resources)):
        for path in paths:
            relative = (base / path).resolve().relative_to(ROOT).as_posix()
            # References are relative to the directory containing the .xcodeproj.
            project_path = "../" + relative
            kind = "sourcecode.cpp.objcpp" if path.endswith(".mm") else "text"
            ref = add(category + path, "PBXFileReference", lastKnownFileType=kind, path=project_path, sourceTree="SOURCE_ROOT")
            files.append(ref)
            builds.append(add("build-" + category + path, "PBXBuildFile", fileRef=ref))
    plist_ref = add("plist", "PBXFileReference", lastKnownFileType="text.plist.xml", path="harness/" + manifest["info_plist"], sourceTree="SOURCE_ROOT")
    files.append(plist_ref)
    for framework in manifest["frameworks"]:
        ref = add("framework-" + framework, "PBXFileReference", lastKnownFileType="wrapper.framework",
                  path="System/Library/Frameworks/" + framework + ".framework", sourceTree="SDKROOT")
        files.append(ref)
        frameworks.append(add("build-framework-" + framework, "PBXBuildFile", fileRef=ref))
    products = add("products", "PBXGroup", children=[product], name="Products", sourceTree="<group>")
    group = add("main", "PBXGroup", children=files + [products], sourceTree="<group>")
    phases = []
    for name, isa, builds in (("sources", "PBXSourcesBuildPhase", sources), ("frameworks", "PBXFrameworksBuildPhase", frameworks),
                              ("resources", "PBXResourcesBuildPhase", resources)):
        phases.append(add(name, isa, buildActionMask=2147483647, files=builds, runOnlyForDeploymentPostprocessing=0))
    project_configs, target_configs = [], []
    for config in ("Debug", "Release"):
        project_configs.append(add("project-" + config, "XCBuildConfiguration", name=config, buildSettings={
            "CLANG_ENABLE_MODULES": "YES", "CLANG_ENABLE_OBJC_ARC": "YES", "CLANG_CXX_LANGUAGE_STANDARD": "c++17",
            "GCC_C_LANGUAGE_STANDARD": "gnu11", "IPHONEOS_DEPLOYMENT_TARGET": toolchain["deployment_target"],
            "SDKROOT": "iphoneos", "GCC_OPTIMIZATION_LEVEL": "0" if config == "Debug" else "s",
            "DEBUG_INFORMATION_FORMAT": "dwarf" if config == "Debug" else "dwarf-with-dsym",
            "GCC_PREPROCESSOR_DEFINITIONS": ["$(inherited)", "DEBUG=1"] if config == "Debug" else ["$(inherited)"],
        }))
        target_configs.append(add("target-" + config, "XCBuildConfiguration", name=config, buildSettings={
            "ARCHS": toolchain["device_arch"], "ONLY_ACTIVE_ARCH": "NO", "TARGETED_DEVICE_FAMILY": "1,2",
            "SUPPORTED_PLATFORMS": "iphoneos iphonesimulator", "SUPPORTS_MACCATALYST": "NO",
            "PRODUCT_NAME": "$(TARGET_NAME)", "PRODUCT_BUNDLE_IDENTIFIER": manifest["bundle_id"],
            "INFOPLIST_FILE": "harness/" + manifest["info_plist"], "GENERATE_INFOPLIST_FILE": "NO",
            "CODE_SIGNING_ALLOWED": "NO", "CODE_SIGNING_REQUIRED": "NO", "CODE_SIGN_IDENTITY": "",
        }))
    project_list = add("project-configs", "XCConfigurationList", buildConfigurations=project_configs,
                       defaultConfigurationIsVisible=0, defaultConfigurationName="Release")
    target_list = add("target-configs", "XCConfigurationList", buildConfigurations=target_configs,
                      defaultConfigurationIsVisible=0, defaultConfigurationName="Release")
    target = add("target", "PBXNativeTarget", buildConfigurationList=target_list, buildPhases=phases, buildRules=[],
                 dependencies=[], name=manifest["name"], productName=manifest["name"], productReference=product,
                 productType="com.apple.product-type.application")
    project = add("project", "PBXProject", attributes={"LastUpgradeCheck": "1640"}, buildConfigurationList=project_list,
                  compatibilityVersion="Xcode 14.0", developmentRegion="en", hasScannedForEncodings=0,
                  knownRegions=["en", "Base"], mainGroup=group, productRefGroup=products, projectDirPath="", projectRoot="", targets=[target])
    pbx = "// !$*UTF8*$!\n" + openstep(dict(archiveVersion=1, classes={}, objectVersion=56, objects=objects, rootObject=project)) + "\n"
    name = escape(manifest["name"])
    reference = f'<BuildableReference BuildableIdentifier="primary" BlueprintIdentifier="{target}" BuildableName="{name}.app" BlueprintName="{name}" ReferencedContainer="container:DoomBFGHarness.xcodeproj"/>'
    scheme = f'''<?xml version="1.0" encoding="UTF-8"?>
<Scheme LastUpgradeVersion="1640" version="1.3">
  <BuildAction parallelizeBuildables="YES" buildImplicitDependencies="YES"><BuildActionEntries>
    <BuildActionEntry buildForTesting="YES" buildForRunning="YES" buildForProfiling="YES" buildForArchiving="YES" buildForAnalyzing="YES">{reference}</BuildActionEntry>
  </BuildActionEntries></BuildAction>
  <TestAction buildConfiguration="Debug" selectedDebuggerIdentifier="Xcode.DebuggerFoundation.Debugger.LLDB" selectedLauncherIdentifier="Xcode.IDEFoundation.Launcher.LLDB" shouldUseLaunchSchemeArgsEnv="YES"/>
  <LaunchAction buildConfiguration="Debug" selectedDebuggerIdentifier="Xcode.DebuggerFoundation.Debugger.LLDB" selectedLauncherIdentifier="Xcode.IDEFoundation.Launcher.LLDB" launchStyle="0" useCustomWorkingDirectory="NO" ignoresPersistentStateOnLaunch="NO" debugDocumentVersioning="YES" allowLocationSimulation="YES"><BuildableProductRunnable runnableDebuggingMode="0">{reference}</BuildableProductRunnable></LaunchAction>
  <ProfileAction buildConfiguration="Release" shouldUseLaunchSchemeArgsEnv="YES" savedToolIdentifier="" useCustomWorkingDirectory="NO" debugDocumentVersioning="YES"><BuildableProductRunnable runnableDebuggingMode="0">{reference}</BuildableProductRunnable></ProfileAction>
  <AnalyzeAction buildConfiguration="Debug"/>
  <ArchiveAction buildConfiguration="Release" revealArchiveInOrganizer="YES"/>
</Scheme>
'''
    return {PROJECT / "project.pbxproj": pbx, PROJECT / "xcshareddata/xcschemes/DoomBFGHarness.xcscheme": scheme}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    for path, content in generate().items():
        if args.check:
            if not path.is_file() or path.read_text(encoding="utf-8") != content:
                print(f"Generated project differs: {path}", file=sys.stderr)
                return 1
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8", newline="\n")
    print("PASS: generated Xcode project" + (" is current" if args.check else ""))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
