#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""push_batch.py — 批量推送指定文件到 GitHub 仓库（Contents API，不碰工作区 git）。
用法：GH_PAT=xxx python push_batch.py
仅推送本脚本内显式列出的文件，绝不 git add -A。
"""
import os, sys, urllib.request, json

TOK = os.environ.get("GH_PAT") or __import__("os").environ.get("GH_PAT", "")
WS = r"C:\Users\Administrator\WorkBuddy\2026-07-24-23-26-27"
COM = r"C:\Users\Administrator\WorkBuddy\2026-07-22-08-14-20\hygzz_cn"
APPWWW = os.path.join(WS, "sxj-android-app", "app", "src", "main", "assets", "www")

# (owner, repo, local_path, repo_path)
JOBS = []
# --- .com 国际站（英文架构图）---
for f in ["index.html", "events.html", "knowledge_tree.html", "concept_tree.html",
          "whitepaper.html", "org_en.html", "history_en.html",
          "assets/org/sxj-org-structure.svg", "assets/org/sxj-org-structure-en.svg"]:
    JOBS.append(("baixi6313", "sxj-international", os.path.join(COM, f), f))
# --- App 内嵌网页 ---
for f in ["index.html", "org.html", "history.html",
          "assets/org/sxj-org-structure.svg", "assets/org/sxj-org-structure-en.svg",
          "theory/events.html", "theory/knowledge_tree.html", "theory/concept_tree.html",
          "theory/whitepaper.html", "theory/co_creation.html"]:
    JOBS.append(("baixi6313", "sxj-android-app", os.path.join(APPWWW, f),
                "app/src/main/assets/www/" + f))

def api(method, url, data=None):
    req = urllib.request.Request(url, data=data,
        headers={"Authorization": f"Bearer {TOK}", "Accept": "application/vnd.github+json",
                 "User-Agent": "sxj", "Content-Type": "application/json"})
    req.get_method = lambda: method
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return r.status, json.loads(r.read().decode() or "{}")
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read().decode() or "{}")

def sha_of(owner, repo, path):
    st, j = api("GET", f"https://api.github.com/repos/{owner}/{repo}/contents/{path}")
    return j.get("sha") if st == 200 else None

ok = 0
for owner, repo, local, repo_path in JOBS:
    if not os.path.exists(local):
        print("SKIP missing:", local); continue
    content = open(local, "rb").read()
    import base64
    b64 = base64.b64encode(content).decode()
    sha = sha_of(owner, repo, repo_path)
    body = {"message": f"deploy: {repo_path} (nav+org)", "content": b64}
    if sha:
        body["sha"] = sha
    st, j = api("PUT", f"https://api.github.com/repos/{owner}/{repo}/contents/{repo_path}",
                json.dumps(body).encode())
    print(f"{'OK' if st in (200,201) else 'FAIL'}({st}) {repo}:{repo_path}")
    if st in (200, 201): ok += 1

print(f"\nPushed {ok}/{len(JOBS)} files.")
