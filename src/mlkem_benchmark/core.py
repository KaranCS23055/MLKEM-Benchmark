"""Native ML-KEM benchmark utilities.

This module invokes pqcrypto's native ML-KEM implementation directly.
It does not implement or modify ML-KEM mathematics.
"""

from __future__ import annotations

import csv
import ctypes
import json
import os
import platform
import sys
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from time import perf_counter_ns
from typing import Any

from importlib.metadata import version

from pqcrypto.kem import ml_kem_1024, ml_kem_512, ml_kem_768

try:
    import resource
except ImportError:  # Windows does not expose POSIX resource accounting.
    resource = None

REQUIRED_COLUMNS = [
    "experiment_id", "run_id", "timestamp", "environment", "measurement_type",
    "architecture", "processor", "cpu_cores", "ram_mb", "os", "compiler",
    "compiler_version", "optimization_flags", "implementation",
    "implementation_version", "mlkem_variant", "operation", "iteration",
    "execution_time_ns", "memory_bytes", "success", "error_message",
]

VARIANT_MODULES = {
    "ML-KEM-512": ml_kem_512,
    "ML-KEM-768": ml_kem_768,
    "ML-KEM-1024": ml_kem_1024,
}
VALID_OPERATIONS = {"keygen", "encapsulation", "decapsulation"}


@dataclass(frozen=True)
class BenchmarkConfig:
    environment: dict[str, Any]
    implementation: dict[str, str]
    variants: list[str]
    operations: list[str]
    iterations: int


def load_config(path: Path) -> BenchmarkConfig:
    """Load and validate a benchmark JSON configuration."""
    with path.open(encoding="utf-8") as handle:
        payload = json.load(handle)

    required = {"environment", "implementation", "variants", "operations", "iterations"}
    missing = required - payload.keys()
    if missing:
        raise ValueError(f"Configuration missing fields: {', '.join(sorted(missing))}")

    iterations = payload["iterations"]
    if not isinstance(iterations, int) or iterations <= 0:
        raise ValueError("iterations must be a positive integer")
    if not isinstance(payload["environment"], dict) or not isinstance(payload["implementation"], dict):
        raise ValueError("environment and implementation must be objects")
    for name in ("name", "type", "architecture"):
        if not payload["environment"].get(name):
            raise ValueError(f"environment.{name} is required")
    affinity_mask = payload["environment"].get("cpu_affinity_mask")
    if affinity_mask is not None and (not isinstance(affinity_mask, int) or affinity_mask <= 0):
        raise ValueError("environment.cpu_affinity_mask must be a positive integer when set")
    for name in ("name", "version"):
        if not payload["implementation"].get(name):
            raise ValueError(f"implementation.{name} is required")
    if not set(payload["variants"]).issubset(VARIANT_MODULES):
        raise ValueError("Unsupported ML-KEM variant in configuration")
    if not payload["variants"]:
        raise ValueError("At least one ML-KEM variant is required")
    if not set(payload["operations"]).issubset(VALID_OPERATIONS):
        raise ValueError("Unsupported operation in configuration")
    if not payload["operations"]:
        raise ValueError("At least one operation is required")

    return BenchmarkConfig(**{key: payload[key] for key in required})


def _windows_memory() -> tuple[int | None, int | None]:
    """Return total RAM and current process working set on Windows, in bytes."""
    class MEMORYSTATUSEX(ctypes.Structure):
        _fields_ = [
            ("dwLength", ctypes.c_ulong), ("dwMemoryLoad", ctypes.c_ulong),
            ("ullTotalPhys", ctypes.c_ulonglong), ("ullAvailPhys", ctypes.c_ulonglong),
            ("ullTotalPageFile", ctypes.c_ulonglong), ("ullAvailPageFile", ctypes.c_ulonglong),
            ("ullTotalVirtual", ctypes.c_ulonglong), ("ullAvailVirtual", ctypes.c_ulonglong),
            ("ullAvailExtendedVirtual", ctypes.c_ulonglong),
        ]

    class PROCESS_MEMORY_COUNTERS_EX(ctypes.Structure):
        _fields_ = [
            ("cb", ctypes.c_ulong), ("PageFaultCount", ctypes.c_ulong),
            ("PeakWorkingSetSize", ctypes.c_size_t), ("WorkingSetSize", ctypes.c_size_t),
            ("QuotaPeakPagedPoolUsage", ctypes.c_size_t), ("QuotaPagedPoolUsage", ctypes.c_size_t),
            ("QuotaPeakNonPagedPoolUsage", ctypes.c_size_t), ("QuotaNonPagedPoolUsage", ctypes.c_size_t),
            ("PagefileUsage", ctypes.c_size_t), ("PeakPagefileUsage", ctypes.c_size_t),
            ("PrivateUsage", ctypes.c_size_t),
        ]

    memory = MEMORYSTATUSEX()
    memory.dwLength = ctypes.sizeof(memory)
    total = None
    if ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(memory)):
        total = int(memory.ullTotalPhys)

    counters = PROCESS_MEMORY_COUNTERS_EX()
    counters.cb = ctypes.sizeof(counters)
    kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
    psapi = ctypes.WinDLL("psapi", use_last_error=True)
    kernel32.GetCurrentProcess.restype = ctypes.c_void_p
    psapi.GetProcessMemoryInfo.argtypes = [ctypes.c_void_p, ctypes.c_void_p, ctypes.c_ulong]
    psapi.GetProcessMemoryInfo.restype = ctypes.c_int
    process = kernel32.GetCurrentProcess()
    working_set = None
    if psapi.GetProcessMemoryInfo(process, ctypes.byref(counters), counters.cb):
        working_set = int(counters.WorkingSetSize)
    return total, working_set


