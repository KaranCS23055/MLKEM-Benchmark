# 📊 NIST FIPS 203 ML-KEM Empirical Benchmark Dataset

[![Dataset Size](https://img.shields.io/badge/Active%20Measurements-36%2C540%20Rows-blue.svg)](raw/)
[![Integrity](https://img.shields.io/badge/SHA--256-Verified%20Manifests-emerald.svg)](metadata/)
[![Standard](https://img.shields.io/badge/NIST%20Standard-FIPS%20203%20ML--KEM-purple.svg)](https://csrc.nist.gov/pubs/fips/203/final)
[![Implementation](https://img.shields.io/badge/Source-mlkem--native%20v1.2.0%20(Pure%20C99)-amber.svg)](https://github.com/pq-code-package/mlkem-native)
[![Targets](https://img.shields.io/badge/Hardware%20Targets-5%20Physical%20Silicon-emerald.svg)](../README.md)

---

## 📌 Dataset Overview

This directory contains the verified, append-only **empirical performance dataset** collected for the NIST FIPS 203 Module-Lattice-Based Key-Encapsulation Mechanism (ML-KEM) benchmark research project.

Every measurement in this dataset is an **empirical execution record** produced by compiling and running the official **`mlkem-native v1.2.0`** C99 source code on **real physical hardware targets only** (no software emulation, no virtual machines).

---

## 📁 Directory Structure

```text
data/
├── raw/                         # 14 immutable, verified raw CSV benchmark files (36,540 rows)
├── metadata/                    # SHA-256 checksums and execution environment manifests
└── processed/
    ├── phase11_statistics/      # Normalized observations and 36-group statistics summary
    │   ├── observations.csv     # Complete 36,540-row master empirical dataset
    │   ├── benchmark_statistics.csv # Grouped Mean, Median, StdDev, P95, P99 metrics
    │   └── admission_manifest.json
    └── phase11_training/        # Feature-engineered training data & model evaluation metrics
        ├── recommendation_candidates.csv
        ├── training_manifest.json
        └── model_evaluation.json
```

---

## 🗂️ Verified Raw Dataset Inventory (14 CSV Files — 36,540 Rows)

Across **5 real physical silicon targets**:

| File Name | Target Hardware / Platform | Architecture | Variant | Rows | Measurements |
| :--- | :--- | :---: | :---: | :---: | :---: |
| `native_x86_64_mlkem_native_mlkem_512_20260913T072724Z.csv` | Intel Core i7-11800H (WSL2 Ubuntu) | `x86_64` | ML-KEM-512 | 3,000 | 1,000 iterations × 3 ops |
| `native_x86_64_mlkem_native_mlkem_768_20260913T072724Z.csv` | Intel Core i7-11800H (WSL2 Ubuntu) | `x86_64` | ML-KEM-768 | 3,000 | 1,000 iterations × 3 ops |
| `native_x86_64_mlkem_native_mlkem_1024_20260913T072724Z.csv` | Intel Core i7-11800H (WSL2 Ubuntu) | `x86_64` | ML-KEM-1024 | 3,000 | 1,000 iterations × 3 ops |
| `native_x86_64_mlkem_native_mlkem_512_20260912T174813Z.csv` | AMD Ryzen 5 4600H (WSL2 Ubuntu) | `x86_64` | ML-KEM-512 | 3,000 | 1,000 iterations × 3 ops |
| `native_x86_64_mlkem_native_mlkem_768_20260912T174813Z.csv` | AMD Ryzen 5 4600H (WSL2 Ubuntu) | `x86_64` | ML-KEM-768 | 3,000 | 1,000 iterations × 3 ops |
| `native_x86_64_mlkem_native_mlkem_1024_20260912T174813Z.csv` | AMD Ryzen 5 4600H (WSL2 Ubuntu) | `x86_64` | ML-KEM-1024 | 3,000 | 1,000 iterations × 3 ops |
| `native_x86_64_mlkem_native_mlkem_512_20260915T105249Z.csv` | AMD Ryzen 3 7320U (WSL2 Ubuntu) | `x86_64` | ML-KEM-512 | 3,000 | 1,000 iterations × 3 ops |
| `native_x86_64_mlkem_native_mlkem_768_20260915T105249Z.csv` | AMD Ryzen 3 7320U (WSL2 Ubuntu) | `x86_64` | ML-KEM-768 | 3,000 | 1,000 iterations × 3 ops |
| `native_x86_64_mlkem_native_mlkem_1024_20260915T105249Z.csv` | AMD Ryzen 3 7320U (WSL2 Ubuntu) | `x86_64` | ML-KEM-1024 | 3,000 | 1,000 iterations × 3 ops |
| `android_vivo_y19_mlkem_512_20260812T204747Z.csv` | MediaTek Helio P65 / Vivo Y19 (Termux) | `aarch64` | ML-KEM-512 | 3,000 | 1,000 iterations × 3 ops |
| `android_vivo_y19_mlkem_768_20260812T204804Z.csv` | MediaTek Helio P65 / Vivo Y19 (Termux) | `aarch64` | ML-KEM-768 | 3,000 | 1,000 iterations × 3 ops |
| `android_vivo_y19_mlkem_1024_20260812T204813Z.csv` | MediaTek Helio P65 / Vivo Y19 (Termux) | `aarch64` | ML-KEM-1024 | 3,000 | 1,000 iterations × 3 ops |
| `esp8266_xtensa_lx106_arduino_mlkem_512_20260915T161500Z.csv` | ESP8266EX Xtensa LX106 @ 80MHz | `xtensa_lx106` | ML-KEM-512 | 270 | 90 iterations × 3 ops |
| `esp8266_xtensa_lx106_arduino_mlkem_768_20260915T180200Z.csv` | ESP8266EX Xtensa LX106 @ 80MHz | `xtensa_lx106` | ML-KEM-768 | 270 | 90 iterations × 3 ops |
| **TOTAL DATASET** | **5 Physical Hardware Targets** | **3 Architectures** | **FIPS 203** | **36,540** | **100% Cryptographic Verification** |

> [!IMPORTANT]
> **Physical Silicon Policy**: All measurements strictly evaluate genuine physical silicon targets: high-performance workstation, mid-range laptop, budget laptop, mobile smartphone SoC, and an embedded IoT microcontroller.
>
> **CPU Core Schema Note**: In all raw CSVs, `cpu_cores` represents the physical CPU core count (e.g. `4` for AMD Ryzen 3 7320U, `6` for AMD Ryzen 5 4600H, `8` for Intel i7-11800H and MediaTek Helio P65, `1` for ESP8266EX).

---

## 📋 Data Schema & Column Definitions

Every measurement row in `data/raw/*.csv` and `data/processed/phase11_statistics/observations.csv` conforms to the 22-column schema:

| Column Name | Data Type | Description | Example |
| :--- | :--- | :--- | :--- |
| `experiment_id` | String | Unique UUIDv4 identifying the benchmark campaign | `5e0ab786-6d00-46ab-9808-4da9d2ecf964` |
| `run_id` | String | Unique UUIDv4 identifier for the iteration batch | `1c3c6121-6750-4f46-8236-3d186432544a` |
| `timestamp` | ISO-8601 | Exact UTC timestamp of run execution | `2026-09-15T10:52:49Z` |
| `environment` | String | Standardized environment identifier | `native_x86_64_ryzen3_7320u_wsl2_mlkem_native` |
| `measurement_type` | Enum | Measurement provenance (`NATIVE_HARDWARE` / `NATIVE_SOFTWARE`) | `NATIVE_SOFTWARE` |
| `architecture` | String | CPU instruction set architecture (`x86_64`, `aarch64`, `xtensa_lx106`) | `x86_64` |
| `processor` | String | Physical silicon processor / SoC model | `AMD Ryzen 3 7320U with Radeon Graphics` |
| `cpu_cores` | Integer | Physical CPU core count | `4` |
| `ram_mb` | Integer | System physical RAM capacity in Megabytes (0 for microcontrollers < 1 MB) | `3534` |
| `os` | String | Operating system platform | `Linux 6.6.87.2-microsoft-standard-WSL2` |
| `compiler` | String | C compiler used for compilation | `gcc` |
| `compiler_version` | String | Compiler release version | `13.3.0` |
| `optimization_flags` | String | Compiler optimization level | `-O3 (WSL2 Ubuntu / GCC)` |
| `implementation` | String | Cryptographic library name | `mlkem-native` |
| `implementation_version` | String | Library release / commit hash | `v1.2.0 (UNKNOWN)` |
| `mlkem_variant` | Enum | NIST parameter set (`ML-KEM-512`, `ML-KEM-768`, `ML-KEM-1024`) | `ML-KEM-768` |
| `operation` | Enum | Cryptographic phase (`keygen`, `encapsulation`, `decapsulation`) | `encapsulation` |
| `iteration` | Integer | Repetition index | `42` |
| `execution_time_ns` | Integer | Execution latency in nanoseconds | `56558` |
| `memory_bytes` | Integer | Resident memory / free heap footprint in bytes | `1572864` |
| `success` | Boolean | Shared-secret cryptographic equivalence verification (`True`/`False`) | `True` |
| `error_message` | String | Error description if verification failed (empty on success) | `""` |