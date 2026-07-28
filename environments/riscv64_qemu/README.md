# RISC-V 64-bit Linux benchmark under QEMU

This adapter builds the unchanged `mlkem-native` v1.2.0 source inside a
RISC-V 64-bit Linux guest and records operation-only `CLOCK_MONOTONIC` timing.
It reuses the reviewed portable C runner, but every row is labelled
`EMULATED`; timing includes the RISC-V guest execution under QEMU and must not
be compared as native hardware timing.

## Run protocol

1. Provision a RISC-V 64-bit Linux QEMU guest with a working monotonic clock.
2. Install the guest's C compiler, Python 3, and Git.
3. Copy this `riscv64_qemu` folder and the `android_arm64` folder beside a
   clean `mlkem-native` clone, then check out commit
   `0ba906cb14b1c241476134d7403a811b382ca498`.
4. Run `./riscv64_qemu/build_and_run_riscv64.sh` for the 100-iteration gate.
5. Copy all CSVs and their SHA-256 values to the host. Only after strict host
   validation, change `ITERATIONS=1000` and use a new output directory.

No RISC-V data is admitted until this protocol completes.
