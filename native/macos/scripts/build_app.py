#!/usr/bin/env python3
"""Build a native macOS bundle. No privileged activation, TCC changes or shell execution."""

import argparse
import hashlib
import json
import os
from pathlib import Path
import plistlib
import re
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parents[1]
BUNDLE_ID = "de.agentauthority.observer"


def run(*args):
    subprocess.run([str(x) for x in args], check=True)


def dependencies(path):
    lines = subprocess.check_output(["otool", "-L", str(path)], text=True).splitlines()[1:]
    return [line.strip().split(" (", 1)[0] for line in lines]


def embed_runtime(destination, runtime_python):
    """Copy the installed Python runtime and its dylibs; rewrite to bundle-relative links."""
    if sys.version_info < (3, 12):
        raise SystemExit("Run this builder with Python 3.12 or later.")
    metadata = json.loads(
        subprocess.check_output(
            [
                str(runtime_python),
                "-I",
                "-c",
                "import sys,sysconfig,json;print(json.dumps({'stdlib':sysconfig.get_path('stdlib'),'prefix':sys.prefix,'version':list(sys.version_info[:2])}))",
            ],
            text=True,
        )
    )
    if metadata["version"] != [3, 12]:
        raise SystemExit("Embedded runtime must be Python 3.12.")
    stdlib = Path(metadata["stdlib"])
    prefix = Path(metadata["prefix"])
    destination.mkdir(parents=True)
    (destination / "bin").mkdir()
    (destination / "lib").mkdir()
    exe = destination / "bin/python3.12"
    shutil.copy2(runtime_python, exe)
    shutil.copytree(
        stdlib,
        destination / "lib/python3.12",
        ignore=shutil.ignore_patterns(
            "site-packages", "__pycache__", "test", "tests", "idlelib", "tkinter", "turtledemo"
        ),
    )
    for dylib in (prefix / "lib").glob("*.dylib"):
        shutil.copy2(dylib, destination / "lib" / dylib.name)
    images = (
        [exe]
        + list((destination / "lib/python3.12/lib-dynload").glob("*.so"))
        + list((destination / "lib").glob("*.dylib"))
    )
    queue = list(images)
    mapping = {}
    while queue:
        image = queue.pop()
        for dependency in dependencies(image):
            if not dependency.startswith("/usr/local/") and not dependency.startswith(
                "/Library/Frameworks/"
            ):
                continue
            if dependency in mapping:
                continue
            name = (
                "libpython3.12.dylib" if dependency.endswith("/Python") else Path(dependency).name
            )
            target = destination / "lib" / name
            if (
                target.exists()
                and hashlib.sha256(target.read_bytes()).digest()
                != hashlib.sha256(Path(dependency).read_bytes()).digest()
            ):
                raise RuntimeError("Conflicting runtime dylib names")
            shutil.copy2(dependency, target)
            mapping[dependency] = target
            queue.append(target)
            images.append(target)
    for image in images:
        image.chmod(image.stat().st_mode | 0o200)
        for dependency in dependencies(image):
            if dependency in mapping:
                relative = os.path.relpath(mapping[dependency], image.parent)
                run("install_name_tool", "-change", dependency, "@loader_path/" + relative, image)
        if image in mapping.values():
            run("install_name_tool", "-id", "@loader_path/" + image.name, image)
    license_sources = list(prefix.glob("**/LICENSE*")) + list(prefix.glob("**/COPYING*"))
    license_folder = destination / "licenses"
    license_folder.mkdir()
    for i, source in enumerate(license_sources):
        if source.is_file():
            shutil.copy2(source, license_folder / (str(i) + "-" + source.name))
    if not license_sources:
        raise RuntimeError("Python runtime license files missing")
    return images


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--configuration", choices=["debug", "release"], default="release")
    parser.add_argument("--output", type=Path, default=ROOT / "build")
    parser.add_argument("--sign", default="-")
    parser.add_argument("--review-label", default="")
    parser.add_argument("--team", default="")
    parser.add_argument("--host-profile", type=Path)
    parser.add_argument("--collector-profile", type=Path)
    parser.add_argument("--skip-runtime", action="store_true")
    parser.add_argument(
        "--runtime-python", type=Path, default=ROOT / ".runtime/standalone/python/bin/python3.12"
    )
    args = parser.parse_args()
    provisioned = (
        args.sign != "-"
        and re.fullmatch(r"[A-Z0-9]{10}", args.team)
        and args.host_profile
        and args.collector_profile
    )
    if args.sign != "-" and not provisioned:
        raise SystemExit(
            "Signed collector builds require --team, --host-profile and --collector-profile."
        )
    run("swift", "build", "--package-path", ROOT, "-c", args.configuration)
    bin_path = Path(
        subprocess.check_output(
            [
                "swift",
                "build",
                "--package-path",
                str(ROOT),
                "-c",
                args.configuration,
                "--show-bin-path",
            ],
            text=True,
        ).strip()
    )
    app = args.output.resolve() / "Agent Authority.app"
    if app.exists():
        shutil.rmtree(app)  # Only this builder's exact output bundle.
    mac = app / "Contents/MacOS"
    resources = app / "Contents/Resources"
    mac.mkdir(parents=True)
    resources.mkdir()
    shutil.copy2(bin_path / "AgentAuthorityMac", mac / "AgentAuthorityMac")
    shutil.copytree(ROOT / "Sources/AuthorityCore/Resources", resources / "AuthorityCore")
    shutil.copytree(
        REPO / "agent_authority",
        resources / "Engine/agent_authority",
        ignore=shutil.ignore_patterns("__pycache__"),
    )
    shutil.copy2(REPO / "LICENSE", resources / "LICENSE-AgentAuthority.txt")
    info = {
        "CFBundleIdentifier": BUNDLE_ID,
        "CFBundleName": "Agent Authority",
        "CFBundleDisplayName": "Agent Authority",
        "CFBundleExecutable": "AgentAuthorityMac",
        "CFBundlePackageType": "APPL",
        "CFBundleVersion": "1",
        "CFBundleShortVersionString": "0.1.0",
        "LSMinimumSystemVersion": "12.0",
        "NSHighResolutionCapable": True,
        "NSPrincipalClass": "NSApplication",
        "CFBundleDevelopmentRegion": "de",
        "CFBundleLocalizations": ["de", "en"],
        "NSAppleEventsUsageDescription": "Agent Authority requests permission for explicitly selected app automation tests.",
        "AAExpectedTeam": args.team if provisioned else "",
    }
    if args.review_label:
        info["AAReviewBuildLabel"] = args.review_label

    (app / "Contents/Info.plist").write_bytes(plistlib.dumps(info))
    strings = json.loads((resources / "AuthorityCore/Strings.json").read_text(encoding="utf-8"))
    for lang in ["de", "en"]:
        folder = resources / (lang + ".lproj")
        folder.mkdir()
        explanation = strings["host.automationDetail"][lang].replace('"', '\\"')
        (folder / "InfoPlist.strings").write_text(
            '"NSAppleEventsUsageDescription" = "' + explanation + '";\n', encoding="utf-8"
        )
    for name, source in [("AAProcessProbe", "ProcessProbe.c"), ("AAWriter", "Writer.c")]:
        cmd = [
            "xcrun",
            "clang",
            "-O2",
            "-Wall",
            "-Wextra",
            "-Werror",
            "-fblocks",
            "-mmacosx-version-min=12.0",
            ROOT / "Support" / source,
            "-o",
            mac / name,
        ]
        if name == "AAProcessProbe":
            cmd += ["-lEndpointSecurity"]
        run(*cmd)
    extension = (
        app
        / "Contents/Library/SystemExtensions/de.agentauthority.observer.collector.systemextension"
    )
    (extension / "Contents/MacOS").mkdir(parents=True)
    run(
        "xcrun",
        "clang",
        "-O2",
        "-Wall",
        "-Wextra",
        "-Werror",
        "-fobjc-arc",
        "-fblocks",
        "-mmacosx-version-min=12.0",
        ROOT / "Collector/main.m",
        "-framework",
        "Foundation",
        "-framework",
        "Security",
        "-lEndpointSecurity",
        "-lbsm",
        "-o",
        extension / "Contents/MacOS/AACollector",
    )
    extension_info = {
        "CFBundleIdentifier": BUNDLE_ID + ".collector",
        "CFBundleName": "Agent Authority Collector",
        "CFBundleExecutable": "AACollector",
        "CFBundlePackageType": "SYSX",
        "CFBundleVersion": "1",
        "CFBundleShortVersionString": "0.1.0",
        "LSMinimumSystemVersion": "12.0",
        "AAExpectedTeam": args.team if provisioned else "",
        "NSEndpointSecurityMachServiceName": args.team + "." + BUNDLE_ID + ".collector.xpc",
        "NSSystemExtensionUsageDescription": "Observe process and file events for explicitly selected Agent Authority tests.",
    }
    (extension / "Contents/Info.plist").write_bytes(plistlib.dumps(extension_info))
    for lang in ["de", "en"]:
        folder = extension / "Contents/Resources" / (lang + ".lproj")
        folder.mkdir(parents=True)
        text = strings["host.esDetail"][lang].replace('"', '\\"')
        (folder / "InfoPlist.strings").write_text(
            '"NSSystemExtensionUsageDescription" = "' + text + '";\n', encoding="utf-8"
        )
    images = [] if args.skip_runtime else embed_runtime(resources / "Runtime", args.runtime_python)
    entitlements = args.output.resolve() / "entitlements"
    entitlements.mkdir(exist_ok=True)
    host_ent = {"com.apple.security.automation.apple-events": True}
    extension_ent = {}
    if provisioned:
        host_ent["com.apple.developer.system-extension.install"] = True
        extension_ent["com.apple.developer.endpoint-security.client"] = True
        shutil.copy2(args.host_profile, app / "Contents/embedded.provisionprofile")
        shutil.copy2(args.collector_profile, extension / "Contents/embedded.provisionprofile")
    (entitlements / "host.plist").write_bytes(plistlib.dumps(host_ent))
    (entitlements / "collector.plist").write_bytes(plistlib.dumps(extension_ent))
    for image in images + [mac / "AAProcessProbe", mac / "AAWriter"]:
        run("codesign", "--force", "--sign", args.sign, "--options", "runtime", image)
    run(
        "codesign",
        "--force",
        "--sign",
        args.sign,
        "--options",
        "runtime",
        "--entitlements",
        entitlements / "collector.plist",
        extension,
    )
    run(
        "codesign",
        "--force",
        "--sign",
        args.sign,
        "--options",
        "runtime",
        "--entitlements",
        entitlements / "host.plist",
        app,
    )
    run("codesign", "--verify", "--strict", "--deep", app)
    manifest = {
        "app": str(app),
        "signing": "Developer ID + provisioned ES" if provisioned else "ad-hoc development only",
        "engine_sha": subprocess.check_output(
            ["git", "-C", str(REPO), "rev-parse", "HEAD"], text=True
        ).strip(),
        "runtime_included": not args.skip_runtime,
        "native_minimum_os": "12.0",
        "runtime_compatibility": "Audit embedded dylib minimum OS before distributing to macOS 12.",
        "collector_activated": False,
    }
    (args.output / "build-manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(app)


if __name__ == "__main__":
    main()
