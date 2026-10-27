def compare_results(previous: list[dict], current: list[dict]) -> dict:
    before = {item["name"]: set(item.get("evidence", [])) for item in previous}
    after = {item["name"]: set(item.get("evidence", [])) for item in current}
    common = before.keys() & after.keys()
    return {
        "newly_observed": sorted(after.keys() - before.keys()),
        "not_observed_now": sorted(before.keys() - after.keys()),
        "evidence_changed": sorted(name for name in common if before[name] != after[name]),
        "unchanged": sorted(name for name in common if before[name] == after[name]),
    }
