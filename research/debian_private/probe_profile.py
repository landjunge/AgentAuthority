"""Persist only this collector's probe counters, never foreign tracefs rows."""

from pathlib import Path


def profile(names):
    try:
        selected = {}
        with Path("/sys/kernel/tracing/kprobe_profile").open() as stream:
            for line in stream:
                row = line.split()
                if len(row) == 3 and row[0] in names:
                    selected[row[0]] = {"hits": int(row[1]), "misses": int(row[2])}
        complete = set(selected) == set(names)
        return {"selected": selected, "complete": complete}
    except (OSError, ValueError):
        return {"selected": {}, "complete": False}
