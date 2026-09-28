"""Benchmark warmed local HTTP turn scoring on fixed synthetic chat prefixes.

The script does not touch PAN12 evaluation partitions or tune any threshold.
Each request recomputes the full prefix, matching the current live demo.
"""

from __future__ import annotations

import argparse
import contextlib
import hashlib
import io
import json
import os
import platform
import random
import statistics
import subprocess
import threading
from datetime import datetime, timezone
from pathlib import Path
from time import perf_counter
from urllib.request import Request, urlopen

import numpy as np
import torch
from werkzeug.serving import WSGIRequestHandler, make_server

from demo_live.app import app, get_engine
from revised_pipeline.contracts import sha256_file


SYNTHETIC_MESSAGES = [
    "Hi, did you finish the group project outline?",
    "Not yet. I can work on the introduction tonight.",
    "Great. Let's compare our notes after class.",
    "I will send the document when I get home.",
    "Which section should I handle first?",
    "Please start with the examples section.",
    "Okay, I found two references we can discuss.",
    "Thanks. I'll check whether they fit the topic.",
    "The first source explains the background clearly.",
    "We should add a short summary of that source.",
    "I can write the summary before dinner.",
    "That works. We still need to check the citations.",
    "Let's review the draft together tomorrow.",
    "I am free after the morning class.",
    "Perfect, I will bring the updated outline.",
    "See you tomorrow. Thanks for helping.",
]
LENGTHS = (1, 4, 8, 16)
MODES = ("primary", "enhanced")


class QuietHandler(WSGIRequestHandler):
    def log(self, _type: str, _message: str, *args: object) -> None:
        return


def percentile(values: list[float], q: float) -> float:
    return float(np.percentile(np.asarray(values, dtype=np.float64), q, method="linear"))


def summarize(samples: list[float]) -> dict:
    return {
        "requests": len(samples),
        "median_ms": percentile(samples, 50),
        "p95_ms": percentile(samples, 95),
        "p99_ms": percentile(samples, 99),
        "mean_ms": statistics.fmean(samples),
        "min_ms": min(samples),
        "max_ms": max(samples),
        "sequential_throughput_requests_per_second": len(samples) / (sum(samples) / 1000),
    }


def cpu_name() -> str:
    if os.name != "nt":
        return platform.processor() or "unknown"
    try:
        process = subprocess.run(
            ["powershell", "-NoProfile", "-Command", "(Get-CimInstance Win32_Processor).Name"],
            capture_output=True, text=True, timeout=10, check=True,
        )
        return process.stdout.strip() or "unknown"
    except (OSError, subprocess.SubprocessError):
        return platform.processor() or "unknown"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repetitions", type=int, default=40)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.repetitions < 25:
        raise ValueError("At least 25 repetitions per length are required for the reported tails")

    started = perf_counter()
    engine = get_engine()
    initialization_seconds_after_import = perf_counter() - started
    app.config["BENCHMARK_QUIET"] = True
    server = make_server("127.0.0.1", 0, app, request_handler=QuietHandler)
    port = server.server_port
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    histories = {
        n: [{"author": "user_A" if i % 2 == 0 else "user_B", "text": text}
            for i, text in enumerate(SYNTHETIC_MESSAGES[:n])]
        for n in LENGTHS
    }
    request_bodies = {
        (mode, n): json.dumps({"model": mode, "history": histories[n]}).encode("utf-8")
        for mode in MODES for n in LENGTHS
    }

    def request_once(mode: str, n: int) -> float:
        payload = request_bodies[(mode, n)]
        request = Request(
            f"http://127.0.0.1:{port}/api/score",
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        t0 = perf_counter()
        with urlopen(request, timeout=30) as response:
            result = json.load(response)
        elapsed_ms = (perf_counter() - t0) * 1000
        key = "lstm" if mode == "primary" else "enhanced_lstm"
        if key not in result["decision"] or result["turns_count"] != n:
            raise AssertionError(f"Invalid {mode} API result at length {n}")
        return elapsed_ms

    try:
        with contextlib.redirect_stdout(io.StringIO()):
            for mode in MODES:
                for n in LENGTHS:
                    for _ in range(3):
                        request_once(mode, n)
            rng = random.Random(42)
            samples: dict[str, dict[int, list[float]]] = {
                mode: {n: [] for n in LENGTHS} for mode in MODES
            }
            for _ in range(args.repetitions):
                cases = [(mode, n) for mode in MODES for n in LENGTHS]
                rng.shuffle(cases)
                for mode, n in cases:
                    samples[mode][n].append(request_once(mode, n))
    finally:
        server.shutdown()
        thread.join(timeout=5)

    report = {
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "status": "measured_local_http_synthetic_replay",
        "method": "Warmed sequential localhost HTTP POST /api/score; full conversation prefix recomputed on each request; one LSTM selected per request; shared DistilBERT classifiers and feature computation included; JSON serialization and local transport included.",
        "scope": "Synthetic unlabelled chat, not PAN12 held-out test or production traffic; no threshold tuning or model training.",
        "hardware": {
            "platform": platform.platform(),
            "processor": platform.processor() or os.environ.get("PROCESSOR_IDENTIFIER", "unknown"),
            "cpu_name": cpu_name(),
            "logical_cpus": os.cpu_count(),
            "device": str(engine.device),
            "torch_version": str(torch.__version__),
            "torch_intraop_threads": torch.get_num_threads(),
            "torch_interop_threads": torch.get_num_interop_threads(),
        },
        "workload": {
            "prefix_lengths": list(LENGTHS),
            "repetitions_per_length_per_model": args.repetitions,
            "warmups_per_length_per_model": 3,
            "randomization_seed": 42,
            "synthetic_messages_sha256": hashlib.sha256(json.dumps(SYNTHETIC_MESSAGES).encode("utf-8")).hexdigest(),
            "concurrency": 1,
        },
        "model_artifacts": {
            "primary_checkpoint_sha256": sha256_file(Path(engine.frozen_protocol["artifact_roles"]["lstm_trajectory7"]["path"]) / "best_model.pt"),
            "enhanced_checkpoint_sha256": sha256_file(Path(engine.frozen_protocol["artifact_roles"]["lstm_enhanced775"]["path"]) / "best_model.pt"),
            "f2_cutoffs": {"primary": engine.lstm_threshold, "enhanced": engine.enhanced_lstm_threshold},
        },
        "engine_initialization_seconds_after_import": initialization_seconds_after_import,
        "results": {},
        "interpretation_note": "Throughput is completed sequential requests divided by cumulative timed request duration. p99 is an empirical estimate from the recorded samples, not a production service guarantee.",
    }
    for mode in MODES:
        combined = [value for n in LENGTHS for value in samples[mode][n]]
        report["results"][mode] = {
            "pooled_equal_prefix_mix": summarize(combined),
            "by_prefix_length": {str(n): summarize(samples[mode][n]) for n in LENGTHS},
        }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(args.output), "engine_initialization_seconds_after_import": initialization_seconds_after_import, "results": report["results"]}, indent=2))


if __name__ == "__main__":
    main()
