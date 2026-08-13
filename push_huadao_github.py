#!/usr/bin/env python3
# 化债讨论稿 + 经济学模型 推 GitHub 备份（sxj-2026-08-08）
# 用法：设置环境变量 GH_PAT 后运行：python push_huadao_github.py
import os, base64, json, urllib.request, urllib.parse, urllib.error

TOKEN = os.environ.get("GH_PAT")
if not TOKEN:
    print("ERROR: 环境变量 GH_PAT 未设置。请先 export GH_PAT=ghp_xxx 再运行。"); raise SystemExit(1)

USER, REPO = "baixi6313", "sxj-2026-08-08"
FILES = [
    "事现鉴-化债ABM与五卡补完-讨论.md",
    "事现鉴-化债范式合成.md",
    "事现鉴-化债操作引擎-矩阵赛马热密度.md",
    "化债引擎→canon映射.md",
    "sxj-economics-model.html",
]
H = {"Authorization": "token " + TOKEN, "Accept": "application/vnd.github+json"}

def api(path, method="GET", data=None):
    url = "https://api.github.com/repos/%s/%s/contents/%s" % (USER, REPO, urllib.parse.quote(path))
    req = urllib.request.Request(url, data=(json.dumps(data).encode() if data else None), headers=H, method=method)
    return urllib.request.urlopen(req)

# 取默认分支
try:
    repo = json.load(api(""))
    BRANCH = repo.get("default_branch", "main")
except Exception as e:
    BRANCH = "main"
    print("取默认分支失败，回退 main：", e)

print("目标仓库 %s/%s @ %s" % (USER, REPO, BRANCH))

def sha_of(path):
    try:
        d = json.load(api(path)); return d.get("sha")
    except urllib.error.HTTPError:
        return None

ok = 0
for f in FILES:
    if not os.path.exists(f):
        print("SKIP 本地缺失：", f); continue
    with open(f, "rb") as fh:
        content = base64.b64encode(fh.read()).decode()
    data = {"message": "docs: 化债引擎讨论稿+canon映射+经济学模型v0.6 备份", "content": content, "branch": BRANCH}
    s = sha_of(f)
    if s: data["sha"] = s
    try:
        r = api(f, "PUT", data); print("OK  ", f, r.status); ok += 1
    except urllib.error.HTTPError as e:
        print("FAIL", f, e.code, e.read().decode()[:200])

print("完成：%d/%d 文件已推送或更新。" % (ok, len(FILES)))
