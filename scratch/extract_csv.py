import json
import os
import pandas as pd

transcript_path = r'C:\Users\KARAN PRAJAPATI\.gemini\antigravity-ide\brain\f9d5e477-f553-48a0-962c-f4af54548f2b\.system_generated\logs\transcript_full.jsonl'
last_content = ""
with open(transcript_path, 'r', encoding='utf-8') as f:
    for line in f:
        data = json.loads(line)
        if data.get('type') == 'USER_INPUT':
            last_content = data.get('content', '')

raw_lines = [l.strip() for l in last_content.splitlines()]
valid_lines = []
for l in raw_lines:
    if l.startswith('"5f5ec8df-') and l.endswith('""'):
        parts = l.split(',')
        if len(parts) >= 20:
            valid_lines.append(l)

print(f"Total valid complete CSV lines: {len(valid_lines)}")

header = 'experiment_id,run_id,timestamp,environment,measurement_type,architecture,processor,cpu_cores,ram_mb,os,compiler,compiler_version,optimization_flags,implementation,implementation_version,mlkem_variant,operation,iteration,execution_time_ns,memory_bytes,success,error_message\n'

out_path = r'c:\Users\KARAN PRAJAPATI\OneDrive\Desktop\MLKEM-Benchmark\data\raw\esp32_xtensa_lx6_arduino_mlkem_512_20260916T110000Z.csv'
with open(out_path, 'w', encoding='utf-8', newline='\n') as out_f:
    out_f.write(header)
    for l in valid_lines:
        out_f.write(l + '\n')

df = pd.read_csv(out_path)
print(f"Successfully loaded DataFrame with {len(df)} rows across {df['iteration'].nunique()} iterations.")
for op in ['keygen', 'encapsulation', 'decapsulation']:
    sub = df[df['operation'] == op]['execution_time_ns'] / 1e6
    print(f"  {op:15s}: mean={sub.mean():.3f} ms | median={sub.median():.3f} ms | min={sub.min():.3f} ms | max={sub.max():.3f} ms | std={sub.std():.3f} ms (N={len(sub)})")

keygen_mean = df[df['operation'] == 'keygen']['execution_time_ns'].mean() / 1e6
encap_mean = df[df['operation'] == 'encapsulation']['execution_time_ns'].mean() / 1e6
decap_mean = df[df['operation'] == 'decapsulation']['execution_time_ns'].mean() / 1e6
total_handshake = keygen_mean + encap_mean + decap_mean
print(f"\nTotal Handshake Latency: {total_handshake:.2f} ms")
