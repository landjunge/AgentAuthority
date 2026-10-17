"""Narrow changed-path browser probe; uses existing Playwright and Chrome only.

The product runs under the supplied >=3.12 Python in its own temporary state.
Passwords stay in process memory. Evidence contains fixed check names/booleans;
this probe does not exercise the earlier complete browser qualification series.
"""

import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import tempfile

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--python", required=True)
    parser.add_argument("--chrome", required=True)
    parser.add_argument("--evidence", type=Path, required=True)
    args = parser.parse_args()
    result = {
        "schema": "aa-helpcenter-ui-check-v1",
        "synthetic": True,
        "checks": {},
        "pageErrors": 0,
        "sourceSha256": {
            name: hashlib.sha256((ROOT / name).read_bytes()).hexdigest()
            for name in (
                "agent_authority/browser_handoff.py",
                "agent_authority/browser_static/app.js",
                "agent_authority/browser_static/index.html",
                "agent_authority/browser_static/strings.json",
            )
        },
    }

    def check(name, condition):
        result["checks"][name] = bool(condition)
        if not condition:
            raise RuntimeError(name)

    process = None
    browser = None
    phase = "synthetic-state"
    try:
        with tempfile.TemporaryDirectory(prefix="aa-helpcenter-ui-") as temporary:
            state = Path(temporary) / "state"
            output = subprocess.check_output(
                [args.python, "-B", "-m", "agent_authority.browser", "init-synthetic", "--state", str(state)],
                cwd=ROOT,
                text=True,
            )
            credentials = dict(
                line.split(": ", 1)
                for line in output.splitlines()
                if line.startswith(("alice:", "bob:"))
            )
            config_path = state / "config.json"
            config = json.loads(config_path.read_text())
            config["accounts"][0]["scopes"].append(
                {
                    "sourceId": "hilfezentrum-synthetic",
                    "jobId": "30000000-0000-4000-8000-000000000001",
                    "adapters": ["report"],
                }
            )
            config_path.write_text(json.dumps(config))
            process = subprocess.Popen(
                [args.python, "-B", "-m", "agent_authority.browser", "serve", "--state", str(state), "--port", "0"],
                cwd=ROOT,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
            origin = process.stdout.readline().strip().rsplit(" ", 1)[-1]
            with sync_playwright() as playwright:
                phase = "browser-launch"
                browser = playwright.chromium.launch(
                    headless=True, executable_path=args.chrome, args=["--disable-gpu"]
                )
                result["browserVersion"] = browser.version
                for lang in ("de", "en"):
                    phase = lang + "-context-login"
                    context = browser.new_context(locale=lang, reduced_motion="reduce")
                    page = context.new_page()
                    page_errors = []
                    page.on("pageerror", lambda error: page_errors.append(type(error).__name__))
                    phase = lang + "-page-goto"
                    page.goto(origin + "#hilfezentrum-demo-" + lang)
                    phase = lang + "-login-form"
                    page.wait_for_selector("#login-form")
                    phase = lang + "-username-input"
                    page.locator("#username").fill("alice")
                    phase = lang + "-password-input"
                    page.locator("#password").fill(credentials["alice"])
                    phase = lang + "-submit-login"
                    page.locator('#login-form button[type="submit"]').click()
                    phase = lang + "-await-context-graph"
                    page.wait_for_selector("#graph-nodes > g:nth-child(5)")
                    phase = lang + "-graph-and-boundaries"
                    check(lang + "_deep_link_context_graph", page.url.endswith("#graph"))
                    check(lang + "_language", page.locator("html").get_attribute("lang") == lang)
                    check(lang + "_synthetic_mode", "SYNTHETIC" in page.locator("#data-mode").inner_text() if lang == "en" else "SYNTHETISCH" in page.locator("#data-mode").inner_text())
                    expected_return = "https://ki-hilfezentrum.netzwerkpunkt.de/" + ("en.html" if lang == "en" else "") + "#agent-authority"
                    check(lang + "_fixed_helpcenter_return", all(href == expected_return for href in page.locator(".help-center-return").evaluate_all("items => items.map(a => a.href)")))
                    check(lang + "_no_verified_nodes", page.locator("#graph-nodes .status-verified").count() == 0)
                    check(lang + "_no_imported_report", page.locator("#report-select").input_value() == "")
                    check(lang + "_no_warning_claim", page.locator("#critical-warning").is_hidden())
                    with page.expect_download() as download:
                        phase = lang + "-context-export"
                        page.locator("#export").click()
                    exported = json.loads(Path(download.value.path()).read_text())
                    check(lang + "_export_fixed_context", exported["schema"] == "hilfezentrum.authority-context.v1" and exported["case"]["synthetic"] is True)
                    check(lang + "_export_no_identity_or_transport", exported["agent_identity_verified"] is False and exported["independence_verified"] is False and exported["external_authority"] == "unknown" and exported["handoff"]["shared_sign_in"] is False and exported["handoff"]["data_transferred"] is False)
                    page.locator("#refresh").click()
                    phase = lang + "-context-refresh"
                    page.wait_for_selector("body:not(.busy)")
                    check(lang + "_refresh_retains_context_boundary", page.locator("#graph-nodes > g").count() == 5 and page.locator("#global-message").get_attribute("class") == "message warning")
                    result["pageErrors"] += len(page_errors)
                    context.close()
                browser.close()
                browser = None
            process.terminate()
            process.wait(timeout=10)
            check("temporary_service_stopped", process.poll() is not None)
            process = None
        check("temporary_state_removed", not Path(temporary).exists())
        check("no_browser_errors", result["pageErrors"] == 0)
        result["passed"] = True
    except Exception as exc:
        result["passed"] = False
        result["failureType"] = type(exc).__name__
        result["failurePhase"] = phase
        result["browserClosed"] = "closed" in str(exc).lower()
        result["cspEvaluationBlocked"] = "unsafe-eval" in str(exc).lower()
    finally:
        if process is not None:
            process.terminate()
            process.wait(timeout=10)
    args.evidence.parent.mkdir(parents=True, exist_ok=True)
    args.evidence.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))
    return 0 if result["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
