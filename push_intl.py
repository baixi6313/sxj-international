import base64, json, subprocess, re, urllib.request, urllib.error, sys
DOM_TOKEN = sys.argv[1]
REPO = r"C:/Users/Administrator/WorkBuddy/2026-07-22-08-14-20/hygzz_cn"
SLUG = "baixi6313/sxj-international"
FILES = ["knowledge_tree.html","whitepaper.html","concept_tree.html","knowledge_tree_v4.html","critical_synthesis_report.html","qualitative_analysis.html","index.html"]
def api(method, url, data=None):
    req = urllib.request.Request(url, method=method, headers={"Authorization": f"Bearer {DOM_TOKEN}", "User-Agent":"sxj","Accept":"application/vnd.github+json"})
    if data is not None:
        req.add_header("Content-Type","application/json"); req.data=json.dumps(data).encode()
    try:
        with urllib.request.urlopen(req, timeout=30) as r: return r.status, json.loads(r.read().decode() or "{}")
    except urllib.error.HTTPError as e:
        b=e.read().decode()
        try: b=json.loads(b)
        except: pass
        return e.code, b
print(f"===== REPO {SLUG} (using domestic PAT) =====")
for f in FILES:
    p=f"{REPO}/{f}"
    try:
        with open(p,"rb") as fh: c=base64.b64encode(fh.read()).decode()
    except FileNotFoundError:
        print(f"  SKIP {f}"); continue
    url=f"https://api.github.com/repos/{SLUG}/contents/{f}"
    st,resp=api("GET",url); sha=resp.get("sha") if st==200 else None
    msg=("add " if not sha else "update ")+f+" (SXJ 2026-07-28)"
    data={"message":msg,"content":c}
    if sha: data["sha"]=sha
    st,resp=api("PUT",url,data)
    print(f"  {'OK ' if st in (200,201) else 'ERR'} {f} [{st}] {resp.get('content',{}).get('html_url','') if st in (200,201) else str(resp)[:120]}")
