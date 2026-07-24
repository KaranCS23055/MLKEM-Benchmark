"""CSV validation for ML-KEM benchmark records."""

from __future__ import annotations

import csv
from collections import defaultdict
from datetime import datetime
from pathlib import Path

from .core import REQUIRED_COLUMNS, VALID_OPERATIONS, VARIANT_MODULES

TEXT_FIELDS = (
    "experiment_id", "run_id", "timestamp", "environment", "measurement_type",
    "architecture", "processor", "cpu_cores", "ram_mb", "os", "compiler",
    "compiler_version", "optimization_flags", "implementation",
    "implementation_version", "mlkem_variant", "operation", "iteration", "success",
)

def validate_csv(path: Path) -> tuple[int, list[str]]:
    """Return row count and validation errors for a raw benchmark CSV."""
    errors: list[str] = []
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames != REQUIRED_COLUMNS:
            return 0, ["CSV header does not match the required schema"]
        rows = list(reader)

    if not rows:
        errors.append("CSV contains no measurements")
    seen: set[tuple[str, str, str, str, str]] = set()
    for row_number, row in enumerate(rows, start=2):
        prefix = f"row {row_number}"
        for field in TEXT_FIELDS:
            if not row[field].strip():
                errors.append(f"{prefix}: missing required value {field}")
        try:
            datetime.fromisoformat(row["timestamp"])
        except ValueError:
            errors.append(f"{prefix}: invalid ISO-8601 timestamp")
        if row["mlkem_variant"] not in VARIANT_MODULES:
            errors.append(f"{prefix}: unsupported variant")
        if row["operation"] not in VALID_OPERATIONS:
            errors.append(f"{prefix}: unsupported operation")
        try:
            iteration = int(row["iteration"])
            if iteration < 1:
                raise ValueError
        except ValueError:
            errors.append(f"{prefix}: invalid iteration")
        if row["success"] not in {"True", "False"}:
            errors.append(f"{prefix}: success must be True or False")
        if row["success"] == "True":
            try:
                if int(row["execution_time_ns"]) <= 0:
                    raise ValueError
                if int(row["memory_bytes"]) <= 0:
                    raise ValueError
            except (TypeError, ValueError):
                errors.append(f"{prefix}: successful row needs positive timing and memory")
            if row["error_message"]:
                errors.append(f"{prefix}: successful row has an error message")
        elif not row["error_message"]:
            errors.append(f"{prefix}: failed row must include an error message")
        if row["operation"] == "decapsulation" and row["success"] != "True":
            errors.append(f"{prefix}: failed cryptographic verification/decapsulation")
        key = (row["run_id"], row["mlkem_variant"], row["operation"], row["iteration"], row["timestamp"])
        if key in seen:
            errors.append(f"{prefix}: duplicate measurement identity")
        seen.add(key)
    return len(rows), errors


def validate_raw_directory(raw_dir: Path) -> dict[Path, tuple[int, list[str]]]:
    """Validate every raw CSV and detect experiment IDs reused across files."""
    results = {path: validate_csv(path) for path in sorted(raw_dir.glob("*.csv"))}
    experiment_files: dict[str, set[Path]] = defaultdict(set)
    for path in results:
        with path.open(newline="", encoding="utf-8") as handle:
            for row in csv.DictReader(handle):
                if row.get("experiment_id"):
                    experiment_files[row["experiment_id"]].add(path)
    for experiment_id, paths in experiment_files.items():
        if len(paths) > 1:
            message = f"duplicate experiment_id across raw files: {experiment_id}"
            for path in paths:
                results[path][1].append(message)
    return results
