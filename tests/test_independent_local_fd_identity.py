"""Linux-only tests for the additive independent SCM_RIGHTS verifier."""
from __future__ import annotations

import array
import copy
import fcntl
import json
import os
from pathlib import Path
import socket
import subprocess
import sys
from types import SimpleNamespace

import pytest

from probes import independent_local_fd_identity as verifier


pytestmark = pytest.mark.skipif(sys.platform != "linux", reason="Linux SCM_RIGHTS contract")


def _open_pair(folder: Path, same: bool) -> tuple[list[int], list[tuple[int, int]]]:
    folder.mkdir()
    first_path = folder / "first"
    first = os.open(first_path, os.O_RDWR | os.O_CREAT | os.O_EXCL, 0o600)
    if same:
        second = os.open(first_path, os.O_RDWR)
    else:
        second = os.open(folder / "second", os.O_RDWR | os.O_CREAT | os.O_EXCL, 0o600)
    handles = [first, second]
    pairs = [(os.fstat(fd).st_dev, os.fstat(fd).st_ino) for fd in handles]
    assert handles[0] != handles[1]
    assert (pairs[0] == pairs[1]) is same
    return handles, pairs


def _close_all(handles: list[int]) -> None:
    for fd in handles:
        try:
            os.close(fd)
        except OSError:
            pass


def _packet(pairs: list[tuple[int, int]], *, omit_regular: bool = False) -> list[dict]:
    refs = [
        {"st_dev": pair[0], "st_ino": pair[1], "regular_file": True}
        for pair in pairs
    ]
    if omit_regular:
        del refs[1]["regular_file"]
    return [
        {
            "run": 1,
            "kind": "live_local_file_refs",
            "value": {
                "scope": {
                    "os": "Linux",
                    "filesystem": "tmpfs",
                    "same_collection_process": True,
                    "live_handle_overlap_confirmed": True,
                },
                "references": refs,
            },
        }
    ]


def _case_profile(number: int, actual: list[tuple[int, int]]) -> tuple[list[dict], dict]:
    if number in (1, 2, 5, 6):
        offered = list(actual)
    elif number == 3:
        offered = [actual[0], actual[0]]
    elif number == 4:
        offered = [actual[0], (actual[0][0], actual[0][1] + 1)]
    elif number == 7:
        offered = [(actual[0][0], actual[0][1] + 1_000_000)] * 2
    else:
        raise AssertionError("case outside C1-C7")
    answers = {
        1: "DIESELBE",
        2: "VERSCHIEDEN",
        3: "DIESELBE",
        4: "VERSCHIEDEN",
        5: "UNBEKANNT",
        6: "UNBEKANNT",
        7: "DIESELBE",
    }
    return _packet(offered, omit_regular=number == 6), {
        "A": answers[number],
        "wrapper_profile": "controlled-source-values",
    }


@pytest.mark.parametrize(
    "number,same,expected",
    [
        (1, True, "DIESELBE"),
        (2, False, "VERSCHIEDEN"),
        (3, False, "UNBEKANNT"),
        (4, True, "UNBEKANNT"),
        (5, True, "UNBEKANNT"),
        (6, True, "UNBEKANNT"),
        (7, False, "UNBEKANNT"),
    ],
)
def test_fresh_c1_c7_matrix_uses_fd_channel_not_archived_truth(
    tmp_path: Path, number: int, same: bool, expected: str
):
    handles, actual = _open_pair(tmp_path / f"C{number}", same)
    try:
        packet, observer = _case_profile(number, actual)
        result = verifier.verify_current_fd_identity(
            packet, 1, observer, handles=handles
        )
        assert result["A"] == expected
        assert result["source_authenticated"] is False
        assert result["positive_identity_authorized"] is (number in (1, 2))
        assert result["fd_set_verified"] is (number in (1, 2, 3, 4, 7))
    finally:
        _close_all(handles)


