from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from ml.train_recommendation_model import train_models


class Phase11ModelTrainingTests(unittest.TestCase):
    def test_trains_and_writes_honest_evaluation_report(self) -> None:
        root = Path(__file__).resolve().parents[1]
        candidates = root / "data" / "processed" / "phase11_training" / "recommendation_candidates.csv"
        if not candidates.exists():
            self.skipTest("Generated candidate dataset is not available")
        with tempfile.TemporaryDirectory() as temp:
            temp_path = Path(temp)
            report = train_models(candidates, temp_path / "model.joblib", temp_path / "report.json")
            self.assertIn(report["selected_model"], {"logistic_regression", "decision_tree", "random_forest"})
            self.assertEqual(report["validation"]["group_column"], "environment")
            self.assertEqual(report["candidate_count"], len(candidates.read_text(encoding="utf-8").strip().splitlines()) - 1)
            self.assertTrue((temp_path / "model.joblib").exists())
            stored = json.loads((temp_path / "report.json").read_text(encoding="utf-8"))
            self.assertIn("limitations", stored)
            self.assertGreaterEqual(stored["selected_model_metrics"]["accuracy"], 0.0)


if __name__ == "__main__":
    unittest.main()
