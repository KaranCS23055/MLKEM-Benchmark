/*
 * ML-KEM-768 Benchmark for ESP32 (Arduino IDE / ESP-IDF)
 * ========================================================
 * Benchmarks ML-KEM-768 on ESP32 (Xtensa LX6 Dual-Core @ 240 MHz).
 * Uses a dedicated 64 KB FreeRTOS Task to prevent loopTask stack canary triggers.
 * Outputs standardized 22-column CSV rows to Serial at 115200 baud.
 */

#include <Arduino.h>
#include <string.h>
#include <stdint.h>
#include <esp_system.h>
#include <esp_random.h>
#include <esp_timer.h>

#define MLK_CONFIG_PARAMETER_SET  768
#define MLK_CONFIG_NO_ASM
#define MLK_CONFIG_CUSTOM_ZEROIZE

/* Custom zeroize definition for ESP32 */
static inline void mlk_zeroize(void *ptr, size_t len) {
  volatile unsigned char *p = (volatile unsigned char *)ptr;
  while (len--) *p++ = 0;
}

extern "C" {
  /* True hardware random number generator via ESP-IDF TRNG */
  int randombytes(uint8_t *out, size_t len) {
    esp_fill_random(out, len);
    return 0;
  }

  #include "mlkem/mlkem_native.c"
}

/* Include public header AFTER implementation */
#include "mlkem/mlkem_native.h"

/* ── Benchmark Configuration ───────────────────────────────────────────── */
#define BENCH_ITER       1000
#define BAUD_RATE        115200
#define TASK_STACK_SIZE  (64 * 1024)   /* 64 KB Stack for ML-KEM */

#define ENV_LABEL        "esp32_xtensa_lx6_arduino"
#define ARCH_LABEL       "xtensa_lx6"
#define PROC_LABEL       "ESP32 Xtensa Dual-Core 240MHz"
#define CPU_CORES        2
#define RAM_MB           0          /* ~520 KB SRAM */
#define OS_LABEL         "FreeRTOS (ESP-IDF / Arduino Core)"
#define COMPILER_LABEL   "xtensa-esp32-elf-gcc"
#define COMPILER_VER     "xtensa-esp32-elf-gcc (Espressif)"
#define OPT_FLAGS        "-O2"
#define IMPL_LABEL       "mlkem-native"
#define IMPL_VERSION     "v1.2.0 (2507ff79a0acfec6e94a9a83709b5774491fdbb6)"
#define MEAS_TYPE        "NATIVE_HARDWARE"
#define VARIANT_LABEL    "ML-KEM-768"

/* ── UUID v4 helper ─────────────────────────────────────────────────────── */
static char hex_c(uint8_t v) { return v < 10 ? '0' + v : 'a' + v - 10; }

static void make_uuid(char buf[37]) {
  uint8_t b[16];
  esp_fill_random(b, 16);
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

static void print_row(const char *op, int iter, uint64_t elapsed_us, bool ok) {
  uint64_t ns      = elapsed_us * 1000ULL;
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
  Serial.print((unsigned long)ns); Serial.print(",");
  Serial.print(freemem); Serial.print(",");
  Serial.print(ok ? "True" : "False");
  Serial.println(",\"\"");
}

/* ── Static buffers ─────────────────────────────────────────────────────── */
static uint8_t pk[CRYPTO_PUBLICKEYBYTES];
static uint8_t sk[CRYPTO_SECRETKEYBYTES];
static uint8_t ct[CRYPTO_CIPHERTEXTBYTES];
static uint8_t ss_enc[CRYPTO_BYTES];
static uint8_t ss_dec[CRYPTO_BYTES];

void benchmarkTask(void *pvParameters) {
  Serial.println("# ================================================");
  Serial.println("# ML-KEM-768 Benchmark — ESP32 Xtensa LX6");
  Serial.println("# mlkem-native v1.2.0  |  FIPS 203");
  Serial.print("# CPU freq : "); Serial.print(ESP.getCpuFreqMHz()); Serial.println(" MHz");
  Serial.print("# Free heap: "); Serial.print(ESP.getFreeHeap()); Serial.println(" bytes");
  Serial.print("# Total RAM: "); Serial.print(ESP.getHeapSize()); Serial.println(" bytes");
  Serial.print("# Task Stack: "); Serial.print(TASK_STACK_SIZE); Serial.println(" bytes");
  Serial.print("# Iterations: "); Serial.println(BENCH_ITER);
  Serial.println("# ================================================");

  make_uuid(exp_id);
  make_uuid(run_id);
  g_ts = "2026-09-16T11:00:00Z";

  print_header();

  for (int i = 1; i <= BENCH_ITER; i++) {
    int64_t t0, t1;

    /* KeyGen */
    t0 = esp_timer_get_time();
    int r_kg = crypto_kem_keypair(pk, sk);
    t1 = esp_timer_get_time();
    print_row("keygen", i, (uint64_t)(t1 - t0), (r_kg == 0));

    /* Encapsulation */
    t0 = esp_timer_get_time();
    int r_enc = crypto_kem_enc(ct, ss_enc, pk);
    t1 = esp_timer_get_time();
    print_row("encapsulation", i, (uint64_t)(t1 - t0), (r_enc == 0));

    /* Decapsulation */
    t0 = esp_timer_get_time();
    int r_dec = crypto_kem_dec(ss_dec, ct, sk);
    t1 = esp_timer_get_time();
    bool ok = (r_dec == 0) && (memcmp(ss_enc, ss_dec, CRYPTO_BYTES) == 0);
    print_row("decapsulation", i, (uint64_t)(t1 - t0), ok);

    if (i % 100 == 0) {
      Serial.print("# Progress: ");
      Serial.print(i); Serial.print("/"); Serial.println(BENCH_ITER);
    }
  }

  Serial.println("#");
  Serial.println("# ====== BENCHMARK COMPLETE ======");
  Serial.println("# Copy all non-# lines above into your dataset!");
  Serial.println("# Device halted. Reset ESP32 to run again.");
  Serial.flush();

  while (true) {
    vTaskDelay(pdMS_TO_TICKS(1000));
  }
}

void setup() {
  Serial.begin(BAUD_RATE);
  delay(1500);

  /* Spawn benchmark with 64 KB stack on Core 1 to avoid loopTask stack limits */
  xTaskCreatePinnedToCore(
    benchmarkTask,
    "mlkem_bench",
    TASK_STACK_SIZE,
    NULL,
    1,
    NULL,
    1
  );
}

void loop() {
  vTaskDelete(NULL);
}
