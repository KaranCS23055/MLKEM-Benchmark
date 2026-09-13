# Android ARM64 Termux setup

The validated target is a Vivo 1915 reporting `aarch64` and `arm64-v8a`. It is a real ARM64 mobile device. Runs on this phone are to be labelled `NATIVE_HARDWARE`, never `EMULATED` or `NATIVE_SOFTWARE`.

Before benchmark execution, use a project-local Python virtual environment, verify that the pinned native `pqcrypto` package can be installed for the current Android/Python combination, and perform a shared-secret correctness check. Do not create benchmark data if that check fails.

Keep the phone charged, close unnecessary apps, and disable battery-saver mode during a measurement run. Record battery and thermal state in the Android environment configuration when it is later created.

## Clean benchmark run

Use the corrected `android_arm64` directory from this project. Do not reuse the
three CSV files already under `data/raw`: two have invalid variant labels and
one is a duplicate. On the phone, place this directory beside a clean checkout
of `mlkem-native` at commit `0ba906cb14b1c241476134d7403a811b382ca498`.

```sh
pkg update && pkg install clang python git
uname -m                 # must print aarch64
cd ~/mlkem-mobile
./android_arm64/build_and_run_termux.sh
sha256sum results_clean/*.csv
```

The script builds three separate binaries and stops unless every generated CSV
has exactly 100 rows for KeyGen, 100 for Encapsulation, and 100 for
Decapsulation with the expected variant. It produces 900 rows in total.
Copy all three files and the displayed SHA-256 values back to the PC without
renaming or editing them. For the final stage, first repeat the same clean run
at 1,000 iterations only after the 100-iteration files pass review.
