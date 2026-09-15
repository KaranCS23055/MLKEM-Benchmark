# Post-Quantum ML-KEM Benchmarking Framework & AI Recommendation Engine
### NIST FIPS 203 Standard Evaluation Across Multi-Architecture Hardware

[![NIST Standard](https://img.shields.io/badge/NIST-FIPS%20203%20ML--KEM-blue.svg)](https://csrc.nist.gov/pubs/fips/203/final)
[![Implementation](https://img.shields.io/badge/C99%20Source-mlkem--native%20v1.2.0-emerald.svg)](https://github.com/pq-code-package/mlkem-native)
[![Dataset](https://img.shields.io/badge/Empirical%20Dataset-27%2C270%20Rows-purple.svg)](data/README.md)
[![Verification](https://img.shields.io/badge/Cryptographic%20Verification-100%25%20memcmp%20Match-brightgreen.svg)](environments/)
[![ML Model](https://img.shields.io/badge/ML%20Surrogate-Random%20Forest-amber.svg)](ml/artifacts/)
[![Tests](https://img.shields.io/badge/Tests-18%2F18%20Passing-brightgreen.svg)](tests/)

---

## 📌 Executive Overview & Motivation

With the emergence of large-scale **Quantum Computing**, classical public-key cryptosystems based on integer factorization (RSA) and discrete logarithms over elliptic curves (ECDSA, ECDH) are vulnerable to polynomial-time key recovery via **Shor's Algorithm**.

To establish post-quantum confidentiality, the National Institute of Standards and Technology (**NIST**) published **FIPS 203: Module-Lattice-Based Key-Encapsulation Mechanism (ML-KEM)** in August 2024. ML-KEM is founded on the hardness of the Module Learning With Errors (**M-LWE**) problem over polynomial rings:
- **ML-KEM-512** (NIST Security Category 1 — AES-128 equivalent)
- **ML-KEM-768** (NIST Security Category 3 — AES-192 equivalent)
- **ML-KEM-1024** (NIST Security Category 5 — AES-256 equivalent)

On resource-constrained embedded systems, edge microcontrollers, and mobile devices, selecting an inappropriately high ML-KEM variant can result in **stack memory exhaustion (Out-of-Memory / OOM crashes)** or **severe violations of real-time latency budgets**.

### 🎯 Research Objectives
1. **Empirical Benchmarking**: High-iteration standardized benchmarks of pure C99 reference code (`mlkem-native v1.2.0`) across **4 distinct physical silicon tiers**: high-performance x86-64 workstation, mainstream laptop, mobile ARM SoC, and an ultra-constrained IoT microcontroller.
2. **Embedded Feasibility Analysis**: Establishing empirical memory and latency feasibility boundaries for sub-100 KB SRAM microcontrollers.
3. **AI Recommendation Engine**: A machine-learning surrogate model that automatically evaluates system hardware constraints and security requirements to recommend the optimal ML-KEM parameter set.

---

## 🖥️ Evaluated Hardware Platforms (Physical Silicon Tiers)

All benchmarks are conducted strictly on **physical hardware** (no emulation or virtualized CPU models):

| Hardware Tier | Processor / SoC | Architecture | Clock Frequency | Compute Units | Memory | Operating System |
| :--- | :--- | :---: | :---: | :---: | :--- | :--- |
| **High-Performance Workstation** | Intel Core i7-11800H | `x86_64` | 4.60 GHz (Turbo) | 8 Cores / 16 Threads | 16 GB DDR4 | Ubuntu 22.04 (WSL2) |
| **Mainstream Laptop** | AMD Ryzen 5 4600H | `x86_64` | 4.00 GHz (Boost) | 6 Cores / 12 Threads | 16 GB DDR4 | Ubuntu 22.04 (WSL2) |
| **Mobile Edge Device** | MediaTek Helio P65 | `aarch64` | 2.00 GHz | 8 Cores (Big.LITTLE) | 4 GB LPDDR4 | Android 10 / Termux |
| **Constrained IoT Node** | Espressif ESP8266EX | `xtensa_lx106` | 80 MHz | 1 Core (Single-core) | 80 KB SRAM | FreeRTOS (Arduino Core) |

---

## 📊 Consolidated Empirical Benchmark Results

All figures represent the **mean execution time** across **90–1,000 independent iterations** per operation with 100% cryptographic shared-secret verification (`memcmp` match):

| Hardware Tier | Processor Model | Variant | KeyGen | Encap | Decap | Full Handshake | Relative Overhead |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **High-Performance Workstation** | Intel Core i7-11800H | **ML-KEM-512**<br>**ML-KEM-768**<br>**ML-KEM-1024** | 0.019 ms<br>0.030 ms<br>0.045 ms | 0.020 ms<br>0.032 ms<br>0.048 ms | 0.025 ms<br>0.038 ms<br>0.055 ms | **0.064 ms**<br>**0.099 ms**<br>**0.147 ms** | **1.00× (Baseline)**<br>1.55×<br>2.30× |
| **Mainstream Laptop** | AMD Ryzen 5 4600H | **ML-KEM-512**<br>**ML-KEM-768**<br>**ML-KEM-1024** | 0.023 ms<br>0.034 ms<br>0.053 ms | 0.023 ms<br>0.037 ms<br>0.058 ms | 0.028 ms<br>0.043 ms<br>0.066 ms | **0.074 ms**<br>**0.114 ms**<br>**0.176 ms** | **1.16×**<br>1.78×<br>2.75× |
| **Mobile Edge Device** | MediaTek Helio P65 | **ML-KEM-512**<br>**ML-KEM-768**<br>**ML-KEM-1024** | 0.044 ms<br>0.089 ms<br>0.112 ms | 0.050 ms<br>0.098 ms<br>0.121 ms | 0.058 ms<br>0.113 ms<br>0.136 ms | **0.151 ms**<br>**0.300 ms**<br>**0.369 ms** | **2.36×**<br>4.69×<br>5.77× |
| **Constrained IoT Node** | ESP8266EX (80 MHz) | **ML-KEM-512**<br>~~ML-KEM-768~~<br>~~ML-KEM-1024~~ | 10.725 ms<br>—<br>— | 13.256 ms<br>—<br>— | 17.179 ms<br>—<br>— | **41.160 ms**<br>*Memory Exceeded*<br>*Memory Exceeded* | **643.1×**<br>N/A<br>N/A |

> [!NOTE]
> **IoT Microcontroller Architectural Boundary**:
> On the ESP8266EX, ML-KEM-512 successfully executes in **41.16 ms** with ~12 KB stack usage. ML-KEM-768 and ML-KEM-1024 exceed the chip's 80 KB Data SRAM and 64 KB Instruction RAM boundaries (91% occupied by firmware). Thus, ML-KEM-512 represents the upper feasible security boundary for sub-100 KB SRAM microcontrollers without external PSRAM.

---

## 📁 Repository Structure & Implementation

```text
├── analysis/              # Data analysis scripts & processed dataset generator
├── backend/               # FastAPI recommendation service & REST endpoints
├── data/
│   ├── metadata/          # Cryptographic SHA-256 manifests & provenance records
│   ├── processed/         # Normalized observations & derived benchmark statistics (27,270 rows)
│   └── raw/               # Immutable raw benchmark CSV files (10 verified files)
├── environments/
│   ├── android_arm64/     # Termux C benchmarking harness for mobile ARMv8
│   ├── esp8266_xtensa_lx106_arduino/ # Arduino IDE firmware sketch & build instructions
│   └── native_x86_64_mlkem_native/   # WSL2 Linux native C benchmark harness
├── frontend/              # Interactive React dashboard for performance visualization
├── ml/                    # AI recommendation surrogate model training pipeline
└── tests/                 # Automated test suite (18 unit tests, 100% pass)
```

---

## ⚡ Embedded IoT Firmware Setup (ESP8266)

The Arduino firmware and reference source are located in:
📁 **[`environments/esp8266_xtensa_lx106_arduino/mlkem_esp8266_bench/`](environments/esp8266_xtensa_lx106_arduino/)**

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
| **Validation Strategy** | Stratified Group Split by Hardware Environment |
| **Training Observations** | 60 derived candidates across 6 application profiles × 4 hardware tiers |
| **Model Artifact** | `ml/artifacts/recommendation_policy_model.joblib` |

---

## 🚀 Quickstart & Verification

### Start Full Application (Backend + Frontend):
```powershell
.\start.ps1
```
- **Dashboard UI**: [http://localhost:3000](http://localhost:3000)
- **FastAPI OpenAPI Swagger**: [http://localhost:8000/docs](http://localhost:8000/docs)

### Run Automated Test Suite:
```powershell
$env:PYTHONPATH="src"
python -m pytest tests/ -v
```
*(All 18 unit tests pass with 100% success rate).*

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
```\n