import argparse
import importlib.util
import io
import json
import os
import stat
import subprocess
import tarfile
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).parents[1] / "native/macos/scripts/build_app.py"
SPEC = importlib.util.spec_from_file_location("aa_build_app", SCRIPT)
assert SPEC and SPEC.loader
BUILD_APP = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(BUILD_APP)


def git(repo: Path, *args: str) -> str:
    return subprocess.check_output(["git", "-C", str(repo), *args], text=True).strip()


def repository(path: Path, export_ignore: str = "") -> Path:
    subprocess.run(["git", "init", str(path)], check=True, capture_output=True)
    (path / ".gitattributes").write_text(export_ignore, encoding="utf-8")
    for relative in BUILD_APP.REQUIRED_SOURCE_PATHS:
        target = path / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(b"fixture source\n")
    (path / "agent_authority/observed.py").write_text("VALUE = 'committed'\n", encoding="utf-8")
    package_tests = path / "native/macos/Tests/MacAppTests/Fixture.swift"
    package_tests.parent.mkdir(parents=True)
    package_tests.write_text("final class Fixture {}\n", encoding="utf-8")
    (path / "native/macos/Package.resolved").write_text("{}\n", encoding="utf-8")
    subprocess.run(["git", "-C", str(path), "add", "-A"], check=True, capture_output=True)
    subprocess.run(
        [
            "git",
            "-C",
            str(path),
            "-c",
            "user.name=Test",
            "-c",
            "user.email=test@example.invalid",
            "commit",
            "-m",
            "baseline",
        ],
        check=True,
        capture_output=True,
    )
    return path


def args_for(root: Path) -> argparse.Namespace:
    return argparse.Namespace(
        output=root / "output",
        runtime_python=root / "runtime/bin/python3.12",
        host_profile=root / "host.provisionprofile",
        collector_profile=root / "collector.provisionprofile",
        skip_runtime=True,
        configuration="release",
        sign="-",
        review_label="",
        team="",
    )


