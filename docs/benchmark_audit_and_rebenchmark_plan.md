# Benchmark audit and clean re-benchmark plan

## What the current files establish

`data/raw/` currently has 17 CSV files and 63,000 successful operation rows:

- 45,000 rows are compiled-C measurements using `mlkem-native v1.2.0`:
  Android ARM64 (real hardware), x86-64 WSL2, x86-64 WSL2 pinned to one logical CPU, x86-32 WSL2, and RISC-V QEMU (emulated).
- 18,000 rows are Windows measurements through Python `pqcrypto 1.0.0`.  These are valid wrapper-level measurements, but are **not** directly comparable with the compiled-C `mlkem-native` measurements.  They must not be described as measurements of the same binary, compiler, or optimization flags.
- RISC-V QEMU is emulation, not physical RISC-V performance.
- A SHA-256 manifest can detect later file modification. It cannot independently prove that the benchmark was run on the hardware named in the CSV.

Do not call the full collection "seven independent hardware devices." There are seven execution configurations, but several x86 configurations share a physical host.

The README summary table's **Throughput** column is also not a comparable "total handshake throughput" measure. For the older C rows it equals `1 / mean(encapsulation time)`; for the two Windows Python rows it equals `1 / mean(keygen time)`. A total-handshake throughput, if operations are serial, must instead be `1 / (mean_keygen + mean_encapsulation + mean_decapsulation)`. Relabel or regenerate that column before using it in a report.

## Important interpretation rules

`cpu_cores` is not consistently a physical-core count. On the Ryzen 5 4600H host, `12` means 6 physical cores with SMT, hence 12 logical CPUs. The WSL2 C harness records `sysconf(_SC_NPROCESSORS_ONLN)`, which returns logical CPUs. A pinned run has `cpu_cores = 1` because the process is restricted to one logical CPU, not because the laptop has one core.

The Windows "multi-core" run is a single Python process with no parallel ML-KEM workers. The OS may move it among logical CPUs; it is not a 12-core throughput test. Label it **"unpinned single-process"**. The `0x1` run pins it to logical CPU 0; that improves repeatability but does not guarantee it is a performance core on every Windows topology.

`memory_bytes` is process RSS/working-set information. It is neither ML-KEM's per-operation RAM usage nor flash memory. Measure flash with the compiled executable's `.text + .rodata + .data` size, and embedded RAM with the linker map, stack watermark, and static `.data + .bss` size.

## Why values fluctuate

The algorithm inputs and FIPS 203 parameter sets are fixed; their key, ciphertext, and shared-secret sizes do not vary by processor. Timing does vary because of clock frequency/turbo, cache state, scheduler interrupts, background work, CPU migration, thermal throttling, OS timer implementation, compiler flags, implementation/backend, random-number generation, and (on phones) big/little core selection.

Larger ML-KEM parameter sets normally take longer, but a single mean can break this order when the sample has high noise or when different optimized code paths are used. The x86-32 ML-KEM-768 mean being lower than ML-KEM-512 is therefore a warning to report median/P95 and repeat independent runs; it is not evidence that ML-KEM-768 is intrinsically cheaper.

## Clean benchmark protocol

1. Pick one implementation and one commit: use the included `third_party/mlkem-native` C source for every device. Do not mix Python-wrapper results into the same comparison table.
2. Compile separately for each target architecture with the recorded compiler version and flags (for example `-O3`; do not use `-march=native` unless it is recorded and intended).
3. Record the CPU model, physical cores, logical CPUs, OS, governor/power mode, temperature/battery state, compiler, flags, implementation commit, and timer source in a manifest.
4. Warm up 1,000 untimed operations. Then collect at least 30 independent batches of 1,000 timed operations per variant and operation. Each CSV row should be one operation time; report median, mean, standard deviation, P95, and the batch-to-batch spread.
5. Use a monotonic timer around only the target operation. Key generation used to prepare an encapsulation or decapsulation input must be outside that operation's timed interval.
6. Validate every iteration: decapsulated shared secret must equal the encapsulated one. Keep failures; never silently discard them.
7. For a single-logical-CPU run, pin the process and verify the actual affinity. For Windows hybrid CPUs, identify a P-core using topology tools rather than assuming logical CPU 0.
8. Store raw CSV, binary hash, source commit, build command, and SHA-256 manifest. Build derived statistics into a separate output directory; do not alter raw evidence.

## Included runners

The compiled-C runner already exists at `environments/native_x86_64_mlkem_native/mlkem_x86_native_bench.c`; its WSL2 build script is `environments/native_x86_64_mlkem_native/build_and_run_wsl.sh`. It compiles ML-KEM-512, -768, and -1024 separately, times key generation/encapsulation/decapsulation, and records 3,000 rows per variant for a 1,000-iteration configuration.

For a new physical device, port that same C harness and build script. Android uses the sibling Termux runner. For bare-metal devices, replace the POSIX clock with a verified hardware cycle counter and report both cycles and clock frequency; do not use the Renode Cortex-M4 functional run as a timing result.
