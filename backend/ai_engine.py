"""ML-KEM Recommendation Engine — Phase 11: Real ML model inference via joblib.

Loads the trained Random Forest surrogate model at startup.
Falls back to rule-based empirical logic if the artifact is missing so the
backend never crashes even in development without a trained model.
"""

from __future__ import annotations
import logging
from pathlib import Path
from typing import List

logger = logging.getLogger(__name__)

# ── Attempt to load the trained model artifact ────────────────────────────────
_MODEL_PATH = Path(__file__).resolve().parent.parent / "ml" / "artifacts" / "recommendation_policy_model.joblib"
_PIPELINE = None
_MODEL_FEATURES = None
_MODEL_NAME = "Unavailable model"
_MODEL_TEST_METRICS = {}

try:
    import joblib
    import numpy as np
    import pandas as pd
    _artifact = joblib.load(_MODEL_PATH)
    _PIPELINE = _artifact["pipeline"]
    _MODEL_FEATURES = _artifact["features"]
    _MODEL_NAME = str(_artifact.get("model_name", "trained recommendation model"))
    _MODEL_TEST_METRICS = _artifact.get("test_metrics", {})
    logger.info("ML-KEM surrogate model loaded from %s (features: %s)", _MODEL_PATH, _MODEL_FEATURES)
except Exception as _e:
    logger.warning("Could not load ML model (%s) — falling back to rule-based engine.", _e)

# ── Pydantic models import (supports both direct + uvicorn module paths) ──────
try:
    from backend.models import RecommendationFormInputs, RecommendationResult, ComparisonBadge, VariantEvaluation
except ImportError:
    from models import RecommendationFormInputs, RecommendationResult, ComparisonBadge, VariantEvaluation

# ── Variant constants ─────────────────────────────────────────────────────────
_RAM_REQ   = {"ML-KEM-512": 16, "ML-KEM-768": 20, "ML-KEM-1024": 28}
_SEC_LEVEL = {"Level 1": "ML-KEM-512", "Level 3": "ML-KEM-768", "Level 5": "ML-KEM-1024"}
_NIST_LABEL = {
    "ML-KEM-512":  "NIST Category 1 (128-bit AES eq.)",
    "ML-KEM-768":  "NIST Category 3 (192-bit AES eq.)",
    "ML-KEM-1024": "NIST Category 5 (256-bit AES eq.)",
}

# Base cycle estimates at 1 MHz derived from empirical mlkem-native dataset
_BASE_CYCLES = {
    "ML-KEM-512":  (430_000, 510_000, 640_000),
    "ML-KEM-768":  (709_500, 826_200, 992_000),
    "ML-KEM-1024": (1_118_000, 1_275_000, 1_472_000),
}

_VARIANTS = ["ML-KEM-512", "ML-KEM-768", "ML-KEM-1024"]
_VARIANT_ORDER = {variant: index for index, variant in enumerate(_VARIANTS, start=1)}
_BENCHMARK_VARIANTS_BY_ARCH = {
    "x86_64": set(_VARIANTS), "aarch64": set(_VARIANTS),
    "xtensa_lx106": {"ML-KEM-512", "ML-KEM-768"}, "xtensa_lx6": set(_VARIANTS),
}


def _model_label() -> str:
    """Return display metadata from the artifact currently loaded by this process."""
    if _PIPELINE is None:
        return "Rule-based fallback"
    accuracy = float(_MODEL_TEST_METRICS.get("accuracy", 0.0)) * 100
    f1 = float(_MODEL_TEST_METRICS.get("f1", 0.0))
    return f"{_MODEL_NAME.replace('_', ' ').title()} | test accuracy {accuracy:.2f}% | test F1 {f1:.3f} | 80/20 train/test"