class BuildProvenanceTests(unittest.TestCase):
    def test_snapshot_omits_ignored_files_and_includes_all_package_inputs(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            repo = repository(root / "repo")
            (repo / ".gitignore").write_text("agent_authority/ignored.local\n", encoding="utf-8")
            git(repo, "add", ".gitignore")
            subprocess.run(
                [
                    "git",
                    "-C",
                    str(repo),
                    "-c",
                    "user.name=Test",
                    "-c",
                    "user.email=test@example.invalid",
                    "commit",
                    "-m",
                    "ignore local file",
                ],
                check=True,
                capture_output=True,
            )
            ignored = repo / "agent_authority/ignored.local"
            ignored.write_text("local-only fixture\n", encoding="utf-8")
            revision = BUILD_APP.clean_source_revision(repo)
            temp_root = root / "private"
            temp_root.mkdir(mode=0o700)

            snapshot = BUILD_APP.create_source_snapshot(repo, revision, temp_root)

            self.assertEqual(stat.S_IMODE(temp_root.stat().st_mode), 0o700)
            self.assertFalse((snapshot / "agent_authority/ignored.local").exists())
            self.assertTrue((snapshot / "native/macos/Tests/MacAppTests/Fixture.swift").is_file())
            self.assertTrue((snapshot / "native/macos/Package.resolved").is_file())
            self.assertEqual(
                set(BUILD_APP.tracked_source_paths(repo, revision)),
                {
                    path.relative_to(snapshot).as_posix()
                    for path in snapshot.rglob("*")
                    if path.is_file()
                },
            )

    def test_export_ignore_cannot_remove_a_required_package_input(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            repo = repository(
                root / "repo",
                "native/macos/Sources/AgentAuthorityMac/main.swift export-ignore\n",
            )
            temp_root = root / "private"
            temp_root.mkdir(mode=0o700)

            with self.assertRaisesRegex(SystemExit, "does not match tracked inputs"):
                BUILD_APP.create_source_snapshot(
                    repo, BUILD_APP.clean_source_revision(repo), temp_root
                )

    def test_dirty_original_is_rejected_before_snapshot_builder_runs(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            repo = repository(root / "repo")
            (repo / "untracked.txt").write_text("dirty\n", encoding="utf-8")
            args = args_for(root)

            def should_not_build(*_):
                self.fail("builder ran for a dirty original checkout")

            with self.assertRaisesRegex(SystemExit, "dirty source tree"):
                BUILD_APP.run_snapshot_build(args, repo, should_not_build)
            self.assertFalse((args.output / "build-manifest.json").exists())

    def test_manifest_pins_the_original_revision_and_snapshot_is_cleaned(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            repo = repository(root / "repo")
            revision = git(repo, "rev-parse", "HEAD")
            args = args_for(root)
            observed = {}

            def successful_snapshot_build(build_args, source_revision, original, snapshot):
                observed["snapshot"] = snapshot
                observed["source"] = (snapshot / "agent_authority/observed.py").read_text()
                self.assertNotEqual(original.resolve(), snapshot.resolve())
                return {"app": str(build_args.output / "Agent Authority.app")}

            manifest = BUILD_APP.run_snapshot_build(args, repo, successful_snapshot_build)

            self.assertEqual(manifest["engine_sha"], revision)
            saved = json.loads((args.output / "build-manifest.json").read_text())
            self.assertEqual(saved["engine_sha"], revision)
            self.assertEqual(observed["source"], "VALUE = 'committed'\n")
            self.assertFalse(observed["snapshot"].exists())

    def test_snapshot_is_used_during_original_wip_change_and_manifest_is_blocked(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            repo = repository(root / "repo")
            args = args_for(root)
            observed = {}

            def change_original_during_build(build_args, revision, original, snapshot):
                observed["snapshot"] = snapshot
                observed["revision"] = revision
                observed["source"] = (snapshot / "agent_authority/observed.py").read_text()
                (original / "agent_authority/observed.py").write_text("VALUE = 'WIP'\n")
                observed["paths"] = (build_args.output, build_args.runtime_python)
                return {"app": str(build_args.output / "Agent Authority.app")}

            with self.assertRaisesRegex(SystemExit, "dirty source tree"):
                BUILD_APP.run_snapshot_build(args, repo, change_original_during_build)

            self.assertEqual(observed["source"], "VALUE = 'committed'\n")
            self.assertEqual(observed["revision"], git(repo, "rev-parse", "HEAD"))
            self.assertTrue(all(path.is_absolute() for path in observed["paths"]))
            self.assertFalse((args.output / "build-manifest.json").exists())
            self.assertFalse(observed["snapshot"].exists())

    def test_head_change_during_build_is_rejected_before_manifest(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            repo = repository(root / "repo")
            args = args_for(root)

            def commit_original_during_build(build_args, revision, original, snapshot):
                subprocess.run(
                    [
                        "git",
                        "-C",
                        str(original),
                        "-c",
                        "user.name=Test",
                        "-c",
                        "user.email=test@example.invalid",
                        "commit",
                        "--allow-empty",
                        "-m",
                        "new head",
                    ],
                    check=True,
                    capture_output=True,
                )
                return {"app": str(build_args.output / "Agent Authority.app")}

            with self.assertRaisesRegex(SystemExit, "Source revision changed during build"):
                BUILD_APP.run_snapshot_build(args, repo, commit_original_during_build)
            self.assertFalse((args.output / "build-manifest.json").exists())

    def test_stale_manifest_is_removed_before_app_mutation_and_never_survives_failure(self):
        for failure in ("build", "postguard"):
            with self.subTest(failure=failure), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                repo = repository(root / "repo")
                args = args_for(root)
                app = args.output / "Agent Authority.app"
                app.mkdir(parents=True)
                (app / "old-app-binary").write_text("old", encoding="utf-8")
                manifest = args.output / "build-manifest.json"
                manifest.write_text('{"engine_sha":"stale"}\n', encoding="utf-8")

                def fail_after_app_mutation(build_args, *_):
                    self.assertFalse(manifest.exists())
                    (app / "old-app-binary").write_text("partially replaced", encoding="utf-8")
                    if failure == "build":
                        raise RuntimeError("simulated build failure")
                    (repo / "agent_authority/observed.py").write_text(
                        "VALUE = 'changed during build'\n", encoding="utf-8"
                    )
                    return {"app": str(app)}

                expected = RuntimeError if failure == "build" else SystemExit
                with self.assertRaises(expected):
                    BUILD_APP.run_snapshot_build(args, repo, fail_after_app_mutation)

                self.assertFalse(manifest.exists())
                self.assertEqual(
                    (app / "old-app-binary").read_text(encoding="utf-8"),
                    "partially replaced",
                )

    def test_output_runtime_and_profiles_are_bound_before_snapshot(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            previous = Path.cwd()
            try:
                os.chdir(root)
                args = argparse.Namespace(
                    output=Path("out"),
                    runtime_python=Path("runtime/python"),
                    host_profile=Path("keys/host.provisionprofile"),
                    collector_profile=Path("keys/collector.provisionprofile"),
                )
                BUILD_APP.bind_original_paths(args)
            finally:
                os.chdir(previous)

            self.assertEqual(args.output, (root / "out").resolve())
            self.assertEqual(args.runtime_python, (root / "runtime/python").resolve())
            self.assertEqual(args.host_profile, (root / "keys/host.provisionprofile").resolve())
            self.assertEqual(
                args.collector_profile, (root / "keys/collector.provisionprofile").resolve()
            )

    def test_archive_rejects_traversal_paths_and_links(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for name, kind in [("../escape", "file"), ("inside/link", "symlink")]:
                archive_path = root / "unsafe.tar"
                with tarfile.open(archive_path, "w") as archive:
                    info = tarfile.TarInfo(name)
                    if kind == "file":
                        info.size = 4
                        archive.addfile(info, fileobj=io.BytesIO(b"test"))
                    else:
                        info.type = tarfile.SYMTYPE
                        info.linkname = "../../escape"
                        archive.addfile(info)
                destination = root / "extract"
                with self.subTest(name=name), self.assertRaises(SystemExit):
                    BUILD_APP.extract_source_archive(archive_path, destination, {"inside/file"})
                self.assertFalse(destination.exists())
                archive_path.unlink()


if __name__ == "__main__":
    unittest.main()
