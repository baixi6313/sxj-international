import urllib.request, ssl
urls = [
  "https://hygzz.cn/",
  "https://www.hygzz.cn/",
  "https://hygzz.cn/whitepaper",
  "https://hygzz.cn/knowledge_tree",
  "https://hygzz.cn/events",
]
ctx = ssl.create_default_context()
for u in urls:
    try:
        req = urllib.request.Request(u, headers={"User-Agent":"Mozilla/5.0"})
        data = urllib.request.urlopen(req, timeout=30, context=ctx).read().decode("utf-8","ignore")
    except Exception as e:
        print(f"[ERR] {u}: {e}"); continue
    hits = {k: data.count(k) for k in ["beta-banner","测试版","BETA"] if k in data}
    note = "  非实地实施声明保留:%d" % data.count("非实地实施") if "非实地实施" in data else ""
    print(f"{u}  len={len(data)}  banner_hits={hits}{note}")
