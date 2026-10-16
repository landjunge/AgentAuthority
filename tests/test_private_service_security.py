"""Authorized negative cases against our own synthetic loopback service only."""

import copy
import hashlib
import json
import os
import secrets
import socket
import subprocess
import sys
import threading
import time
from pathlib import Path
from urllib.request import urlopen

import pytest
import test_private_service as contracts
from test_private_service import new_job, queue_job
from test_private_service_retention import complete, receipt

from research.private_service.boundary import ReportSigner, report_policy, run_component
from research.private_service.configuration import api_configuration
from research.private_service.http import HEADER_BYTES
from research.private_service.limits import DEADLINE, HTTP_SECONDS, unprivileged
from research.private_service.protocol import (
    Problem,
    blob,
    blob_digest,
    parse,
    sign,
    verify,
)


@pytest.fixture
def api(tmp_path):
    yield from contracts.api.__wrapped__(tmp_path)


@pytest.fixture
def actual_evidence(api):
    return contracts.actual_evidence.__wrapped__(api)


def token(api, role="client"):
    return next(t["token"] for t in api[4]["tokens"] if t["role"] == role)


def wire(api, raw):
    port = int(api[6].rsplit(":", 1)[1])
    with socket.create_connection(("127.0.0.1", port), timeout=8) as sock:
        sock.sendall(raw.replace(b"PORT", str(port).encode()))
        data = bytearray()
        while chunk := sock.recv(65536):
            data.extend(chunk)
    return bytes(data)


@pytest.mark.parametrize(
    "paths",
    [
        ["/.git/HEAD", "/.git/config", "/.git/objects/", "/research/private_service/service.py"],
        [
            "/config.json",
            "/.env",
            "/api-config.json",
            "/root/ca-private.pem",
            "/report/ca-private.pem",
        ],
        [
            "/service.sqlite",
            "/service.sqlite-wal",
            "/service.sqlite-shm",
            "/service.sqlite-journal",
        ],
        [
            "/backup.zip",
            "/source.tar.gz",
            "/archives/agent-authority/README.md",
            "/tmp/report.json",
        ],
        [
            "/../config.json",
            "/%2e%2e/config.json",
            "/%252e%252e/config.json",
            "/a/../../.git/HEAD",
            "/\\..\\config.json",
        ],
        [
            "/v1/graph",
            "/v1/jobs?tenant=test-b",
            "/v1/sign",
            "/sign",
            "/download",
            "/inspector.js/config.json",
        ],
    ],
)
def test_only_explicit_routes_no_source_secret_backup_or_traversal(api, paths):
    # An authenticated client gets no general file server either.
    for path in paths:
        raw = (
            "GET "
            + path
            + " HTTP/1.1\r\nHost: 127.0.0.1:PORT\r\nAuthorization: Bearer "
            + token(api)
            + "\r\n\r\n"
        ).encode()
        response = wire(api, raw)
        assert response.startswith(b"HTTP/1.0 404")
        assert b"NOT_FOUND" in response and b"PRIVATE KEY" not in response
        assert b"SQLite format" not in response and b"Traceback" not in response


def test_symlink_alias_never_served_or_followed(api):
    link = api[0].state / "inspector.js"
    link.symlink_to(api[4]["report_private_key"])
    try:
        with urlopen(api[6] + "/inspector.js", timeout=5) as response:
            script = response.read()
        assert b"textContent" in script and b"PRIVATE KEY" not in script
    finally:
        link.unlink()


@pytest.mark.parametrize(
    "headers,status",
    [
        (b"Host: evil.invalid\r\n", 400),
        (b"Authorization: Bearer secret-marker\r\n", 400),
        (b"Content-Length: 1\r\nContent-Length: 2\r\n", 400),
        (b"Transfer-Encoding: chunked\r\n", 400),
        (b"Content-Encoding: gzip\r\n", 415),
        (b"Expect: 100-continue\r\n", 417),
        (b"Origin: https://foreign.invalid\r\n", 403),
        (b"X-Test: x\r\n folded-secret-marker\r\n", 431),
        (b"X-Test: " + b"x" * HEADER_BYTES + b"\r\n", 431),
    ],
)
def test_http_ambiguous_framing_headers_and_origin(api, headers, status):
    response = wire(
        api,
        b"GET / HTTP/1.1\r\nHost: 127.0.0.1:PORT\r\nAuthorization: Bearer "
        + token(api).encode()
        + b"\r\n"
        + headers
        + b"\r\n",
    )
    assert response.startswith(f"HTTP/1.0 {status}".encode())
    assert b"secret-marker" not in response and b"Traceback" not in response


