from __future__ import annotations

import csv
import json
import tempfile
import unittest
from pathlib import Path

from mlkem_benchmark.core import REQUIRED_COLUMNS
from mlkem_benchmark.processing import build_processed_dataset


def _row(*, iteration: int, timing: int) -> dict[str, str]:
    row = {column: "" for column in REQUIRED_COLUMNS}
    row.update({
        "experiment_id": "experiment", "run_id": "run-a", "timestamp": f"2026-08-13T00:00:0{iteration}+00:00",
        "environment": "test-device", "measurement_type": "NATIVE_HARDWARE", "architecture": "aarch64",
        "processor": "test", "cpu_cores": "1", "ram_mb": "1", "os": "test", "compiler": "test",
        "compiler_version": "1", "optimization_flags": "-O3", "implementation": "mlkem-native",
        "implementation_version": "v1", "mlkem_variant": "ML-KEM-512", "operation": "keygen",
        "iteration": str(iteration), "execution_time_ns": str(timing), "memory_bytes": "100", "success": "True",
    })
    return row


class Phase11ProcessingTests(unittest.TestCase):
    def test_builds_normalized_observations_statistics_and_manifest(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            raw = root / "raw"
            raw.mkdir()
            with (raw / "input.csv").open("w", newline="", encoding="utf-8") as handle:
                writer = csv.DictWriter(handle, fieldnames=REQUIRED_COLUMNS)
                writer.writeheader()
                writer.writerows([_row(iteration=1, timing=100), _row(iteration=2, timing=300)])
            output = root / "processed"
            manifest = build_processed_dataset(raw, output)
            self.assertEqual(manifest["row_count"], 2)
            self.assertEqual(manifest["statistics_group_count"], 1)
            with (output / "observations.csv").open(newline="", encoding="utf-8") as handle:
                observations = list(csv.DictReader(handle))
            self.assertEqual(observations[0]["measurement_type"], "NATIVE_HARDWARE")
            self.assertEqual(observations[0]["normalized_measurement_type"], "REAL_HARDWARE")
            with (output / "benchmark_statistics.csv").open(newline="", encoding="utf-8") as handle:
                statistic = next(csv.DictReader(handle))
            self.assertEqual(statistic["count"], "2")
            self.assertEqual(float(statistic["mean_execution_time_ns"]), 200.0)
            stored_manifest = json.loads((output / "admission_manifest.json").read_text(encoding="utf-8"))
            self.assertEqual(stored_manifest["measurement_type_counts"], {"REAL_HARDWARE": 2})

    def test_refuses_overwrite_and_invalid_raw_data(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            raw = root / "raw"
            raw.mkdir()
            with (raw / "input.csv").open("w", newline="", encoding="utf-8") as handle:
                writer = csv.DictWriter(handle, fieldnames=REQUIRED_COLUMNS)
                writer.writeheader()
                writer.writerow(_row(iteration=1, timing=100))
            output = root / "processed"
            build_processed_dataset(raw, output)
            with self.assertRaises(FileExistsError):
                build_processed_dataset(raw, output)
            (raw / "broken.csv").write_text("not,a,valid,header\n", encoding="utf-8")
            with self.assertRaises(ValueError):
                build_processed_dataset(raw, root / "other-output")


if __name__ == "__main__":
    unittest.main()
