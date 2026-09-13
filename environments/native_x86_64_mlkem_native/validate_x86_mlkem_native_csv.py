"""Dependency-free validator for x86-64 mlkem-native raw benchmark CSVs.

Usage:
    python3 validate_x86_mlkem_native_csv.py CSV ITERATIONS ML-KEM-VARIANT

Checks:
  - Schema matches the 22-column REQUIRED_COLUMNS format.
  - measurement_type == NATIVE_SOFTWARE.
  - architecture == x86_64.
  - implementation == mlkem-native.
  - Exact expected row count (iterations * 3 operations).
  - All operations succeeded (success == True).
  - Positive timing and memory values for every row.
  - No duplicate operation/iteration identities within the file.
  - Exactly one experiment_id and one run_id per file.
"""

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
            raise SystemExit(
                f"FAIL: CSV schema mismatch.\n"
                f"  Expected: {COLUMNS}\n"
                f"  Got:      {reader.fieldnames}"
            )
        rows = list(reader)

    expected_rows = expected_iterations * 3
    if len(rows) != expected_rows:
        raise SystemExit(
            f"FAIL: Expected {expected_rows} rows, found {len(rows)}"
        )
    if expected_variant not in {"ML-KEM-512", "ML-KEM-768", "ML-KEM-1024"}:
        raise SystemExit(f"FAIL: Unsupported expected variant: {expected_variant}")

    identities: set[tuple[str, str, str]] = set()
    counts: Counter[str] = Counter()
    experiment_ids: set[str] = set()
    run_ids: set[str] = set()

    for number, row in enumerate(rows, start=2):
        # Required non-empty fields (all except error_message)
        for col in COLUMNS[:-1]:
            if not row[col].strip():
                raise SystemExit(f"FAIL row {number}: missing required value '{col}'")

        if row["measurement_type"] != "NATIVE_SOFTWARE":
            raise SystemExit(
                f"FAIL row {number}: measurement_type is '{row['measurement_type']}', "
                f"expected NATIVE_SOFTWARE"
            )
        if row["architecture"] != "x86_64":
            raise SystemExit(
                f"FAIL row {number}: architecture is '{row['architecture']}', "
                f"expected x86_64"
            )
        if row["implementation"] != "mlkem-native":
            raise SystemExit(
                f"FAIL row {number}: implementation is '{row['implementation']}', "
                f"expected mlkem-native"
            )
        if row["mlkem_variant"] != expected_variant:
            raise SystemExit(
                f"FAIL row {number}: expected {expected_variant}, "
                f"found {row['mlkem_variant']}"
            )
        if row["operation"] not in OPERATIONS:
            raise SystemExit(
                f"FAIL row {number}: unsupported operation '{row['operation']}'"
            )
        if row["success"] != "True" or row["error_message"].strip():
            raise SystemExit(
                f"FAIL row {number}: cryptographic operation did not succeed "
                f"(success={row['success']!r}, error={row['error_message']!r})"
            )
        if int(row["execution_time_ns"]) <= 0 or int(row["memory_bytes"]) <= 0:
            raise SystemExit(
                f"FAIL row {number}: non-positive timing or memory value"
            )

        identity = (row["operation"], row["iteration"], row["mlkem_variant"])
        if identity in identities:
            raise SystemExit(
                f"FAIL row {number}: duplicate operation/iteration identity {identity}"
            )
        identities.add(identity)
        counts[row["operation"]] += 1
        experiment_ids.add(row["experiment_id"])
        run_ids.add(row["run_id"])

    if set(counts) != OPERATIONS or any(
        counts[op] != expected_iterations for op in OPERATIONS
    ):
        raise SystemExit(f"FAIL: incorrect per-operation counts: {dict(counts)}")
    if len(experiment_ids) != 1 or len(run_ids) != 1:
        raise SystemExit(
            "FAIL: CSV must contain exactly one experiment_id and one run_id"
        )

    processor = rows[0]["processor"] if rows else "unknown"
    impl_ver = rows[0]["implementation_version"] if rows else "unknown"
    print(
        f"VALID: {path.name}; {len(rows)} NATIVE_SOFTWARE {expected_variant} "
        f"measurements; processor={processor!r}; impl_ver={impl_ver!r}"
    )
    return 0


if __name__ == "__main__":
    if len(sys.argv) != 4:
        raise SystemExit(
            "Usage: validate_x86_mlkem_native_csv.py CSV ITERATIONS ML-KEM-VARIANT"
        )
    raise SystemExit(main(Path(sys.argv[1]), int(sys.argv[2]), sys.argv[3]))