@pytest.mark.parametrize(
    "method,path",
    [
        ("DELETE", "/v1/jobs/unknown"),
        ("PUT", "/v1/jobs"),
        ("PATCH", "/v1/jobs"),
        ("POST", "/inspector.js"),
        ("GET", "/v1/revocations"),
        ("GET", "/v1/jobs/unknown/evidence"),
    ],
)
def test_unsupported_methods_and_route_combinations(api, method, path):
    result = wire(api, f"{method} {path} HTTP/1.1\r\nHost: 127.0.0.1:PORT\r\n\r\n".encode())
    assert result.startswith(b"HTTP/1.0 405")


def test_long_request_line_is_sanitized(api):
    result = wire(api, b"GET /" + b"secret-marker" * 200 + b" HTTP/1.1\r\n\r\n")
    assert result.startswith(b"HTTP/1.0 414") and b"secret-marker" not in result


@pytest.mark.parametrize(
    "value",
    [
        {"x": list(range(4097))},
        {str(k): k for k in range(129)},
        {"x": "a" * 196609},
        [[list(range(4000)) for _ in range(6)]],
    ],
)
def test_parser_width_string_and_total_node_limits(value):
    with pytest.raises(Problem):
        parse(json.dumps(value).encode())


def test_outer_and_base64_legacy_depth_duplicates_and_nonfinite(api, actual_evidence):
    jid, row, original = actual_evidence
    for raw in (b"[" * 35 + b"0" + b"]" * 35, b'{"x":1,"x":2}', b'{"x":NaN}', b"null"):
        package = copy.deepcopy(original)
        package["registry"] = blob(raw)
        package["manifest"]["registry_sha256"] = blob_digest(package["registry"])
        report = api[0].verify_evidence(
            "test-a", jid, row, package, int(time.time() * 1000), "runner"
        )
        assert report["classification"] == "UNVOLLSTAENDIG"
        assert report["layers"]["independent_write"] == "UNBEKANNT"
    with pytest.raises(Problem):
        parse(b"[" * 35 + b"0" + b"]" * 35)


@pytest.mark.parametrize(
    "field,value",
    [
        ("scenario", "shell"),
        ("command", "id"),
        ("path", "/etc/passwd"),
        ("url", "http://foreign.invalid"),
        ("code", "print(1)"),
        ("filename", "../backup"),
    ],
)
def test_synthetic_actions_reject_code_shell_paths_and_net_targets(api, field, value):
    payload = {"scenario": "a4-write16-v1", "receiver_kid": "receiver", field: value}
    packet = api[2]("sender", "/v1/jobs", payload)
    assert api[1]("client", "POST", "/v1/jobs", packet)[0] == 422
    with api[0].connection() as db:
        assert db.execute("SELECT count(*) FROM jobs").fetchone() == (0,)


def test_same_tenant_object_read_and_cached_write_are_scoped(api):
    signed, job = new_job(api)
    outsider = secrets.token_hex(32)
    api[0].config["tokens"].append(
        {
            "tenant": "test-a",
            "role": "client",
            "subjects": ["outsider"],
            "sha256": hashlib.sha256(outsider.encode()).hexdigest(),
        }
    )
    from research.private_service.http import call

    for path in (job["status_url"], job["report_url"]):
        assert call(api[6], outsider, "GET", path)[0] == 404
    # Even exact idempotency-cache hits must pass the current bearer subject ACL.
    assert call(api[6], outsider, "POST", "/v1/jobs", signed)[0] == 403
    for operation in ("receipts", "cancellations", "acceptances"):
        path = job["status_url"] + "/" + operation
        packet = api[2]("sender", path, {"job_id": job["job_id"]})
        assert call(api[6], outsider, "POST", path, packet)[0] == 403
    assert api[1]("client", "GET", job["status_url"])[0] == 200


