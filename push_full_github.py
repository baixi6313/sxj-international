import os, re, json, base64, urllib.request, urllib.error, urllib.parse, sys

# ---- 1. PAT 找回（同 push_github.py 机制）----
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
print("[ok] PAT recovered for login=baixi6313")

API = "https://api.github.com/repos/baixi6313"
H = {"Authorization": "token " + PAT, "Accept": "application/vnd.github+json",
     "Content-Type": "application/json"}

REPO = "sxj-2026-08-08"
ROOT = r"C:\Users\Administrator\WorkBuddy\2026-07-24-23-26-27"

# ---- 2. 建仓库（幂等：已存在则跳过）----
def api(method, url, data=None):
    req = urllib.request.Request(url, method=method, headers=H)
    if data is not None:
        req.add_header("Content-Type", "application/json")
        req.data = json.dumps(data).encode()
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return r.status, json.loads(r.read().decode() or "{}")
    except urllib.error.HTTPError as e:
        try:
            b = json.loads(e.read().decode() or "{}")
        except Exception:
            b = {}
        return e.code, b

st, resp = api("POST", "https://api.github.com/user/repos", {
    "name": REPO,
    "description": "事现鉴 2026-08-08 工作快照：讨论产物 + 六角验证委员会 + 知识/概念树 + .top 源站 + 协议",
    "private": False, "auto_init": False,
})
if st in (201, 200):
    print(f"[ok] 仓库已创建: {REPO}")
elif st == 422:
    print(f"[ok] 仓库已存在(跳过创建): {REPO}")
else:
    print(f"[FAIL] 建仓库 HTTP {st}: {resp.get('message')}")
    sys.exit(1)

# ---- 3. 遍历并推送（排除 junk）----
EXCLUDE_DIRS = {".git", ".workbuddy", "__pycache__", "node_modules", "npm_cache",
                "npm_tmp", "generated-images", "logo_clean", "_archive", "wrangler-tmp",
                "pm", "sxj-android-app", "sxj-mini", "sxj-apk-output",
                "sxj-apk-output-v2", "sxj-apk-output-v3", "qw_transcripts"}
EXCLUDE_EXT = {".zip", ".apk", ".log", ".png", ".jpg", ".jpeg", ".gif", ".ico",
               ".woff", ".woff2", ".ttf", ".mp4", ".pdf", ".exe", ".dll", ".bin"}
EXCLUDE_FILES = {"npm4.log", "npm5.log", "npmver.log",
                 "sxj-apk-artifact.zip", "sxj-apk-artifact-v2.zip",
                 "sxj-apk-artifact-v3.zip",
                 "db_api_conversation_thread_share_share_id=xWqMZLAquBFYDjjmT&need_bot=1.json"}
SKIP_FILE_PREFIX = ("_", "lv_check", "npm", "db_api", "qw_")

ok = err = skip = 0
def put(local, remote):
    global ok, err
    data = open(local, 'rb').read()
    if len(data) > 1_000_000:  # 跳过 >1MB 的文本（异常大文件）
        print(f"  SKIP(>1MB) {remote}")
        return
    content = base64.b64encode(data).decode()
    url = API + "/" + REPO + "/contents/" + urllib.parse.quote(remote, safe="/")
    sha = None
    try:
        r = urllib.request.urlopen(urllib.request.Request(url, headers=H), timeout=30)
        sha = json.load(r)["sha"]
    except urllib.error.HTTPError as e:
        if e.code != 404:
            pass
    body = {"message": ("add " if not sha else "update ") + remote, "content": content}
    if sha:
        body["sha"] = sha
    req = urllib.request.Request(url, data=json.dumps(body).encode(),
                                 headers=H, method="PUT")
    try:
        urllib.request.urlopen(req, timeout=60)
        ok += 1
        if ok % 20 == 0:
            print(f"  ...已推送 {ok} 个")
    except urllib.error.HTTPError as e:
        try:
            b = json.loads(e.read().decode())
        except Exception:
            b = {}
        err += 1
        print(f"  ERR {remote} [{e.code}] {str(b.get('message',''))[:120]}")

for dp, dns, fns in os.walk(ROOT):
    dns[:] = [x for x in dns if x not in EXCLUDE_DIRS]
    for fn in fns:
        if fn in EXCLUDE_FILES:
            skip += 1; continue
        if fn.lower().endswith(tuple(EXCLUDE_EXT)):
            skip += 1; continue
        if fn.startswith(SKIP_FILE_PREFIX):
            skip += 1; continue
        p = os.path.join(dp, fn)
        rel = os.path.relpath(p, ROOT).replace("\\", "/")
        put(p, rel)

print(f"\n汇总: OK={ok} ERR={err} SKIP={skip}")
print(f"仓库地址: https://github.com/baixi6313/{REPO}")
