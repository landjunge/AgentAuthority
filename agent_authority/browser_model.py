"""Bounded browser projection of the existing observer report and native graph.

The wire vocabulary follows AuthorityCore/Models.swift and UIWarnings.swift.
Only the neutral ``build_report`` contract is accepted here. macOS ES events,
Linux verifier reports and UI graph documents are distinct contracts, never
implicitly reinterpreted as neutral observations. This module executes nothing.
"""

from __future__ import annotations

import json
import re
from collections import Counter, deque
from typing import Any

from agent_authority.observations import KINDS, TOKEN
from agent_authority.report import DIAGNOSTIC_TEXT

MAX_REPORT_BYTES = 8 * 1024 * 1024
MAX_ENTRIES = 10_000
MAX_DISPLAY = 100
MAX_NODES = 10_000
MAX_EDGES = 30_000
MAX_EVIDENCE = 64
GRAPH_SCHEMA = "agent-authority-ui-graph-v1"
REPORT_SCHEMA = "agent-authority-observation-report-v1"
NODE_KINDS = frozenset(
    {
        "agent",
        "identity",
        "authority",
        "delegation",
        "process",
        "action",
        "evidence",
        "task",
        "entry",
        "cluster",
    }
)
STATUSES = frozenset({"reported", "observed", "verified", "incomplete", "contradictory", "unknown"})
SHA256 = re.compile(r"[0-9a-f]{64}\Z")
TASK_ALIAS = re.compile(r"A[1-9][0-9]{0,4}\Z")


class ModelError(ValueError):
    """A bounded contract failure; messages contain fixed labels, not input data."""


def _require(condition: bool, label: str) -> None:
    if not condition:
        raise ModelError("invalid " + label)


def _object(value: Any, required: set[str], label: str, optional: set[str] | None = None) -> dict:
    _require(type(value) is dict, label)
    _require(required <= value.keys() <= required | (optional or set()), label + " fields")
    return value


def _text(value: Any, maximum: int, label: str, *, empty: bool = False) -> str:
    _require(type(value) is str and (empty or bool(value.strip())) and len(value) <= maximum, label)
    return value


def _number(value: Any, maximum: int, label: str, minimum: int = 0) -> int:
    _require(type(value) is int and minimum <= value <= maximum, label)
    return value


def _boolean(value: Any, label: str) -> bool:
    _require(type(value) is bool, label)
    return value


def _list(value: Any, maximum: int, label: str) -> list:
    _require(type(value) is list and len(value) <= maximum, label)
    return value


def _token(value: Any, label: str) -> str:
    _require(type(value) is str and TOKEN.fullmatch(value) is not None, label)
    return value


def _counts(value: Any, label: str) -> dict:
    _require(type(value) is dict and value.keys() <= KINDS, label)
    for count in value.values():
        _number(count, MAX_ENTRIES, label, 1)
    _require(sum(value.values()) <= MAX_ENTRIES, label)
    return value


def _unique(pairs: list[tuple[str, Any]]) -> dict:
    value: dict = {}
    for key, item in pairs:
        _require(key not in value, "duplicate JSON key")
        value[key] = item
    return value


def _nonfinite(_: str) -> Any:
    raise ModelError("invalid nonfinite JSON")


def _load(data: bytes | str | dict) -> dict:
    try:
        if type(data) is dict:
            encoded = json.dumps(data, ensure_ascii=True, allow_nan=False, separators=(",", ":"))
            _require(len(encoded.encode("utf-8")) <= MAX_REPORT_BYTES, "report size")
            # Also detach caller-owned dictionaries from returned graph/report values.
            raw = json.loads(encoded)
        else:
            _require(type(data) in {bytes, str}, "report input")
            encoded_bytes = data if type(data) is bytes else data.encode("utf-8")
            _require(len(encoded_bytes) <= MAX_REPORT_BYTES, "report size")
            raw = json.loads(encoded_bytes, object_pairs_hook=_unique, parse_constant=_nonfinite)
    except (UnicodeError, RecursionError, TypeError, ValueError) as exc:
        if isinstance(exc, ModelError):
            raise
        raise ModelError("invalid report JSON") from None
    _require(type(raw) is dict, "report object")
    return raw


