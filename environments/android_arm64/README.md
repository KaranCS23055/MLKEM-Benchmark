# Android ARM64 native benchmark

This runner builds the unchanged `mlkem-native` C source on a real Android
ARM64 device using Termux clang. It records `CLOCK_MONOTONIC` elapsed time,
uses Android kernel `getrandom()` for the ML-KEM randomized APIs, and writes
the project's raw CSV schema directly.

It is intentionally separate from the Cortex-M4 emulator: its output is
labelled `NATIVE_HARDWARE` and is appropriate for performance analysis.

It requires source commit `0ba906cb14b1c241476134d7403a811b382ca498`
(`mlkem-native` v1.2.0), matching the x86-64 and Cortex-M4 provenance used
by this project. It deliberately stops rather than mixing incompatible APIs.

Run `build_and_run_termux.sh` from the `mlkem-mobile` directory after placing
this `android_arm64` folder beside the existing `mlkem-native` clone:

```sh
./android_arm64/build_and_run_termux.sh
```

The first run uses 100 iterations and produces three CSV files, one per
ML-KEM variant (900 measurements total), under `results_clean`. The included
validator rejects a wrong schema, missing values, failed operations,
non-positive timings, and a wrong variant label.
