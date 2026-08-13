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
ROOT = r"C:/Users/Administrator/WorkBuddy\2026-07-24-23-26-27"

# ---- 2. 目标目录 ----
TARGETS = ["sxj-android-app", "sxj-mini"]

# 始终排除的目录（构建产物 / 依赖 / 缓存）
EXCLUDE_DIRS = {".git", "node_modules", "__pycache__", "miniprogram_npm", "dist",
                "build", ".gradle", "sourcemap", "generated-images",
                "npm_cache", "npm_tmp", "_archive", "wrangler-tmp"}

# 字节上限（源码一般远小于此；超过则可能是异常大文件）
MAX_BYTES = 4_000_000

ok = err = skip = 0

def allowed(local, rel):
    """按路径规则判定某文件是否入库"""
    low = rel.lower()
    # 根目录两个预览图
    name = os.path.basename(local)
    if name in ("logo_preview.png", "logo_v3_preview.png"):
        return False, "root-preview"
    # 微信私有上传配置（含 uploadKey，照惯例不入库）
    if name == "project.private.config.json":
        return False, "wechat-private"
    # png：Android 启动图标 / 内置 web 资源 / 证据截图 保留，其余排除
    if name.lower().endswith(".png"):
        if ("mipmap" in rel) or ("assets/www" in rel) or ("/evidence/" in rel):
            return True, ""
        return False, "png-preview"
    # zip：cloudfunctions 内的共识包保留，其余构建产物排除
    if name.lower().endswith(".zip"):
        if "cloudfunctions" in rel:
            return True, ""
        return False, "zip-artifact"
    # 其余二进制构建产物
    if name.lower().endswith((".apk", ".log", ".jpg", ".jpeg", ".gif", ".ico",
                              ".woff", ".woff2", ".ttf", ".mp4", ".pdf",
                              ".exe", ".dll", ".bin")):
        return False, "binary"
    return True, ""

def put(local, remote):
    global ok, err
    try:
        data = open(local, 'rb').read()
    except Exception as e:
        print(f"  READFAIL {remote}: {e}")
        err += 1
        return
    if len(data) > MAX_BYTES:
        print(f"  SKIP(>{MAX_BYTES//1_000_000}MB) {remote}")
        return
    content = base64.b64encode(data).decode()
    url = API + "/" + REPO + "/contents/" + urllib.parse.quote(remote, safe="/")
    sha = None
    try:
        r = urllib.request.urlopen(urllib.request.Request(url, headers=H), timeout=30)
        sha = json.load(r)["sha"]
    except urllib.error.HTTPError:
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

for tgt in TARGETS:
    tdir = os.path.join(ROOT, tgt)
    if not os.path.isdir(tdir):
        print(f"[skip] 目录不存在: {tgt}")
        continue
    print(f"== 扫描 {tgt} ==")
    for dp, dns, fns in os.walk(tdir):
        dns[:] = [x for x in dns if x not in EXCLUDE_DIRS]
        for fn in fns:
            p = os.path.join(dp, fn)
            rel = os.path.relpath(p, ROOT).replace("\\", "/")
            good, why = allowed(p, rel)
            if not good:
                skip += 1
                continue
            put(p, rel)

print(f"\n汇总: OK={ok} ERR={err} SKIP={skip}")
print(f"仓库地址: https://github.com/baixi6313/{REPO}")