def validate_report(report: dict) -> None:
    """Validate every field emitted by build_report, including omission counters.

    Unknown fields are rejected so a forged trust marker or arbitrary input
    content cannot be carried into the raw evidence panel. Diagnostic references
    may contain invalid filenames; those are bounded foreign text, never paths.
    """
    raw = _object(
        report,
        {
            "schema_version",
            "role",
            "source",
            "summary",
            "tasks",
            "recent_entries",
            "warnings",
            "display",
            "task_completion_proven",
            "rights_inherited",
        },
        "report",
    )
    _require(
        raw["schema_version"] == REPORT_SCHEMA and raw["role"] == "observer_only", "report schema"
    )
    _require(
        raw["task_completion_proven"] is False and raw["rights_inherited"] is False,
        "observer boundary",
    )
    source = _object(
        raw["source"],
        {
            "scope",
            "kind",
            "source_id",
            "files_seen",
            "files_examined",
            "files_seen_is_lower_bound",
            "directory_entries_seen",
            "directory_scan_complete",
            "bytes_read",
            "entries_read",
            "complete_observed_read",
            "coverage_of_all_agent_activity",
            "source_authenticated",
            "identity",
            "effect",
        },
        "source",
    )
    _require(source["scope"] == "selected_local_observations", "source scope")
    _token(source["kind"], "source kind")
    if source["source_id"] is not None:
        _token(source["source_id"], "source identifier")
    _require(
        source["source_authenticated"] is False
        and all(
            source[key] == "UNBEKANNT"
            for key in ("identity", "effect", "coverage_of_all_agent_activity")
        ),
        "source boundary",
    )
    # An overflow scan counts one additional name/file, as file_reader.py does.
    _number(source["files_seen"], MAX_ENTRIES + 1, "files seen")
    _number(source["files_examined"], MAX_ENTRIES, "files examined")
    _number(source["directory_entries_seen"], MAX_ENTRIES + 1, "directory entries")
    _number(source["bytes_read"], MAX_REPORT_BYTES + 1, "bytes read")
    total = _number(source["entries_read"], MAX_ENTRIES, "entries read")
    _require(total <= source["files_examined"] <= source["files_seen"], "file counts")
    for key in ("files_seen_is_lower_bound", "directory_scan_complete", "complete_observed_read"):
        _boolean(source[key], key)
    _require(
        source["files_seen_is_lower_bound"] is not source["directory_scan_complete"], "scan state"
    )
    summary = _object(
        raw["summary"],
        {
            "reported_kind_counts",
            "tasks_with_reported_association",
            "claims_without_later_result_in_read_entries",
            "structural_warning_count",
        },
        "summary",
    )
    counts = _counts(summary["reported_kind_counts"], "summary kind counts")
    _require(sum(counts.values()) == total, "entry count total")
    tasks_total = _number(summary["tasks_with_reported_association"], total, "task count")
    pending = _number(
        summary["claims_without_later_result_in_read_entries"], tasks_total, "pending claims"
    )
    warnings_total = _number(
        summary["structural_warning_count"], 2 * MAX_ENTRIES + 10, "warning count"
    )
    _require(source["complete_observed_read"] == (warnings_total == 0), "read completeness")
    display = _object(
        raw["display"], {"limit", "tasks_omitted", "entries_omitted", "warnings_omitted"}, "display"
    )
    limit = _number(display["limit"], MAX_DISPLAY, "display limit", 1)
    tasks = _list(raw["tasks"], limit, "tasks")
    entries = _list(raw["recent_entries"], limit, "recent entries")
    warnings = _list(raw["warnings"], limit, "warnings")
    for key, shown, count in (
        ("tasks_omitted", tasks, tasks_total),
        ("entries_omitted", entries, total),
        ("warnings_omitted", warnings, warnings_total),
    ):
        _number(display[key], 2 * MAX_ENTRIES + 10, key)
        _require(
            len(shown) == min(limit, count) and display[key] == count - len(shown), "display counts"
        )

    references: dict[str, tuple[int, str]] = {}

    def reference(value: Any, *, diagnostic: bool = False) -> dict:
        if diagnostic and type(value) is dict and set(value) == {"entry_id"}:
            _text(value["entry_id"], 255, "diagnostic reference", empty=True)
            return value
        ref = _object(value, {"entry_id", "ordinal", "file_sha256"}, "evidence reference")
        identifier = _token(ref["entry_id"], "evidence identifier")
        ordinal = _number(ref["ordinal"], 2**63 - 1, "evidence ordinal")
        fingerprint = ref["file_sha256"]
        _require(
            type(fingerprint) is str and SHA256.fullmatch(fingerprint) is not None,
            "evidence fingerprint",
        )
        prior = references.setdefault(identifier, (ordinal, fingerprint))
        _require(prior == (ordinal, fingerprint), "inconsistent evidence")
        return ref

    seen_entries: set[str] = set()
    visible_counts: Counter = Counter()
    for entry in entries:
        _object(
            entry,
            {"entry_id", "ordinal", "file_sha256", "reported_kind", "reported_actor_type"},
            "entry",
        )
        reference({key: entry[key] for key in ("entry_id", "ordinal", "file_sha256")})
        _require(entry["entry_id"] not in seen_entries, "duplicate entry")
        seen_entries.add(entry["entry_id"])
        _require(
            type(entry["reported_kind"]) is str and entry["reported_kind"] in KINDS, "entry kind"
        )
        _text(entry["reported_actor_type"], 80, "reported actor")
        visible_counts[entry["reported_kind"]] += 1
    _require(
        all(value <= counts.get(kind, 0) for kind, value in visible_counts.items()),
        "visible kind counts",
    )
    aliases: set[str] = set()
    task_refs: set[str] = set()
    task_counts: Counter = Counter()
    visible_pending = 0
    for task in tasks:
        _object(
            task,
            {
                "task_alias",
                "association_basis",
                "last_reported_kind",
                "order_ambiguous",
                "entry_count",
                "reported_kind_counts",
                "claim_without_later_result",
                "evidence",
            },
            "task",
        )
        alias = task["task_alias"]
        _require(
            type(alias) is str
            and TASK_ALIAS.fullmatch(alias) is not None
            and int(alias[1:]) <= tasks_total
            and alias not in aliases,
            "task alias",
        )
        aliases.add(alias)
        _require(task["association_basis"] == "reported_task_id_only", "task basis")
        ambiguous = _boolean(task["order_ambiguous"], "task ambiguity")
        task_total = _number(task["entry_count"], total, "task entries", 1)
        task_kind_counts = _counts(task["reported_kind_counts"], "task kind counts")
        _require(sum(task_kind_counts.values()) == task_total, "task entry total")
        task_counts.update(task_kind_counts)
        if ambiguous:
            _require(
                task["last_reported_kind"] is None and task["claim_without_later_result"] is None,
                "ambiguous task outcome",
            )
        else:
            _require(
                type(task["last_reported_kind"]) is str
                and task["last_reported_kind"] in task_kind_counts,
                "task last kind",
            )
            _boolean(task["claim_without_later_result"], "task pending claim")
            visible_pending += int(task["claim_without_later_result"])
        refs = _list(task["evidence"], 3, "task evidence")
        _require(len(refs) == min(3, task_total), "task evidence count")
        for ref in refs:
            reference(ref)
            _require(ref["entry_id"] not in task_refs, "duplicate task evidence")
            task_refs.add(ref["entry_id"])
    _require(
        all(value <= counts.get(kind, 0) for kind, value in task_counts.items()), "task kind totals"
    )
    _require(
        visible_pending <= pending <= visible_pending + display["tasks_omitted"],
        "pending claim total",
    )
    for warning in warnings:
        _object(warning, {"code", "evidence"}, "warning")
        _require(
            type(warning["code"]) is str and warning["code"] in DIAGNOSTIC_TEXT, "diagnostic code"
        )
        refs = _list(warning["evidence"], MAX_ENTRIES, "warning evidence")
        warning_refs: set[str] = set()
        for ref in refs:
            reference(ref, diagnostic=True)
            _require(ref["entry_id"] not in warning_refs, "duplicate warning evidence")
            warning_refs.add(ref["entry_id"])
        if warning["code"] == "ordinal_collision":
            _require(
                len(refs) >= 2
                and all("ordinal" in ref for ref in refs)
                and len({ref["ordinal"] for ref in refs}) == 1,
                "ordinal collision evidence",
            )
    _require(len(references) <= total, "evidence entry count")


