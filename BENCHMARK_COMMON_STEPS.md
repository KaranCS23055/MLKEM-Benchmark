# 🚀 Universal ML-KEM Benchmarking Protocol (Common Steps Across All Devices)
### Standardized Empirical Execution Workflow for NIST FIPS 203 Evaluation

---

## 📌 The Unified Principle

Regardless of whether you are benchmarking a **high-end workstation (AMD Ryzen 5)**, a **laptop (Intel Core i7)**, an **ARM64 smartphone (MediaTek Helio P65)**, a **legacy 32-bit system**, or an **emulated RISC-V platform**, the benchmarking pipeline follows the **exact same universal 4-step workflow**.

```
+-----------------------------------------------------------------------------+
|                          UNIVERSAL 4-STEP WORKFLOW                          |
|                                                                             |
|   Step 1: Install Toolchain     ->  Compiler (GCC/Clang) + Git + Python3    |
|   Step 2: Clone Repository      ->  git clone <repo-url>                    |
|   Step 3: Execute Benchmark     ->  bash environments/<dir>/build_and_run*  |
|   Step 4: Aggregate Dataset     ->  python analysis/build_processed_dataset |
+-----------------------------------------------------------------------------+
```

---

## 🔒 What is 100% Identical & Standardized Across All Architectures

| Parameter / Dimension | Standard Value for ALL Devices | Scientific Rationale |
| :--- | :--- | :--- |
| **Cryptographic Source** | Pure C99 `mlkem-native v1.2.0` | Official NIST FIPS 203 reference implementation (PQ-Code Package) |
| **Compiler Optimization** | `-O3 -std=c99` | Highest standard production optimization level |
| **Input Entropy Source** | **32 Bytes (256 bits)** from OS Kernel RNG | High-entropy random seed via `getrandom()` / `/dev/urandom` |
| **Shared Secret Output** | **32 Bytes (256 bits)** | Fixed standard symmetric key material output |
| **Cryptographic Check** | `memcmp(shared_enc, shared_dec, 32) == 0` | 100% byte-for-byte correctness check asserted on every decapsulation |
| **Timer Mechanism** | High-resolution `CLOCK_MONOTONIC` | Nanosecond wall-clock timing; immune to NTP adjustments or sleep drift |
| **Sample Size** | **1,000 iterations per operation** | 3,000 rows per variant × 3 variants = **9,000 rows per device** |
| **Output Schema** | Unified 22-column CSV schema | Identical column headers and data types across all platforms |

---

## 📋 The 4 Common Steps (Run on Any Device)

### Step 1: Install Common Prerequisites (One-Time Setup)

Every target system requires only three fundamental tools:
1. A **C99-compliant compiler** (`gcc` for x86/RISC-V, or `clang` for ARM)
2. **Git** (to clone the source code and pinned commit)
3. **Python 3** (to execute the automatic post-benchmark validation script)

**Installation command for Linux / WSL2 / Ubuntu:**
```bash
sudo apt update && sudo apt install -y build-essential git python3
```

**Installation command for Android (Termux):**
```bash
pkg update && pkg install -y clang git python
```

---

### Step 2: Clone Repository & Enter Project Directory

```bash
git clone https://github.com/abhaykatre-dev/MLKEM-Benchmark.git
cd MLKEM-Benchmark
```

---

### Step 3: Run the Automated Benchmark Runner (Single Command)

Every architecture provides an automated shell runner and a configuration file in its respective `environments/` directory:

```bash
bash environments/<TARGET_FOLDER>/build_and_run_*.sh environments/<TARGET_FOLDER>/<CONFIG_FILE>.sh
```

#### Architecture Quick Reference:

| Target Platform | Folder (`environments/`) | Runner Command |
| :--- | :--- | :--- |
| **AMD Ryzen 5 (Multi-Core)** | `native_x86_64_mlkem_native/` | `bash environments/native_x86_64_mlkem_native/build_and_run_wsl.sh environments/native_x86_64_mlkem_native/benchmark_config_1000.sh` |
| **AMD Ryzen 5 (Single-Core Pin)** | `native_x86_64_single_core_mlkem_native/` | `bash environments/native_x86_64_single_core_mlkem_native/build_and_run_wsl.sh environments/native_x86_64_single_core_mlkem_native/benchmark_config_1000.sh` |
| **Intel Core i7-1255U** | `native_x86_64_mlkem_native/` | `bash environments/native_x86_64_mlkem_native/build_and_run_wsl.sh environments/native_x86_64_mlkem_native/benchmark_config_i7_1000.sh` |
| **Legacy 32-bit x86 (`-m32`)** | `native_x86_32_mlkem_native/` | `bash environments/native_x86_32_mlkem_native/build_and_run_wsl.sh environments/native_x86_32_mlkem_native/benchmark_config_1000.sh` |
| **Android ARM64 (Vivo Y19)** | `android_arm64/` | `bash environments/android_arm64/build_and_run_termux.sh environments/android_arm64/benchmark_config.sh` |
| **RISC-V 64-bit (QEMU Guest)** | `riscv64_qemu/` | `bash environments/riscv64_qemu/build_and_run_riscv64.sh environments/riscv64_qemu/benchmark_config.sh` |

