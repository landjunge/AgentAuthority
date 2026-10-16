"""Loopback-only HTTP adapter and browser inspector. No ambient browser login."""

import argparse
import http.client
import json
import re
import socket
import sqlite3
import threading
import time
from collections import deque
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from urllib.error import HTTPError
from urllib.parse import urlsplit
from urllib.request import HTTPRedirectHandler, ProxyHandler, Request, build_opener

from research.private_service.limits import (
    DEADLINE,
    HTTP_SECONDS,
    MAX_BYTES,
    process_limits,
    unprivileged,
)
from research.private_service.protocol import Problem, parse, require
from research.private_service.service import Service

JOB_ROUTE = re.compile(
    r"/v1/jobs/([A-Za-z0-9_-]{1,80})(?:/(report|acceptances|evidence|receipts|cancellations))?\Z"
)
CONTROL_ROUTES = {"/v1/challenges", "/v1/enrollments", "/v1/revocations", "/v1/jobs"}
PUBLIC_ROUTES = {"/", "/inspector.js", "/v1/privacy"}
HEADER_BYTES = 16384


class HeaderReader:
    def __init__(self, source):
        self.source, self.left = source, HEADER_BYTES

    def readline(self, limit=-1):
        line = self.source.readline(min(limit, self.left + 1) if limit > 0 else self.left + 1)
        self.left -= len(line)
        if self.left < 0 or (line[:1] in (b" ", b"\t")):
            raise http.client.LineTooLong("header limit")
        return line


PAGE = b"""<!doctype html><meta charset="utf-8"><title>Agent Authority - privater Test</title>
<h1>Agent Authority: privaten Testlauf pruefen</h1>
<p>Nur kontrollierte Testidentitaeten. Keine Rechteerteilung, kein Sicherheitszertifikat.</p>
<p lang="de">Vor der Einreichung: Wir erheben nur Testkennungen, Publickeys,
Signaturen und begrenzte Prozess-/Write-Nachweise zur Pruefung dieses Testlaufs.
Eingaben und Zwischenstaende verschwinden nach der Pruefung und Berichterstellung.
Berichte bleiben ab Fertigstellung hoechstens 24 Stunden, nach signierter Bestaetigung
des vollstaendigen Empfangs kuerzer. Abruf allein loescht nichts. Inhaltsfreie
Requestsperren bleiben bis Ende der Signierschluesselepoche plus 65 Sekunden;
Loeschstatus bis zum spaeteren Ende dieser Frist oder der Berichtsfrist plus 65 Sekunden.
Schluesselregister und lokale Zugangsdaten werden getrennt verwaltet.</p>
<p lang="de">Grenzen: Bei Dienstausfall kann die Dateibereinigung erst beim Neustart
stattfinden; dann wird vor erneutem Abruf gesperrt. Keine Zusage physischer
SSD-/RAM- oder Backup-Loeschung. Neue VM-Liveversuche sind bis zur Qualifikation
eines verschluesselten kurzlebigen Runner-Speichers gesperrt.</p>
<p lang="en">Before submission: We collect test identifiers, public keys, signatures
and bounded process/write evidence to verify this test. Inputs and intermediate
data are removed after verification and report creation. Reports expire within
24 hours of completion, or earlier after a signed confirmation of complete receipt.
A download alone never deletes a report. Content-free replay records remain until
the signing key epoch ends plus 65 seconds; deletion status until the later of
that deadline or report expiry plus 65 seconds. Key registers and local credentials
have a separate lifecycle. Cleanup failures remain visible; no physical erasure claim.</p>
<p lang="en">Limits: During downtime file cleanup waits for restart, before renewed
access. No SSD/RAM or backup erasure guarantee. New VM executions are blocked until
encrypted ephemeral runner storage is qualified.</p>
<label>Lokaler Zugangstoken <input id="token" type="password" autocomplete="off"></label>
<label>Laufkennung <input id="job" maxlength="80"></label>
<button id="status">Status</button><button id="report">Pruefbericht</button>
<p id="summary">Laufkennung und lokalen Zugang eingeben.</p>
<details><summary>Technische Details</summary><pre id="out"></pre></details>
<script src="/inspector.js"></script>"""
SCRIPT = b"""for (const mode of ['status','report']) document.getElementById(mode).onclick=async()=>{
const id=document.getElementById('job').value;
if(!/^[A-Za-z0-9_-]{1,80}$/.test(id))return;
const r=await fetch('/v1/jobs/'+id+(mode==='report'?'/report':''),{headers:{
Authorization:'Bearer '+document.getElementById('token').value}});
const data=await r.json();
const names={BELEGT:'Belegt im kontrollierten Test',WIDERSPRUECHLICH:'Belege widersprechen sich',
UNVOLLSTAENDIG:'Nachweise fehlen',UNBEKANNT:'Ergebnis unbekannt'};
const body=data.report&&data.report.body;
document.getElementById('summary').textContent=(data.label||(body?
(names[body.classification]||'Ergebnis unbekannt')+'. Umfang: kontrollierter Linux-Test. Provideridentitaet unbekannt.':data.code||'Abruf fehlgeschlagen'))+
(data.expires_at?' Ablauf / expires: '+data.expires_at:'')+
(data.receipt_state?' Empfang / receipt: '+data.receipt_state:'')+
(data.cleanup_state?' Bereinigung / cleanup: '+data.cleanup_state:'')+
(data.cleanup_completed_at?' Bestaetigt abgeschlossen / confirmed: '+data.cleanup_completed_at:'');
document.getElementById('out').textContent=JSON.stringify(data,null,2);};"""