def _fact(label: str, value: str, localized: bool = False) -> dict:
    return {"labelKey": label, "value": value, "valueKey": localized}


def _node(
    identifier: str,
    kind: str,
    name: str,
    status: str,
    *,
    localized: bool = False,
    group: str = "",
    facts: list | None = None,
    evidence: list | None = None,
) -> dict:
    return {
        "id": identifier,
        "kind": kind,
        "name": name,
        "nameKey": localized,
        "status": status,
        "group": group,
        "facts": facts or [],
        "evidence": evidence or [],
    }


def _edge(
    parent: str, child: str, relation: str, status: str, evidence: list | None = None
) -> dict:
    return {
        "from": parent,
        "to": child,
        "relation": relation,
        "status": status,
        "evidence": evidence or [],
    }


def _document(source: str, demo: bool = False) -> dict:
    return {
        "schema": GRAPH_SCHEMA,
        "source": source,
        "isDemo": demo,
        "nodes": [],
        "edges": [],
        "reportJSON": None,
        "completeRead": None,
        "totalEntries": None,
        "reportedTaskCount": None,
        "reportedWarningCount": None,
        "omitted": 0,
        "warnings": [],
    }


def decode_report(data: bytes | str | dict) -> dict:
    """Project a validated neutral report; this never supplies demonstration data."""
    raw = _load(data)
    validate_report(raw)
    source, summary = raw["source"], raw["summary"]
    doc = _document(source["source_id"] or source["kind"])
    doc.update(
        completeRead=source["complete_observed_read"],
        totalEntries=source["entries_read"],
        reportedTaskCount=summary["tasks_with_reported_association"],
        reportedWarningCount=summary["structural_warning_count"],
        omitted=raw["display"]["entries_omitted"],
        warnings=[w["code"] for w in raw["warnings"]],
        reportJSON=json.dumps(raw, ensure_ascii=True, separators=(",", ":"), sort_keys=True),
    )
    reserved = {"task-" + task["task_alias"] for task in raw["tasks"]}
    reserved.update("warning-" + str(index) for index in range(len(raw["warnings"])))
    # ':' cannot appear in neutral IDs. Preserve native IDs except where its
    # task-/warning- prefixes would otherwise collide with legitimate entries.
    refs = {
        entry["entry_id"]: (
            "entry:" + entry["entry_id"] if entry["entry_id"] in reserved else entry["entry_id"]
        )
        for entry in raw["recent_entries"]
    }
    for entry in raw["recent_entries"]:
        identifier = entry["entry_id"]
        doc["nodes"].append(
            _node(
                refs[identifier],
                "entry",
                "entry." + entry["reported_kind"],
                "reported",
                localized=True,
                facts=[
                    _fact("field.actor", entry["reported_actor_type"]),
                    _fact("field.ordinal", str(entry["ordinal"])),
                    _fact("field.sha256", entry["file_sha256"]),
                    _fact("field.identity", "status.unknown", True),
                    _fact("field.effect", "status.unknown", True),
                ],
                evidence=[identifier],
            )
        )
    for task in raw["tasks"]:
        identifier = "task-" + task["task_alias"]
        doc["nodes"].append(
            _node(
                identifier,
                "task",
                task["task_alias"],
                "reported",
                group=identifier,
                facts=[
                    _fact("field.basis", "basis.task", True),
                    _fact("field.identity", "status.unknown", True),
                ],
            )
        )
        for ref in task["evidence"]:
            if ref["entry_id"] in refs:
                doc["edges"].append(
                    _edge(
                        identifier,
                        refs[ref["entry_id"]],
                        "reportedTask",
                        "reported",
                        [ref["entry_id"]],
                    )
                )
    for index, warning in enumerate(raw["warnings"]):
        identifier = "warning-" + str(index)
        evidence = [ref["entry_id"] for ref in warning["evidence"]]
        facts = [_fact("field.diagnostic", warning["code"])]
        node = _node(
            identifier,
            "evidence",
            "diagnostic." + warning["code"],
            "incomplete",
            localized=True,
            facts=facts,
            evidence=evidence[:MAX_EVIDENCE],
        )
        if len(evidence) > MAX_EVIDENCE:
            node["evidenceOmitted"] = len(evidence) - MAX_EVIDENCE
            facts.append(_fact("field.evidenceOmitted", str(node["evidenceOmitted"])))
        doc["nodes"].append(node)
        for ref in evidence:
            if ref in refs:
                doc["edges"].append(_edge(identifier, refs[ref], "evidence", "incomplete", [ref]))
    validate_graph(doc)
    return doc


