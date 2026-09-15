/*
 * ML-KEM Benchmark for ESP8266 (Arduino IDE)
 * ============================================
 * Benchmarks ML-KEM-512 on ESP8266 (Xtensa LX106 @ 80 MHz).
 * Outputs 22-column CSV rows to Serial at 115200 baud.
 */

#include <Arduino.h>
#include <string.h>
#include <stdint.h>

#define MLK_CONFIG_PARAMETER_SET  1024
#define MLK_CONFIG_NO_ASM
#define MLK_CONFIG_CUSTOM_ZEROIZE

/* Custom zeroize definition for ESP8266 */
static inline void mlk_zeroize(void *ptr, size_t len) {
  volatile unsigned char *p = (volatile unsigned char *)ptr;
  while (len--) *p++ = 0;
}

extern "C" {
  /* randombytes definition required by mlkem-native */
  int randombytes(uint8_t *out, size_t len) {
    size_t i = 0;
    while (i < len) {
      uint32_t r = RANDOM_REG32;   /* 0x3FF20E44 — ESP8266 hardware RNG */
      for (int b = 0; b < 4 && i < len; b++, i++) {
        out[i] = (uint8_t)(r & 0xFF);
        r >>= 8;
      }
    }
    return 0;
  }

  #include "mlkem/mlkem_native.c"
}

/* Include public header AFTER implementation so CRYPTO_* macros and
 * crypto_kem_keypair/enc/dec declarations are visible in C++ scope.
 * mlkem_native.c does NOT pull in mlkem_native.h — we must do it here. */
#include "mlkem/mlkem_native.h"

/* ── Config ────────────────────────────────────────────────────────────── */
#define BENCH_ITER       90
#define BAUD_RATE        115200

#define ENV_LABEL        "esp8266_xtensa_lx106_arduino"
#define ARCH_LABEL       "xtensa_lx106"
#define PROC_LABEL       "ESP8266 Xtensa LX106 80MHz"
#define CPU_CORES        1
#define RAM_MB           0          /* ~80 KB SRAM */
#define OS_LABEL         "FreeRTOS (ESP8266 RTOS via Arduino)"
#define COMPILER_LABEL   "xtensa-lx106-elf-gcc"
#define COMPILER_VER     "xtensa-lx106-elf-gcc (Espressif)"
#define OPT_FLAGS        "-O2"
#define IMPL_LABEL       "mlkem-native"
#define IMPL_VERSION     "v1.2.0 (2507ff79a0acfec6e94a9a83709b5774491fdbb6)"
#define MEAS_TYPE        "NATIVE_HARDWARE"
#define VARIANT_LABEL    "ML-KEM-1024"

/* ── UUID v4 helper ─────────────────────────────────────────────────────── */
static char hex_c(uint8_t v) { return v < 10 ? '0' + v : 'a' + v - 10; }

static void make_uuid(char buf[37]) {
  uint8_t b[16];
  for (int i = 0; i < 16; i += 4) {
    uint32_t r = RANDOM_REG32;
    b[i] = r & 0xFF; b[i+1] = (r >> 8) & 0xFF; b[i+2] = (r >> 16) & 0xFF; b[i+3] = (r >> 24) & 0xFF;
  }
  b[6] = (b[6] & 0x0F) | 0x40;
  b[8] = (b[8] & 0x3F) | 0x80;
  int p = 0, i = 0;
  int groups[] = {4, 2, 2, 2, 6};
  for (int g = 0; g < 5; g++) {
    if (g) buf[p++] = '-';
    for (int k = 0; k < groups[g]; k++, i++) {
      buf[p++] = hex_c(b[i] >> 4);
      buf[p++] = hex_c(b[i] & 0x0F);
    }
  }
  buf[p] = '\0';
}

/* ── CSV Header ─────────────────────────────────────────────────────────── */
static void print_header() {
  Serial.println(
    "experiment_id,run_id,timestamp,environment,measurement_type,architecture,"
    "processor,cpu_cores,ram_mb,os,compiler,compiler_version,optimization_flags,"
    "implementation,implementation_version,mlkem_variant,operation,iteration,"
    "execution_time_ns,memory_bytes,success,error_message"
  );
}

/* ── CSV Row ────────────────────────────────────────────────────────────── */
static char exp_id[37], run_id[37];
static const char *g_ts;

