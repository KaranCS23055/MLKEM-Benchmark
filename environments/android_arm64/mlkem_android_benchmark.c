/* Portable Linux ML-KEM runner; Android and RISC-V wrappers set its metadata. */
#define _GNU_SOURCE
#define _POSIX_C_SOURCE 200809L

#include <errno.h>
#include <fcntl.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/random.h>
#include <sys/resource.h>
#include <sys/stat.h>
#include <sys/types.h>
#include <sys/utsname.h>
#include <time.h>
#include <unistd.h>

/* Some Termux Android API headers omit this Linux syscall declaration. */
extern ssize_t getrandom(void *buffer, size_t length, unsigned int flags);

#include "mlkem_native.h"

#ifndef BENCHMARK_PARAMETER_SET
#error "BENCHMARK_PARAMETER_SET must be passed by the build script"
#endif
#ifndef BENCHMARK_VARIANT_LABEL
#error "BENCHMARK_VARIANT_LABEL must be passed by the build script"
#endif
#ifndef BENCHMARK_MEASUREMENT_TYPE
#define BENCHMARK_MEASUREMENT_TYPE "REAL_HARDWARE"
#endif
#ifndef BENCHMARK_ARCHITECTURE
#define BENCHMARK_ARCHITECTURE "aarch64"
#endif
#ifndef BENCHMARK_OPTIMIZATION_FLAGS
#define BENCHMARK_OPTIMIZATION_FLAGS "-O3 -march=armv8-a"
#endif
#if MLK_CONFIG_PARAMETER_SET != BENCHMARK_PARAMETER_SET
#error "Benchmark label and compiled ML-KEM parameter set disagree"
#endif

#ifndef MLKEM_NATIVE_VERSION
#define MLKEM_NATIVE_VERSION "unknown"
#endif
#ifndef MLKEM_NATIVE_COMMIT
#define MLKEM_NATIVE_COMMIT "unknown"
#endif
#ifdef __clang__
#define COMPILER_NAME "clang"
#define COMPILER_VERSION __clang_version__
#else
#define COMPILER_NAME "C compiler"
#define COMPILER_VERSION "unknown"
#endif

static int os_random(unsigned char *buffer, size_t length)
{
  size_t offset = 0;
  while (offset < length) {
    ssize_t got = getrandom(buffer + offset, length - offset, 0);
    if (got > 0) { offset += (size_t)got; continue; }
    if (got < 0 && errno == EINTR) { continue; }
    return -1;
  }
  return 0;
}

/* Required by mlkem-native randomized APIs. Android kernel entropy only. */
int randombytes(unsigned char *buffer, size_t length) { return os_random(buffer, length); }

static long long monotonic_ns(void)
{
  struct timespec value;
  if (clock_gettime(CLOCK_MONOTONIC, &value) != 0) { return -1; }
  return (long long)value.tv_sec * 1000000000LL + value.tv_nsec;
}

static void utc_timestamp(char output[32])
{
  struct timespec value;
  struct tm utc;
  clock_gettime(CLOCK_REALTIME, &value);
  gmtime_r(&value.tv_sec, &utc);
  strftime(output, 32, "%Y-%m-%dT%H:%M:%SZ", &utc);
}

static long memory_bytes(void)
{
  struct rusage usage;
  if (getrusage(RUSAGE_SELF, &usage) != 0 || usage.ru_maxrss <= 0) { return 1; }
  return usage.ru_maxrss * 1024L; /* Linux/Android reports KiB. */
}

static long total_ram_mb(void)
{
  FILE *file = fopen("/proc/meminfo", "r");
  char key[64];
  long kb;
  char unit[16];
  if (file == NULL) { return 1; }
  while (fscanf(file, "%63s %ld %15s", key, &kb, unit) == 3) {
    if (strcmp(key, "MemTotal:") == 0) { fclose(file); return kb / 1024L; }
  }
  fclose(file);
  return 1;
}

static void csv_field(FILE *file, const char *value)
{
  const char *cursor;
  fputc('"', file);
  for (cursor = value; *cursor != '\0'; ++cursor) {
    if (*cursor == '"') { fputc('"', file); }
    fputc(*cursor, file);
  }
  fputc('"', file);
}

static void uuid4(char output[37])
{
  unsigned char bytes[16];
  static const char hex[] = "0123456789abcdef";
  size_t i;
  if (os_random(bytes, sizeof(bytes)) != 0) { memset(bytes, 0, sizeof(bytes)); }
  bytes[6] = (unsigned char)((bytes[6] & 0x0fU) | 0x40U);
  bytes[8] = (unsigned char)((bytes[8] & 0x3fU) | 0x80U);
  for (i = 0; i < sizeof(bytes); ++i) {
    size_t position = i * 2 + (i >= 4) + (i >= 6) + (i >= 8) + (i >= 10);
    output[position] = hex[bytes[i] >> 4];
    output[position + 1] = hex[bytes[i] & 0x0fU];
  }
  output[8] = output[13] = output[18] = output[23] = '-';
  output[36] = '\0';
}

