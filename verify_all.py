import urllib.request, ssl
urls = [
  "https://hygzz.cn/", "https://www.hygzz.cn/",
  "https://hygzz.com/", "https://www.hygzz.com/",
  "https://hygzz.top/", "https://www.hygzz.top/",
  "https://hygzz.com/whitepaper", "https://hygzz.top/whitepaper",
  "https://hygzz.cn/events", "https://hygzz.com/events", "https://hygzz.top/events",
]
ctx = ssl.create_default_context()
allclean = True
for u in urls:
    try:
        req = urllib.request.Request(u, headers={"User-Agent":"Mozilla/5.0"})
        data = urllib.request.urlopen(req, timeout=30, context=ctx).read().decode("utf-8","ignore")
    except Exception as e:
        print(f"[ERR] {u}: {e}"); allclean=False; continue
    hits = {k: data.count(k) for k in ["beta-banner","测试版","BETA"] if k in data}
    if hits: allclean=False
    print(f"{'OK ' if not hits else 'BAD'} {u}  banner_hits={hits}")
print("\n==> ALL CLEAN:" , allclean)
