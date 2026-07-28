#!/bin/bash
# Build and run 32-bit x86 ML-KEM measurements using mlkem-native v1.2.0 (-m32).
set -eu

SCRIPT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
CONFIG_FILE=${1:-"$SCRIPT_DIR/benchmark_config_1000.sh"}
. "$CONFIG_FILE"

PROJECT_ROOT=$(CDPATH= cd -- "$SCRIPT_DIR/../.." && pwd)
SOURCE_ROOT="$PROJECT_ROOT/third_party/mlkem-native"
BUILD_DIR="$SCRIPT_DIR/build"
OUTPUT_DIR="$PROJECT_ROOT/data/raw"

EXPECTED_COMMIT=0ba906cb14b1c241476134d7403a811b382ca498
VERSION="v1.2.0 ($EXPECTED_COMMIT)"
mkdir -p "$BUILD_DIR" "$OUTPUT_DIR"

TIMESTAMP=$(date -u +%Y%m%dT%H%M%SZ)
echo "=== 32-bit x86 mlkem-native benchmark ==="

for VARIANT in 512 768 1024; do
  BINARY="$BUILD_DIR/mlkem_x86_32_${VARIANT}"
  OUTPUT="$OUTPUT_DIR/native_x86_32_mlkem_native_mlkem_${VARIANT}_${TIMESTAMP}.csv"

  gcc -m32 -O3 -std=c99 \
    -DMLK_CONFIG_PARAMETER_SET="$VARIANT" \
    "-DBENCHMARK_PARAMETER_SET=$VARIANT" \
    "-DBENCHMARK_VARIANT_LABEL=\"ML-KEM-$VARIANT\"" \
    "-DMLKEM_NATIVE_VERSION=\"$VERSION\"" \
    "-DMLKEM_NATIVE_COMMIT=\"$EXPECTED_COMMIT\"" \
    '-DBENCHMARK_MEASUREMENT_TYPE="NATIVE_SOFTWARE"' \
    '-DBENCHMARK_ARCHITECTURE="x86"' \
    '-DBENCHMARK_OPTIMIZATION_FLAGS="-m32 -O3 (WSL2 GCC)"' \
    -I"$SOURCE_ROOT/mlkem" \
    "$SCRIPT_DIR/mlkem_x86_32_bench.c" \
    "$SOURCE_ROOT/mlkem/mlkem_native.c" \
    -o "$BINARY"

  "$BINARY" --iterations "$ITERATIONS" --output "$OUTPUT" --environment "$ENVIRONMENT"
  python3 "$SCRIPT_DIR/validate_x86_32_csv.py" "$OUTPUT" "$ITERATIONS" "ML-KEM-$VARIANT"
done

echo "DONE: 32-bit x86 CSVs written to $OUTPUT_DIR"
python3 "$SCRIPT_DIR/create_manifest.py" "$OUTPUT_DIR" "$TIMESTAMP"
