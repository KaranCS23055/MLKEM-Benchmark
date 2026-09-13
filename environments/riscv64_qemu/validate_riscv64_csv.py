"""Strict validation for RISC-V Linux QEMU ML-KEM raw benchmark CSVs."""

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
    if expected_variant not in {"ML-KEM-512", "ML-KEM-768", "ML-KEM-1024"}:
        raise SystemExit("Unsupported expected variant")
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames != COLUMNS:
            raise SystemExit("Invalid CSV schema")
        rows = list(reader)
    if len(rows) != expected_iterations * 3:
        raise SystemExit(f"Expected {expected_iterations * 3} rows, found {len(rows)}")
    counts: Counter[str] = Counter()
    identities: set[tuple[str, str]] = set()
    for number, row in enumerate(rows, 2):
        if any(not row[column] for column in COLUMNS[:-1]):
            raise SystemExit(f"Row {number}: missing required value")
        if row["measurement_type"] != "EMULATED" or row["architecture"] != "riscv64":
            raise SystemExit(f"Row {number}: not an EMULATED RISC-V measurement")
        if row["mlkem_variant"] != expected_variant or row["operation"] not in OPERATIONS:
            raise SystemExit(f"Row {number}: incorrect variant or operation")
        if row["success"] != "True" or row["error_message"]:
            raise SystemExit(f"Row {number}: cryptographic operation failed")
        if int(row["execution_time_ns"]) <= 0 or int(row["memory_bytes"]) <= 0:
            raise SystemExit(f"Row {number}: invalid timing or memory")
        identity = (row["operation"], row["iteration"])
        if identity in identities:
            raise SystemExit(f"Row {number}: duplicate operation/iteration")
        identities.add(identity)
        counts[row["operation"]] += 1
    if set(counts) != OPERATIONS or any(counts[x] != expected_iterations for x in OPERATIONS):
        raise SystemExit("Incorrect operation counts")
    print(f"VALID: {path.name}; {len(rows)} EMULATED RISC-V {expected_variant} measurements")
    return 0


if __name__ == "__main__":
    if len(sys.argv) != 4:
        raise SystemExit("Usage: validate_riscv64_csv.py CSV ITERATIONS ML-KEM-VARIANT")
    raise SystemExit(main(Path(sys.argv[1]), int(sys.argv[2]), sys.argv[3]))
