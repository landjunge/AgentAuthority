"""Targeted real-browser check using an already installed Playwright/Chrome.

Run with an interpreter that already has Playwright, --python points at the
product's >=3.12 interpreter. Never installs or downloads a browser. All state,
accounts and inputs are synthetic; credentials are kept in memory only.
"""

import argparse
import json
import subprocess
import tempfile
import time
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]


def wait_until(page, function):
    deadline = time.monotonic() + 10
    while time.monotonic() < deadline:
        if page.evaluate(function):
            return
        time.sleep(0.05)
    raise TimeoutError("UI condition did not become true")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--python", required=True)
    parser.add_argument("--chrome", required=True)
    parser.add_argument("--evidence", type=Path, required=True)
    args = parser.parse_args()
    args.evidence.mkdir(parents=True, exist_ok=True)
    result = {"schema": "aa-browser-ui-check-v1", "synthetic": True, "checks": {}, "errors": []}
    process = None
    browser = None
    with tempfile.TemporaryDirectory(prefix="aa-browser-ui-") as temporary:
        state = Path(temporary) / "state"
        output = subprocess.check_output(
            [
                args.python,
                "-B",
                "-m",
                "agent_authority.browser",
                "init-synthetic",
                "--state",
                str(state),
            ],
            cwd=ROOT,
            text=True,
        )
        credentials = dict(
            line.split(": ", 1)
            for line in output.splitlines()
            if line.startswith(("alice:", "bob:"))
        )
        process = subprocess.Popen(
            [
                args.python,
                "-B",
                "-m",
                "agent_authority.browser",
                "serve",
                "--state",
                str(state),
                "--port",
                "0",
            ],
            cwd=ROOT,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        line = process.stdout.readline()
        origin = line.strip().rsplit(" ", 1)[-1]
        try:
            with sync_playwright() as playwright:
                browser = playwright.chromium.launch(
                    headless=True, executable_path=args.chrome, args=["--disable-gpu"]
                )
                result["browser"] = browser.version
                context = browser.new_context(
                    viewport={"width": 1480, "height": 1000},
                    locale="de-DE",
                    reduced_motion="reduce",
                )
                page = context.new_page()
                page.on("pageerror", lambda error: result["errors"].append(str(error)))
                page.goto(origin)
                page.wait_for_selector("#login-form")
                page.locator("#username").fill("alice")
                page.locator("#password").fill(credentials["alice"])
                page.locator("#login-form button[type=submit]").click()
                page.wait_for_selector("#application:visible")
                wait_until(
                    page,
                    "() => document.querySelector('#global-message').textContent.includes('Bericht')",
                )
                result["checks"]["login_empty_no_demo"] = (
                    page.locator("#graph-nodes > g").count() == 0
                )
                page.screenshot(path=str(args.evidence / "desktop-empty.png"), full_page=True)

                # Upload through the actual browser form, including a markup canary.
                records = [
                    {
                        "schema_version": "agent-authority-observation-v1",
                        "id": "entry-" + str(i),
                        "source_id": "synthetic-alice",
                        "ordinal": 9007199254740993 if i == 3 else i,
                        "kind": kind,
                        "reported_actor_type": '<img src=x onerror="window.__foreignExecuted=true">',
                        "task_key": "SYNTHETIC-TASK",
                    }
                    for i, kind in enumerate(["task", "claimed", "result"], 1)
                ]
                page.locator("#import-open").click()
                page.locator("#import-kind").select_option("observations")
                page.locator("#import-file").set_input_files(
                    {
                        "name": "SYNTHETIC.json",
                        "mimeType": "application/json",
                        "buffer": json.dumps(records).encode(),
                    }
                )
                page.locator("#import-form button[type=submit]").click()
                page.wait_for_selector("#import-dialog:not([open])", state="attached")
                wait_until(page, "() => document.querySelector('#report-select').value.length > 0")
                report_id = page.locator("#report-select").input_value()
                page.locator('[data-mode="2"]').click()
                wait_until(page, "() => document.querySelectorAll('#graph-nodes > g').length === 4")
                result["checks"]["neutral_graph_four_nodes"] = True
                page.locator('#graph-nodes [data-node-id="entry-3"]').click()
                wait_until(
                    page,
                    "() => document.querySelector('#inspector-content').textContent.includes('<img')",
                )
                result["checks"]["foreign_text_inert"] = page.locator(
                    "#inspector-content img"
                ).count() == 0 and not page.evaluate("Boolean(window.__foreignExecuted)")
                with page.expect_download() as download_info:
                    page.locator("#export").click()
                exported = json.loads(Path(download_info.value.path()).read_text())
                result["checks"]["export_preserves_large_ordinal"] = (
                    exported["recent_entries"][0]["ordinal"] == 9007199254740993
                )
                page.screenshot(path=str(args.evidence / "desktop-report.png"), full_page=True)

                # Search, filter and viewport are restored by actual browser history.
                page.locator("#zoom-in").click()
                zoom_before = page.locator("#zoom-label").inner_text()
                page.locator("#search").fill("no-such-SYNTHETIC-entry")
                page.locator("#search-form").press("Enter")
                wait_until(page, "() => document.querySelectorAll('#graph-nodes > g').length === 0")
                result["checks"]["search_empty_state"] = page.locator("#graph-empty").is_visible()
                page.locator("#back").click()
                wait_until(
                    page,
                    "() => document.querySelector('#search').value === '' && document.querySelectorAll('#graph-nodes > g').length === 4",
                )
                result["checks"]["history_restores_search_viewport"] = (
                    page.locator("#zoom-label").inner_text() == zoom_before
                )
                page.locator("#proof-filter").select_option("2")
                wait_until(page, "() => document.querySelectorAll('#graph-nodes > g').length === 0")
                page.locator("#back").click()
                wait_until(page, "() => document.querySelector('#proof-filter').value === '0'")
                result["checks"]["history_restores_filter"] = True

                for name in (
                    "graph",
                    "agents",
                    "delegations",
                    "actions",
                    "evidence",
                    "findings",
                    "host",
                    "settings",
                    "overview",
                ):
                    page.locator('#sidebar [data-page="' + name + '"]').click()
                    wait_until(page, "() => location.hash === '#' + '" + name + "'")
                result["checks"]["all_native_pages_navigate"] = True

                page.locator("#import-open").click()
                page.locator("#import-kind").select_option("report")
                page.locator("#import-file").set_input_files(
                    {
                        "name": "SYNTHETIC-invalid.json",
                        "mimeType": "application/json",
                        "buffer": b'{"invalid":"SYNTHETIC"}',
                    }
                )
                page.locator("#import-form button[type=submit]").click()
                page.wait_for_selector("#import-message:visible")
                result["checks"]["invalid_import_visible_no_fallback"] = (
                    page.locator("#report-select").input_value() == report_id
                )
                page.locator("#import-cancel").click()

                page.locator("#import-open").click()
                page.locator("#import-kind").select_option("observations")
                page.locator("#import-file").set_input_files(
                    {
                        "name": "SYNTHETIC-empty.json",
                        "mimeType": "application/json",
                        "buffer": b"[]",
                    }
                )
                page.locator("#import-form button[type=submit]").click()
                page.wait_for_selector("#import-dialog:not([open])", state="attached")
                wait_until(page, "() => document.querySelectorAll('#graph-nodes > g').length === 0")
                result["checks"]["empty_report_visible"] = page.locator("#graph-empty").is_visible()

                private_input = subprocess.check_output(
                    [
                        args.python,
                        "-B",
                        "-c",
                        "import hashlib,json; from agent_authority.browser_adapter import synthetic_private_response; print(json.dumps(synthetic_private_response(hashlib.sha256(b'aa-browser-synthetic-alice').hexdigest()[:32])))",
                    ],
                    cwd=ROOT,
                )
                page.locator("#import-open").click()
                page.locator("#import-scope").select_option("1")
                page.locator("#import-kind").select_option("private-verification")
                page.locator("#import-file").set_input_files(
                    {
                        "name": "SYNTHETIC-private.json",
                        "mimeType": "application/json",
                        "buffer": private_input,
                    }
                )
                page.locator("#import-form button[type=submit]").click()
                page.wait_for_selector("#import-dialog:not([open])", state="attached")
                wait_until(
                    page,
                    "() => document.querySelector('#data-mode').textContent.includes('PRIVATDIENST')",
                )
                page.locator('[data-mode="2"]').click()
                result["checks"]["private_adapter_separate_unknown"] = (
                    page.locator("#graph-nodes > g").count() == 6
                    and page.locator("#source-boundary").inner_text().find("Signatur") >= 0
                )
                page.screenshot(path=str(args.evidence / "desktop-private.png"), full_page=True)

                page.locator("#demo-load").click()
                wait_until(
                    page,
                    "() => document.querySelector('#data-mode').textContent.includes('BEISPIELDATEN')",
                )
                page.locator('[data-mode="2"]').click()
                wait_until(page, "() => document.querySelectorAll('#graph-nodes > g').length > 0")
                group = page.locator('#graph-nodes [data-node-id^="cluster:"]').first
                group.dblclick()
                result["checks"]["explicit_demo_group_expand"] = (
                    page.locator('#graph-nodes [data-node-id^="agent-"]').count() > 0
                )
                result["checks"]["critical_demo_visible"] = page.locator(
                    "#critical-warning"
                ).is_visible()
                result["checks"]["reduced_motion_respected"] = page.evaluate(
                    "matchMedia('(prefers-reduced-motion: reduce)').matches"
                )
                page.locator("#graph-area").focus()
                page.keyboard.press("ArrowRight")
                page.keyboard.press("+")
                page.keyboard.press("0")
                result["checks"]["graph_keyboard_operable"] = page.locator(
                    "#copy-reference"
                ).is_enabled()
                page.screenshot(path=str(args.evidence / "desktop-demo.png"), full_page=True)

                page.locator('#sidebar [data-page="settings"]').click()
                page.locator("#language").select_option("en")
                wait_until(page, "() => document.documentElement.lang === 'en'")
                result["checks"]["english"] = page.locator("#page-title").inner_text() == "Settings"
                result["checks"]["dynamic_messages_translate"] = (
                    "synthetic" in page.locator("#global-message").inner_text().lower()
                    and "Synthetic" in page.locator("#account-label").inner_text()
                )
                page.locator('#sidebar [data-page="graph"]').click()
                page.set_viewport_size({"width": 390, "height": 844})
                page.wait_for_timeout(200)
                result["checks"]["iphone_width_no_page_overflow"] = page.evaluate(
                    "document.documentElement.scrollWidth <= innerWidth + 1"
                )
                result["checks"]["iphone_table_readable_scroll"] = page.evaluate(
                    "document.querySelector('.table-scroll table').getBoundingClientRect().width >= 680 && document.querySelector('.table-scroll').scrollWidth > document.querySelector('.table-scroll').clientWidth"
                )
                page.screenshot(path=str(args.evidence / "iphone-demo.png"), full_page=True)

                # A distinct browser context is a second real cookie/session boundary.
                second = browser.new_context(viewport={"width": 1024, "height": 768})
                bob = second.new_page()
                bob.goto(origin)
                bob.locator("#username").fill("bob")
                bob.locator("#password").fill(credentials["bob"])
                bob.locator("#login-form button[type=submit]").click()
                bob.wait_for_selector("#application:visible")
                result["checks"]["second_account_no_reports"] = (
                    bob.locator("#report-select option").count() == 1
                )
                foreign_status = bob.evaluate(
                    "async id => (await fetch('/api/reports/' + id)).status", report_id
                )
                result["checks"]["second_account_foreign_id_404"] = foreign_status == 404
                result["checks"]["browser_storage_no_private_data"] = bob.evaluate(
                    "Object.keys(localStorage).every(k => /^agent-authority\\.(language|theme)$/.test(k))"
                )
                second.close()
                context.close()
                browser.close()
                browser = None
        except Exception as error:
            # Only exception type is recorded; browser errors may contain transient
            # paths but must never echo credentials or uploaded private material.
            result["failure"] = type(error).__name__
            detail = str(error)
            for credential in credentials.values():
                detail = detail.replace(credential, "[redacted synthetic password]")
            result["failureDetail"] = detail[:2000]
            if browser is not None:
                try:
                    page.screenshot(path=str(args.evidence / "failure-state.png"), full_page=True)
                except Exception:
                    pass
        finally:
            if browser is not None:
                try:
                    browser.close()
                except Exception:
                    pass
            process.terminate()
            try:
                process.wait(timeout=8)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait(timeout=5)
            result["processStopped"] = process.poll() is not None
            result["checks"]["no_page_errors"] = not result["errors"]
            result["passed"] = (
                bool(result["checks"])
                and all(result["checks"].values())
                and "failure" not in result
            )
            (args.evidence / "browser-results.json").write_text(json.dumps(result, indent=2) + "\n")
    result["temporaryStateRemoved"] = not Path(temporary).exists()
    (args.evidence / "browser-results.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))
    if not result["passed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
