"""Loopback-only HTTP adapter and browser inspector. No ambient browser login."""

import argparse
import json
import sqlite3
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import Request, urlopen

from research.private_service.protocol import Problem, parse, require
from research.private_service.service import Service

MAX_BYTES = 262144
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
    require(url.startswith("http://127.0.0.1:"))
    raw = None if body is None else json.dumps(body).encode()
    req = Request(
        url + path,
        data=raw,
        method=method,
        headers={"Authorization": "Bearer " + token, "Content-Type": "application/json"},
    )
    try:
        response = urlopen(req, timeout=30)
    except HTTPError as error:
        response = error
    with response:
        return response.status, json.loads(response.read())


def server(service, port=0):
    class PrivateServer(HTTPServer):
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
        def setup(self):
            super().setup()
            self.connection.settimeout(5)

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
            self.send_header("X-Content-Type-Options", "nosniff")
            self.send_header(
                "Content-Security-Policy",
                "default-src 'none'; script-src 'self'; connect-src 'self'; frame-ancestors 'none'; form-action 'none'",
            )
            self.end_headers()
            self.wfile.write(raw)

        def route(self):
            host = self.headers.get("Host", "")
            require(host == f"127.0.0.1:{self.server.server_port}", 403, "HOST_FORBIDDEN")
            origin = self.headers.get("Origin")
            require(origin is None or origin == f"http://{host}", 403, "ORIGIN_FORBIDDEN")
            require(not self.headers.get("Transfer-Encoding"), 400, "TRANSFER_ENCODING_UNSUPPORTED")
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
                result = service.read(tenant, parts[3], len(parts) == 5)
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
            try:
                # Serialize report materialization+send with deletion across API
                # processes. Already sent bytes cannot be recalled from a client.
                with service.exclusive():
                    self.dispatch()
            except (OSError, TimeoutError):
                pass  # Disconnect is never a receipt.

        do_GET = handle_request
        do_POST = handle_request

    return PrivateServer(("127.0.0.1", port), Handler)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--state", type=Path, required=True)
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--port", type=int, default=8765)
    args = parser.parse_args()
    instance = server(Service(args.state, json.loads(args.config.read_text())), args.port)
    print(f"Private inspector: http://127.0.0.1:{instance.server_port}", flush=True)
    instance.serve_forever()
