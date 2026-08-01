import base64, json, subprocess, sys, urllib.request, urllib.error

REPOS = [
    r"C:/Users/Administrator/WorkBuddy/2026-07-22-08-14-20/hygzz_cn",
]
FILES = [
    "knowledge_tree.html", "whitepaper.html", "concept_tree.html",
    "knowledge_tree_v4.html", "critical_synthesis_report.html",
    "qualitative_analysis.html", "index.html",
]

def get_remote(repo):
    out = subprocess.check_output(["git", "-C", repo, "config", "--get", "remote.origin.url"]).decode().strip()
    # https://USER:TOKEN@github.com/OWNER/NAME.git
    import re
    # Accept both https://TOKEN@github.com/... and https://USER:TOKEN@github.com/...
    m = re.match(r"https://(?:([^:@/]+):)?([^@]+)@github\.com/(.+?)(?:\.git)?$", out)
    if not m:
        raise SystemExit(f"cannot parse remote in {repo}: {out}")
    token = m.group(2)  # the part right before @ (after optional user:)
    slug = m.group(3)
    return "x-access-token", token, slug

def api(token, method, url, data=None):
    req = urllib.request.Request(url, method=method,
          headers={"Authorization": f"Bearer {token}", "User-Agent": "sxj-deploy",
                   "Accept": "application/vnd.github+json"})
    if data is not None:
        req.add_header("Content-Type", "application/json")
        req.data = json.dumps(data).encode()
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return r.status, json.loads(r.read().decode() or "{}")
    except urllib.error.HTTPError as e:
        body = e.read().decode()
        try: body = json.loads(body)
        except: pass
        return e.code, body

for repo in REPOS:
    user, token, slug = get_remote(repo)
    print(f"\n===== REPO {slug} =====")
    for f in FILES:
        path = f"{repo}/{f}"
        try:
            with open(path, "rb") as fh:
                content = base64.b64encode(fh.read()).decode()
        except FileNotFoundError:
            print(f"  SKIP {f} (not found)"); continue
        url = f"https://api.github.com/repos/{slug}/contents/{f}"
        status, resp = api(token, "GET", url)
        sha = resp.get("sha") if status == 200 else None
        msg = f"add {f} (SXJ 2026-07-28 手绘知识树+白皮书v2)"
        if sha:
            msg = f"update {f} (SXJ 2026-07-28 nav+新页)"
            status, resp = api(token, "PUT", url, {"message": msg, "content": content, "sha": sha})
        else:
            status, resp = api(token, "PUT", url, {"message": msg, "content": content})
        if status in (200, 201):
            print(f"  OK  {f}  -> {resp.get('content',{}).get('html_url','')}")
        else:
            print(f"  ERR {f}  [{status}] {str(resp)[:160]}")
