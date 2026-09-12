# Post-Quantum ML-KEM Benchmarking Framework & AI Recommendation Engine
### NIST FIPS 203 Standard Evaluation Across Multi-Architecture Hardware

[![NIST Standard](https://img.shields.io/badge/NIST-FIPS%20203%20ML--KEM-blue.svg)](https://csrc.nist.gov/pubs/fips/203/final)
[![Implementation](https://img.shields.io/badge/C99%20Source-mlkem--native%20v1.2.0-emerald.svg)](https://github.com/pq-code-package/mlkem-native)
[![Dataset](https://img.shields.io/badge/Empirical%20Dataset-45%2C000%2B%20Rows-purple.svg)](data/README.md)
[![Verification](https://img.shields.io/badge/Cryptographic%20Verification-100%25%20memcmp%20Match-brightgreen.svg)](environments/)
[![ML Model](https://img.shields.io/badge/ML%20Surrogate-Random%20Forest%20(86.7%25)-amber.svg)](ml/artifacts/)
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
1. **Empirical Benchmarking**: Execute standardized, high-iteration (1,000 iterations per operation) benchmarks of pure C99 reference code (`mlkem-native v1.2.0`) across heterogeneous computing architectures:
   - Modern x86-64 multi-core workstations (AMD Ryzen 5 4600H)
   - Isolated single-core x86-64 execution environments (`taskset -c 0`)
   - High-end mobile x86-64 laptop platforms (Intel Core i7-1255U)
   - Genuine ARM64 mobile hardware (MediaTek Helio P65 SoC)
   - Legacy 32-bit x86 environments (GCC Multilib `-m32`)
   - Emulated 64-bit RISC-V platforms (QEMU system mode)
2. **Standardized Methodology**: Enforce identical 32-byte hardware RNG seeding, nanosecond-precision monotonic timing (`CLOCK_MONOTONIC`), shared-secret cryptographic integrity verification (`memcmp`), and strict 22-column schema parity.
3. **AI Recommendation Surrogate**: Train a machine-learning surrogate model that automatically evaluates target system constraints (clock speed, available SRAM, compiler flags, and latency SLA) to select the optimal, safe ML-KEM parameter set.

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

> [!NOTE]
> Moving from ML-KEM-512 ($k=2$) to ML-KEM-1024 ($k=4$) quadruples the number of Number Theoretic Transform (NTT) polynomial multiplications from $k^2 = 4$ to $k^2 = 16$. This accounts for the monotonic latency increase observed across all 64-bit computing platforms.

---

## 📊 Summary of Verified Empirical Benchmark Results

All figures represent the **mean execution time** across **1,000 independent iterations** per operation (3,000 iterations per variant, 9,000 measurements per environment). All operations use pure C99 `mlkem-native v1.2.0` with 100% cryptographic shared-secret assertion verification.

| Target Architecture & Environment | Parameter Set | KeyGen ($\mu s$) | Encap ($\mu s$) | Decap ($\mu s$) | Handshake Total | Scaling Order ($512 < 768 < 1024$) | Throughput (ops/s) |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **x86-64 Multi-Core Workstation**<br>*(AMD Ryzen 5 4600H, 12 Threads, GCC -O3)* | ML-KEM-512<br>ML-KEM-768<br>ML-KEM-1024 | 22.55<br>34.15<br>52.63 | 23.03<br>36.71<br>58.00 | 28.24<br>43.34<br>65.75 | **73.82 $\mu s$ (0.074 ms)**<br>**114.20 $\mu s$ (0.114 ms)**<br>**176.39 $\mu s$ (0.176 ms)** | **Monotonic** ✅<br>**Monotonic** ✅<br>**Monotonic** ✅ | 41,060<br>26,532<br>17,150 |
| **x86-64 Single-Core Isolated**<br>*(AMD Ryzen 5 4600H, `taskset -c 0`, GCC -O3)* | ML-KEM-512<br>ML-KEM-768<br>ML-KEM-1024 | 23.38<br>38.46<br>57.92 | 24.17<br>39.75<br>61.30 | 31.06<br>47.63<br>69.89 | **78.60 $\mu s$ (0.079 ms)**<br>**125.84 $\mu s$ (0.126 ms)**<br>**189.11 $\mu s$ (0.189 ms)** | **Monotonic** ✅<br>**Monotonic** ✅<br>**Monotonic** ✅ | 38,785<br>24,051<br>15,962 |
| **ARM64 Real Mobile Hardware**<br>*(MediaTek Helio P65 SoC, Android Termux Clang -O3)* | ML-KEM-512<br>ML-KEM-768<br>ML-KEM-1024 | 43.88<br>88.57<br>111.57 | 49.68<br>98.26<br>121.10 | 57.50<br>112.90<br>136.22 | **151.07 $\mu s$ (0.151 ms)**<br>**299.73 $\mu s$ (0.300 ms)**<br>**368.89 $\mu s$ (0.369 ms)** | **Monotonic** ✅<br>**Monotonic** ✅<br>**Monotonic** ✅ | 20,102<br>10,109<br>8,187 |
| **Legacy 32-bit x86 Mode**<br>*(i686 Multilib GCC `-m32 -O3`)* | ML-KEM-512<br>ML-KEM-768<br>ML-KEM-1024 | 72.41<br>111.68<br>181.75 | 75.50<br>117.59<br>187.47 | 93.97<br>142.07<br>221.39 | **241.88 $\mu s$ (0.242 ms)**<br>**371.33 $\mu s$ (0.371 ms)**<br>**590.62 $\mu s$ (0.591 ms)** | **Monotonic** ✅<br>**Monotonic** ✅<br>**Monotonic** ✅ | 12,566<br>8,166<br>5,118 |
| **RISC-V 64-bit Emulated Guest**<br>*(QEMU system-mode, RV64GC Linux, GCC -O3)* | ML-KEM-512<br>ML-KEM-768<br>ML-KEM-1024 | 290.16<br>466.17<br>675.85 | 308.33<br>497.43<br>717.02 | 373.59<br>583.42<br>828.57 | **972.08 $\mu s$ (0.972 ms)**<br>**1,547.03 $\mu s$ (1.547 ms)**<br>**2,221.43 $\mu s$ (2.221 ms)** | **Monotonic** ✅<br>**Monotonic** ✅<br>**Monotonic** ✅ | 3,122<br>1,956<br>1,360 |

### 🏆 Hardware Performance Ranking (Fastest to Slowest)
1. **AMD Ryzen 5 4600H (Multi-Core Workstation)**: **$121.5\,\mu s$** avg handshake
2. **AMD Ryzen 5 4600H (Single-Core Pin `taskset -c 0`)**: **$131.2\,\mu s$** avg handshake
3. **MediaTek Helio P65 (ARM64 Smartphone)**: **$273.2\,\mu s$** avg handshake
4. **Legacy 32-bit x86 Mode (`gcc -m32`)**: **$401.3\,\mu s$** avg handshake
5. **RISC-V 64-bit Emulated Guest (QEMU `rv64gc`)**: **$1,580.2\,\mu s$** avg handshake

---

## 🚀 Universal Benchmarking Workflow

For complete common benchmarking execution steps that apply identically to any target hardware, see:
👉 **[`BENCHMARK_COMMON_STEPS.md`](BENCHMARK_COMMON_STEPS.md)**

---

## 🤖 Machine Learning Recommendation Engine

The AI recommendation engine is a **Random Forest Classifier** trained on empirical benchmark observations and project-defined application profiles (Banking, IoT, Cloud/Data Center, Mobile/Edge, Healthcare, Government/Critical Infrastructure).

| Hyperparameter / Metric | Specification |
| :--- | :--- |
| **Algorithm** | `RandomForestClassifier` (Scikit-Learn) |
| **Estimators** | `n_estimators = 300` |
| **Max Tree Depth** | `max_depth = 6` |
| **Class Weighting** | `balanced` |
| **Validation Strategy** | Stratified 80% Train / 20% Test Split |
| **Test Accuracy** | **86.67%** |
| **Weighted F1-Score** | **0.786** |
| **Model Artifact** | `ml/artifacts/recommendation_policy_model.joblib` |

**Input features:** security requirement, latency sensitivity, throughput importance, memory constraint level, compute budget level, max acceptable latency (ms), mean/P95 handshake latency (ms), mean memory (bytes), architecture, measurement type, ML-KEM variant, minimum variant.

**Output:** Binary recommendation (`True`/`False`) with confidence score — served live via `POST /api/recommendation`.

---

## 📋 Data Provenance & Integrity Constraints

All benchmark records carry explicit **provenance labels**:

| Label | Meaning |
| :--- | :--- |
| `REAL_HARDWARE` | Measured on physical silicon (e.g., ARM64 Vivo Y19) |
| `NATIVE_SOFTWARE` | Measured natively on the host OS without virtualization |
| `EMULATED` | Measured inside a full-system emulator (e.g., QEMU RISC-V) |
| `DERIVED` | Computed from benchmark aggregates + policy rules (ML training inputs) |
| `FUNCTIONAL_ONLY` | Correctness verified; no timing measurements accepted |

- **Raw data is append-only.** Processed datasets, figures, and trained models are reproducible from versioned inputs.
- All cross-architecture comparisons use the same implementation: **`mlkem-native v1.2.0`**.

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
python ml/build_training_dataset.py
```

---

## 🔬 Hardware Expansion Roadmap

If expanding to **physical bare-metal IoT hardware**:
- **ARM Cortex-M4**: STM32F407G-DISC1 Discovery Board (168 MHz, 192 KB SRAM) — requires hardware DWT cycle counter for valid timing.
- **ARM Cortex-M33**: Raspberry Pi Pico 2 / RP2350 (150 MHz, 520 KB SRAM).
- **Espressif Xtensa / RISC-V**: ESP32-S3 DevKit (240 MHz, 512 KB SRAM).
- **Bare-Metal RISC-V**: Kendryte K210 / Sipeed Maix Bit (400 MHz RV64GC).
- **Zero-Overhead Hardware Cycle Counter**: ARM `DWT->CYCCNT` register.
- **Transient Energy Probing**: $0.1\,\Omega$ precision shunt resistor measured via Digital Storage Oscilloscope ($E = \int V \cdot I \, dt$).

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
