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
    "apiBaseUrl": "http://127.0.0.1:8000/api",
    "renodePath": "C:\\Program Files\\Renode\\renode.exe",
    "useLiveApi": True,
    "themePreference": "system",
    "cacheEnabled": True,
    "logLevel": "INFO",
    "maxLatencyThresholdUs": 10000,
}


def _dataset_path() -> Path:
    root_dir = Path(__file__).resolve().parent.parent
    configured_path = os.getenv("MLKEM_DATASET_PATH")
    return Path(configured_path) if configured_path else root_dir / "data" / "processed" / "phase11_statistics" / "observations.csv"


_DATASET_ROWS_CACHE: Optional[List[Dict[str, str]]] = None
_BENCHMARK_RECORDS_CACHE: Optional[List[Dict[str, Any]]] = None


def _load_dataset() -> List[Dict[str, str]]:
    global _DATASET_ROWS_CACHE
    if _DATASET_ROWS_CACHE is not None:
        return _DATASET_ROWS_CACHE
    dataset_path = _dataset_path()
    if not dataset_path.exists():
        raise HTTPException(status_code=404, detail=f"Benchmark dataset not found: {dataset_path}")
    try:
        with dataset_path.open(mode="r", newline="", encoding="utf-8") as handle:
            _DATASET_ROWS_CACHE = list(csv.DictReader(handle))
            return _DATASET_ROWS_CACHE
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
        "experiment_id": row.get("experiment_id", ""),
        "run_id": row.get("run_id", ""),
        "timestamp": row.get("timestamp", ""),
        "mcu": row.get("processor") or row.get("environment", "Generic Target"),
        "processor": row.get("processor", ""),
        "core": row.get("architecture", "unknown"),
        "architecture": row.get("architecture", "unknown"),
        "cpu_cores": _parse_number(row.get("cpu_cores"), int),
        "ram_mb": _parse_number(row.get("ram_mb"), float),
        "os": row.get("os", ""),
        "compiler": row.get("compiler", ""),
        "compiler_version": row.get("compiler_version", ""),
        "optimization": row.get("optimization_flags", "unknown"),
        "optimization_flags": row.get("optimization_flags", ""),
        "implementation": row.get("implementation", ""),
        "implementation_version": row.get("implementation_version", ""),
        "variant": row.get("mlkem_variant", "ML-KEM-768"),
        "mlkem_variant": row.get("mlkem_variant", ""),
        "operation": operation,
        "iteration": _parse_number(row.get("iteration"), int),
        "clock_mhz": None,
        "flash_kb": None,
        "ram_kb": round(int(mem_bytes) / 1024.0, 1) if mem_bytes else 0.0,
        "keygen_cycles": int(ns_val * 2.0) if operation == "keygen" else 0,
        "encap_cycles": int(ns_val * 2.0) if operation == "encapsulation" else 0,
        "decap_cycles": int(ns_val * 2.0) if operation == "decapsulation" else 0,
        "keygen_us": us_val if operation == "keygen" else 0.0,
        "encap_us": us_val if operation == "encapsulation" else 0.0,
        "decap_us": us_val if operation == "decapsulation" else 0.0,
        "execution_time_ns": ns_val,
        "memory_bytes": mem_bytes,
        "success": row.get("success", "True"),
        "error_message": row.get("error_message", ""),
        "source_file": row.get("source_file", ""),
        "verification_status": "PASS" if str(row.get("success", "True")).lower() == "true" else ("OOM" if "oom" in str(row.get("error_message", "")).lower() else "FAIL"),
        "environment": row.get("environment", "unknown"),
        "measurement_type": row.get("measurement_type", "unknown"),
        "normalized_measurement_type": row.get("normalized_measurement_type", row.get("measurement_type", "unknown")),
    }


def _get_cached_benchmark_records() -> List[Dict[str, Any]]:
    global _BENCHMARK_RECORDS_CACHE
    if _BENCHMARK_RECORDS_CACHE is not None:
        return _BENCHMARK_RECORDS_CACHE
    rows = _load_dataset()
    _BENCHMARK_RECORDS_CACHE = [_benchmark_record(row, index) for index, row in enumerate(rows)]
    return _BENCHMARK_RECORDS_CACHE


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
    records = _get_cached_benchmark_records()
    return records[:1500] if type == "baseline" else records


