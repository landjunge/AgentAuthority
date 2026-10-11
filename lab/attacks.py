"""Builders for frozen attack sequences. Assertions live in tests/."""

from __future__ import annotations

from lab.models import ActionRequest


def budget_split(workflow_id: str) -> list[ActionRequest]:
    reqs: list[ActionRequest] = []
    for i in range(60):
        reqs.append(ActionRequest("A", "file.read", f"a/{i}", {}, workflow_id))
    for i in range(41):
        reqs.append(ActionRequest("B", "file.read", f"b/{i}", {}, workflow_id))
    return reqs


def file_limit_split(workflow_id: str) -> list[ActionRequest]:
    return [
        ActionRequest("A" if i < 6 else "B", "file.write", f"src/f{i}.txt", {}, workflow_id)
        for i in range(11)
    ]


def slow_drift(workflow_id: str, n: int = 101) -> list[ActionRequest]:
    return [ActionRequest("A", "file.read", f"drift/{i}", {}, workflow_id) for i in range(n)]