def call(url, token, method, path, body=None):
    require(type(url) is str and all(33 <= ord(c) <= 126 for c in url))
    try:
        target = urlsplit(url)
        port = target.port
    except ValueError as error:
        raise Problem(422, "LOOPBACK_TARGET_REQUIRED") from error
    require(
        target.scheme == "http"
        and target.hostname == "127.0.0.1"
        and target.username is None
        and target.password is None
        and not target.path
        and not target.query
        and not target.fragment
        and port is not None
        and 0 < port < 65536,
        422,
        "LOOPBACK_TARGET_REQUIRED",
    )
    require(type(path) is str and path.startswith("/") and "?" not in path and "#" not in path)

    class NoRedirect(HTTPRedirectHandler):
        def redirect_request(self, *args):
            return None

    opener = build_opener(ProxyHandler({}), NoRedirect())
    raw = None if body is None else json.dumps(body).encode()
    req = Request(
        url + path,
        data=raw,
        method=method,
        headers={"Authorization": "Bearer " + token, "Content-Type": "application/json"},
    )
    try:
        response = opener.open(req, timeout=10)
    except HTTPError as error:
        response = error
    with response:
        require(not 300 <= response.status < 400, 422, "REDIRECT_FORBIDDEN")
        raw = response.read(MAX_BYTES + 1)
        require(len(raw) <= MAX_BYTES, 413, "RESPONSE_LIMIT")
        return response.status, json.loads(raw)