def test_foreign_tenant_cannot_read_delete_or_reach_cached_response(api):
    _, job, report = complete(api)
    path, signed = receipt(api, job, report)
    assert api[1]("reader", "POST", path, signed)[0] == 403
    for route in (job["status_url"], job["report_url"]):
        assert api[1]("reader", "GET", route)[0] == 404
    assert api[1]("client", "GET", job["report_url"])[0] == 200


def test_runner_revocation_finishes_current_job_without_positive_result(api):
    _, job, _ = queue_job(api)
    assert api[0].claim()
    signed = api[2]("sender", "/v1/revocations", {"kid": "runner"})
    assert api[1]("admin", "POST", "/v1/revocations", signed)[0] == 200
    result = api[1]("client", "GET", job["report_url"])[1]["report"]
    assert result["body"]["classification"] == "UNBEKANNT"
    assert result["body"]["reason"] == "KEY_REVOKED_DURING_RUN"
    path = job["status_url"] + "/evidence"
    assert api[1]("runner", "POST", path, api[2]("runner", path, {}))[1]["code"] == "KEY_REVOKED"


def test_api_config_contains_no_signer_client_runner_credentials(api, monkeypatch):
    _, job, _ = queue_job(api)  # Client signs before observing the API's reads.
    raw = json.dumps(api[0].config)
    for entry in api[4]["tokens"]:
        assert entry["token"] not in raw
    for name in ("report_private_key", "client_private_key", "runner_private_key", "runner_token"):
        assert name not in api[0].config
    old_read = Path.read_bytes

    def no_private_read(path):
        assert path.suffix != ".pem", "private key read by API process"
        return old_read(path)

    monkeypatch.setattr(Path, "read_bytes", no_private_read)
    assert api[0].claim()
    api[0].recover()
    report = api[1]("client", "GET", job["report_url"])[1]
    assert verify(api[4]["report_public_key"], report["report"])
    assert api[1]("client", "GET", job["report_url"])[0] == 200


def test_signer_is_report_only_and_rejects_extra_fields_or_action_rights(api):
    _, _, response = complete(api)
    body = response["report"]["body"]
    for changes in ({"domain": "AA-REQUEST-v1"}, {"grants_rights": True}, {"arbitrary": "data"}):
        bad = {**body, **changes}
        with pytest.raises(Problem):
            report_policy(bad)
        with pytest.raises(Problem, match="COMPONENT_FAILED"):
            run_component("report", bad, api[4]["report_private_key"])


def test_signer_refuses_symlink_world_readable_and_hardlink_keys(api, tmp_path):
    original = Path(api[4]["report_private_key"])
    link = tmp_path / "key-link"
    link.symlink_to(original)
    with pytest.raises(Problem):
        ReportSigner(link)
    link.unlink()
    os.link(original, link)
    with pytest.raises(Problem):
        ReportSigner(original)
    link.unlink()
    original.chmod(0o644)
    try:
        with pytest.raises(Problem):
            ReportSigner(original)
    finally:
        original.chmod(0o600)


def test_technical_errors_contain_no_paths_tokens_or_payload(api, monkeypatch, capfd):
    signed, _ = new_job(api)
    secret = "secret-marker-" + token(api)

    def fail(*args):
        raise RuntimeError(secret + "/private/source.py")

    monkeypatch.setattr(api[0], "mutate", fail)
    status, result = api[1]("client", "POST", "/v1/jobs", signed)
    assert status == 500 and set(result) == {"type", "title", "status", "code"}
    captured = capfd.readouterr()
    assert secret not in json.dumps(result) + captured.out + captured.err


@pytest.mark.parametrize("phase", ["headers", "body"])
def test_absolute_slow_client_deadline_releases_server_and_no_job(api, phase):
    port = int(api[6].rsplit(":", 1)[1])
    with socket.create_connection(("127.0.0.1", port), timeout=8) as slow:
        prefix = f"POST /v1/jobs HTTP/1.1\r\nHost: 127.0.0.1:{port}\r\n"
        if phase == "body":
            prefix += f"Authorization: Bearer {token(api)}\r\nContent-Type: application/json\r\nContent-Length: 100\r\n\r\n"
        slow.sendall(prefix.encode())
        begin = time.monotonic()

        def drip():
            while time.monotonic() - begin < HTTP_SECONDS + 2:
                try:
                    slow.sendall(b" ")
                except OSError:
                    return
                time.sleep(0.4)

        thread = threading.Thread(target=drip)
        thread.start()
        # Body/header intake does not own the cross-process lifecycle lock.
        with api[0].exclusive():
            pass
        slow.recv(65536)
        elapsed = time.monotonic() - begin
        thread.join(3)
        assert HTTP_SECONDS - 0.5 <= elapsed < HTTP_SECONDS + 2
    with urlopen(api[6], timeout=3) as response:
        assert response.status == 200
    with api[0].connection() as db:
        assert db.execute("SELECT count(*) FROM jobs").fetchone() == (0,)


