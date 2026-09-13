# Processor Rollout — Completed Environments & Rationale

## ✅ Completed environments (63,000 rows total)

| Environment | Hardware | Rows | Date | Rationale |
| :--- | :--- | ---: | :--- | :--- |
| `native_x86_64_wsl2_mlkem_native` | AMD Ryzen 5 4600H (Multi-Core) | 9,000 | 2026-08-13 | 64-bit SIMD baseline; modern x86 workstation |
| `native_x86_64_wsl2_mlkem_native` | Intel Core i7-11800H (Multi-Core) | 9,000 | 2026-09-13 | Higher-end x86-64 comparison point; same env ID, processor field distinguishes |
| `native_x86_64_single_core_wsl2_mlkem_native` | AMD Ryzen 5 4600H (taskset -c 0) | 9,000 | 2026-08-13 | Isolates per-core latency; removes OS migration noise |
| `native_x86_64_single_core_wsl2_mlkem_native` | Intel Core i7-11800H (taskset -c 0) | 9,000 | 2026-09-13 | Same isolation for i7; confirms single-threaded nature of ML-KEM |
| `android_vivo_y19_termux` | MediaTek Helio P65 ARM64 (Vivo Y19) | 9,000 | 2026-08-12 | Real physical smartphone silicon; ARM64 deployment target |
| `native_x86_32_wsl2_mlkem_native` | AMD Ryzen 5 4600H (gcc -m32) | 9,000 | 2026-09-12 | Legacy 32-bit simulation: ATMs, PLCs, SCADA, medical devices |
| `riscv64_qemu_linux` | RISC-V RV64GC (QEMU emulated) | 9,000 | 2026-08-12 | Emerging IoT RISC-V coverage before physical boards available |

---

## 🗺️ Why each environment was chosen

### x86-64 Multi-Core (AMD Ryzen 5 4600H + Intel Core i7-11800H)
**Target:** Cloud servers, workstations, laptops running 64-bit Linux/Windows.  
**Purpose:** Establishes the performance ceiling achievable with full AVX2 SIMD on modern x86-64.
Two different CPUs under the same environment ID allows processor-level comparison. The `processor` column in each CSV distinguishes them.

### x86-64 Single-Core (`taskset -c 0`)
**Target:** Containerized microservices with CPU pinning, embedded x86 SBCs with one active core.  
**Purpose:** Eliminates OS scheduler core-migration noise. ML-KEM is inherently single-threaded — this confirms that adding more cores brings zero benefit to a single operation. The ~1–2 µs difference vs multi-core is pure scheduler jitter.

### ARM64 Real Hardware (MediaTek Helio P65 — Vivo Y19)
**Target:** Android/iOS smartphones, tablets, ARM-based servers (AWS Graviton, Apple M-series).  
**Purpose:** Real silicon measurements — not emulated. Proves ML-KEM-512 handshake completes in 151 µs on mid-range mobile hardware, well within TLS budgets.

### Legacy 32-bit x86 (`gcc -m32` on AMD Ryzen 5 4600H)
**Target:** ATMs (Diebold/NCR on Windows XP Embedded), factory PLCs, medical devices, SCADA, government voting machines — all running 32-bit OS on 32-bit or legacy-mode 64-bit hardware.

**Why this is critical for the 2030 deadline:**  
Governments and standards bodies (NIST, ENISA, BSI) mandate post-quantum migration by 2030. Hundreds of millions of 32-bit devices exist in critical infrastructure with 10–15 year replacement cycles — they **cannot** all be upgraded before the deadline.

**What the data proves:**
- 32-bit mode = **3.2× slower** than 64-bit on identical hardware (72.4 µs vs 22.5 µs keygen)
- Reason: `gcc -m32` disables AVX2/SSE4 SIMD; mlkem-native falls back to scalar C99
- A 32-bit Ryzen (241.9 µs handshake) is **60% slower than an ARM64 phone** (151.1 µs) — counterintuitive but proven
- ML-KEM-512 handshake at 241.9 µs is **still within a 1–10 ms TLS budget** → feasible but CPU-intensive
- ML-KEM-1024 at 590.6 µs is tight for real-time systems → ML-KEM-512 is the recommended variant for legacy 32-bit

### RISC-V 64-bit QEMU (Emulated `rv64gc`)
**Target:** Emerging embedded RISC-V boards (SiFive HiFive, StarFive VisionFive, Kendryte K210, Espressif ESP32-C3/C6).

**Why emulated (not real hardware):**  
Physical RISC-V Linux boards are not currently available in this project's hardware inventory. QEMU `rv64gc` provides a standardized, reproducible RISC-V Linux environment using the same `gcc -O3` toolchain. Results are labeled `EMULATED` and must not be compared directly to `NATIVE_SOFTWARE` or `REAL_HARDWARE` rows.

**What the data proves:**
- QEMU RISC-V = **~15× slower** than native x86-64 (290 µs vs 18.7 µs keygen)
- Overhead is entirely from QEMU's dynamic binary translation (DBT) — not the RISC-V ISA itself
- Real RISC-V hardware (e.g., SiFive P670 @ 1.4 GHz) would likely perform between ARM64 phone and 32-bit x86
- Confirms that a RISC-V physical board benchmark is a high-priority future expansion

---

## 📋 Required rule for every new target

For each new architecture:
1. Build **unchanged** `mlkem-native v1.2.0` source with target compiler
2. Validate all 3 variants × 3 operations (KeyGen, Encap, Decap) pass `memcmp` shared-secret check
3. Run **100 calibration iterations** → validate schema, row count, field types
4. Run **1,000 final iterations** → 3,000 rows per CSV, 9,000 rows per environment
5. Generate SHA-256 manifest via `create_manifest.py`
6. Run `scripts/verify_dataset.py` → must report ALL PASS before merging into `data/raw/`
7. **Never synthesize, interpolate, or copy** timing values from other processors

---

## 🔭 Future Hardware Expansion Targets

| Target | Architecture | Type | Priority | Notes |
| :--- | :--- | :--- | :--- | :--- |
| SiFive HiFive Unmatched | `riscv64` | `REAL_HARDWARE` | High | Replace QEMU with real silicon |
| Raspberry Pi 4 (64-bit) | `aarch64` | `REAL_HARDWARE` | High | Second ARM64 data point |
| STM32F407 Discovery | `armv7-m` (Cortex-M4) | `REAL_HARDWARE` | Medium | Requires DWT cycle counter, not POSIX clock |
| Raspberry Pi Pico 2 (RP2350) | `armv8-m` (Cortex-M33) | `REAL_HARDWARE` | Medium | Bare-metal, 520 KB SRAM |
| ESP32-S3 | `xtensa-lx7` | `REAL_HARDWARE` | Low | Xtensa ISA, 512 KB SRAM |
