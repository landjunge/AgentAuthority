#!/usr/bin/env python3
"""Build a native macOS bundle. No privileged activation, TCC changes or shell execution."""

import argparse
import hashlib
import json
import os
import plistlib
import re
import shutil
import stat
import subprocess
import tarfile
import tempfile
from pathlib import Path, PurePosixPath

ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parents[1]
BUNDLE_ID = "de.agentauthority.observer"
SOURCE_ARCHIVE_PATHS = (
    "agent_authority",
    "LICENSE",
    "assets/design/icons/macos/Agent-Authority-dark.icns",
    "native/macos",
)
REQUIRED_SOURCE_PATHS = (
    "agent_authority/__init__.py",
    "agent_authority/cli.py",
    "LICENSE",
    "assets/design/icons/macos/Agent-Authority-dark.icns",
    "native/macos/Package.swift",
    "native/macos/Sources/AgentAuthorityMac/main.swift",
    "native/macos/Sources/AgentAuthorityMac/Resources/ProductHeader/networkpunkt-appbar-assets.json",
    "native/macos/Sources/AuthorityCore/Resources/Strings.json",
    "native/macos/Sources/NativeSupport/Transport.m",
    "native/macos/Sources/NativeSupport/include/NativeSupport.h",
    "native/macos/Support/ProcessProbe.c",
    "native/macos/Support/Writer.c",
    "native/macos/Collector/main.m",
)
MAX_ARCHIVE_MEMBERS = 20_000
MAX_ARCHIVE_BYTES = 128 * 1024 * 1024


def run(*args):
    subprocess.run([str(x) for x in args], check=True)


def clean_source_revision(repository):
    status = subprocess.check_output(
        ["git", "-C", str(repository), "status", "--porcelain=v1", "--untracked-files=all"],
        text=True,
    )
    if status:
        raise SystemExit(
            "Refusing to package a dirty source tree; build manifest would be misleading."
        )
    return subprocess.check_output(
        ["git", "-C", str(repository), "rev-parse", "HEAD"], text=True
    ).strip()


def verify_source_revision(repository, expected_revision):
    current_revision = clean_source_revision(repository)
    if current_revision != expected_revision:
        raise SystemExit(
            "Source revision changed during build; refusing to write a pinned manifest."
        )


def bind_original_paths(args):
    args.output = Path(args.output).expanduser().resolve()
    args.runtime_python = Path(args.runtime_python).expanduser().resolve()
    for name in ("host_profile", "collector_profile"):
        value = getattr(args, name)
        if value is not None:
            setattr(args, name, Path(value).expanduser().resolve())
    return args


def tracked_source_paths(repository, revision):
    result = subprocess.check_output(
        [
            "git",
            "-C",
            str(repository),
            "ls-tree",
            "-r",
            "-z",
            "--name-only",
            "--full-tree",
            revision,
            "--",
            *SOURCE_ARCHIVE_PATHS,
        ]
    )
    paths = {os.fsdecode(path) for path in result.split(b"\0") if path}
    missing = set(REQUIRED_SOURCE_PATHS) - paths
    if missing:
        raise SystemExit(f"Pinned source is missing required build inputs: {sorted(missing)}")
    return paths


def _safe_archive_name(name):
    normalized = name.removesuffix("/")
    parts = normalized.split("/")
    if (
        not normalized
        or normalized.startswith("/")
        or "\\" in normalized
        or "\0" in normalized
        or any(part in ("", ".", "..") for part in parts)
    ):
        raise SystemExit("Unsafe path in source archive.")
    return normalized


def extract_source_archive(archive_path, destination, expected_files):
    archive_path = Path(archive_path)
    destination = Path(destination)
    if destination.exists():
        raise SystemExit("Source snapshot destination must be new.")
    if not stat.S_ISREG(archive_path.lstat().st_mode):
        raise SystemExit("Source archive must be a regular file.")
    if archive_path.resolve().parent != destination.parent.resolve():
        raise SystemExit("Source snapshot must remain beside its private archive.")
    if archive_path.stat().st_size > MAX_ARCHIVE_BYTES:
        raise SystemExit("Source archive exceeds the extraction size limit.")
    if not callable(getattr(tarfile, "data_filter", None)):
        raise SystemExit("Safe tar data filtering is unavailable in this Python runtime.")

    expected_files = set(expected_files)
    expected_dirs = set()
    for name in expected_files:
        parent = PurePosixPath(name).parent
        while str(parent) != ".":
            expected_dirs.add(str(parent))
            parent = parent.parent

    try:
        with tarfile.open(archive_path, mode="r:") as source:
            members = source.getmembers()
            if len(members) > MAX_ARCHIVE_MEMBERS:
                raise SystemExit("Source archive exceeds the member-count limit.")
            seen, actual_files, total_size = set(), set(), 0
            for member in members:
                name = _safe_archive_name(member.name)
                if name in seen:
                    raise SystemExit("Duplicate path in source archive.")
                seen.add(name)
                if member.isdir():
                    if name not in expected_dirs:
                        raise SystemExit("Unexpected directory in source archive.")
                elif member.type in (tarfile.REGTYPE, tarfile.AREGTYPE) and member.isfile():
                    if name not in expected_files or member.issparse():
                        raise SystemExit("Unexpected file type or path in source archive.")
                    if member.size < 0:
                        raise SystemExit("Invalid file size in source archive.")
                    total_size += member.size
                    actual_files.add(name)
                else:
                    raise SystemExit("Links and special files are forbidden in source archives.")
                if total_size > MAX_ARCHIVE_BYTES:
                    raise SystemExit("Expanded source archive exceeds the size limit.")

            missing = expected_files - actual_files
            extra = actual_files - expected_files
            if missing or extra:
                raise SystemExit(
                    f"Source archive does not match tracked inputs; missing={sorted(missing)}, "
                    f"extra={sorted(extra)}"
                )
            destination.mkdir(mode=0o700, parents=False)
            source.extractall(destination, members=members, filter="data")
    except (tarfile.TarError, OSError) as error:
        raise SystemExit(f"Could not safely extract source archive: {error}") from error
    return destination