static void print_row(const char *op, int iter, uint32_t elapsed_us, bool ok) {
  uint32_t ns      = elapsed_us * 1000UL;
  uint32_t freemem = ESP.getFreeHeap();

  Serial.print('"'); Serial.print(exp_id); Serial.print("\",\"");
  Serial.print(run_id); Serial.print("\",\"");
  Serial.print(g_ts); Serial.print("\",\"");
  Serial.print(ENV_LABEL); Serial.print("\",\"");
  Serial.print(MEAS_TYPE); Serial.print("\",\"");
  Serial.print(ARCH_LABEL); Serial.print("\",\"");
  Serial.print(PROC_LABEL); Serial.print("\",");
  Serial.print(CPU_CORES); Serial.print(",");
  Serial.print(RAM_MB); Serial.print(",\"");
  Serial.print(OS_LABEL); Serial.print("\",\"");
  Serial.print(COMPILER_LABEL); Serial.print("\",\"");
  Serial.print(COMPILER_VER); Serial.print("\",\"");
  Serial.print(OPT_FLAGS); Serial.print("\",\"");
  Serial.print(IMPL_LABEL); Serial.print("\",\"");
  Serial.print(IMPL_VERSION); Serial.print("\",\"");
  Serial.print(VARIANT_LABEL); Serial.print("\",\"");
  Serial.print(op); Serial.print("\",");
  Serial.print(iter); Serial.print(",");
  Serial.print(ns); Serial.print(",");
  Serial.print(freemem); Serial.print(",");
  Serial.print(ok ? "True" : "False");
  Serial.println(",\"\"");
}

/* ── Static buffers (avoid heap & stack fragmentation) ─────────────────── */
static uint8_t pk[CRYPTO_PUBLICKEYBYTES];
static uint8_t sk[CRYPTO_SECRETKEYBYTES];
static uint8_t ct[CRYPTO_CIPHERTEXTBYTES];
static uint8_t ss_enc[CRYPTO_BYTES];
static uint8_t ss_dec[CRYPTO_BYTES];

void setup() {
  Serial.begin(BAUD_RATE);
  delay(2000);

  /* Disable soft watchdog — ML-KEM ops are slow, WDT would fire otherwise */
  ESP.wdtDisable();

  Serial.println("# ================================================");
  Serial.println("# ML-KEM-1024 Benchmark — ESP8266 Xtensa LX106");
  Serial.println("# mlkem-native v1.2.0  |  FIPS 203");
  Serial.print("# CPU freq : "); Serial.print(ESP.getCpuFreqMHz()); Serial.println(" MHz");
  Serial.print("# Free heap: "); Serial.print(ESP.getFreeHeap()); Serial.println(" bytes");
  Serial.print("# Iterations: "); Serial.println(BENCH_ITER);
  Serial.println("# ================================================");

  make_uuid(exp_id);
  make_uuid(run_id);
  g_ts = "2026-09-15T10:15:00Z";

  print_header();

  for (int i = 1; i <= BENCH_ITER; i++) {
    uint32_t t0, t1;

    /* KeyGen */
    t0 = micros();
    int r_kg = crypto_kem_keypair(pk, sk);
    t1 = micros();
    print_row("keygen", i, t1 - t0, (r_kg == 0));

    /* Encapsulation */
    t0 = micros();
    int r_enc = crypto_kem_enc(ct, ss_enc, pk);
    t1 = micros();
    print_row("encapsulation", i, t1 - t0, (r_enc == 0));

    /* Decapsulation */
    t0 = micros();
    int r_dec = crypto_kem_dec(ss_dec, ct, sk);
    t1 = micros();
    bool ok = (r_dec == 0) && (memcmp(ss_enc, ss_dec, CRYPTO_BYTES) == 0);
    print_row("decapsulation", i, t1 - t0, ok);

    ESP.wdtFeed();  /* Feed hardware WDT on EVERY iteration */

    if (i % 5 == 0) {
      Serial.print("# Progress: ");
      Serial.print(i); Serial.print("/"); Serial.println(BENCH_ITER);
    }
    /* NO yield() here — it causes stack overflow panic on ESP8266 */
  }

  Serial.println("#");
  Serial.println("# ====== BENCHMARK COMPLETE ======");
  Serial.println("# Copy all non-# lines above into your dataset!");
  Serial.println("# Device halted. Reset ESP8266 to run again.");
  Serial.flush();

  /* Halt forever to prevent auto-restart — feed WDT to stay alive */
  while (true) {
    ESP.wdtFeed();
    delay(500);
  }
}

void loop() {
  delay(10000);
}