def test_clean_exec_process_ignores_all_five_source_monkeypatches(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
):
    handles, actual = _open_pair(tmp_path / "separate", True)
    packet = _packet(actual)
    calls = []

    def fake(name: str, value: object):
        def replacement(*args: object, **kwargs: object) -> object:
            calls.append((name, args, kwargs))
            return value

        return replacement

    monkeypatch.setattr(fcntl, "fcntl", fake("fcntl", 0))
    monkeypatch.setattr(os, "fstat", fake("fstat", SimpleNamespace(
        st_mode=0, st_dev=999, st_ino=999
    )))
    monkeypatch.setattr(os, "uname", fake("uname", SimpleNamespace(sysname="attacker")))
    monkeypatch.setattr(subprocess, "run", fake("run", SimpleNamespace(
        returncode=0, stdout="attacker"
    )))
    monkeypatch.setattr(os, "stat", fake("stat", SimpleNamespace(st_dev=999)))
    try:
        result = verifier.verify_current_fd_identity(
            packet, 1, {"A": "DIESELBE"}, handles=handles
        )
        assert result["A"] == "DIESELBE"
        evidence = result["verifier"]
        assert evidence["pid"] != os.getpid()
        assert evidence["ppid"] == os.getpid()
        assert evidence["parent_pid"] == os.getpid()
        assert evidence["syscall_origin"] == "clean-exec-verifier"
        assert evidence["executable"] == sys.executable
        assert evidence["process_reaped"] is True
        assert [row["pair_before"] for row in evidence["measurements"]] == [
            list(actual[0]),
            list(actual[1]),
        ]
        assert calls == []
    finally:
        _close_all(handles)


def test_invalid_descriptor_arguments_fail_closed_and_child_is_reaped():
    packet = _packet([(1, 10), (1, 11)])
    result = verifier.verify_current_fd_identity(
        packet,
        1,
        {"A": "VERSCHIEDEN"},
        handles=[2**30, 2**30 + 1],
    )
    assert result["A"] == "UNBEKANNT"
    assert result["B"] == "verifier_transport_failed"
    assert result["verifier"]["process_reaped"] is True
    pid = result["verifier"].get("pid")
    if pid is not None:
        assert not Path(f"/proc/{pid}").exists()


def test_non_regular_received_fds_fail_closed():
    read_fd, write_fd = os.pipe()
    native = [os.fstat(read_fd), os.fstat(write_fd)]
    packet = _packet([(row.st_dev, row.st_ino) for row in native])
    try:
        result = verifier.verify_current_fd_identity(
            packet, 1, {"A": "DIESELBE"}, handles=[read_fd, write_fd]
        )
        assert result["A"] == "UNBEKANNT"
        assert result["B"] == "verifier_response_rejected"
    finally:
        _close_all([read_fd, write_fd])


def test_missing_verifier_fails_closed(tmp_path: Path):
    handles, actual = _open_pair(tmp_path / "missing", True)
    try:
        result = verifier._verify_current_fd_identity(
            _packet(actual),
            1,
            {"A": "DIESELBE"},
            handles=handles,
            timeout=3.0,
            argv_factory=lambda fd: ["/definitely/missing/aa-fd-verifier"],
        )
        assert result["A"] == "UNBEKANNT"
        assert result["B"] == "verifier_transport_failed"
        assert result["verifier"]["transport_status"] == "error"
    finally:
        _close_all(handles)


def test_verifier_process_failure_is_not_a_positive_answer(tmp_path: Path):
    handles, actual = _open_pair(tmp_path / "process-failure", False)
    try:
        result = verifier._verify_current_fd_identity(
            _packet(actual),
            1,
            {"A": "VERSCHIEDEN"},
            handles=handles,
            timeout=3.0,
            argv_factory=lambda fd: [
                sys.executable,
                "-I",
                "-S",
                "-c",
                "raise SystemExit(7)",
            ],
        )
        assert result["A"] == "UNBEKANNT"
        assert result["B"] == "verifier_transport_failed"
        assert result["verifier"]["transport_status"] == "error"
        assert result["verifier"]["process_reaped"] is True
    finally:
        _close_all(handles)


