from __future__ import annotations

from lab.models import (
    DELETE_ACTIONS,
    I1_ACTION_BUDGET,
    I2_FILE_LIMIT,
    I3_PROTECTED_PATH,
    I4_DELEGATION_DEPTH,
    I5_NETWORK,
    I6_IRREVERSIBLE,
    I7_SECURITY_TEST_DELETE,
    I8_PROTECTED_MUTATION,
    I9_UNKNOWN_ACTION_PROTECTED,
    IRREVERSIBLE_ACTIONS,
    KNOWN_ACTIONS,
    MAX_ACTIONS,
    MAX_DELEGATION_DEPTH,
    MAX_UNIQUE_FILES,
    MUTATING_ACTIONS,
    PROTECTED_PATH,
    WRITE_ACTIONS,
    ActionRequest,
    WorkflowState,
)
from lab.paths import is_protected_path, is_security_test_path


def evaluate(req: ActionRequest, predicted: WorkflowState) -> list[str]:
    """Return violated invariant IDs. No LLM. No semantic intent."""
    violated: list[str] = []

    if predicted.action_count > MAX_ACTIONS:
        violated.append(I1_ACTION_BUDGET)

    if predicted.files_changed > MAX_UNIQUE_FILES:
        violated.append(I2_FILE_LIMIT)

    if req.action in WRITE_ACTIONS and is_protected_path(req.resource, PROTECTED_PATH):
        violated.append(I3_PROTECTED_PATH)

    if predicted.delegation_depth > MAX_DELEGATION_DEPTH:
        violated.append(I4_DELEGATION_DEPTH)

    if predicted.network_destinations:
        violated.append(I5_NETWORK)

    if req.action in IRREVERSIBLE_ACTIONS and not req.parameters.get("approval_token"):
        violated.append(I6_IRREVERSIBLE)

    if (
        req.action in DELETE_ACTIONS
        and is_security_test_path(req.resource)
        and not req.parameters.get("approval_token")
    ):
        violated.append(I7_SECURITY_TEST_DELETE)

    if req.action in MUTATING_ACTIONS:
        policy = is_protected_path(req.resource, PROTECTED_PATH)
        security_test = is_security_test_path(req.resource)
        if policy and req.action not in WRITE_ACTIONS:
            # I3 remains write-only in its deny_reason. Other verbs → I8.
            # No token override: I3 is not relaxed.
            violated.append(I8_PROTECTED_MUTATION)
        elif (
            security_test
            and req.action not in DELETE_ACTIONS
            and not req.parameters.get("approval_token")
        ):
            # I7 remains delete-only in its deny_reason. Other verbs → I8.
            violated.append(I8_PROTECTED_MUTATION)

    if req.action not in KNOWN_ACTIONS and (
        is_protected_path(req.resource, PROTECTED_PATH) or is_security_test_path(req.resource)
    ):
        # Fail closed at the protected boundary. Do not interpret the verb.
        violated.append(I9_UNKNOWN_ACTION_PROTECTED)

    return violated
