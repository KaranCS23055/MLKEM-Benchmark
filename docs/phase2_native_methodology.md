# Phase 2 native methodology

## Implementation

The benchmark uses Python package `pqcrypto==0.4.0` and its native ML-KEM bindings. Its published package documentation lists `ml_kem_512`, `ml_kem_768`, and `ml_kem_1024`. The benchmark calls only these public bindings; it does not reimplement or modify ML-KEM mathematics.

The selected version is pinned in `requirements.txt`. The prebuilt Windows x86-64 wheel is used as `NATIVE_SOFTWARE`; no claim is made that the Python orchestration layer itself is a C-level benchmark harness.

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
