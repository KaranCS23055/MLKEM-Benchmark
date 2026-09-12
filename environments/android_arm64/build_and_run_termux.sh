#!/data/data/com.termux/files/usr/bin/bash
# Build and run genuine ARM64 Android ML-KEM measurements. Run in mlkem-native.
set -eu

SCRIPT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
CONFIG_FILE=${1:-"$SCRIPT_DIR/benchmark_config.sh"}
. "$CONFIG_FILE"
SOURCE_ROOT=$(CDPATH= cd -- "$SCRIPT_DIR/../mlkem-native" && pwd)
BUILD_DIR="$SCRIPT_DIR/build"
mkdir -p "$BUILD_DIR" "$OUTPUT_DIR"

if [ "$(uname -m)" != "aarch64" ]; then
  echo "BLOCKED: This runner requires a real aarch64 Android device; found $(uname -m)." >&2
  exit 2
fi
if ! command -v clang >/dev/null 2>&1 || ! command -v python >/dev/null 2>&1; then
  echo "BLOCKED: Install only the required Termux packages: pkg install clang python" >&2
  exit 2
fi

COMMIT=$(git -C "$SOURCE_ROOT" rev-parse HEAD)
VERSION=$(git -C "$SOURCE_ROOT" describe --tags --always --dirty)
EXPECTED_COMMIT=2507ff79a0acfec6e94a9a83709b5774491fdbb6
if [ "$COMMIT" != "$EXPECTED_COMMIT" ]; then
  echo "BLOCKED: This runner is validated against mlkem-native $EXPECTED_COMMIT, but found $COMMIT." >&2
  echo "Do not benchmark mixed versions. After checking git status, check out the documented commit." >&2
  exit 2
fi
for VARIANT in 512 768 1024; do
  BINARY="$BUILD_DIR/mlkem_android_$VARIANT"
  OUTPUT="$OUTPUT_DIR/android_vivo_y19_mlkem_${VARIANT}_$(date -u +%Y%m%dT%H%M%SZ).csv"
  clang -O3 -std=c99 -march=armv8-a -DMLK_CONFIG_PARAMETER_SET="$VARIANT" \
    "-DBENCHMARK_PARAMETER_SET=$VARIANT" "-DBENCHMARK_VARIANT_LABEL=\"ML-KEM-$VARIANT\"" \
    "-DMLKEM_NATIVE_VERSION=\"$VERSION ($COMMIT)\"" "-DMLKEM_NATIVE_COMMIT=\"$COMMIT\"" \
    '-DBENCHMARK_MEASUREMENT_TYPE="REAL_HARDWARE"' \
    "-DBENCHMARK_PROCESSOR_LABEL=\"${PROCESSOR_LABEL:-aarch64}\"" \
    -I"$SOURCE_ROOT/mlkem" "$SCRIPT_DIR/mlkem_android_benchmark.c" \
    "$SOURCE_ROOT/mlkem/mlkem_native.c" -o "$BINARY"
  "$BINARY" --iterations "$ITERATIONS" --output "$OUTPUT" --environment "$ENVIRONMENT"
  python "$SCRIPT_DIR/validate_android_csv.py" "$OUTPUT" "$ITERATIONS" "ML-KEM-$VARIANT"
done

echo "DONE: 3 CSV files; total measurements: $((ITERATIONS * 3 * 3))"
echo "Output directory: $OUTPUT_DIR"
