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
VERSION="v1.2.0 ($EXPECTED_COMMIT)"
mkdir -p "$BUILD_DIR" "$OUTPUT_DIR"

TIMESTAMP=$(date -u +%Y%m%dT%H%M%SZ)
echo "=== Single-Core x86-64 mlkem-native benchmark ==="

for VARIANT in 512 768 1024; do
  BINARY="$BUILD_DIR/mlkem_x86_single_core_${VARIANT}"
  OUTPUT="$OUTPUT_DIR/native_x86_64_single_core_mlkem_native_mlkem_${VARIANT}_${TIMESTAMP}.csv"

  gcc -O3 -std=c99 \
    -DMLK_CONFIG_PARAMETER_SET="$VARIANT" \
    "-DBENCHMARK_PARAMETER_SET=$VARIANT" \
    "-DBENCHMARK_VARIANT_LABEL=\"ML-KEM-$VARIANT\"" \
    "-DMLKEM_NATIVE_VERSION=\"$VERSION\"" \
    "-DMLKEM_NATIVE_COMMIT=\"$EXPECTED_COMMIT\"" \
    '-DBENCHMARK_MEASUREMENT_TYPE="NATIVE_SOFTWARE"' \
    '-DBENCHMARK_ARCHITECTURE="x86_64"' \
    '-DBENCHMARK_OPTIMIZATION_FLAGS="-O3 (taskset -c 0)"' \
    -I"$SOURCE_ROOT/mlkem" \
    "$SCRIPT_DIR/mlkem_x86_single_core_bench.c" \
    "$SOURCE_ROOT/mlkem/mlkem_native.c" \
    -o "$BINARY"

  taskset -c 0 "$BINARY" --iterations "$ITERATIONS" --output "$OUTPUT" --environment "$ENVIRONMENT"
  python3 "$SCRIPT_DIR/validate_single_core_csv.py" "$OUTPUT" "$ITERATIONS" "ML-KEM-$VARIANT"
done

echo "DONE: Single-Core x86-64 CSVs written to $OUTPUT_DIR"
python3 "$SCRIPT_DIR/create_manifest.py" "$OUTPUT_DIR" "$TIMESTAMP"