#### What Happens Automatically in Step 3:
1. **CPU Auto-Detection**: Reads `/proc/cpuinfo` or hardware registers to extract the exact processor name and core count.
2. **Automated Compilation**: Builds 3 optimized binaries (ML-KEM-512, ML-KEM-768, ML-KEM-1024) in loop using `-O3`.
3. **Execution Loop**: Executes 1,000 KeyGen, 1,000 Encapsulation, and 1,000 Decapsulation cycles per variant.
4. **Cryptographic Self-Test**: Automatically asserts `memcmp(shared_enc, shared_dec, 32) == 0`.
5. **CSV Generation**: Emits raw data directly to `data/raw/` in the 22-column schema.
6. **Automatic Integrity Verification**: Executes the Python validator to verify row counts, positive timestamps, and error flags.

---

### Step 4: Ingest and Aggregate Data (Host Machine)

Once benchmarks are collected on the target device, synchronize raw CSVs to `data/raw/` and execute the master aggregation script:

```powershell
# On host machine (PowerShell in project root):
$env:PYTHONPATH="src"
python analysis/build_processed_dataset.py --overwrite
```

This single command:
- Ingests all raw CSVs in `data/raw/`.
- Computes mean, median, standard deviation, P95, P99, and throughput metrics.
- Updates `data/processed/phase11_statistics/benchmark_statistics.csv` and `observations.csv`.
- Generates SHA-256 manifest records in `data/processed/phase11_statistics/admission_manifest.json`.

---

## 📊 Summary of Master Verified Results

All empirical measurements using this common protocol demonstrate strictly monotonic scaling:

| Architecture | Parameter Set | KeyGen ($\mu s$) | Encap ($\mu s$) | Decap ($\mu s$) | Total Handshake | Monotonic Order ($512 < 768 < 1024$) |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| **AMD Ryzen 5 4600H (Multi-Core)** | ML-KEM-512<br>ML-KEM-768<br>ML-KEM-1024 | 22.55<br>34.15<br>52.63 | 23.03<br>36.71<br>58.00 | 28.24<br>43.34<br>65.75 | **73.82 $\mu s$ (0.074 ms)**<br>**114.20 $\mu s$ (0.114 ms)**<br>**176.39 $\mu s$ (0.176 ms)** | ✅ Confirmed<br>✅ Confirmed<br>✅ Confirmed |
| **AMD Ryzen 5 4600H (Single-Core Pin)** | ML-KEM-512<br>ML-KEM-768<br>ML-KEM-1024 | 23.38<br>38.46<br>57.92 | 24.17<br>39.75<br>61.30 | 31.06<br>47.63<br>69.89 | **78.60 $\mu s$ (0.079 ms)**<br>**125.84 $\mu s$ (0.126 ms)**<br>**189.11 $\mu s$ (0.189 ms)** | ✅ Confirmed<br>✅ Confirmed<br>✅ Confirmed |
| **MediaTek Helio P65 (ARM64 Smartphone)** | ML-KEM-512<br>ML-KEM-768<br>ML-KEM-1024 | 43.88<br>88.57<br>111.57 | 49.68<br>98.26<br>121.10 | 57.50<br>112.90<br>136.22 | **151.07 $\mu s$ (0.151 ms)**<br>**299.73 $\mu s$ (0.300 ms)**<br>**368.89 $\mu s$ (0.369 ms)** | ✅ Confirmed<br>✅ Confirmed<br>✅ Confirmed |
| **Legacy 32-bit x86 Mode (`gcc -m32`)** | ML-KEM-512<br>ML-KEM-768<br>ML-KEM-1024 | 72.41<br>111.68<br>181.75 | 75.50<br>117.59<br>187.47 | 93.97<br>142.07<br>221.39 | **241.88 $\mu s$ (0.242 ms)**<br>**371.33 $\mu s$ (0.371 ms)**<br>**590.62 $\mu s$ (0.591 ms)** | ✅ Confirmed<br>✅ Confirmed<br>✅ Confirmed |
| **RISC-V 64-bit Emulated Guest (QEMU)** | ML-KEM-512<br>ML-KEM-768<br>ML-KEM-1024 | 290.16<br>466.17<br>675.85 | 308.33<br>497.43<br>717.02 | 373.59<br>583.42<br>828.57 | **972.08 $\mu s$ (0.972 ms)**<br>**1,547.03 $\mu s$ (1.547 ms)**<br>**2,221.43 $\mu s$ (2.221 ms)** | ✅ Confirmed<br>✅ Confirmed<br>✅ Confirmed |

---

## 🧪 Automated Verification Suite

Run automated unit and integration tests across the framework:

```powershell
$env:PYTHONPATH="src"
python -m pytest tests/ -v
```
*(All 18 tests pass with 100% success rate).*
