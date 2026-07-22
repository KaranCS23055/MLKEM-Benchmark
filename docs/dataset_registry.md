# Dataset registry

This registry is the authoritative admission record for benchmark data. `data/raw/` contains only standardized, valid `mlkem-native v1.2.0` measurements. Historical or calibration files are archived separately under `data/archive/`.

## Admitted benchmark datasets (45,000 rows total)

All 45,000 admitted rows are directly comparable and use **`mlkem-native v1.2.0`** (commit `0ba906cb14b1c241476134d7403a811b382ca498`).

| Environment ID | Architecture | Execution Type | Compiler | Rows | Scope |
| --- | --- | --- | --- | ---: | --- |
| `native_x86_64_wsl2_mlkem_native` | `x86_64` | `NATIVE_SOFTWARE` | GCC 15.2 | 9,000 | x86-64 Multi-Core (AMD Ryzen 5 4600H), 1,000 iterations per variant |
| `native_x86_64_single_core_wsl2_mlkem_native` | `x86_64` | `NATIVE_SOFTWARE` | GCC 15.2 | 9,000 | x86-64 Single-Core (`taskset -c 0`), 1,000 iterations per variant |
| `native_x86_32_wsl2_mlkem_native` | `x86` | `NATIVE_SOFTWARE` | GCC 15.2 (`-m32`) | 9,000 | 32-bit x86 (i686 mode), 1,000 iterations per variant |
| `android_vivo_y19_termux` | `aarch64` | `REAL_HARDWARE`¹ | Clang 18.1 | 9,000 | Physical Vivo Y19 Phone (Helio P65 MT6768), 1,000 iterations |
| `riscv64_qemu_linux` | `riscv64` | `EMULATED` | GCC 13.3 | 9,000 | RISC-V 64-bit Ubuntu QEMU guest, 1,000 iterations per variant |

**Total comparable training rows: 45,000 across 5 distinct environments.**

¹ Raw CSVs record `measurement_type = "NATIVE_HARDWARE"` (legacy label used before standardization). The correct project-standard label is `REAL_HARDWARE`. The normalization is documented in `data/processed/android_normalized/`.

## SHA-256 integrity

All admitted files have verified SHA-256 manifests under `data/metadata/`:

| Environment | Manifest location |
|-------------|------------------|
| x86-64 mlkem-native (Multi-Core) | `data/metadata/native_x86_64_mlkem_native_20260813T090600Z_manifest.json` |
| x86-64 mlkem-native (Single-Core) | `data/metadata/native_x86_64_single_core_mlkem_native_20260813T094355Z_manifest.json` |
| 32-bit x86 mlkem-native | `data/metadata/native_x86_32_mlkem_native_20260813T100912Z_manifest.json` |
| Android ARM64 (Vivo Y19) | `data/metadata/android_vivo_y19_stage2_1000_20260812/SHA256SUMS.txt` |
| RISC-V 64-bit QEMU | `data/metadata/riscv64_qemu_stage2_1000_20260812/SHA256SUMS.txt` |

## Archived historical datasets

Pre-standardization reference runs (such as initial `pqcrypto 0.4.0` experiments and 100-iteration calibration files) are preserved under `data/archive/historical_pqcrypto_reference/` and `data/archive/calibration_and_replication/`. They are excluded from `data/raw/` to ensure the core dataset remains 100% standardized on `mlkem-native`.
