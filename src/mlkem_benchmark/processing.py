"""Reproducible processing of admitted ML-KEM raw benchmark data.

This module deliberately keeps raw observations immutable. Its outputs are
derived artifacts: a normalized observation table, grouped statistics, and an
admission manifest that records the exact input hashes used to create them.
"""

from __future__ import annotations

import csv
import hashlib
import json
import math
import statistics
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

from .core import REQUIRED_COLUMNS
from .validation import validate_raw_directory

NORMALIZED_MEASUREMENT_TYPES = {
    "NATIVE_HARDWARE": "REAL_HARDWARE", "REAL_HARDWARE": "REAL_HARDWARE",
    "NATIVE_SOFTWARE": "NATIVE_SOFTWARE", "VIRTUALIZED": "VIRTUALIZED",
    "EMULATED": "EMULATED", "DERIVED": "DERIVED",
}
OBSERVATION_COLUMNS = [*REQUIRED_COLUMNS, "source_file", "normalized_measurement_type"]
STATISTICS_COLUMNS = [
    "environment", "architecture", "raw_measurement_type", "normalized_measurement_type",
    "mlkem_variant", "operation", "count", "mean_execution_time_ns", "median_execution_time_ns",
    "min_execution_time_ns", "max_execution_time_ns", "stddev_execution_time_ns",
    "coefficient_of_variation", "p95_execution_time_ns", "p99_execution_time_ns",
    "mean_memory_bytes", "median_memory_bytes", "throughput_ops_per_second",
]


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _percentile(values: list[int], percentile: float) -> float:
    ordered = sorted(values)
    index = (len(ordered) - 1) * percentile
    lower, upper = math.floor(index), math.ceil(index)
    if lower == upper:
        return float(ordered[lower])
    return ordered[lower] + (ordered[upper] - ordered[lower]) * (index - lower)


def _statistics_row(key: tuple[str, str, str, str, str, str], rows: list[dict[str, str]]) -> dict[str, object]:
    timings = [int(row["execution_time_ns"]) for row in rows]
    memories = [int(row["memory_bytes"]) for row in rows]
    mean = statistics.mean(timings)
    stddev = statistics.stdev(timings) if len(timings) > 1 else 0.0
    return dict(zip(STATISTICS_COLUMNS, [
        *key, len(rows), mean, statistics.median(timings), min(timings), max(timings), stddev,
        stddev / mean if mean else 0.0, _percentile(timings, 0.95), _percentile(timings, 0.99),
        statistics.mean(memories), statistics.median(memories), 1_000_000_000 / mean if mean else 0.0,
    ]))


def build_processed_dataset(raw_dir: Path, output_dir: Path, *, overwrite: bool = False) -> dict[str, object]:
    """Validate raw data and write derived artifacts without changing raw files."""
    validation = validate_raw_directory(raw_dir)
    invalid = {str(path): errors for path, (_, errors) in validation.items() if errors}
    if invalid:
        details = "; ".join(f"{path}: {len(errors)} error(s)" for path, errors in invalid.items())
        raise ValueError(f"Raw-data validation failed; no processed output written: {details}")
    if not validation:
        raise ValueError("No raw CSV files found")

    expected = [output_dir / name for name in ("observations.csv", "benchmark_statistics.csv", "admission_manifest.json")]
    if not overwrite and any(path.exists() for path in expected):
        raise FileExistsError("Processed output already exists; choose a new directory or pass overwrite=True")
    output_dir.mkdir(parents=True, exist_ok=True)

    observations: list[dict[str, str]] = []
    groups: dict[tuple[str, str, str, str, str, str], list[dict[str, str]]] = defaultdict(list)
    identities: set[tuple[str, str, str, str, str]] = set()
    source_files = []
    for path in sorted(validation):
        row_count, _ = validation[path]
        source_files.append({"file": path.name, "sha256": _sha256(path), "row_count": row_count})
        with path.open(newline="", encoding="utf-8") as handle:
            for raw_row in csv.DictReader(handle):
                normalized = NORMALIZED_MEASUREMENT_TYPES.get(raw_row["measurement_type"])
                if normalized is None:
                    raise ValueError(f"Unsupported measurement type in admitted data: {raw_row['measurement_type']}")
                identity = (raw_row["environment"], raw_row["run_id"], raw_row["mlkem_variant"], raw_row["operation"], raw_row["iteration"])
                if identity in identities:
                    raise ValueError(f"Duplicate benchmark identity across raw files: {identity}")
                identities.add(identity)
                row = {**raw_row, "source_file": path.name, "normalized_measurement_type": normalized}
                observations.append(row)
                if raw_row["success"] == "True":
                    key = (raw_row["environment"], raw_row["architecture"], raw_row["measurement_type"], normalized, raw_row["mlkem_variant"], raw_row["operation"])
                    groups[key].append(row)

    statistics_rows = [_statistics_row(key, groups[key]) for key in sorted(groups)]
    if overwrite:
        for path in expected:
            if path.exists():
                path.unlink()
    with (output_dir / "observations.csv").open("x", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=OBSERVATION_COLUMNS)
        writer.writeheader()
        writer.writerows(observations)
    with (output_dir / "benchmark_statistics.csv").open("x", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=STATISTICS_COLUMNS)
        writer.writeheader()
        writer.writerows(statistics_rows)

    manifest = {
        "schema_version": "1.0",
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "provenance": "DERIVED from validated data/raw only; raw files were not modified.",
        "normalization": {"NATIVE_HARDWARE": "REAL_HARDWARE"},
        "row_count": len(observations),
        "successful_measurement_count": sum(len(rows) for rows in groups.values()),
        "statistics_group_count": len(statistics_rows),
        "source_files": source_files,
        "measurement_type_counts": dict(sorted(Counter(row["normalized_measurement_type"] for row in observations).items())),
        "limitations": [
            "Timing values from different execution types must not be pooled as equivalent hardware performance.",
            "NATIVE_SOFTWARE x86 configurations share one physical host and are execution configurations, not independent devices.",
            "EMULATED results are not measurements of physical RISC-V hardware.",
            "memory_bytes is a process-level measurement, not per-operation memory allocation.",
        ],
    }
    with (output_dir / "admission_manifest.json").open("x", encoding="utf-8") as handle:
        json.dump(manifest, handle, indent=2)
        handle.write("\n")
    return manifest
