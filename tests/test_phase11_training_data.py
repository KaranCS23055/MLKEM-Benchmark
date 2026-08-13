from __future__ import annotations

import csv
import tempfile
import unittest
from pathlib import Path

from ml.build_training_dataset import build_training_dataset


STAT_COLUMNS = [
    "environment", "architecture", "raw_measurement_type", "normalized_measurement_type", "mlkem_variant", "operation", "count",
    "mean_execution_time_ns", "median_execution_time_ns", "min_execution_time_ns", "max_execution_time_ns", "stddev_execution_time_ns",
    "coefficient_of_variation", "p95_execution_time_ns", "p99_execution_time_ns", "mean_memory_bytes", "median_memory_bytes", "throughput_ops_per_second",
]


class Phase11TrainingDataTests(unittest.TestCase):
    def test_creates_candidates_and_one_recommendation_per_profile_environment(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            statistics = root / "statistics.csv"
            rows = []
            for variant, timing in (("ML-KEM-512", 100), ("ML-KEM-768", 200), ("ML-KEM-1024", 300)):
                for operation in ("keygen", "encapsulation", "decapsulation"):
                    rows.append({
                        "environment": "test", "architecture": "x86_64", "raw_measurement_type": "NATIVE_SOFTWARE",
                        "normalized_measurement_type": "NATIVE_SOFTWARE", "mlkem_variant": variant, "operation": operation,
                        "count": "1000", "mean_execution_time_ns": str(timing), "median_execution_time_ns": str(timing),
                        "min_execution_time_ns": str(timing), "max_execution_time_ns": str(timing), "stddev_execution_time_ns": "0",
                        "coefficient_of_variation": "0", "p95_execution_time_ns": str(timing), "p99_execution_time_ns": str(timing),
                        "mean_memory_bytes": "100", "median_memory_bytes": "100", "throughput_ops_per_second": "1",
                    })
            with statistics.open("w", newline="", encoding="utf-8") as handle:
                writer = csv.DictWriter(handle, fieldnames=STAT_COLUMNS)
                writer.writeheader()
                writer.writerows(rows)
            output = root / "candidates.csv"
            manifest = build_training_dataset(statistics, output)
            self.assertEqual(manifest["candidate_count"], 18)
            self.assertEqual(manifest["recommended_count"], 6)
            with output.open(newline="", encoding="utf-8") as handle:
                candidates = list(csv.DictReader(handle))
            self.assertEqual(sum(row["recommended"] == "True" for row in candidates), 6)
            self.assertTrue(all(row["provenance"].startswith("DERIVED") for row in candidates))


if __name__ == "__main__":
    unittest.main()
