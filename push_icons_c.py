# -*- coding: utf-8 -*-
"""把 logo_clean/C_瓦当 的 10 个 mipmap 图标推送到 GitHub 仓库(Contents API)，触发 Actions 重编译。"""
import os, sys, base64, json, urllib.request, urllib.error

TOKEN = __import__("os").environ.get("GH_PAT", "")
REPO = "baixi6313/sxj-android-app"
SRC = r"C:\Users\Administrator\WorkBuddy\2026-07-24-23-26-27\logo_clean\C_瓦当"
DENS = ["mdpi", "hdpi", "xhdpi", "xxhdpi", "xxxhdpi"]
API = "https://api.github.com/repos/%s/contents" % REPO
AUTH = {"Authorization": "token " + TOKEN, "Content-Type": "application/json"}

def api(method, path, data=None):
    url = API + path
    req = urllib.request.Request(url, data=(json.dumps(data).encode() if data else None),
                                 headers=AUTH, method=method)
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return r.status, json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read().decode("utf-8", "replace"))

def update(local, repo_path):
    with open(local, "rb") as f:
        content = base64.b64encode(f.read()).decode()
    st, meta = api("GET", "/" + repo_path)
    sha = meta.get("sha") if st == 200 else None
    if not sha:
        print("  GET失败(%s) %s -> %s" % (st, repo_path, meta.get("message")))
        return False
    st2, _ = api("PUT", "/" + repo_path,
                 {"message": "replace launcher icon with clean 瓦当 logo (C)",
                  "sha": sha, "content": content})
    print("  PUT %s -> %s" % (repo_path, st2))
    return st2 == 200

ok = 0; total = 0
for dn in DENS:
    d = os.path.join(SRC, "mipmap-" + dn)
    for name in ("ic_launcher.png", "ic_launcher_round.png"):
        lp = os.path.join(d, name)
        rp = "app/src/main/res/mipmap-%s/%s" % (dn, name)
        total += 1
        if update(lp, rp):
            ok += 1
print("推送完成: %d/%d" % (ok, total))
