import urllib.request, json, time, zipfile, io, base64

TOKEN = __import__("os").environ.get("GH_PAT", "")
REPO = "baixi6313/sxj-android-app"
H = {"Authorization": f"Bearer {TOKEN}", "User-Agent": "poll", "Accept": "application/vnd.github+json"}

def get(path, accept=None):
    h = dict(H)
    if accept: h["Accept"] = accept
    req = urllib.request.Request(f"https://api.github.com/repos/{REPO}/{path}", headers=h)
    with urllib.request.urlopen(req, timeout=60) as r:
        return r.read().decode("utf-8")

# 1) wait for the latest run (triggered by our push) to finish
print("等待云端构建...")
run = None
for i in range(24):  # up to ~12 min
    data = json.loads(get("actions/runs?per_page=1"))
    run = data["workflow_runs"][0]
    print(f"  [{i}] run {run['id']} status={run['status']} conclusion={run['conclusion']}")
    if run["status"] == "completed":
        break
    time.sleep(30)

if run["status"] != "completed" or run["conclusion"] != "success":
    print("!! 构建未完成/失败:", run.get("html_url"))
    raise SystemExit(1)

print("构建成功。检查 Release v1.0 资产...")
rel = json.loads(get("releases/tags/v1.0"))
apk = next(a for a in rel["assets"] if a["name"] == "app-debug.apk")
print(f"  app-debug.apk  updated_at={apk['updated_at']}  size={apk['size']}")

# 2) download APK and inspect embedded js/app.js
print("下载 APK 并解包校验...")
req = urllib.request.Request(apk["browser_download_url"], headers={"User-Agent": "x"})
raw = urllib.request.urlopen(req, timeout=120).read()
print(f"  APK 下载字节数={len(raw)}")
z = zipfile.ZipFile(io.BytesIO(raw))
names = [n for n in z.namelist() if n.endswith("js/app.js")]
print("  内嵌 js/app.js 路径:", names)
bad = False
for n in names:
    txt = z.read(n).decode("utf-8", "ignore")
    if "(BETA)" in txt or "beta-banner" in txt or "测试版" in txt:
        bad = True
        print(f"  [!!] 发现横幅残留于 {n}")
    else:
        print(f"  [OK] {n} 无横幅残留")
print("\n==> APK 横幅校验:", "失败(仍有BETA)" if bad else "通过(已无BETA)")
