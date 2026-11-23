"""Typed producer claims for update observations, with no trust or action authority."""

from __future__ import annotations

import re
from collections.abc import Iterable
from dataclasses import dataclass
from typing import Any

from agent_authority.file_reader import ReadIssue

UPDATE_EVENT = "update.observed"
REFERENCE = re.compile(r"[A-Za-z0-9][A-Za-z0-9_.:-]{0,255}\Z")
COMMIT = re.compile(r"(?:[0-9a-f]{40}|[0-9a-f]{64})\Z")
SHA256 = re.compile(r"[0-9a-f]{64}\Z")
CI_TERMINAL = frozenset({"success", "failure", "cancelled", "skipped"})

FIELDS: dict[str, dict[str, re.Pattern[str] | frozenset[str]]] = {
    "source": {"commit": COMMIT, "ref": REFERENCE},
    "release": {
        "tag": REFERENCE,
        "commit": COMMIT,
        "ref": REFERENCE,
        "status": frozenset({"published", "not_published", "unknown"}),
    },
    "artifact": {"sha256": SHA256, "commit": COMMIT, "ref": REFERENCE},
    "ci": {
        "commit": COMMIT,
        "run_ref": REFERENCE,
        "status": CI_TERMINAL | {"pending", "unknown"},
    },
    "installation": {
        "commit": COMMIT,
        "artifact_sha256": SHA256,
        "target_ref": REFERENCE,
        "status": frozenset({"present", "absent", "unknown"}),
    },
}


@dataclass(frozen=True)
class UpdateEvidence:
    update_id: str
    facts: tuple[tuple[str, tuple[tuple[str, str], ...]], ...]

    def projection(self) -> dict[str, Any]:
        reported = {name: dict(values) for name, values in self.facts}
        source_commit = reported["source"].get("commit")
        differences = [
            {"fields": ["source.commit", f"{name}.commit"], "state": "reported_difference"}
            for name in ("release", "artifact", "ci", "installation")
            if source_commit
            and (related := reported[name].get("commit"))
            and source_commit != related
        ]
        artifact_hash = reported["artifact"].get("sha256")
        installed_hash = reported["installation"].get("artifact_sha256")
        if artifact_hash and installed_hash and artifact_hash != installed_hash:
            differences.append(
                {
                    "fields": ["artifact.sha256", "installation.artifact_sha256"],
                    "state": "reported_difference",
                }
            )
        return {
            "update_id": self.update_id,
            "facts": {
                name: {
                    "state": "reported"
                    if values and values.get("status") != "unknown"
                    else "unknown",
                    "claims": values,
                }
                for name, values in reported.items()
            },
            "differences": differences,
            "signature_verification": "unknown",
        }


def parse_update_evidence(raw: Any) -> UpdateEvidence:
    """Keep only bounded fact metadata; never copy a signature or raw input."""
    if not isinstance(raw, dict) or not isinstance(raw.get("update_id"), str):
        raise ReadIssue("workflow_invalid_update_evidence")
    identifier = raw["update_id"]
    if not REFERENCE.fullmatch(identifier):
        raise ReadIssue("workflow_invalid_update_evidence")
    facts = []
    for name, fields in FIELDS.items():
        value = raw.get(name, {})
        if not isinstance(value, dict):
            raise ReadIssue("workflow_invalid_update_evidence")
        claims = []
        for field, constraint in fields.items():
            if field not in value:
                continue
            item = value[field]
            if not isinstance(item, str):
                raise ReadIssue("workflow_invalid_update_evidence")
            if isinstance(constraint, frozenset):
                valid = item in constraint
            else:
                valid = constraint.fullmatch(item) is not None
            if not valid:
                raise ReadIssue("workflow_invalid_update_evidence")
            claims.append((field, item))
        facts.append((name, tuple(claims)))
    return UpdateEvidence(identifier, tuple(facts))


def ci_conflicts(
    observations: Iterable[tuple[str, UpdateEvidence]], limit: int
) -> tuple[list[dict[str, Any]], int]:
    """Compare terminal claims for the same immutable check-attempt reference."""
    groups: dict[tuple[str, str, str], dict[str, str]] = {}
    for event_id, evidence in observations:
        ci = dict(dict(evidence.facts)["ci"])
        status, commit, ref = ci.get("status"), ci.get("commit"), ci.get("run_ref")
        if status is not None and status in CI_TERMINAL and commit and ref:
            groups.setdefault((evidence.update_id, commit, ref), {}).setdefault(status, event_id)
    conflicts = [
        {
            "update_id": update_id,
            "commit": commit,
            "ci_run_ref": ref,
            "claims": [
                {"status": status, "event_id": event_id} for status, event_id in statuses.items()
            ],
            "state": "reported_conflict",
        }
        for (update_id, commit, ref), statuses in groups.items()
        if len(statuses) > 1
    ]
    return conflicts[:limit], max(0, len(conflicts) - limit)
