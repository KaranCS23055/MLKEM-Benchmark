"""CLI entry point for creating the Phase 11 derived benchmark dataset."""

from __future__ import annotations

import argparse
from pathlib import Path

from mlkem_benchmark.processing import build_processed_dataset


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser(description="Validate ML-KEM raw data and build derived statistics.")
    parser.add_argument("--raw-dir", type=Path, default=root / "data" / "raw")
    parser.add_argument("--output-dir", type=Path, default=root / "data" / "processed" / "phase11_statistics")
    parser.add_argument("--overwrite", action="store_true", help="Replace only existing derived output files.")
    args = parser.parse_args()
    manifest = build_processed_dataset(args.raw_dir, args.output_dir, overwrite=args.overwrite)
    print(f"Wrote {manifest['row_count']} observations and {manifest['statistics_group_count']} statistic groups to {args.output_dir}")


if __name__ == "__main__":
    main()