def _variant_evaluations(inputs: RecommendationFormInputs, chosen: str) -> list[VariantEvaluation]:
    """Explain every policy decision, including constraints that failed."""
    required = _VARIANT_ORDER[_SEC_LEVEL.get(inputs.securityLevel, "ML-KEM-512")]
    available = _BENCHMARK_VARIANTS_BY_ARCH.get(inputs.architecture, set(_VARIANTS))
    evaluations = []
    for variant in _VARIANTS:
        security_match = _VARIANT_ORDER[variant] >= required
        ram_match = inputs.ram >= _RAM_REQ[variant]
        keygen, encap, decap = _latency_estimate(variant, inputs.frequency, inputs.optimization, inputs.cpuLoad)
        total = keygen + encap + decap
        latency_match = total <= inputs.latencyBudget
        benchmark_coverage = (
            "Observed benchmark coverage for this architecture and variant"
            if variant in available else
            "No benchmark record for this architecture/variant; practical support is unverified"
        )
        if variant == chosen:
            status, label = "SELECTED", "Selected"
            reason = (
                f"Selected for {inputs.applicationProfile} because it meets the {inputs.securityLevel} security floor, "
                f"fits the {inputs.ram} KB SRAM budget, and its estimated {total:,} us full-operation latency "
                f"is {'within' if latency_match else 'above'} the {inputs.latencyBudget:,} us budget. "
                f"Benchmark evidence: {benchmark_coverage.lower()}."
            )
        elif variant not in available:
            status, label = "UNSUPPORTED_HARDWARE", "Unsupported by benchmark coverage"
            reason = f"Not selected: {benchmark_coverage}; the framework cannot claim practical benchmark performance for this target."
        elif not ram_match:
            status, label = "DISQUALIFIED_RAM", "Insufficient RAM"
            reason = f"Not selected: requires at least {_RAM_REQ[variant]} KB SRAM but the target provides {inputs.ram} KB."
        elif not security_match:
            status, label = "DISQUALIFIED_SECURITY", "Below security floor"
            reason = f"Not selected: provides NIST Category {_VARIANT_ORDER[variant]} but {inputs.securityLevel} requires Category {required} or higher."
        elif not latency_match:
            status, label = "DISQUALIFIED_LATENCY", "Latency budget exceeded"
            reason = f"Not selected: estimated full-operation latency is {total:,} us, above the {inputs.latencyBudget:,} us budget."
        else:
            status, label = "FEASIBLE", "Feasible alternative"
            reason = f"Not selected: it is feasible, but benchmark-informed policy ranked {chosen} higher for {inputs.applicationProfile}."
        evaluations.append(VariantEvaluation(
            variant=variant, status=status, statusLabel=label,
            securityMatch=security_match, ramMatch=ram_match, latencyMatch=latency_match,
            reason=reason, benchmarkCoverage=benchmark_coverage,
            estimatedKeygenUs=keygen, estimatedEncapUs=encap, estimatedDecapUs=decap,
            estimatedRamKb=_RAM_REQ[variant], nistCategory=_NIST_LABEL[variant],
        ))
    return evaluations


def _latency_estimate(variant: str, frequency_mhz: int, optimization: str, cpu_load: int):
    """Return (keygen_us, encap_us, decap_us) estimates."""
    kg, enc, dec = _BASE_CYCLES.get(variant, _BASE_CYCLES["ML-KEM-512"])
    opt_mul = {"O0": 2.1, "O1": 1.4, "O2": 1.1, "O3": 1.0}.get(optimization, 1.0)
    load_mul = 1.0 + (cpu_load / 100.0) * 0.35
    freq = max(8, frequency_mhz)
    return (
        round((kg  * opt_mul * load_mul) / freq),
        round((enc * opt_mul * load_mul) / freq),
        round((dec * opt_mul * load_mul) / freq),
    )