def test_timeout_fails_closed_kills_child_and_preserves_original_fds(tmp_path: Path):
    handles, actual = _open_pair(tmp_path / "timeout", False)
    try:
        result = verifier._verify_current_fd_identity(
            _packet(actual),
            1,
            {"A": "VERSCHIEDEN"},
            handles=handles,
            timeout=0.15,
            argv_factory=lambda fd: [
                sys.executable,
                "-I",
                "-S",
                "-c",
                "import time; time.sleep(60)",
            ],
        )
        assert result["A"] == "UNBEKANNT"
        assert result["verifier"]["transport_status"] == "timeout"
        assert result["verifier"]["process_reaped"] is True
        assert not Path(f"/proc/{result['verifier']['pid']}").exists()
        assert all(fcntl.fcntl(fd, fcntl.F_GETFD) >= 0 for fd in handles)
    finally:
        _close_all(handles)


def _write_rogue_verifier(path: Path) -> None:
    path.write_text(
        "import json, os, socket, sys\n"
        "s=socket.socket(fileno=int(sys.argv[1]))\n"
        "request=json.loads(s.recvmsg(65536, socket.CMSG_SPACE(32))[0])\n"
        "response={'protocol':request['protocol'],'request_id':request['request_id'],"
        "'status':'OK','verdict':'GLEICH','pid':os.getpid(),'ppid':os.getppid(),"
        "'executable':sys.executable,'syscall_origin':'clean-exec-verifier',"
        "'measurements':[]}\n"
        "s.sendall(json.dumps(response).encode('ascii'))\n"
        "s.close()\n",
        encoding="utf-8",
    )


def test_response_without_nonce_handshake_is_rejected(tmp_path: Path):
    handles, actual = _open_pair(tmp_path / "bad-response", True)
    rogue = tmp_path / "rogue.py"
    _write_rogue_verifier(rogue)
    try:
        result = verifier._verify_current_fd_identity(
            _packet(actual),
            1,
            {"A": "DIESELBE"},
            handles=handles,
            timeout=3.0,
            argv_factory=lambda fd: [
                sys.executable,
                "-I",
                "-S",
                str(rogue),
                str(fd),
            ],
        )
        assert result["A"] == "UNBEKANNT"
        assert result["B"] == "verifier_response_rejected"
        assert result["verifier"]["validation"] == "invalid_response_shape"
    finally:
        _close_all(handles)


def test_bound_response_mutations_are_rejected(tmp_path: Path):
    handles, actual = _open_pair(tmp_path / "mutations", False)
    nonce = "12" * 32
    try:
        exchange = verifier._exchange(handles, 3.0, nonce, verifier._default_argv)
        assert exchange["transport_status"] == "ok"
        raw = exchange["raw_response"]
        mutations = []
        wrong_nonce = copy.deepcopy(raw)
        wrong_nonce["nonce"] = "34" * 32
        mutations.append(wrong_nonce)
        missing_binding = copy.deepcopy(raw)
        del missing_binding["request_id"]
        mutations.append(missing_binding)
        false_verdict = copy.deepcopy(raw)
        false_verdict["verdict"] = "GLEICH"
        mutations.append(false_verdict)
        changed_measurement = copy.deepcopy(raw)
        changed_measurement["measurements"][1]["pair_after"][1] += 1
        mutations.append(changed_measurement)
        for response in mutations:
            pairs, reason, evidence = verifier._validate_response(
                response,
                nonce=nonce,
                process_pid=exchange["pid"],
                parent_pid=exchange["parent_pid"],
            )
            assert pairs is None
            assert reason != "ok"
            assert evidence is None
    finally:
        _close_all(handles)


