# Android ARM64 Metadata Normalization

## Purpose

This directory documents the correction of two metadata fields in the admitted Android ARM64 benchmark datasets. The **raw CSV files are immutable and have not been modified**. This directory provides the normalization record for downstream use.

## Affected raw files

All three admitted Android stage-2 files (in `data/raw/`):

| File | Rows | Raw value | Normalized value | Reason |
|------|------|-----------|-----------------|--------|
| `android_vivo_y19_mlkem_512_20260812T204747Z.csv` | 3,000 | `processor = "aarch64"` | `processor = "MediaTek Helio P65 (MT6768)"` | `uname().machine` returns the ISA string, not the SoC model |
| `android_vivo_y19_mlkem_768_20260812T204804Z.csv` | 3,000 | same | same | same |
| `android_vivo_y19_mlkem_1024_20260812T204813Z.csv` | 3,000 | same | same | same |
| All three above | 9,000 | `measurement_type = "NATIVE_HARDWARE"` | `measurement_type = "REAL_HARDWARE"` | Project standard is `REAL_HARDWARE` per `PROJECT_PLAN.md` |

## SoC identification — Vivo Y19

Device: **Vivo Y19** (model 1915)  
SoC: **MediaTek Helio P65 (MT6768)**  
Architecture: AArch64 / ARMv8-A  
CPU cores: 8 (2× Cortex-A75 @ 2.0 GHz + 6× Cortex-A55 @ 1.7 GHz)  
RAM: 4 GB LPDDR4x (observed `ram_mb=3741` in CSV, consistent with OS-visible RAM)

Source: Published Vivo Y19 specifications. The `cpu_cores=8` and `ram_mb=3741` values in the raw CSVs are consistent with this SoC.

The Android runner reads `processor = system_info.machine` from `uname(2)`. On ARM64 Linux (including Android/Termux), `uname.machine` always returns `"aarch64"` regardless of the physical SoC. This is a known limitation of `uname` on Linux ARM devices.

## Normalization rule

When consuming Android rows for ML training or analysis:

```
IF source == "android_vivo_y19_*"
  AND raw.processor == "aarch64"
  AND raw.architecture == "aarch64"
THEN
  normalized.processor = "MediaTek Helio P65 (MT6768)"
  normalized.measurement_type = "REAL_HARDWARE"
```

The `architecture` column remains `"aarch64"` — it is correct.

## Future runs

The Android runner (`environments/android_arm64/mlkem_android_benchmark.c`) has been updated to attempt reading the SoC/processor model from a `BENCHMARK_PROCESSOR_LABEL` compile-time define. The validator (`environments/android_arm64/validate_android_csv.py`) now accepts `REAL_HARDWARE` instead of `NATIVE_HARDWARE`.

## Integrity

The raw CSV files are SHA-256 verified and must not be modified. The normalization is applied only in processed/derived outputs, never in the raw files.
