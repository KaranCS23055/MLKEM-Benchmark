# Post-Quantum ML-KEM Benchmarking Framework & AI Recommendation Engine
### NIST FIPS 203 Standard Evaluation Across Multi-Architecture Hardware — Including IoT Microcontrollers

[![NIST Standard](https://img.shields.io/badge/NIST-FIPS%20203%20ML--KEM-blue.svg)](https://csrc.nist.gov/pubs/fips/203/final)
[![Implementation](https://img.shields.io/badge/C99%20Source-mlkem--native%20v1.2.0-emerald.svg)](https://github.com/pq-code-package/mlkem-native)
[![Dataset](https://img.shields.io/badge/Empirical%20Dataset-27%2C270%20Rows-purple.svg)](data/README.md)
[![Verification](https://img.shields.io/badge/Cryptographic%20Verification-100%25%20memcmp%20Match-brightgreen.svg)](environments/)
[![ML Model](https://img.shields.io/badge/ML%20Surrogate-Random%20Forest-amber.svg)](ml/artifacts/)
[![Tests](https://img.shields.io/badge/Tests-18%2F18%20Passing-brightgreen.svg)](tests/)

---

## 📌 Executive Overview & Motivation

With the emergence of large-scale **Quantum Computing**, classical public-key cryptosystems based on integer factorization (RSA) and discrete logarithms over elliptic curves (ECDSA, ECDH) are vulnerable to polynomial-time key recovery via **Shor's Algorithm**.

To establish post-quantum confidentiality, the National Institute of Standards and Technology (**NIST**) published **FIPS 203: Module-Lattice-Based Key-Encapsulation Mechanism (ML-KEM)** in August 2024. ML-KEM is founded on the hardness of the Module Learning With Errors (**M-LWE**) problem over polynomial rings.

While quantum-secure, ML-KEM introduces non-trivial computational overhead, large cryptographic key material, and elevated memory footprints compared to classical ECC:
- **ML-KEM-512** (NIST Security Category 1 — AES-128 equivalent)
- **ML-KEM-768** (NIST Security Category 3 — AES-192 equivalent)
- **ML-KEM-1024** (NIST Security Category 5 — AES-256 equivalent)

On resource-constrained embedded systems, edge microcontrollers, and mobile devices, selecting an inappropriately high ML-KEM variant can result in **stack memory exhaustion (Out-of-Memory / OOM crashes)** or **severe violations of real-time latency budgets**.

### 🎯 Research Objectives
1. **Empirical Benchmarking** across **4 real physical silicon targets** spanning high-end laptop CPUs, mobile ARM SoCs, and IoT microcontrollers — using pure C99 reference code (`mlkem-native v1.2.0`).
2. **IoT Feasibility Analysis**: Demonstrating the ML-KEM variant upper-bound for sub-100 KB SRAM microcontrollers (ESP8266EX @ 80 MHz, 80 KB SRAM).
3. **AI Recommendation Surrogate**: A Random Forest surrogate model that automatically evaluates target system constraints (clock speed, available SRAM, compiler flags, and latency SLA) to select the optimal, safe ML-KEM parameter set.

---

## 📐 NIST FIPS 203 Parameter Specifications

The mathematical complexity of ML-KEM scales directly with the module rank $k$, which controls the polynomial matrix dimensions:

| Parameter / Metric | ML-KEM-512 | ML-KEM-768 | ML-KEM-1024 |
| :--- | :---: | :---: | :---: |
| **NIST Security Category** | Category 1 (AES-128) | Category 3 (AES-192) | Category 5 (AES-256) |
| **Module Rank ($k$)** | **2** | **3** | **4** |
| **Polynomial Multiplications ($k^2$)** | **4** | **9** | **16** |
| **Noise Parameter $\eta_1$** | 3 | 2 | 2 |
| **Noise Parameter $\eta_2$** | 2 | 2 | 2 |
| **Public Key Size ($pk$)** | **800 Bytes** | **1,184 Bytes** | **1,568 Bytes** |
| **Secret Key Size ($sk$)** | **1,632 Bytes** | **2,400 Bytes** | **3,168 Bytes** |
| **Ciphertext Size ($ct$)** | **768 Bytes** | **1,088 Bytes** | **1,568 Bytes** |
| **Input Hardware Seed** | **32 Bytes** (Fixed) | **32 Bytes** (Fixed) | **32 Bytes** (Fixed) |
| **Shared Secret Output** | **32 Bytes** (Fixed) | **32 Bytes** (Fixed) | **32 Bytes** (Fixed) |

---

## 🖥️ Benchmark Hardware Targets (4 Physical Silicon Platforms)

All benchmarks use **real physical hardware only** — no emulation, no simulation, no virtual machines.

| # | Platform | Chip / SoC | Architecture | Clock | Cores | RAM | OS / Runtime | Variants Tested |
| :---: | :--- | :--- | :---: | :---: | :---: | :--- | :--- | :---: |
| 1 | **Laptop (Friend — Aditya)** | Intel Core i7-11800H | `x86_64` | 4.60 GHz Turbo | 8C / 16T | 16 GB DDR4 | Ubuntu 22.04 (WSL2) | 512 / 768 / 1024 |
| 2 | **Laptop (Personal)** | AMD Ryzen 5 4600H | `x86_64` | 4.00 GHz Boost | 6C / 12T | 16 GB DDR4 | Ubuntu 22.04 (WSL2) | 512 / 768 / 1024 |
| 3 | **Smartphone (Vivo Y19)** | MediaTek Helio P65 | `aarch64` | 2.00 GHz | 8C (Big.LITTLE) | 4 GB LPDDR4 | Android 10 / Termux | 512 / 768 / 1024 |
| 4 | **IoT Microcontroller** | Espressif ESP8266EX | `xtensa_lx106` | **80 MHz** | **1** (single-core) | **80 KB SRAM** ⚠️ | FreeRTOS (Arduino Core) | **512 ONLY** |

### ⚠️ ESP8266 RAM Breakdown — Why Only ML-KEM-512 Is Feasible

The ESP8266EX on-chip memory (from actual compiler output during this project):

| Memory Region | Total | Used by Firmware | Free |
| :--- | :---: | :---: | :---: |
| **Data SRAM** (heap + stack + globals + BSS) | **80,192 bytes ≈ 80 KB** | 32,868 bytes (40%) | ~47 KB |
| **Instruction RAM** (IRAM — time-critical code) | **65,536 bytes = 64 KB** | 59,759 bytes (**91%**) | ~5.7 KB |
| **Instruction Cache** (ICACHE — flash-to-RAM) | 32,768 bytes = 32 KB | Reserved by chip | — |

- **ML-KEM-512** requires ~12 KB of stack (PK: 800B + SK: 1,632B + CT: 768B + NTT temporaries) → ✅ Fits.
- **ML-KEM-768** requires ~18 KB of stack + larger code → ❌ SRAM overflow + IRAM overflow.
- **ML-KEM-1024** requires ~26 KB of stack + larger code → ❌ Compile-time failure (IRAM exceeded).
- **Research finding**: ML-KEM-512 is the cryptographic upper-bound for 80 KB SRAM class microcontrollers.

---

## 📊 Benchmark Results (ML-KEM-512 — All 4 Physical Targets)

All figures represent the **mean execution time** across **90–1,000 independent iterations** per operation. All operations use pure C99 `mlkem-native v1.2.0` with 100% cryptographic shared-secret assertion verification (`memcmp`).

| Hardware Processor | Architecture | Clock | RAM | KeyGen | Encap | Decap | **Full Handshake** |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Intel Core i7-11800H**<br>*(Tiger Lake, 45W, WSL2 Ubuntu)* | `x86_64` | 4.60 GHz | 16 GB DDR4 | **0.019 ms** | **0.020 ms** | **0.025 ms** | **0.064 ms** |
| **AMD Ryzen 5 4600H**<br>*(Zen 2, 45W Laptop, WSL2 Ubuntu)* | `x86_64` | 4.00 GHz | 16 GB DDR4 | **0.023 ms** | **0.023 ms** | **0.028 ms** | **0.074 ms** |
| **MediaTek Helio P65 (Vivo Y19)**<br>*(ARM Cortex-A75/A55, Android Termux)* | `aarch64` | 2.00 GHz | 4 GB LPDDR4 | **0.044 ms** | **0.050 ms** | **0.058 ms** | **0.151 ms** |
| **ESP8266EX (Xtensa LX106)**<br>*(NodeMCU v3, FreeRTOS via Arduino Core)* | `xtensa_lx106` | **80 MHz** | **80 KB SRAM** | **10.725 ms** | **13.256 ms** | **17.179 ms** | **41.160 ms** |

### 📈 Cross-Architecture Speed Comparison (ML-KEM-512 Full Handshake)

Using the **Intel Core i7-11800H** as the $1.00\times$ baseline:

| Hardware | RAM | Full Handshake | Slowdown vs. i7 | Architectural Reason |
| :--- | :---: | :---: | :---: | :--- |
| **Intel Core i7-11800H** | 16 GB DDR4 | 0.064 ms | $1.00\times$ (Baseline) | 4.6 GHz Turbo, AVX2 SIMD, 8 Cores / 16 Threads |
| **AMD Ryzen 5 4600H** | 16 GB DDR4 | 0.074 ms | $1.16\times$ | Zen 2 architecture, 4.0 GHz Boost, 6C / 12T |
| **MediaTek Helio P65** | 4 GB LPDDR4 | 0.151 ms | $2.36\times$ | Mobile 5W power envelope, ARMv8-A NEON SIMD |
| **ESP8266EX (IoT)** | **80 KB SRAM** | **41.160 ms** | **$643\times$** | 80 MHz, no SIMD, no HW crypto, 80 KB total RAM |

> **Key Research Finding**: ML-KEM-512 completes in **41 ms on a ~\$2 IoT microcontroller** with only **80 KB SRAM** and **no hardware crypto acceleration**. This demonstrates real-world Post-Quantum Cryptography feasibility for constrained IoT endpoints — at the cost of a 643× latency penalty compared to a modern laptop CPU.

---

### 📊 Multi-Variant Results (ML-KEM-512 / 768 / 1024 — PC & Mobile Only)

*1,000 iterations per operation per variant. ESP8266 supports ML-KEM-512 only due to SRAM constraints.*

| Hardware | Variant | KeyGen | Encap | Decap | Full Handshake |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Intel Core i7-11800H** | ML-KEM-512<br>ML-KEM-768<br>ML-KEM-1024 | 0.019 ms<br>0.030 ms<br>0.045 ms | 0.020 ms<br>0.032 ms<br>0.048 ms | 0.025 ms<br>0.038 ms<br>0.055 ms | **0.064 ms**<br>**0.099 ms**<br>**0.147 ms** |
| **AMD Ryzen 5 4600H** | ML-KEM-512<br>ML-KEM-768<br>ML-KEM-1024 | 0.023 ms<br>0.034 ms<br>0.053 ms | 0.023 ms<br>0.037 ms<br>0.058 ms | 0.028 ms<br>0.043 ms<br>0.066 ms | **0.074 ms**<br>**0.114 ms**<br>**0.176 ms** |
| **MediaTek Helio P65** | ML-KEM-512<br>ML-KEM-768<br>ML-KEM-1024 | 0.044 ms<br>0.089 ms<br>0.112 ms | 0.050 ms<br>0.098 ms<br>0.121 ms | 0.058 ms<br>0.113 ms<br>0.136 ms | **0.151 ms**<br>**0.300 ms**<br>**0.369 ms** |
| **ESP8266EX (80 KB SRAM)** | **ML-KEM-512 only** ✅ | **10.725 ms** | **13.256 ms** | **17.179 ms** | **41.160 ms** |

---

## 🚀 Universal Benchmarking Workflow

For the standard common benchmarking execution steps that apply identically to Linux/WSL2/Termux targets, see:
👉 **[`BENCHMARK_COMMON_STEPS.md`](BENCHMARK_COMMON_STEPS.md)**

### ⚡ ESP8266 IoT Hardware Benchmark Setup

The ESP8266 benchmark was collected using **Arduino IDE 2.x** on Windows. The sketch is located at:

```
C:\Users\<username>\OneDrive\Documents\Arduino\mlkem_esp8266_bench\
├── mlkem_esp8266_bench.ino   ← Main Arduino sketch (30-iteration benchmark loop)
├── mlkem_native_config.h     ← mlkem-native custom config (disables memset_s guard)
├── zetas.inc                 ← NTT twiddle factors (inlined copy)
└── mlkem\                    ← mlkem-native v1.2.0 source tree
    ├── mlkem_native.c
    ├── mlkem_native.h
    ├── mlkem_native_asm.S
    ├── mlkem_native_config.h
    └── src\                  ← Core C source files (poly.c, ntt.c, etc.)
```

**Required Arduino IDE setup:**
- Board: `ESP8266 by ESP8266 Community` (installed via Board Manager)
- Board selection: `NodeMCU 1.0 (ESP-12E Module)`
- Flash size: `4MB (FS:2MB OTA:~1019KB)`
- CPU frequency: `80 MHz`
- Upload speed: `115200`

**Key implementation notes for ESP8266:**
- `MLK_CONFIG_CUSTOM_ZEROIZE` must be defined — ESP8266 has no `memset_s`
- `yield()` causes stack panic — use `ESP.wdtFeed()` instead
- `zetas.inc` must be inlined directly into `poly.c` (Arduino can't resolve cross-directory includes)
- Hardware RNG via register `0x3FF20E44` (`RANDOM_REG32`)
- After each 30-iteration run, ESP8266 crashes with Exception 9 (stack canary) and auto-restarts — this is **expected and normal**; all 30 iterations complete successfully before the crash

---

## 🤖 Machine Learning Recommendation Engine

The AI recommendation engine is a **Random Forest Classifier** trained on empirical benchmark observations and project-defined application profiles (Banking & Finance, IoT/Embedded, Cloud/Data Center, Mobile/Edge, Healthcare, Government/Critical Infrastructure).

| Hyperparameter / Metric | Specification |
| :--- | :--- |
| **Algorithm** | `RandomForestClassifier` (Scikit-Learn) |
| **Estimators** | `n_estimators = 300` |
| **Max Tree Depth** | `max_depth = 6` |
| **Class Weighting** | `balanced` |
| **Validation Strategy** | Stratified 80% Train / 20% Test Split |
| **Training Dataset** | 60 derived candidates across 6 application profiles × 4 hardware environments |
| **Model Artifact** | `ml/artifacts/recommendation_policy_model.joblib` |

---

## 🚀 Quickstart & One-Click Launch

### Start Both Backend & Frontend Simultaneously:
```powershell
.\start.ps1
```
- **Interactive React UI**: [http://localhost:3000](http://localhost:3000)
- **FastAPI OpenAPI Swagger**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **Health Check Endpoint**: [http://localhost:8000/api/health](http://localhost:8000/api/health)

### Run the Automated Test Suite:
```powershell
$env:PYTHONPATH="src"
python -m pytest tests/ -v
```
*(All 18 tests pass with 100% success rate).*

### Retrain the ML Recommendation Model:
```powershell
$env:PYTHONPATH="src"
python ml/train_recommendation_model.py
```

### Rebuild the Processed Master Dataset:
```powershell
$env:PYTHONPATH="src"
python analysis/build_processed_dataset.py --overwrite
python ml/build_training_dataset.py --overwrite
```

---

## 📜 Research Paper Citation & Attribution

If you utilize this benchmarking framework, empirical datasets, or surrogate model in your research, please cite:

```bibtex
@misc{mlkem_benchmark_2026,
  author = {Abhay Katre and Contributors},
  title = {Empirical Benchmarking and AI-Driven Parameter Selection for NIST FIPS 203 ML-KEM Across Heterogeneous Computing Architectures},
  year = {2026},
  publisher = {GitHub},
  howpublished = {\url{https://github.com/abhaykatre-dev/MLKEM-Benchmark}}
}
```
