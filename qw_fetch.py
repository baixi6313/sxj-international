import urllib.request, json, os

share_ids = [
 "798b4cdb136a412ba4cf07c706804ca2",
 "3b6ef11f6dd54f96998b2f1014c11dee",
 "b812d9d299f942d088cf4b40d2626d31",
 "a53255ba934b4f52b242d5b6673cae9c",
 "ae8564ad4e5442c483439b191f65b50f",
 "d668df18c83d42a48e02e3f51d8ed0e7",
]
url = "https://chat2-api.qianwen.com/api/v1/share/info"
for sid in share_ids:
    req = urllib.request.Request(url,
        data=json.dumps({"share_id": sid}).encode(),
        headers={"User-Agent":"Mozilla/5.0","Content-Type":"application/json",
                  "Referer":"https://www.qianwen.com/share/chat/"+sid})
    try:
        with urllib.request.urlopen(req, timeout=40) as r:
            data = r.read()
        open("qw_"+sid+".json","wb").write(data)
        print(sid, "OK bytes=", len(data))
    except Exception as e:
        print(sid, "ERR", repr(e))

# probe structure of first
print("\n=== STRUCTURE PROBE (798b...) ===")
d = json.load(open("qw_798b4cdb136a412ba4cf07c706804ca2.json", encoding="utf-8"))
print("top keys:", list(d.keys()))
data = d.get("data", {})
print("data keys:", list(data.keys()))
sess = data.get("session", {})
print("session keys:", list(sess.keys()))
rl = data.get("record_list", [])
print("record_list len:", len(rl))
if rl:
    rec0 = rl[0]
    print("record[0] keys:", list(rec0.keys()))
    for k,v in rec0.items():
        if isinstance(v, list):
            print("  ", k, "list len", len(v))
            if v and isinstance(v[0], dict):
                print("    item[0] keys:", list(v[0].keys()))
        else:
            s = str(v)
            print("  ", k, "=", s[:120])
