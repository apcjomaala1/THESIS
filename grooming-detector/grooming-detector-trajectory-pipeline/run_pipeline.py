"""One-shot pipeline driver: clean → centroid → val features → tune → eval.

Run with:
    python run_pipeline.py

All paths are hardcoded relative to this file's directory so there's no
shell-wrap or quoting risk. Edit the constants below if your layout changes.
"""

import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).parent
DATASET_DIR = HERE.parent / "dataset"
PAN12 = HERE.parent / "trained_model_distillbert" / "pan12_final_dataset.csv"

POSITIVE_SOURCES = [
    f"pan12={PAN12}",
    f"roblox_run={DATASET_DIR / 'RobloxPredatorTriesToRun.csv'}",
    f"yt_dyadic={DATASET_DIR / 'WeGotARobloxPredatorArrested.csv'}",
    f"yt_dyadic2={DATASET_DIR / 'WeGotARobloxPredatorArrested2.csv'}",
]

CENTROID_SOURCES = [
    f"pan12={PAN12}",
    f"discord={DATASET_DIR / 'DiscordCommunityChat.csv'}",
    f"groupchat={DATASET_DIR / 'anonymized_group_chat_dataset.csv'}",
]

CENTROID = HERE / "benign_centroid.npy"
SCORER = HERE / "weighted_scorer.json"
VAL_FEATURES = HERE / "val_features.npz"


def run(label, cmd):
    print(f"\n=== {label} ===")
    print(" ".join(str(x) for x in cmd))
    r = subprocess.run([str(x) for x in cmd], cwd=HERE)
    if r.returncode != 0:
        print(f"\n[run_pipeline] step '{label}' failed with exit code {r.returncode}")
        sys.exit(r.returncode)


def main():
    py = sys.executable

    run("1/6 clean datasets",
        [py, "clean_datasets.py", "--in", DATASET_DIR])

    run("2/6 build benign centroid",
        [py, "compute_benign_centroid.py",
         "--datasets", *CENTROID_SOURCES,
         "--no-require-dyadic",
         "--out", CENTROID])

    if SCORER.exists():
        SCORER.unlink()
        print(f"\n[run_pipeline] removed stale {SCORER.name}")

    run("3/6 dump val features",
        [py, "main.py",
         "--datasets", *POSITIVE_SOURCES,
         "--centroid", CENTROID,
         "--scorer-config", SCORER,
         "--dump-val-features", VAL_FEATURES])

    run("4/6 tune weighted scorer",
        [py, "tune_weights.py",
         "--val-features", VAL_FEATURES,
         "--out", SCORER])

    run("5/6 final evaluation",
        [py, "main.py",
         "--datasets", *POSITIVE_SOURCES,
         "--centroid", CENTROID,
         "--scorer-config", SCORER])

    print("\n=== 6/6 done ===")
    print(f"Tuned scorer:  {SCORER}")
    print(f"Centroid:      {CENTROID}")
    print(f"Val features:  {VAL_FEATURES}")
    print("Demo:          python -m demo.app  (then open http://127.0.0.1:5000)")


if __name__ == "__main__":
    main()
