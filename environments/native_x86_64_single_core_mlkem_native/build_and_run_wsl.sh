#!/bin/bash
# Build and run Single-Core constrained x86-64 ML-KEM measurements.
set -eu

SCRIPT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
CONFIG_FILE=${1:-"$SCRIPT_DIR/benchmark_config_1000.sh"}
. "$CONFIG_FILE"

PROJECT_ROOT=$(CDPATH= cd -- "$SCRIPT_DIR/../.." && pwd)
SOURCE_ROOT="$PROJECT_ROOT/third_party/mlkem-native"
BUILD_DIR="$SCRIPT_DIR/build"
OUTPUT_DIR="$PROJECT_ROOT/data/raw"

EXPECTED_COMMIT=2507ff79a0acfec6e94a9a83709b5774491fdbb6
ACTUAL_COMMIT=$(git -C "$SOURCE_ROOT" rev-parse HEAD 2>/dev/null || echo "UNKNOWN")
VERSION="v1.2.0 ($ACTUAL_COMMIT)"
mkdir -p "$BUILD_DIR" "$OUTPUT_DIR"

TIMESTAMP=$(date -u +%Y%m%dT%H%M%SZ)
echo "=== Single-Core x86-64 mlkem-native benchmark ==="
echo "Processor: $(grep -m1 'model name' /proc/cpuinfo | cut -d: -f2 | xargs)"
echo "Config:    $CONFIG_FILE"
echo "Output:    $OUTPUT_DIR"
echo "Core Pin:  taskset -c 0"
echo ""

for VARIANT in 512 768 1024; do
  BINARY="$BUILD_DIR/mlkem_x86_single_core_${VARIANT}"
  OUTPUT="$OUTPUT_DIR/native_x86_64_single_core_mlkem_native_mlkem_${VARIANT}_${TIMESTAMP}.csv"

  echo "--- Building ML-KEM-$VARIANT (Single-Core Pin) ---"
  gcc -O3 -std=c99 \
    -DMLK_CONFIG_PARAMETER_SET="$VARIANT" \
    "-DBENCHMARK_PARAMETER_SET=$VARIANT" \
    "-DBENCHMARK_VARIANT_LABEL=\"ML-KEM-$VARIANT\"" \
    "-DMLKEM_NATIVE_VERSION=\"$VERSION\"" \
    "-DMLKEM_NATIVE_COMMIT=\"$ACTUAL_COMMIT\"" \
    '-DBENCHMARK_MEASUREMENT_TYPE="NATIVE_SOFTWARE"' \
    '-DBENCHMARK_ARCHITECTURE="x86_64"' \
    '-DBENCHMARK_OPTIMIZATION_FLAGS="-O3 (taskset -c 0)"' \
    -I"$SOURCE_ROOT/mlkem" \
    "$SCRIPT_DIR/mlkem_x86_single_core_bench.c" \
    "$SOURCE_ROOT/mlkem/mlkem_native.c" \
    -o "$BINARY"

  echo "--- Running ML-KEM-$VARIANT ($ITERATIONS iterations on Core 0) ---"
  taskset -c 0 "$BINARY" --iterations "$ITERATIONS" --output "$OUTPUT" --environment "$ENVIRONMENT"

  echo "--- Validating ML-KEM-$VARIANT ---"
  python3 "$SCRIPT_DIR/validate_single_core_csv.py" "$OUTPUT" "$ITERATIONS" "ML-KEM-$VARIANT"
  echo ""
done

echo "DONE: Single-Core x86-64 CSVs written to $OUTPUT_DIR"
python3 "$SCRIPT_DIR/create_manifest.py" "$OUTPUT_DIR" "$TIMESTAMP"
