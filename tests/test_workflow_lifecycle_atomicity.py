"""Deterministic registry races for Lab.submit / finish.

docs/PHASE1-WORKFLOW-LIFECYCLE-ATOMICITY.md.

No sleeps. Events/Barriers with timeouts: a hang fails the test instead of
blocking CI. Every patched hook is counted so a refactor cannot go green by
skipping the seam.
"""

from __future__ import annotations

import threading

from lab.models import CAPACITY_EXCEEDED, ActionRequest
from lab.validator import Lab

HOOK_TIMEOUT = 5.0
JOIN_TIMEOUT = 10.0


def _read(lab: Lab, workflow_id: str, path: str = "src/app.py"):
    return lab.submit(ActionRequest("agent-a", "file.read", path, {}, workflow_id))


def _join(thread: threading.Thread) -> None:
    thread.join(timeout=JOIN_TIMEOUT)
    assert not thread.is_alive(), f"{thread.name} hung"


# ── Defect A: capacity check and reservation are not atomic ──────────────────


def test_capacity_check_and_reservation_are_atomic():
    """Two new ids at max_tracked=1: at most one ALLOW, tracked never exceeds 1.

    The seam lives inside `_admit`, after the first capacity look and before
    the insert — not in `submit` before `_admit`. A refactor that splits
    check and reserve inside `_admit` is then forced to lose, instead of
    going green because the window moved past the hook. `seam_hits == 2`
    still guards a refactor that stops calling the hook at all.
    """
    lab = Lab(max_tracked=1)
    seam_hits: list[str] = []
    barrier = threading.Barrier(2)
    results: list = []
    errors: list[BaseException] = []

    def seam(workflow_id: str) -> None:
        seam_hits.append(workflow_id)
        barrier.wait(timeout=HOOK_TIMEOUT)

    lab._capacity_seam = seam  # type: ignore[method-assign]

    def go(wid: str) -> None:
        try:
            results.append(_read(lab, wid))
        except BaseException as exc:  # noqa: BLE001 — surface in parent thread
            errors.append(exc)

    t1 = threading.Thread(target=go, args=("n1",), name="admit-n1")
    t2 = threading.Thread(target=go, args=("n2",), name="admit-n2")
    t1.start()
    t2.start()
    _join(t1)
    _join(t2)

    assert errors == []
    assert len(seam_hits) == 2, seam_hits
    assert len(results) == 2
    allows = [d for d in results if d.allow]
    denys = [d for d in results if not d.allow]
    assert lab.tracked_workflows() <= 1
    assert len(lab._states) <= 1
    assert len(lab._locks) <= 1
    assert set(lab._states) == set(lab._locks)
    assert len(allows) == 1, results
    assert len(denys) == 1
    assert denys[0].deny_reason == CAPACITY_EXCEEDED
    assert denys[0].violated_invariants == [CAPACITY_EXCEEDED]


# ── Defect B: finish() invalidates a lock a submit() is waiting to acquire ──


def test_finish_does_not_orphan_state_on_stale_lock_reference():
    """submit() holds a lock *reference* and has not acquired it yet.

    finish() then removes that lock from the registry. The waiting submit()
    must not create state under the stale lock (orphaned state, later a
    second lock for the same id). Forced with events, not scheduling luck.
    """
    lab = Lab()
    wid = "wf-stale"
    assert _read(lab, wid).allow

    got_ref = threading.Event()
    finish_done = threading.Event()
    after_ref_hits: list[str] = []
    finish_hold_hits: list[str] = []
    stale_lock: dict[str, threading.Lock] = {}
    errors: list[BaseException] = []
    result: list = []

    def after_ref(workflow_id: str, lock: threading.Lock) -> None:
        if workflow_id != wid:
            return
        after_ref_hits.append(workflow_id)
        stale_lock["lock"] = lock
        got_ref.set()
        assert finish_done.wait(timeout=HOOK_TIMEOUT), (
            "finish() never completed while submit held only a ref"
        )

    def finish_hold(workflow_id: str) -> None:
        if workflow_id != wid:
            return
        finish_hold_hits.append(workflow_id)

    lab._after_lock_ref = after_ref  # type: ignore[method-assign]
    lab._finish_holding_after_state_removed = finish_hold  # type: ignore[method-assign]

    def go_submit() -> None:
        try:
            result.append(_read(lab, wid, path="src/after-finish.py"))
        except BaseException as exc:  # noqa: BLE001
            errors.append(exc)

    t_submit = threading.Thread(target=go_submit, name="stale-submit")
    t_submit.start()
    assert got_ref.wait(timeout=HOOK_TIMEOUT), "_after_lock_ref was not reached"
    assert after_ref_hits == [wid]

    existed = lab.finish(wid)
    assert existed is True
    assert finish_hold_hits == [wid], "_finish_holding_after_state_removed was not reached"
    finish_done.set()
    _join(t_submit)

    assert errors == []
    assert len(result) == 1
    assert result[0].allow is True
    # Live registry: lock and state are one identity. No orphan, no second lock.
    assert set(lab._states) == set(lab._locks)
    assert lab.tracked_workflows() == 1
    assert wid in lab._locks
    assert wid in lab._states
    # The lock submit() waited on must not be a live second identity.
    live_lock = lab._locks[wid]
    assert live_lock is not None
    st = lab.state(wid)
    assert st.action_count == 1
    assert lab.finish(wid) is True
    assert lab.tracked_workflows() == 0
    assert lab._locks == {}
    assert lab._states == {}


def test_distinct_workflows_proceed_in_parallel():
    """Table lock must not be held for the whole of submit.

    Two different ids barrier inside the per-workflow critical section. If
    admission still held `_table_lock`, the second thread could not enter
    and the barrier would time out.
    """
    lab = Lab()
    hits: list[str] = []
    barrier = threading.Barrier(2)
    results: list = []
    errors: list[BaseException] = []

    def inside(workflow_id: str) -> None:
        hits.append(workflow_id)
        barrier.wait(timeout=HOOK_TIMEOUT)

    lab._inside_submit_locked = inside  # type: ignore[method-assign]

    def go(wid: str) -> None:
        try:
            results.append(_read(lab, wid))
        except BaseException as exc:  # noqa: BLE001
            errors.append(exc)

    t1 = threading.Thread(target=go, args=("a",), name="par-a")
    t2 = threading.Thread(target=go, args=("b",), name="par-b")
    t1.start()
    t2.start()
    _join(t1)
    _join(t2)

    assert errors == []
    assert sorted(hits) == ["a", "b"]
    assert len(results) == 2
    assert all(d.allow for d in results)
    assert lab.tracked_workflows() == 2


def test_capacity_exceeded_creates_no_state_lock_or_provenance():
    lab = Lab(max_tracked=1)
    assert _read(lab, "kept").allow
    denied = _read(lab, "overflow")
    assert denied.allow is False
    assert denied.deny_reason == CAPACITY_EXCEEDED
    assert lab.tracked_workflows() == 1
    assert "overflow" not in lab._states
    assert "overflow" not in lab._locks
    assert lab.state("overflow").action_count == 0
    assert lab.state("overflow").provenance == []
    assert lab.state("kept").action_count == 1


def test_existing_workflow_still_runs_at_capacity():
    lab = Lab(max_tracked=1)
    assert _read(lab, "live").allow
    assert _read(lab, "other").allow is False
    assert _read(lab, "live", path="src/two.py").allow
    assert lab.state("live").action_count == 2
    assert lab.tracked_workflows() == 1