def _build_result(
    chosen_variant: str,
    confidence: float,
    reason: str,
    inputs: RecommendationFormInputs,
    model_used: str,
    variant_evaluations: list[VariantEvaluation] | None = None,
) -> RecommendationResult:
    if chosen_variant == "UNSUPPORTED":
        return RecommendationResult(
            recommendedVariant="UNSUPPORTED",
            confidence=round(confidence, 1),
            reason=reason,
            estimatedKeygenUs=0,
            estimatedEncapUs=0,
            estimatedDecapUs=0,
            estimatedRamKb=0,
            ramUtilizationPercent=100,
            latencyCompliance="EXCEEDED",
            latencyBudgetUs=inputs.latencyBudget,
            comparisonBadges=[
                ComparisonBadge(
                    label="Security Level",
                    value="Unsupported (RAM < 16 KB)",
                    type="error",
                ),
                ComparisonBadge(
                    label="SRAM Footprint",
                    value=f"Insufficient ({inputs.ram} KB < 16 KB)",
                    type="error",
                ),
                ComparisonBadge(
                    label="Inference Engine",
                    value=model_used,
                    type="info",
                ),
            ],
            variantEvaluations=variant_evaluations or _variant_evaluations(inputs, "UNSUPPORTED"),
            applicationProfile=inputs.applicationProfile or "general",
            modelName=model_used,
        )

    est_kg, est_enc, est_dec = _latency_estimate(
        chosen_variant, inputs.frequency, inputs.optimization, inputs.cpuLoad
    )
    ram_kb = _RAM_REQ.get(chosen_variant, 16)
    ram_util = min(100, round((ram_kb / inputs.ram) * 100)) if inputs.ram > 0 else 100
    total = est_kg + est_enc + est_dec
    lb = inputs.latencyBudget
    latency_compliance = (
        "EXCELLENT" if total <= lb * 0.5
        else "COMPLIANT" if total <= lb
        else "WARNING"   if total <= lb * 1.5
        else "EXCEEDED"
    )
    badges: List[ComparisonBadge] = [
        ComparisonBadge(
            label="Security Level",
            value=_NIST_LABEL.get(chosen_variant, "NIST Category 1 (128-bit AES eq.)"),
            type="info",
        ),
        ComparisonBadge(
            label="SRAM Footprint",
            value=f"{ram_kb} KB ({ram_util}% of {inputs.ram} KB available)",
            type="warning" if ram_util > 90 else "success",
        ),
        ComparisonBadge(
            label="Execution Latency",
            value=f"{est_enc / 1000:.2f} ms Encapsulation",
            type="info",
        ),
        ComparisonBadge(
            label="Inference Engine",
            value=model_used,
            type="success",
        ),
    ]
    return RecommendationResult(
        recommendedVariant=chosen_variant,
        confidence=round(confidence, 1),
        reason=reason,
        estimatedKeygenUs=est_kg,
        estimatedEncapUs=est_enc,
        estimatedDecapUs=est_dec,
        estimatedRamKb=ram_kb,
        ramUtilizationPercent=ram_util,
        latencyCompliance=latency_compliance,
        latencyBudgetUs=inputs.latencyBudget,
        comparisonBadges=badges,
        variantEvaluations=variant_evaluations or _variant_evaluations(inputs, chosen_variant),
        applicationProfile=inputs.applicationProfile or "general",
        modelName=model_used,
    )


