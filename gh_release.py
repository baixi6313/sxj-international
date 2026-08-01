import json, urllib.request, urllib.error, os

TOKEN = __import__("os").environ.get("GH_PAT", "")
REPO = "baixi6313/sxj-android-app"
APK_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sxj-apk-output", "app-debug.apk")

headers = {
    "Authorization": f"token {TOKEN}",
    "Accept": "application/vnd.github+json",
    "X-GitHub-Api-Version": "2022-11-28"
}

# 1. 创建 Release
print("正在创建 Release...")
body = {
    "tag_name": "v1.0",
    "target_commitish": "main",
    "name": "事现鉴 App v1.0 - 公共事实验证",
    "body": "事现鉴 (SXJ) Android App v1.0\n\n功能:\n- 三值体系(共济值/贡献值/负贡献值)\n- 事现簿事件验证\n- SHA-256 哈希链\n- 五大理论页面\n\n安装方法:\n1. 下载 app-debug.apk\n2. 手机设置 -> 安全 -> 允许未知来源安装\n3. 点击 APK 文件安装\n\n注意: 此为 debug 版本,用于测试体验。上架应用商店需要 release 签名版。",
    "draft": False,
    "prerelease": False
}

req = urllib.request.Request(
    f"https://api.github.com/repos/{REPO}/releases",
    data=json.dumps(body).encode(),
    method='POST',
    headers={**headers, "Content-Type": "application/json"}
)

with urllib.request.urlopen(req, timeout=30) as r:
    release = json.loads(r.read())

release_id = release['id']
upload_url = release['upload_url'].split('{')[0]
html_url = release['html_url']
print(f"Release 创建成功! ID: {release_id}")
print(f"Release 页面: {html_url}")

# 2. 上传 APK 到 Release
print("\n正在上传 APK...")
with open(APK_PATH, 'rb') as f:
    apk_data = f.read()

upload_headers = {
    "Authorization": f"token {TOKEN}",
    "Accept": "application/vnd.github+json",
    "Content-Type": "application/vnd.android.package-archive"
}

req2 = urllib.request.Request(
    f"{upload_url}?name=app-debug.apk",
    data=apk_data,
    method='POST',
    headers=upload_headers
)

with urllib.request.urlopen(req2, timeout=60) as r:
    asset = json.loads(r.read())

print(f"APK 上传成功!")
print(f"下载链接: {asset['browser_download_url']}")
print(f"文件大小: {asset['size']} bytes ({asset['size']/1024:.1f} KB)")
print(f"\n=== 完成! ===")
print(f"Release 页面: {html_url}")
print(f"APK 直接下载: {asset['browser_download_url']}")
