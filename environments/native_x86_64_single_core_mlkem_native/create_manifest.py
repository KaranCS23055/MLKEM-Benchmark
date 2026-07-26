import csv, hashlib, json, sys
from datetime import datetime, timezone
from pathlib import Path

def main(raw_dir: Path, timestamp: str) -> int:
    pattern = f"native_x86_64_single_core_mlkem_native_mlkem_*_{timestamp}.csv"
    csv_files = sorted(raw_dir.glob(pattern))
    if not csv_files:
        raise SystemExit(f"No files matching {pattern}")

    metadata_dir = raw_dir.parent / "metadata"
    metadata_dir.mkdir(parents=True, exist_ok=True)
    manifest_path = metadata_dir / f"native_x86_64_single_core_mlkem_native_{timestamp}_manifest.json"
    sha256_path = metadata_dir / f"native_x86_64_single_core_mlkem_native_{timestamp}_SHA256SUMS.txt"

    sha256s, total_rows, sample = [], 0, {}
    for fpath in csv_files:
        h = hashlib.sha256(fpath.read_bytes()).hexdigest()
        sha256s.append(f"{h}  {fpath.name}")
        with fpath.open(newline="", encoding="utf-8") as f:
            rows = list(csv.DictReader(f))
        total_rows += len(rows)
        if rows and not sample: sample = rows[0]

    manifest = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "timestamp_token": timestamp,
        "raw_files": [f.name for f in csv_files],
        "total_rows": total_rows,
        "environment": sample.get("environment"),
        "measurement_type": sample.get("measurement_type"),
        "architecture": sample.get("architecture"),
        "processor": sample.get("processor"),
        "cpu_cores": 1,
        "implementation": {"name": "mlkem-native", "version": sample.get("implementation_version"), "commit": "0ba906cb14b1c241476134d7403a811b382ca498"},
        "os": sample.get("os"),
        "note": "Single-Core constrained x86-64 native benchmark run using taskset -c 0 under WSL2 Ubuntu."
    }

    sha256_path.write_text("\n".join(sha256s) + "\n", encoding="utf-8")
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(f"Manifest written: {manifest_path}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main(Path(sys.argv[1]), sys.argv[2]))
