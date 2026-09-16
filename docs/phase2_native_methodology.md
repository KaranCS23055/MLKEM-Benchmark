# Benchmark methodology and provenance

## Implementation

The admitted benchmark dataset uses unchanged `mlkem-native v1.2.0` C99 implementations for ML-KEM-512, ML-KEM-768, and ML-KEM-1024. The project does not reimplement or modify ML-KEM mathematics. Earlier `pqcrypto==0.4.0` experiments are historical reference data under `data/archive/` and are not the current admitted dataset.

The execution type is recorded in every row. The current x86_64 profiles are `NATIVE_SOFTWARE`; Android and Xtensa firmware runs are `REAL_HARDWARE`. The Python tools process and validate CSV output but do not turn native software timings into physical-device measurements.

## Timing method

`time.perf_counter_ns()` surrounds only the operation under measurement:

- KeyGen: native `generate_keypair()`.
- Encapsulation: native `encrypt(public_key)`. Recipient key creation is setup, excluded from timing.
- Decapsulation: native `decrypt(secret_key, ciphertext)`. Key and ciphertext creation are setup, excluded from timing.

Each decapsulated secret is compared byte-for-byte with the encapsulated secret. Any exception or mismatch is retained as a failed CSV row and causes later validation to flag the record.

## Memory method

On Windows, `memory_bytes` is the process working-set size sampled immediately after each operation via Windows process APIs. On Linux/Android, it is the process maximum resident-set-size high-water mark from `getrusage`, converted to bytes. Neither is a per-operation allocation measurement; the manifest records the exact definition.

## Provenance limitations

The runner obtains OS, architecture, logical CPU count, total RAM, Python version, and package version at execution. The sandbox denied WMI hardware queries, so the processor model may be recorded as unknown. This is retained transparently rather than inferred.
