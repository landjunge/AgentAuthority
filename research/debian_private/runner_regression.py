"""Historical counterexamples in the real runner sandbox; never claims/actions."""

import json

from research.debian_private.ipc import SECURE
from research.debian_private.runner import counterexamples


def main():
    data = json.loads((SECURE / "runner/regression.json").read_bytes())
    print(
        json.dumps(
            {
                "scope": "historical regression only; no current action",
                "cases": counterexamples(data["evidence"], data["binding"]),
            }
        )
    )


if __name__ == "__main__":
    main()
