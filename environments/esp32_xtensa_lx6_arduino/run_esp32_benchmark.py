#!/usr/bin/env python3
"""
Automated ML-KEM Benchmarking Runner for ESP32
Compiles, flashes, and captures standardized CSV output from ESP32 over serial UART.
"""

import os
import sys
import time
import datetime
import subprocess
import argparse
import serial
import serial.tools.list_ports

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

ARDUINO_CLI = r"C:\Users\KARAN PRAJAPATI\AppData\Local\Programs\Arduino IDE\resources\app\lib\backend\resources\arduino-cli.exe"
FQBN = "esp32:esp32:esp32"
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(BASE_DIR, "..", ".."))
RAW_DATA_DIR = os.path.join(PROJECT_ROOT, "data", "raw")

SKETCH_DIRS = {
    "512": os.path.join(BASE_DIR, "mlkem_esp32_bench_512"),
    "768": os.path.join(BASE_DIR, "mlkem_esp32_bench_768"),
    "1024": os.path.join(BASE_DIR, "mlkem_esp32_bench_1024"),
}

def find_default_port():
    ports = [p.device for p in serial.tools.list_ports.comports() if "USB" in p.description or "CH340" in p.description or "CH9102" in p.description or "CP210" in p.description]
    if ports:
        return ports[0]
    all_ports = [p.device for p in serial.tools.list_ports.comports()]
    return all_ports[0] if all_ports else "COM5"

def compile_sketch(sketch_path):
    print(f"[*] Compiling sketch: {sketch_path}")
    cmd = [ARDUINO_CLI, "compile", "--fqbn", FQBN, sketch_path]
    res = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
    if res.returncode != 0:
        print("[!] Compilation failed:")
        print(res.stderr)
        return False
    print("[+] Compilation succeeded.")
    return True

def upload_sketch(sketch_path, port):
    print(f"[*] Uploading firmware to {port}...")
    cmd = [ARDUINO_CLI, "upload", "-p", port, "--fqbn", FQBN, sketch_path]
    res = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
    if res.returncode != 0:
        print("[!] Upload failed:")
        print(res.stderr)
        return False
    print("[+] Firmware uploaded successfully.")
    return True

def capture_benchmark(port, baudrate, variant, timeout_sec=90):
    print(f"[*] Opening {port} at {baudrate} baud...")
    time.sleep(1.0)
    
    ser = serial.Serial(port, baudrate=baudrate, timeout=1.0)
    # Toggle DTR/RTS to reset the ESP32 cleanly
    ser.setDTR(False)
    ser.setRTS(True)
    time.sleep(0.1)
    ser.setRTS(False)
    time.sleep(0.5)

    csv_lines = []
    header_found = False
    last_activity = time.time()
    inactivity_timeout_sec = 20.0
    
    print("[*] Listening for benchmark CSV stream...")
    
    while (time.time() - last_activity) < inactivity_timeout_sec:
        line = ser.readline().decode("utf-8", errors="replace").strip()
        if not line:
            continue
        last_activity = time.time()
        
        if line.startswith("# Progress:"):
            print(f"  ESP32 -> {line}")
        elif not line.startswith('"') and not line.startswith('experiment_id'):
            print(f"  ESP32 -> {line}")
            
        if line.startswith("experiment_id,run_id"):
            header_found = True
            csv_lines.append(line)
        elif header_found and line.startswith('"') and not line.startswith('#'):
            csv_lines.append(line)
        elif "BENCHMARK COMPLETE" in line:
            print("[+] Benchmark run finished on device.")
            break
            
    ser.close()
    
    if not csv_lines:
        print("[!] Error: No CSV data received from device.")
        return None
        
    ts = datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    out_filename = f"esp32_xtensa_lx6_arduino_mlkem_{variant}_{ts}.csv"
    out_path = os.path.join(RAW_DATA_DIR, out_filename)
    
    os.makedirs(RAW_DATA_DIR, exist_ok=True)
    with open(out_path, "w", encoding="utf-8", newline="\n") as f:
        for cl in csv_lines:
            f.write(cl + "\n")
            
    print(f"[+] Saved {len(csv_lines)-1} benchmark records to: {out_path}")
    return out_path

def main():
    parser = argparse.ArgumentParser(description="Run ML-KEM Benchmark on ESP32")
    parser.add_argument("--variant", choices=["512", "768", "1024", "all"], default="all",
                        help="ML-KEM variant to benchmark (512, 768, 1024, or all)")
    parser.add_argument("--port", default=find_default_port(),
                        help="Serial COM port (default: auto-detected)")
    parser.add_argument("--baud", type=int, default=115200,
                        help="Serial baud rate (default: 115200)")
    parser.add_argument("--skip-compile", action="store_true",
                        help="Skip compilation step and flash existing build")
    parser.add_argument("--capture-only", action="store_true",
                        help="Only capture serial output (if already flashed via Arduino IDE)")
    args = parser.parse_args()

    variants = ["512", "768", "1024"] if args.variant == "all" else [args.variant]
    
    for v in variants:
        print(f"\n{'='*60}")
        print(f"  BENCHMARKING ML-KEM-{v} ON ESP32 ({args.port})")
        print(f"{'='*60}")
        
        sketch_path = SKETCH_DIRS[v]
        if not args.capture_only:
            if not args.skip_compile:
                if not compile_sketch(sketch_path):
                    sys.exit(1)
                    
            if not upload_sketch(sketch_path, args.port):
                sys.exit(1)
            
        csv_file = capture_benchmark(args.port, args.baud, v)
        if not csv_file:
            print(f"[!] Failed to capture benchmark for ML-KEM-{v}")
            if not args.capture_only:
                sys.exit(1)
            
    print("\n[✓] All requested ML-KEM benchmarks completed successfully!")

if __name__ == "__main__":
    main()
