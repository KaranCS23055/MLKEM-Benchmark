# Phase 5 scaled native run

The Phase 5 native x86-64 experiment used the configuration in configs/native_x86_64_1000.json. It was selected after Phase 4 calibration estimated 978 iterations for the highest-variation configuration at a 95% confidence target with a 5% relative margin.

## Execution

Command:

    .\.venv\Scripts\python.exe scripts\run_benchmark.py --config configs\native_x86_64_1000.json

The run produced 9,000 independent raw measurements: three variants times three operations times 1,000 iterations. Every decapsulation result was compared with the paired encapsulated shared secret.

## Integrity

The raw CSV is append-only and was validated after execution. All 9,000 rows succeeded, including 3,000 successful decapsulation/shared-secret checks. The original 100-iteration calibration files remain unchanged.
