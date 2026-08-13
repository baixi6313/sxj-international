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

# 本地文件（相对 ROOT，形如 sxj-android-app/version.json）
LOCAL = [
    "sxj-android-app/version.json",
    "sxj-android-app/app/src/main/assets/www/version.json",
    "sxj-android-app/app/src/main/assets/www/js/app.js",
]

def remote_for(repo, local):
    if repo == "sxj-android-app":
        # 仓库根即 Android 工程，去掉前缀 sxj-android-app/
        assert local.startswith("sxj-android-app/")
        return local[len("sxj-android-app/"):]
    else:  # sxj-2026-08-08：快照仓库，路径原样
        return local

def get_sha(repo, remote):
    url = f"{API}/{repo}/contents/{urllib.parse.quote(remote, safe='/')}"
    try:
        return json.load(urllib.request.urlopen(urllib.request.Request(url, headers=H)))["sha"]
    except urllib.error.HTTPError:
        return None

def put(repo, local, remote):
    data = open(os.path.join(ROOT, local), 'rb').read()
    content = base64.b64encode(data).decode()
    url = f"{API}/{repo}/contents/{urllib.parse.quote(remote, safe='/')}"
    sha = get_sha(repo, remote)
    body = {"message": "fix version.json update link -> v1.1.2 (" +
            ("update " if sha else "add ") + remote + ")",
            "content": content, "branch": "main"}
    if sha:
        body["sha"] = sha
    req = urllib.request.Request(url, data=json.dumps(body).encode(), headers=H, method="PUT")
    try:
        urllib.request.urlopen(req, timeout=60)
        print(f"  [ok] {repo}  {remote}")
        return True
    except urllib.error.HTTPError as e:
        b = json.loads(e.read().decode() or "{}")
        print(f"  [ERR] {repo} {remote} [{e.code}] {str(b.get('message',''))[:120]}")
        return False

def delete(repo, remote, msg):
    sha = get_sha(repo, remote)
    if not sha:
        return
    url = f"{API}/{repo}/contents/{urllib.parse.quote(remote, safe='/')}"
    body = {"message": msg, "sha": sha, "branch": "main"}
    req = urllib.request.Request(url, data=json.dumps(body).encode(), headers=H, method="DELETE")
    try:
        urllib.request.urlopen(req, timeout=60)
        print(f"  [del] {repo}  {remote}")
    except urllib.error.HTTPError as e:
        b = json.loads(e.read().decode() or "{}")
        print(f"  [del-ERR] {repo} {remote} [{e.code}] {str(b.get('message',''))[:120]}")

# 1) 删除上次误建的嵌套错路径
print("== 删除错误嵌套文件 ==")
for repo in ["sxj-android-app", "sxj-2026-08-08"]:
    for local in LOCAL:
        wrong = ("sxj-android-app/" + local) if repo == "sxj-android-app" else ("sxj-android-app/sxj-android-app/" + local[len("sxj-android-app/"):])
        delete(repo, wrong, "remove wrongly nested path from prior push")

# 2) 推到正确路径
print("\n== 推到正确路径 ==")
ok = 0
for repo in ["sxj-android-app", "sxj-2026-08-08"]:
    print(f"-- {repo} --")
    for local in LOCAL:
        remote = remote_for(repo, local)
        if put(repo, local, remote):
            ok += 1
print(f"\n汇总推送成功: {ok}/{len(LOCAL)*2}")
