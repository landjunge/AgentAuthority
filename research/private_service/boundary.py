"""Fixed one-shot verifier/signer IPC; never a network or arbitrary-code endpoint.

The local prototype uses the same UID. These process boundaries and limits do
not substitute for separate OS users, filesystem ACLs and a sandbox at deployment.
"""

import json
import os
import stat
import subprocess
import sys
from pathlib import Path

from research.private_service.limits import (
    MAX_CHILD_INPUT,
    MAX_CHILD_OUTPUT,
    process_limits,
    remaining,
)
from research.private_service.protocol import AUDIENCE, Problem, fields, identifier, parse, require

ROOT = Path(__file__).resolve().parents[2]


def run_component(operation, value, keyfile=None):
    require(operation in ("verify", "report"), 503, "COMPONENT_FORBIDDEN")
    raw = json.dumps(value).encode()
    require(len(raw) <= MAX_CHILD_INPUT, 413, "COMPONENT_INPUT_LIMIT")
    command = [sys.executable, "-m", "research.private_service.boundary", operation]
    if keyfile is not None:
        command.append(str(keyfile))  # trusted bootstrap path, never an HTTP field
    try:
        with subprocess.Popen(
            command,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            cwd=ROOT,
            env={"PATH": os.defpath, "PYTHONDONTWRITEBYTECODE": "1"},
            close_fds=True,
            start_new_session=True,
        ) as child:
            try:
                output, _ = child.communicate(raw, timeout=remaining())
            except BaseException:
                child.kill()
                child.communicate()
                raise
            require(child.returncode == 0, 503, "COMPONENT_FAILED")
        require(len(output) <= MAX_CHILD_OUTPUT, 503, "COMPONENT_OUTPUT_LIMIT")
        return parse(output)
    except subprocess.TimeoutExpired as error:
        raise Problem(503, "COMPONENT_TIMEOUT") from error


def report_policy(body):
    require(type(body) is dict, 422, "REPORT_POLICY")
    common = {
        "schema",
        "domain",
        "audience",
        "signing_kid",
        "tenant",
        "job_id",
        "classification",
        "verifier_version",
        "trust_catalog_version",
        "issued_ms",
        "scope",
        "provider_model_session",
        "uncertainties",
        "grants_rights",
        "completed_at",
        "expires_at",
        "report_version",
    }
    unknown = {"reason", "sources"}
    measured = {
        "verifier_sha256",
        "normalization",
        "job_sha256",
        "acceptance_sha256",
        "source",
        "checks",
        "critical_loss_metrics",
        "reasons",
        "layers",
        "trust_basis",
    }
    require(set(body) in (common | unknown, common | measured), 422, "REPORT_POLICY")
    identifier(body["tenant"])
    require(
        len(body["job_id"]) == 32 and all(c in "0123456789abcdef" for c in body["job_id"]),
        422,
        "REPORT_POLICY",
    )
    require(
        body["schema"] == "aa-report-v1"
        and body["domain"] == "AA-REPORT-v1"
        and body["audience"] == AUDIENCE
        and body["signing_kid"] == "local-report-v1"
        and body["scope"] == "controlled-a4-write16"
        and body["grants_rights"] is False
        and body["provider_model_session"] == "UNBEKANNT"
        and body["report_version"] == "1"
        and body["classification"] in ("UNBEKANNT", "UNVOLLSTAENDIG", "WIDERSPRUECHLICH", "BELEGT"),
        422,
        "REPORT_POLICY",
    )
    if "reason" in body:
        require(
            body["classification"] == "UNBEKANNT" and body["sources"] == [], 422, "REPORT_POLICY"
        )
        require(
            body["reason"]
            in (
                "RUNNER_OR_INTAKE_ERROR",
                "KEY_REVOKED_DURING_RUN",
                "KEY_REVOKED_BEFORE_RUN",
                "WORKER_INTERRUPTED",
                "WORKER_TIMEOUT",
                "REQUEST_EXPIRED",
                "CANCELLED_NO_RERUN",
                "KEY_REVOKED",
                "KEY_EXPIRED",
                "EXPIRED_OR_FUTURE",
            ),
            422,
            "REPORT_POLICY",
        )
    if body["classification"] == "BELEGT":
        checks, loss = body["checks"], body["critical_loss_metrics"]
        require(len(checks) == 28 and all(v is True for v in checks.values()), 422, "REPORT_POLICY")
        require(
            len(loss) == 23 and all(type(v) is int and v == 0 for v in loss.values()),
            422,
            "REPORT_POLICY",
        )


class ReportSigner:
    def __init__(self, keyfile):
        # No private bytes are loaded into the API process. No client-selected path.
        path = Path(keyfile).absolute()
        require(not any(p.is_symlink() for p in (path, *path.parents)), 503, "UNSAFE_SIGNER_KEY")
        mode = path.stat()
        require(
            stat.S_ISREG(mode.st_mode)
            and mode.st_uid == os.getuid()
            and stat.S_IMODE(mode.st_mode) == 0o600
            and mode.st_nlink == 1,
            503,
            "UNSAFE_SIGNER_KEY",
        )
        self._keyfile = path

    def __call__(self, body):
        report_policy(body)
        return run_component("report", body, self._keyfile)


def main():
    process_limits(child=True)
    operation = sys.argv[1]
    raw = sys.stdin.buffer.read(MAX_CHILD_INPUT + 1)
    require(len(raw) <= MAX_CHILD_INPUT, 413, "COMPONENT_INPUT_LIMIT")
    value = parse(raw)
    if operation == "report":
        report_policy(value)
        key = ReportSigner(sys.argv[2])._keyfile
        from research.private_service.crypto import sign

        result = sign(key, value)
    elif operation == "verify":
        fields(value, "payload pins expected")
        from research.private_service.verifier import evaluate_evidence

        result = evaluate_evidence(value["payload"], value["pins"], value["expected"])
    else:
        raise Problem(422, "COMPONENT_FORBIDDEN")
    output = json.dumps(result).encode()
    require(len(output) <= MAX_CHILD_OUTPUT, 503, "COMPONENT_OUTPUT_LIMIT")
    sys.stdout.buffer.write(output)


if __name__ == "__main__":
    try:
        main()
    except Exception:  # noqa: BLE001 - isolated boundary emits no free error text
        sys.exit(1)  # no payloads, key material, paths or exception text
