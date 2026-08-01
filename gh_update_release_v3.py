import json, urllib.request, os

TOKEN = __import__("os").environ.get("GH_PAT", "")
REPO = "baixi6313/sxj-android-app"
APK_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sxj-apk-output-v3", "app-debug.apk")

def api(method, url, body=None, binary=False, extra_headers=None):
    data = None
    if body is not None and not binary:
        data = json.dumps(body).encode()
    elif body is not None and binary:
        data = body
    headers = {
        "Authorization": f"token {TOKEN}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28"
    }
    if extra_headers:
        headers.update(extra_headers)
    req = urllib.request.Request(url, data=data, method=method, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return r.status, r.read()
    except urllib.error.HTTPError as e:
        return e.code, e.read()

# 1. 获取 Release
status, body = api('GET', f"https://api.github.com/repos/{REPO}/releases/tags/v1.0")
release = json.loads(body)
print(f"Release: {release['html_url']}")

# 2. 删除旧 asset
for asset in release.get('assets', []):
    if asset['name'] == 'app-debug.apk':
        status, _ = api('DELETE', f"https://api.github.com/repos/{REPO}/releases/assets/{asset['id']}")
        print(f"删除旧 asset: {status}")

# 3. 上传新 APK
upload_url = release['upload_url'].split('{')[0]
with open(APK_PATH, 'rb') as f:
    apk_data = f.read()
status, body = api('POST', f"{upload_url}?name=app-debug.apk", body=apk_data, binary=True, extra_headers={"Content-Type": "application/vnd.android.package-archive"})
asset = json.loads(body)
print(f"上传新 APK: {status}")
print(f"下载链接: {asset['browser_download_url']}")
print(f"文件大小: {asset['size']} bytes ({asset['size']/1024:.1f} KB)")
print(f"\n=== Release v1.0 已更新 ===")
print(f"Release 页面: {release['html_url']}")
print(f"APK 直链: {asset['browser_download_url']}")
