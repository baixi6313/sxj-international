import json, urllib.request, urllib.error, os

TOKEN = __import__("os").environ.get("GH_PAT", "")
REPO = "baixi6313/sxj-android-app"
APK_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sxj-apk-output-v2", "app-debug.apk")

def api_call(method, url, body=None, extra_headers=None, binary=False):
    headers = {
        "Authorization": f"token {TOKEN}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28"
    }
    if extra_headers:
        headers.update(extra_headers)

    data = None
    if body is not None and not binary:
        data = json.dumps(body).encode()
    elif body is not None and binary:
        data = body

    req = urllib.request.Request(url, data=data, method=method, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            resp = r.read()
            return json.loads(resp) if not binary else resp
    except urllib.error.HTTPError as e:
        err_body = e.read().decode()[:500]
        print(f"HTTP {e.code}: {err_body}")
        raise

# 1. 获取 Release v1.0
print("查找 Release v1.0...")
releases = api_call('GET', f"https://api.github.com/repos/{REPO}/releases")
release = next((r for r in releases if r['tag_name'] == 'v1.0'), None)
if not release:
    print("未找到 v1.0 Release")
    exit(1)

release_id = release['id']
print(f"Release ID: {release_id}")

# 2. 删除旧的 app-debug.apk asset
for asset in release.get('assets', []):
    if asset['name'] == 'app-debug.apk':
        print(f"删除旧 asset: {asset['name']} (id: {asset['id']})")
        api_call('DELETE', f"https://api.github.com/repos/{REPO}/releases/assets/{asset['id']}")

# 3. 上传新的 APK
print("\n上传新 APK...")
with open(APK_PATH, 'rb') as f:
    apk_data = f.read()

upload_url = release['upload_url'].split('{')[0]
asset = api_call(
    'POST',
    f"{upload_url}?name=app-debug.apk",
    body=apk_data,
    extra_headers={"Content-Type": "application/vnd.android.package-archive"},
    binary=True
)

print(f"APK 上传成功!")
print(f"下载链接: {asset['browser_download_url']}")
print(f"文件大小: {asset['size']} bytes ({asset['size']/1024:.1f} KB)")
print(f"\n=== Release 已更新 ===")
print(f"Release 页面: {release['html_url']}")
print(f"APK 直链: {asset['browser_download_url']}")
