"""Browser projection contract, using only synthetic observer snapshots."""

from __future__ import annotations

import copy
import hashlib
import json

import pytest

from agent_authority.browser_model import (
    MAX_REPORT_BYTES,
    ModelError,
    chain_statuses,
    decode_report,
    demo_graph,
    neighborhood,
    trace,
    validate_graph,
    validate_report,
    warning_assessments,
)
from agent_authority.observations import Diagnostic, Entry, Snapshot, Source
from agent_authority.json_source import read_observations
from agent_authority.report import build_report


def entry(
    identifier="entry-1", ordinal=1, kind="result", task="synthetic-task", actor="test-client"
):
    return Entry(
        identifier, ordinal, kind, actor, task, hashlib.sha256(identifier.encode()).hexdigest()
    )


def report(entries=None, diagnostics=(), limit=100):
    entries = (entry(),) if entries is None else tuple(entries)
    return build_report(
        Snapshot(
            Source("json-directory", "synthetic-source"),
            entries,
            tuple(diagnostics),
            len(entries),
            len(entries),
            directory_entries_seen=len(entries),
        ),
        limit,
    )


def test_projection_matches_native_neutral_mapping_without_claiming_identity_or_effect():
    raw = report([entry("one", 1, "claimed"), entry("two", 2, "result")])
    graph = decode_report(json.dumps(raw).encode())
    assert graph["isDemo"] is False
    assert graph["source"] == "synthetic-source"
    assert graph["completeRead"] is True
    assert graph["totalEntries"] == 2
    assert graph["reportedTaskCount"] == 1
    assert graph["reportedWarningCount"] == 0
    assert graph["omitted"] == 0
    nodes = {node["id"]: node for node in graph["nodes"]}
    assert nodes["two"]["kind"] == "entry"
    assert nodes["two"]["name"] == "entry.result"
    assert nodes["two"]["status"] == "reported"
    facts = {fact["labelKey"]: fact["value"] for fact in nodes["two"]["facts"]}
    assert facts["field.identity"] == facts["field.effect"] == "status.unknown"
    assert graph["edges"] == [
        {
            "from": "task-A1",
            "to": "one",
            "relation": "reportedTask",
            "status": "reported",
            "evidence": ["one"],
        },
        {
            "from": "task-A1",
            "to": "two",
            "relation": "reportedTask",
            "status": "reported",
            "evidence": ["two"],
        },
    ]
    assert set(chain_statuses(graph).values()) == {"unknown"}
    assert warning_assessments(graph) == {}
    assert json.loads(graph["reportJSON"]) == raw


def test_input_is_detached_and_never_implicitly_demo():
    raw = report()
    graph = decode_report(raw)
    raw["recent_entries"][0]["reported_actor_type"] = "changed"
    assert "changed" not in graph["reportJSON"]
    assert decode_report(report([]))["nodes"] == []
    with pytest.raises(ModelError):
        decode_report({})


def test_incomplete_empty_and_display_limited_states_preserve_provenance():
    graph = decode_report(report([], [Diagnostic("source_unavailable")]))
    assert graph["completeRead"] is False
    assert graph["totalEntries"] == 0
    assert graph["warnings"] == ["source_unavailable"]
    assert graph["nodes"][0]["status"] == "incomplete"
    graph = decode_report(report([entry(f"e-{i}", i) for i in range(10)], limit=2))
    assert graph["omitted"] == 8
    assert graph["totalEntries"] == 10
    assert {node["id"] for node in graph["nodes"]} == {"e-9", "e-8", "task-A1"}
    assert all(edge["to"] in {"e-9", "e-8"} for edge in graph["edges"])


def test_reserved_entry_ids_cannot_overwrite_task_or_warning_nodes():
    graph = decode_report(report([entry("task-A1", 1), entry("warning-0", 1)]))
    nodes = {node["id"]: node for node in graph["nodes"]}
    assert nodes["task-A1"]["kind"] == "task"
    assert nodes["warning-0"]["kind"] == "evidence"
    assert nodes["entry:task-A1"]["evidence"] == ["task-A1"]
    assert nodes["entry:warning-0"]["evidence"] == ["warning-0"]
    assert {edge["to"] for edge in graph["edges"]} == {"entry:task-A1", "entry:warning-0"}


def test_ordinal_collision_large_evidence_is_explicitly_bounded_in_graph_only():
    raw = report([entry(f"entry-{i}", 4) for i in range(100)])
    graph = decode_report(raw)
    warning = next(node for node in graph["nodes"] if node["kind"] == "evidence")
    assert len(warning["evidence"]) == 64
    assert warning["evidenceOmitted"] == 36
    assert {fact["labelKey"]: fact["value"] for fact in warning["facts"]}[
        "field.evidenceOmitted"
    ] == "36"
    assert len([edge for edge in graph["edges"] if edge["relation"] == "evidence"]) == 100
    assert len(json.loads(graph["reportJSON"])["warnings"][0]["evidence"]) == 100
    assert raw["tasks"][0]["last_reported_kind"] is None


