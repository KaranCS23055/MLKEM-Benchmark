"""Run ML-KEM benchmarks on this laptop and write results to data/raw/.

Usage:
    python scripts/run_laptop_benchmark.py                     # both multi + single core
    python scripts/run_laptop_benchmark.py --config <path>     # specific config only
    python scripts/run_laptop_benchmark.py --multi-only        # skip single-core run
    python scripts/run_laptop_benchmark.py --single-only       # skip multi-core run
"""

from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

# Ensure the src/ package is importable when run directly.
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from mlkem_benchmark.core import load_config, run_benchmark  # noqa: E402


MULTI_CORE_CONFIG = ROOT / "configs" / "native_x86_64_i7_1255u_windows.json"
SINGLE_CORE_CONFIG = ROOT / "configs" / "native_x86_64_i7_1255u_windows_single_core.json"
RAW_DIR = ROOT / "data" / "raw"
METADATA_DIR = ROOT / "data" / "metadata"


def _run_one(config_path: Path) -> None:
    print(f"\n{'='*70}")
    print(f"  Loading config: {config_path.name}")
    config = load_config(config_path)
    env_name = config.environment["name"]
    total_ops = len(config.variants) * len(config.operations) * config.iterations
    print(f"  Environment  : {env_name}")
    print(f"  Variants     : {', '.join(config.variants)}")
    print(f"  Operations   : {', '.join(config.operations)}")
    print(f"  Iterations   : {config.iterations}")
    print(f"  Total rows   : {total_ops}")
    affinity = config.environment.get("cpu_affinity_mask")
    if affinity:
        print(f"  CPU affinity : {affinity:#x} (single logical core)")
    else:
        print(f"  CPU affinity : not set (OS-scheduled, all cores)")
    print(f"{'='*70}")
    print("  Starting benchmark … (this may take several minutes)")

    t0 = time.perf_counter()
    raw_path, manifest_path, row_count = run_benchmark(config, RAW_DIR, METADATA_DIR)
    elapsed = time.perf_counter() - t0

    print(f"\n  ✓ Done in {elapsed:.1f}s")
    print(f"  ✓ Rows written    : {row_count}")
    print(f"  ✓ Raw CSV         : {raw_path.relative_to(ROOT)}")
    print(f"  ✓ Manifest JSON   : {manifest_path.relative_to(ROOT)}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Run Intel i7-1255U ML-KEM benchmarks.")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--multi-only", action="store_true", help="Run only the multi-core benchmark.")
    group.add_argument("--single-only", action="store_true", help="Run only the single-core benchmark.")
    group.add_argument("--config", type=Path, metavar="PATH", help="Run a specific config JSON.")
    args = parser.parse_args()

    print("\n" + "="*70)
    print("  ML-KEM Benchmark -- Intel i7-1255U / Windows 11 Native")
    print("="*70)

    if args.config:
        _run_one(args.config)
    elif args.multi_only:
        _run_one(MULTI_CORE_CONFIG)
    elif args.single_only:
        _run_one(SINGLE_CORE_CONFIG)
    else:
        # Default: run both (multi-core first, then single-core)
        _run_one(MULTI_CORE_CONFIG)
        _run_one(SINGLE_CORE_CONFIG)

    print("\n" + "="*70)
    print("  All benchmarks complete!")
    print("  Next step -- regenerate the processed dataset:")
    print("    .venv\\Scripts\\python.exe analysis\\build_processed_dataset.py --overwrite")
    print("="*70 + "\n")


if __name__ == "__main__":
    main()