def test_expired_processing_budget_kills_and_reaps_component(api, monkeypatch):
    _, _, response = complete(api)
    children = []
    original = subprocess.Popen

    def track(*args, **kwargs):
        child = original(*args, **kwargs)
        children.append(child)
        return child

    monkeypatch.setattr(subprocess, "Popen", track)
    handle = DEADLINE.set(time.monotonic() + 0.001)
    try:
        with pytest.raises(Problem) as caught:
            run_component("report", response["report"]["body"], api[4]["report_private_key"])
        assert caught.value.code in ("COMPONENT_TIMEOUT", "REQUEST_TIMEOUT")
    finally:
        DEADLINE.reset(handle)
    assert len(children) == 1 and children[0].poll() is not None


def test_root_api_start_is_refused(monkeypatch):
    monkeypatch.setattr(os, "geteuid", lambda: 0)
    with pytest.raises(Problem, match="PRIVILEGED_API_FORBIDDEN"):
        unprivileged()


def test_real_child_cpu_limit_and_no_secret_diagnostics():
    code = "from research.private_service.limits import process_limits; process_limits(True)\nwhile True: pass\n"
    begin = time.monotonic()
    result = subprocess.run(
        [sys.executable, "-c", code], capture_output=True, timeout=8, check=False
    )
    assert result.returncode < 0 and time.monotonic() - begin < 8
    assert result.stdout == b"" and result.stderr == b""


def test_actual_cli_scoped_config_loopback_and_limits(api, tmp_path):
    configfile = tmp_path / "api.json"
    configfile.write_text(json.dumps(api_configuration(api[4])))
    configfile.chmod(0o600)
    # Separate read-only inspector process on the same existing synthetic state.
    command = [
        sys.executable,
        "-m",
        "research.private_service.http",
        "--state",
        str(api[0].state),
        "--config",
        str(configfile),
        "--signer-key",
        api[4]["report_private_key"],
        "--port",
        "0",
    ]
    with subprocess.Popen(
        command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
    ) as child:
        try:
            import select

            assert select.select([child.stdout], [], [], 5)[0]
            line = child.stdout.readline().strip()
            assert line.startswith("Private inspector: http://127.0.0.1:")
            with urlopen(line.split(" ", 2)[2], timeout=5) as response:
                assert response.status == 200
        finally:
            child.terminate()
            _, error = child.communicate(timeout=5)
            assert error == ""
            configfile.unlink()


@pytest.mark.parametrize(
    "mutation,status,code",
    [
        ("missing", 422, "INVALID_FORMAT"),
        ("empty", 401, "SIGNATURE_INVALID"),
        ("wrong-key", 401, "SIGNATURE_INVALID"),
        ("changed", 401, "SIGNATURE_INVALID"),
        ("expired", 410, "EXPIRED_OR_FUTURE"),
        ("schema", 422, "TARGET_MISMATCH"),
        ("path", 422, "TARGET_MISMATCH"),
        ("audience", 422, "TARGET_MISMATCH"),
    ],
)
def test_signature_and_version_adversarial_matrix(api, mutation, status, code):
    signed = api[2]("sender", "/v1/jobs", {"scenario": "a4-write16-v1", "receiver_kid": "receiver"})
    if mutation == "missing":
        del signed["signature"]
    elif mutation == "empty":
        signed["signature"] = ""
    elif mutation == "wrong-key":
        signed = sign(api[5]["receiver"]["private"], signed["body"])
    elif mutation == "changed":
        signed["body"]["payload"]["receiver_kid"] = "sender"
    else:
        changes = {
            "expired": {"issued_ms": 1, "expires_ms": 60001},
            "schema": {"schema": "aa-private-v2"},
            "path": {"path": "/v1/revocations"},
            "audience": {"audience": "other-service"},
        }[mutation]
        signed = sign(api[5]["sender"]["private"], {**signed["body"], **changes})
    actual, problem = api[1]("client", "POST", "/v1/jobs", signed)
    assert (actual, problem["code"]) == (status, code)
    with api[0].connection() as db:
        assert db.execute("SELECT count(*) FROM jobs").fetchone() == (0,)