def validate_graph(graph: dict) -> None:
    """Validate the native graph vocabulary before serving or traversing it."""
    _object(
        graph,
        {"schema", "source", "isDemo", "nodes", "edges", "omitted", "warnings"},
        "graph",
        {"reportJSON", "completeRead", "totalEntries", "reportedTaskCount", "reportedWarningCount"},
    )
    _require(graph["schema"] == GRAPH_SCHEMA, "graph schema")
    _text(graph["source"], 128, "graph source", empty=True)
    _boolean(graph["isDemo"], "graph demo")
    nodes = _list(graph["nodes"], MAX_NODES, "graph nodes")
    edges = _list(graph["edges"], MAX_EDGES, "graph edges")
    identifiers: set[str] = set()

    def evidence_list(value: Any) -> None:
        for ref in _list(value, MAX_EVIDENCE, "graph evidence"):
            _text(ref, 255, "graph evidence reference", empty=True)

    for node in nodes:
        _object(
            node,
            {"id", "kind", "name", "nameKey", "status", "group", "facts", "evidence"},
            "graph node",
            {"evidenceOmitted"},
        )
        # A collision-prefixed neutral entry may have 128 + len('entry:') chars.
        identifier = _text(node["id"], 134, "graph identifier")
        _require(identifier not in identifiers, "duplicate graph identifier")
        identifiers.add(identifier)
        _require(
            type(node["kind"]) is str
            and node["kind"] in NODE_KINDS
            and type(node["status"]) is str
            and node["status"] in STATUSES,
            "graph vocabulary",
        )
        _text(node["name"], 300, "graph name", empty=True)
        _boolean(node["nameKey"], "graph name localization")
        _text(node["group"], 134, "graph group", empty=True)
        for fact in _list(node["facts"], 32, "graph facts"):
            _object(fact, {"labelKey", "value", "valueKey"}, "graph fact")
            _text(fact["labelKey"], 128, "fact label")
            _text(fact["value"], 2048, "fact value", empty=True)
            _boolean(fact["valueKey"], "fact localization")
        evidence_list(node["evidence"])
        if "evidenceOmitted" in node:
            _number(node["evidenceOmitted"], MAX_ENTRIES, "omitted evidence", 1)
    for edge in edges:
        _object(edge, {"from", "to", "relation", "status", "evidence"}, "graph edge")
        _require(
            type(edge["from"]) is str
            and type(edge["to"]) is str
            and edge["from"] in identifiers
            and edge["to"] in identifiers,
            "graph reference",
        )
        _text(edge["relation"], 80, "graph relation")
        _require(type(edge["status"]) is str and edge["status"] in STATUSES, "edge status")
        evidence_list(edge["evidence"])
    _number(graph["omitted"], MAX_ENTRIES, "omitted entries")
    for warning in _list(graph["warnings"], MAX_DISPLAY, "graph warnings"):
        _text(warning, 128, "graph warning")
    if graph.get("reportJSON") is not None:
        _text(graph["reportJSON"], MAX_REPORT_BYTES, "graph report")
    if graph.get("completeRead") is not None:
        _boolean(graph["completeRead"], "graph completeness")
    for key in ("totalEntries", "reportedTaskCount", "reportedWarningCount"):
        if graph.get(key) is not None:
            _number(graph[key], 2 * MAX_ENTRIES + 10, key)


