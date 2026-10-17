"""Check one actual browser zipapp in a private disposable loopback process.

stdlib only; no installation, deployment, external service or browser execution.
Credentials and HTTP responses stay in memory. The evidence contains only fixed
check names, booleans, counts and versions. Never print subprocess output/errors.
"""

from __future__ import annotations

import argparse
import base64
import hashlib
import http.client
import json
import os
import platform
import re
import selectors
import signal
import socket
import subprocess
import sys
import tempfile
import time
import zipfile
from pathlib import Path
from typing import Any

CHECKS = (
    "package_manifest",
    "package_hashes",
    "package_state_files_excluded",
    "package_static_files",
    "synthetic_init",
    "synthetic_examples",
    "service_start",
    "static_http",
    "anonymous_denied",
    "synthetic_login",
    "live_logout",
    "revoked_cookie_denied",
    "fresh_login_after_logout",
    "empty_accounts",
    "neutral_import",
    "neutral_model_and_foreign_text",
    "owner_isolation",
    "source_job_isolation",
    "source_isolation",
    "job_isolation",
    "adapter_isolation",
    "csrf_denied",
    "duplicate_json_denied",
    "private_import",
    "private_report_unverified",
    "private_owner_isolation",
    "report_states_listing",
    "production_blocked",
    "status_process_queue_limits",
    "second_instance_denied",
    "first_instance_healthy",
    "explicit_demo",
    "demo_does_not_create_report",
    "package_credentials_absent",
    "first_sigterm",
    "first_port_closed",
    "restart",
    "sessions_not_persisted",
    "report_persisted",
    "final_sigterm",
    "final_port_closed",
    "package_repository_modules",
    "repository_state_roundtrip",
    "atomic_quota",
    "temporary_directory_removed",
    "own_processes_reaped",
)


# This narrowly scoped child probe imports the actual checked archive, never the
# repository checkout. Its two private stores are separate from the HTTP store.
# Only fixed booleans/counts leave the process, including on unexpected failure.
REPOSITORY_PROBE = r"""
import hashlib
import json
import os
import sys
import threading
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

names = ('package_repository_modules', 'repository_state_roundtrip', 'atomic_quota')
result = {
    'checks': {name: False for name in names},
    'executed': {name: False for name in names},
    'counts': {'quotaReports': 0, 'quotaInserted': 0, 'quotaRejected': 0,
               'quotaConnections': 0, 'repositoryStates': 0},
}
repositories = []

def check(name, condition):
    result['executed'][name] = True
    result['checks'][name] = bool(condition)
    if not condition:
        raise RuntimeError()

def payload(number, adapter='observations', state=None):
    value = {
        'metadata': {
            'id': f'{number:032x}', 'sourceId': 'synthetic-source',
            'jobId': 'synthetic-job', 'adapter': adapter,
            'createdAt': '2026-10-17T07:00:00+00:00',
        },
        'report': {'claim': 'synthetic, unauthenticated'},
        'graph': {'nodes': [{'id': 'entry-1'}]},
    }
    if state is not None:
        value['metadata']['state'] = state
    return value

try:
    os.umask(0o077)
    package = Path(sys.argv[1]).resolve()
    root = Path(sys.argv[2])
    root.mkdir(mode=0o700)
    sys.path.insert(0, str(package))
    import agent_authority.browser_contracts as contracts
    import agent_authority.browser_repository as repository_module

    result['packageSha256'] = hashlib.sha256(package.read_bytes()).hexdigest()
    check('package_repository_modules', all(
        module.__file__ == str(package / (module.__name__.replace('.', '/') + '.py'))
        for module in (contracts, repository_module)
    ))
    actor = contracts.Principal('synthetic-owner', (
        contracts.Scope('synthetic-source', 'synthetic-job',
                        ('observations', 'report', 'private-verification')),
    ))
    states = root / 'states'
    states.mkdir(mode=0o700)
    first = repository_module.LocalReportRepository(states)
    repositories.append(first)
    expected = {}
    for number, adapter, state in (
        (1, 'observations', 'complete'),
        (2, 'report', 'incomplete'),
        (3, 'private-verification', 'reported-private-verification'),
        (4, 'observations', None),
    ):
        first.insert(actor, payload(number, adapter, state))
        expected[f'{number:032x}'] = state or 'unknown'
    first.close()
    repositories.remove(first)
    reopened = repository_module.LocalReportRepository(states)
    repositories.append(reopened)
    listed = reopened.listing(actor)
    result['counts']['repositoryStates'] = len(listed)
    check('repository_state_roundtrip',
          {item['id']: item['state'] for item in listed} == expected
          and all('report' not in item and 'graph' not in item for item in listed))

    quota = root / 'quota'
    quota.mkdir(mode=0o700)
    first = repository_module.LocalReportRepository(quota)
    repositories.append(first)
    for number in range(1, 50):
        first.insert(actor, payload(number))
    second = repository_module.LocalReportRepository(quota)
    repositories.append(second)
    result['counts']['quotaConnections'] = 2
    barrier = threading.Barrier(2)

    def insert(repository, number):
        barrier.wait(timeout=3)
        try:
            repository.insert(actor, payload(number))
            return 'inserted'
        except contracts.Problem as exc:
            return 'quota' if (exc.status, exc.code) == (409, 'STORAGE_LIMIT') else 'unexpected'

    with ThreadPoolExecutor(max_workers=2) as executor:
        futures = [executor.submit(insert, first, 50), executor.submit(insert, second, 51)]
        outcomes = [future.result(timeout=5) for future in futures]
    count = first.db.execute('SELECT COUNT(*) FROM reports WHERE owner=?',
                             (actor.subject,)).fetchone()[0]
    result['counts'].update(quotaReports=count, quotaInserted=outcomes.count('inserted'),
                            quotaRejected=outcomes.count('quota'))
    check('atomic_quota', sorted(outcomes) == ['inserted', 'quota'] and count == 50
          and len(second.listing(actor)) == 50)
except BaseException:
    pass
finally:
    for repository in repositories:
        try:
            repository.close()
        except BaseException:
            pass
    print(json.dumps(result, separators=(',', ':')))
"""