def _raw_exchange(fds: list[int]) -> dict:
    parent, child = socket.socketpair(socket.AF_UNIX, verifier._SOCKET_TYPE)
    process = subprocess.Popen(
        verifier._default_argv(child.fileno()),
        close_fds=True,
        pass_fds=(child.fileno(),),
        stdin=subprocess.DEVNULL,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    child.close()
    nonce = "56" * 32
    request = {
        "protocol": verifier.PROTOCOL,
        "nonce": nonce,
        "request_id": verifier._request_id(verifier.PROTOCOL, nonce),
    }
    if fds:
        rights = array.array("i", fds)
        parent.sendmsg(
            [verifier._canonical(request)],
            [(socket.SOL_SOCKET, socket.SCM_RIGHTS, rights.tobytes())],
        )
    else:
        parent.sendall(verifier._canonical(request))
    parent.shutdown(socket.SHUT_WR)
    payload = parent.recv(verifier.MAX_MESSAGE)
    parent.close()
    assert process.wait(timeout=3) == 0
    return json.loads(payload)


@pytest.mark.parametrize("count", [0, 1, 3])
def test_verifier_requires_exactly_two_scm_rights(tmp_path: Path, count: int):
    handles = []
    try:
        for index in range(max(count, 1)):
            folder = tmp_path / str(index)
            folder.mkdir()
            handles.append(os.open(folder / "file", os.O_RDWR | os.O_CREAT, 0o600))
        response = _raw_exchange(handles[:count])
        assert response["status"] == "UNBEKANNT"
        assert "exactly_two_received_fds_required" in response["reason"]
    finally:
        _close_all(handles)


def test_fd_order_swap_and_substitution_are_not_accepted(tmp_path: Path):
    intended, offered = _open_pair(tmp_path / "intended", False)
    substitute, _ = _open_pair(tmp_path / "substitute", False)
    packet = _packet(offered)
    try:
        swapped = verifier.verify_current_fd_identity(
            packet, 1, {"A": "VERSCHIEDEN"}, handles=list(reversed(intended))
        )
        replaced = verifier.verify_current_fd_identity(
            packet, 1, {"A": "VERSCHIEDEN"}, handles=substitute
        )
        assert swapped["A"] == "UNBEKANNT"
        assert swapped["B"] == "verifier_packet_mismatch"
        assert replaced["A"] == "UNBEKANNT"
        assert replaced["B"] == "verifier_packet_mismatch"
        assert all(fcntl.fcntl(fd, fcntl.F_GETFD) >= 0 for fd in intended + substitute)
    finally:
        _close_all(intended + substitute)


def test_matching_fd_substitution_is_outside_origin_authentication(tmp_path: Path):
    intended, _ = _open_pair(tmp_path / "original-intent", True)
    substitute, substitute_pairs = _open_pair(tmp_path / "sender-substitute", True)
    try:
        result = verifier.verify_current_fd_identity(
            _packet(substitute_pairs),
            1,
            {"A": "DIESELBE"},
            handles=substitute,
        )
        assert result["A"] == "DIESELBE"
        assert result["fd_set_verified"] is True
        assert result["source_authenticated"] is False
        assert "Keine Authentisierung" in result["D"]
        assert [(os.fstat(fd).st_dev, os.fstat(fd).st_ino) for fd in intended] != substitute_pairs
    finally:
        _close_all(intended + substitute)


def test_positive_verifier_packet_result_cannot_override_observer_disagreement(
    tmp_path: Path,
):
    handles, actual = _open_pair(tmp_path / "observer-disagreement", False)
    try:
        result = verifier.verify_current_fd_identity(
            _packet(actual), 1, {"A": "DIESELBE"}, handles=handles
        )
        assert result["A"] == "UNBEKANNT"
        assert result["B"] == "verifier_observer_mismatch"
        assert result["fd_set_verified"] is True
        assert result["positive_identity_authorized"] is False
    finally:
        _close_all(handles)


@pytest.mark.parametrize(
    "events,observer,handles,reason",
    [
        (None, {"A": "DIESELBE"}, [7, 8], "invalid_packet_binding"),
        (_packet([(1, 1), (1, 1)], omit_regular=True), {"A": "DIESELBE"}, [7, 8],
         "invalid_packet_references"),
        (_packet([(1, 1), (1, 1)]), {"A": "UNBEKANNT"}, [7, 8],
         "observer_not_positive"),
        (_packet([(1, 1), (1, 1)]), {"A": "DIESELBE"}, [7, 7],
         "invalid_fd_arguments"),
    ],
)
def test_preconditions_fail_closed_without_starting_broker(
    events: object, observer: object, handles: object, reason: str
):
    result = verifier.verify_current_fd_identity(
        events, 1, observer, handles=handles  # type: ignore[arg-type]
    )
    assert result["A"] == "UNBEKANNT"
    assert result["B"] == reason
    assert "verifier" not in result
