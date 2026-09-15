# Project Plan: Post-Quantum ML-KEM Benchmarking Framework

## Scope and research principles

The project benchmarks standardized NIST FIPS 203 ML-KEM-512, ML-KEM-768, and ML-KEM-1024 operations: key generation, encapsulation, and decapsulation. It evaluates performance, not cryptographic security.

All benchmark records must retain their provenance. Execution types are `REAL_HARDWARE`, `NATIVE_SOFTWARE`, `VIRTUALIZED`, `EMULATED`, or `DERIVED`. A derived profile or emulated result must always be visibly labelled and must never be reported as measured hardware data.

Raw data is append-only. Processed datasets, figures, statistical reports, and trained models must be reproducible from versioned inputs, configurations, and documented commands.

## Implementation standard

All cross-architecture performance comparisons must use the same ML-KEM implementation. The project standard is **mlkem-native v1.2.0** (commit `0ba906cb14b1c241476134d7403a811b382ca498`). The original `pqcrypto==0.4.0` x86-64 dataset is retained as a historical reference and is labelled separately.

## Phase 1 — Skeleton and documentation ✅ COMPLETE

Created the repository layout, this implementation plan, the README, dependency manifest, ignore rules, and placeholders preserving empty data and source directories.

**Exit criteria met:** Repository layout exists; README documents status, integrity constraints, layout, and basic verification.

## Phase 2 — Native x86-64 benchmark foundation ✅ COMPLETE

Implemented configuration parsing and a native benchmark runner using `pqcrypto==0.4.0` for all three ML-KEM variants and operations. Shared-secret verification is enforced for every run. Produced a 9,000-row validated dataset (`NATIVE_SOFTWARE`, `pqcrypto 0.4.0`, 1,000 iterations per variant/operation).

**Exit criteria met:** Native run executes actual operations and records provenance without fabricated values.

## Phase 2b — x86-64 mlkem-native standardization ✅ COMPLETE

To resolve the implementation mismatch identified during audit: implemented a C harness (`environments/native_x86_64_mlkem_native/`) that compiles mlkem-native v1.2.0 portable-C via GCC under WSL2 Ubuntu. Produced a second 9,000-row x86-64 dataset using the same implementation as the ARM64 and RISC-V environments. The CPU model is correctly read from `/proc/cpuinfo`.

**Implementation:** mlkem-native v1.2.0, commit `0ba906cb`, NATIVE_SOFTWARE, `AMD Ryzen 5 4600H with Radeon Graphics`, GCC 15.2.0.

## Phase 3 — Validation and statistical analysis ✅ COMPLETE

Full raw-data validation against the required schema including required values, variants, operations, success/error state, cryptographic-verification failures, and duplicate experiment identifiers across raw files. Deterministic summaries with count, mean, median, minimum, maximum, sample standard deviation, coefficient of variation, P95, P99, and throughput. SVG plots generated from valid raw data only.

**Exit criteria met:** Validation report transparently identifies valid and invalid raw files; statistics and plots are reproducible from valid data only.

## Phase 4 — Calibration ✅ COMPLETE

Inspected timing distributions, outliers, and stability in the validated 100-iteration experiment. CV analysis justified 1,000 iterations for the scaled run. Calibration decision documented without changing existing raw measurements.

**Exit criteria met:** Calibration notes and experimentally justified iteration count documented in `docs/phase4_calibration.md`.

## Phase 5 — Scaled native experiment ✅ COMPLETE

Used the calibration decision to run 1,000 iterations. Preserved calibration data separately. Produced a versioned 9,000-row pqcrypto x86-64 analysis artifact. Runs are separately identified by unique run IDs.

**Exit criteria met:** Scaled raw data and reproducible summary with experimental rationale.

## Phase 6 — Controlled x86-64 environments ✅ COMPLETE

Added CPU affinity constraint (2 logical CPUs, mask 0x003). Produced a 900-row controlled run (`NATIVE_SOFTWARE`). Controlled environment is distinguishable from unrestricted native measurements via `environment_controls` in the manifest.

**Exit criteria met:** Controlled environment results are distinguishable from unrestricted native measurements.

## Phase 7 — ARM64/AArch64 ✅ COMPLETE

Produced a 9,000-row dataset from a physical Vivo Y19 Android device (MediaTek Helio P65 / MT6768, AArch64) using mlkem-native v1.2.0 compiled via Termux/Clang. SHA-256 integrity verified from device. Android metadata normalization documented in `data/processed/android_normalized/`.

**Metadata corrections applied (non-destructive):**
- `measurement_type`: raw=`NATIVE_HARDWARE` → correct label=`REAL_HARDWARE` (documented, raw not rewritten)
- `processor`: raw=`"aarch64"` → actual SoC=`"MediaTek Helio P65 (MT6768)"` (documented, raw not rewritten)

