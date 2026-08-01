import urllib.request, urllib.error, base64, json, os

TOKEN = __import__("os").environ.get("GH_PAT", "")
REPO = "baixi6313/sxj-android-app"
BASE = r"C:\Users\Administrator\WorkBuddy\2026-07-24-23-26-27\sxj-android-app"

# (local_rel, repo_path)
FILES = [
    (r"app\src\main\assets\www\js\app.js", "app/src/main/assets/www/js/app.js"),
    (r"app\build.gradle", "app/build.gradle"),
    (r"version.json", "version.json"),
    (r".github\workflows\build.yml", ".github/workflows/build.yml"),
]

def api(method, path, data=None):
    url = f"https://api.github.com/repos/{REPO}/{path}"
    req = urllib.request.Request(url, method=method,
        headers={"Authorization": f"Bearer {TOKEN}",
                 "Accept": "application/vnd.github+json",
                 "User-Agent": "push-script",
                 "Content-Type": "application/json"})
    if data is not None:
        req.data = json.dumps(data).encode("utf-8")
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return r.status, json.loads(r.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", "ignore")
        return e.code, body

for local_rel, repo_path in FILES:
    local = os.path.join(BASE, local_rel)
    content = open(local, "rb").read()
    b64 = base64.b64encode(content).decode("ascii")
    # get current sha
    st, resp = api("GET", f"contents/{repo_path}")
    if st != 200:
        print(f"[SKIP] {repo_path}: GET failed {st} {str(resp)[:120]}")
        continue
    sha = resp["sha"]
    msg = "chore: remove BETA label, bump 1.0.1, auto-publish APK to release"
    st2, resp2 = api("PUT", f"contents/{repo_path}",
                     {"message": msg, "content": b64, "sha": sha})
    if st2 in (200, 201):
        print(f"[OK]   {repo_path} -> committed")
    else:
        print(f"[FAIL] {repo_path}: PUT {st2} {str(resp2)[:200]}")
print("DONE")
