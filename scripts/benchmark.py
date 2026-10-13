"""Measure actual assessment plus warmed OSCAL validation, not production certification. Created by Jason Stys."""
# BEGIN CODE MAP (generated; python scripts/code_map.py)
# variable: ROOT — line 33
# definition: measure — line 40
# variable: root — line 42
# variable: samples — line 44
# variable: _ — line 45
# variable: started — line 46
# variable: _ — line 47
# variable: bundle — line 48
# variable: result — line 48
# variable: _ — line 58
# variable: peak — line 58
# variable: sample — line 66
# definition: main — line 74
# variable: parser — line 76
# variable: arguments — line 78
# variable: result — line 79
# variable: stream — line 82
# END CODE MAP

from __future__ import annotations

import argparse
import json
import platform
import statistics
import sys
import time
import tracemalloc
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from rmf.assessment import assess  # noqa: E402
from rmf.oscal import build  # noqa: E402


def measure() -> dict[str, object]:
    """Measure five batches of ten real six-control assessments and schema/reference validations after a cold warmup."""
    root = ROOT / "examples/baseline"
    build(*assess(root, "2026-10-12T12:00:00Z"))
    samples = []
    for _ in range(5):
        started = time.perf_counter()
        for _ in range(10):
            bundle, result = assess(root, "2026-10-12T12:00:00Z")
            build(bundle, result)
            if (
                result["summary"]["UNKNOWN"] != 1
                or result["summary"]["NOT_SATISFIED"] != 2
            ):
                raise ValueError("benchmark oracle mismatch")
        samples.append((time.perf_counter() - started) * 1000 / 10)
    tracemalloc.start()
    build(*assess(root, "2026-10-12T12:00:00Z"))
    _, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    return {
        "controls_per_snapshot": 6,
        "oscal_models_per_snapshot": 6,
        "batches": 5,
        "snapshots_per_batch": 10,
        "median_ms_per_snapshot": round(statistics.median(samples), 3),
        "samples_ms_per_snapshot": [round(sample, 3) for sample in samples],
        "peak_python_allocated_bytes": peak,
        "python": platform.python_version(),
        "os": platform.system(),
        "scope": "warm Python assessment + actual OSCAL schema/reference validation; includes local evidence reads, excludes Node startup, SQLite and production collection; timings informational",
    }


def main() -> int:
    """Print measured evidence or write a new requested benchmark file without overwriting previous results."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    arguments = parser.parse_args()
    result = json.dumps(measure(), indent=2, sort_keys=True)
    if arguments.output:
        arguments.output.parent.mkdir(parents=True, exist_ok=True)
        with arguments.output.open("x", encoding="utf-8") as stream:
            stream.write(result + "\n")
    print(result)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
