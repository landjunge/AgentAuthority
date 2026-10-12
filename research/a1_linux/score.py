"""Offline conservative scoring; never runs inside or supplies input to collector."""


def _evaluate(capture, oracle):
    ready = next((x for x in capture if x.get("ready")), None)
    summary = next((x["summary"] for x in capture if "summary" in x), None)
    result = {
        "evidence": "UNBEKANNT",
        "correct": 0,
        "wrong": 0,
        "unclear": None,
        "logical_agent_identity": "UNBEKANNT",
        "reasons": [],
    }
    if ready is None or summary is None:
        result["reasons"].append("incomplete capture")
        return result
    writes = [x["record"] for x in capture if x.get("record", {}).get("kind") == 1]
    profile = summary.get("kprobe_profile")
    stats = summary["stats"]
    healthy = (
        summary["perf_lost"] == 0
        and summary["pending"] == 0
        and all(stats.get(str(k), -1) == 0 for k in [3, 4, 5, 7])
        and stats.get("0") == stats.get("1") == stats.get("2") == len(writes)
        and profile is not None
        and len(profile) >= 1
        and any(row[0].startswith("r_vfs_write") for row in profile)
        and all(int(row[-1]) == 0 for row in profile)
    )
    expected = [
        row
        for row in oracle["rows"]
        if row.get("file") == ready["file"] and row["action"] == "write" and row["result"] > 0
    ]
    result.update(
        expected_actions=len(expected),
        observed_actions=len(writes),
        unclear=len(expected),
        loss_checks=healthy,
    )
    if not healthy:
        result["reasons"].append("loss/pair/profile coverage unknown or failed")
        return result
    if any(
        record["start_ns"] <= 0
        or record["tgid"] <= 0
        or record["entry_ns"] <= 0
        or record["exit_ns"] < record["entry_ns"]
        for record in writes
    ):
        result["reasons"].append("invalid kernel instance/time fields")
        return result
    if (
        oracle["controller"]["boot_hash"] != ready["boot_hash"]
        or oracle["controller"]["pid_namespace"] != ready["pid_namespace"]
    ):
        result["reasons"].append("boot/namespace mismatch")
        return result
    consumed = set()
    for row in expected:
        process = row["process"]
        matches = []
        if not row["stable"] or not row["pidfd_exit_seen"] or row["exit_status"] != 0:
            result["reasons"].append("oracle instance/lifecycle unstable")
            continue
        for index, record in enumerate(writes):
            if index in consumed:
                continue
            if (
                record["tgid"] == process["pid"]
                and record["ppid"] == process["ppid"]
                and record["start_ns"] > 0
                and record["boot_hash"] == ready["boot_hash"]
                and abs(
                    record["start_ns"] * process["clock_ticks"] // 1_000_000_000
                    - process["start_ticks"]
                )
                <= 1
                and {k: record[k] for k in ["dev", "inode"]} == row["file"]
                and record["count"] == record["result"] == row["result"] == 16
                and ready["ready_ns"]
                <= row["begin_ns"]
                <= record["entry_ns"]
                <= record["exit_ns"]
                <= row["end_ns"]
                <= summary["end_ns"]
            ):
                matches.append(index)
        if len(matches) == 1:
            consumed.add(matches[0])
            result["correct"] += 1
        else:
            result["reasons"].append("missing/ambiguous action-instance binding")
    result["unclear"] = len(expected) - result["correct"]
    result["wrong"] = len(writes) - len(consumed)
    result["false_claim_used"] = any(r["tgid"] == oracle.get("forged_claim_pid") for r in writes)
    result["sequential_order"] = all(
        writes[i]["exit_ns"] <= writes[i + 1]["entry_ns"] for i in range(len(writes) - 1)
    )
    result["exit_records"] = len([x for x in capture if x.get("record", {}).get("kind") == 2])
    result["distinct_process_instances"] = len(
        {(r["boot_hash"], r["tgid"], r["start_ns"]) for r in writes}
    )
    if result["wrong"] or result["false_claim_used"] or not result["sequential_order"]:
        result["evidence"] = "WIDERLEGT"
    elif result["unclear"]:
        result["evidence"] = "TEILWEISE BELEGT" if result["correct"] else "UNBEKANNT"
    else:
        result["evidence"] = "BELEGT"
    return result


def evaluate(capture, oracle):
    try:
        return _evaluate(capture, oracle)
    except (KeyError, TypeError, ValueError, AttributeError):
        return {
            "evidence": "UNBEKANNT",
            "correct": 0,
            "wrong": None,
            "unclear": None,
            "logical_agent_identity": "UNBEKANNT",
            "reasons": ["malformed evidence"],
        }
