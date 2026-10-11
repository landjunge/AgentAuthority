"""v0.3: aliases collapse to one artifact. v0.2 tests stay unmodified."""

from lab.models import I2_FILE_LIMIT, I3_PROTECTED_PATH, ActionRequest
from lab.validator import Lab


def test_protected_path_aliases_are_denied():
    lab = Lab()
    wid = "wf-canon-prot"
    aliases = [
        "./config/security-policy.json",
        "config/../config/security-policy.json",
        "config//security-policy.json",
    ]
    for path in aliases:
        before = lab.state(wid).snapshot()
        d = lab.submit(ActionRequest("A", "file.write", path, {}, wid))
        assert d.allow is False, path
        assert d.deny_reason == I3_PROTECTED_PATH
        assert lab.state(wid).action_count == before.action_count
        assert lab.state(wid).touched_paths == before.touched_paths


def test_same_file_aliases_count_as_one_unique():
    lab = Lab()
    wid = "wf-canon-files"
    for path in ("src/a.py", "./src/a.py", "src/../src/a.py"):
        d = lab.submit(ActionRequest("A", "file.write", path, {}, wid))
        assert d.allow is True, path
    assert lab.state(wid).files_changed == 1
    for i in range(9):
        assert lab.submit(ActionRequest("B", "file.write", f"src/n{i}.py", {}, wid)).allow
    denied = lab.submit(ActionRequest("B", "file.write", "src/n9.py", {}, wid))
    assert denied.allow is False
    assert denied.deny_reason == I2_FILE_LIMIT
    assert lab.state(wid).files_changed == 10
