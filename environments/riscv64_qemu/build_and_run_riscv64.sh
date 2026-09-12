#!/bin/sh
# Run inside a RISC-V 64-bit Linux QEMU guest, beside mlkem-native.
set -eu

SCRIPT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
. "${1:-$SCRIPT_DIR/benchmark_config.sh}"
SOURCE_ROOT=$(CDPATH= cd -- "$SCRIPT_DIR/../mlkem-native" && pwd)
BUILD_DIR="$SCRIPT_DIR/build"
EXPECTED_COMMIT=2507ff79a0acfec6e94a9a83709b5774491fdbb6

if [ "$(uname -m)" != "riscv64" ]; then
  echo "BLOCKED: run this inside the RISC-V Linux guest; found $(uname -m)." >&2
  exit 2
fi
if ! command -v cc >/dev/null 2>&1 || ! command -v python3 >/dev/null 2>&1; then
  echo "BLOCKED: install the guest packages for a C compiler and Python 3." >&2
  exit 2
fi
if [ "$(git -C "$SOURCE_ROOT" rev-parse HEAD)" != "$EXPECTED_COMMIT" ]; then
  echo "BLOCKED: mlkem-native is not at the pinned source commit." >&2
  exit 2
fi

mkdir -p "$BUILD_DIR" "$OUTPUT_DIR"
for VARIANT in 512 768 1024; do
  BINARY="$BUILD_DIR/mlkem_riscv64_$VARIANT"
  OUTPUT="$OUTPUT_DIR/riscv64_qemu_mlkem_${VARIANT}_$(date -u +%Y%m%dT%H%M%SZ).csv"
  cc -O3 -std=c99 -DMLK_CONFIG_PARAMETER_SET="$VARIANT" \
    "-DBENCHMARK_PARAMETER_SET=$VARIANT" "-DBENCHMARK_VARIANT_LABEL=\"ML-KEM-$VARIANT\"" \
    '-DBENCHMARK_MEASUREMENT_TYPE="EMULATED"' '-DBENCHMARK_ARCHITECTURE="riscv64"' \
    '-DBENCHMARK_OPTIMIZATION_FLAGS="-O3 (RISC-V Linux guest)"' \
    "-DMLKEM_NATIVE_VERSION=\"v1.2.0 ($EXPECTED_COMMIT)\"" \
    "-DMLKEM_NATIVE_COMMIT=\"$EXPECTED_COMMIT\"" \
    -I"$SOURCE_ROOT/mlkem" "$SCRIPT_DIR/../android_arm64/mlkem_android_benchmark.c" \
    "$SOURCE_ROOT/mlkem/mlkem_native.c" -o "$BINARY"
  "$BINARY" --iterations "$ITERATIONS" --output "$OUTPUT" --environment "$ENVIRONMENT"
  python3 "$SCRIPT_DIR/validate_riscv64_csv.py" "$OUTPUT" "$ITERATIONS" "ML-KEM-$VARIANT"
done
echo "DONE: 3 RISC-V QEMU CSV files; total measurements: $((ITERATIONS * 3 * 3))"
