import json, os, re

SHARE = {
 "798b4cdb136a412ba4cf07c706804ca2": "A",
 "3b6ef11f6dd54f96998b2f1014c11dee": "B",
 "b812d9d299f942d088cf4b40d2626d31": "C",
 "a53255ba934b4f52b242d5b6673cae9c": "D",
 "ae8564ad4e5442c483439b191f65b50f": "E",
 "d668df18c83d42a48e02e3f51d8ed0e7": "F",
}
KW = ["共创论","事现鉴","寰宇光锥舟","全球社保","贡献值","共通值","负贡献","白玺",
       "美元负债","系统置信度","第四次","三值体系","UBV","GZZ","光锥","数字世界统一法",
       "财政直销","双闭环","五卡","事现鉴四维","可逆性","分母缺失","公开验证"]

os.makedirs("qw_transcripts", exist_ok=True)
summary = []
for sid in SHARE:
    d = json.load(open("qw_"+sid+".json", encoding="utf-8"))
    sess = d["data"]["session"]
    title = sess.get("title","")
    rl = sess.get("record_list", [])
    turns = []
    for rec in rl:
        um = "".join(m.get("content","") for m in rec.get("request_messages",[]) if isinstance(m.get("content"),str))
        am_parts = [m["content"] for m in rec.get("response_messages",[]) if isinstance(m.get("content"),str) and m["content"].strip()]
        am = "\n".join(am_parts)
        turns.append((um, am))
    # write transcript
    lines = [f"# {title}\n# share_id={sid}\n# turns={len(turns)}\n\n"]
    for i,(u,a) in enumerate(turns,1):
        lines.append(f"## 第{i}轮 · 用户\n{u}\n")
        lines.append(f"## 第{i}轮 · 千问\n{a}\n")
    txt = "\n".join(lines)
    open(f"qw_transcripts/{SHARE[sid]}_{sid}.txt","w",encoding="utf-8").write(txt)
    # keyword scan over whole text
    hits = {k: len(re.findall(re.escape(k), txt)) for k in KW}
    hits = {k:v for k,v in hits.items() if v}
    # dates
    times = [rec.get("create_time","") for rec in rl if rec.get("create_time")]
    summary.append({
        "tag": SHARE[sid], "sid": sid, "title": title,
        "turns": len(turns), "chars": len(txt),
        "first_user": turns[0][0][:160] if turns else "",
        "first_ai": turns[0][1][:160] if turns else "",
        "keywords": hits,
        "time_span": (times[0], times[-1]) if times else ("",""),
    })
    print(f"[{SHARE[sid]}] {title} | turns={len(turns)} chars={len(txt)} kw={hits}")

json.dump(summary, open("qw_summary.json","w",encoding="utf-8"), ensure_ascii=False, indent=2)
print("\nSaved transcripts -> qw_transcripts/ ; summary -> qw_summary.json")
