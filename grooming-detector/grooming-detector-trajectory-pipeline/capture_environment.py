"""Print or verify the software environment used by the current workspace."""

from __future__ import annotations

import argparse
import json
import platform
from datetime import date
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path


TRACKED_DISTRIBUTIONS = (
    "torch",
    "transformers",
    "accelerate",
    "datasets",
    "scikit-learn",
    "numpy",
    "pandas",
    "tqdm",
    "flask",
    "pytest",
    "scipy",
)


def collect_environment():
    packages = {}
    for distribution in TRACKED_DISTRIBUTIONS:
        try:
            packages[distribution] = version(distribution)
        except PackageNotFoundError:
            packages[distribution] = None

    return {
        "schema_version": 1,
        "captured_on": date.today().isoformat(),
        "scope": (
            "Current rerun/demo environment only; not proof of the historical "
            "Layer 1 training environment."
        ),
        "python": platform.python_version(),
        "platform": platform.platform(),
        "packages": packages,
    }


def compare_snapshot(expected, current):
    differences = []
    for key in ("python", "platform"):
        if expected.get(key) != current.get(key):
            differences.append(f"{key}: expected {expected.get(key)!r}, got {current.get(key)!r}")

    expected_packages = expected.get("packages", {})
    for distribution in TRACKED_DISTRIBUTIONS:
        expected_version = expected_packages.get(distribution)
        current_version = current["packages"].get(distribution)
        if expected_version != current_version:
            differences.append(
                f"{distribution}: expected {expected_version!r}, got {current_version!r}"
            )
    return differences


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check",
        type=Path,
        help="Compare the current environment with an existing JSON snapshot.",
    )
    args = parser.parse_args()

    current = collect_environment()
    if args.check:
        expected = json.loads(args.check.read_text(encoding="utf-8"))
        differences = compare_snapshot(expected, current)
        if differences:
            print("Environment differs from the snapshot:")
            for difference in differences:
                print(f"- {difference}")
            raise SystemExit(1)
        print("Environment matches the recorded snapshot.")
        return

    print(json.dumps(current, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