def neighborhood(graph: dict, identifier: str) -> set[str]:
    """Native undirected connected component, with an unknown anchor empty."""
    validate_graph(graph)
    if identifier not in {node["id"] for node in graph["nodes"]}:
        return set()
    neighbors: dict[str, list[str]] = {}
    for edge in graph["edges"]:
        neighbors.setdefault(edge["from"], []).append(edge["to"])
        neighbors.setdefault(edge["to"], []).append(edge["from"])
    result = {identifier}
    queue = deque([identifier])
    while queue:
        for other in neighbors.get(queue.popleft(), []):
            if other not in result:
                result.add(other)
                queue.append(other)
    return result


def trace(graph: dict, identifier: str) -> set[str]:
    """Port GraphDocument.trace: all ancestors, own non-agent descendants."""
    validate_graph(graph)
    kinds = {node["id"]: node["kind"] for node in graph["nodes"]}
    if identifier not in kinds:
        return set()
    parents: dict[str, list[str]] = {}
    children: dict[str, list[str]] = {}
    for edge in graph["edges"]:
        parents.setdefault(edge["to"], []).append(edge["from"])
        children.setdefault(edge["from"], []).append(edge["to"])
    result = {identifier}
    queue = deque([identifier])
    while queue:
        for other in parents.get(queue.popleft(), []):
            if other not in result:
                result.add(other)
                queue.append(other)
    queue = deque([identifier])
    while queue:
        for other in children.get(queue.popleft(), []):
            if other not in result and kinds[other] != "agent":
                result.add(other)
                queue.append(other)
    return result


