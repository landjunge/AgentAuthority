"""Linux private API plus a peer-bound control channel, never a root dispatch API."""

import json
import os
import sys
import threading
import traceback
from pathlib import Path

from research.debian_private.ipc import SECURE, component, guard_healthy, serve, uid
from research.private_service.http import server
from research.private_service.limits import process_limits
from research.private_service.protocol import fields, require, verify
from research.private_service.service import Service


def healthy():
    guard_healthy()


def main():
    process_limits()
    os.environ["AA_PRIVATE_LINUX_IPC"] = "1"
    config = json.loads(Path("/etc/aa-private/api.json").read_bytes())

    def report(body):
        signed = component("report", body)
        if "checks" in body:
            require(
                component("verify", {"cleanup_report": signed}) == {"inputs_removed": True},
                503,
                "INPUT_CLEANUP_FAILED",
            )
        return signed

    instance = Service(SECURE / "api", config, report)

    def control(data):
        healthy()
        if data == {"op": "claim"}:
            binding = instance.claim()
            if binding is None:
                return None
            tenant, jid = binding["tenant"], binding["job_id"]
            with instance.connection() as db:
                row = db.execute(
                    "SELECT request,acceptance FROM jobs WHERE tenant=? AND id=?", (tenant, jid)
                ).fetchone()
            return {
                "binding": binding,
                "request": instance.unseal(tenant, jid, "request", row[0]),
                "acceptance": instance.unseal(tenant, jid, "acceptance", row[1]),
            }
        fields(data, "op pin")
        require(data["op"] == "pin", 422, "CONTROL_OPERATION")
        require(
            verify(
                json.loads(Path("/etc/aa-private/collector-public.json").read_bytes())["public"],
                data["pin"],
            ),
            403,
            "COLLECTOR_SIGNATURE",
        )
        pin = data["pin"]["body"]
        fields(pin, "pins expected")
        tenant, jid = pin["expected"]["tenant"], pin["expected"]["job_id"]
        with instance.exclusive(), instance.connection() as db:
            db.execute("BEGIN IMMEDIATE")
            row = db.execute(
                "SELECT state FROM jobs WHERE tenant=? AND id=?", (tenant, jid)
            ).fetchone()
            require(row == ("running",), 409, "JOB_STATE")
            cached = db.execute(
                "SELECT context FROM dispatch_pins WHERE tenant=? AND job_id=?", (tenant, jid)
            ).fetchone()
            if cached is None:
                db.execute(
                    "INSERT INTO dispatch_pins VALUES (?,?,?)",
                    (tenant, jid, instance.seal(tenant, jid, "pins", pin["pins"])),
                )
            else:
                require(
                    instance.unseal(tenant, jid, "pins", cached[0]) == pin["pins"],
                    409,
                    "PIN_ALREADY_BOUND",
                )
            db.commit()
        return {"pinned": True}

    thread = threading.Thread(
        target=lambda: serve("control", {uid("aa-runner")}, control, output=262144), daemon=True
    )
    thread.start()
    old = instance.mutate

    def mutate(tenant, role, path, data):
        with instance.exclusive():
            if path == "/v1/jobs":
                healthy()
                with instance.connection() as db:
                    active = db.execute(
                        "SELECT count(*) FROM jobs WHERE state IN ('awaiting_acceptance','queued','running')"
                    ).fetchone()[0]
                    cached = db.execute(
                        "SELECT 1 FROM requests WHERE tenant=? AND idem=?",
                        (tenant, data.get("body", {}).get("idempotency_key")),
                    ).fetchone()
                require(active == 0 or cached is not None, 429, "ONE_JOB_LIMIT")
            return old(tenant, role, path, data)

    instance.mutate = mutate
    listener = server(instance, 8765)
    original_finish = listener.RequestHandlerClass.finish

    def finish(handler):
        try:
            original_finish(handler)
        finally:
            # Reap our cancelled absolute-deadline thread before another request.
            # This avoids transient thread stacks/arenas exhausting RLIMIT_AS.
            handler.timer.join(timeout=0.2)

    listener.RequestHandlerClass.finish = finish

    def error_metadata(_request, _address):
        error = sys.exception()
        (SECURE / "api/transport-error.json").write_text(
            json.dumps(
                {
                    "type": type(error).__name__,
                    "frames": [
                        {
                            "function": frame.name,
                            "line": frame.lineno,
                            "file": Path(frame.filename).name,
                        }
                        for frame in traceback.extract_tb(error.__traceback__)
                    ],
                }
            )
        )

    listener.handle_error = error_metadata
    original_rate = listener.rate

    def rate(tenant):
        original_rate(tenant)
        require(len(listener.rates[tenant]) <= 48, 429, "RATE_LIMIT")

    listener.rate = rate
    try:
        listener.serve_forever()
    finally:
        listener.server_close()


if __name__ == "__main__":
    main()
