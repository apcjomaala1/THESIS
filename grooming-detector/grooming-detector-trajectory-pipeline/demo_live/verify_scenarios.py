"""Verify every synthetic demo prefix and the saved validation examples under F2."""

from __future__ import annotations

import json

from demo_live.app import SCENARIOS, get_engine
from demo_live.scenarios import SCENARIOS as SYNTHETIC_SCENARIOS
from privacy import redact_text


def verify() -> dict:
    engine = get_engine()
    failures: list[str] = []
    rows: list[dict] = []
    for scenario in SCENARIOS:
        history = [
            {"author": turn["author"], "text": redact_text(turn["text"])}
            for turn in scenario["turns"]
        ]
        prefix_flags: list[bool] = []
        if scenario in SYNTHETIC_SCENARIOS:
            for length in range(1, len(history) + 1):
                prefix_result = engine.score_turn(history[:length])
                if prefix_result["turns_count"] != length:
                    failures.append(f"{scenario['id']}: wrong prefix length {length}")
                prefix_flags.append(bool(prefix_result["decision"]["lstm"]["flagged"]))
            result = prefix_result
        else:
            result = engine.score_turn(history)
        decisions = {
            key: bool(value["flagged"]) for key, value in result["decision"].items()
        }
        first = next(
            (i + 1 for i, flag in enumerate(result["trajectory_curve"]["lstm_flags"]) if flag),
            None,
        )
        if prefix_flags and prefix_flags != result["trajectory_curve"]["lstm_flags"]:
            failures.append(f"{scenario['id']}: independently scored prefixes differ from trajectory")
        if scenario in SYNTHETIC_SCENARIOS:
            for key, expected in scenario["expected_flags"].items():
                if decisions.get(key) != expected:
                    failures.append(f"{scenario['id']}: {key} expected {expected}, got {decisions.get(key)}")
            if first != scenario["expected_first_flag_turn"]:
                failures.append(f"{scenario['id']}: expected first flag {scenario['expected_first_flag_turn']}, got {first}")
        rows.append({"id": scenario["id"], "turns": len(history), "decisions": decisions, "primary_first_flagged_turn": first})
    return {"passed": not failures, "failures": failures, "scenarios": rows}


def main() -> None:
    report = verify()
    print(json.dumps(report, indent=2))
    raise SystemExit(0 if report["passed"] else 1)


if __name__ == "__main__":
    main()