def test_job_parallelism_limit_and_slot_release(api):
    jobs = [new_job(api)[1] for _ in range(16)]
    packet = api[2]("sender", "/v1/jobs", {"scenario": "a4-write16-v1", "receiver_kid": "receiver"})
    assert api[1]("client", "POST", "/v1/jobs", packet)[1]["code"] == "QUEUE_FULL"
    path = jobs[0]["status_url"] + "/cancellations"
    assert (
        api[1]("client", "POST", path, api[2]("sender", path, {"job_id": jobs[0]["job_id"]}))[0]
        == 200
    )
    assert api[1]("client", "POST", "/v1/jobs", packet)[0] == 202
    assert api[0].claim() is None  # none were accepted; no implicit execution


@pytest.mark.parametrize(
    "which,limit,code",
    [
        ("MAX_REQUEST_RECORDS", 6, "REQUEST_CAPACITY"),
        ("MAX_JOB_RECORDS", 0, "JOB_CAPACITY"),
    ],
)
def test_storage_capacity_fails_closed_without_recording_failed_request(
    api, monkeypatch, which, limit, code
):
    import research.private_service.service as module

    monkeypatch.setattr(module, which, limit)
    signed = api[2]("sender", "/v1/jobs", {"scenario": "a4-write16-v1", "receiver_kid": "receiver"})
    assert api[1]("client", "POST", "/v1/jobs", signed)[1]["code"] == code
    with api[0].connection() as db:
        assert db.execute("SELECT count(*) FROM jobs").fetchone() == (0,)


def test_tenant_rate_limit_is_bounded_and_recovers(api, monkeypatch):
    import research.private_service.http as module

    # A fresh server makes the rate budget explicit, without 120 noisy writes.
    instance = module.server(api[0])
    try:
        clock = [100.0]
        monkeypatch.setattr(module.time, "monotonic", lambda: clock[0])
        for _ in range(120):
            instance.rate("test-a")
        with pytest.raises(Problem, match="RATE_LIMIT"):
            instance.rate("test-a")
        assert len(instance.rates["test-a"]) == 120
        clock[0] += 60
        instance.rate("test-a")
        assert len(instance.rates["test-a"]) == 1
    finally:
        instance.server_close()


def test_original_http_duplicate_host_and_sliding_timeout_reproduced(api):
    """Execute only the pinned old adapter in our own loopback fixture.

    This is an intentionally vulnerable pre-fix reproduction, no production test.
    The current adapter is tested separately for rejection/absolute timeout.
    """
    import types

    source = subprocess.check_output(
        ["git", "show", "09bc5f2:research/private_service/http.py"], timeout=5
    )
    module = types.ModuleType("aa_original_http_security_reproduction")
    exec(compile(source, "<pinned-private-http-09bc5f2>", "exec"), module.__dict__)  # noqa: S102 - fixed trusted historical source
    old = module.server(api[0])
    thread = threading.Thread(target=old.serve_forever, daemon=True)
    thread.start()
    old_api = (*api[:6], f"http://127.0.0.1:{old.server_port}")
    try:
        response = wire(
            old_api, b"GET / HTTP/1.1\r\nHost: 127.0.0.1:PORT\r\nHost: foreign.invalid\r\n\r\n"
        )
        assert response.startswith(b"HTTP/1.0 200")
        with socket.create_connection(("127.0.0.1", old.server_port), timeout=8) as sock:
            begin = time.monotonic()
            sock.sendall(b"GET / HTTP/1.1\r\n")
            time.sleep(3)
            sock.sendall(f"Host: 127.0.0.1:{old.server_port}\r\n".encode())
            time.sleep(3)
            sock.sendall(b"\r\n")
            response = sock.recv(8192)
            assert response.startswith(b"HTTP/1.0 200") and time.monotonic() - begin > HTTP_SECONDS
    finally:
        old.shutdown()
        thread.join(5)
        old.server_close()


