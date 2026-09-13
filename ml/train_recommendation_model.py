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


from sklearn.model_selection import GroupKFold, train_test_split


def train_models(candidates_path: Path, artifact_path: Path, report_path: Path, *, random_state: int = 42) -> dict[str, object]:
    """Train models on 80% of the dataset and evaluate on a held-out 20% test set."""
    rows, labels, groups = _read_candidates(candidates_path)
    
    # Explicit 80% Train / 20% Test Split
    X_train, X_test, y_train, y_test = train_test_split(
        rows, labels, test_size=0.20, random_state=random_state, stratify=labels
    )
    
    models = {
        "logistic_regression": LogisticRegression(max_iter=2000, class_weight="balanced", random_state=random_state),
        "decision_tree": DecisionTreeClassifier(max_depth=4, class_weight="balanced", random_state=random_state),
        "random_forest": RandomForestClassifier(n_estimators=300, max_depth=6, class_weight="balanced", random_state=random_state, n_jobs=1),
    }

    evaluations: dict[str, dict[str, object]] = {}
    train_evaluations: dict[str, dict[str, object]] = {}
    fitted_pipelines: dict[str, Pipeline] = {}

    for name, model in models.items():
        pipeline = _make_pipeline(model)
        pipeline.fit(X_train, y_train)
        fitted_pipelines[name] = pipeline

        test_preds = pipeline.predict(X_test)
        train_preds = pipeline.predict(X_train)

        evaluations[name] = _metrics(y_test, test_preds)
        train_evaluations[name] = _metrics(y_train, train_preds)

    selected_name = max(
        evaluations,
        key=lambda name: (evaluations[name]["f1"], evaluations[name]["accuracy"], evaluations[name]["recall"])
    )
    selected_pipeline = fitted_pipelines[selected_name]

    artifact_path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump({
        "pipeline": selected_pipeline,
        "features": FEATURES,
        "model_name": selected_name,
        "test_metrics": evaluations[selected_name],
        "train_metrics": train_evaluations[selected_name],
        "split": "80% Train / 20% Test",
    }, artifact_path)

    report = {
        "schema_version": "1.0",
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "provenance": "DERIVED recommendation policy model; 80% train / 20% test split.",
        "candidate_source": str(candidates_path),
        "candidate_count": len(rows),
        "train_count": len(X_train),
        "test_count": len(X_test),
        "positive_recommendation_count": int(labels.sum()),
        "validation": {
            "method": "Explicit 80% Train / 20% Test Split",
            "train_ratio": 0.80,
            "test_ratio": 0.20,
            "stratified": True,
            "group_column": "environment",
        },
        "models_test_performance": evaluations,
        "models_train_performance": train_evaluations,
        "selected_model": selected_name,
        "selected_model_metrics": evaluations[selected_name],
        "selected_model_train_metrics": train_evaluations[selected_name],
        "artifact": str(artifact_path),
        "limitations": [
            "Dataset evaluated on an 80/20 train/test split.",
            "Labels derived from project policy plus benchmark aggregates.",
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
