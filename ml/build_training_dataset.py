"""Create transparent, derived ML-KEM recommendation candidates.

The generated labels are not user observations. They encode the documented
project policy: meet a profile's minimum variant, satisfy its latency bound
when possible, then prefer the candidate with lower measured P95 handshake
latency. This artifact is suitable for evaluating a model as a surrogate for
that policy, not for claiming universal device prediction.
"""

from __future__ import annotations

import argparse
import csv
import json
from collections import defaultdict
from pathlib import Path

from mlkem_benchmark.profiles import load_application_profiles

VARIANT_ORDER = {"ML-KEM-512": 1, "ML-KEM-768": 2, "ML-KEM-1024": 3}
CANDIDATE_COLUMNS = [
    "provenance", "profile_id", "environment", "architecture", "measurement_type",
    "mlkem_variant", "security_requirement", "latency_sensitivity", "throughput_importance",
    "memory_constraint_level", "compute_budget_level", "max_acceptable_latency_ms",
    "minimum_variant", "mean_handshake_latency_ms", "p95_handshake_latency_ms",
    "mean_memory_bytes", "eligible_security", "meets_latency_constraint", "policy_score",
    "recommended", "recommendation_reason",
]


def _load_variant_aggregates(statistics_path: Path) -> dict[tuple[str, str, str, str], dict[str, float]]:
    grouped: dict[tuple[str, str, str, str], list[dict[str, str]]] = defaultdict(list)
    with statistics_path.open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            grouped[(row["environment"], row["architecture"], row["normalized_measurement_type"], row["mlkem_variant"])].append(row)
    aggregates = {}
    for key, rows in grouped.items():
        if {row["operation"] for row in rows} != {"keygen", "encapsulation", "decapsulation"}:
            raise ValueError(f"Incomplete operation set for {key}")
        aggregates[key] = {
            "mean_handshake_latency_ms": sum(float(row["mean_execution_time_ns"]) for row in rows) / 1_000_000,
            "p95_handshake_latency_ms": sum(float(row["p95_execution_time_ns"]) for row in rows) / 1_000_000,
            "mean_memory_bytes": max(float(row["mean_memory_bytes"]) for row in rows),
        }
    return aggregates


def build_training_dataset(statistics_path: Path, output_path: Path, *, overwrite: bool = False) -> dict[str, object]:
    """Write recommendation candidates and a manifest from processed statistics."""
    if output_path.exists() and not overwrite:
        raise FileExistsError("Training dataset exists; choose another file or pass overwrite=True")
    aggregates = _load_variant_aggregates(statistics_path)
    profiles = load_application_profiles()
    by_environment: dict[tuple[str, str, str], list[tuple[str, dict[str, float]]]] = defaultdict(list)
    for (environment, architecture, measurement_type, variant), metrics in aggregates.items():
        by_environment[(environment, architecture, measurement_type)].append((variant, metrics))

    rows: list[dict[str, object]] = []
    for profile in profiles:
        for (environment, architecture, measurement_type), candidates in sorted(by_environment.items()):
            eligible = [(variant, metrics) for variant, metrics in candidates if VARIANT_ORDER[variant] >= VARIANT_ORDER[profile.min_recommended_variant]]
            feasible = [(variant, metrics) for variant, metrics in eligible if metrics["p95_handshake_latency_ms"] <= profile.max_acceptable_latency_ms]
            selected_pool = feasible or eligible
            if not selected_pool:
                raise ValueError(f"No variant meets profile security floor for {profile.id}")
            selected_variant, _ = min(selected_pool, key=lambda item: (item[1]["p95_handshake_latency_ms"], VARIANT_ORDER[item[0]]))
            for variant, metrics in sorted(candidates):
                security = VARIANT_ORDER[variant] >= VARIANT_ORDER[profile.min_recommended_variant]
                latency = metrics["p95_handshake_latency_ms"] <= profile.max_acceptable_latency_ms
                recommended = variant == selected_variant
                reason = (
                    "Selected by derived policy: meets the profile security floor and has the lowest measured P95 handshake latency among feasible variants."
                    if recommended and feasible else
                    "Selected by derived fallback policy: no security-eligible variant met the latency bound; lowest measured P95 handshake latency chosen."
                    if recommended else
                    "Not selected by the derived policy."
                )
                rows.append({
                    "provenance": "DERIVED / project-defined profile policy plus measured benchmark aggregates",
                    "profile_id": profile.id, "environment": environment, "architecture": architecture,
                    "measurement_type": measurement_type, "mlkem_variant": variant,
                    "security_requirement": profile.security_requirement, "latency_sensitivity": profile.latency_sensitivity,
                    "throughput_importance": profile.throughput_importance, "memory_constraint_level": profile.memory_constraint_level,
                    "compute_budget_level": profile.compute_budget_level, "max_acceptable_latency_ms": profile.max_acceptable_latency_ms,
                    "minimum_variant": profile.min_recommended_variant,
                    **metrics, "eligible_security": security, "meets_latency_constraint": latency,
                    "policy_score": -metrics["p95_handshake_latency_ms"] if security and latency else None,
                    "recommended": recommended, "recommendation_reason": reason,
                })
    output_path.parent.mkdir(parents=True, exist_ok=True)
    if output_path.exists():
        output_path.unlink()
    with output_path.open("x", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=CANDIDATE_COLUMNS)
        writer.writeheader()
        writer.writerows(rows)
    return {
        "provenance": "DERIVED / project-defined profile policy plus measured benchmark aggregates",
        "candidate_count": len(rows), "recommended_count": sum(row["recommended"] for row in rows),
        "profile_count": len(profiles), "execution_configuration_count": len(by_environment),
        "source_statistics": str(statistics_path), "output": str(output_path),
        "limitations": [
            "Labels are policy-derived, not independently observed user choices.",
            "The five execution configurations do not represent five independent physical devices.",
            "EMULATED RISC-V candidates must not be interpreted as physical-device performance.",
        ],
    }


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser(description="Build derived ML-KEM recommendation candidates.")
    parser.add_argument("--statistics", type=Path, default=root / "data" / "processed" / "phase11_statistics" / "benchmark_statistics.csv")
    parser.add_argument("--output", type=Path, default=root / "data" / "processed" / "phase11_training" / "recommendation_candidates.csv")
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args()
    manifest = build_training_dataset(args.statistics, args.output, overwrite=args.overwrite)
    manifest_path = args.output.with_name("training_manifest.json")
    if manifest_path.exists() and not args.overwrite:
        raise FileExistsError("Training manifest exists; choose another file or pass overwrite=True")
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {manifest['candidate_count']} derived candidates ({manifest['recommended_count']} selected) to {args.output}")


if __name__ == "__main__":
    main()
