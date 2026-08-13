# Processor rollout after x86-64 and Android ARM64

## Completed measured environments

1. Windows x86-64 native software: final 9,000-row run.
2. Vivo Y19 ARM64 native hardware: final 9,000-row run.
3. Windows x86-64 constrained to two logical CPUs: two 900-row calibration/replication runs. This is a controlled condition, not a different processor.

## Next implementation order

### 1. RISC-V Linux virtual machine / emulator

Implement a portable C runner derived from the Android runner, using
`clock_gettime(CLOCK_MONOTONIC)` and the unchanged `mlkem-native` portable C
backend. Run it only on a RISC-V Linux guest or emulator that has a verified
monotonic clock. Record `environment_type = EMULATED` (or `VIRTUALIZED` if it
is a full VM) and the QEMU/toolchain version. First execute 100 iterations;
after validation, execute 1,000 iterations per variant/operation.

This is the best next software-only processor target. It requires an approved
QEMU RISC-V installation and a RISC-V Linux image/toolchain; neither is
currently installed.

### 2. Cortex-M4 emulator, functional evidence only for now

The current Renode STM32F4 platform successfully verifies all ML-KEM variants
but lacks a usable DWT cycle counter. Do not create timing CSVs from it.
Either obtain an STM32F4 board and measure hardware cycles with DWT, or find a
Renode model with a documented, working timing source and label every result
`EMULATED`.

### 3. Cortex-M0 and Cortex-M7

Reuse the portable C harness only after each target passes KeyGen,
Encapsulation, Decapsulation, and shared-secret equality. Their measurements
must use a target-supported timer/cycle counter; otherwise retain them as
functional-only evidence. They must never inherit timings from the M4.

### 4. Optional ARM64 replication

If another ARM64 device is available, rerun the same Android runner as a
separate environment. Do not label it as the Vivo Y19 and do not pool its
repetitions with the Vivo dataset.

## Required rule for every new target

For each architecture: build unchanged ML-KEM source; validate all three
variants and all three operations; run 100 real repetitions; validate schema,
variant, source hashes, and duplicate identities; then run the 1,000-repetition
final dataset. Never synthesize a missing processor result.
