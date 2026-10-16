"""One isolated A4-completion repetition; measurement sources remain unchanged."""

import argparse
import hashlib
import importlib.util
import json
import os
import secrets
import select
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "research/a4_completion"))
spec = importlib.util.spec_from_file_location("original_completion_driver", ROOT / "research/a4_completion/driver.py")
driver = importlib.util.module_from_spec(spec)
spec.loader.exec_module(driver)


def dump(path, value):
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")


def run(out):
    os.chdir(ROOT)
    pins = driver.prepare(out)
    dump(out / "attempt.json", {
        "attempts": 1, "controlled_test_agents": 2,
        "source_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip(),
        "harness_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "protocol_sha256": hashlib.sha256((ROOT / "docs/HOSTED-QUALIFICATION-PROTOCOL-20261016.md").read_bytes()).hexdigest(),
    })
    target = "/var/tmp/a1-research-a4-" + pins["run_id"] + "/" + secrets.token_hex(16)
    observer = None
    first = b""
    try:
        driver.guest(["sudo", "-n", "python3", "-c",
                      "import os,pathlib,sys;p=pathlib.Path(sys.argv[1]);p.parent.mkdir(mode=0o755);p.touch(exist_ok=False);os.chmod(p,0o666)", target])
        observer = subprocess.Popen(driver.BASE + ["sudo", "-n", "python3", "-B",
                                    pins["scope"] + "/observer.py", target, "--duration", "12"],
                                    env=driver.ENV, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if not select.select([observer.stdout], [], [], 45)[0]:
            raise TimeoutError("observer readiness")
        first = observer.stdout.readline()
        if not json.loads(first).get("ready"):
            raise ValueError("observer did not become ready")
        for source, expected in pins["source_sha256"].items():
            if hashlib.sha256(Path(source).read_bytes()).hexdigest() != expected:
                raise ValueError("source changed before trial")
        trial = subprocess.run(driver.BASE + ["sudo", "-n", "python3", "-B",
                               pins["scope"] + "/guest.py", "trial", pins["vault"],
                               "--certificate", pins["certificate"], "--path", target],
                               env=driver.ENV, capture_output=True, timeout=35, check=False)
        (out / "trial.stdout.json").write_bytes(trial.stdout)
        (out / "trial.stderr.log").write_bytes(trial.stderr)
        rest, errors = observer.communicate(timeout=20)
        (out / "capture.jsonl").write_bytes(first + rest)
        (out / "observer.stderr.log").write_bytes(errors)
        dump(out / "process-status.json", {"observer_exit": observer.returncode, "trial_exit": trial.returncode})
        if trial.returncode or observer.returncode:
            raise RuntimeError("live trial failed; no retry")
        result = driver.evaluate(json.loads((out / "registry.json").read_text()),
                                 [json.loads(line) for line in (first + rest).splitlines()],
                                 json.loads(trial.stdout), pins["pinned_ca_public_key"])
        # Existing verifier's phase2_authorized_by_gate is a historical test label,
        # never an instruction to start another cohort or a product permission.
        dump(out / "evaluation.json", result)
        print(json.dumps({"gate": result["full_chain_gate"],
                          "checks": len(result["checks"]),
                          "failed_checks": [k for k, v in result["checks"].items() if v is not True],
                          "critical_loss_fields": len(result["critical_loss_metrics"])}))
    except Exception as error:
        dump(out / "failure.json", {"type": type(error).__name__, "message": str(error),
                                    "classification": "UNBEKANNT", "retry": False})
        raise
    finally:
        if observer is not None and observer.poll() is None:
            rest, errors = observer.communicate(timeout=25)
            (out / "capture.jsonl").write_bytes(first + rest)
            (out / "observer.stderr.log").write_bytes(errors)
        cleanup = """
import json,os,pathlib,sys
vault,scope,target,run_id=map(str,sys.argv[1:])
v=pathlib.Path(vault)
assert v.name=='a4c-private-'+run_id and v.parent==pathlib.Path('/var/tmp')
assert set(p.name for p in v.iterdir())=={'registrar','TestA','TestB'}
assert all(p.is_file() and not p.is_symlink() for p in v.iterdir())
for name in ['registrar','TestA','TestB']: (v/name).unlink()
v.rmdir()
recovery=pathlib.Path('/var/tmp/aa-hosted-recovery-'+run_id)
recovery.mkdir(mode=0o700)
assert scope=='/opt/a4c-'+run_id
assert pathlib.Path(target).parent==pathlib.Path('/var/tmp/a1-research-a4-'+run_id)
os.rename(scope,recovery/'sources')
os.rename(pathlib.Path(target).parent,recovery/'synthetic-target')
print(json.dumps({'private_guest_files_removed':3,'nonsecret_recovery':str(recovery)}))
"""
        cleanup_result = json.loads(driver.guest(["sudo", "-n", "python3", "-c", cleanup,
                                                  pins["vault"], pins["scope"], target, pins["run_id"]]).stdout)
        private = Path("/tmp/a4-private-host-" + pins["run_id"])
        assert set(p.name for p in private.iterdir()) == {"ca-private.pem"}
        assert not (private / "ca-private.pem").is_symlink()
        (private / "ca-private.pem").unlink()
        private.rmdir()
        cleanup_result.update(host_private_ca_removed=True, keys_archived=False,
                              secure_ram_or_ssd_erasure_proven=False)
        dump(out / "cleanup.json", cleanup_result)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("output", type=Path)
    run(parser.parse_args().output.resolve())
