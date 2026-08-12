import json
from pathlib import Path

from capture_environment import collect_environment, compare_snapshot


def test_recorded_environment_matches_current_runtime():
    pipeline_root = Path(__file__).resolve().parents[1]
    expected = json.loads(
        (pipeline_root / "environment_snapshot.json").read_text(encoding="utf-8")
    )

    differences = compare_snapshot(expected, collect_environment())

    assert differences == []