def chain_statuses(graph: dict) -> dict[str, str]:
    """Port native demo propagation; every real chain remains unknown."""
    validate_graph(graph)
    if not graph["isDemo"]:
        return {node["id"]: "unknown" for node in graph["nodes"]}
    rank = {
        "verified": 0,
        "observed": 0,
        "reported": 1,
        "unknown": 2,
        "incomplete": 3,
        "contradictory": 4,
    }

    def normalized(status: str) -> str:
        return "verified" if status == "observed" else status

    def worse(a: str, b: str) -> str:
        return a if rank[a] >= rank[b] else b

    result = {node["id"]: normalized(node["status"]) for node in graph["nodes"]}
    incoming = dict.fromkeys(result, 0)
    outgoing: dict[str, list[dict]] = {}
    for edge in graph["edges"]:
        incoming[edge["to"]] += 1
        outgoing.setdefault(edge["from"], []).append(edge)
    queue = deque(identifier for identifier in result if incoming[identifier] == 0)
    visited: set[str] = set()
    while queue:
        identifier = queue.popleft()
        visited.add(identifier)
        for edge in outgoing.get(identifier, []):
            child = edge["to"]
            result[child] = worse(
                worse(result[child], result[identifier]), normalized(edge["status"])
            )
            incoming[child] -= 1
            if incoming[child] == 0:
                queue.append(child)
    for identifier in result.keys() - visited:
        result[identifier] = "contradictory"
    return result


