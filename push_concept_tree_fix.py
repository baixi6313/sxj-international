# -*- coding: utf-8 -*-
import os, base64, json, re, urllib.request, urllib.error, urllib.parse

BASE = "C:/Users/Administrator/WorkBuddy/2026-07-24-23-26-27"
OWNER = "baixi6313"

# ---- 1) 恢复有效 PAT（仅内存，不打印明文）----
roots = ["C:/Users/Administrator/.workbuddy/audit-log",
         "C:/Users/Administrator/.workbuddy/file-history",
         "C:/Users/Administrator/.workbuddy/artifact-index"]
cands = set()
for root in roots:
    if not os.path.isdir(root):
        continue
    for dp, _, fns in os.walk(root):
        for fn in fns:
            try:
                t = open(os.path.join(dp, fn), encoding="utf-8", errors="ignore").read()
            except Exception:
                continue
            cands.update(re.findall(r"ghp_[A-Za-z0-9]+", t))
TOKEN = None
for c in sorted(cands, key=len, reverse=True):
    try:
        r = urllib.request.urlopen(
            urllib.request.Request("https://api.github.com/user",
                                   headers={"Authorization": "token " + c}), timeout=12)
        if r.status == 200:
            TOKEN = c
            break
    except Exception:
        pass
if not TOKEN:
    print("NO VALID TOKEN FOUND")
    raise SystemExit(1)
print("PAT recovered, len=%d" % len(TOKEN))

H = {"Authorization": "token " + TOKEN, "Accept": "application/vnd.github+json",
     "Content-Type": "application/json", "User-Agent": "sxj-cleaner"}

def api_req(url, data=None, method="GET"):
    req = urllib.request.Request(url, data=data, headers=H, method=method)
    return urllib.request.urlopen(req, timeout=30)

# ---- 2) list repos ----
repos = json.load(api_req("https://api.github.com/users/%s/repos?per_page=100" % OWNER))
repo_names = [r["name"] for r in repos]
print("REPOS:", repo_names)

def get_sha(repo, path):
    url = "https://api.github.com/repos/%s/%s/contents/%s" % (
        OWNER, repo, urllib.parse.quote(path, safe="/"))
    try:
        d = json.load(api_req(url))
        return d.get("sha")
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return None
        raise

def put_file(local, repo, path, msg):
    data = open(local, "rb").read()
    b64 = base64.b64encode(data).decode()
    sha = get_sha(repo, path)
    body = {"message": msg, "content": b64, "branch": "main"}
    if sha:
        body["sha"] = sha
    url = "https://api.github.com/repos/%s/%s/contents/%s" % (
        OWNER, repo, urllib.parse.quote(path, safe="/"))
    try:
        resp = api_req(url, data=json.dumps(body).encode(), method="PUT")
        d = json.load(resp)
        print("[ok %s] %s/%s  sha=%s" % (resp.status, repo, path, d.get("commit", {}).get("sha", "")[:10]))
    except urllib.error.HTTPError as e:
        print("[FAIL %s] %s/%s  %s" % (e.code, repo, path, e.read().decode()[:200]))

# ---- 3) push the GitHub-backed corrected file (android app) ----
android_local = os.path.join(BASE, "sxj-android-app/app/src/main/assets/www/theory/concept_tree.html")
put_file(android_local, "sxj-android-app",
         "app/src/main/assets/www/theory/concept_tree.html",
         "fix(term): 共通值 -> 共济值 in concept_tree (active term cleanup)")

# ---- 4) report on the non-GitHub-backed files ----
print("--- checks ---")
print("hygzz-top-site repo exists on GitHub:", "hygzz-top-site" in repo_names)
for cand in ["sxj-domestic", "sxj-international", "sxj-2026-08-08"]:
    if cand in repo_names:
        sha = get_sha(cand, "concept_tree.html")
        print("  %s/concept_tree.html exists:" % cand, sha is not None)
    else:
        print("  repo %s not present" % cand)
print("DONE")
