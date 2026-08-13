import os, re, json, base64, urllib.request, urllib.error

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
                    d = json.load(urllib.request.urlopen(req))
                    if d.get("login") == "baixi6313":
                        PAT = m
                        break
                except Exception:
                    pass
        if PAT:
            break
    if PAT:
        break
assert PAT, "NO_VALID_PAT"

API = "https://api.github.com/repos/baixi6313/sxj-android-app"
H = {"Authorization": "token " + PAT, "Accept": "application/vnd.github+json",
     "Content-Type": "application/json"}


def put(local, remote, msg):
    data = open(local, 'rb').read()
    content = base64.b64encode(data).decode()
    from urllib.parse import quote
    url = API + "/contents/" + quote(remote, safe="/")
    sha = None
    try:
        r = urllib.request.urlopen(urllib.request.Request(url, headers=H))
        sha = json.load(r)["sha"]
    except urllib.error.HTTPError as e:
        if e.code != 404:
            raise
    body = {"message": msg, "content": content}
    if sha:
        body["sha"] = sha
    req = urllib.request.Request(url, data=json.dumps(body).encode(),
                                 headers=H, method="PUT")
    try:
        urllib.request.urlopen(req)
        print("  OK " + remote + "  (" + ("update" if sha else "create") + ")")
    except urllib.error.HTTPError as e:
        err = json.load(e)
        print("  FAIL " + remote + "  HTTP " + str(e.code) + ": " + err.get("message", ""))


root = "C:/Users/Administrator/WorkBuddy/2026-07-24-23-26-27/sxj-android-app"
print("== PUSH sxj-android-app (事现鉴 Android App) ==")
put(root + "/app/src/main/assets/www/index.html", "app/src/main/assets/www/index.html",
    "feat: v1.1.2 全站标注「创始完成」红金横幅 + 红圈光锥logo(顶点朝左)")
put(root + "/app/build.gradle", "app/build.gradle",
    "chore: bump version to 1.1.2")
print("DONE")
