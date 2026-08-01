import base64, json, subprocess, re, urllib.request, urllib.error

def get_token(repo):
    out = subprocess.check_output(["git","-C",repo,"config","--get","remote.origin.url"]).decode().strip()
    m = re.match(r"https://([^@]+)@github\.com/(.+?)(?:\.git)?$", out)
    if not m: raise SystemExit("cannot parse remote in "+repo)
    return m.group(1)

DOM_REPO  = r"C:/Users/Administrator/WorkBuddy/2026-07-22-08-14-20/hygzz_cn_domestic"
INTL_REPO = r"C:/Users/Administrator/WorkBuddy/2026-07-22-08-14-20/hygzz_cn"
TOKEN = get_token(DOM_REPO)

TARGETS = [
    (DOM_REPO,  "baixi6313/sxj-domestic",     ["events.html","index.html"]),
    (INTL_REPO, "baixi6313/sxj-international", ["events.html","index.html"]),
]

def api(method, url, data=None):
    req = urllib.request.Request(url, method=method, headers={
        "Authorization": f"Bearer {TOKEN}", "User-Agent":"sxj",
        "Accept":"application/vnd.github+json", "Content-Type":"application/json"})
    if data is not None: req.data = json.dumps(data).encode()
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return r.status, json.loads(r.read().decode() or "{}")
    except urllib.error.HTTPError as e:
        b = e.read().decode()
        try: b = json.loads(b)
        except: pass
        return e.code, b

for repo, slug, files in TARGETS:
    print(f"===== {slug} =====")
    for f in files:
        p = f"{repo}/{f}"
        with open(p,"rb") as fh: c = base64.b64encode(fh.read()).decode()
        url = f"https://api.github.com/repos/{slug}/contents/{f}"
        st, resp = api("GET", url)
        sha = resp.get("sha") if st == 200 else None
        msg = ("add " if not sha else "update ")+f+" (SXJ 事件簿 2026-07-29)"
        data = {"message": msg, "content": c}
        if sha: data["sha"] = sha
        st, resp = api("PUT", url, data)
        ok = st in (200, 201)
        print(f"  {'OK ' if ok else 'ERR'} {f} [{st}] {resp.get('content',{}).get('html_url','') if ok else str(resp)[:160]}")
