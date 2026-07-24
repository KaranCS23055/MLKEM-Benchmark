"""Calibration analysis for deciding a justified future iteration count."""

from __future__ import annotations

import csv
import math
import statistics
from collections import defaultdict
from pathlib import Path


def _quantile(values: list[int], probability: float) -> float:
    ordered = sorted(values)
    index = (len(ordered) - 1) * probability
    low, high = math.floor(index), math.ceil(index)
    if low == high:
        return float(ordered[low])
    return ordered[low] + (ordered[high] - ordered[low]) * (index - low)


def calibrate_csv(raw_path: Path, relative_margin: float = 0.05) -> dict:
    """Analyze valid measurements and estimate sample sizes from observed CVs.

    The estimate is n = ceil((1.96 * CV / relative_margin)^2), using a
    normal-approximation 95% confidence interval for the mean. It is a
    calibration decision aid, not a claimed guarantee of timing normality.
    """
    if not 0 < relative_margin < 1:
        raise ValueError("relative_margin must be between 0 and 1")
    groups: dict[tuple[str, str], list[int]] = defaultdict(list)
    with raw_path.open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            if row["success"] == "True":
                groups[(row["mlkem_variant"], row["operation"])].append(int(row["execution_time_ns"]))
    analyses = []
    for (variant, operation), values in sorted(groups.items()):
        mean = statistics.mean(values)
        stddev = statistics.stdev(values) if len(values) > 1 else 0.0
        cv = stddev / mean if mean else 0.0
        q1, q3 = _quantile(values, 0.25), _quantile(values, 0.75)
        iqr = q3 - q1
        lower, upper = q1 - 1.5 * iqr, q3 + 1.5 * iqr
        outliers = [value for value in values if value < lower or value > upper]
        estimated_n = max(len(values), math.ceil((1.96 * cv / relative_margin) ** 2))
        analyses.append({
            "mlkem_variant": variant, "operation": operation, "count": len(values),
            "mean_ns": mean, "stddev_ns": stddev, "coefficient_of_variation": cv,
            "relative_standard_error": cv / math.sqrt(len(values)) if values else 0.0,
            "q1_ns": q1, "q3_ns": q3, "iqr_ns": iqr,
            "outlier_lower_bound_ns": lower, "outlier_upper_bound_ns": upper,
            "outlier_count": len(outliers), "estimated_samples_for_target": estimated_n,
        })
    recommended_iterations = max(item["estimated_samples_for_target"] for item in analyses)
    return {
        "source_raw_csv": str(raw_path), "input_iterations": len(next(iter(groups.values()))) if groups else 0,
        "relative_margin": relative_margin, "confidence_level": 0.95,
        "groups": analyses, "recommended_iterations": recommended_iterations,
        "recommendation_basis": "Maximum estimated sample size across observed variant/operation groups.",
    }
