import os, base64, json, urllib.request, urllib.error, subprocess, time

TOKEN = __import__("os").environ.get("GH_PAT", "")
REPO = "baixi6313/sxj-android-app"
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sxj-android-app")

def api_put(path, body):
    """PUT to GitHub Contents API"""
    url = f"https://api.github.com/repos/{REPO}/contents/{path}"
    data = json.dumps(body).encode()
    req = urllib.request.Request(url, data=data, method='PUT',
        headers={
            "Authorization": f"token {TOKEN}",
            "Content-Type": "application/json",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28"
        })
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return json.loads(r.read())
    except urllib.error.HTTPError as e:
        err_body = e.read().decode()[:500]
        print(f"  HTTP {e.code}: {err_body}")
        raise

# 获取37个已提交文件
files = subprocess.check_output(['git', 'ls-files'], cwd=ROOT, text=True).strip().split('\n')
files = [f for f in files if f]
print(f"共 {len(files)} 个文件待上传 (Contents API)\n")

ok = 0
fail = 0
for i, rel in enumerate(files, 1):
    fp = os.path.join(ROOT, rel.replace('/', os.sep))
    with open(fp, 'rb') as f:
        content = base64.b64encode(f.read()).decode()

    commit_msg = f"事现鉴 App v1.0 - 初始上传 ({i}/{len(files)})"
    body = {
        "message": commit_msg,
        "content": content,
        "branch": "main"
    }

    # 重试机制（网络偶发超时）
    for attempt in range(3):
        try:
            r = api_put(rel, body)
            ok += 1
            sha = r.get('commit', {}).get('sha', '????')[:8]
            print(f"  [{i:2d}/{len(files)}] OK  {rel}  (commit {sha})")
            break
        except Exception as e:
            if attempt < 2:
                print(f"  [{i:2d}/{len(files)}] 重试 {attempt+1}... {rel}")
                time.sleep(3)
            else:
                fail += 1
                print(f"  [{i:2d}/{len(files)}] FAIL {rel}: {e}")

    # 小延迟，避免触发API限流
    time.sleep(0.5)

print(f"\n=== 上传完成: 成功 {ok}/{len(files)}, 失败 {fail} ===")
