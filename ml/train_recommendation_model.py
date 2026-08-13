"""Train and evaluate transparent recommendation-policy surrogate models.

The target is a project-derived policy label, not an observed human decision.
Evaluation keeps whole execution configurations together, preventing repeated
candidates from the same configuration appearing in both train and test sets.
"""

from __future__ import annotations

import argparse
import csv
import json
from datetime import datetime, timezone
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, confusion_matrix, f1_score, precision_score, recall_score
from sklearn.model_selection import GroupKFold
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.tree import DecisionTreeClassifier

NUMERIC_FEATURES = [
    "security_requirement", "latency_sensitivity", "throughput_importance",
    "memory_constraint_level", "compute_budget_level", "max_acceptable_latency_ms",
    "mean_handshake_latency_ms", "p95_handshake_latency_ms", "mean_memory_bytes",
]
CATEGORICAL_FEATURES = ["architecture", "measurement_type", "mlkem_variant", "minimum_variant"]
FEATURES = [*NUMERIC_FEATURES, *CATEGORICAL_FEATURES]


def _read_candidates(path: Path) -> tuple[pd.DataFrame, np.ndarray, np.ndarray]:
    rows: list[dict[str, object]] = []
    labels: list[int] = []
    groups: list[str] = []
    with path.open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            if not row["provenance"].startswith("DERIVED"):
                raise ValueError("Training candidates must be explicitly DERIVED")
            rows.append({
                **{name: float(row[name]) for name in NUMERIC_FEATURES},
                **{name: row[name] for name in CATEGORICAL_FEATURES},
            })
            labels.append(row["recommended"] == "True")
            groups.append(row["environment"])
    if not rows:
        raise ValueError("Candidate dataset is empty")
    if len(set(groups)) < 2:
        raise ValueError("At least two execution configurations are required for grouped validation")
    return pd.DataFrame(rows, columns=FEATURES), np.asarray(labels, dtype=int), np.asarray(groups)


def _make_pipeline(model) -> Pipeline:
    preprocessor = ColumnTransformer([
        ("numeric", StandardScaler(), NUMERIC_FEATURES),
        ("categorical", OneHotEncoder(handle_unknown="ignore"), CATEGORICAL_FEATURES),
    ])
    return Pipeline([( "preprocessor", preprocessor), ("classifier", model)])


def _metrics(y_true: np.ndarray, y_pred: np.ndarray) -> dict[str, object]:
    return {
        "accuracy": accuracy_score(y_true, y_pred),
        "precision": precision_score(y_true, y_pred, zero_division=0),
        "recall": recall_score(y_true, y_pred, zero_division=0),
        "f1": f1_score(y_true, y_pred, zero_division=0),
        "confusion_matrix_labels": ["not_recommended", "recommended"],
        "confusion_matrix": confusion_matrix(y_true, y_pred, labels=[0, 1]).tolist(),
    }


def train_models(candidates_path: Path, artifact_path: Path, report_path: Path, *, random_state: int = 42) -> dict[str, object]:
    """Evaluate three models with GroupKFold, then persist the best full-data fit."""
    rows, labels, groups = _read_candidates(candidates_path)
    split_count = len(set(groups))
    splitter = GroupKFold(n_splits=split_count)
    models = {
        "logistic_regression": LogisticRegression(max_iter=2000, class_weight="balanced", random_state=random_state),
        "decision_tree": DecisionTreeClassifier(max_depth=4, class_weight="balanced", random_state=random_state),
        "random_forest": RandomForestClassifier(n_estimators=300, max_depth=6, class_weight="balanced", random_state=random_state, n_jobs=1),
    }
    evaluations: dict[str, dict[str, object]] = {}
    for name, model in models.items():
        predictions = np.zeros(len(labels), dtype=int)
        for train_index, test_index in splitter.split(rows, labels, groups):
            pipeline = _make_pipeline(model)
            pipeline.fit(rows.iloc[train_index], labels[train_index])
            predictions[test_index] = pipeline.predict(rows.iloc[test_index])
        evaluations[name] = _metrics(labels, predictions)

    selected_name = max(evaluations, key=lambda name: (evaluations[name]["f1"], evaluations[name]["accuracy"], evaluations[name]["recall"]))
    selected_pipeline = _make_pipeline(models[selected_name])
    selected_pipeline.fit(rows, labels)
    artifact_path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump({"pipeline": selected_pipeline, "features": FEATURES, "model_name": selected_name}, artifact_path)

    report = {
        "schema_version": "1.0",
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "provenance": "DERIVED recommendation policy model; not a universal device-performance predictor.",
        "candidate_source": str(candidates_path),
        "candidate_count": len(rows),
        "positive_recommendation_count": int(labels.sum()),
        "execution_configuration_count": len(set(groups)),
        "validation": {
            "method": f"GroupKFold with {split_count} folds grouped by environment",
            "group_column": "environment",
            "reason": "All candidates from one execution configuration are held out together; repeated benchmark evidence cannot leak into both training and test folds.",
        },
        "models": evaluations,
        "selected_model": selected_name,
        "selected_model_metrics": evaluations[selected_name],
        "artifact": str(artifact_path),
        "limitations": [
            "Labels are derived from the documented project policy, not independent user-choice observations.",
            "Only five execution configurations are available; evaluation uncertainty is high.",
            "The x86 configurations share one physical host, and RISC-V is emulated.",
            "Metrics measure agreement with the derived policy on held-out configurations, not universal accuracy on new devices.",
        ],
    }
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    return report


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser(description="Train ML-KEM recommendation-policy surrogate models.")
    parser.add_argument("--candidates", type=Path, default=root / "data" / "processed" / "phase11_training" / "recommendation_candidates.csv")
    parser.add_argument("--artifact", type=Path, default=root / "ml" / "artifacts" / "recommendation_policy_model.joblib")
    parser.add_argument("--report", type=Path, default=root / "data" / "processed" / "phase11_training" / "model_evaluation.json")
    args = parser.parse_args()
    report = train_models(args.candidates, args.artifact, args.report)
    metrics = report["selected_model_metrics"]
    print(f"Selected {report['selected_model']} with grouped F1={metrics['f1']:.4f}, accuracy={metrics['accuracy']:.4f}")


if __name__ == "__main__":
    main()
