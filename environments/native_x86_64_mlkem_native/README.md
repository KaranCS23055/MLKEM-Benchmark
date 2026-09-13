# x86-64 mlkem-native environment

This environment benchmarks `mlkem-native v1.2.0` (commit `0ba906cb14b1c241476134d7403a811b382ca498`) on the native x86-64 CPU using WSL2 Ubuntu (GCC, Linux, `CLOCK_MONOTONIC`). It resolves the **implementation mismatch** identified in the project audit: the existing pqcrypto x86-64 dataset uses a different implementation than the ARM64 and RISC-V datasets.

## Why this exists

| Environment | Implementation | Comparable? |
|---|---|---|
| Windows x86-64 (pqcrypto) | pqcrypto 0.4.0 | Reference only — opaque prebuilt wheel |
| **x86-64 WSL2 (this)** | **mlkem-native v1.2.0 portable C** | **Yes — same source as ARM64 + RISC-V** |
| Android ARM64 (Vivo Y19) | mlkem-native v1.2.0 portable C | Yes |
| RISC-V QEMU | mlkem-native v1.2.0 portable C | Yes |

## Files

| File | Purpose |
|---|---|
| `mlkem_x86_native_bench.c` | C benchmark harness (reads CPU model from `/proc/cpuinfo`) |
| `build_and_run_wsl.sh` | Build, run, and validate all three variants via WSL2 |
| `benchmark_config_100.sh` | Stage-1: 100 iterations (calibration) |
| `benchmark_config_1000.sh` | Stage-2: 1,000 iterations (final dataset) |
| `validate_x86_mlkem_native_csv.py` | Per-CSV validator |
| `create_manifest.py` | SHA-256 and provenance manifest generator |

## Execution

From PowerShell in the project root:

```powershell
# Stage 1 — calibration (100 iterations)
wsl bash environments/native_x86_64_mlkem_native/build_and_run_wsl.sh `
    environments/native_x86_64_mlkem_native/benchmark_config_100.sh

# After reviewing Stage 1 output — Stage 2 (1000 iterations)
wsl bash environments/native_x86_64_mlkem_native/build_and_run_wsl.sh `
    environments/native_x86_64_mlkem_native/benchmark_config_1000.sh

# Create SHA-256 manifest (replace TIMESTAMP with the token in the CSV filenames)
python environments/native_x86_64_mlkem_native/create_manifest.py data/raw TIMESTAMP
```

## Environment details

- **Measurement type:** `NATIVE_SOFTWARE`
- **Architecture:** `x86_64`
- **Processor:** AMD CPU model read from `/proc/cpuinfo` (e.g., `AMD Ryzen 7 4800H with Radeon Graphics`)
- **Host layer:** WSL2 Ubuntu under Hyper-V on Windows 11 — documented in manifest; same physical AMD CPU as pqcrypto run
- **Timing:** `CLOCK_MONOTONIC` via `clock_gettime(3)` — identical to RISC-V and Android harnesses
- **Implementation:** mlkem-native portable-C backend, compiled with GCC `-O3`, commit pinned and verified at build time

## Provenance rule

Never pool these rows with the `pqcrypto` x86-64 rows in the same feature set without including `implementation` as an explicit column. The pqcrypto dataset is retained as a historical reference.
