# Dataset registry

This registry is the authoritative admission record for benchmark data. `data/raw/` contains only standardized, valid `mlkem-native v1.2.0` measurements. Historical or calibration files are archived separately under `data/archive/`.

## Admitted benchmark datasets (37,914 rows total)

All admitted rows use the same **`mlkem-native v1.2.0`** implementation and operation protocol. They are comparable for implementation-level analysis, but timings from different execution types must **not** be pooled or described as equivalent physical-hardware performance. The current admission manifest records 17 source files, 37,914 successful rows, and 51 statistic groups.

| Processor/device profile | Architecture | Execution type | Rows | Variants |
| --- | --- | --- | ---: | --- |
| Intel Core i7-11800H | `x86_64` | `NATIVE_SOFTWARE` | 9,000 | 512, 768, 1024 |
| AMD Ryzen 5 4600H | `x86_64` | `NATIVE_SOFTWARE` | 9,000 | 512, 768, 1024 |
| AMD Ryzen 3 7320U | `x86_64` | `NATIVE_SOFTWARE` | 9,000 | 512, 768, 1024 |
| MediaTek Helio P65 / Vivo Y19 | `aarch64` | `REAL_HARDWARE` | 9,000 | 512, 768, 1024 |
| Espressif ESP8266EX | `xtensa_lx106` | `REAL_HARDWARE` | 540 | 512, 768 |
| Espressif ESP32 Xtensa LX6 | `xtensa_lx6` | `REAL_HARDWARE` | 1,374 | 512, 768, 1024 |

Historical single-core, 32-bit x86, and RISC-V records remain outside the current admitted raw inventory. ESP8266 ML-KEM-1024 is also outside the current inventory because it was not benchmarked; its absence is not a measured failure.

> [!NOTE]
> **Why 32-bit?** The NIST 2030 post-quantum migration deadline applies to *all* device classes. Hundreds of millions of ATMs, industrial PLCs, SCADA systems, and medical devices run 32-bit OS and cannot be replaced before 2030. The `native_x86_32` environment directly measures ML-KEM feasibility on those systems — proving ML-KEM-512 is viable (241.9 µs) but ML-KEM-1024 is tight (590.6 µs) for real-time use.

> [!NOTE]
> **Why QEMU RISC-V?** Physical RISC-V Linux boards are not yet in this project's hardware inventory. QEMU `rv64gc` provides a reproducible RISC-V Linux environment. Results are labeled `EMULATED` — the ~15× overhead vs native x86-64 is QEMU's dynamic binary translation, not the RISC-V ISA itself.

Raw CSVs may record the legacy `NATIVE_HARDWARE` label; processed data normalizes it to `REAL_HARDWARE`.

## SHA-256 integrity

All admitted files have verified SHA-256 manifests under `data/metadata/`:

| Environment | Manifest location |
|-------------|------------------|
| x86-64 mlkem-native Multi-Core (AMD Ryzen 5 4600H) | `data/metadata/native_x86_64_mlkem_native_20260813T090600Z_manifest.json` |
| x86-64 mlkem-native Multi-Core (Intel Core i7-11800H) | `data/metadata/native_x86_64_mlkem_native_20260913T072724Z_manifest.json` |
| x86-64 mlkem-native Single-Core (AMD Ryzen 5 4600H) | `data/metadata/native_x86_64_single_core_mlkem_native_20260813T094355Z_manifest.json` |
| x86-64 mlkem-native Single-Core (Intel Core i7-11800H) | `data/metadata/native_x86_64_single_core_mlkem_native_20260913T074611Z_manifest.json` |
| 32-bit x86 mlkem-native | `data/metadata/native_x86_32_mlkem_native_20260813T100912Z_manifest.json` |
| Android ARM64 (Vivo Y19) | `data/metadata/android_vivo_y19_stage2_1000_20260812/SHA256SUMS.txt` |
| RISC-V 64-bit QEMU | `data/metadata/riscv64_qemu_stage2_1000_20260812/SHA256SUMS.txt` |

## Archived historical datasets

Pre-standardization reference runs (such as initial `pqcrypto 0.4.0` experiments and 100-iteration calibration files) are preserved under `data/archive/historical_pqcrypto_reference/` and `data/archive/calibration_and_replication/`. They are excluded from `data/raw/` to ensure the core dataset remains 100% standardized on `mlkem-native`.

