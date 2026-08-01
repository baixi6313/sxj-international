import os, base64, json, urllib.request, urllib.error, subprocess

TOKEN = __import__("os").environ.get("GH_PAT", "")
REPO = "baixi6313/sxj-android-app"
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sxj-android-app")

def api(method, path, body=None):
    url = f"https://api.github.com/repos/{REPO}/{path}"
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(url, data=data, method=method,
        headers={"Authorization": f"token {TOKEN}", "Content-Type": "application/json",
                 "Accept": "application/vnd.github+json"})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return json.loads(r.read())
    except urllib.error.HTTPError as e:
        print(f"HTTP {e.code}: {e.read().decode()[:200]}")
        raise

# 获取已提交文件列表（git ls-files 只列37个工程文件）
files = subprocess.check_output(['git', 'ls-files'], cwd=ROOT, text=True).strip().split('\n')
files = [f for f in files if f]
print(f"共 {len(files)} 个文件待上传")

# 1. 创建 blobs
tree_items = []
for rel in files:
    fp = os.path.join(ROOT, rel.replace('/', os.sep))
    with open(fp, 'rb') as f:
        content = base64.b64encode(f.read()).decode()
    r = api('POST', 'git/blobs', {'content': content, 'encoding': 'base64'})
    tree_items.append({'path': rel, 'mode': '100644', 'type': 'blob', 'sha': r['sha']})
    print(f"  blob OK: {rel}")

# 2. 创建 tree
r = api('POST', 'git/trees', {'tree': tree_items})
tree_sha = r['sha']
print(f"tree: {tree_sha[:8]}")

# 3. 创建 commit (initial, 无parent)
r = api('POST', 'git/commits', {'message': '事现鉴 App v1.0', 'tree': tree_sha, 'parents': []})
commit_sha = r['sha']
print(f"commit: {commit_sha[:8]}")

# 4. 创建 ref (main分支)
try:
    r = api('POST', 'git/refs', {'ref': 'refs/heads/main', 'sha': commit_sha})
    print(f"ref main -> {commit_sha[:8]}")
except Exception:
    r = api('PATCH', 'git/refs/heads/main', {'sha': commit_sha})
    print(f"ref main 更新 -> {commit_sha[:8]}")

print("=== 推送完成! ===")
