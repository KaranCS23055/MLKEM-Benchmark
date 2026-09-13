"""Dependency-free validation for Android native raw ML-KEM benchmark CSVs."""

import csv
import sys
from collections import Counter
from pathlib import Path

COLUMNS = [
    "experiment_id", "run_id", "timestamp", "environment", "measurement_type",
    "architecture", "processor", "cpu_cores", "ram_mb", "os", "compiler",
    "compiler_version", "optimization_flags", "implementation",
    "implementation_version", "mlkem_variant", "operation", "iteration",
    "execution_time_ns", "memory_bytes", "success", "error_message",
]
OPERATIONS = {"keygen", "encapsulation", "decapsulation"}


def main(path: Path, expected_iterations: int, expected_variant: str) -> int:
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames != COLUMNS:
            raise SystemExit("Invalid CSV schema")
        rows = list(reader)
    if len(rows) != expected_iterations * 3:
        raise SystemExit(f"Expected {expected_iterations * 3} rows, found {len(rows)}")
    if expected_variant not in {"ML-KEM-512", "ML-KEM-768", "ML-KEM-1024"}:
        raise SystemExit(f"Unsupported expected variant: {expected_variant}")
    identities: set[tuple[str, str, str]] = set()
    counts: Counter[str] = Counter()
    experiment_ids: set[str] = set()
    run_ids: set[str] = set()
    for number, row in enumerate(rows, start=2):
        if any(not row[column] for column in COLUMNS[:-1]):
            raise SystemExit(f"Row {number}: missing required value")
        if row["measurement_type"] not in {"REAL_HARDWARE", "NATIVE_HARDWARE"}:
            raise SystemExit(
                f"Row {number}: measurement_type must be REAL_HARDWARE (or legacy "
                f"NATIVE_HARDWARE for admitted historical files); "
                f"got {row['measurement_type']!r}"
            )
        if row["architecture"] != "aarch64":
            raise SystemExit(f"Row {number}: not an ARM64 measurement")
        if row["mlkem_variant"] != expected_variant:
            raise SystemExit(
                f"Row {number}: expected {expected_variant}, found {row['mlkem_variant']}"
            )
        if row["operation"] not in OPERATIONS:
            raise SystemExit(f"Row {number}: invalid variant or operation")
        if row["success"] != "True" or row["error_message"]:
            raise SystemExit(f"Row {number}: cryptographic operation failed")
        if int(row["execution_time_ns"]) <= 0 or int(row["memory_bytes"]) <= 0:
            raise SystemExit(f"Row {number}: invalid timing or memory")
        identity = (row["operation"], row["iteration"], row["mlkem_variant"])
        if identity in identities:
            raise SystemExit(f"Row {number}: duplicate operation/iteration identity")
        identities.add(identity)
        counts[row["operation"]] += 1
        experiment_ids.add(row["experiment_id"])
        run_ids.add(row["run_id"])
    if set(counts) != OPERATIONS or any(counts[operation] != expected_iterations for operation in OPERATIONS):
        raise SystemExit(f"Incorrect per-operation counts: {dict(counts)}")
    if len(experiment_ids) != 1 or len(run_ids) != 1:
        raise SystemExit("CSV must contain exactly one experiment_id and one run_id")
    mtype = rows[0]["measurement_type"] if rows else "unknown"
    print(f"VALID: {path.name}; {len(rows)} {mtype} {expected_variant} measurements")
    return 0


if __name__ == "__main__":
    if len(sys.argv) != 4:
        raise SystemExit("Usage: validate_android_csv.py CSV ITERATIONS ML-KEM-VARIANT")
    raise SystemExit(main(Path(sys.argv[1]), int(sys.argv[2]), sys.argv[3]))