def test_foreign_text_is_data_with_no_markup_interpretation_or_path_resolution():
    actor = '<img src=x onerror="alert(1)">'
    diagnostic = "../../<script>alert(1)</script>"
    graph = decode_report(
        report([entry(actor=actor)], [Diagnostic("invalid_filename", diagnostic)])
    )
    assert actor in [fact["value"] for node in graph["nodes"] for fact in node["facts"]]
    assert graph["nodes"][-1]["evidence"] == [diagnostic]
    assert json.loads(graph["reportJSON"])["warnings"][0]["evidence"][0]["entry_id"] == diagnostic


def test_existing_file_adapter_and_engine_feed_projection_without_semantic_replacement(tmp_path):
    record = {
        "schema_version": "agent-authority-observation-v1",
        "id": "synthetic-event",
        "source_id": "synthetic-source",
        "ordinal": 3,
        "kind": "result",
        "reported_actor_type": "test-client",
        "task_key": "synthetic-task",
        "metadata": {"identity": "forged", "effect": "executed"},
    }
    (tmp_path / "synthetic-event.json").write_text(json.dumps(record))
    (tmp_path / "<foreign>.json").write_text("{}")
    raw = build_report(read_observations(tmp_path, "synthetic-source"), 20)
    graph = decode_report(raw)
    assert graph["totalEntries"] == 1 and graph["completeRead"] is False
    assert graph["warnings"] == ["invalid_filename"]
    assert "forged" not in graph["reportJSON"]
    assert "executed" not in graph["reportJSON"]
    assert graph["nodes"][-1]["evidence"] == ["<foreign>"]


@pytest.mark.parametrize(
    "path,value",
    [
        (("role",), "executor"),
        (("schema_version",), "agent-authority-macos-es-v1"),
        (("source", "source_authenticated"), True),
        (("source", "identity"), "verified"),
        (("source", "effect"), "verified"),
        (("source", "coverage_of_all_agent_activity"), "complete"),
        (("task_completion_proven",), True),
        (("rights_inherited",), True),
        (("source", "entries_read"), True),
        (("source", "files_examined"), -1),
        (("source", "bytes_read"), MAX_REPORT_BYTES + 2),
        (("source", "source_id"), "../../source"),
        (("summary", "structural_warning_count"), 1),
        (("display", "entries_omitted"), 2),
        (("display", "limit"), 101),
        (("recent_entries", 0, "ordinal"), True),
        (("recent_entries", 0, "ordinal"), 2**63),
        (("recent_entries", 0, "file_sha256"), "Z" * 64),
        (("recent_entries", 0, "reported_actor_type"), " " * 4),
        (("recent_entries", 0, "reported_actor_type"), "a" * 81),
        (("recent_entries", 0, "reported_kind"), "executed"),
        (("recent_entries", 0, "reported_kind"), []),
        (("tasks", 0, "association_basis"), "verified_identity"),
        (("tasks", 0, "last_reported_kind"), {}),
        (("tasks", 0, "task_alias"), "A0"),
        (("tasks", 0, "entry_count"), 2),
        (("tasks", 0, "claim_without_later_result"), True),
        (("tasks", 0, "evidence", 0, "file_sha256"), "f" * 64),
    ],
)
def test_full_contract_rejects_boundary_type_bounds_and_consistency_changes(path, value):
    raw = report()
    target = raw
    for key in path[:-1]:
        target = target[key]
    target[path[-1]] = value
    with pytest.raises(ModelError):
        decode_report(raw)


@pytest.mark.parametrize("section", [None, "source", "summary", "display"])
def test_unknown_fields_are_not_carried_into_raw_evidence(section):
    raw = report()
    (raw if section is None else raw[section])["private_content"] = "SYNTHETIC_SECRET"
    with pytest.raises(ModelError):
        decode_report(raw)


def test_missing_fields_invalid_json_duplicates_and_oversize_are_rejected():
    for section, key in (
        (None, "tasks"),
        ("source", "identity"),
        ("summary", "reported_kind_counts"),
        ("display", "limit"),
    ):
        raw = report()
        del (raw if section is None else raw[section])[key]
        with pytest.raises(ModelError):
            decode_report(raw)
    for encoded in (
        b"{",
        b'{"role":"observer_only","role":"observer_only"}',
        b'{"x": NaN}',
        b"[1]",
        b"\xff",
        b" " * (MAX_REPORT_BYTES + 1),
        (b"[" * 2000) + (b"]" * 2000),
    ):
        with pytest.raises(ModelError):
            decode_report(encoded)


