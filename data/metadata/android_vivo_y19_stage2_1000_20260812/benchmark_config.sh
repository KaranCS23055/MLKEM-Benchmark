# Native Android ARM64 benchmark configuration.
# Stage 2: 1000 iterations (final admitted run).
ITERATIONS=1000
ENVIRONMENT=android_vivo_y19_termux
MEASUREMENT_TYPE=REAL_HARDWARE
ARCHITECTURE=aarch64
# Vivo Y19 SoC: MediaTek Helio P65 (MT6768). Passed to the harness at compile time.
PROCESSOR_LABEL="MediaTek Helio P65 (MT6768)"
# Clean, separate output area.
OUTPUT_DIR=$HOME/mlkem-mobile/results_final_1000
