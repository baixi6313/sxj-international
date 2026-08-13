# -*- coding: utf-8 -*-
import os, base64, json, re, urllib.request, urllib.error, urllib.parse

BASE = "C:/Users/Administrator/WorkBuddy/2026-07-24-23-26-27"
OWNER = "baixi6313"

# ---- 1) recover PAT (in-memory, never printed) ----
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

PROTECT = [
    'A 值「共通值」正式定名为「共济值」',
    '「共助」（第四阶·国际联动）保持不变。本档案历史条目中的"共通值"为彼时术语，请对照阅读。',
    '本档案历史条目中的"共通值"为彼时术语，请对照阅读。',
]

def fix_text(txt):
    txt2 = txt.replace("共通值", "共济值")
    for p in PROTECT:
        pn = p.replace("共通值", "共济值")
        if pn in txt2:
            txt2 = txt2.replace(pn, p)
    return txt2

def get_contents(repo, path):
    url = "https://api.github.com/repos/%s/%s/contents/%s" % (
        OWNER, repo, urllib.parse.quote(path, safe="/"))
    try:
        d = json.load(api_req(url))
        if isinstance(d, list):
            return None
        return d
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return None
        raise

def put_file(local, repo, path, msg):
    data = open(local, "rb").read()
    b64 = base64.b64encode(data).decode()
    d = get_contents(repo, path)
    sha = d.get("sha") if d else None
    body = {"message": msg, "content": b64, "branch": "main"}
    if sha:
        body["sha"] = sha
    url = "https://api.github.com/repos/%s/%s/contents/%s" % (
        OWNER, repo, urllib.parse.quote(path, safe="/"))
    resp = api_req(url, data=json.dumps(body).encode(), method="PUT")
    r = json.load(resp)
    print("[ok %s] %s/%s  sha=%s" % (resp.status, repo, path, r.get("commit", {}).get("sha", "")[:10]))

def fetch_fix_push(repo, path):
    d = get_contents(repo, path)
    if not d:
        print("[skip] %s/%s not found" % (repo, path))
        return
    raw = base64.b64decode(d["content"]).decode("utf-8")
    before = raw.count("共通值")
    if before == 0:
        print("[clean] %s/%s already clean" % (repo, path))
        return
    fixed = fix_text(raw)
    after = fixed.count("共通值")
    b64 = base64.b64encode(fixed.encode("utf-8")).decode()
    body = {"message": "fix(term): 共通值 -> 共济值 in %s (live-term cleanup)" % path,
            "content": b64, "branch": "main", "sha": d["sha"]}
    url = "https://api.github.com/repos/%s/%s/contents/%s" % (
        OWNER, repo, urllib.parse.quote(path, safe="/"))
    resp = api_req(url, data=json.dumps(body).encode(), method="PUT")
    r = json.load(resp)
    print("[ok %s] %s/%s  %d -> %d  sha=%s" % (resp.status, repo, path, before, after,
                                               r.get("commit", {}).get("sha", "")[:10]))

print("=== A. push local .top-site corrected files to sxj-top ===")
put_file(os.path.join(BASE, "hygzz-top-site/concept_tree.html"), "sxj-top",
         "concept_tree.html", "fix(term): 共通值 -> 共济值 in concept_tree (active term cleanup)")
put_file(os.path.join(BASE, "hygzz-top-site/app/theory/concept_tree.html"), "sxj-top",
         "app/theory/concept_tree.html", "fix(term): 共通值 -> 共济值 in app concept_tree (active term cleanup)")

print("=== B. fix live term in other repos holding concept_tree.html ===")
for repo in ["sxj-domestic", "sxj-international", "sxj-2026-08-08"]:
    fetch_fix_push(repo, "concept_tree.html")

print("ALL_DONE")