def server(service, port=0):
    unprivileged()

    class PrivateServer(HTTPServer):
        request_queue_size = 4
        # One active request and one child component per process. Bounded backlog;
        # no unbounded thread/fork-per-connection path.

        def __init__(self, *args):
            self.rates = {"anonymous": deque()}
            self.rates.update({t["tenant"]: deque() for t in service.config["tokens"]})
            super().__init__(*args)

        def rate(self, tenant):
            events = self.rates[tenant]
            stamp = time.monotonic()
            while events and events[0] <= stamp - 60:
                events.popleft()
            require(len(events) < 120, 429, "RATE_LIMIT")
            events.append(stamp)

        def service_actions(self):
            try:
                with service.exclusive():
                    service.sweep()
            except (Problem, OSError, sqlite3.Error):
                self.maintenance_failed = True  # No content/exception dumps.
            else:
                self.maintenance_failed = False

        def handle_error(self, request, client_address):
            pass  # No traceback/local variable/request dumps on broken sockets.

    class Handler(BaseHTTPRequestHandler):
        server_version = "AgentAuthorityPrivate"
        sys_version = ""

        def setup(self):
            super().setup()
            self.connection.settimeout(HTTP_SECONDS)
            self.deadline = time.monotonic() + HTTP_SECONDS

            def expire():
                try:
                    self.connection.shutdown(socket.SHUT_RDWR)
                except OSError:
                    pass

            self.timer = threading.Timer(HTTP_SECONDS, expire)
            self.timer.daemon = True
            self.timer.start()

        def finish(self):
            self.timer.cancel()
            super().finish()

        def parse_request(self):
            if len(self.raw_requestline) > 2048:
                self.requestline, self.request_version, self.command = "", "HTTP/1.0", None
                self.send_error(414)
                return False
            source = self.rfile
            self.rfile = HeaderReader(source)
            try:
                return super().parse_request()
            finally:
                self.rfile = source

        def log_message(self, *args):
            pass  # Never log tokens, paths, bodies or free exception strings.

        def send_error(self, code, message=None, explain=None):
            # BaseHTTPRequestHandler otherwise reflects malformed request lines.
            self.send(
                code,
                {
                    "type": "urn:aa:problem:invalid-http",
                    "title": "INVALID_HTTP",
                    "status": code,
                    "code": "INVALID_HTTP",
                },
                "application/problem+json",
            )

        def send(self, status, data, content_type="application/json"):
            raw = data if isinstance(data, bytes) else json.dumps(data).encode()
            self.send_response(status)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(raw)))
            self.send_header("Cache-Control", "no-store")
            self.send_header("Connection", "close")
            self.close_connection = True
            self.send_header("X-Content-Type-Options", "nosniff")
            self.send_header(
                "Content-Security-Policy",
                "default-src 'none'; script-src 'self'; connect-src 'self'; frame-ancestors 'none'; form-action 'none'",
            )
            self.end_headers()
            self.wfile.write(raw)

        def route(self):
            self.server.rate("anonymous")
            for name in ("Host", "Origin", "Authorization", "Content-Type", "Content-Length"):
                require(len(self.headers.get_all(name) or []) <= 1, 400, "DUPLICATE_HEADER")
            host = self.headers.get("Host", "")
            require(host == f"127.0.0.1:{self.server.server_port}", 403, "HOST_FORBIDDEN")
            origin = self.headers.get("Origin")
            require(origin is None or origin == f"http://{host}", 403, "ORIGIN_FORBIDDEN")
            require(not self.headers.get("Transfer-Encoding"), 400, "TRANSFER_ENCODING_UNSUPPORTED")
            require(
                self.headers.get("Content-Encoding") is None, 415, "CONTENT_ENCODING_UNSUPPORTED"
            )
            require(self.headers.get("Expect") is None, 417, "EXPECT_UNSUPPORTED")
            require(self.command in ("GET", "POST"), 405, "METHOD_FORBIDDEN")
            job_route = JOB_ROUTE.fullmatch(self.path)
            require(self.path in PUBLIC_ROUTES | CONTROL_ROUTES or job_route, 404, "NOT_FOUND")
            if self.command == "GET":
                require(
                    self.path in PUBLIC_ROUTES or (job_route and job_route[2] in (None, "report")),
                    405,
                    "METHOD_FORBIDDEN",
                )
                require(self.headers.get("Content-Length", "0") == "0", 400, "UNEXPECTED_BODY")
            else:
                require(
                    self.path in CONTROL_ROUTES
                    or (
                        job_route
                        and job_route[2] in ("acceptances", "evidence", "receipts", "cancellations")
                    ),
                    405,
                    "METHOD_FORBIDDEN",
                )
            if self.command == "GET" and self.path == "/v1/privacy":
                self.send(
                    200,
                    {
                        "schema": "aa-retention-v1",
                        "report_max_age_seconds": 86400,
                        "receipt_requires": "authenticated signed tenant/job/version/digest and received_complete=true",
                        "replay_retention": "signer key expires_ms + 60000ms maximum request + 5000ms retention tolerance",
                        "de": "Nur Testkennungen, Publickeys, Signaturen und begrenzte Prozess-/Write-Nachweise zur Pruefung. Eingaben nach Pruefung entfernen; Berichtszugriff maximal 24h ab Fertigstellung, frueher nach bestaetigtem vollstaendigem Empfang. Inhaltsfreie Sperrdaten bis zur konkreten residual_expires_at; Authregister getrennt. Dateibereinigung bei Ausfall erst beim Neustart; keine physische/Backup-Loeschgarantie. VM-Liverunner gesperrt.",
                        "en": "Only test IDs, public keys, signatures and bounded process/write evidence for verification. Remove inputs after verification; report access at most 24h from completion, earlier after confirmed full receipt. Content-free replay/deletion records until their stated expiry; auth registers separate. Cleanup during downtime waits for restart; no physical/backup erasure guarantee. VM live runner blocked.",
                    },
                )
                return
            if self.command == "GET" and self.path in ("/", "/inspector.js"):
                self.send(
                    200,
                    PAGE if self.path == "/" else SCRIPT,
                    "text/html; charset=utf-8" if self.path == "/" else "text/javascript",
                )
                return
            auth = self.headers.get("Authorization", "")
            require(auth.startswith("Bearer "), 401, "AUTH_REQUIRED")
            tenant, role = service.authenticate(auth[7:])
            self.server.rate(tenant)
            if self.command == "POST":
                require(self.headers.get("Content-Type") == "application/json", 415, "CONTENT_TYPE")
                lengths = self.headers.get_all("Content-Length") or []
                require(len(lengths) == 1 and lengths[0].isdigit(), 411, "LENGTH_REQUIRED")
                length = int(lengths[0])
                require(0 < length <= MAX_BYTES, 413, "BODY_LIMIT")
                raw = self.rfile.read(length)
                require(len(raw) == length, 400, "TRUNCATED_BODY")
                data = parse(raw)
                if self.path == "/v1/challenges":
                    result = service.challenge(tenant, role, data)
                else:
                    if self.path not in ("/v1/enrollments", "/v1/revocations"):
                        require(type(data) is dict and type(data.get("body")) is dict)
                        service.authorize_signer(auth[7:], data["body"].get("kid"))
                    result = service.mutate(tenant, role, self.path, data)
            else:
                require(role in ("client", "admin", "reader"), 403, "ROLE_FORBIDDEN")
                parts = self.path.split("/")
                require(
                    len(parts) in (4, 5)
                    and parts[1:3] == ["v1", "jobs"]
                    and (len(parts) == 4 or parts[4] == "report"),
                    404,
                    "NOT_FOUND",
                )
                # Serialize report materialization AND send with receipt/expiry.
                # Already transmitted bytes cannot be recalled from a client.
                with service.exclusive():
                    service.authorize_read(auth[7:], parts[3])
                    result = service.read(tenant, parts[3], len(parts) == 5)
                    self.send(*result)
                return
            self.send(*result)

        def dispatch(self):
            try:
                self.route()
            except Problem as error:
                self.send(
                    error.status,
                    {
                        "type": "urn:aa:problem:" + error.code.lower(),
                        "title": error.code,
                        "status": error.status,
                        "code": error.code,
                    },
                    "application/problem+json",
                )
            except (sqlite3.Error, OSError, TimeoutError):
                self.send(
                    503,
                    {
                        "type": "urn:aa:problem:service-unavailable",
                        "title": "SERVICE_UNAVAILABLE",
                        "status": 503,
                        "code": "SERVICE_UNAVAILABLE",
                    },
                    "application/problem+json",
                )
            except Exception:  # noqa: BLE001 - do not expose internal errors over HTTP
                self.send(
                    500,
                    {
                        "type": "urn:aa:problem:internal-error",
                        "title": "INTERNAL_ERROR",
                        "status": 500,
                        "code": "INTERNAL_ERROR",
                    },
                    "application/problem+json",
                )

        def handle_request(self):
            token = DEADLINE.set(self.deadline)
            try:
                # Lock acquisition is inside dispatch's error handling. Slow body
                # intake cannot hold the shared lifecycle/delete lock.
                self.dispatch()
            except (OSError, TimeoutError):
                pass  # Disconnect is never a receipt.
            finally:
                DEADLINE.reset(token)

        do_GET = handle_request
        do_POST = handle_request
        do_DELETE = handle_request
        do_PUT = handle_request
        do_PATCH = handle_request
        do_HEAD = handle_request
        do_OPTIONS = handle_request

    return PrivateServer(("127.0.0.1", port), Handler)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--state", type=Path, required=True)
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--port", type=int, default=8765)
    parser.add_argument(
        "--signer-key",
        type=Path,
        required=True,
        help="operator-only report key; never client/root/runner key",
    )
    args = parser.parse_args()
    process_limits()
    config = parse(args.config.read_bytes())
    from research.private_service.boundary import ReportSigner
    from research.private_service.protocol import fields

    fields(config, "root_pins report_public_key trust_version runner_tenant runner_kid tokens")
    for entry in config["tokens"]:
        fields(entry, "tenant role sha256 subjects")
    instance = server(Service(args.state, config, ReportSigner(args.signer_key)), args.port)
    print(f"Private inspector: http://127.0.0.1:{instance.server_port}", flush=True)
    try:
        instance.serve_forever()
    finally:
        instance.server_close()


if __name__ == "__main__":
    try:
        main()
    except (Problem, OSError, ValueError, KeyError, TypeError):
        raise SystemExit("PRIVATE_SERVICE_START_FAILED") from None
