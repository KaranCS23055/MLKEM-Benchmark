# 📊 NIST FIPS 203 ML-KEM Empirical Benchmark Dataset

[![Dataset Size](https://img.shields.io/badge/Active%20Measurements-45%2C000%20Rows-blue.svg)](raw/)
[![Integrity](https://img.shields.io/badge/SHA--256-Verified%20Manifests-emerald.svg)](metadata/)
[![Standard](https://img.shields.io/badge/NIST%20Standard-FIPS%20203%20ML--KEM-purple.svg)](https://csrc.nist.gov/pubs/fips/203/final)
[![Implementation](https://img.shields.io/badge/Source-mlkem--native%20v1.2.0%20(Pure%20C99)-amber.svg)](https://github.com/pq-code-package/mlkem-native)

---

## 📌 Dataset Overview

This directory contains the verified, append-only **empirical performance dataset** collected for the NIST FIPS 203 Module-Lattice-Based Key-Encapsulation Mechanism (ML-KEM) benchmark research project.

Every single measurement in this dataset is an **empirical execution record** produced by compiling and running the official **`mlkem-native v1.2.0`** C99 source code on real hardware and architecture emulators.

---

## 📁 Directory Structure

```text
data/
├── raw/                         # 15 immutable, verified raw CSV benchmark files (45,000 rows)
├── metadata/                    # SHA-256 checksums and execution environment manifests
└── processed/
    ├── phase11_statistics/      # Normalized observations and 45-group statistics summary
    │   ├── observations.csv     # Complete 45,000-row master empirical dataset
    │   ├── benchmark_statistics.csv # Grouped Mean, Median, StdDev, P95, P99 metrics
    │   └── admission_manifest.json
    └── phase11_training/        # Feature-engineered training data & model evaluation metrics
        ├── recommendation_candidates.csv
        └── model_evaluation.json
```

---

## 🗂️ Verified Raw Dataset Inventory (15 CSV Files — 45,000 Rows)

Each file contains **3,000 rows** (1,000 iterations × 3 operations: KeyGen, Encapsulation, Decapsulation):

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
| **TOTAL VERIFIED DATASET** | **5 Environments** | **4 Architectures**| **All 3 Variants** | **45,000** | **~18.5 MB** |

> **Note on Intel Core i7-1255U**: Previous historical Python-wrapper (`pqcrypto`) data has been quarantined. The clean pure C99 benchmark for Intel i7 can be generated via `environments/native_x86_64_mlkem_native/benchmark_config_i7_1000.sh` to add 9,000 additional verified rows.

---

## 📋 Data Schema & Column Definitions

Every measurement row in `data/raw/*.csv` and `data/processed/phase11_statistics/observations.csv` conforms to the following schema:

| Column Name | Data Type | Description | Example |
| :--- | :--- | :--- | :--- |
| `experiment_id` | String | Unique UUIDv4 identifying the benchmark campaign | `5e0ab786-6d00-46ab-9808-4da9d2ecf964` |
| `run_id` | String | Unique UUIDv4 identifier for the 1,000-iteration batch | `1c3c6121-6750-4f46-8236-3d186432544a` |
| `timestamp` | ISO-8601 | Exact UTC timestamp of run execution | `2026-09-12T17:48:13Z` |
| `environment` | String | Standardized environment identifier | `native_x86_64_wsl2_mlkem_native` |
| `measurement_type` | Enum | Measurement provenance (`REAL_HARDWARE`, `NATIVE_SOFTWARE`, `EMULATED`) | `NATIVE_SOFTWARE` |
| `architecture` | String | CPU instruction set architecture | `x86_64` |
| `processor` | String | Physical silicon processor / SoC model | `AMD Ryzen 5 4600H with Radeon Graphics` |
| `cpu_cores` | Integer | Number of logical/physical CPU cores available | `12` |
| `ram_mb` | Integer | System physical RAM capacity in Megabytes | `3620` |
| `os` | String | Operating system platform | `Linux 6.18.33.2-microsoft-standard-WSL2` |
| `compiler` | String | C compiler used for compilation | `gcc` |
| `compiler_version` | String | Compiler release version | `15.2.0` |
| `optimization_flags` | String | Compiler optimization level | `-O3 (WSL2 Ubuntu / GCC)` |
| `implementation` | String | Cryptographic library name | `mlkem-native` |
| `implementation_version` | String | Library release / commit hash | `v1.2.0 (2507ff79)` |
| `mlkem_variant` | Enum | NIST parameter set (`ML-KEM-512`, `ML-KEM-768`, `ML-KEM-1024`) | `ML-KEM-768` |
| `operation` | Enum | Cryptographic phase (`keygen`, `encapsulation`, `decapsulation`) | `encapsulation` |
| `iteration` | Integer | Repetition index (from 1 to 1,000) | `452` |
| `execution_time_ns` | Integer | Execution latency in nanoseconds (measured via POSIX clock) | `36710` |
| `memory_bytes` | Integer | Peak resident memory footprint in bytes | `1871872` |
| `success` | Boolean | Shared-secret cryptographic equivalence verification (`True`/`False`) | `True` |
| `error_message` | String | Error description if verification failed (empty on success) | `""` |

---

## 🔬 Measurement Methodology

1. **Timer Granularity**: Timings are captured using high-resolution monotonic clocks:
   ```c
   struct timespec value;
   clock_gettime(CLOCK_MONOTONIC, &value);
   long long ns = (long long)value.tv_sec * 1000000000LL + value.tv_nsec;
   ```
   This timer bypasses NTP adjustments and system sleep drift, providing exact nanosecond-level accuracy.
2. **Cryptographic Self-Checking**:
   After KeyGen, Encap, and Decap complete in each iteration, the C harness executes:
   ```c
   if (rc == 0 && memcmp(shared_enc, shared_dec, CRYPTO_BYTES) != 0) {
     rc = -1; // Flag cryptographic failure
   }
   ```
   A row is only recorded with `success=True` if the 32-byte shared secrets match byte-for-byte.
3. **Data Integrity**: Every raw CSV file has an accompanying SHA-256 checksum in `data/metadata/` to prevent silent corruption or tampering.
