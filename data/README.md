# 📊 NIST FIPS 203 ML-KEM Empirical Benchmark Dataset

[![Dataset Size](https://img.shields.io/badge/Total%20Measurements-63%2C000%20Rows-blue.svg)](raw/)
[![Integrity](https://img.shields.io/badge/SHA--256-Verified%20Manifests-emerald.svg)](metadata/)
[![Standard](https://img.shields.io/badge/NIST%20Standard-FIPS%20203%20ML--KEM-purple.svg)](https://csrc.nist.gov/pubs/fips/203/final)
[![Implementation](https://img.shields.io/badge/Source-mlkem--native%20v1.2.0-amber.svg)](https://github.com/pq-code-package/mlkem-native)

---

## 📌 Dataset Overview

This directory contains the complete, append-only **empirical performance dataset** collected for the NIST FIPS 203 Module-Lattice-Based Key-Encapsulation Mechanism (ML-KEM) benchmark research project.

Every single measurement in this dataset is an **empirical execution record** produced by compiling and running the official **`mlkem-native v1.2.0`** C99 source code (commit `0ba906cb14b1c241476134d7403a811b382ca498`) on real hardware and architecture emulators.

---

## 📁 Directory Structure

```text
data/
├── raw/                         # 17 immutable, append-only CSV benchmark files (63,000 rows)
├── metadata/                    # SHA-256 checksums and execution environment manifests
├── processed/
│   ├── phase11_statistics/      # Normalized observations and 63-group statistics summary
│   │   ├── observations.csv     # Complete 63,000-row merged master dataset
│   │   ├── benchmark_statistics.csv # Grouped Mean, Median, StdDev, P95, P99 metrics
│   │   └── admission_manifest.json
│   └── phase11_training/        # Feature-engineered training data & model evaluation metrics
│       ├── recommendation_candidates.csv
│       └── model_evaluation.json
└── archive/                     # Historical calibration runs and quarantined legacy data
```

---

## 🗂️ Raw Dataset Inventory (17 CSV Files — 63,000 Rows)

Each file contains **3,000 rows** (or 9,000 rows for consolidated 3-variant runs):

| File Name | Hardware / SoC | Architecture | Variant | Rows | Size |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `android_vivo_y19_mlkem_512_*.csv` | MediaTek Helio P65 | `aarch64` | ML-KEM-512 | 3,000 | 1.09 MB |
| `android_vivo_y19_mlkem_768_*.csv` | MediaTek Helio P65 | `aarch64` | ML-KEM-768 | 3,000 | 1.09 MB |
| `android_vivo_y19_mlkem_1024_*.csv` | MediaTek Helio P65 | `aarch64` | ML-KEM-1024 | 3,000 | 1.10 MB |
| `native_x86_64_mlkem_native_mlkem_512_*.csv` | AMD Ryzen 5 4600H | `x86_64` | ML-KEM-512 | 3,000 | 1.24 MB |
| `native_x86_64_mlkem_native_mlkem_768_*.csv` | AMD Ryzen 5 4600H | `x86_64` | ML-KEM-768 | 3,000 | 1.24 MB |
| `native_x86_64_mlkem_native_mlkem_1024_*.csv` | AMD Ryzen 5 4600H | `x86_64` | ML-KEM-1024 | 3,000 | 1.24 MB |
| `native_x86_64_single_core_*_512_*.csv` | AMD Ryzen 5 (taskset -c 0) | `x86_64` | ML-KEM-512 | 3,000 | 1.35 MB |
| `native_x86_64_single_core_*_768_*.csv` | AMD Ryzen 5 (taskset -c 0) | `x86_64` | ML-KEM-768 | 3,000 | 1.35 MB |
| `native_x86_64_single_core_*_1024_*.csv`| AMD Ryzen 5 (taskset -c 0) | `x86_64` | ML-KEM-1024 | 3,000 | 1.35 MB |
| `native_x86_32_mlkem_native_mlkem_512_*.csv` | 32-bit x86 (i686 Multilib) | `x86` | ML-KEM-512 | 3,000 | 1.28 MB |
| `native_x86_32_mlkem_native_mlkem_768_*.csv` | 32-bit x86 (i686 Multilib) | `x86` | ML-KEM-768 | 3,000 | 1.28 MB |
| `native_x86_32_mlkem_native_mlkem_1024_*.csv`| 32-bit x86 (i686 Multilib) | `x86` | ML-KEM-1024 | 3,000 | 1.28 MB |
| `riscv64_qemu_mlkem_512_*.csv` | RV64GC Linux Guest | `riscv64` | ML-KEM-512 | 3,000 | 1.07 MB |
| `riscv64_qemu_mlkem_768_*.csv` | RV64GC Linux Guest | `riscv64` | ML-KEM-768 | 3,000 | 1.07 MB |
| `riscv64_qemu_mlkem_1024_*.csv`| RV64GC Linux Guest | `riscv64` | ML-KEM-1024 | 3,000 | 1.07 MB |
| `native_x86_64_i7_1255u_windows_*.csv` | Intel i7-1255U (Multi-core) | `x86_64` | All 3 Variants | 9,000 | 2.50 MB |
| `native_x86_64_i7_1255u_windows_single_core_*.csv` | Intel i7-1255U (P-Core Affinity 0x1) | `x86_64` | All 3 Variants | 9,000 | 2.50 MB |
| **TOTAL RAW DATASET** | **7 Environments** | **4 Architectures**| **All 3 Variants** | **63,000** | **~25.0 MB** |

---

## 📋 Data Schema & Column Definitions

Every measurement row in `data/raw/*.csv` and `data/processed/phase11_statistics/observations.csv` conforms to the following schema:

| Column Name | Data Type | Description | Example |
| :--- | :--- | :--- | :--- |
| `experiment_id` | String | Unique hash identifying the benchmark campaign | `exp_mlkem_native_arm64` |
| `run_id` | String | Unique run identifier for the 1,000-iteration batch | `run_20260812T204747Z` |
| `timestamp` | ISO-8601 | Exact UTC timestamp of run execution | `2026-08-12T20:47:47Z` |
| `environment` | String | Standardized environment identifier | `vivo_y19_aarch64` |
| `measurement_type` | Enum | Measurement provenance (`REAL_HARDWARE`, `NATIVE_SOFTWARE`, `EMULATED`) | `REAL_HARDWARE` |
| `architecture` | String | CPU instruction set architecture | `aarch64` |
| `processor` | String | Physical silicon processor / SoC model | `MediaTek Helio P65` |
| `cpu_cores` | Integer | Number of logical/physical CPU cores available | `8` |
| `ram_mb` | Integer | System physical RAM capacity in Megabytes | `4096` |
| `os` | String | Operating system platform | `Linux (Android Termux)` |
| `compiler` | String | C compiler used for compilation | `clang` |
| `compiler_version` | String | Compiler release version | `18.1.8` |
| `optimization_flags` | String | Compiler optimization level | `-O3` |
| `implementation` | String | Cryptographic library name | `mlkem-native` |
| `implementation_version` | String | Library release / commit hash | `v1.2.0 (0ba906cb)` |
| `mlkem_variant` | Enum | NIST parameter set (`ML-KEM-512`, `ML-KEM-768`, `ML-KEM-1024`) | `ML-KEM-768` |
| `operation` | Enum | Cryptographic phase (`keygen`, `encapsulation`, `decapsulation`) | `encapsulation` |
| `iteration` | Integer | Repetition index (from 1 to 1,000) | `452` |
| `execution_time_ns` | Float | Execution latency in nanoseconds (measured via POSIX clock) | `98260.0` |
| `memory_bytes` | Integer | Peak resident memory footprint in bytes | `3612672` |
| `success` | Boolean | Shared-secret cryptographic equivalence verification (`True`/`False`) | `True` |
| `error_message` | String | Error description if verification failed (empty on success) | `""` |

---

## 🔬 Measurement Methodology

1. **Timer Granularity**: Timings are captured using the POSIX system call:
   ```c
   clock_gettime(CLOCK_MONOTONIC_RAW, &start_time);
   // Cryptographic operation
   clock_gettime(CLOCK_MONOTONIC_RAW, &end_time);
   ```
   This timer bypasses NTP adjustments and system sleep drift, providing exact nanosecond-level accuracy.
2. **Cryptographic Self-Checking**:
   After KeyGen, Encap, and Decap complete in each iteration, the C harness executes:
   ```c
   assert(memcmp(shared_secret_encap, shared_secret_decap, 32) == 0);
   ```
   A row is only recorded with `success=True` if the 32-byte shared secrets match byte-for-byte.
3. **Data Integrity**: Every raw CSV file has an accompanying SHA-256 checksum in `data/metadata/` to prevent silent corruption or tampering.
