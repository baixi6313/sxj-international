import json, urllib.request, urllib.error, os

TOKEN = __import__("os").environ.get("GH_PAT", "")
REPO = "baixi6313/sxj-android-app"
APK_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sxj-apk-output-v2", "app-debug.apk")

# 获取 Release v1.0 的 upload_url
req = urllib.request.Request(
    f"https://api.github.com/repos/{REPO}/releases/tags/v1.0",
    headers={
        "Authorization": f"token {TOKEN}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28"
    }
)
with urllib.request.urlopen(req, timeout=30) as r:
    release = json.loads(r.read())

upload_url = release['upload_url'].split('{')[0]
print(f"Release: {release['html_url']}")
print(f"Upload URL: {upload_url}")

# 上传新 APK
print("\n上传新 APK...")
with open(APK_PATH, 'rb') as f:
    apk_data = f.read()

req2 = urllib.request.Request(
    f"{upload_url}?name=app-debug.apk",
    data=apk_data,
    method='POST',
    headers={
        "Authorization": f"token {TOKEN}",
        "Accept": "application/vnd.github+json",
        "Content-Type": "application/vnd.android.package-archive"
    }
)
with urllib.request.urlopen(req2, timeout=60) as r:
    asset = json.loads(r.read())

print(f"APK 上传成功!")
print(f"下载链接: {asset['browser_download_url']}")
print(f"文件大小: {asset['size']} bytes ({asset['size']/1024:.1f} KB)")
print(f"\n=== Release v1.0 已更新为新图标版 APK ===")
print(f"Release 页面: {release['html_url']}")
print(f"APK 直链: {asset['browser_download_url']}")
