"""Create a SHA-256 manifest for a completed x86-64 mlkem-native benchmark run.

Usage (from project root, after the benchmark has written its CSVs):
    python3 environments/native_x86_64_mlkem_native/create_manifest.py \\
        data/raw TIMESTAMP

TIMESTAMP must match the timestamp token embedded in the CSV filenames
(e.g. 20260813T090000Z).

Writes:
  data/metadata/native_x86_64_mlkem_native_<TIMESTAMP>_manifest.json
  data/metadata/native_x86_64_mlkem_native_<TIMESTAMP>_SHA256SUMS.txt
"""

import csv
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def main(raw_dir: Path, timestamp: str) -> int:
    pattern = f"native_x86_64_mlkem_native_mlkem_*_{timestamp}.csv"
    csv_files = sorted(raw_dir.glob(pattern))
    if not csv_files:
        raise SystemExit(
            f"No files matching {pattern!r} found in {raw_dir}"
        )

    metadata_dir = raw_dir.parent / "metadata"
    metadata_dir.mkdir(parents=True, exist_ok=True)

    manifest_path = metadata_dir / f"native_x86_64_mlkem_native_{timestamp}_manifest.json"
    sha256_path   = metadata_dir / f"native_x86_64_mlkem_native_{timestamp}_SHA256SUMS.txt"

    if manifest_path.exists() or sha256_path.exists():
        raise SystemExit(f"Manifest already exists for timestamp {timestamp}")

    total_rows = 0
    sha256s: list[str] = []
    sample_meta: dict = {}

    for csv_path in csv_files:
        digest = sha256_file(csv_path)
        sha256s.append(f"{digest}  {csv_path.name}")
        with csv_path.open(newline="", encoding="utf-8") as f:
            rows = list(csv.DictReader(f))
        total_rows += len(rows)
        if rows and not sample_meta:
            r = rows[0]
            sample_meta = {
                "environment":          r["environment"],
                "measurement_type":     r["measurement_type"],
                "architecture":         r["architecture"],
                "processor":            r["processor"],
                "implementation":       r["implementation"],
                "implementation_version": r["implementation_version"],
                "compiler":             r["compiler"],
                "compiler_version":     r["compiler_version"],
                "optimization_flags":   r["optimization_flags"],
                "os":                   r["os"],
            }

    manifest = {
        "generated_at":      datetime.now(timezone.utc).isoformat(),
        "timestamp_token":   timestamp,
        "raw_files":         [f.name for f in csv_files],
        "total_rows":        total_rows,
        "environment":       sample_meta.get("environment"),
        "measurement_type":  sample_meta.get("measurement_type"),
        "architecture":      sample_meta.get("architecture"),
        "processor":         sample_meta.get("processor"),
        "implementation": {
            "name":    sample_meta.get("implementation"),
            "version": sample_meta.get("implementation_version"),
            "commit":  "0ba906cb14b1c241476134d7403a811b382ca498",
            "backend": "portable C",
        },
        "compiler": {
            "name":              sample_meta.get("compiler"),
            "version":           sample_meta.get("compiler_version"),
            "optimization_flags": sample_meta.get("optimization_flags"),
        },
        "os":          sample_meta.get("os"),
        "host_layer":  "WSL2 Ubuntu (Hyper-V) on Windows 11 x86-64 host",
        "timing_definition": (
            "CLOCK_MONOTONIC elapsed time around the specified ML-KEM operation only; "
            "setup (keypair generation for enc/dec) is excluded from timing."
        ),
        "memory_definition": (
            "Process maximum resident-set-size high-water mark from getrusage "
            "(Linux reports KiB; converted to bytes)."
        ),
        "integrity_sha256": f"native_x86_64_mlkem_native_{timestamp}_SHA256SUMS.txt",
        "note": (
            "x86-64 standardization run. Uses mlkem-native v1.2.0 portable-C backend "
            "compiled with GCC under WSL2 Ubuntu on the same AMD physical CPU as the "
            "pqcrypto reference run. Allows direct implementation-matched comparison "
            "with ARM64 and RISC-V mlkem-native runs."
        ),
    }

    sha256_path.write_text("\n".join(sha256s) + "\n", encoding="utf-8")
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    print(f"Written: {manifest_path}")
    print(f"Written: {sha256_path}")
    print(f"Total rows: {total_rows}")
    return 0


if __name__ == "__main__":
    if len(sys.argv) != 3:
        raise SystemExit("Usage: create_manifest.py RAW_DIR TIMESTAMP")
    raise SystemExit(main(Path(sys.argv[1]), sys.argv[2]))