static void write_row(FILE *file, const char *experiment_id, const char *run_id,
                      const char *environment, const char *processor, long cores,
                      long ram_mb, const char *os, const char *variant,
                      const char *operation, int iteration, long long elapsed,
                      int success, const char *error)
{
  char timestamp[32];
  utc_timestamp(timestamp);
  csv_field(file, experiment_id); fputc(',', file); csv_field(file, run_id); fputc(',', file);
  csv_field(file, timestamp); fputc(',', file); csv_field(file, environment); fputc(',', file);
  csv_field(file, BENCHMARK_MEASUREMENT_TYPE); fputc(',', file); csv_field(file, BENCHMARK_ARCHITECTURE); fputc(',', file);
  csv_field(file, processor); fprintf(file, ",%ld,%ld,", cores, ram_mb); csv_field(file, os);
  fputc(',', file); csv_field(file, COMPILER_NAME); fputc(',', file); csv_field(file, COMPILER_VERSION);
  fputc(',', file); csv_field(file, BENCHMARK_OPTIMIZATION_FLAGS); fputc(',', file);
  csv_field(file, "mlkem-native"); fputc(',', file); csv_field(file, MLKEM_NATIVE_VERSION);
  fputc(',', file); csv_field(file, variant); fputc(',', file); csv_field(file, operation);
  fprintf(file, ",%d,%lld,%ld,%s,", iteration, elapsed > 0 ? elapsed : 1LL, memory_bytes(), success ? "True" : "False");
  csv_field(file, error); fputc('\n', file);
}

static int require_argument(int argc, char **argv, const char *name, const char **value)
{
  int index;
  for (index = 1; index + 1 < argc; ++index) {
    if (strcmp(argv[index], name) == 0) { *value = argv[index + 1]; return 0; }
  }
  return -1;
}

int main(int argc, char **argv)
{
  const char *iteration_text = NULL;
  const char *output_path = NULL;
  const char *environment = NULL;
  int iterations;
  int iteration;
  FILE *file;
  int output_fd;
  char experiment_id[37];
  char run_id[37];
  char os[256];
  /* processor: prefer the compile-time SoC label (e.g. MediaTek Helio P65);
   * fall back to uname.machine (typically "aarch64" on ARM Linux). */
#ifdef BENCHMARK_PROCESSOR_LABEL
  const char *processor = BENCHMARK_PROCESSOR_LABEL;
#else
  const char *processor = "aarch64";
#endif
  struct utsname system_info;
  long cores = sysconf(_SC_NPROCESSORS_ONLN);
  const char *variant = BENCHMARK_VARIANT_LABEL;

  if (require_argument(argc, argv, "--iterations", &iteration_text) ||
      require_argument(argc, argv, "--output", &output_path) ||
      require_argument(argc, argv, "--environment", &environment)) {
    fprintf(stderr, "Usage: %s --iterations N --output FILE --environment NAME\n", argv[0]);
    return 2;
  }
  iterations = atoi(iteration_text);
  if (iterations <= 0) { fprintf(stderr, "iterations must be positive\n"); return 2; }
  if (uname(&system_info) == 0) {
    snprintf(os, sizeof(os), "%s %s", system_info.sysname, system_info.release);
    processor = system_info.machine;
  } else { strcpy(os, "Android/Termux"); }
  if (cores <= 0) { cores = 1; }
  output_fd = open(output_path, O_WRONLY | O_CREAT | O_EXCL, 0600);
  if (output_fd < 0) { perror("open output"); return 2; }
  file = fdopen(output_fd, "w");
  if (file == NULL) { close(output_fd); perror("fdopen output"); return 2; }
  fputs("experiment_id,run_id,timestamp,environment,measurement_type,architecture,processor,cpu_cores,ram_mb,os,compiler,compiler_version,optimization_flags,implementation,implementation_version,mlkem_variant,operation,iteration,execution_time_ns,memory_bytes,success,error_message\n", file);
  uuid4(experiment_id); uuid4(run_id);
  for (iteration = 1; iteration <= iterations; ++iteration) {
    unsigned char pk[CRYPTO_PUBLICKEYBYTES], sk[CRYPTO_SECRETKEYBYTES], ct[CRYPTO_CIPHERTEXTBYTES];
    unsigned char shared_enc[CRYPTO_BYTES], shared_dec[CRYPTO_BYTES];
    long long start, elapsed;
    int rc;
    start = monotonic_ns(); rc = crypto_kem_keypair(pk, sk); elapsed = monotonic_ns() - start;
    write_row(file, experiment_id, run_id, environment, processor, cores, total_ram_mb(), os, variant, "keygen", iteration, elapsed, rc == 0, rc == 0 ? "" : "ML-KEM key generation or Android RNG failed");
    rc = crypto_kem_keypair(pk, sk);
    if (rc == 0) { start = monotonic_ns(); rc = crypto_kem_enc(ct, shared_enc, pk); elapsed = monotonic_ns() - start; }
    else { elapsed = 1; }
    write_row(file, experiment_id, run_id, environment, processor, cores, total_ram_mb(), os, variant, "encapsulation", iteration, elapsed, rc == 0, rc == 0 ? "" : "ML-KEM encapsulation setup or Android RNG failed");
    if (rc == 0) { start = monotonic_ns(); rc = crypto_kem_dec(shared_dec, ct, sk); elapsed = monotonic_ns() - start; }
    else { elapsed = 1; }
    if (rc == 0 && memcmp(shared_enc, shared_dec, CRYPTO_BYTES) != 0) { rc = -1; }
    write_row(file, experiment_id, run_id, environment, processor, cores, total_ram_mb(), os, variant, "decapsulation", iteration, elapsed, rc == 0, rc == 0 ? "" : "ML-KEM decapsulation or shared-secret verification failed");
  }
  if (fclose(file) != 0) { perror("close output"); return 2; }
  fprintf(stdout, "Wrote %d rows for %s to %s (source commit %s)\n", iterations * 3, variant, output_path, MLKEM_NATIVE_COMMIT);
  return 0;
}
