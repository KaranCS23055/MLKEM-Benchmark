# Dataset registry

This registry is the authoritative admission record for benchmark data. `data/raw/` contains only standardized, valid `mlkem-native v1.2.0` measurements. Historical or calibration files are archived separately under `data/archive/`.

## Admitted benchmark datasets (63,000 rows total)

All 63,000 admitted rows use the same **`mlkem-native v1.2.0`** implementation and the same operation protocol. They are comparable for implementation-level analysis, but timings from different execution types must **not** be pooled or claimed as equivalent physical-hardware performance.

| Environment ID | Architecture | Execution Type | Compiler | Rows | Real-World Target | Key Finding |
| --- | --- | --- | --- | ---: | --- | --- |
| `native_x86_64_wsl2_mlkem_native` | `x86_64` | `NATIVE_SOFTWARE` | GCC 15.2 | 18,000 | Cloud servers, workstations, laptops | Performance ceiling: 63.8 µs ML-KEM-512 handshake |
| `native_x86_64_single_core_wsl2_mlkem_native` | `x86_64` | `NATIVE_SOFTWARE` | GCC 15.2 | 18,000 | CPU-pinned containers, embedded x86 | Multi-core ≈ single-core: ML-KEM is single-threaded |
| `native_x86_32_wsl2_mlkem_native` | `x86` | `NATIVE_SOFTWARE` | GCC 15.2 (`-m32`) | 9,000 | **ATMs, PLCs, SCADA, medical devices** | 3.2× slower than 64-bit — no AVX2; still TLS-viable at 241.9 µs |
| `android_vivo_y19_termux` | `aarch64` | `REAL_HARDWARE`¹ | Clang 18.1 | 9,000 | Android smartphones, ARM servers | Mobile feasibility: 151.1 µs real-silicon handshake |
| `riscv64_qemu_linux` | `riscv64` | `EMULATED` | GCC 13.3 | 9,000 | Emerging RISC-V IoT/embedded boards | ~15× QEMU overhead; baseline for future real-hardware comparison |

**Total admitted observations: 63,000 across 7 distinct execution configurations.** The x86-64 multi-core, x86-64 single-core, and x86-32 configurations share physical host hardware; they are not three independent devices. Intel i7-11800H and AMD Ryzen 5 4600H data are merged under the same environment ID but distinguished by the `processor` field in each CSV. RISC-V is emulated.

> [!NOTE]
> **Why 32-bit?** The NIST 2030 post-quantum migration deadline applies to *all* device classes. Hundreds of millions of ATMs, industrial PLCs, SCADA systems, and medical devices run 32-bit OS and cannot be replaced before 2030. The `native_x86_32` environment directly measures ML-KEM feasibility on those systems — proving ML-KEM-512 is viable (241.9 µs) but ML-KEM-1024 is tight (590.6 µs) for real-time use.

> [!NOTE]
> **Why QEMU RISC-V?** Physical RISC-V Linux boards are not yet in this project's hardware inventory. QEMU `rv64gc` provides a reproducible RISC-V Linux environment. Results are labeled `EMULATED` — the ~15× overhead vs native x86-64 is QEMU's dynamic binary translation, not the RISC-V ISA itself.

¹ Raw CSVs record `measurement_type = "NATIVE_HARDWARE"` (legacy label used before standardization). The correct project-standard label is `REAL_HARDWARE`. The normalization is documented in `data/processed/android_normalized/`.

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

