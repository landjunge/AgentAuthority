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
document.getElementById('summary').textContent=data.label||(body?
(names[body.classification]||'Ergebnis unbekannt')+'. Umfang: kontrollierter Linux-Test. Provideridentitaet unbekannt.':data.code||'Abruf fehlgeschlagen');
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
    class Handler(BaseHTTPRequestHandler):
        def setup(self):
            super().setup()
            self.connection.settimeout(5)

        def log_message(self, *args):
            pass  # Never log tokens, paths, bodies or free exception strings.

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

        def handle_request(self):
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

        do_GET = handle_request
        do_POST = handle_request

    return HTTPServer(("127.0.0.1", port), Handler)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--state", type=Path, required=True)
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--port", type=int, default=8765)
    args = parser.parse_args()
    instance = server(Service(args.state, json.loads(args.config.read_text())), args.port)
    print(f"Private inspector: http://127.0.0.1:{instance.server_port}", flush=True)
    instance.serve_forever()
