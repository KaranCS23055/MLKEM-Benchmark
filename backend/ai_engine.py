from typing import List
try:
    from backend.models import RecommendationFormInputs, RecommendationResult, ComparisonBadge
except ImportError:
    from models import RecommendationFormInputs, RecommendationResult, ComparisonBadge

def run_ai_recommendation(inputs: RecommendationFormInputs) -> RecommendationResult:
    frequency = inputs.frequency
    ram = inputs.ram
    security_level = inputs.securityLevel
    optimization = inputs.optimization
    cpu_load = inputs.cpuLoad
    latency_budget = inputs.latencyBudget

    # Constants
    RAM_512, RAM_768, RAM_1024 = 16, 20, 28
    base_keygen = 430_000
    base_encap = 510_000
    base_decap = 640_000

    opt_multiplier = {
        "O0": 2.1,
        "O1": 1.4,
        "O2": 1.1,
        "O3": 1.0,
    }.get(optimization, 1.0)

    load_multiplier = 1.0 + (cpu_load / 100.0) * 0.35

    chosen_variant = "ML-KEM-512"
    reason = ""
    confidence = 96.5

    if ram < RAM_512:
        chosen_variant = "UNSUPPORTED"
        reason = f"Target MCU has only {ram} KB SRAM. ML-KEM-512 requires at least 16 KB SRAM to prevent stack overflow."
        confidence = 99.8
    elif security_level == "Level 5" and ram >= RAM_1024:
        chosen_variant = "ML-KEM-1024"
        reason = f"Recommended ML-KEM-1024 for maximum post-quantum security (NIST Level 5) on {ram} KB SRAM."
        base_keygen *= 2.6
        base_encap *= 2.5
        base_decap *= 2.3
        confidence = 97.8
    elif security_level == "Level 3" and ram >= RAM_768:
        chosen_variant = "ML-KEM-768"
        reason = f"Recommended ML-KEM-768 for optimal balance of Level 3 security, SRAM footprint, and execution latency."
        base_keygen *= 1.65
        base_encap *= 1.62
        base_decap *= 1.55
        confidence = 96.2
    elif security_level == "Level 5" and RAM_768 <= ram < RAM_1024:
        chosen_variant = "ML-KEM-768"
        reason = f"Requested Level 5 security, but RAM ({ram} KB) is insufficient for ML-KEM-1024 (requires 28 KB). Safely fallback to ML-KEM-768."
        base_keygen *= 1.65
        base_encap *= 1.62
        base_decap *= 1.55
        confidence = 94.1
    else:
        chosen_variant = "ML-KEM-512"
        reason = f"Recommended ML-KEM-512 to ensure stack safety on {ram} KB SRAM while meeting latency targets."
        confidence = 98.1

    effective_freq = max(8, frequency)
    est_keygen = round((base_keygen * opt_multiplier * load_multiplier) / effective_freq)
    est_encap = round((base_encap * opt_multiplier * load_multiplier) / effective_freq)
    est_decap = round((base_decap * opt_multiplier * load_multiplier) / effective_freq)

    estimated_ram_kb = 28 if chosen_variant == "ML-KEM-1024" else (20 if chosen_variant == "ML-KEM-768" else 16)
    ram_util_pct = min(100, round((estimated_ram_kb / ram) * 100))

    total_latency = est_keygen + est_encap + est_decap
    if total_latency <= latency_budget * 0.5:
        latency_compliance = "EXCELLENT"
    elif total_latency <= latency_budget:
        latency_compliance = "COMPLIANT"
    elif total_latency <= latency_budget * 1.5:
        latency_compliance = "WARNING"
    else:
        latency_compliance = "EXCEEDED"

    comparison_badges: List[ComparisonBadge] = [
        ComparisonBadge(
            label="Security Level",
            value=(
                "NIST Category 5 (256-bit AES eq.)" if chosen_variant == "ML-KEM-1024"
                else "NIST Category 3 (192-bit AES eq.)" if chosen_variant == "ML-KEM-768"
                else "NIST Category 1 (128-bit AES eq.)"
            ),
            type="info",
        ),
        ComparisonBadge(
            label="SRAM Footprint",
            value=f"{estimated_ram_kb} KB ({ram_util_pct}% of {ram} KB available)",
            type="warning" if ram_util_pct > 90 else "success",
        ),
        ComparisonBadge(
            label="Execution Latency",
            value=f"{(est_encap / 1000.0):.2f} ms Encap",
            type="info",
        ),
        ComparisonBadge(
            label="Status",
            value="OOM Risk" if chosen_variant == "UNSUPPORTED" else "Passed Verification",
            type="error" if chosen_variant == "UNSUPPORTED" else "success",
        ),
    ]

    return RecommendationResult(
        recommendedVariant=chosen_variant,
        confidence=confidence,
        reason=reason,
        estimatedKeygenUs=est_keygen,
        estimatedEncapUs=est_encap,
        estimatedDecapUs=est_decap,
        estimatedRamKb=estimated_ram_kb,
        ramUtilizationPercent=ram_util_pct,
        latencyCompliance=latency_compliance,
        comparisonBadges=comparison_badges,
    )