**Exit criteria met:** Architecture-comparable ARM64 dataset with documented methodology.

## Phase 8 — Cortex-M environments 🔶 PARTIAL

Cortex-M4 (STM32F4 / Renode): functional correctness verified (KeyGen + Encapsulation + Decapsulation + shared-secret equality). No timing measurements accepted because Renode's STM32F4 model lacks a working DWT cycle counter. Cortex-M0 and Cortex-M7 not yet started.

**Policy:** Cortex-M0/M7 will only produce timing measurements if a scientifically valid timer source is available. Functional-only results must never be reported as timing data.

## Phase 9 — RISC-V ✅ COMPLETE

Produced a 9,000-row dataset from a RISC-V 64-bit Linux guest under QEMU 10.2.1 (WSL2 host). mlkem-native v1.2.0 portable-C backend, GCC, `CLOCK_MONOTONIC`. SHA-256 integrity verified inside QEMU guest. Manifest records emulator version, guest OS, CPU model, and timing definition.

**Exit criteria met:** Reproducible RISC-V EMULATED dataset with complete provenance.

## Phase 10 — Derived application profiles ✅ COMPLETE

Define six project-designed profiles: Banking/Financial Services, IoT, Cloud/Data Center, Mobile/Edge, Healthcare, and Government/Critical Infrastructure. Use a documented 1–5 requirement scale for security, latency, throughput, memory, compute, and long-term security. Label all profiles `DERIVED`/project-defined.

**Exit criteria:** Profiles have sources/rationale for their design and are never represented as measured industry data.

## Phase 11 — ML recommendation pipeline ✅ COMPLETE

Built a validated, provenance-preserving derived observation table and grouped statistics from `data/raw/`. Combined benchmark aggregates with project-defined application profiles to generate training candidates. Trained a Random Forest Classifier using a stratified 80/20 holdout split. Persisted the model to `ml/artifacts/recommendation_policy_model.joblib`. Current evaluation achieves **72.73% Test Accuracy** and **0.667 F1-Score**. Integrated model into `backend/ai_engine.py` for live sub-millisecond inference.

**Exit criteria met:** Saved joblib model passes automated inference tests and exposes live confidence, latency compliance, and empirical explanations.

## Phase 12 — Demonstration dashboard ✅ COMPLETE

Built a responsive React 18 + Vite + TypeScript dashboard connected live to FastAPI backend REST endpoints (`/api/recommendation`, `/api/benchmarks`, `/api/analytics`, `/api/processors`). Replaced all static mock datasets with real-time empirical data streams. Implemented interactive hardware constraint wizards, benchmark data explorer with filtering/sorting, and multi-dimensional Recharts analytics.

**Exit criteria met:** Dashboard reads live backend API data and renders real empirical measurements and ML inferences without static mock dependencies.

## Phase 13 — End-to-end validation ✅ COMPLETE

Executed end-to-end integration tests (`pytest` suite with 9 passing tests) and frontend production builds (`tsc && vite build` passed with 0 errors). Verified end-to-end workflow from raw CSV data through statistical feature processing, ML model inference, and frontend UI visualization.

**Exit criteria met:** Complete system compiles cleanly, passes 100% of test suites, and operates smoothly via `start.ps1`.

## Phase 14 — Report and demonstration 🔶 READY FOR DEFENSE

Final project documentation, architecture diagrams, benchmark methodology, and presentation guide prepared for mentor review.

## Cross-phase record requirements

Each measurement includes at least: `experiment_id`, `run_id`, `timestamp`, `environment`, `measurement_type`, `architecture`, `processor`, `cpu_cores`, `ram_mb`, `os`, `compiler`, `compiler_version`, `optimization_flags`, `implementation`, `implementation_version`, `mlkem_variant`, `operation`, `iteration`, `execution_time_ns`, `memory_bytes`, `success`, and `error_message`.

For every experiment, save the configuration, random seed where applicable, machine information, implementation version, and a run manifest. Do not overwrite raw records; use a new run identifier and output file for every execution.

## Test strategy

Tests are introduced with the relevant phase: configuration parsing, record schema, result validation, shared-secret correctness, statistics, model loading, and recommendation inference. Each implementation phase ends by running the relevant tests, executing a small real experiment, inspecting its output, and documenting what worked before progressing.

## Dependency policy

Before adding any package or large tool, document (1) why it is needed, (2) the experiment it enables, and (3) why an existing dependency cannot perform the same job. Do not install emulators, SDKs, containers, or IDEs until the current phase needs them.
