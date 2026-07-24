"""Deterministic summary generation from raw ML-KEM benchmark records."""

from __future__ import annotations

import csv
import json
import math
import statistics
from collections import defaultdict
from pathlib import Path


def _percentile(values: list[int], percentile: float) -> float:
    ordered = sorted(values)
    index = (len(ordered) - 1) * percentile
    lower, upper = math.floor(index), math.ceil(index)
    if lower == upper:
        return float(ordered[lower])
    return ordered[lower] + (ordered[upper] - ordered[lower]) * (index - lower)


def summarize_csv(raw_path: Path) -> dict:
    groups: dict[tuple[str, str], list[int]] = defaultdict(list)
    with raw_path.open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            if row["success"] == "True":
                groups[(row["mlkem_variant"], row["operation"])].append(int(row["execution_time_ns"]))

    summary = {"source_raw_csv": str(raw_path), "groups": []}
    for (variant, operation), values in sorted(groups.items()):
        mean = statistics.mean(values)
        summary["groups"].append({
            "mlkem_variant": variant, "operation": operation, "count": len(values),
            "mean_ns": mean, "median_ns": statistics.median(values), "min_ns": min(values),
            "max_ns": max(values), "stddev_ns": statistics.stdev(values) if len(values) > 1 else 0.0,
            "coefficient_of_variation": (statistics.stdev(values) / mean) if len(values) > 1 and mean else 0.0,
            "p95_ns": _percentile(values, 0.95), "p99_ns": _percentile(values, 0.99),
            "throughput_ops_per_second": 1_000_000_000 / mean if mean else 0.0,
        })
    return summary


def write_summary(raw_path: Path, output_path: Path) -> dict:
    if output_path.exists():
        raise FileExistsError("Refusing to overwrite an existing processed summary")
    summary = summarize_csv(raw_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("x", encoding="utf-8") as handle:
        json.dump(summary, handle, indent=2)
        handle.write("\n")
    return summary

