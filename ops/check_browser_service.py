"""Narrow live probes; secrets stay in memory, temporary synthetic row removed.

One bounded lab runner only, while the shared Debian lock is held by the caller.
The service and this runner share the new aa-browser.slice aggregate budget.
"""

import base64
import http.client
import json
import signal
import socket
import sqlite3
import ssl
import subprocess
import time
from pathlib import Path

ROOT = Path("/opt/agent-authority-browser")
STATE = Path("/var/lib/agent-authority-browser")
NAME = "agent-authority-browser.service"
HOST = "v2202608211799501333.goodsrv.de"
PREFIX = "/agent-authority"
RESULTS = []
ACCESS = None


def check(name, condition):
    RESULTS.append({"check": name, "passed": bool(condition)})
    if not condition:
        raise AssertionError(name)


def basic(user):
    return "Basic " + base64.b64encode((user + ":" + ACCESS["accounts"][user]).encode()).decode()


def request(path="/", method="GET", data=None, user="alice", headers=None, direct=False, timeout=8):
    h = {"Host": HOST}
    if user:
        h["Authorization"] = basic(user)
    if headers:
        h.update(headers)
    raw = None if data is None else json.dumps(data).encode()
    if raw is not None:
        h["Content-Type"] = "application/json"
    if direct:

        class UnixHTTP(http.client.HTTPConnection):
            def connect(self):
                self.sock = socket.socket(socket.AF_UNIX)
                self.sock.settimeout(self.timeout)
                self.sock.connect("/opt/4allpass/sites/.aa-transport/browser.sock")

        c = UnixHTTP(HOST, timeout=timeout)
    else:
        c = http.client.HTTPSConnection(HOST, timeout=timeout, context=ssl.create_default_context())
    try:
        c.request(method, PREFIX + path, body=raw, headers=h)
        r = c.getresponse()
        raw = r.read()
        hs = dict(r.getheaders())
        try:
            body = json.loads(raw)
        except ValueError:
            body = raw
        return r.status, body, hs
    finally:
        c.close()


def wait(seconds=15):
    deadline = time.monotonic() + seconds
    while time.monotonic() < deadline:
        try:
            if request(timeout=min(2, max(0.1, deadline - time.monotonic())))[0] == 200:
                return
        except (OSError, http.client.HTTPException):
            pass
        time.sleep(min(0.2, max(0, deadline - time.monotonic())))
    raise AssertionError("service_not_ready")


class ProbeTerminated(Exception):
    pass


def terminate(_signum, _frame):
    raise ProbeTerminated("bounded probe terminated; restoring own temporary state")


def control(action):
    subprocess.run(["systemctl", action, NAME], check=True, capture_output=True, timeout=30)


def login(user):
    code, body, headers = request("/api/login", "POST", {}, user)
    check("login_" + user, code == 200 and body["user"] == {"id": user, "synthetic": True})
    cookie = headers["Set-Cookie"]
    check(
        "secure_cookie_" + user,
        all(
            v in cookie
            for v in (
                "HttpOnly",
                "Secure",
                "SameSite=Strict",
                "Path=/agent-authority/",
                "Max-Age=1800",
            )
        )
        and "Domain=" not in cookie,
    )
    return {"Cookie": cookie.split(";", 1)[0], "X-CSRF-Token": body["csrfToken"]}


