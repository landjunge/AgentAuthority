"""Run only inside the existing isolated guest; bind service inputs in the A4 job.

The original registrar/worker/collector are copied byte-for-byte beside this file.
The only adaptation enriches the job before its existing digest and signatures.
"""

import argparse
import json
import os
from pathlib import Path

import original_guest

original_digest = original_guest.digest
context = json.loads(Path(__file__).with_name("service-binding.json").read_text())


def service_digest(value):
    if (
        type(value) is dict
        and set(value) == {"operation", "file"}
        and value["operation"] == "write16"
    ):
        value["service_binding"] = context
    return original_digest(value)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=["trial"])
    parser.add_argument("vault", type=Path)
    parser.add_argument("--certificate", type=Path)
    parser.add_argument("--path", type=Path)
    args = parser.parse_args()
    if os.geteuid() != 0 or not str(args.vault).startswith("/var/tmp/a4c-private-"):
        raise ValueError("isolated guest root required")
    original_guest.digest = service_digest
    print(json.dumps(original_guest.trial(args.vault, args.certificate, args.path)))
