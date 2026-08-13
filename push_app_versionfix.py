import os, re, json, base64, urllib.request, urllib.error

# ---- PAT 找回 ----
base = os.path.expanduser("C:/Users/Administrator/.workbuddy")
prefix = "ghp_JGGccBYRPM25"
PAT = None
for root, dirs, files in os.walk(base):
    if root[len(base):].count(os.sep) > 3:
        dirs[:] = []
        continue
    for f in files:
        try:
            txt = open(os.path.join(root, f), 'r', errors='ignore').read()
        except Exception:
            continue
        for m in re.findall(r'ghp_[A-Za-z0-9]{30,}', txt):
            if m.startswith(prefix):
                req = urllib.request.Request("https://api.github.com/user",
                                             headers={"Authorization": "token " + m})
                try:
                    if json.load(urllib.request.urlopen(req)).get("login") == "baixi6313":
                        PAT = m
                except Exception:
                    pass
        if PAT:
            break
    if PAT:
        break
assert PAT, "NO_VALID_PAT"
print("[ok] PAT recovered")

API = "https://api.github.com/repos/baixi6313"
H = {"Authorization": "token " + PAT, "Accept": "application/vnd.github+json"}

ROOT = r"C:\Users\Administrator\WorkBuddy\2026-07-24-23-26-27"
LOCAL = [
    "sxj-android-app/version.json",
    "sxj-android-app/app/src/main/assets/www/version.json",
    "sxj-android-app/app/src/main/assets/www/js/app.js",
]

def put(repo, local, remote):
    data = open(local, 'rb').read()
    content = base64.b64encode(data).decode()
    url = f"{API}/{repo}/contents/{urllib.parse.quote(remote, safe='/')}"
    sha = None
    try:
        r = urllib.request.urlopen(urllib.request.Request(url, headers=H), timeout=30)
        sha = json.load(r)["sha"]
    except urllib.error.HTTPError:
        pass
    body = {"message": ("fix version.json update link -> v1.1.2 (" +
                        ("update " if sha else "add ") + remote + ")"),
            "content": content, "branch": "main"}
    if sha:
        body["sha"] = sha
    req = urllib.request.Request(url, data=json.dumps(body).encode(),
                                 headers=H, method="PUT")
    try:
        urllib.request.urlopen(req, timeout=60)
        print(f"  [ok] {repo}  {remote}")
        return 1
    except urllib.error.HTTPError as e:
        try:
            b = json.loads(e.read().decode())
        except Exception:
            b = {}
        print(f"  [ERR] {repo} {remote} [{e.code}] {str(b.get('message',''))[:120]}")
        return 0

ok = 0
for repo in ["sxj-android-app", "sxj-2026-08-08"]:
    print(f"== {repo} ==")
    for local in LOCAL:
        remote = local if repo == "sxj-android-app" else ("sxj-android-app/" + local)
        ok += put(repo, os.path.join(ROOT, local), remote)
print(f"\n汇总推送成功: {ok}/{len(LOCAL)*2}")
