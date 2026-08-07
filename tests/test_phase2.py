from __future__ import annotations

import csv
import tempfile
import unittest
from pathlib import Path

from pqcrypto.kem import ml_kem_1024, ml_kem_512, ml_kem_768

from mlkem_benchmark.core import REQUIRED_COLUMNS, load_config
from mlkem_benchmark.calibration import calibrate_csv
from mlkem_benchmark.summary import summarize_csv
from mlkem_benchmark.validation import validate_csv, validate_raw_directory


class Phase2Tests(unittest.TestCase):
    def _get_config_path(self, name: str) -> Path:
        root = Path(__file__).resolve().parents[1]
        p = root / "configs" / name
        if p.exists():
            return p
        return root / "data" / "archive" / "historical_pqcrypto_reference" / "configs" / name

    def test_config_parses(self) -> None:
        config = load_config(self._get_config_path("native_x86_64_100.json"))
        self.assertEqual(config.iterations, 100)
        self.assertEqual(set(config.variants), {"ML-KEM-512", "ML-KEM-768", "ML-KEM-1024"})

    def test_scaled_config_parses(self) -> None:
        config = load_config(self._get_config_path("native_x86_64_1000.json"))
        self.assertEqual(config.iterations, 1000)

    def test_controlled_config_parses(self) -> None:
        config = load_config(self._get_config_path("controlled_x86_64_two_cpu_100.json"))
        self.assertEqual(config.environment["cpu_affinity_mask"], 3)

    def test_shared_secret_verification_all_variants(self) -> None:
        for kem in (ml_kem_512, ml_kem_768, ml_kem_1024):
            public_key, secret_key = kem.generate_keypair()
            ciphertext, shared_secret = kem.encrypt(public_key)
            self.assertEqual(shared_secret, kem.decrypt(secret_key, ciphertext))

    def test_schema_validation_and_statistics(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "records.csv"
            row = {column: "" for column in REQUIRED_COLUMNS}
            row.update({
                "experiment_id": "experiment", "run_id": "run", "timestamp": "2026-08-12T00:00:00+00:00",
                "environment": "native", "measurement_type": "NATIVE_SOFTWARE", "architecture": "x86_64",
                "processor": "test", "cpu_cores": "1", "ram_mb": "1", "os": "test",
                "compiler": "N/A", "compiler_version": "N/A", "optimization_flags": "N/A",
                "implementation": "pqcrypto", "implementation_version": "0.4.0",
                "mlkem_variant": "ML-KEM-512", "operation": "keygen", "iteration": "1",
                "execution_time_ns": "100", "memory_bytes": "1", "success": "True",
            })
            with path.open("w", newline="", encoding="utf-8") as handle:
                writer = csv.DictWriter(handle, fieldnames=REQUIRED_COLUMNS)
                writer.writeheader()
                writer.writerow(row)
            count, errors = validate_csv(path)
            self.assertEqual(count, 1)
            self.assertEqual(errors, [])
            summary = summarize_csv(path)
            self.assertEqual(summary["groups"][0]["mean_ns"], 100)

    def test_validation_detects_missing_invalid_and_failed_decap(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "invalid.csv"
            row = {column: "x" for column in REQUIRED_COLUMNS}
            row.update({
                "experiment_id": "", "run_id": "run", "timestamp": "not-a-date",
                "mlkem_variant": "not-mlkem", "operation": "decapsulation",
                "iteration": "0", "execution_time_ns": "", "memory_bytes": "",
                "success": "False", "error_message": "",
            })
            with path.open("w", newline="", encoding="utf-8") as handle:
                writer = csv.DictWriter(handle, fieldnames=REQUIRED_COLUMNS)
                writer.writeheader()
                writer.writerow(row)
            _, errors = validate_csv(path)
            joined = "\n".join(errors)
            self.assertIn("missing required value experiment_id", joined)
            self.assertIn("unsupported variant", joined)
            self.assertIn("failed cryptographic verification/decapsulation", joined)

    def test_validation_detects_invalid_operation(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "invalid-operation.csv"
            row = {column: "" for column in REQUIRED_COLUMNS}
            row.update({
                "experiment_id": "experiment", "run_id": "run", "timestamp": "2026-08-12T00:00:00+00:00",
                "environment": "native", "measurement_type": "NATIVE_SOFTWARE", "architecture": "x86_64",
                "processor": "test", "cpu_cores": "1", "ram_mb": "1", "os": "test",
                "compiler": "N/A", "compiler_version": "N/A", "optimization_flags": "N/A",
                "implementation": "pqcrypto", "implementation_version": "0.4.0",
                "mlkem_variant": "ML-KEM-512", "operation": "wrong-operation", "iteration": "1",
                "execution_time_ns": "100", "memory_bytes": "1", "success": "True",
            })
            with path.open("w", newline="", encoding="utf-8") as handle:
                writer = csv.DictWriter(handle, fieldnames=REQUIRED_COLUMNS)
                writer.writeheader()
                writer.writerow(row)
            _, errors = validate_csv(path)
            self.assertIn("row 2: unsupported operation", errors)

    def test_duplicate_experiment_id_across_files(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            for name in ("a.csv", "b.csv"):
                row = {column: "" for column in REQUIRED_COLUMNS}
                row.update({
                    "experiment_id": "same", "run_id": name, "timestamp": "2026-08-12T00:00:00+00:00",
                    "environment": "native", "measurement_type": "NATIVE_SOFTWARE", "architecture": "x86_64",
                    "processor": "test", "cpu_cores": "1", "ram_mb": "1", "os": "test",
                    "compiler": "N/A", "compiler_version": "N/A", "optimization_flags": "N/A",
                    "implementation": "pqcrypto", "implementation_version": "0.4.0",
                    "mlkem_variant": "ML-KEM-512", "operation": "keygen", "iteration": "1",
                    "execution_time_ns": "100", "memory_bytes": "1", "success": "True",
                })
                with (root / name).open("w", newline="", encoding="utf-8") as handle:
                    writer = csv.DictWriter(handle, fieldnames=REQUIRED_COLUMNS)
                    writer.writeheader()
                    writer.writerow(row)
            results = validate_raw_directory(root)
            self.assertTrue(all(any("duplicate experiment_id" in error for error in errors) for _, errors in results.values()))

    def test_calibration_estimates_future_iterations(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "calibration.csv"
            rows = []
            for index, timing in enumerate((100, 110, 90, 100), start=1):
                row = {column: "" for column in REQUIRED_COLUMNS}
                row.update({
                    "experiment_id": "experiment", "run_id": "run", "timestamp": f"2026-08-12T00:00:0{index}+00:00",
                    "environment": "native", "measurement_type": "NATIVE_SOFTWARE", "architecture": "x86_64",
                    "processor": "test", "cpu_cores": "1", "ram_mb": "1", "os": "test",
                    "compiler": "N/A", "compiler_version": "N/A", "optimization_flags": "N/A",
                    "implementation": "pqcrypto", "implementation_version": "0.4.0",
                    "mlkem_variant": "ML-KEM-512", "operation": "keygen", "iteration": str(index),
                    "execution_time_ns": str(timing), "memory_bytes": "1", "success": "True",
                })
                rows.append(row)
            with path.open("w", newline="", encoding="utf-8") as handle:
                writer = csv.DictWriter(handle, fieldnames=REQUIRED_COLUMNS)
                writer.writeheader()
                writer.writerows(rows)
            result = calibrate_csv(path)
            self.assertGreaterEqual(result["recommended_iterations"], 4)
            self.assertEqual(result["groups"][0]["outlier_count"], 0)


if __name__ == "__main__":
    unittest.main()