@app.get("/api/processors", tags=["Hardware Profiles"])
@app.get("/processors", include_in_schema=False)
async def get_processors():
    return [
        {
            "mcu": "Intel Core i7-11800H",
            "name": "Intel Core i7-11800H Workstation",
            "core": "x86_64 (8 Cores / 16 Threads)",
            "architecture": "x86_64",
            "frequency": 4600,
            "ram": 16384,
            "flash": 512000,
            "voltage": "1.2V",
            "supportedVariants": ["ML-KEM-512", "ML-KEM-768", "ML-KEM-1024"],
            "description": "High-performance 11th Gen Intel Core i7 workstation processor with AVX2 vector extensions evaluated via WSL2 Ubuntu.",
            "features": ["AVX2 SIMD", "8 Cores / 16 Threads", "4.60 GHz Turbo", "WSL2 Linux Host"],
        },
        {
            "mcu": "AMD Ryzen 5 4600H",
            "name": "AMD Ryzen 5 4600H Mid-Range Laptop",
            "core": "x86_64 (6 Cores / 12 Threads)",
            "architecture": "x86_64",
            "frequency": 4000,
            "ram": 16384,
            "flash": 512000,
            "voltage": "1.2V",
            "supportedVariants": ["ML-KEM-512", "ML-KEM-768", "ML-KEM-1024"],
            "description": "Mainstream 6-core / 12-thread AMD Ryzen mobile processor with AVX2 vector units evaluated via WSL2 Ubuntu.",
            "features": ["AVX2 SIMD", "6 Cores / 12 Threads", "4.00 GHz Boost", "WSL2 Linux Host"],
        },
        {
            "mcu": "AMD Ryzen 3 7320U",
            "name": "AMD Ryzen 3 7320U Budget Laptop",
            "core": "x86_64 (4 Cores / 8 Threads)",
            "architecture": "x86_64",
            "frequency": 4100,
            "ram": 8192,
            "flash": 256000,
            "voltage": "1.2V",
            "supportedVariants": ["ML-KEM-512", "ML-KEM-768", "ML-KEM-1024"],
            "description": "Budget laptop processor (4 Cores / 8 Threads) evaluated via Linux 6.6 WSL2 Ubuntu with GCC 13.3.",
            "features": ["AVX2 SIMD", "4 Cores / 8 Threads", "4.10 GHz Boost", "8GB LPDDR5"],
        },
        {
            "mcu": "MediaTek Helio P65",
            "name": "MediaTek Helio P65 MT6768 (Vivo Y19)",
            "core": "ARM Cortex-A75 / A55",
            "architecture": "aarch64",
            "frequency": 2000,
            "ram": 4096,
            "flash": 128000,
            "voltage": "3.8V",
            "supportedVariants": ["ML-KEM-512", "ML-KEM-768", "ML-KEM-1024"],
            "description": "Physical 64-bit ARM mobile smartphone SoC evaluated natively via Android Termux and Clang 18.1.",
            "features": ["NEON SIMD", "ARMv8.2-A", "8 Cores (Big.LITTLE)", "Real Smartphone Silicon"],
        },
        {
            "mcu": "ESP8266EX",
            "name": "Espressif ESP8266EX IoT Microcontroller",
            "core": "Xtensa LX106",
            "architecture": "xtensa_lx106",
            "frequency": 80,
            "ram": 80,
            "flash": 4096,
            "voltage": "3.3V",
            "supportedVariants": ["ML-KEM-512", "ML-KEM-768"],
            "description": "Resource-constrained 32-bit RISC microcontroller with 80 KB SRAM evaluating FIPS 203 ML-KEM.",
            "features": ["80MHz Tensilica Core", "80KB SRAM", "Hardware WDT Guard", "Real IoT Silicon"],
        },
        {
            "mcu": "ESP32 Xtensa Dual-Core 240MHz",
            "name": "Espressif ESP32 Xtensa LX6 (Arduino Core)",
            "core": "Xtensa LX6 (2 Cores)",
            "architecture": "xtensa_lx6",
            "frequency": 240,
            "ram": 0,
            "flash": 0,
            "voltage": "3.3V",
            "supportedVariants": ["ML-KEM-512", "ML-KEM-768", "ML-KEM-1024"],
            "description": "Physical ESP32 Xtensa LX6 benchmark target using Arduino/FreeRTOS and mlkem-native v1.2.0.",
            "features": ["240MHz dual core", "Xtensa LX6", "Arduino Core", "Real IoT Silicon", "Dataset RAM field unavailable"],
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
    model_accuracy = 0.0
    report_path = Path(__file__).resolve().parent.parent / "data" / "processed" / "phase11_training" / "model_evaluation.json"
    if report_path.exists():
        try:
            with report_path.open(encoding="utf-8") as handle:
                model_accuracy = float(json.load(handle).get("selected_model_metrics", {}).get("accuracy", 0.0)) * 100
        except (OSError, ValueError, TypeError):
            model_accuracy = 0.0
    processors = {row.get("processor") for row in rows if row.get("processor")}
    return {
        "totalBenchmarks": len(rows),
        "totalPasses": len(successful_rows),
        "totalOOMs": sum(row.get("error_message") == "OOM" for row in rows),
        "passRatePercent": round(len(successful_rows) / len(rows) * 100, 2) if rows else 0.0,
        "avgEncapLatencyUs": round(sum(encapsulations) / len(encapsulations) / 1000, 2) if encapsulations else 0.0,
        "supportedProcessors": len(processors),
        "supportedPlatforms": len({row.get("environment") for row in rows}),
        "mlkemVariants": len({row.get("mlkem_variant") for row in rows}),
        "aiAccuracyPercent": round(model_accuracy, 2),
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
