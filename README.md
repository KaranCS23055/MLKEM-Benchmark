# Post-Quantum ML-KEM Benchmarking Framework & AI Recommendation Engine

[![NIST Standard](https://img.shields.io/badge/NIST-FIPS%20203%20ML--KEM-blue.svg)](https://csrc.nist.gov/pubs/fips/203/final)
[![Implementation](https://img.shields.io/badge/C99%20Source-mlkem--native%20v1.2.0-emerald.svg)](https://github.com/pq-code-package/mlkem-native)
[![Dataset](https://img.shields.io/badge/Empirical%20Dataset-17%20Raw%20CSVs%20%7C%2063%2C000%2B%20Rows-purple.svg)](data/README.md)
[![ML Model](https://img.shields.io/badge/ML%20Surrogate-Random%20Forest%20(86.7%25)-amber.svg)](ml/artifacts/)
[![Tests](https://img.shields.io/badge/Tests-Passing-brightgreen.svg)](tests/)

---

## 📌 Project Overview & Motivation

With the advent of **Quantum Computing**, traditional public-key cryptosystems (such as RSA-2048 and Elliptic Curve Cryptography - ECC) are vulnerable to polynomial-time key extraction via **Shor's Algorithm**.

To establish quantum resistance, the National Institute of Standards and Technology (**NIST**) finalized **FIPS 203: Module-Lattice-Based Key-Encapsulation Mechanism (ML-KEM)** in August 2024.

However, ML-KEM introduces significant **computational latency, public key/ciphertext network overhead, and SRAM memory footprints** compared to classical ECC:
- **ML-KEM-512** (NIST Category 1 — AES-128 equivalent)
- **ML-KEM-768** (NIST Category 3 — AES-192 equivalent)
- **ML-KEM-1024** (NIST Category 5 — AES-256 equivalent)

On resource-constrained embedded systems and microcontrollers (e.g., IoT edge sensors, medical devices, automotive ECUs with $\le 32$ KB RAM), running the highest security level can cause **instant Out-Of-Memory (OOM) stack overflow or violation of real-time latency budgets**.

### 🎯 Research Objective
This project builds an end-to-end empirical benchmarking pipeline and an **AI-driven Recommendation Surrogate Model** that automatically analyzes a target device's clock frequency, SRAM capacity, compiler optimization, and latency SLA to select the optimal, safe ML-KEM variant without device failure.

---

## 🏛️ System Architecture & Logical Workflow

```
+-----------------------------------------------------------------------------------+
|                           1. DATA COLLECTION LAYER                                |
|                                                                                   |
|  [x86-64 Multi-Core]    [x86-64 Single-Core]    [x86-32 Multilib]                 |
|  (AMD Ryzen 5 4600H)    (taskset -c 0 Core Pin) (GCC -m32 i686)                   |
|                                                                                   |
|  [Intel i7-1255U Multi] [Intel i7-1255U P-Core] [ARM64 Real Hardware]             |
|  (Windows 11 Native)    (Affinity Mask 0x1)     (MediaTek Helio P65 Phone)        |
|                                                                                   |
|  [RISC-V 64-bit QEMU]   [ARM Cortex-M4 STM32F4]                                  |
|  (RV64GC Linux Guest)   (Renode — Functional Only, No Timing)                     |
|                                                                                   |
|  * Source: mlkem-native v1.2.0 (C99 Portable Backend, SHA: 0ba906cb)             |
|  * Timing: POSIX CLOCK_MONOTONIC_RAW (Nanosecond precision)                       |
|  * Output: 17 Raw CSVs — 63,000+ rows (1,000 iters x variant x op x env)         |
+------------------------------------------+----------------------------------------+
                                           |
                                           v
+-----------------------------------------------------------------------------------+
|                        2. PROCESSING & INTEGRITY LAYER                            |
|                                                                                   |
|  * data/raw/              -> 17 Raw CSVs (Append-only, SHA-256 Manifests)        |
|  * analysis/build_processed_dataset.py -> Schema Validation, IQR Outlier Scrub   |
|  * ml/build_training_dataset.py        -> Requirement Policy & Candidate Derivation|
|  * data/processed/        -> Normalized statistics, P95 latencies, SRAM bounds   |
+------------------------------------------+----------------------------------------+
                                           |
                                           v
+-----------------------------------------------------------------------------------+
|                           3. MACHINE LEARNING ENGINE                              |
|                                                                                   |
|  * ml/train_recommendation_model.py                                               |
|  * Algorithm: Random Forest Classifier (n_estimators=300, max_depth=6)            |
|  * Validation: Stratified 80% Train / 20% Test Split                             |
|  * Metrics: 86.67% Test Accuracy, 0.786 Weighted F1                               |
|  * Artifact: ml/artifacts/recommendation_policy_model.joblib                     |
+------------------------------------------+----------------------------------------+
                                           |
                                           v
+-----------------------------------------------------------------------------------+
|                      4. BACKEND REST API SERVER (Active)                          |
|                                                                                   |
|  * Framework: FastAPI (Python 3.13 / Uvicorn)                                     |
|  * Live Endpoints:                                                                |
|      - POST /api/recommendation  -> Live Joblib Model Inference + Rule Fallback  |
|      - GET  /api/benchmarks      -> Stream Empirical Raw Measurements            |
|      - GET  /api/analytics       -> Aggregated Performance & Memory Metrics      |
|      - GET  /api/processors      -> Multi-architecture Hardware Profiles          |
+------------------------------------------+----------------------------------------+
                                           |
                                           v
+-----------------------------------------------------------------------------------+
|                    5. INTERACTIVE REACT UI DASHBOARD (Active)                     |
|                                                                                   |
|  * Stack: React 18, TypeScript, Vite, Tailwind CSS, Recharts, Lucide Icons        |
|  * Modules:                                                                       |
|      - AI Recommendation Page    -> Interactive Hardware Constraint Wizard        |
|      - Benchmark Explorer        -> Real-time Filter, Sort, Pagination & CSV Export|
|      - Performance Analytics     -> Multi-dimensional Latency, SRAM & Radar Graphs|
|      - Specification Comparator  -> NIST FIPS 203 Parameter Level Matrix         |
+-----------------------------------------------------------------------------------+
```

---

## 🛠️ Complete Technology Stack & Libraries Used

| Component / Layer | Technology / Library | Purpose |
| :--- | :--- | :--- |
| **Cryptographic Primitives** | **`mlkem-native` v1.2.0** (`C99`) | Official NIST FIPS 203 ML-KEM standard implementation (PQ-Code Package). |
| **Microcontroller Firmware** | **ARM C99 + GNU Linker (`linker.ld`)** | Bare-metal STM32F407 startup vector table and UART register drivers. |
| **Microcontroller Simulation**| **Antmicro Renode 1.16.1** | Instruction set simulator for STM32F4 Discovery board (functional correctness only — no DWT timing). |
| **Data Processing** | **Python 3.13, Pandas, NumPy** | Automated raw dataset validation, statistical aggregation, and P95 calculation. |
| **Machine Learning** | **Scikit-Learn, Joblib** | Random Forest surrogate model training with stratified 80/20 train-test split. |
| **Backend REST API** | **FastAPI, Uvicorn, Pydantic** | Asynchronous REST backend serving real-time ML inference and benchmark streams. |
| **Frontend Framework** | **React 18, Vite, TypeScript** | Fast single-page application with type-safe interfaces. |
| **Styling & Icons** | **Tailwind CSS, Lucide React** | Responsive design system and consistent icon library. |
| **Data Visualization** | **Recharts** | Interactive SVG-rendered bar charts, line plots, radar charts, and pie distributions. |
| **Testing & CI** | **Pytest, Pytest-AnyIO** | Automated unit and integration testing suite. |

---

## 📂 Repository Layout

```
MLKEM-Benchmark/
├── analysis/               # Statistical processing scripts and SVG plot generation
├── backend/                # FastAPI server (main.py, ai_engine.py, models.py)
├── configs/                # Benchmark configuration files
├── data/
│   ├── raw/                # 17 append-only empirical CSV files (SHA-256 manifests)
│   ├── processed/          # Normalized statistics, P95 latencies, training candidates
│   ├── metadata/           # Run manifests and provenance records
│   └── archive/            # Historical pqcrypto-0.4.0 reference data
├── docs/                   # Phase calibration notes and methodology documents
├── environments/           # Per-environment C harnesses and benchmark runners
├── frontend/               # React 18 + Vite + TypeScript dashboard
├── ml/
│   ├── artifacts/          # Trained joblib model (recommendation_policy_model.joblib)
│   ├── build_training_dataset.py
│   └── train_recommendation_model.py
├── scripts/                # Utility scripts for data collection and processing
├── src/                    # Shared Python utilities and configuration parsers
├── tests/                  # Pytest test suite (6 test modules)
├── third_party/            # mlkem-native v1.2.0 source (commit 0ba906cb)
├── requirements.txt        # Python dependencies
├── start.ps1               # One-click launcher for backend + frontend
└── pytest.ini
```

---

## 📊 Summary of Empirical Results (17 Raw CSVs — 63,000+ Rows)

Across **7 timed execution environments**, **3 variants**, and **3 operations** (1,000 iterations each):

| Environment / Hardware | Variant | KeyGen Latency | Encap Latency | Decap Latency | Total Handshake | Throughput |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **ARM64 Mobile Hardware**<br>*(MediaTek Helio P65 Phone)* | ML-KEM-512<br>ML-KEM-768<br>ML-KEM-1024 | 43.88 $\mu s$<br>88.57 $\mu s$<br>111.57 $\mu s$ | 49.68 $\mu s$<br>98.26 $\mu s$<br>121.10 $\mu s$ | 57.50 $\mu s$<br>112.90 $\mu s$<br>136.22 $\mu s$ | **0.151 ms**<br>**0.300 ms**<br>**0.369 ms** | 20,128 ops/s<br>10,177 ops/s<br>8,257 ops/s |
| **x86-64 Native Workstation**<br>*(AMD Ryzen 5 4600H)* | ML-KEM-512<br>ML-KEM-768<br>ML-KEM-1024 | 22.83 $\mu s$<br>38.47 $\mu s$<br>53.24 $\mu s$ | 24.12 $\mu s$<br>39.41 $\mu s$<br>57.85 $\mu s$ | 30.16 $\mu s$<br>47.56 $\mu s$<br>64.43 $\mu s$ | **0.077 ms**<br>**0.125 ms**<br>**0.175 ms** | 41,465 ops/s<br>25,372 ops/s<br>17,285 ops/s |
| **32-Bit Legacy x86**<br>*(i686 Multilib GCC)* | ML-KEM-512<br>ML-KEM-768<br>ML-KEM-1024 | 145.47 $\mu s$<br>130.26 $\mu s$<br>192.49 $\mu s$ | 151.57 $\mu s$<br>138.44 $\mu s$<br>198.55 $\mu s$ | 189.53 $\mu s$<br>167.63 $\mu s$<br>233.73 $\mu s$ | **0.487 ms**<br>**0.436 ms**<br>**0.625 ms** | 6,598 ops/s<br>7,223 ops/s<br>5,036 ops/s |
| **64-Bit RISC-V QEMU Guest**<br>*(RV64GC Linux)* | ML-KEM-512<br>ML-KEM-768<br>ML-KEM-1024 | 290.16 $\mu s$<br>466.17 $\mu s$<br>675.85 $\mu s$ | 308.33 $\mu s$<br>497.43 $\mu s$<br>717.02 $\mu s$ | 373.59 $\mu s$<br>583.42 $\mu s$<br>828.57 $\mu s$ | **0.972 ms**<br>**1.547 ms**<br>**2.221 ms** | 3,243 ops/s<br>2,010 ops/s<br>1,395 ops/s |
| **x86-64 Windows Native (Multi-Core)**<br>*(Intel i7-1255U, 12th Gen)* | ML-KEM-512<br>ML-KEM-768<br>ML-KEM-1024 | 51.80 $\mu s$<br>89.87 $\mu s$<br>126.92 $\mu s$ | 62.45 $\mu s$<br>106.83 $\mu s$<br>146.38 $\mu s$ | 84.69 $\mu s$<br>135.58 $\mu s$<br>180.39 $\mu s$ | **0.199 ms**<br>**0.332 ms**<br>**0.454 ms** | 19,307 ops/s<br>11,127 ops/s<br>7,879 ops/s |
| **x86-64 Windows Native (Single P-Core)**<br>*(Intel i7-1255U, Affinity Mask 0x1)* | ML-KEM-512<br>ML-KEM-768<br>ML-KEM-1024 | 55.65 $\mu s$<br>86.91 $\mu s$<br>158.57 $\mu s$ | 69.78 $\mu s$<br>104.29 $\mu s$<br>187.21 $\mu s$ | 94.73 $\mu s$<br>132.77 $\mu s$<br>232.69 $\mu s$ | **0.220 ms**<br>**0.324 ms**<br>**0.578 ms** | 17,970 ops/s<br>11,506 ops/s<br>6,306 ops/s |

> **Note — ARM Cortex-M4 (STM32F4 / Renode):** Functional correctness verified (KeyGen + Encapsulation + Decapsulation + shared-secret equality). Timing measurements are **not included** because Renode's STM32F4 model lacks a working DWT cycle counter. These results are labelled `FUNCTIONAL_ONLY` and are never reported as timing data.

*For complete dataset documentation and column schemas, see [`data/README.md`](data/README.md).*

---

## 🤖 Machine Learning Pipeline

The AI recommendation engine is a **Random Forest Classifier** trained on derived benchmark observations and project-defined application profiles (Banking, IoT, Cloud/Data Center, Mobile/Edge, Healthcare, Government/Critical Infrastructure).

| Parameter | Value |
| :--- | :--- |
| **Algorithm** | `RandomForestClassifier` (Scikit-Learn) |
| **Estimators** | `n_estimators = 300` |
| **Max Depth** | `max_depth = 6` |
| **Class Weighting** | `balanced` |
| **Validation Strategy** | Stratified 80% Train / 20% Test Split |
| **Test Accuracy** | **86.67%** |
| **Weighted F1-Score** | **0.786** |
| **Model Artifact** | `ml/artifacts/recommendation_policy_model.joblib` |

**Input features:** security requirement, latency sensitivity, throughput importance, memory constraint level, compute budget level, max acceptable latency (ms), mean/P95 handshake latency (ms), mean memory (bytes), architecture, measurement type, ML-KEM variant, minimum variant.

**Output:** Binary recommendation (`True`/`False`) with confidence score — served live via `POST /api/recommendation`.

---

## 🚀 Quickstart & One-Click Launch

### Prerequisites
- Python 3.11+ with a virtual environment (`.venv/`)
- Node.js 18+ (for the React frontend)

### Start Both Backend & Frontend Simultaneously:
```powershell
.\start.ps1
```
- **Interactive Web UI**: [http://localhost:3000](http://localhost:3000)
- **FastAPI OpenAPI Swagger**: [http://localhost:8000/docs](http://localhost:8000/docs)

### Run the Automated Test Suite:
```powershell
.\.venv\Scripts\python.exe -m pytest tests/ -v
```

### Retrain the ML Model:
```powershell
.\.venv\Scripts\python.exe ml/train_recommendation_model.py
```

### Rebuild the Processed Dataset:
```powershell
.\.venv\Scripts\python.exe analysis/build_processed_dataset.py
.\.venv\Scripts\python.exe ml/build_training_dataset.py
```

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
- All cross-architecture comparisons use the same implementation: **`mlkem-native v1.2.0`** (commit `0ba906cb`).
- The historical `pqcrypto==0.4.0` x86-64 dataset is retained in `data/archive/` as a labelled reference only.

---

## 🔬 Hardware Expansion Roadmap

If expanding to **physical bare-metal IoT hardware**:
- **ARM Cortex-M4**: STM32F407G-DISC1 Discovery Board (168 MHz, 192 KB SRAM) — requires hardware DWT cycle counter or external logic analyzer for valid timing.
- **ARM Cortex-M33**: Raspberry Pi Pico 2 / RP2350 (150 MHz, 520 KB SRAM).
- **Espressif Xtensa / RISC-V**: ESP32-S3 DevKit (240 MHz, 512 KB SRAM).
- **Bare-Metal RISC-V**: Kendryte K210 / Sipeed Maix Bit (400 MHz RV64GC).
- **Zero-Overhead Hardware Cycle Counter**: ARM `DWT->CYCCNT` register.
- **Transient Energy Probing**: $0.1\,\Omega$ precision shunt resistor measured via Digital Storage Oscilloscope ($E = \int V \cdot I \, dt$).
