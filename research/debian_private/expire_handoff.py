"""Fixed encrypted handoff expiry; no paths accepted from clients."""

from research.debian_private.ipc import SECURE
from research.private_service.retention import fsync_dir

if __name__ == "__main__":
    p = SECURE / "runner/pending.json"
    assert not p.is_symlink()
    p.unlink(missing_ok=True)
    fsync_dir(p.parent)
