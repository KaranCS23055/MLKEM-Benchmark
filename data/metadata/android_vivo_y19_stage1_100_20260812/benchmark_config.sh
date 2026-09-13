# Native Android ARM64 benchmark configuration.
# Keep ITERATIONS at 100 for the first verified run.
ITERATIONS=100
ENVIRONMENT=android_vivo_y19_termux
MEASUREMENT_TYPE=NATIVE_HARDWARE
ARCHITECTURE=aarch64
# Clean, separate output area. Existing earlier test CSVs are preserved.
OUTPUT_DIR=$HOME/mlkem-mobile/results_clean