class CheckFailure(Exception):
    pass


class Probe:
    def __init__(self, package: Path):
        self.package = package
        self.evidence: dict[str, Any] = {
            "schema": "aa-browser-package-check-v1",
            "pythonVersion": platform.python_version(),
            "packageSha256": hashlib.sha256(package.read_bytes()).hexdigest(),
            "packageSourceVersion": "unknown",
            "packageSourceClean": False,
            "browserExecuted": False,
            "checks": {name: False for name in CHECKS},
            "executed": {name: False for name in CHECKS},
            "counts": {"accounts": 0, "storedReports": 0, "serviceStarts": 0},
        }
        self.processes: list[subprocess.Popen] = []
        self.port = 0
        self.secrets: list[bytes] = []
        self.sessions: dict[str, tuple[str, str]] = {}

    def check(self, name: str, condition: bool) -> None:
        self.evidence["executed"][name] = True
        self.evidence["checks"][name] = bool(condition)
        if not condition:
            raise CheckFailure()

    def command(self, cwd: Path, *arguments: str) -> subprocess.CompletedProcess:
        environment = dict(os.environ)
        environment.pop("PYTHONPATH", None)
        arguments_list = [sys.executable, "-I", "-B", str(self.package), *arguments]
        process = subprocess.Popen(
            arguments_list,
            cwd=cwd,
            env=environment,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        self.processes.append(process)
        try:
            stdout, stderr = process.communicate(timeout=20)
        except BaseException:
            process.kill()
            process.communicate(timeout=5)
            raise
        return subprocess.CompletedProcess(arguments_list, process.returncode, stdout, stderr)

    def inspect_package(self) -> list[bytes]:
        with zipfile.ZipFile(self.package) as package:
            names = package.namelist()
            manifest = json.loads(package.read("PACKAGE-MANIFEST.json"))
            version = manifest.get("sourceCommit", "")
            self.check(
                "package_manifest",
                manifest.get("schema") == "aa-browser-package-v1"
                and manifest.get("role") == "observer_only"
                and manifest.get("productionIntegration") == "blocked"
                and type(manifest.get("files")) is dict
                and type(version) is str
                and re.fullmatch(r"[0-9a-f]{40}", version) is not None,
            )
            self.evidence["packageSourceVersion"] = version
            self.evidence["packageSourceClean"] = manifest.get("sourceClean") is True
            runtime_hashes = {
                name: digest
                for name, digest in manifest["files"].items()
                if name.startswith("agent_authority/") or name == "__main__.py"
            }
            self.evidence["runtimeSha256"] = hashlib.sha256(
                json.dumps(runtime_hashes, sort_keys=True, separators=(",", ":")).encode()
            ).hexdigest()
            expected = set(manifest["files"]) | {"PACKAGE-MANIFEST.json", "__main__.py"}
            self.check(
                "package_hashes",
                len(names) == len(set(names))
                and set(names) == expected
                and manifest.get("runtimeSha256") == self.evidence["runtimeSha256"]
                and all(
                    hashlib.sha256(package.read(name)).hexdigest() == digest
                    for name, digest in manifest["files"].items()
                ),
            )
            allowed = all(
                name
                in {"LICENSE", "PACKAGE-MANIFEST.json", "__main__.py", "scripts/package_browser.py"}
                or re.fullmatch(r"agent_authority/[a-z_]+\.py", name)
                or name
                in {
                    "agent_authority/browser_static/" + item
                    for item in ("app.js", "index.html", "style.css", "strings.json")
                }
                or re.fullmatch(r"docs/BROWSER-[A-Z0-9-]+\.md", name)
                for name in names
            )
            self.check("package_state_files_excluded", allowed)
            self.check(
                "package_static_files",
                all(
                    "agent_authority/browser_static/" + name in names
                    and bool(package.read("agent_authority/browser_static/" + name))
                    for name in ("app.js", "index.html", "style.css", "strings.json")
                ),
            )
            return [package.read(name) for name in names]

    def start(self, cwd: Path, state: Path) -> subprocess.Popen:
        environment = dict(os.environ)
        environment.pop("PYTHONPATH", None)
        process = subprocess.Popen(
            [
                sys.executable,
                "-I",
                "-B",
                str(self.package),
                "serve",
                "--state",
                str(state),
                "--port",
                "0",
            ],
            cwd=cwd,
            env=environment,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        self.processes.append(process)
        assert process.stdout is not None
        output = b""
        deadline = time.monotonic() + 10
        with selectors.DefaultSelector() as selector:
            selector.register(process.stdout, selectors.EVENT_READ)
            while time.monotonic() < deadline:
                if not selector.select(min(0.2, max(0, deadline - time.monotonic()))):
                    continue
                chunk = os.read(process.stdout.fileno(), 4096)
                if not chunk:
                    break
                output += chunk
                if len(output) > 8192:
                    break
                ready = re.search(
                    rb"^Agent Authority synthetic private service: http://127\.0\.0\.1:([0-9]+)\r?$",
                    output,
                    re.MULTILINE,
                )
                if ready:
                    self.port = int(ready[1])
                    self.evidence["counts"]["serviceStarts"] += 1
                    return process
        raise CheckFailure()

    def request(
        self,
        method: str,
        path: str,
        value: Any = None,
        *,
        user: str | None = None,
        headers: dict | None = None,
        raw: bytes | None = None,
    ) -> tuple[int, Any, dict]:
        request_headers = {"Content-Type": "application/json"}
        if user:
            cookie, csrf = self.sessions[user]
            request_headers.update(Cookie=cookie, **{"X-CSRF-Token": csrf})
        request_headers.update(headers or {})
        body = raw if raw is not None else json.dumps(value).encode() if value is not None else None
        connection = http.client.HTTPConnection("127.0.0.1", self.port, timeout=8)
        try:
            connection.request(method, path, body=body, headers=request_headers)
            response = connection.getresponse()
            payload = response.read(24 * 1024 * 1024 + 1)
            if len(payload) > 24 * 1024 * 1024:
                raise CheckFailure()
            result = (
                json.loads(payload)
                if response.getheader("Content-Type", "").startswith("application/json")
                else payload
            )
            return response.status, result, dict(response.getheaders())
        finally:
            connection.close()

    def login(self, username: str, password: str) -> dict:
        authorization = base64.b64encode(f"{username}:{password}".encode()).decode()
        status, body, headers = self.request(
            "POST", "/api/login", {}, headers={"Authorization": "Basic " + authorization}
        )
        if status != 200 or body.get("user") != {"id": username, "synthetic": True}:
            raise CheckFailure()
        cookie = headers["Set-Cookie"].split(";", 1)[0]
        csrf = body["csrfToken"]
        if (
            "HttpOnly" not in headers["Set-Cookie"]
            or "SameSite=Strict" not in headers["Set-Cookie"]
        ):
            raise CheckFailure()
        self.sessions[username] = cookie, csrf
        self.secrets.extend([cookie.encode(), cookie.partition("=")[2].encode(), csrf.encode()])
        return body

    def stop(self, process: subprocess.Popen) -> bool:
        if process.poll() is None:
            process.send_signal(signal.SIGTERM)
        try:
            process.communicate(timeout=8)
        except subprocess.TimeoutExpired:
            process.kill()
            process.communicate(timeout=5)
            return False
        return process.returncode == 0

    def port_closed(self) -> bool:
        with socket.socket() as connection:
            connection.settimeout(1)
            return connection.connect_ex(("127.0.0.1", self.port)) != 0

    def repository_probe(self, cwd: Path) -> None:
        environment = dict(os.environ)
        environment.pop("PYTHONPATH", None)
        process = subprocess.Popen(
            [
                sys.executable,
                "-I",
                "-B",
                "-c",
                REPOSITORY_PROBE,
                str(self.package),
                str(cwd / "repository-probe"),
            ],
            cwd=cwd,
            env=environment,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        self.processes.append(process)
        try:
            stdout, _ = process.communicate(timeout=20)
        except BaseException:
            process.kill()
            process.communicate(timeout=5)
            raise
        result = json.loads(stdout)
        names = ("package_repository_modules", "repository_state_roundtrip", "atomic_quota")
        for name in names:
            self.evidence["executed"][name] = result["executed"][name] is True
            self.evidence["checks"][name] = result["checks"][name] is True
        if result.get("packageSha256") != self.evidence["packageSha256"]:
            self.evidence["checks"]["package_repository_modules"] = False
        for name in (
            "quotaReports",
            "quotaInserted",
            "quotaRejected",
            "quotaConnections",
            "repositoryStates",
        ):
            value = result["counts"][name]
            if type(value) is not int or not 0 <= value <= 50:
                raise CheckFailure()
            self.evidence["counts"][name] = value
        if process.returncode != 0 or not all(self.evidence["checks"][name] for name in names):
            raise CheckFailure()

    def exercise(self, cwd: Path, package_contents: list[bytes]) -> None:
        state, examples = cwd / "state", cwd / "examples"
        initialized = self.command(cwd, "init-synthetic", "--state", str(state))
        credentials = {}
        for line in initialized.stdout.decode("utf-8").splitlines():
            match = re.fullmatch(r"(alice|bob): ([A-Za-z0-9_-]{20,})", line)
            if match:
                credentials[match[1]] = match[2]
        self.check(
            "synthetic_init", initialized.returncode == 0 and set(credentials) == {"alice", "bob"}
        )
        self.secrets.extend(value.encode() for value in credentials.values())
        generated = self.command(cwd, "examples", "--output", str(examples))
        self.check("synthetic_examples", generated.returncode == 0)
        process = self.start(cwd, state)
        self.check("service_start", process.poll() is None)
        self.check(
            "static_http",
            all(
                status == 200
                and bool(body)
                and "default-src 'none'" in headers.get("Content-Security-Policy", "")
                for status, body, headers in (
                    self.request("GET", path)
                    for path in ("/", "/app.js", "/style.css", "/strings.json")
                )
            ),
        )
        self.check(
            "anonymous_denied",
            all(
                self.request("GET", path)[0] == 401
                for path in ("/api/session", "/api/reports", "/api/demo", "/api/status")
            ),
        )
        scopes = {}
        for username in ("alice", "bob"):
            scopes[username] = self.login(username, credentials[username])["scopes"]
        self.evidence["counts"]["accounts"] = len(self.sessions)
        self.check("synthetic_login", len(self.sessions) == 2)
        revoked_cookie = self.sessions["alice"][0]
        status, body, headers = self.request("POST", "/api/logout", {}, user="alice")
        self.check(
            "live_logout",
            status == 200
            and body == {"loggedOut": True}
            and "Max-Age=0" in headers.get("Set-Cookie", ""),
        )
        self.check(
            "revoked_cookie_denied",
            all(
                self.request("GET", path, user="alice")[0] == 401
                for path in ("/api/session", "/api/reports", "/api/status")
            ),
        )
        self.login("alice", credentials["alice"])
        self.check(
            "fresh_login_after_logout",
            self.sessions["alice"][0] != revoked_cookie
            and self.request("GET", "/api/session", user="alice")[0] == 200,
        )
        self.check(
            "empty_accounts",
            all(
                self.request("GET", "/api/reports", user=user)[1]["reports"] == []
                for user in ("alice", "bob")
            ),
        )
        records = json.loads((examples / "SYNTHETIC-alice-observations.json").read_bytes())
        foreign_text = '<img src=x onerror="alert(1)">'
        records[0]["reported_actor_type"] = foreign_text
        envelope = {
            "sourceId": "synthetic-alice",
            "jobId": "test-alice",
            "kind": "observations",
            "data": records,
        }
        status, metadata, _ = self.request("POST", "/api/reports/import", envelope, user="alice")
        self.check("neutral_import", status == 201)
        neutral_id = metadata["id"]
        status, result, _ = self.request("GET", "/api/reports/" + neutral_id, user="alice")
        report, graph = result["report"], result["graph"]
        self.check(
            "neutral_model_and_foreign_text",
            status == 200
            and report["source"]["entries_read"] == 4
            and report["source"]["identity"] == report["source"]["effect"] == "UNBEKANNT"
            and report["source"]["source_authenticated"] is False
            and report["task_completion_proven"] is False
            and report["rights_inherited"] is False
            and graph["isDemo"] is False
            and len(graph["edges"]) == 3
            and foreign_text
            in [fact["value"] for node in graph["nodes"] for fact in node["facts"]],
        )
        self.check(
            "owner_isolation",
            self.request("GET", "/api/reports/" + neutral_id, user="bob")[0] == 404
            and self.request("GET", "/api/reports", user="bob")[1]["reports"] == [],
        )
        denied_owner = self.request("POST", "/api/reports/import", envelope, user="bob")[0]
        denied_source = self.request(
            "POST",
            "/api/reports/import",
            dict(envelope, sourceId="not-configured"),
            user="alice",
        )[0]
        denied_job = self.request(
            "POST",
            "/api/reports/import",
            dict(envelope, jobId="not-configured"),
            user="alice",
        )[0]
        self.check("source_isolation", denied_source == 403)
        self.check("job_isolation", denied_job == 403)
        self.check(
            "source_job_isolation",
            denied_owner == denied_source == denied_job == 403,
        )
        self.check(
            "adapter_isolation",
            self.request(
                "POST",
                "/api/reports/import",
                dict(envelope, kind="private-verification"),
                user="alice",
            )[0]
            == 403,
        )
        self.check(
            "csrf_denied",
            self.request(
                "POST",
                "/api/reports/import",
                envelope,
                user="alice",
                headers={"X-CSRF-Token": "wrong"},
            )[0]
            == 403,
        )
        self.check(
            "duplicate_json_denied",
            self.request("POST", "/api/reports/import", user="alice", raw=b'{"data":1,"data":2}')[0]
            == 400,
        )
        private = json.loads((examples / "SYNTHETIC-alice-private-report.json").read_bytes())
        private_scope = next(
            scope for scope in scopes["alice"] if scope["sourceId"] == "synthetic-private-alice"
        )
        status, metadata, _ = self.request(
            "POST",
            "/api/reports/import",
            {**private_scope, "kind": "private-verification", "data": private},
            user="alice",
        )
        self.check("private_import", status == 201)
        private_id = metadata["id"]
        status, result, _ = self.request("GET", "/api/reports/" + private_id, user="alice")
        self.check(
            "private_report_unverified",
            status == 200
            and result["report"] is None
            and result["privateReport"]["signature_omitted"] is True
            and result["privateReport"]["signature_verification"] == "UNBEKANNT"
            and result["metadata"]["productionIntegration"] == "blocked"
            and all(node["status"] == "unknown" for node in result["graph"]["nodes"]),
        )
        self.check(
            "private_owner_isolation",
            self.request("GET", "/api/reports/" + private_id, user="bob")[0] == 404,
        )
        status, result, _ = self.request("GET", "/api/status", user="alice")
        self.check(
            "production_blocked",
            status == 200
            and result["actions"] is False
            and result["grantsRights"] is False
            and result["liveConnection"] is False
            and all(
                result["production"][key] == "blocked"
                for key in ("identity", "collector", "privateService")
            ),
        )
        architecture, processing = result["architecture"], result["processing"]
        self.check(
            "status_process_queue_limits",
            architecture["graphComputation"] == "browser"
            and architecture["profile"] == "single-instance-local-synthetic"
            and architecture["stateLease"]
            == "exclusive-local-process-lock; not a distributed lease"
            and architecture["httpConcurrency"] == 1
            and architecture["socketBacklog"] == 8
            and architecture["durableQueue"] is False
            and architecture["globalAdmission"] == "not-implemented; multi-instance-blocked"
            and result["production"]["multiInstance"] == "blocked"
            and processing
            == {
                "scope": "process",
                "concurrencyLimit": 1,
                "active": 0,
                "completed": 2,
                "failed": 0,
                "rejectedBusy": 0,
                "waitingJobs": 0,
                "durableQueue": False,
                "automaticRetry": False,
            },
        )
        duplicate = self.command(cwd, "serve", "--state", str(state), "--port", "0")
        self.check(
            "second_instance_denied",
            duplicate.returncode == 2
            and b"Agent Authority synthetic private service:" not in duplicate.stdout,
        )
        self.check(
            "first_instance_healthy",
            process.poll() is None
            and self.request("GET", "/api/status", user="alice")[0] == 200
            and self.request("GET", "/api/reports/" + neutral_id, user="alice")[0] == 200,
        )
        status, result, _ = self.request("GET", "/api/demo", user="alice")
        self.check(
            "explicit_demo",
            status == 200
            and result["graph"]["isDemo"] is True
            and result["metadata"]["synthetic"] is True
            and len(result["warningAssessments"]) == 6,
        )
        reports = self.request("GET", "/api/reports", user="alice")[1]["reports"]
        self.evidence["counts"]["storedReports"] = len(reports)
        self.check(
            "demo_does_not_create_report",
            {item["id"] for item in reports} == {neutral_id, private_id},
        )
        self.check(
            "report_states_listing",
            {item["id"]: item["state"] for item in reports}
            == {neutral_id: "complete", private_id: "reported-private-verification"}
            and all("graph" not in item and "report" not in item for item in reports),
        )
        self.check(
            "package_credentials_absent",
            not any(secret in content for secret in self.secrets for content in package_contents),
        )
        self.check("first_sigterm", self.stop(process))
        self.check("first_port_closed", self.port_closed())
        process = self.start(cwd, state)
        self.check("restart", process.poll() is None)
        self.check(
            "sessions_not_persisted", self.request("GET", "/api/session", user="alice")[0] == 401
        )
        self.login("alice", credentials["alice"])
        self.check(
            "report_persisted",
            self.request("GET", "/api/reports/" + neutral_id, user="alice")[0] == 200,
        )
        self.check("final_sigterm", self.stop(process))
        self.check("final_port_closed", self.port_closed())
        self.repository_probe(cwd)

    def run(self) -> dict:
        temporary = tempfile.TemporaryDirectory(prefix="aa-browser-package-check-")
        path = Path(temporary.name)
        try:
            contents = self.inspect_package()
            self.exercise(path, contents)
        except (Exception, KeyboardInterrupt) as exc:  # noqa: BLE001
            # Failed/absent checks remain false and unexecuted. Never persist an
            # exception message: it could contain credentials or local paths.
            self.evidence["failureType"] = type(exc).__name__
        finally:
            reaped = True
            for process in self.processes:
                if process.poll() is None:
                    reaped = self.stop(process) and reaped
                reaped = process.poll() is not None and reaped
            try:
                temporary.cleanup()
                removed = not path.exists()
            except OSError:
                removed = False
            for name, result in (
                ("own_processes_reaped", reaped),
                ("temporary_directory_removed", removed),
            ):
                self.evidence["executed"][name] = True
                self.evidence["checks"][name] = result
        checks, executed = self.evidence["checks"], self.evidence["executed"]
        self.evidence["counts"].update(
            passed=sum(checks.values()),
            failed=sum(executed[name] and not checks[name] for name in CHECKS),
            notExecuted=sum(not value for value in executed.values()),
        )
        self.evidence["passed"] = all(checks.values()) and all(executed.values())
        return self.evidence


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--package", required=True, type=Path)
    parser.add_argument("--evidence", required=True, type=Path)
    args = parser.parse_args()
    os.umask(0o077)

    def interrupted(signum: int, frame: Any) -> None:
        raise KeyboardInterrupt()

    signal.signal(signal.SIGTERM, interrupted)
    result = Probe(args.package.resolve()).run()
    try:
        with args.evidence.open("x", encoding="utf-8") as target:
            json.dump(result, target, indent=2)
            target.write("\n")
    except OSError:
        # No path or partial data is printed on evidence-output failure.
        print("Evidence output unavailable; no existing file overwritten.", file=sys.stderr)
        return 2
    print(json.dumps(result, separators=(",", ":")))
    return 0 if result["passed"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