def apply_environment_controls(config: BenchmarkConfig) -> dict[str, Any]:
    """Apply only explicitly configured, process-local controls."""
    mask = config.environment.get("cpu_affinity_mask")
    if mask is None:
        return {"cpu_affinity_applied": False}
    if os.name != "nt":
        raise RuntimeError("cpu_affinity_mask is currently supported only on Windows")
    kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
    kernel32.GetCurrentProcess.restype = ctypes.c_void_p
    kernel32.GetProcessAffinityMask.argtypes = [
        ctypes.c_void_p, ctypes.POINTER(ctypes.c_size_t), ctypes.POINTER(ctypes.c_size_t),
    ]
    kernel32.GetProcessAffinityMask.restype = ctypes.c_int
    kernel32.SetProcessAffinityMask.argtypes = [ctypes.c_void_p, ctypes.c_size_t]
    kernel32.SetProcessAffinityMask.restype = ctypes.c_int
    process = kernel32.GetCurrentProcess()
    current_mask, system_mask = ctypes.c_size_t(), ctypes.c_size_t()
    if not kernel32.GetProcessAffinityMask(process, ctypes.byref(current_mask), ctypes.byref(system_mask)):
        raise OSError(ctypes.get_last_error(), "GetProcessAffinityMask failed")
    if mask & system_mask.value != mask:
        raise ValueError(f"cpu_affinity_mask {mask:#x} is not a subset of system mask {system_mask.value:#x}")
    if not kernel32.SetProcessAffinityMask(process, mask):
        raise OSError(ctypes.get_last_error(), "SetProcessAffinityMask failed")
    return {
        "cpu_affinity_applied": True,
        "requested_cpu_affinity_mask": f"{mask:#x}",
        "available_system_affinity_mask": f"{system_mask.value:#x}",
        "controlled_logical_cpus": mask.bit_count(),
    }


def environment_metadata(config: BenchmarkConfig, controls: dict[str, Any]) -> dict[str, Any]:
    """Collect reproducibility metadata without requiring external system tools."""
    total_ram, _ = _windows_memory() if os.name == "nt" else (None, None)
    return {
        "environment": config.environment["name"],
        "measurement_type": config.environment["type"],
        "architecture": config.environment["architecture"],
        "processor": platform.processor() or "unknown (not exposed by Python)",
        "cpu_cores": os.cpu_count() or 0,
        "ram_mb": round(total_ram / (1024 * 1024)) if total_ram else None,
        "os": platform.platform(),
        "compiler": "N/A (prebuilt Python extension wheel)",
        "compiler_version": "N/A",
        "optimization_flags": "N/A (prebuilt wheel)",
        "implementation": config.implementation["name"],
        "implementation_version": version("pqcrypto"),
        "implementation_backend": config.implementation.get("backend", ""),
        "python_version": sys.version,
        "machine": platform.machine(),
        "environment_controls": controls,
    }


def _memory_bytes() -> int | None:
    if os.name == "nt":
        return _windows_memory()[1]
    # Linux/Android ru_maxrss is the process maximum resident-set size in KiB.
    # It is recorded as a process-level high-water mark, not per-operation allocation.
    if resource is None:
        return None
    return int(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss) * 1024


def _base_row(metadata: dict[str, Any], experiment_id: str, run_id: str,
              variant: str, operation: str, iteration: int) -> dict[str, Any]:
    return {
        "experiment_id": experiment_id,
        "run_id": run_id,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "environment": metadata["environment"],
        "measurement_type": metadata["measurement_type"],
        "architecture": metadata["architecture"],
        "processor": metadata["processor"],
        "cpu_cores": metadata["cpu_cores"],
        "ram_mb": metadata["ram_mb"],
        "os": metadata["os"],
        "compiler": metadata["compiler"],
        "compiler_version": metadata["compiler_version"],
        "optimization_flags": metadata["optimization_flags"],
        "implementation": metadata["implementation"],
        "implementation_version": metadata["implementation_version"],
        "mlkem_variant": variant,
        "operation": operation,
        "iteration": iteration,
        "execution_time_ns": None,
        "memory_bytes": None,
        "success": False,
        "error_message": "",
    }


