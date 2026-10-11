"""FakeAdapter and the monitor share one path identity. docs/PHASE1-ADAPTER-IDENTITY.md."""

from lab.fake_adapter import FakeAdapter


def test_alias_writes_are_one_repo_key_and_one_monitor_file():
    ad = FakeAdapter()
    wid = "wf-t19"
    assert ad.write("A", "src/a.py", wid, "v1").allow
    assert ad.write("A", "./src/a.py", wid, "v2").allow
    assert ad.write("A", "src/foo/../a.py", wid, "v3").allow
    assert ad.repo.files["src/a.py"] == "v3"
    assert "./src/a.py" not in ad.repo.files
    assert "src/foo/../a.py" not in ad.repo.files
    st = ad.lab.state(wid)
    assert st.files_changed == 1
    assert st.touched_paths == {"src/a.py"}


def test_alias_delete_pops_the_canonical_key():
    ad = FakeAdapter()
    wid = "wf-t19-del"
    assert ad.write("A", "src/a.py", wid, "keep").allow
    d = ad.delete("A", "./src/foo/../a.py", wid)
    assert d.allow is True
    assert "src/a.py" not in ad.repo.files
    assert "./src/foo/../a.py" not in ad.repo.files


def test_alias_delete_of_seeded_security_test_uses_canonical_key():
    ad = FakeAdapter()
    ad.repo.files["tests/security/check.py"] = "important"
    d = ad.delete("A", "tests/other/../security/check.py", "wf-canonical-adapter", "approved")
    assert d.allow is True
    assert "tests/security/check.py" not in ad.repo.files
