# Post-Quantum ML-KEM Benchmarking Framework

Research framework for reproducibly benchmarking the NIST FIPS 203 ML-KEM parameter sets (ML-KEM-512, ML-KEM-768, and ML-KEM-1024) and training an evidence-based recommendation model. All measurements are real, never fabricated.

## Current status — Phase 9 complete, Phase 10 next

| Phase | Description | Status |
|-------|-------------|--------|
| 0 | Audit | ✅ Complete |
| 1 | Skeleton & documentation | ✅ Complete |
| 2 | Native x86-64 benchmark | ✅ Complete |
| 2b | x86-64 mlkem-native standardization (WSL2) | ✅ Complete |
| 3 | Validation & statistics | ✅ Complete |
| 4 | Calibration | ✅ Complete |
| 5 | Scaled native run (1,000 iter) | ✅ Complete |
| 6 | Controlled x86-64 (Single-Core & Affinity) | ✅ Complete |
| 7 | ARM64 (Vivo Y19 real hardware) | ✅ Complete |
| 8 | Cortex-M environments | 🔶 Partial (M4 functional only) |
| 9 | RISC-V QEMU | ✅ Complete |
| 10 | Application requirement profiles | ✅ Complete |
| 11 | ML recommendation pipeline | 🔲 Next |
| 12 | Dashboard | 🔲 Not started |
| 13 | End-to-end validation | 🔲 Not started |
| 14 | Report & demo | 🔲 Not started |

## Admitted benchmark dataset (45,000 rows)

| Environment | Architecture | Type | Implementation | Rows |
|-------------|-------------|------|----------------|------|
| **x86-64 WSL2 mlkem-native (Multi-Core)** | `x86_64` | `NATIVE_SOFTWARE` | mlkem-native v1.2.0 | **9,000** |
| **x86-64 WSL2 mlkem-native (Single-Core)** | `x86_64` | `NATIVE_SOFTWARE` | mlkem-native v1.2.0 | **9,000** |
| **32-bit x86 WSL2 mlkem-native (i686)** | `x86` | `NATIVE_SOFTWARE` | mlkem-native v1.2.0 | **9,000** |
| **Vivo Y19 ARM64 (Termux/Clang)** | `aarch64` | `REAL_HARDWARE`¹ | mlkem-native v1.2.0 | **9,000** |
| **RISC-V QEMU (Ubuntu/WSL2)** | `riscv64` | `EMULATED` | mlkem-native v1.2.0 | **9,000** |
| **Total admitted raw dataset** | | | | **45,000** |

¹ Raw CSVs record `NATIVE_HARDWARE` (legacy label). Normalized label is `REAL_HARDWARE` — see `data/processed/android_normalized/`.

All 45,000 rows use **mlkem-native v1.2.0** (`0ba906cb14b1c241476134d7403a811b382ca498`) compiled from source with GCC/Clang and timed via `CLOCK_MONOTONIC`.

## Repository layout

```text
analysis/          Statistical scripts and generated figures
configs/           Versioned experiment configuration files (JSON)
data/raw/          15 append-only mlkem-native benchmark measurements (CSV)
data/metadata/     Environment manifests and SHA-256 checksum files
data/processed/    Reproducible outputs derived from raw measurements
data/archive/      Historical reference runs and 100-iter calibration files
docs/              Methodology, data dictionary, and environment notes
environments/      Per-architecture C harnesses, build scripts, validators
  android_arm64/               Vivo Y19 ARM64 (Termux/Clang)
  cortex_m4/                   STM32F4 Renode (functional-only, no timing)
  native_x86_32_mlkem_native/  32-bit x86 WSL2 mlkem-native (i686 GCC)
  native_x86_64_mlkem_native/  x86-64 WSL2 mlkem-native (GCC Multi-Core)
  native_x86_64_single_core_mlkem_native/ x86-64 WSL2 mlkem-native (Single-Core)
  riscv64_qemu/                RISC-V 64-bit QEMU (Ubuntu Linux guest)
ml/                Feature engineering, training, and model artifacts (Phase 11)
src/               Python benchmark framework & application profiles loader
tests/             Automated test suite (11 passing tests)
third_party/mlkem-native/  mlkem-native v1.2.0 source (commit 0ba906cb)
```

## Running the unit tests

```powershell
$env:PYTHONPATH="src"; .\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

## Integrity commitments

- Never fabricate, duplicate, or silently overwrite benchmark measurements.
- Never present emulated, virtualized, or derived results as real hardware measurements.
- Preserve raw benchmark data as append-only records.
- Use standardized ML-KEM without modifying its mathematical algorithm.
- Label application profiles as project-defined derived requirements.
- Calculate reported statistics and model metrics from actual data and executions.
