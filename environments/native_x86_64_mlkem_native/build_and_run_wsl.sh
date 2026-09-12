#!/bin/bash
# Build and run x86-64 native ML-KEM measurements using mlkem-native v1.2.0.
# Run from the project root via WSL2:
#   wsl bash environments/native_x86_64_mlkem_native/build_and_run_wsl.sh \
#       environments/native_x86_64_mlkem_native/benchmark_config_100.sh
#
# Writes output CSVs directly into data/raw/ on the Windows filesystem.
# WSL2 accesses the Windows project root under /mnt/c/...
set -eu

SCRIPT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
CONFIG_FILE=${1:-"$SCRIPT_DIR/benchmark_config_100.sh"}
. "$CONFIG_FILE"

# Resolve project root (two levels up from this script: environments/native_x86_64_mlkem_native/)
PROJECT_ROOT=$(CDPATH= cd -- "$SCRIPT_DIR/../.." && pwd)
SOURCE_ROOT="$PROJECT_ROOT/third_party/mlkem-native"
BUILD_DIR="$SCRIPT_DIR/build"
OUTPUT_DIR="$PROJECT_ROOT/data/raw"

# --- Sanity guards ---
if [ "$(uname -m)" != "x86_64" ]; then
  echo "BLOCKED: This runner requires x86_64 Linux; found $(uname -m)." >&2
  exit 2
fi
if ! command -v gcc >/dev/null 2>&1; then
  echo "BLOCKED: gcc not found. Install with: sudo apt-get install gcc" >&2
  exit 2
fi
if ! command -v python3 >/dev/null 2>&1; then
  echo "BLOCKED: python3 not found." >&2
  exit 2
fi

# --- Commit pin enforcement ---
EXPECTED_COMMIT=2507ff79a0acfec6e94a9a83709b5774491fdbb6
ACTUAL_COMMIT=$(git -C "$SOURCE_ROOT" rev-parse HEAD 2>/dev/null || echo "UNKNOWN")
if [ "$ACTUAL_COMMIT" != "$EXPECTED_COMMIT" ]; then
  echo "BLOCKED: mlkem-native is not at the pinned commit." >&2
  echo "  Expected: $EXPECTED_COMMIT" >&2
  echo "  Found:    $ACTUAL_COMMIT" >&2
  echo "Check out the documented commit before benchmarking." >&2
  exit 2
fi

VERSION="v1.2.0 ($EXPECTED_COMMIT)"
mkdir -p "$BUILD_DIR" "$OUTPUT_DIR"

TIMESTAMP=$(date -u +%Y%m%dT%H%M%SZ)
echo "=== mlkem-native x86-64 WSL2 benchmark ==="
echo "Config:  $CONFIG_FILE"
echo "Commit:  $EXPECTED_COMMIT"
echo "Output:  $OUTPUT_DIR"
echo "GCC:     $(gcc --version | head -1)"
echo ""

for VARIANT in 512 768 1024; do
  BINARY="$BUILD_DIR/mlkem_x86_native_${VARIANT}"
  OUTPUT="$OUTPUT_DIR/native_x86_64_mlkem_native_mlkem_${VARIANT}_${TIMESTAMP}.csv"

  echo "--- Building ML-KEM-$VARIANT ---"
  gcc -O3 -std=c99 \
    -DMLK_CONFIG_PARAMETER_SET="$VARIANT" \
    "-DBENCHMARK_PARAMETER_SET=$VARIANT" \
    "-DBENCHMARK_VARIANT_LABEL=\"ML-KEM-$VARIANT\"" \
    "-DMLKEM_NATIVE_VERSION=\"$VERSION\"" \
    "-DMLKEM_NATIVE_COMMIT=\"$EXPECTED_COMMIT\"" \
    '-DBENCHMARK_MEASUREMENT_TYPE="NATIVE_SOFTWARE"' \
    '-DBENCHMARK_ARCHITECTURE="x86_64"' \
    '-DBENCHMARK_OPTIMIZATION_FLAGS="-O3 (WSL2 Ubuntu / GCC)"' \
    -I"$SOURCE_ROOT/mlkem" \
    "$SCRIPT_DIR/mlkem_x86_native_bench.c" \
    "$SOURCE_ROOT/mlkem/mlkem_native.c" \
    -o "$BINARY"

  echo "--- Running ML-KEM-$VARIANT ($ITERATIONS iterations) ---"
  "$BINARY" \
    --iterations "$ITERATIONS" \
    --output "$OUTPUT" \
    --environment "$ENVIRONMENT"

  echo "--- Validating ML-KEM-$VARIANT ---"
  python3 "$SCRIPT_DIR/validate_x86_mlkem_native_csv.py" \
    "$OUTPUT" "$ITERATIONS" "ML-KEM-$VARIANT"
  echo ""
done

echo "DONE: 3 CSVs written to $OUTPUT_DIR"
echo "Total rows: $((ITERATIONS * 3 * 3))"
echo ""
echo "Next step: compute SHA-256 hashes and create the metadata manifest."
echo "  Run: python3 environments/native_x86_64_mlkem_native/create_manifest.py data/raw $TIMESTAMP"
