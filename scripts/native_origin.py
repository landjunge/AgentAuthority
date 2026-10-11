"""Explicit Agent Authority receiver/client; no observer or action-boundary changes."""

import argparse
import json
import sys

from lab.origin import OriginReceiver
from lab.origin.receiver import MAX_MESSAGE, encode_message


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    actions = parser.add_subparsers(dest="action", required=True)
    receiver = actions.add_parser("receive")
    receiver.add_argument("--task", required=True)
    receiver.add_argument("--count", type=int, default=1, choices=range(1, 9))
    client = actions.add_parser("send")
    client.add_argument("--endpoint", required=True)
    client.add_argument("--replay", action="store_true")
    args = parser.parse_args()
    if args.action == "receive":
        with OriginReceiver(args.task) as ingress:
            print(json.dumps({"endpoint": ingress.endpoint, "task": args.task}), flush=True)
            for _ in range(args.count):
                print(json.dumps(ingress.receive()), flush=True)
        return 0
    if sys.platform != "darwin":
        print(json.dumps({"status": "UNBEKANNT", "reason": "unsupported_platform"}))
        return 2
    from lab.origin.macos import MachClient

    data = sys.stdin.buffer.read(MAX_MESSAGE + 1)
    native = MachClient(args.endpoint)
    try:
        challenge = native.hello()
        wire = encode_message(challenge, data)
        print(native.request(wire).data.decode(), flush=True)
        if args.replay:
            print(native.request(wire).data.decode(), flush=True)
    finally:
        native.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
