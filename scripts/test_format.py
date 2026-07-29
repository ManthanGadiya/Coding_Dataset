"""Test EKR formatting speed."""
import sys; sys.path.insert(0, "src")
from datasets import load_dataset
import json, time

ds = load_dataset("parquet", data_files="release/v0.4/dataset_1m.parquet", split="train")
print(f"loaded {len(ds)}")

def parse_field(v):
    if isinstance(v, str):
        try:
            return json.loads(v)
        except (json.JSONDecodeError, TypeError):
            return []
    return v if isinstance(v, list) else []

def format_ekr(ekr):
    domain = ekr.get("domain", "GEN")
    ep_type = ekr.get("episode_type", ekr.get("_episode_type", "unknown"))
    reasoning = parse_field(ekr.get("reasoning", []))
    decisions = parse_field(ekr.get("decisions", []))
    steps = "\n".join(f"  [{s.get('operation', 'Step')}] {s.get('content', '')}" for s in reasoning)
    dec_text = ""
    if decisions:
        dec_text = "\nDecisions:\n" + "\n".join(f"  - {d.get('decision', d.get('outcome', ''))}" for d in decisions)
    return f"<|domain|> {domain}\n<|episode|> {ep_type}\n<|reasoning|>\n{steps}{dec_text}"

t0 = time.perf_counter()
txt = format_ekr(ds[0])
t1 = time.perf_counter()
print(f"1 record: {(t1-t0)*1000:.1f}ms, length={len(txt)}")
print("---")
print(txt[:300])
print("---")

t2 = time.perf_counter()
for i in range(100):
    _ = format_ekr(ds[i])
t3 = time.perf_counter()
print(f"100 records: {(t3-t2)*1000:.1f}ms ({((t3-t2)/100)*1000:.2f}ms/rec)")
