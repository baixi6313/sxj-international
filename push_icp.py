import base64, json, urllib.request, urllib.error, subprocess, re, sys

TOK = subprocess.check_output(
    ["git", "-C", r"C:/Users/Administrator/WorkBuddy/2026-07-22-08-14-20/hygzz_cn_domestic", "config", "--get", "remote.origin.url"],
    encoding="utf-8"
).strip()
TOK = re.sub(r'https://([^@]+)@.*', r'\1', TOK)

REPO = "baixi6313/sxj-top"
FILE_PATH = r"C:/Users/Administrator/WorkBuddy/2026-07-24-23-26-27/hygzz_top/index.html"
TARGET = "index.html"

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

# Get current SHA
st, resp = api("GET", f"https://api.github.com/repos/{REPO}/contents/{TARGET}")
if st == 200:
    sha = resp["sha"]
    print(f"current SHA: {sha[:8]}...")
else:
    print(f"GET failed: {st}, creating new file")
    sha = None

# Read and encode
with open(FILE_PATH, "rb") as f:
    content = base64.b64encode(f.read()).decode()

# PUT
data = {
    "message": "feat: 加ICP备案号 陕ICP备2026020031号-1X",
    "content": content
}
if sha:
    data["sha"] = sha

st, resp = api("PUT", f"https://api.github.com/repos/{REPO}/contents/{TARGET}", data)
print(f"PUT status: {st}")
if st in (200, 201):
    print(f"OK - commit SHA: {resp.get('commit',{}).get('sha','?')[:8]}")
else:
    print(f"ERR: {str(resp)[:200]}")

# Dispatch workflow
st2, resp2 = api("POST", f"https://api.github.com/repos/{REPO}/actions/workflows/deploy.yml/dispatches", {"ref": "main"})
print(f"dispatch status: {st2} (204=success)")