def _measure(operation_fn) -> tuple[int, Any]:
    start = perf_counter_ns()
    result = operation_fn()
    return perf_counter_ns() - start, result


def _artifact_prefix(environment_name: str) -> str:
    """Return a filesystem-safe, provenance-preserving environment prefix."""
    return "".join(character if character.isalnum() else "_" for character in environment_name).strip("_")


def run_benchmark(config: BenchmarkConfig, raw_dir: Path, metadata_dir: Path) -> tuple[Path, Path, int]:
    """Run real native ML-KEM operations and write a new append-only CSV."""
    raw_dir.mkdir(parents=True, exist_ok=True)
    metadata_dir.mkdir(parents=True, exist_ok=True)
    experiment_id = str(uuid.uuid4())
    run_id = str(uuid.uuid4())
    controls = apply_environment_controls(config)
    metadata = environment_metadata(config, controls)
    timestamp_token = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    prefix = _artifact_prefix(config.environment["name"])
    raw_path = raw_dir / f"{prefix}_{timestamp_token}_{run_id}.csv"
    manifest_path = metadata_dir / f"{prefix}_{timestamp_token}_{run_id}.json"
    if raw_path.exists() or manifest_path.exists():
        raise FileExistsError("Refusing to overwrite an existing benchmark artifact")

    rows: list[dict[str, Any]] = []
    for variant in config.variants:
        kem = VARIANT_MODULES[variant]
        for iteration in range(1, config.iterations + 1):
            if "keygen" in config.operations:
                row = _base_row(metadata, experiment_id, run_id, variant, "keygen", iteration)
                try:
                    elapsed, keypair = _measure(kem.generate_keypair)
                    public_key, secret_key = keypair
                    if not public_key or not secret_key:
                        raise ValueError("key generation returned empty key material")
                    row.update(execution_time_ns=elapsed, memory_bytes=_memory_bytes(), success=True)
                except Exception as exc:  # Row retained so failures cannot be hidden.
                    row["error_message"] = f"{type(exc).__name__}: {exc}"
                rows.append(row)

            recipient_public, recipient_secret = kem.generate_keypair()
            if "encapsulation" in config.operations:
                row = _base_row(metadata, experiment_id, run_id, variant, "encapsulation", iteration)
                try:
                    elapsed, encapsulation = _measure(lambda: kem.encrypt(recipient_public))
                    ciphertext, shared_secret = encapsulation
                    row.update(execution_time_ns=elapsed, memory_bytes=_memory_bytes(), success=True)
                except Exception as exc:
                    row["error_message"] = f"{type(exc).__name__}: {exc}"
                rows.append(row)
            else:
                ciphertext, shared_secret = kem.encrypt(recipient_public)

            if "decapsulation" in config.operations:
                row = _base_row(metadata, experiment_id, run_id, variant, "decapsulation", iteration)
                try:
                    elapsed, recovered_secret = _measure(lambda: kem.decrypt(recipient_secret, ciphertext))
                    if recovered_secret != shared_secret:
                        raise ValueError("decapsulated shared secret does not match encapsulated shared secret")
                    row.update(execution_time_ns=elapsed, memory_bytes=_memory_bytes(), success=True)
                except Exception as exc:
                    row["error_message"] = f"{type(exc).__name__}: {exc}"
                rows.append(row)

    with raw_path.open("x", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=REQUIRED_COLUMNS, extrasaction="raise")
        writer.writeheader()
        writer.writerows(rows)

    manifest = {
        "experiment_id": experiment_id,
        "run_id": run_id,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "config": {
            "environment": config.environment, "implementation": config.implementation,
            "variants": config.variants, "operations": config.operations,
            "iterations": config.iterations,
        },
        "environment_metadata": metadata,
        "raw_data_file": str(raw_path),
        "measurement_count": len(rows),
        "memory_bytes_definition": (
            "Post-operation process working-set size, in bytes (Windows); "
            "or process maximum resident-set size high-water mark, in bytes (Linux/Android)."
        ),
        "timing_definition": "perf_counter_ns elapsed time around the specified ML-KEM operation only; setup is excluded for encapsulation and decapsulation.",
        "random_seed": "Not set; the implementation uses its cryptographic system RNG.",
    }
    with manifest_path.open("x", encoding="utf-8") as handle:
        json.dump(manifest, handle, indent=2)
        handle.write("\n")
    return raw_path, manifest_path, len(rows)
