import json
import re
from pathlib import Path

transcript_path = Path(r"C:\Users\KARAN PRAJAPATI\.gemini\antigravity-ide\brain\48cd74a5-2183-4f15-9874-0deea0eac87f\.system_generated\logs\transcript_full.jsonl")
output_csv = Path(r"c:\Users\KARAN PRAJAPATI\OneDrive\Desktop\MLKEM-Benchmark\data\raw\esp32_xtensa_lx6_arduino_mlkem_1024_20260916T110000Z.csv")

header = 'experiment_id,run_id,timestamp,environment,measurement_type,architecture,processor,cpu_cores,ram_mb,os,compiler,compiler_version,optimization_flags,implementation,implementation_version,mlkem_variant,operation,iteration,execution_time_ns,memory_bytes,success,error_message'

csv_lines = []

with transcript_path.open('r', encoding='utf-8') as f:
    for line_idx, line in enumerate(f):
        data = json.loads(line)
        if data.get('type') == 'USER_INPUT':
            content = str(data.get('content', ''))
            print(f"Step {line_idx} content length: {len(content)}")
            for text_line in content.splitlines():
                if 'esp32_xtensa_lx6_arduino' in text_line and 'ML-KEM-1024' in text_line:
                    csv_lines.append(text_line.strip())

print(f"Extracted {len(csv_lines)} CSV lines from transcript.")

if csv_lines:
    seen = set()
    unique_lines = []
    for line in csv_lines:
        if line not in seen:
            seen.add(line)
            unique_lines.append(line)
    
    print(f"Unique CSV lines: {len(unique_lines)}")
    
    with output_csv.open('w', encoding='utf-8', newline='\n') as f:
        f.write(header + '\n')
        for line in unique_lines:
            f.write(line + '\n')
    print(f"Saved {output_csv.name} successfully.")
