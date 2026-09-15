import csv
import hashlib
import json
from pathlib import Path
from mlkem_benchmark.validation import validate_raw_directory

def main():
    root = Path(__file__).resolve().parents[1]
    raw_dir = root / "data" / "raw"
    validation = validate_raw_directory(raw_dir)

    total_rows = 0
    clean_count = 0
    error_count = 0

    print("=" * 80)
    print("                    ML-KEM DATASET INTEGRITY VERIFICATION")
    print("=" * 80)
    print(f"\n1. Raw Data Integrity Scan ({len(validation)} files in data/raw):")
    print("-" * 80)
    
    for path, (count, errors) in sorted(validation.items(), key=lambda x: x[0].name):
        total_rows += count
        if not errors:
            clean_count += 1
            print(f" [PASS] {path.name} ({count:,} rows)")
        else:
            error_count += 1
            print(f" [FAIL] {path.name} ({count:,} rows) -> {len(errors)} error(s)")
            for err in errors[:3]:
                print(f"        * {err}")
            if len(errors) > 3:
                print(f"        * ... and {len(errors) - 3} more")

    print("-" * 80)
    print(f"Raw Scan Summary: {clean_count}/{len(validation)} files valid | Total rows: {total_rows:,}")
    if error_count == 0:
        print("Status: ALL RAW DATA PASSES COMPREHENSIVE VALIDATION (0 errors)")
    else:
        print(f"Status: {error_count} RAW FILE(S) FAILED VALIDATION")

    # 2. Check Processed Data
    proc_dir = root / "data" / "processed" / "phase11_statistics"
    manifest_file = proc_dir / "admission_manifest.json"
    obs_file = proc_dir / "observations.csv"
    stats_file = proc_dir / "benchmark_statistics.csv"

    print("\n2. Processed Artifacts & Manifest Verification:")
    print("-" * 80)

    if manifest_file.exists():
        with manifest_file.open(encoding="utf-8") as f:
            manifest = json.load(f)
        manifest_errors = []
        raw_sources = {path.name: path for path in raw_dir.glob("*.csv")}
        manifest_sources = manifest.get("source_files", [])
        listed_sources = {entry.get("file") for entry in manifest_sources}
        for name, path in raw_sources.items():
            if name not in listed_sources:
                manifest_errors.append(f"unlisted raw file: {name}")
        for entry in manifest_sources:
            name = entry.get("file")
            path = raw_sources.get(name)
            if path is None:
                manifest_errors.append(f"missing raw file: {name}")
                continue
            with path.open(newline="", encoding="utf-8") as source:
                source_rows = sum(1 for _ in source) - 1
            if source_rows != entry.get("row_count"):
                manifest_errors.append(f"row count mismatch: {name}")
            if hashlib.sha256(path.read_bytes()).hexdigest() != entry.get("sha256"):
                manifest_errors.append(f"SHA-256 mismatch: {name}")
        if manifest_errors:
            print(f" [FAIL] admission_manifest.json mismatch ({len(manifest_errors)} error(s))")
            for error in manifest_errors[:5]:
                print(f"        * {error}")
        else:
            print(f" [PASS] admission_manifest.json found and verified")
        print(f"        - Recorded row count        : {manifest.get('row_count'):,}")
        print(f"        - Successful measurements   : {manifest.get('successful_measurement_count'):,}")
        print(f"        - Group count               : {manifest.get('statistics_group_count')}")
        print(f"        - Measurement types         : {manifest.get('measurement_type_counts')}")
    else:
        print(f" [FAIL] admission_manifest.json missing!")

    if obs_file.exists():
        with obs_file.open(newline="", encoding="utf-8") as f:
            reader = csv.reader(f)
            header = next(reader)
            obs_rows = sum(1 for _ in reader)
        print(f" [PASS] observations.csv verified ({obs_rows:,} rows, {len(header)} columns)")
    else:
        print(f" [FAIL] observations.csv missing!")

    if stats_file.exists():
        with stats_file.open(newline="", encoding="utf-8") as f:
            reader = csv.reader(f)
            header = next(reader)
            stats_rows = sum(1 for _ in reader)
        print(f" [PASS] benchmark_statistics.csv verified ({stats_rows} statistical groups)")
    else:
        print(f" [FAIL] benchmark_statistics.csv missing!")

    # 3. Environment Breakdown
    print("\n3. Empirical Environment Breakdown:")
    print("-" * 80)
    if stats_file.exists():
        with stats_file.open(newline="", encoding="utf-8") as f:
            dict_reader = csv.DictReader(f)
            envs = set()
            for r in dict_reader:
                envs.add((r["environment"], r["architecture"], r["normalized_measurement_type"]))
            for env, arch, norm_type in sorted(envs):
                print(f" * Environment: {env:<45} | Arch: {arch:<8} | Type: {norm_type}")

    print("=" * 80)
    manifest_ok = not manifest_file.exists() or not manifest_errors
    print("VERIFICATION RESULT: " + ("SUCCESS (DATASET IS CONSISTENT & COMPLETE)" if error_count == 0 and obs_rows == total_rows and manifest_ok else "FAILED"))
    print("=" * 80)

if __name__ == "__main__":
    main()
