from __future__ import annotations

import json
import re
from dataclasses import asdict, dataclass
from pathlib import Path

FINGERPRINTS = Path(__file__).parents[1] / "fingerprints" / "technologies.json"


@dataclass(frozen=True)
class Evidence:
    source: str
    matched: str
    kind: str
    weight: int


@dataclass(frozen=True)
class Detection:
    name: str
    category: str
    score: int
    confidence: str
    evidence: tuple[Evidence, ...]

    def to_dict(self):
        result = asdict(self)
        result["evidence"] = [asdict(item) for item in self.evidence]
        return result


def _values(snapshot: dict, source: str) -> list[str]:
    if source.startswith("header:"):
        value = snapshot.get("headers", {}).get(source.partition(":")[2].lower())
        return [str(value)] if value else []
    if source == "meta_generator":
        return [
            str(item.get("content", ""))
            for item in snapshot.get("meta", [])
            if item.get("name", "").lower() == "generator"
        ]
    if source in {"script_src", "style_href"}:
        return [str(value) for value in snapshot.get("scripts" if source == "script_src" else "styles", [])]
    if source == "html":
        return [str(snapshot.get("html", ""))]
    return []


def detect(snapshot: dict, fingerprints_path: Path = FINGERPRINTS) -> list[Detection]:
    ruleset = json.loads(fingerprints_path.read_text(encoding="utf-8"))
    detected = []
    for technology in ruleset:
        evidence = []
        seen = set()
        score = 0
        for rule in technology["rules"]:
            pattern = rule["pattern"]
            for value in _values(snapshot, rule["source"]):
                match = re.search(pattern, value, re.IGNORECASE)
                if match:
                    matched = match.group(0)[:240]
                    key = (rule["source"], matched.casefold())
                    if key not in seen:
                        seen.add(key)
                        weight = max(0, min(100, int(rule["weight"])))
                        evidence.append(Evidence(
                            rule["source"], matched,
                            "direct" if rule["source"].startswith("header:") or rule["source"] == "meta_generator" else "indirect",
                            weight,
                        ))
                        score = min(100, score + weight)
                    break
        if evidence:
            confidence = "high" if score >= 70 else "medium" if score >= 40 else "low"
            detected.append(Detection(technology["name"], technology["category"], score, confidence, tuple(evidence)))
    return sorted(detected, key=lambda item: (item.category, item.name.casefold()))
