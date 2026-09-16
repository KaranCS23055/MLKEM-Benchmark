# Post-Quantum ML-KEM Benchmarking Framework & AI Recommendation Engine
### NIST FIPS 203 Standard Evaluation Across Multi-Architecture Hardware

[![NIST Standard](https://img.shields.io/badge/NIST-FIPS%20203%20ML--KEM-blue.svg)](https://csrc.nist.gov/pubs/fips/203/final)
[![Implementation](https://img.shields.io/badge/C99%20Source-mlkem--native%20v1.2.0-emerald.svg)](https://github.com/pq-code-package/mlkem-native)
[![Dataset](https://img.shields.io/badge/Empirical%20Dataset-37%2C914%20Rows-purple.svg)](data/README.md)
[![Verification](https://img.shields.io/badge/Cryptographic%20Verification-100%25%20memcmp%20Match-brightgreen.svg)](environments/)
[![ML Model](https://img.shields.io/badge/ML%20Surrogate-Random%20Forest-amber.svg)](ml/artifacts/)
[![Tests](https://img.shields.io/badge/Tests-19%2F19%20Passing-brightgreen.svg)](tests/)

---

## 📌 Executive Overview & Motivation

With the emergence of large-scale **Quantum Computing**, classical public-key cryptosystems based on integer factorization (RSA) and discrete logarithms over elliptic curves (ECDSA, ECDH) are vulnerable to polynomial-time key recovery via **Shor's Algorithm**.

To establish post-quantum confidentiality, the National Institute of Standards and Technology (**NIST**) published **FIPS 203: Module-Lattice-Based Key-Encapsulation Mechanism (ML-KEM)** in August 2024. ML-KEM is founded on the hardness of the Module Learning With Errors (**M-LWE**) problem over polynomial rings:
- **ML-KEM-512** (NIST Security Category 1 — AES-128 equivalent)
- **ML-KEM-768** (NIST Security Category 3 — AES-192 equivalent)
- **ML-KEM-1024** (NIST Security Category 5 — AES-256 equivalent)

On resource-constrained embedded systems, edge microcontrollers, and mobile devices, selecting an inappropriately high ML-KEM variant can result in **stack memory exhaustion (Out-of-Memory / OOM crashes / WDT resets)** or **severe violations of real-time latency budgets**.

### 🎯 Research Objectives
1. **Empirical Benchmarking**: Standardized benchmarks of `mlkem-native v1.2.0` across **6 processor/device profiles**: Intel Core i7-11800H, AMD Ryzen 5 4600H, AMD Ryzen 3 7320U, MediaTek Helio P65, Espressif ESP8266EX, and Espressif ESP32 Xtensa LX6. The x86_64 records are native software execution profiles; ARM64 and Xtensa records are physical hardware runs.
2. **Standardized Methodology**: Operation-only timing, shared-secret cryptographic integrity verification, and strict 22-column raw schema parity across **37,914** empirical observations. Processed observations add provenance fields such as `source_file` and `normalized_measurement_type`.
3. **AI Recommendation Surrogate**: A model selected from logistic regression, decision tree, and random forest candidates using an explicit stratified **80% training / 20% test split**. The current report selects Random Forest with **90.48% test accuracy**, **1.00 precision**, **0.71 recall**, and **0.83 F1**; metrics are stored in `data/processed/phase11_training/model_evaluation.json`.

## Current Verified Dataset Scope

The current raw inventory contains **17 CSV files and 37,914 rows**:

| Target | Architecture | Raw files / rows | Variants benchmarked |
| --- | --- | ---: | --- |
| Intel Core i7-11800H | `x86_64` | 3 / 9,000 | 512, 768, 1024 |
| AMD Ryzen 5 4600H | `x86_64` | 3 / 9,000 | 512, 768, 1024 |
| AMD Ryzen 3 7320U | `x86_64` | 3 / 9,000 | 512, 768, 1024 |
| MediaTek Helio P65 / Vivo Y19 | `aarch64` | 3 / 9,000 | 512, 768, 1024 |
| Espressif ESP8266EX | `xtensa_lx106` | 2 / 540 | 512, 768 |
| Espressif ESP32 Xtensa LX6 | `xtensa_lx6` | 3 / 1,374 | 512, 768, 1024 |

Each variant run covers KeyGen, Encapsulation, and Decapsulation. Latency is recorded in `execution_time_ns`; memory observations are recorded in `memory_bytes`. The raw ESP32 records report `ram_mb = 0`, so the framework preserves that missing capacity value rather than inventing a RAM estimate. Use the processed statistics and UI for aggregate latency, memory, and pass/fail views.

### Variant Coverage by Processor

The table below separates successful benchmark coverage from variants that were not run. “Not benchmarked” means the repository contains no measurement for that processor/variant; it is not an invented OOM or failure result.

| Processor / device | ML-KEM-512 | ML-KEM-768 | ML-KEM-1024 |
| --- | --- | --- | --- |
| Intel Core i7-11800H | Benchmarked: 3,000 successful rows | Benchmarked: 3,000 successful rows | Benchmarked: 3,000 successful rows |
| AMD Ryzen 5 4600H | Benchmarked: 3,000 successful rows | Benchmarked: 3,000 successful rows | Benchmarked: 3,000 successful rows |
| AMD Ryzen 3 7320U | Benchmarked: 3,000 successful rows | Benchmarked: 3,000 successful rows | Benchmarked: 3,000 successful rows |
| MediaTek Helio P65 / Vivo Y19 | Benchmarked: 3,000 successful rows | Benchmarked: 3,000 successful rows | Benchmarked: 3,000 successful rows |
| Espressif ESP32 Xtensa LX6 | Benchmarked: 459 successful rows | Benchmarked: 459 successful rows | Benchmarked: 456 successful rows |
| Espressif ESP8266EX Xtensa LX106 | Benchmarked: 270 successful rows | Benchmarked: 270 successful rows | **Not benchmarked / not validated** |

#### ESP8266 ML-KEM-1024 Status

ML-KEM-1024 is not included for ESP8266EX because the current raw dataset contains no ML-KEM-1024 CSV or measurement. The ESP8266 environment has only 80 KB SRAM and the project does not claim a measured ML-KEM-1024 OOM, watchdog reset, latency, or cryptographic result for it. Recommendations that require this variant must report the lack of benchmark coverage instead of presenting it as a measured failure. Arduino Uno and Mega are also unbenchmarked hardware candidates, as documented below; they are separate from the ESP8266 result.

### Complete Processor and Arduino Feasibility Summary

This table includes every processor/device profile in the current project plus Arduino Uno and Mega. **Not benchmarked** means there is no validated measurement in this repository; it does not mean that a failure measurement was recorded.

| Processor/device | Architecture and resources | ML-KEM-512 | ML-KEM-768 | ML-KEM-1024 | Reason for missing coverage |
| --- | --- | --- | --- | --- | --- |
| Intel Core i7-11800H | `x86_64`, native software profile | Benchmarked | Benchmarked | Benchmarked | None; all three variants have successful rows |
| AMD Ryzen 5 4600H | `x86_64`, native software profile | Benchmarked | Benchmarked | Benchmarked | None; all three variants have successful rows |
| AMD Ryzen 3 7320U | `x86_64`, native software profile | Benchmarked | Benchmarked | Benchmarked | None; all three variants have successful rows |
| MediaTek Helio P65 / Vivo Y19 | `aarch64`, physical Android hardware | Benchmarked | Benchmarked | Benchmarked | None; all three variants have successful rows |
| Espressif ESP32 Xtensa LX6 | 240 MHz dual-core, physical hardware | Benchmarked | Benchmarked | Benchmarked | None; all three variants have successful rows |
| Espressif ESP8266EX Xtensa LX106 | 80 MHz, 80 KB SRAM, physical hardware | Benchmarked | Benchmarked | **Not benchmarked** | No ML-KEM-1024 CSV exists; limited SRAM and compute make reliable validation impractical. No failure result is claimed. |
| Arduino Uno (ATmega328P) | 8-bit AVR, 16 MHz, 2 KB SRAM, 32 KB Flash | **Not benchmarked** | **Not benchmarked** | **Not benchmarked** | SRAM, 8-bit arithmetic, and lack of a validated AVR `mlkem-native` integration make reliable ML-KEM execution impractical. |
| Arduino Mega (ATmega2560) | 8-bit AVR, 16 MHz, 8 KB SRAM, 256 KB Flash | **Not benchmarked** | **Not benchmarked** | **Not benchmarked** | SRAM and compute limits plus lack of a validated AVR `mlkem-native` integration; no benchmark result is claimed. |

The current recommendation engine reports these cases as unsupported or lacking benchmark coverage rather than fabricating latency, memory, or OOM values.

### Benchmark Methodology and Software Environment

The benchmark invokes unchanged `mlkem-native v1.2.0` implementations and records processor, architecture, core count, OS/runtime, compiler, compiler version, optimization flags, variant, operation, iteration, latency, memory observation, verification result, and error text. KeyGen times only key generation; Encapsulation and Decapsulation setup is excluded. Decapsulation checks the encapsulated and decapsulated shared secrets byte-for-byte. Native x86-64 runs use the project’s native Linux/WSL2 harness; Android uses Termux/Clang; ESP8266 and ESP32 use Arduino/FreeRTOS firmware harnesses. Timing and memory definitions, including their process-level limitations, are documented in [phase2_native_methodology.md](docs/phase2_native_methodology.md).

`NATIVE_HARDWARE` is normalized to `REAL_HARDWARE` in processed data. The repository distinguishes physical silicon from emulation and controlled software conditions; no timing value is copied or synthesized between targets.

### Arduino Uno and Mega: Why They Were Not Benchmarked

Arduino Uno (ATmega328P) and Arduino Mega (ATmega2560) were **not benchmarked** and must not be presented as unsupported measurements. Both use 8-bit AVR MCUs at 16 MHz with only 2 KB SRAM on the Uno and 8 KB SRAM on the Mega, plus 32 KB and 256 KB Flash respectively. ML-KEM requires substantially larger working buffers and polynomial/NTT computation than these devices can reliably provide alongside the Arduino runtime, stack, buffers, and I/O state. Their 8-bit architecture also makes the integer arithmetic and memory movement impractically slow for a reliable three-operation benchmark.

The project’s validated `mlkem-native` integration targets 32-bit and 64-bit environments with suitable toolchains and platform support. No maintained, validated AVR/Arduino Uno/Mega port is included here, and no reproducible implementation/library configuration was available for these boards. Consequently, attempting a run would risk stack exhaustion, watchdog resets, timing dominated by failures, or incomplete cryptographic verification rather than a useful benchmark. They are therefore **impractical/unvalidated hardware candidates**, not devices that were actually benchmarked and not devices for which this project claims measured OOM or latency results.

---

## 🖥️ Evaluated Hardware Platforms (Physical Silicon Tiers)

The admitted dataset contains both native software execution profiles and physical hardware runs. The execution type is recorded per row and must be considered when comparing measurements:

| Hardware Tier | Processor / SoC | Architecture | Clock Frequency | Compute Units | Memory | Operating System |
| :--- | :--- | :---: | :---: | :---: | :--- | :--- |
| **High-Performance Workstation** | Intel Core i7-11800H | `x86_64` | 4.60 GHz (Turbo) | 8 Cores / 16 Threads | 16 GB DDR4 | Ubuntu 22.04 (WSL2) |
| **Mid-Range Laptop** | AMD Ryzen 5 4600H | `x86_64` | 4.00 GHz (Boost) | 6 Cores / 12 Threads | 16 GB DDR4 | Ubuntu 22.04 (WSL2) |
| **Budget Laptop** | AMD Ryzen 3 7320U | `x86_64` | 4.10 GHz (Boost) | 4 Cores / 8 Threads | 8 GB LPDDR5 | Ubuntu 24.04 (WSL2) |
| **Mobile Edge Device** | MediaTek Helio P65 | `aarch64` | 2.00 GHz | 8 Cores (Big.LITTLE) | 4 GB LPDDR4 | Android 10 / Termux |
| **Constrained IoT Node** | Espressif ESP8266EX | `xtensa_lx106` | 80 MHz | 1 Core (Single-core) | 80 KB SRAM | FreeRTOS (Arduino Core) |
| **Embedded IoT Node** | Espressif ESP32 Xtensa LX6 | `xtensa_lx6` | 240 MHz | 2 Cores | Not reported in CSV (`ram_mb=0`) | FreeRTOS (Arduino Core) |

---

## Benchmark Results

The UI and API expose the actual per-operation observations and aggregate statistics from the processed CSV. This README intentionally does not reproduce a hand-maintained latency table: values must remain traceable to `execution_time_ns`, `memory_bytes`, and the recorded verification status. Missing values remain missing, including the ESP32 system RAM field.

---

## 📁 Repository Structure & Implementation

```text
├── analysis/              # Data analysis scripts & processed dataset generator
├── backend/               # FastAPI recommendation service & REST endpoints
├── data/
│   ├── metadata/          # Cryptographic SHA-256 manifests & provenance records
│   ├── processed/         # Normalized observations & derived benchmark statistics (37,914 rows)
│   └── raw/               # Immutable raw benchmark CSV files (17 verified files)
├── environments/
│   ├── android_arm64/     # Termux C benchmarking harness for mobile ARMv8
│   ├── esp32_xtensa_lx6_arduino/ # Arduino/FreeRTOS ESP32 benchmark harness
│   ├── esp8266_xtensa_lx106_arduino/ # Arduino IDE firmware sketch & build instructions
│   └── native_x86_64_mlkem_native/   # WSL2 Linux native C benchmark harness
├── frontend/              # Interactive React dashboard for performance visualization
├── ml/                    # AI recommendation surrogate model training pipeline
└── tests/                 # Automated test suite
```

---

## ⚡ Embedded IoT Firmware Setup (ESP8266)

The Arduino firmware and reference source are located in:
📁 **[`environments/esp8266_xtensa_lx106_arduino/mlkem_esp8266_bench_768/`](environments/esp8266_xtensa_lx106_arduino/)**

- **Board Configuration**: NodeMCU 1.0 (ESP-12E Module), 80 MHz CPU frequency, 115200 baud.
- **Implementation**: Pure C99 `mlkem-native v1.2.0` with custom zeroize (`MLK_CONFIG_CUSTOM_ZEROIZE`) and hardware RNG integration (`RANDOM_REG32`).
- Detailed setup instructions are provided in [`environments/esp8266_xtensa_lx106_arduino/README.md`](environments/esp8266_xtensa_lx106_arduino/README.md).

---

## 🤖 Machine Learning Recommendation Engine

The AI recommendation engine evaluates system constraints (clock speed, memory budget, latency SLA, security floor) across 6 application profiles (Banking & Finance, IoT/Embedded, Cloud/Data Center, Mobile/Edge, Healthcare, Government/Critical Infrastructure):

| Hyperparameter / Metric | Specification |
| :--- | :--- |
| **Algorithm** | `RandomForestClassifier` (Scikit-Learn) |
| **Estimators** | `n_estimators = 300` |
| **Max Tree Depth** | `max_depth = 6` |
| **Class Weighting** | `balanced` |
| **Validation Strategy** | Stratified 80% Train / 20% Test Split |
| **Test Accuracy** | **90.48%** |
| **Test Precision / Recall / F1** | **1.00 / 0.71 / 0.83** |
| **Model Artifact** | `ml/artifacts/recommendation_policy_model.joblib` |

### Recommendation UI Workflow

The recommendation screen uses only verified hardware presets: Intel Core i7-11800H, AMD Ryzen 5 4600H, AMD Ryzen 3 7320U, MediaTek Helio P65/Vivo Y19, and ESP8266EX. QEMU, STM32 demo targets, and fictional processor presets are not presented as measured hardware. ESP32 Xtensa LX6 appears as an informational target because its current CSV records do not report system RAM; users must enter a RAM value manually before using it for inference.

The compact recommendation workspace uses a two-sided layout. The input form is shown first; selecting **Get ML-KEM Recommendation** flips to the result view, and **Edit inputs** returns to the form. The result explains the selected variant in plain language, shows KeyGen/Encapsulation/Decapsulation estimates, compares total estimated time with the entered latency budget, and explains why each alternative was not selected. Latency labels are presented as “Comfortably within budget,” “Within budget,” “Slightly over budget,” or “Over budget.”

The backend response includes the active model name, test accuracy/F1 metadata, application profile, latency budget, and per-variant security, RAM, latency, and benchmark-coverage decisions. The UI preserves unavailable dataset values rather than inventing measurements.

---

## 🚀 Quickstart & Verification

### Start Full Application (Backend + Frontend):
```powershell
# Install Python dependencies from the repository root
python -m pip install -r requirements.txt

# Install frontend dependencies in a second terminal
cd frontend
npm install
```

Start the services in **two PowerShell terminals**:

```powershell
# Terminal 1: FastAPI Backend Server (Port 8000)
$env:PYTHONPATH="."; python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000
```

```powershell
# Terminal 2: Vite Frontend Server (Port 3000)
cd frontend
npm run dev
```

Or start both services with:

```powershell
.\start.ps1
```

The script starts the backend and frontend as PowerShell jobs and prints both URLs.

- **Dashboard UI**: [http://localhost:3000](http://localhost:3000)
- **FastAPI OpenAPI Swagger**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

### Run Automated Test Suite:
```powershell
$env:PYTHONPATH="src;."
python -m pytest tests/ -v
```
*(All 19 tests pass with 100% success rate.)*

### Rebuild Derived Statistics & Retrain Model:
```powershell
$env:PYTHONPATH="src"
python analysis/build_processed_dataset.py --overwrite
python ml/build_training_dataset.py --overwrite
python ml/train_recommendation_model.py
```

---

## 📜 Citation & Attribution

```bibtex
@misc{mlkem_benchmark_2026,
  author = {Abhay Katre and Contributors},
  title = {Empirical Benchmarking and AI-Driven Parameter Selection for NIST FIPS 203 ML-KEM Across Heterogeneous Computing Architectures},
  year = {2026},
  publisher = {GitHub},
  howpublished = {\url{https://github.com/abhaykatre-dev/MLKEM-Benchmark}}
}
```