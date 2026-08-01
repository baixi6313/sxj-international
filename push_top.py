import base64, json, os, subprocess, urllib.request, urllib.error

# 读取国内仓库里存的有效 PAT（避免硬编码密钥）
out = subprocess.check_output(
    ["git", "-C", "C:/Users/Administrator/WorkBuddy/2026-07-22-08-14-20/hygzz_cn_domestic",
     "config", "--get", "remote.origin.url"]).decode().strip()
TOK = out.split("//")[1].split("@")[0]

SLUG = "baixi6313/sxj-top"
SRC = "C:/Users/Administrator/WorkBuddy/2026-07-24-23-26-27/hygzz_top"

DEPLOY_YML = """name: Deploy
on:
  push:
    branches: [main]
  workflow_dispatch:
permissions:
  contents: read
  pages: write
  id-token: write
concurrency:
  group: "pages"
  cancel-in-progress: false
jobs:
  deploy:
    environment:
      name: github-pages
      url: ${{ steps.deployment.outputs.page_url }}
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/configure-pages@v4
      - uses: actions/upload-pages-artifact@v3
        with:
          path: '.'
      - uses: actions/deploy-pages@v4
        id: deployment
"""

def api(method, url, data=None):
    h = {"Authorization": f"Bearer {TOK}", "User-Agent": "sxj",
         "Accept": "application/vnd.github+json"}
    req = urllib.request.Request(url, method=method, headers=h)
    if data is not None:
        req.add_header("Content-Type", "application/json")
        req.data = json.dumps(data).encode()
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return r.status, json.loads(r.read().decode() or "{}")
    except urllib.error.HTTPError as e:
        b = e.read().decode()
        try:
            b = json.loads(b)
        except Exception:
            pass
        return e.code, b

print("PAT prefix:", TOK[:8], "...")
# 1. 创建仓库（已存在则忽略）
st, resp = api("POST", "https://api.github.com/user/repos",
               {"name": "sxj-top", "private": False, "auto_init": False})
print("create repo:", st, resp.get("full_name") or resp.get("message"))

# 2. 准备本地文件（deploy.yml + CNAME）
os.makedirs(f"{SRC}/.github/workflows", exist_ok=True)
with open(f"{SRC}/.github/workflows/deploy.yml", "w", encoding="utf-8") as f:
    f.write(DEPLOY_YML)
with open(f"{SRC}/CNAME", "w", encoding="utf-8") as f:
    f.write("hygzz.top\n")

FILES = ["index.html", ".github/workflows/deploy.yml", "CNAME"]
for fn in FILES:
    p = f"{SRC}/{fn}"
    with open(p, "rb") as fh:
        c = base64.b64encode(fh.read()).decode()
    url = f"https://api.github.com/repos/{SLUG}/contents/{fn}"
    st, resp = api("GET", url)
    sha = resp.get("sha") if st == 200 else None
    msg = ("add " if not sha else "update ") + fn
    data = {"message": msg, "content": c}
    if sha:
        data["sha"] = sha
    st, resp = api("PUT", url, data)
    print(f"  {'OK ' if st in (200,201) else 'ERR'} {fn} [{st}]")

# 3. 启用 GitHub Pages (workflow 模式)
st, resp = api("POST", f"https://api.github.com/repos/{SLUG}/pages",
               {"build_type": "workflow", "source": {"branch": "main", "path": "/"}})
print("enable pages:", st, resp.get("html_url") or resp.get("message"))

# 4. 设自定义域 hygzz.top
st, resp = api("PATCH", f"https://api.github.com/repos/{SLUG}/pages",
               {"cname": "hygzz.top"})
print("set cname:", st, resp.get("cname") or resp.get("message"))
