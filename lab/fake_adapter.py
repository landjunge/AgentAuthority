from __future__ import annotations

from typing import Any

from lab.fake_repo import FakeRepo
from lab.models import ActionRequest, Decision
from lab.paths import canonical_path
from lab.validator import Lab


class FakeAdapter:
    """Local action surface. No sockets, no real git, no credentials."""

    def __init__(self, lab: Lab | None = None) -> None:
        self.lab = lab or Lab()
        self.repo = FakeRepo()

    def _key(self, path: str) -> str:
        """One identity for the monitor and the repo. T-19."""
        return canonical_path(path) or path

    def write(
        self,
        actor: str,
        path: str,
        workflow_id: str,
        content: str = "",
        approval_token: Any = None,
    ) -> Decision:
        _ = content  # not persisted on deny; repo only updates on allow
        key = self._key(path)
        params: dict[str, Any] = {"content": content}
        if approval_token is not None:
            params["approval_token"] = approval_token
        req = ActionRequest(actor, "file.write", key, params, workflow_id)
        d = self.lab.submit(req)
        if d.allow:
            self.lab.commit_effect(req, d, lambda: self.repo.files.__setitem__(key, content))
        else:
            d.effect_committed = False
        return d

    def read(self, actor: str, path: str, workflow_id: str) -> Decision:
        return self.lab.submit(ActionRequest(actor, "file.read", self._key(path), {}, workflow_id))

    def delete(
        self, actor: str, path: str, workflow_id: str, approval_token: Any = None
    ) -> Decision:
        params: dict[str, Any] = {}
        if approval_token is not None:
            params["approval_token"] = approval_token
        key = self._key(path)
        req = ActionRequest(actor, "file.delete", key, params, workflow_id)
        d = self.lab.submit(req)
        if d.allow:

            def delete_effect() -> None:
                self.repo.files.pop(key, None)

            self.lab.commit_effect(req, d, delete_effect)
        else:
            d.effect_committed = False
        return d

    def delegate(self, actor: str, to: str, workflow_id: str) -> Decision:
        return self.lab.submit(ActionRequest(actor, "delegate", to, {"to": to}, workflow_id))

    def net_connect(self, actor: str, destination: str, workflow_id: str) -> Decision:
        return self.lab.submit(
            ActionRequest(
                actor, "net.connect", destination, {"destination": destination}, workflow_id
            )
        )

    def irreversible(
        self, actor: str, action: str, workflow_id: str, approval_token: Any = None
    ) -> Decision:
        params: dict[str, Any] = {}
        if approval_token is not None:
            params["approval_token"] = approval_token
        return self.lab.submit(ActionRequest(actor, action, action, params, workflow_id))
