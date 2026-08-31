"""Integration tests for Backend API and AI Recommendation Engine."""

import pytest
from backend.models import RecommendationFormInputs, RecommendationResult
from backend.ai_engine import run_ai_recommendation


def test_ai_recommendation_cortex_m4():
    inputs = RecommendationFormInputs(
        mcu="STM32F407VGT6",
        frequency=168,
        ram=192,
        flash=1024,
        securityLevel="Level 3",
        optimization="O3",
        cpuLoad=25,
        latencyBudget=8000,
    )
    result = run_ai_recommendation(inputs)
    assert isinstance(result, RecommendationResult)
    assert result.recommendedVariant in ["ML-KEM-512", "ML-KEM-768", "ML-KEM-1024"]
    assert result.confidence > 0
    assert result.estimatedKeygenUs > 0
    assert result.estimatedEncapUs > 0
    assert result.estimatedDecapUs > 0
    assert len(result.comparisonBadges) >= 3


def test_ai_recommendation_x86_server():
    inputs = RecommendationFormInputs(
        mcu="Ryzen5-x86_64",
        frequency=3000,
        ram=16384,
        flash=512000,
        securityLevel="Level 5",
        optimization="O3",
        cpuLoad=10,
        latencyBudget=50000,
    )
    result = run_ai_recommendation(inputs)
    assert result.recommendedVariant == "ML-KEM-1024"
    assert result.latencyCompliance == "EXCELLENT"


def test_ai_recommendation_unsupported_ram():
    inputs = RecommendationFormInputs(
        mcu="UltraLowPower-Tiny",
        frequency=16,
        ram=8,  # Below 16KB minimum
        flash=64,
        securityLevel="Level 1",
        optimization="O0",
        cpuLoad=0,
        latencyBudget=10000,
    )
    result = run_ai_recommendation(inputs)
    assert result.recommendedVariant == "UNSUPPORTED"
    assert result.estimatedKeygenUs == 0
    assert result.estimatedEncapUs == 0
    assert result.estimatedDecapUs == 0
    assert result.estimatedRamKb == 0
    assert result.latencyCompliance == "EXCEEDED"


def test_ai_recommendation_ram_constraint_fallback():
    inputs = RecommendationFormInputs(
        mcu="Constrained-Target",
        frequency=100,
        ram=24,  # Fits 512 (16KB) and 768 (20KB), but NOT 1024 (28KB)
        flash=512,
        securityLevel="Level 5",  # Wants 1024 minimum
        optimization="O2",
        cpuLoad=10,
        latencyBudget=20000,
    )
    result = run_ai_recommendation(inputs)
    assert result.recommendedVariant == "ML-KEM-768"
    assert result.estimatedRamKb == 20
    assert "exceeds available RAM" in result.reason
