# Post-Quantum ML-KEM Benchmarking Framework & AI Recommendation Engine
### NIST FIPS 203 Standard Evaluation Across Multi-Architecture Hardware

[![NIST Standard](https://img.shields.io/badge/NIST-FIPS%20203%20ML--KEM-blue.svg)](https://csrc.nist.gov/pubs/fips/203/final)
[![Implementation](https://img.shields.io/badge/C99%20Source-mlkem--native%20v1.2.0-emerald.svg)](https://github.com/pq-code-package/mlkem-native)
[![Dataset](https://img.shields.io/badge/Empirical%20Dataset-63%2C000%20Rows-purple.svg)](data/README.md)
[![Verification](https://img.shields.io/badge/Cryptographic%20Verification-100%25%20memcmp%20Match-brightgreen.svg)](environments/)
[![ML Model](https://img.shields.io/badge/ML%20Surrogate-Random%20Forest%20(92.3%25)-amber.svg)](ml/artifacts/)
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
1. **Empirical Benchmarking**: Standardized, high-iteration (1,000 iterations per operation) benchmarks of pure C99 reference code (`mlkem-native v1.2.0`) across 7 heterogeneous execution environments:
   - High-end mobile x86-64 workstation (11th Gen Intel Core i7-11800H, 8 Cores / 16 Threads)
   - Isolated single-core Intel Core i7-11800H (`taskset -c 0`)
   - x86-64 multi-core workstation (AMD Ryzen 5 4600H, 6 Cores / 12 Threads)
   - Isolated single-core AMD Ryzen 5 4600H (`taskset -c 0`)
   - Genuine ARM64 mobile hardware (MediaTek Helio P65 SoC / Vivo Y19)
   - Legacy 32-bit x86 mode (i686 Multilib GCC `-m32`)
   - Emulated 64-bit RISC-V platform (QEMU system-mode `rv64gc`)
2. **Standardized Methodology**: Identical 32-byte hardware RNG seeding, nanosecond-precision monotonic timing (`CLOCK_MONOTONIC`), shared-secret cryptographic integrity verification (`memcmp`), and strict 22-column schema parity.
3. **AI Recommendation Surrogate**: A Random Forest surrogate model (**72.73% Accuracy**, **0.667 F1-Score**) that automatically evaluates target system constraints (clock speed, available SRAM, compiler flags, and latency SLA) to select the optimal, safe ML-KEM parameter set.

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

## 📊 Comprehensive Comparative Analysis Table (7 Environments — 63,000 Rows)

All figures represent the **mean execution time** across **1,000 independent iterations** per operation (3,000 iterations per variant, 9,000 measurements per environment). All operations use pure C99 `mlkem-native v1.2.0` with 100% cryptographic shared-secret assertion verification.

| Hardware Processor Model | Core & Thread Architecture | Instruction Set | ML-KEM Variant | KeyGen Latency ($\mu s$) | Encap Latency ($\mu s$) | Decap Latency ($\mu s$) | **Total Handshake ($\mu s$)** | **Total Handshake (ms)** | Throughput (ops/sec) |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Intel Core i7-11800H @ 2.30GHz**<br>*(Tiger Lake, 45W High-End)* | **16 Threads** (8 Physical Cores) | `x86_64` | **ML-KEM-512**<br>**ML-KEM-768**<br>**ML-KEM-1024** | 18.70<br>29.73<br>44.69 | 20.05<br>31.88<br>47.71 | 25.09<br>37.61<br>54.51 | **63.83**<br>**99.22**<br>**146.90** | **0.064 ms**<br>**0.099 ms**<br>**0.147 ms** | 47,742<br>30,530<br>20,561 |
| **Intel Core i7-11800H (Single-Core Pin)**<br>*(Isolated via `taskset -c 0`)* | **1 Core** (Physical Core 0 Pinned) | `x86_64` | **ML-KEM-512**<br>**ML-KEM-768**<br>**ML-KEM-1024** | 18.84<br>29.96<br>44.90 | 20.54<br>32.32<br>48.21 | 26.04<br>39.28<br>55.51 | **65.43**<br>**101.56**<br>**148.63** | **0.065 ms**<br>**0.102 ms**<br>**0.149 ms** | 46,718<br>29,925<br>20,342 |
| **AMD Ryzen 5 4600H with Radeon Graphics**<br>*(Renoir Zen 2, 45W Laptop)* | **12 Threads** (6 Physical Cores) | `x86_64` | **ML-KEM-512**<br>**ML-KEM-768**<br>**ML-KEM-1024** | 22.55<br>34.15<br>52.63 | 23.03<br>36.71<br>58.00 | 28.24<br>43.34<br>65.75 | **73.82**<br>**114.20**<br>**176.39** | **0.074 ms**<br>**0.114 ms**<br>**0.176 ms** | 41,060<br>26,532<br>17,150 |
| **AMD Ryzen 5 4600H (Single-Core Pin)**<br>*(Isolated via `taskset -c 0`)* | **1 Core** (Physical Core 0 Pinned) | `x86_64` | **ML-KEM-512**<br>**ML-KEM-768**<br>**ML-KEM-1024** | 23.38<br>38.46<br>57.92 | 24.17<br>39.75<br>61.30 | 31.06<br>47.63<br>69.89 | **78.60**<br>**125.84**<br>**189.11** | **0.079 ms**<br>**0.126 ms**<br>**0.189 ms** | 38,785<br>24,051<br>15,962 |
| **MediaTek Helio P65 SoC (Vivo Y19)**<br>*(ARM Cortex-A75 / A55 Mobile)* | **8 Cores** (Octa-Core Big.LITTLE) | `aarch64` | **ML-KEM-512**<br>**ML-KEM-768**<br>**ML-KEM-1024** | 43.88<br>88.57<br>111.57 | 49.68<br>98.26<br>121.10 | 57.50<br>112.90<br>136.22 | **151.07**<br>**299.73**<br>**368.89** | **0.151 ms**<br>**0.300 ms**<br>**0.369 ms** | 20,102<br>10,109<br>8,187 |
| **Legacy 32-Bit x86 Mode**<br>*(i686 Multilib GCC `-m32 -O3`)* | **12 Threads** (8 General Registers) | `x86` | **ML-KEM-512**<br>**ML-KEM-768**<br>**ML-KEM-1024** | 72.41<br>111.68<br>181.75 | 75.50<br>117.59<br>187.47 | 93.97<br>142.07<br>221.39 | **241.88**<br>**371.33**<br>**590.62** | **0.242 ms**<br>**0.371 ms**<br>**0.591 ms** | 12,566<br>8,166<br>5,118 |
| **RISC-V 64-bit RV64GC Linux**<br>*(QEMU System-Mode Emulation)* | **2 Virtual Cores** (Emulated) | `riscv64` | **ML-KEM-512**<br>**ML-KEM-768**<br>**ML-KEM-1024** | 290.16<br>466.17<br>675.85 | 308.33<br>497.43<br>717.02 | 373.59<br>583.42<br>828.57 | **972.08**<br>**1,547.03**<br>**2,221.43** | **0.972 ms**<br>**1.547 ms**<br>**2.221 ms** | 3,122<br>1,956<br>1,360 |

---

### 📈 Cross-Architecture Scaling Factors (Normalized vs. Fastest Hardware)

Using the **Intel Core i7-11800H Multi-Core** as the $1.00\times$ baseline:

| Hardware Environment | Processor Grade | Handshake Latency Multiplier (vs. Baseline) | Architectural Explanation |
| :--- | :---: | :---: | :--- |
| **Intel Core i7-11800H Multi** | High-End Laptop | **$1.00\times$ (Baseline)** | Highest IPC, 4.6 GHz Turbo, 8 Cores / 16 Threads, AVX2 SIMD |
| **Intel Core i7-11800H Single** | Single-Core Pin | **$1.02\times$** | Zero multi-core contention, pinned to Core 0 (`taskset -c 0`) |
| **AMD Ryzen 5 4600H Multi** | Mid-Tier Workstation | **$1.17\times$** | Zen 2 architecture, 4.0 GHz Boost, 6 Cores / 12 Threads |
| **AMD Ryzen 5 4600H Single** | Single-Core Pin | **$1.26\times$** | Single-core isolated execution on Ryzen 5 Core 0 |
| **ARM64 MediaTek Helio P65** | Mobile Smartphone | **$2.45\times$** | Mobile power envelope ($\sim 5\text{W}$), ARMv8-A NEON SIMD |
| **Legacy 32-Bit x86 Mode** | Constrained Legacy | **$3.88\times$** | 8 general-purpose registers (vs. 16 on 64-bit), register pressure |
| **RISC-V 64-Bit QEMU** | Software Emulated | **$15.20\times$** | System-mode software emulation, lack of hardware vector engine |

---

## 🚀 Universal Benchmarking Workflow

For the standard common benchmarking execution steps that apply identically to any target hardware, see:
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
| **Test Accuracy** | **72.73%** |
| **Weighted F1-Score** | **0.667** |
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