def _ml_inference(inputs: RecommendationFormInputs) -> RecommendationResult | None:
    """Use the trained joblib model to pick the best variant."""
    if _PIPELINE is None:
        return None
    try:
        if inputs.ram < 16:
            return _build_result(
                "UNSUPPORTED",
                99.8,
                f"Target device has only {inputs.ram} KB SRAM — insufficient for any ML-KEM variant (minimum 16 KB SRAM required for ML-KEM-512 stack buffers).",
                inputs,
                _model_label(),
            )

        import pandas as pd
        VARIANT_ORDER = _VARIANT_ORDER
        sec_req = {"Level 1": 1, "Level 3": 2, "Level 5": 3}.get(inputs.securityLevel, 2)
        min_variant = _SEC_LEVEL.get(inputs.securityLevel, "ML-KEM-512")
        min_var_order = VARIANT_ORDER[min_variant]
        latency_sens = min(5, max(1, round(5 - (inputs.latencyBudget / 10000) * 4)))
        mem_level = min(5, max(1, round(5 - (inputs.ram / 1000))))

        rows = []
        variants = _VARIANTS
        for v in variants:
            est_kg, est_enc, est_dec = _latency_estimate(v, inputs.frequency, inputs.optimization, inputs.cpuLoad)
            mean_hs = (est_kg + est_enc + est_dec) / 1000.0  # µs → ms
            rows.append({
                "security_requirement":    float(sec_req),
                "latency_sensitivity":     float(latency_sens),
                "throughput_importance":   3.0,
                "memory_constraint_level": float(mem_level),
                "compute_budget_level":    3.0,
                "max_acceptable_latency_ms": float(inputs.latencyBudget / 1000.0),
                "mean_handshake_latency_ms": mean_hs,
                "p95_handshake_latency_ms":  mean_hs * 1.15,
                "mean_memory_bytes":        float(_RAM_REQ[v] * 1024),
                "architecture":             inputs.architecture,
                "measurement_type":         "REAL_HARDWARE" if inputs.architecture == "aarch64" else "NATIVE_SOFTWARE",
                "mlkem_variant":            v,
                "minimum_variant":          min_variant,
            })

        df = pd.DataFrame(rows)
        proba = _PIPELINE.predict_proba(df)[:, 1]  # probability of recommended=True

        ram_eligible = [i for i, v in enumerate(variants) if _RAM_REQ[v] <= inputs.ram]
        if not ram_eligible:
            return _build_result(
                "UNSUPPORTED",
                99.8,
                f"Target device has only {inputs.ram} KB SRAM — insufficient for any ML-KEM variant.",
                inputs,
                "ML Random Forest (Phase 11)",
            )

        sec_eligible = [i for i in ram_eligible if VARIANT_ORDER[variants[i]] >= min_var_order]
        eligible = sec_eligible if sec_eligible else ram_eligible

        if not sec_eligible:
            best_idx = max(eligible, key=lambda i: (VARIANT_ORDER[variants[i]], proba[i]))
        else:
            best_idx = max(eligible, key=lambda i: proba[i])
        chosen = variants[best_idx]
        confidence = round(float(proba[best_idx]) * 100, 1)

        if not sec_eligible:
            reason = (
                f"Random Forest surrogate model selected {chosen} with {confidence}% confidence "
                f"as the highest-security variant fitting in available RAM ({inputs.ram} KB SRAM). "
                f"Note: {min_variant} requested for {inputs.securityLevel} exceeds available RAM."
            )
        else:
            reason = (
                f"{_model_label()} "
                f"selected {chosen} with {confidence}% confidence based on your hardware "
                f"profile ({inputs.ram} KB SRAM, {inputs.frequency} MHz, {inputs.securityLevel} security), "
                f"measured benchmark aggregates, and application profile policy."
            )
        return _build_result(chosen, confidence, reason, inputs, _model_label(), _variant_evaluations(inputs, chosen))
    except Exception as exc:
        logger.warning("ML inference failed (%s), falling back to rule-based engine.", exc)
        return None


def _rule_based(inputs: RecommendationFormInputs) -> RecommendationResult:
    """Empirical rule-based fallback (always available)."""
    ram = inputs.ram
    sec = inputs.securityLevel
    chosen, confidence, reason = "ML-KEM-512", 96.5, ""

    if ram < 16:
        chosen, confidence = "UNSUPPORTED", 99.8
        reason = f"Target has only {ram} KB SRAM — insufficient for any ML-KEM variant (minimum 16 KB)."
    elif sec == "Level 5" and ram >= 28:
        chosen, confidence = "ML-KEM-1024", 97.8
        reason = f"ML-KEM-1024 selected for NIST Level 5 security ({ram} KB SRAM ≥ 28 KB requirement)."
    elif sec in ("Level 3", "Level 5") and ram >= 20:
        chosen, confidence = "ML-KEM-768", 96.2
        if sec == "Level 5":
            reason = (
                f"ML-KEM-768 selected as the highest-security variant fitting in {ram} KB SRAM. "
                "ML-KEM-1024 requested for Level 5 exceeds available RAM."
            )
        else:
            reason = f"ML-KEM-768 selected for balanced Level 3 security on {ram} KB SRAM."
    else:
        chosen, confidence = "ML-KEM-512", 98.1
        reason = f"ML-KEM-512 selected for stack safety on {ram} KB SRAM."

    return _build_result(chosen, confidence, reason, inputs, "Rule-Based Empirical (Fallback)", _variant_evaluations(inputs, chosen))


def run_ai_recommendation(inputs: RecommendationFormInputs) -> RecommendationResult:
    """Primary entrypoint — tries ML model first, falls back to rule-based logic."""
    result = _ml_inference(inputs)
    if result is not None:
        return result
    return _rule_based(inputs)
