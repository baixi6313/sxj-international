import os, base64, json, urllib.request, urllib.error, subprocess, time

TOKEN = __import__("os").environ.get("GH_PAT", "")
REPO = "baixi6313/sxj-android-app"
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sxj-android-app")

def api(method, path, body=None):
    url = f"https://api.github.com/repos/{REPO}/contents/{path}"
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(url, data=data, method=method,
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

# 获取本地最近一次提交中修改的文件（相对于 GitHub 的 main）
# 简化处理：直接读取 git status 中已修改的文件
files = subprocess.check_output(['git', 'diff', '--name-only', 'HEAD~1'], cwd=ROOT, text=True).strip().split('\n')
files = [f for f in files if f]
print(f"共 {len(files)} 个文件待更新到 GitHub\n")

ok = 0
fail = 0
for i, rel in enumerate(files, 1):
    fp = os.path.join(ROOT, rel.replace('/', os.sep))

    # 1. 获取 GitHub 上当前文件的 SHA
    try:
        r = api('GET', f"{rel}?ref=main")
        current_sha = r['sha']
    except Exception as e:
        print(f"  [{i:2d}/{len(files)}] 获取SHA失败 {rel}: {e}")
        fail += 1
        continue

    # 2. 读取新内容
    with open(fp, 'rb') as f:
        content = base64.b64encode(f.read()).decode()

    # 3. PUT 更新
    body = {
        "message": f"更新应用图标为新 logo ({rel})",
        "content": content,
        "sha": current_sha,
        "branch": "main"
    }

    for attempt in range(3):
        try:
            r = api('PUT', rel, body)
            ok += 1
            new_sha = r.get('commit', {}).get('sha', '????')[:8]
            print(f"  [{i:2d}/{len(files)}] OK  {rel}  (commit {new_sha})")
            break
        except Exception as e:
            if attempt < 2:
                print(f"  [{i:2d}/{len(files)}] 重试 {attempt+1}... {rel}")
                time.sleep(3)
            else:
                fail += 1
                print(f"  [{i:2d}/{len(files)}] FAIL {rel}: {e}")

    time.sleep(0.5)

print(f"\n=== 更新完成: 成功 {ok}/{len(files)}, 失败 {fail} ===")