@pytest.mark.parametrize(
    "url",
    [
        "http://127.0.0.1:8765@foreign.invalid",
        "http://foreign.invalid:8765",
        "http://127.0.0.1:8765/path",
        "http://127.0.0.1:8765?target=foreign",
        "http://127.0.0.1:8765#x",
        "https://127.0.0.1:8765",
        "http://127.0.0.1:\n8765",
    ],
)
def test_local_client_rejects_ambiguous_net_target_before_connection(url):
    from research.private_service.http import call

    with pytest.raises(Problem):
        call(url, "unused", "GET", "/v1/privacy")


def test_http_rate_limit_is_applied_to_actual_requests(api):
    successes = 0
    for _ in range(121):
        response = wire(api, b"GET /inspector.js HTTP/1.1\r\nHost: 127.0.0.1:PORT\r\n\r\n")
        if response.startswith(b"HTTP/1.0 429"):
            assert b"RATE_LIMIT" in response
            break
        assert response.startswith(b"HTTP/1.0 200")
        successes += 1
    else:
        pytest.fail("HTTP rate limit missing")
    assert 0 < successes <= 120


def test_real_cross_process_lock_timeout_and_release(api):
    code = "import fcntl,sys; f=open(sys.argv[1],'a'); fcntl.flock(f,fcntl.LOCK_EX); print('locked',flush=True); sys.stdin.read()"
    command = [sys.executable, "-c", code, str(api[0].state / ".lifecycle.lock")]
    with subprocess.Popen(
        command, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE
    ) as holder:
        try:
            import select

            assert select.select([holder.stdout], [], [], 5)[0]
            assert holder.stdout.readline() == b"locked\n"
            begin = time.monotonic()
            with pytest.raises(Problem, match="STORAGE_BUSY"), api[0].exclusive():
                pytest.fail("acquired held process lock")
            assert 0.8 <= time.monotonic() - begin < 2
        finally:
            holder.communicate(timeout=5)
    with api[0].exclusive():
        pass


def test_verifier_timeout_cannot_commit_a_positive_report(api, monkeypatch):
    _, job, _ = queue_job(api)
    assert api[0].claim()

    def timeout(*args):
        raise Problem(503, "COMPONENT_TIMEOUT")

    monkeypatch.setattr(api[0], "verify_evidence", timeout)
    path = job["status_url"] + "/evidence"
    result = api[1]("runner", "POST", path, api[2]("runner", path, {}))
    assert result[0] == 503 and result[1]["code"] == "COMPONENT_TIMEOUT"
    assert api[1]("client", "GET", job["report_url"])[1]["code"] == "REPORT_PENDING"
    path = job["status_url"] + "/cancellations"
    assert (
        api[1]("client", "POST", path, api[2]("sender", path, {"job_id": job["job_id"]}))[0] == 200
    )
    assert (
        api[1]("client", "GET", job["report_url"])[1]["report"]["body"]["classification"]
        == "UNBEKANNT"
    )


@pytest.mark.parametrize("old_kid", ["sender", "runner"])
def test_rotation_invalidates_running_job_atomically(api, old_kid):
    from research.private_service.protocol import create_ca

    _, job, _ = queue_job(api)
    assert api[0].claim()
    new_kid = "rotated-" + old_kid
    key, public = create_ca(api[0].state / new_kid)
    api[5][new_kid] = {"private": str(key), "public": public}
    packet = api[3](new_kid, replaces=old_kid)
    if old_kid == "runner":
        cert = packet["body"]["payload"]["certificate"]["body"]
        cert["role"] = "runner"
        packet["body"]["payload"]["certificate"] = sign(api[0].state / "root/ca-private.pem", cert)
        packet = sign(key, packet["body"])
    assert api[1]("admin", "POST", "/v1/enrollments", packet)[0] == 201
    result = api[1]("client", "GET", job["report_url"])[1]["report"]["body"]
    assert result["classification"] == "UNBEKANNT" and result["reason"] == "KEY_REVOKED_DURING_RUN"
