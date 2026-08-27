"""FastAPI Backend Server for ML-KEM Benchmarking Framework and AI Recommendation System."""

import csv
import json
import os
from pathlib import Path
from typing import List, Optional, Dict, Any

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse

try:
    from backend.models import (
        RecommendationFormInputs,
        RecommendationResult,
        HealthCheck,
    )
    from backend.ai_engine import run_ai_recommendation
except ImportError:
    from models import (
        RecommendationFormInputs,
        RecommendationResult,
        HealthCheck,
    )
    from ai_engine import run_ai_recommendation

app = FastAPI(
    title="NIST FIPS 203 ML-KEM Benchmarking Framework API",
    description="Backend API for post-quantum ML-KEM empirical benchmarks and AI recommendation system.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

SETTINGS_DB = {
    "datasetSource": "data/processed/phase11_statistics/observations.csv",
    "themePreference": "system",
    "cacheEnabled": True,
    "logLevel": "INFO",
    "maxLatencyThresholdUs": 10000,
}


def _dataset_path() -> Path:
    root_dir = Path(__file__).resolve().parent.parent
    configured_path = os.getenv("MLKEM_DATASET_PATH")
    return Path(configured_path) if configured_path else root_dir / "data" / "processed" / "phase11_statistics" / "observations.csv"


def _load_dataset() -> List[Dict[str, str]]:
    dataset_path = _dataset_path()
    if not dataset_path.exists():
        raise HTTPException(status_code=404, detail=f"Benchmark dataset not found: {dataset_path}")
    try:
        with dataset_path.open(mode="r", newline="", encoding="utf-8") as handle:
            return list(csv.DictReader(handle))
    except OSError as exc:
        raise HTTPException(status_code=500, detail=f"Failed to load benchmark dataset: {exc}") from exc


def _parse_number(value: Optional[str], target_type=float) -> float | int:
    if value in (None, "", "OOM", "N/A"):
        return 0
    try:
        return target_type(value)
    except ValueError:
        return 0


def _benchmark_record(row: Dict[str, str], index: int) -> Dict[str, Any]:
    ns_val = _parse_number(row.get("execution_time_ns"), float)
    mem_bytes = _parse_number(row.get("memory_bytes"), int)
    operation = row.get("operation", "encapsulation")
    us_val = round(float(ns_val) / 1000.0, 2) if ns_val else 0.0
    return {
        "id": f"{row.get('experiment_id')}_{row.get('iteration')}_{index}",
        "mcu": row.get("processor") or row.get("environment", "Generic Target"),
        "core": row.get("architecture", "unknown"),
        "clock_mhz": None,
        "flash_kb": None,
        "ram_kb": round(int(mem_bytes) / 1024.0, 1) if mem_bytes else 0.0,
        "variant": row.get("mlkem_variant", "ML-KEM-768"),
        "operation": operation,
        "optimization": row.get("optimization_flags", "unknown"),
        "keygen_cycles": int(ns_val * 2.0) if operation == "keygen" else 0,
        "encap_cycles": int(ns_val * 2.0) if operation == "encapsulation" else 0,
        "decap_cycles": int(ns_val * 2.0) if operation == "decapsulation" else 0,
        "keygen_us": us_val if operation == "keygen" else 0.0,
        "encap_us": us_val if operation == "encapsulation" else 0.0,
        "decap_us": us_val if operation == "decapsulation" else 0.0,
        "execution_time_ns": ns_val,
        "verification_status": "PASS" if row.get("success", "True").lower() == "true" else "FAIL",
        "environment": row.get("environment", "unknown"),
        "measurement_type": row.get("normalized_measurement_type", row.get("measurement_type", "unknown")),
    }


@app.get("/", include_in_schema=False)
async def root():
    return RedirectResponse(url="/docs")


@app.get("/api/health", response_model=HealthCheck, tags=["Health"])
@app.get("/health", response_model=HealthCheck, include_in_schema=False)
async def get_health():
    return HealthCheck(status="ok", version="1.0.0")


@app.post("/api/recommendation", response_model=RecommendationResult, tags=["AI Recommendation"])
@app.post("/recommendation", response_model=RecommendationResult, include_in_schema=False)
async def get_recommendation(inputs: RecommendationFormInputs):
    try:
        return run_ai_recommendation(inputs)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Inference error: {str(e)}")


@app.get("/api/benchmarks", tags=["Benchmarks"])
@app.get("/benchmarks", include_in_schema=False)
async def get_benchmarks(type: Optional[str] = Query("baseline", description="'baseline' or 'full'")):
    rows = _load_dataset()
    records = [_benchmark_record(row, index) for index, row in enumerate(rows)]
    return records[:1500] if type == "baseline" else records


@app.get("/api/processors", tags=["Hardware Profiles"])
@app.get("/processors", include_in_schema=False)
async def get_processors():
    return [
        {
            "mcu": "x86_64-multi-core",
            "name": "AMD Ryzen 5 4600H (x86-64 Multi-Core)",
            "core": "x86_64",
            "architecture": "x86_64",
            "frequency": 3000,
            "ram": 16384,
            "flash": 512000,
            "voltage": "1.2V",
            "supportedVariants": ["ML-KEM-512", "ML-KEM-768", "ML-KEM-1024"],
            "description": "High-performance multi-core x86-64 server & workstation node.",
            "features": ["AVX2", "BMI2", "6-Core 12-Thread"],
        },
        {
            "mcu": "x86_64-single-core",
            "name": "AMD Ryzen 5 4600H (Single-Core Pin taskset -c 0)",
            "core": "x86_64",
            "architecture": "x86_64",
            "frequency": 3000,
            "ram": 16384,
            "flash": 512000,
            "voltage": "1.2V",
            "supportedVariants": ["ML-KEM-512", "ML-KEM-768", "ML-KEM-1024"],
            "description": "Single-core pinned x86-64 execution environment eliminating core hopping.",
            "features": ["Core Affinity Pinning", "AVX2", "Deterministic Cache"],
        },
        {
            "mcu": "x86-32bit-mode",
            "name": "32-bit x86 (i686 Multilib GCC -m32)",
            "core": "x86-32",
            "architecture": "x86",
            "frequency": 3000,
            "ram": 4096,
            "flash": 256000,
            "voltage": "1.2V",
            "supportedVariants": ["ML-KEM-512", "ML-KEM-768", "ML-KEM-1024"],
            "description": "Legacy 32-bit x86 execution environment for embedded x86 compatibility.",
            "features": ["i686 ABI", "32-bit Register File", "Multilib C Run-Time"],
        },
        {
            "mcu": "aarch64-vivo-y19",
            "name": "MediaTek Helio P65 MT6768 (Vivo Y19 Phone)",
            "core": "ARM Cortex-A75 / A55",
            "architecture": "aarch64",
            "frequency": 2000,
            "ram": 4096,
            "flash": 128000,
            "voltage": "3.8V",
            "supportedVariants": ["ML-KEM-512", "ML-KEM-768", "ML-KEM-1024"],
            "description": "Physical ARM64 mobile hardware running Linux Termux & Clang 18.1.",
            "features": ["NEON SIMD", "ARMv8.2-A", "Real Physical Mobile Hardware"],
        },
        {
            "mcu": "riscv64-qemu-guest",
            "name": "RISC-V 64-bit QEMU Linux Guest",
            "core": "RV64GC",
            "architecture": "riscv64",
            "frequency": 1000,
            "ram": 2096,
            "flash": 64000,
            "voltage": "3.3V",
            "supportedVariants": ["ML-KEM-512", "ML-KEM-768", "ML-KEM-1024"],
            "description": "64-bit RISC-V open ISA virtualized Linux environment.",
            "features": ["RV64GC Vector-ready", "Open ISA Standard", "GCC 13.3 Linux Guest"],
        },
        {
            "mcu": "cortex-m4-stm32f4",
            "name": "STM32F407 Cortex-M4 Microcontroller",
            "core": "ARM Cortex-M4F",
            "architecture": "armv7em",
            "frequency": 168,
            "ram": 192,
            "flash": 1024,
            "voltage": "3.3V",
            "supportedVariants": ["ML-KEM-512", "ML-KEM-768"],
            "description": "Embedded ARM Cortex-M4 microcontroller for IoT edge hardware verification.",
            "features": ["DSP & FPU", "Functional Pass Verification", "Zero-Wait Flash"],
        },
    ]


@app.get("/api/variants", tags=["ML-KEM Specifications"])
@app.get("/variants", include_in_schema=False)
async def get_variants():
    return [
        {
            "variant": "ML-KEM-512",
            "claimedNistLevel": "Level 1",
            "securityBits": 128,
            "publicKeySize": 800,
            "secretKeySize": 1632,
            "ciphertextSize": 768,
            "minRamRequirement": 16,
            "performanceRating": "High",
            "memoryUsageRating": "Compact",
            "recommendedUseCases": ["Ultra-low-power IoT nodes", "Constrained microcontrollers (<32KB RAM)"],
        },
        {
            "variant": "ML-KEM-768",
            "claimedNistLevel": "Level 3",
            "securityBits": 192,
            "publicKeySize": 1184,
            "secretKeySize": 2400,
            "ciphertextSize": 1088,
            "minRamRequirement": 20,
            "performanceRating": "Medium",
            "memoryUsageRating": "Moderate",
            "recommendedUseCases": ["General IoT gateways", "TLS 1.3 Post-Quantum Hybrid Handshakes"],
        },
        {
            "variant": "ML-KEM-1024",
            "claimedNistLevel": "Level 5",
            "securityBits": 256,
            "publicKeySize": 1568,
            "secretKeySize": 3168,
            "ciphertextSize": 1568,
            "minRamRequirement": 28,
            "performanceRating": "Maximum Security",
            "memoryUsageRating": "Heavy",
            "recommendedUseCases": ["High-security edge servers", "Long-term data confidentiality"],
        },
    ]


@app.get("/api/profiles", tags=["Application Profiles"])
@app.get("/profiles", include_in_schema=False)
async def get_profiles():
    config_path = Path(__file__).resolve().parent.parent / "configs" / "application_profiles.json"
    if not config_path.exists():
        raise HTTPException(status_code=404, detail="Application profiles JSON not found.")
    with config_path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


@app.get("/api/analytics", tags=["Analytics"])
@app.get("/analytics", include_in_schema=False)
async def get_analytics():
    rows = _load_dataset()
    successful_rows = [row for row in rows if row.get("success", "").lower() == "true"]
    encapsulations = [float(_parse_number(row.get("execution_time_ns"))) for row in successful_rows if row.get("operation") == "encapsulation"]
    return {
        "totalBenchmarks": len(rows),
        "totalPasses": len(successful_rows),
        "totalOOMs": sum(row.get("error_message") == "OOM" for row in rows),
        "passRatePercent": round(len(successful_rows) / len(rows) * 100, 2) if rows else 0.0,
        "avgEncapLatencyUs": round(sum(encapsulations) / len(encapsulations) / 1000, 2) if encapsulations else 0.0,
        "supportedProcessors": len({row.get("environment") for row in rows}),
        "mlkemVariants": len({row.get("mlkem_variant") for row in rows}),
        "aiAccuracyPercent": 86.67,
    }


@app.get("/api/settings", tags=["Settings"])
@app.get("/settings", include_in_schema=False)
async def get_settings():
    return SETTINGS_DB


@app.post("/api/settings", tags=["Settings"])
@app.post("/settings", include_in_schema=False)
async def update_settings(payload: Dict[str, Any]):
    SETTINGS_DB.update(payload)
    return {"status": "ok", "settings": SETTINGS_DB}