def demo_graph(agents: int = 50) -> dict:
    """Deterministic synthetic DemoData.make port, only called explicitly."""
    _require(type(agents) is int, "demo agent count")
    count = min(max(agents, 2), 1000)
    doc = _document("AA-SAMPLE", True)
    doc["nodes"] = [
        _node(
            "root",
            "agent",
            "demo.coordinator",
            "verified",
            localized=True,
            group="root",
            facts=[_fact("field.identity", "AA-ROOT"), _fact("field.anchor", "demo.testCA", True)],
        ),
        _node(
            "identity-root",
            "identity",
            "demo.testCA",
            "verified",
            localized=True,
            group="root",
            facts=[_fact("field.anchor", "demo.controller", True)],
        ),
        _node(
            "authority-root",
            "authority",
            "demo.authority",
            "verified",
            localized=True,
            group="root",
            facts=[
                _fact("field.issuer", "demo.controller", True),
                _fact("field.scope", "demo.scope", True),
            ],
        ),
    ]
    doc["edges"] = [
        _edge("identity-root", "root", "identity", "verified"),
        _edge("authority-root", "root", "authority", "verified"),
    ]
    for i in range(1, count):
        identifier, branch = f"agent-{i:03d}", f"branch-{(i - 1) // 10}"
        status = "incomplete" if i % 13 == 0 else "unknown" if i % 17 == 0 else "verified"
        parent = "root" if i <= 5 else f"agent-{(i - 1) // 2:03d}"
        doc["nodes"].append(
            _node(
                identifier,
                "agent",
                f"AA-{i:03d}",
                status,
                group=branch,
                facts=[
                    _fact("field.identity", identifier),
                    _fact("field.anchor", "demo.testCA", True),
                    _fact("field.authority", "authority-root"),
                    _fact("field.provider", "status.unknown", True),
                ],
                evidence=[f"E-{i}-ID"],
            )
        )
        doc["edges"].append(_edge(parent, identifier, "delegates", status, [f"E-{i}-D"]))
        doc["nodes"].extend(
            [
                _node(
                    f"process-{i}",
                    "process",
                    "python3.12",
                    "observed" if status == "verified" else "unknown",
                    group=branch,
                    facts=[
                        _fact("field.pid", str(8000 + i)),
                        _fact("field.instance", f"SAMPLE-{i}"),
                        _fact("field.start", "demo.synthetic", True),
                    ],
                    evidence=[f"E-{i}-P"],
                ),
                _node(
                    f"action-{i}",
                    "action",
                    "demo.write",
                    "observed" if status == "verified" else "reported",
                    localized=True,
                    group=branch,
                    facts=[
                        _fact("field.object", f"SAMPLE-OBJ-{i}"),
                        _fact("field.effect", "boundary.durable", True),
                    ],
                    evidence=[f"E-{i}-W"],
                ),
            ]
        )
        doc["edges"].extend(
            [
                _edge(identifier, f"process-{i}", "bound", status),
                _edge(f"process-{i}", f"action-{i}", "caused", status),
            ]
        )
    validate_graph(doc)
    return doc


def warning_assessments(graph: dict) -> dict[str, dict]:
    """Port UIWarningDemo separately from graph and report semantics."""
    validate_graph(graph)
    if not graph["isDemo"]:
        return {}
    identifiers = {node["id"] for node in graph["nodes"]}
    result = {}
    for index, identifier in enumerate(["root"] + [f"agent-{i:03d}" for i in range(1, 6)]):
        if identifier not in identifiers:
            continue
        severity = ["information", "attention", "warning", "critical", None, None][index]
        performed = index != 4
        result[identifier] = {
            "nodeID": identifier,
            "relationship": "root → agent-002" if index == 2 else None,
            "severity": severity,
            "dataState": "current" if performed else "missing",
            "checkPerformed": performed,
            "reasonKey": f"warning.demoReason.{index}",
            "timestamp": "2026-10-12T12:00:00Z",
            "sourceKey": "warning.syntheticSource",
            "evidence": ["UI-DEMO-002"] if index == 2 else [],
            "isSynthetic": True,
            "isAssessable": performed,
            "outcome": (severity or "checkedClear") if performed else "notAssessable",
        }
    return result
