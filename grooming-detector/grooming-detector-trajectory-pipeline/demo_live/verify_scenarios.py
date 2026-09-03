"""Run every synthetic demo chat prefix through the real frozen engine."""

from __future__ import annotations

import json
import sys
from pathlib import Path

PIPELINE_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PIPELINE_ROOT))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from scenarios import SCENARIOS
from scoring_engine import LiveDemoEngine


def verify() -> dict:
    engine = LiveDemoEngine()
    rows = []
    failures = []

    for scenario in SCENARIOS:
        final_result = None
        for prefix_length in range(1, len(scenario["turns"]) + 1):
            final_result = engine.score_turn(scenario["turns"][:prefix_length])
            if final_result.get("turns_count") != prefix_length:
                failures.append(
                    f"{scenario['id']}: prefix {prefix_length} did not score completely"
                )

        assert final_result is not None
        flags = final_result["trajectory_curve"]["lstm_flags"]
        first_flag = next((index + 1 for index, flag in enumerate(flags) if flag), None)
        actual_flag = bool(final_result["decision"]["lstm"]["flagged"])
        expected_flag = scenario["expected_lstm_flagged"]
        expected_first = scenario["expected_first_flag_turn"]

        if actual_flag != expected_flag:
            failures.append(
                f"{scenario['id']}: expected flagged={expected_flag}, got {actual_flag}"
            )
        if first_flag != expected_first:
            failures.append(
                f"{scenario['id']}: expected first flag {expected_first}, got {first_flag}"
            )

        rows.append(
            {
                "id": scenario["id"],
                "prefixes_scored": len(scenario["turns"]),
                "final_lstm_score": final_result["decision"]["lstm"]["score"],
                "lstm_threshold": final_result["decision"]["lstm"]["threshold"],
                "final_flagged": actual_flag,
                "first_flag_turn": first_flag,
            }
        )

    return {"passed": not failures, "failures": failures, "scenarios": rows}


if __name__ == "__main__":
    report = verify()
    print(json.dumps(report, indent=2))
    raise SystemExit(0 if report["passed"] else 1)