def main():
    global ACCESS
    ACCESS = json.loads(Path("/etc/agent-authority-browser/operator-access.json").read_text())
    RESULTS.clear()
    signal.signal(signal.SIGTERM, terminate)
    report_id = None
    service_stop_owned = False
    original_caddy = Path("/opt/4allpass/Caddyfile").read_bytes()
    try:
        wait()
        check("outer_anonymous_401", request(user=None)[0] == 401)
        check("inner_anonymous_401", request("/api/session")[0] == 401)
        check("tls_prefix_and_private_login_page", request()[0] == 200)
        navigation = {
            "Sec-Fetch-Site": "cross-site",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Dest": "document",
        }
        check("helpcenter_navigation_landing_200", request(headers=navigation)[0] == 200)
        check("cross_site_api_still_403", request("/api/session", headers=navigation)[0] == 403)
        check("private_python_not_served", request("/browser.py")[0] == 401)
        check("direct_socket_without_proxy_403", request(direct=True)[0] == 403)
        check(
            "direct_forged_forwarded_403",
            request(direct=True, headers={"X-Forwarded-Proto": "https", "X-Forwarded-Host": HOST})[
                0
            ]
            == 403,
        )
        alice = login("alice")
        bob = login("bob")
        check("private_python_authenticated_404", request("/browser.py", headers=alice)[0] == 404)
        check(
            "real_context_contract_409",
            request("/api/hilfezentrum/context", "POST", {}, headers=alice)[0] == 409,
        )
        check(
            "origin_403",
            request("/api/session", headers={**alice, "Origin": "https://invalid.example.test"})[0]
            == 403,
        )
        check(
            "fetch_site_403",
            request("/api/session", headers={**alice, "Sec-Fetch-Site": "cross-site"})[0] == 403,
        )
        check(
            "csrf_403",
            request("/api/hilfezentrum/demo", "POST", {}, headers={"Cookie": alice["Cookie"]})[0]
            == 403,
        )
        code, body, _ = request("/api/hilfezentrum/demo", "POST", {}, headers=alice)
        check(
            "synthetic_connection_200",
            code == 200
            and body["metadata"]["synthetic"]
            and not body["metadata"]["realContextTransferred"]
            and body["context"]["schema"] == "hilfezentrum.authority-context.v1",
        )
        check(
            "foreign_fixture_404",
            request("/api/hilfezentrum/demo", "POST", {}, user="bob", headers=bob)[0] == 404,
        )
        check(
            "handoff_parameters_rejected_422",
            request(
                "/api/hilfezentrum/demo",
                "POST",
                {"url": "https://invalid.example.test"},
                headers=alice,
            )[0]
            == 422,
        )
        code, body, _ = request("/api/status", headers=alice)
        check(
            "production_gates_unchanged",
            code == 200
            and all(
                body["production"][k] == "blocked"
                for k in ("identity", "collector", "privateService", "multiInstance")
            )
            and body["actions"] is False
            and body["architecture"]["graphComputation"] == "browser",
        )
        envelope = {
            "sourceId": "synthetic-alice",
            "jobId": "test-alice",
            "kind": "observations",
            "data": [],
        }
        code, body, _ = request("/api/reports/import", "POST", envelope, headers=alice)
        check("synthetic_report_created", code == 201)
        report_id = body["id"]
        check("owner_report_200", request("/api/reports/" + report_id, headers=alice)[0] == 200)
        check(
            "foreign_id_404",
            request("/api/reports/" + report_id, user="bob", headers=bob)[0] == 404,
        )
        check("anonymous_id_401", request("/api/reports/" + report_id)[0] == 401)
        check(
            "source_scope_403",
            request("/api/reports/import", "POST", envelope, user="bob", headers=bob)[0] == 403,
        )
        code, body, _ = request(
            "/api/reports/" + report_id, headers={**alice, "X-AA-Proxy-Token": "forged"}
        )
        check("proxy_overwrites_client_token", code == 200)
        # Genuine lease collision, not a second listener. It fails before opening DB.
        code = "from agent_authority.browser_repository import StateLease; from pathlib import Path; StateLease(Path('/var/lib/agent-authority-browser/data'))"
        collision = subprocess.run(
            [
                "runuser",
                "-u",
                "aa-browser",
                "--",
                "env",
                "PYTHONDONTWRITEBYTECODE=1",
                "PYTHONPATH=" + str(ROOT / "current/browser.pyz"),
                str(ROOT / "runtime/bin/python"),
                "-B",
                "-c",
                code,
            ],
            capture_output=True,
            timeout=8,
            check=False,
        )
        check(
            "single_state_lease",
            collision.returncode != 0 and b"local state already in use" in collision.stderr,
        )
        service_stop_owned = True
        control("stop")
        check(
            "stop_inactive",
            subprocess.run(["systemctl", "is-active", "--quiet", NAME], check=False).returncode
            != 0,
        )
        check("stop_no_application", request()[0] == 502)
        # Remove exactly the probe-owned row only while all workers are stopped.
        with sqlite3.connect(STATE / "data/reports.sqlite3") as db:
            cursor = db.execute("DELETE FROM reports WHERE owner=? AND id=?", ("alice", report_id))
            check("temporary_report_removed", cursor.rowcount == 1)
        report_id = None
        control("start")
        service_stop_owned = False
        wait()
        check("start_revokes_old_session", request("/api/session", headers=alice)[0] == 401)
        alice = login("alice")
        control("restart")
        wait()
        check("restart_revokes_old_session", request("/api/session", headers=alice)[0] == 401)
        alice = login("alice")
        check("state_retained_empty", request("/api/reports", headers=alice)[1]["reports"] == [])
        properties = subprocess.check_output(
            [
                "systemctl",
                "show",
                NAME,
                "-p",
                "User",
                "-p",
                "Group",
                "-p",
                "MemoryMax",
                "-p",
                "MemorySwapMax",
                "-p",
                "CPUQuotaPerSecUSec",
                "-p",
                "TasksMax",
                "-p",
                "MainPID",
                "-p",
                "NRestarts",
            ],
            text=True,
        )
        props = dict(line.split("=", 1) for line in properties.splitlines())
        check(
            "unprivileged_and_limits",
            props["User"] == "aa-browser"
            and props["Group"] == "aa-browser"
            and props["MemoryMax"] == "268435456"
            and props["MemorySwapMax"] == "0"
            and props["CPUQuotaPerSecUSec"] == "400ms"
            and props["TasksMax"] == "16",
        )
        main = int(props["MainPID"])
        children = Path(f"/proc/{main}/task/{main}/children").read_text().split()
        check(
            "one_actual_worker",
            len(children) == 1
            and Path("/proc/" + children[0] + "/status").read_text().split("Uid:")[1].split()[0]
            != "0",
        )
        aggregate = subprocess.check_output(
            [
                "systemctl",
                "show",
                "aa-browser.slice",
                "-p",
                "MemoryMax",
                "-p",
                "MemorySwapMax",
                "-p",
                "CPUQuotaPerSecUSec",
            ],
            text=True,
        )
        check(
            "aggregate_probe_limits",
            all(
                v in aggregate
                for v in ("MemoryMax=838860800", "MemorySwapMax=0", "CPUQuotaPerSecUSec=400ms")
            ),
        )
        before = json.loads(
            Path("/var/backups/agent-authority-browser/20261017/before.json").read_text()
        )
        import hashlib

        check(
            "existing_units_unchanged",
            all(
                hashlib.sha256(subprocess.check_output(["systemctl", "cat", name])).hexdigest()
                == digest
                for name, digest in before["other_units"].items()
            ),
        )
        check(
            "collector_remains_inactive",
            subprocess.run(
                ["systemctl", "is-active", "--quiet", "aa-private-collector.service"], check=False
            ).returncode
            != 0,
        )
        check(
            "verifier_remains_active",
            subprocess.run(
                ["systemctl", "is-active", "--quiet", "aa-private-verifier.service"], check=False
            ).returncode
            == 0,
        )
        print(
            json.dumps(
                {
                    "passed": True,
                    "checks": RESULTS,
                    "unit": props,
                    "aggregate": aggregate,
                    "no_real_data": True,
                    "temporary_reports_remaining": 0,
                },
                indent=2,
            )
        )
    finally:
        # RuntimeMaxSec sends SIGTERM. Finish only this probe's bounded cleanup
        # before the transient unit exits; another SIGTERM cannot interrupt it.
        signal.signal(signal.SIGTERM, signal.SIG_IGN)
        try:
            if report_id:
                service_stop_owned = True
                control("stop")
                with sqlite3.connect(STATE / "data/reports.sqlite3") as db:
                    db.execute("DELETE FROM reports WHERE owner=? AND id=?", ("alice", report_id))
        finally:
            if service_stop_owned:
                control("start")
            assert Path("/opt/4allpass/Caddyfile").read_bytes() == original_caddy


if __name__ == "__main__":
    main()
