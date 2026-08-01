import base64, json, urllib.request, urllib.error, subprocess, re

TOK = subprocess.check_output(
    ["git", "-C", r"C:/Users/Administrator/WorkBuddy/2026-07-22-08-14-20/hygzz_cn_domestic", "config", "--get", "remote.origin.url"],
    encoding="utf-8"
).strip()
TOK = re.sub(r'https://([^@]+)@.*', r'\1', TOK)

def api(method, url, data=None):
    req = urllib.request.Request(url, method=method, headers={
        "Authorization": f"Bearer {TOK}",
        "User-Agent": "sxj",
        "Accept": "application/vnd.github+json"
    })
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

repos = [
    ("baixi6313/sxj-domestic", r"C:/Users/Administrator/WorkBuddy/2026-07-22-08-14-20/hygzz_cn_domestic/index.html"),
    ("baixi6313/sxj-international", r"C:/Users/Administrator/WorkBuddy/2026-07-22-08-14-20/hygzz_cn/index.html"),
]

for repo, fpath in repos:
    target = "index.html"
    print(f"\n===== {repo}: {target} =====")
    
    # Get SHA
    st, resp = api("GET", f"https://api.github.com/repos/{repo}/contents/{target}")
    sha = resp.get("sha") if st == 200 else None
    print(f"  current SHA: {sha[:8] if sha else 'NEW'}...")
    
    # Encode
    with open(fpath, "rb") as f:
        content = base64.b64encode(f.read()).decode()
    
    # PUT
    data = {"message": "feat: 加ICP备案号 陕ICP备2026020031号-1X", "content": content}
    if sha: data["sha"] = sha
    
    st, resp = api("PUT", f"https://api.github.com/repos/{repo}/contents/{target}", data)
    print(f"  PUT: {st} {'OK' if st in (200,201) else 'ERR'}")
    if st not in (200,201):
        print(f"  err: {str(resp)[:200]}")

# Dispatch workflows for both repos
for repo in ["baixi6313/sxj-domestic", "baixi6313/sxj-international"]:
    st, resp = api("POST", f"https://api.github.com/repos/{repo}/actions/workflows/deploy.yml/dispatches", {"ref": "main"})
    print(f"  dispatch {repo}: {st} {'OK' if st == 204 else 'ERR'}")
