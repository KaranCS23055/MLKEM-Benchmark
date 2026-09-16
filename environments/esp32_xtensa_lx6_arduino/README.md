# ESP32 (Xtensa LX6 Dual-Core @ 240 MHz) IoT Benchmark Environment

## 📌 Overview
This environment benchmark measures NIST FIPS 203 **ML-KEM-512**, **ML-KEM-768**, and **ML-KEM-1024** on physical IoT silicon: the **Espressif ESP32** microcontroller.

- **Board**: ESP32 Dev Module (e.g. NodeMCU-32S / ESP-WROOM-32)
- **Processor**: Dual-Core Tensilica Xtensa LX6 @ 240 MHz
- **RAM**: ~520 KB total SRAM (~300+ KB free heap available to user code)
- **Flash**: 4 MB – 16 MB SPI Flash
- **Operating System / RTOS**: FreeRTOS via ESP-IDF / Arduino Core
- **Compiler**: `xtensa-esp32-elf-gcc` with `-O2`
- **Algorithm**: `mlkem-native` v1.2.0 (FIPS 203 C99 reference)
- **Variants Supported**: **ML-KEM-512**, **ML-KEM-768**, **ML-KEM-1024** (All 3 variants)

---

## 📁 Directory Structure
```
environments/esp32_xtensa_lx6_arduino/
├── README.md                          <- Documentation
├── run_esp32_benchmark.py             <- Automated CLI compiler, flasher & data capturer
├── mlkem_esp32_bench_512/             <- ML-KEM-512 Arduino Sketch
│   ├── mlkem_esp32_bench_512.ino
│   ├── mlkem_native_config.h
│   ├── zetas.inc
│   └── mlkem/                         <- mlkem-native C tree
├── mlkem_esp32_bench_768/             <- ML-KEM-768 Arduino Sketch
│   ├── mlkem_esp32_bench_768.ino
│   ├── mlkem_native_config.h
│   ├── zetas.inc
│   └── mlkem/
└── mlkem_esp32_bench_1024/            <- ML-KEM-1024 Arduino Sketch
    ├── mlkem_esp32_bench_1024.ino
    ├── mlkem_native_config.h
    ├── zetas.inc
    └── mlkem/
```

---

## 🚀 Running Benchmarks Automatically (CLI)

You can run automated compilation, flashing, and dataset capture using the Python runner:

```bash
# Run all three variants (512, 768, and 1024)
python environments/esp32_xtensa_lx6_arduino/run_esp32_benchmark.py --variant all --port COM5

# Or run a specific variant:
python environments/esp32_xtensa_lx6_arduino/run_esp32_benchmark.py --variant 512 --port COM5
python environments/esp32_xtensa_lx6_arduino/run_esp32_benchmark.py --variant 768 --port COM5
python environments/esp32_xtensa_lx6_arduino/run_esp32_benchmark.py --variant 1024 --port COM5
```

The script will:
1. Compile the respective sketch.
2. Flash the firmware onto the ESP32 via USB serial.
3. Capture the 22-column CSV stream into `data/raw/esp32_xtensa_lx6_arduino_mlkem_<variant>_<timestamp>.csv`.

---

## ⚙️ Running via Arduino IDE GUI

1. **Install ESP32 Core** (if not already installed):
   - Go to `File` -> `Preferences`.
   - In "Additional Boards Manager URLs", add:
     `https://raw.githubusercontent.com/espressif/arduino-esp32/gh-pages/package_esp32_index.json`
   - Go to `Tools` -> `Board` -> `Boards Manager...`, search `esp32` and install `esp32 by Espressif Systems`.
2. **Select Board & Configuration**:
   - **Board**: `ESP32 Dev Module`
   - **CPU Frequency**: `240MHz (WiFi/BT)`
   - **Flash Frequency**: `80MHz`
   - **Upload Speed**: `921600` (or `115200`)
   - **Port**: Select your ESP32 COM port (e.g. `COM5`).
3. **Open & Upload Sketch**:
   - Open `mlkem_esp32_bench_512.ino`, `mlkem_esp32_bench_768.ino`, or `mlkem_esp32_bench_1024.ino`.
   - Click **Upload** (➔).
   - Open **Serial Monitor** at **115200 baud** to view real-time benchmark results.
