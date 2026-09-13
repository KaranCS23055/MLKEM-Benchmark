import csv, sys
from pathlib import Path

COLUMNS = [
    "experiment_id", "run_id", "timestamp", "environment", "measurement_type",
    "architecture", "processor", "cpu_cores", "ram_mb", "os", "compiler",
    "compiler_version", "optimization_flags", "implementation",
    "implementation_version", "mlkem_variant", "operation", "iteration",
    "execution_time_ns", "memory_bytes", "success", "error_message"
]

def main(path: Path, expected_iterations: int, expected_variant: str) -> int:
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames != COLUMNS:
            raise SystemExit("Schema mismatch")
        rows = list(reader)

    if len(rows) != expected_iterations * 3:
        raise SystemExit(f"Expected {expected_iterations*3} rows, got {len(rows)}")

    for r in rows:
        if r["architecture"] != "x86":
            raise SystemExit(f"Invalid arch: {r['architecture']}")
        if r["measurement_type"] != "NATIVE_SOFTWARE":
            raise SystemExit("Invalid measurement_type")
        if r["success"] != "True":
            raise SystemExit("Crypto operation failed")

    print(f"VALID: {path.name}; {len(rows)} 32-bit x86 measurements; processor={rows[0]['processor']!r}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main(Path(sys.argv[1]), int(sys.argv[2]), sys.argv[3]))
