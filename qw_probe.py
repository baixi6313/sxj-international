import json

def load(sid):
    return json.load(open("qw_"+sid+".json", encoding="utf-8"))

sid = "798b4cdb136a412ba4cf07c706804ca2"
d = load(sid)
sess = d["data"]["session"]
rl = sess["record_list"]
print("record_list len:", len(rl))
print("session title:", sess.get("title"))
if rl:
    rec0 = rl[0]
    print("rec0 keys:", list(rec0.keys()))
    for k,v in rec0.items():
        if isinstance(v, list):
            print("  ", k, "len", len(v))
            if v and isinstance(v[0], dict):
                print("     item0 keys:", list(v[0].keys()))
        else:
            print("  ", k, "=", str(v)[:100])
    # look at message content samples
    for k in ("request_messages","response_messages","messages","answer_messages"):
        if k in rec0 and rec0[k]:
            m = rec0[k][0]
            print(f"  >>> {k}[0] sample keys:", list(m.keys()))
            # print any content-ish field
            for ck in ("content","text","role","author","user_type","message"):
                if ck in m:
                    val = str(m[ck])
                    print(f"      {ck} = {val[:200]}")