def test_duplicate_entries_and_conflicting_reference_fingerprints_fail():
    raw = report([entry("one", 1), entry("two", 2)])
    raw["recent_entries"][1] = copy.deepcopy(raw["recent_entries"][0])
    with pytest.raises(ModelError):
        decode_report(raw)
    raw = report([entry("one", 1), entry("two", 2)])
    raw["tasks"][0]["evidence"][0]["ordinal"] = 3
    with pytest.raises(ModelError):
        decode_report(raw)


def test_native_demo_graph_is_deterministic_separate_and_bounded():
    graph = demo_graph()
    assert graph == demo_graph(50)
    assert graph["source"] == "AA-SAMPLE" and graph["isDemo"] is True
    assert graph["reportJSON"] is None
    assert len(graph["nodes"]) == 3 + 49 * 3
    assert len(graph["edges"]) == 2 + 49 * 3
    assert len(demo_graph(1001)["nodes"]) == 3000
    assert len(demo_graph(-1)["nodes"]) == 6
    with pytest.raises(ModelError):
        demo_graph(True)
    assert chain_statuses(graph)["agent-013"] == "incomplete"
    assert chain_statuses(graph)["action-27"] == "incomplete"  # inherited through parent 13
    assert chain_statuses(graph)["action-1"] == "verified"
    assert graph["nodes"][3]["evidence"] == ["E-1-ID"]


def test_chain_trace_preserves_ancestors_but_does_not_pull_sibling_agents():
    graph = demo_graph(50)
    assert trace(graph, "agent-001") == {
        "agent-001",
        "root",
        "identity-root",
        "authority-root",
        "process-1",
        "action-1",
    }
    assert trace(graph, "action-1") == {
        "agent-001",
        "root",
        "identity-root",
        "authority-root",
        "process-1",
        "action-1",
    }
    assert len(neighborhood(graph, "agent-001")) == len(graph["nodes"])
    assert trace(graph, "missing") == neighborhood(graph, "missing") == set()


def test_chain_cycles_terminate_and_remain_selectable_but_contradictory():
    graph = demo_graph(4)
    graph["edges"].append(
        {
            "from": "agent-001",
            "to": "root",
            "relation": "delegates",
            "status": "verified",
            "evidence": [],
        }
    )
    assert chain_statuses(graph)["root"] == "contradictory"
    assert chain_statuses(graph)["action-1"] == "contradictory"
    assert "agent-001" in trace(graph, "root")


def test_warning_assessability_and_severity_are_only_synthetic_demo_vocabulary():
    warnings = warning_assessments(demo_graph())
    assert [warnings[key]["outcome"] for key in warnings] == [
        "information",
        "attention",
        "warning",
        "critical",
        "notAssessable",
        "checkedClear",
    ]
    assert all(item["isSynthetic"] for item in warnings.values())
    assert warnings["agent-002"]["relationship"] == "root → agent-002"
    assert warnings["agent-004"]["isAssessable"] is False
    graph = demo_graph()
    graph["isDemo"] = False
    assert warning_assessments(graph) == {}
    assert set(chain_statuses(graph).values()) == {"unknown"}


def test_graph_validation_rejects_dangling_edges_duplicate_nodes_and_unbounded_facts():
    for mutation in (
        lambda graph: graph["edges"][0].update(to="missing"),
        lambda graph: graph["nodes"].append(copy.deepcopy(graph["nodes"][0])),
        lambda graph: graph["nodes"][0].update(facts=[{}] * 33),
        lambda graph: graph["nodes"][0].update(evidence=["E"] * 65),
        lambda graph: graph["nodes"][0].update(kind=[]),
        lambda graph: graph["edges"][0].update(status={}),
        lambda graph: graph["nodes"][0]["facts"][0].update(value="x" * 2049),
    ):
        graph = demo_graph(2)
        mutation(graph)
        with pytest.raises(ModelError):
            validate_graph(graph)


def test_scan_overflow_counts_and_invalid_source_diagnostics_are_valid_engine_outputs():
    raw = report([])
    raw["source"].update(
        files_seen=10001,
        directory_entries_seen=10001,
        directory_scan_complete=False,
        files_seen_is_lower_bound=True,
        complete_observed_read=False,
    )
    raw["summary"]["structural_warning_count"] = 1
    raw["warnings"] = [{"code": "directory_limit", "evidence": []}]
    validate_report(raw)
    raw = report([], [Diagnostic("invalid_source_id")])
    raw["source"]["source_id"] = None
    assert decode_report(raw)["source"] == "json-directory"


def test_private_adapter_graph_accepts_its_bounded_contract_text():
    from agent_authority.browser_adapter import adapt_private_report, synthetic_private_response

    raw = synthetic_private_response("a" * 32)
    raw["report"]["body"]["uncertainties"] = ["x" * 2048]
    projected = adapt_private_report(raw, "synthetic-private-alice", "a" * 32)
    validate_graph(projected["graph"])
    assert set(chain_statuses(projected["graph"]).values()) == {"unknown"}
