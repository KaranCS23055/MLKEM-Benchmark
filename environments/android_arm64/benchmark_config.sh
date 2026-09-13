# Native Android ARM64 benchmark configuration.
# Keep ITERATIONS at 100 for the first verified run.
ITERATIONS=100
ENVIRONMENT=android_vivo_y19_termux
MEASUREMENT_TYPE=REAL_HARDWARE
ARCHITECTURE=aarch64
# Vivo Y19 SoC: MediaTek Helio P65 (MT6768). Passed to the harness at compile time.
PROCESSOR_LABEL="MediaTek Helio P65 (MT6768)"
# Clean, separate output area. Existing earlier test CSVs are preserved.
OUTPUT_DIR="$HOME/mlkem-mobile/results_clean"
