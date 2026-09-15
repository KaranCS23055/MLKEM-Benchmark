# ESP8266 (Xtensa LX106 @ 80 MHz) IoT Benchmark Environment

## 📌 Overview
This environment benchmark measures NIST FIPS 203 **ML-KEM-512** on physical resource-constrained IoT silicon: the **Espressif ESP8266EX** microcontroller.

- **Board**: NodeMCU 1.0 (ESP-12E Module)
- **Processor**: Tensilica Xtensa LX106 32-bit RISC core @ 80 MHz
- **RAM**: 80 KB total Data SRAM (~47.6 KB free heap available to user code)
- **Flash**: 4 MB SPI Flash
- **Operating System / RTOS**: Non-OS / FreeRTOS via Arduino Core (v3.1.2)
- **Compiler**: `xtensa-lx106-elf-gcc` with `-O2`
- **Algorithm**: `mlkem-native` v1.2.0 (FIPS 203 C99 reference)
- **Variant**: ML-KEM-512 (Category 1, AES-128 equivalent)

---

## 📁 Directory Structure
```
environments/esp8266_xtensa_lx106_arduino/
├── README.md                          <- This documentation
└── mlkem_esp8266_bench/               <- Arduino IDE Sketch Folder
    ├── mlkem_esp8266_bench.ino        <- Main benchmark sketch (30 iterations per run)
    ├── mlkem_native_config.h          <- Custom zeroize & config header
    ├── zetas.inc                      <- NTT twiddle factors (inlined copy)
    └── mlkem/                         <- mlkem-native v1.2.0 source tree
        ├── mlkem_native.c             <- Unified C source
        ├── mlkem_native.h             <- Unified header
        ├── mlkem_native_asm.S         <- Assembly stubs
        ├── mlkem_native_config.h      <- Config header
        └── src/                       <- Core cryptographic routines (poly.c, ntt.c, etc.)
```

---

## ⚙️ Arduino IDE Setup Instructions

1. **Install Arduino IDE 2.x**: Download from [arduino.cc](https://www.arduino.cc/en/software).
2. **Add ESP8266 Board Manager URL**:
   - Go to `File` -> `Preferences`.
   - In "Additional Boards Manager URLs", add:
     `http://arduino.esp8266.com/stable/package_esp8266com_index.json`
3. **Install ESP8266 Core**:
   - Open `Tools` -> `Board` -> `Boards Manager...`.
   - Search `esp8266` and install `esp8266 by ESP8266 Community`.
4. **Select Board & Configuration**:
   - **Board**: `NodeMCU 1.0 (ESP-12E Module)`
   - **CPU Frequency**: `80 MHz`
   - **Flash Size**: `4MB (FS:2MB OTA:~1019KB)`
   - **Upload Speed**: `115200`
   - **Port**: Select the COM port assigned to your ESP8266 (e.g. `COM4`).
5. **Open Sketch**:
   - Open `environments/esp8266_xtensa_lx106_arduino/mlkem_esp8266_bench/mlkem_esp8266_bench.ino`.
6. **Compile & Upload**:
   - Click **Verify** (✓) to compile.
   - Click **Upload** (➔) to flash the firmware.
7. **Monitor Serial Output**:
   - Open Serial Monitor at **115200 baud**.
   - Output will print standardized 22-column CSV rows for all 30 iterations of KeyGen, Encapsulation, and Decapsulation.

---

## 🔬 Technical Details & Research Findings

### 1. Memory Constraints & Variant Feasibility
- **Data SRAM**: 80,192 bytes (~80 KB). Firmware + FreeRTOS stack uses ~33 KB (40%), leaving ~47 KB.
- **Instruction RAM (IRAM)**: 59,759 / 65,536 bytes (**91% full**).
- **ML-KEM-512**: Requires ~12 KB working stack (PK: 800B + SK: 1,632B + CT: 768B + polynomial arrays). Fits safely.
- **ML-KEM-768 / 1024**: Require > 18 KB and > 26 KB stack memory, and exceed the remaining 5.7 KB of IRAM. **They cannot run safely without causing IRAM compile errors or runtime stack smashing.**

### 2. Implementation Challenges Resolved
- **Zeroize Guard**: ESP8266 libc lacks `memset_s` and inline ASM memory barriers. Solved by defining `MLK_CONFIG_CUSTOM_ZEROIZE` to use a volatile pointer clearing loop.
- **Watchdog Timer (WDT)**: Long lattice operations trigger the ESP8266 hardware WDT. Solved by feeding the watchdog via `ESP.wdtFeed()` between iterations.
- **Hardware RNG**: Seeded using register `0x3FF20E44` (`RANDOM_REG32`), the internal ESP8266 RF/thermal noise hardware random number generator.

### 3. Empirical Results (ML-KEM-512)
- **KeyGen Latency**: 10.725 ms
- **Encapsulation Latency**: 13.256 ms
- **Decapsulation Latency**: 17.179 ms
- **Total Handshake Latency**: **41.160 ms**
- **Verification**: 100% shared secret match across all iterations.\n