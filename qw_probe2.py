import json

d = json.load(open("qw_798b4cdb136a412ba4cf07c706804ca2.json", encoding="utf-8"))
rl = d["data"]["session"]["record_list"]
rec = rl[0]
rm = rec["response_messages"][0]
print("response msg keys:", list(rm.keys()))
md = rm.get("meta_data")
print("meta_data type:", type(md))
print("meta_data (first 1500):")
print(str(md)[:1500])
# try to parse if json
if isinstance(md, str):
    try:
        obj = json.loads(md)
        print("\n--- parsed meta_data keys:", list(obj.keys()) if isinstance(obj,dict) else type(obj))
    except Exception as e:
        print("not json:", e)
