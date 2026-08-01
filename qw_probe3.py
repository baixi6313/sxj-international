import json

d = json.load(open("qw_798b4cdb136a412ba4cf07c706804ca2.json", encoding="utf-8"))
rl = d["data"]["session"]["record_list"]
rec = rl[0]
print("=== response_messages count:", len(rec["response_messages"]))
for i, m in enumerate(rec["response_messages"]):
    print(f"\n--- response[{i}] keys:", list(m.keys()))
    for k,v in m.items():
        if isinstance(v, str):
            print(f"    {k} (str len={len(v)}): {v[:300]}")
        elif isinstance(v, dict):
            print(f"    {k} (dict keys={list(v.keys())[:10]})")
        elif isinstance(v, list):
            print(f"    {k} (list len={len(v)})")
        else:
            print(f"    {k} = {v}")