def create_source_snapshot(repository, revision, temporary_root):
    repository = Path(repository).resolve()
    temporary_root = Path(temporary_root).resolve()
    expected_files = tracked_source_paths(repository, revision)
    archive_path = temporary_root / "source.tar"
    with archive_path.open("xb") as archive:
        os.chmod(archive_path, 0o600)
        subprocess.run(
            [
                "git",
                "-C",
                str(repository),
                "archive",
                "--format=tar",
                revision,
                *SOURCE_ARCHIVE_PATHS,
            ],
            stdout=archive,
            stderr=subprocess.PIPE,
            check=True,
        )
    return extract_source_archive(archive_path, temporary_root / "source", expected_files)


def dependencies(path):
    lines = subprocess.check_output(["otool", "-L", str(path)], text=True).splitlines()[1:]
    return [line.strip().split(" (", 1)[0] for line in lines]


def embed_runtime(destination, runtime_python):
    """Copy the installed Python runtime and its dylibs; rewrite to bundle-relative links."""
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


def extract_build(args, source_revision, source_repository, build_repository):
    repo = Path(build_repository).resolve()
    root = repo / "native/macos"
    if repo == Path(source_repository).resolve():
        raise SystemExit("Build inputs must come from the extracted source snapshot.")
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
    run("swift", "build", "--package-path", root, "-c", args.configuration)
    bin_path = Path(
        subprocess.check_output(
            [
                "swift",
                "build",
                "--package-path",
                str(root),
                "-c",
                args.configuration,
                "--show-bin-path",
            ],
            text=True,
        ).strip()
    )
    output = Path(args.output)
    app = output / "Agent Authority.app"
    if app.exists():
        shutil.rmtree(app)  # Only this builder's exact output bundle.
    mac = app / "Contents/MacOS"
    resources = app / "Contents/Resources"
    mac.mkdir(parents=True)
    resources.mkdir()
    shutil.copy2(bin_path / "AgentAuthorityMac", mac / "AgentAuthorityMac")
    shutil.copytree(root / "Sources/AuthorityCore/Resources", resources / "AuthorityCore")
    shutil.copytree(
        repo / "agent_authority",
        resources / "Engine/agent_authority",
        ignore=shutil.ignore_patterns("__pycache__"),
    )
    shutil.copy2(repo / "LICENSE", resources / "LICENSE-AgentAuthority.txt")
    shutil.copy2(
        repo / "assets/design/icons/macos/Agent-Authority-dark.icns",
        resources / "AgentAuthority.icns",
    )
    # The packaged header resolves its original assets without a checkout or SwiftPM build path.
    shutil.copytree(
        root / "Sources/AgentAuthorityMac/Resources/ProductHeader", resources / "ProductHeader"
    )
    info = {
        "CFBundleIdentifier": BUNDLE_ID,
        "CFBundleName": "Agent Authority",
        "CFBundleDisplayName": "Agent Authority",
        "CFBundleExecutable": "AgentAuthorityMac",
        "CFBundleIconFile": "AgentAuthority.icns",
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
            root / "Support" / source,
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
        root / "Collector/main.m",
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
    entitlements = output / "entitlements"
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
    return {
        "app": str(app),
        "signing": "Developer ID + provisioned ES" if provisioned else "ad-hoc development only",
        "engine_sha": source_revision,
        "runtime_included": not args.skip_runtime,
        "native_minimum_os": "12.0",
        "runtime_compatibility": "Audit embedded dylib minimum OS before distributing to macOS 12.",
        "collector_activated": False,
    }


def run_snapshot_build(args, source_repository=REPO, build_function=extract_build):
    args = bind_original_paths(args)
    source_repository = Path(source_repository).resolve()
    source_revision = clean_source_revision(source_repository)
    with tempfile.TemporaryDirectory(prefix="agent-authority-source-") as temporary:
        temporary_root = Path(temporary)
        os.chmod(temporary_root, 0o700)
        build_repository = create_source_snapshot(
            source_repository, source_revision, temporary_root
        )
        output = Path(args.output)
        manifest_path = output / "build-manifest.json"
        if manifest_path.exists() or manifest_path.is_symlink():
            manifest_path.unlink()
        manifest = build_function(args, source_revision, source_repository, build_repository)
        verify_source_revision(source_repository, source_revision)
        manifest = dict(manifest)
        manifest["engine_sha"] = source_revision
        output.mkdir(parents=True, exist_ok=True)
        descriptor, temporary_manifest = tempfile.mkstemp(
            prefix=".build-manifest-", suffix=".tmp", dir=output
        )
        try:
            with os.fdopen(descriptor, "w", encoding="utf-8") as stream:
                stream.write(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n")
                stream.flush()
                os.fsync(stream.fileno())
            os.replace(temporary_manifest, manifest_path)
        except BaseException:
            try:
                os.unlink(temporary_manifest)
            except FileNotFoundError:
                pass
            raise
        print(manifest["app"])
        return manifest


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
    run_snapshot_build(parser.parse_args())


if __name__ == "__main__":
    main()
