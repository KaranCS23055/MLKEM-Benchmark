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

try:
    import joblib
    import numpy as np
    import pandas as pd
    _artifact = joblib.load(_MODEL_PATH)
    _PIPELINE = _artifact["pipeline"]
    _MODEL_FEATURES = _artifact["features"]
    logger.info("ML-KEM surrogate model loaded from %s (features: %s)", _MODEL_PATH, _MODEL_FEATURES)
except Exception as _e:
    logger.warning("Could not load ML model (%s) — falling back to rule-based engine.", _e)

# ── Pydantic models import (supports both direct + uvicorn module paths) ──────
try:
    from backend.models import RecommendationFormInputs, RecommendationResult, ComparisonBadge
except ImportError:
    from models import RecommendationFormInputs, RecommendationResult, ComparisonBadge

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
        comparisonBadges=badges,
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
                "ML Random Forest (Phase 11)",
            )

        import pandas as pd
        VARIANT_ORDER = {"ML-KEM-512": 1, "ML-KEM-768": 2, "ML-KEM-1024": 3}
        sec_req = {"Level 1": 1, "Level 3": 2, "Level 5": 3}.get(inputs.securityLevel, 2)
        min_variant = _SEC_LEVEL.get(inputs.securityLevel, "ML-KEM-512")
        min_var_order = VARIANT_ORDER[min_variant]
        latency_sens = min(5, max(1, round(5 - (inputs.latencyBudget / 10000) * 4)))
        mem_level = min(5, max(1, round(5 - (inputs.ram / 1000))))

        rows = []
        variants = ["ML-KEM-512", "ML-KEM-768", "ML-KEM-1024"]
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
                "architecture":             "x86_64",
                "measurement_type":         "NATIVE_SOFTWARE",
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
                f"Random Forest surrogate model (Accuracy 84.6%, 80/20 Split F1 0.778) "
                f"selected {chosen} with {confidence}% confidence based on your hardware "
                f"profile ({inputs.ram} KB SRAM, {inputs.frequency} MHz, {inputs.securityLevel} security), "
                f"measured benchmark aggregates, and application profile policy."
            )
        return _build_result(chosen, confidence, reason, inputs, "ML Random Forest (Phase 11)")
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
        reason = f"ML-KEM-768 selected for balanced Level 3 security on {ram} KB SRAM."
    else:
        chosen, confidence = "ML-KEM-512", 98.1
        reason = f"ML-KEM-512 selected for stack safety on {ram} KB SRAM."

    return _build_result(chosen, confidence, reason, inputs, "Rule-Based Empirical (Fallback)")


def run_ai_recommendation(inputs: RecommendationFormInputs) -> RecommendationResult:
    """Primary entrypoint — tries ML model first, falls back to rule-based logic."""
    result = _ml_inference(inputs)
    if result is not None:
        return result
    return _rule_based(inputs)
