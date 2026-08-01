# -*- coding: utf-8 -*-
"""把事现鉴验证门户(自包含 index.html)推到 GitHub 并启用 Pages。
用法: GH_PAT=xxx python push_portal_github.py
"""
import os, sys, json, base64, urllib.request, urllib.error

TOKEN = os.environ.get("GH_PAT")
if not TOKEN:
    print("[错误] 未提供 GH_PAT 环境变量"); sys.exit(1)

OWNER = "baixi6313"
REPO = "sxj-verify-portal"
PORTAL = os.path.join(os.path.dirname(os.path.abspath(__file__)), "portal", "index.html")
API = "https://api.github.com"

def api(method, path, body=None, accept="application/vnd.github+json"):
    url = API + path
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(url, data=data, method=method)
    req.add_header("Authorization", "Bearer " + TOKEN)
    req.add_header("Accept", accept)
    req.add_header("User-Agent", "sxj-portal-push")
    if data:
        req.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return r.status, (r.read().decode() or "")
    except urllib.error.HTTPError as e:
        return e.code, (e.read().decode() or "")

# 1) 仓库是否存在
st, _ = api("GET", f"/repos/{OWNER}/{REPO}")
if st == 404:
    print(f"[1] 创建仓库 {OWNER}/{REPO} ...")
    st2, resp = api("POST", "/user/repos", {
        "name": REPO, "public": True,
        "description": "事现鉴(SXJ)全量可验证对话档案 · 对外验证门户（自包含静态页）",
        "auto_init": False,
    })
    print("    ->", st2, (json.loads(resp).get("html_url") if st2 < 300 else resp[:200]))
elif st == 200:
    print(f"[1] 仓库已存在 {OWNER}/{REPO}，跳过创建")
else:
    print("[1] 仓库检查异常:", st); sys.exit(1)

# 2) 上传 index.html（存在则更新）
with open(PORTAL, "rb") as f:
    content_b64 = base64.b64encode(f.read()).decode()
content_sha = None
st_get, resp_get = api("GET", f"/repos/{OWNER}/{REPO}/contents/index.html")
if st_get == 200:
    content_sha = json.loads(resp_get).get("sha")
    print("[2] index.html 已存在，更新中 ...")
else:
    print("[2] 上传 index.html ...")
put_body = {
    "message": "add SXJ verification portal (self-contained)",
    "content": content_b64,
    "branch": "main",
}
if content_sha:
    put_body["sha"] = content_sha
st3, resp3 = api("PUT", f"/repos/{OWNER}/{REPO}/contents/index.html", put_body)
print("    ->", st3, (json.loads(resp3).get("content", {}).get("html_url") if st3 < 300 else resp3[:200]))

# 3) 启用 GitHub Pages
print("[3] 启用 GitHub Pages ...")
st4, resp4 = api("POST", f"/repos/{OWNER}/{REPO}/pages", {
    "source": {"branch": "main", "path": "/"},
    "build_type": "legacy",
})
if st4 in (201, 200):
    html_url = json.loads(resp4).get("html_url")
    print("    -> Pages 已启用:", html_url)
elif st4 == 409:
    # 已启用，取当前状态
    st5, resp5 = api("GET", f"/repos/{OWNER}/{REPO}/pages")
    print("    -> 已启用:", json.loads(resp5).get("html_url") if st5 < 300 else resp5[:200])
else:
    print("    -> Pages 启用返回", st4, resp4[:300])
    print("    可手动在仓库 Settings > Pages 选择 main 分支启用。")

print("\n[完成] 仓库: https://github.com/%s/%s" % (OWNER, REPO))
print("       Pages: https://%s.github.io/%s/" % (OWNER, REPO))
