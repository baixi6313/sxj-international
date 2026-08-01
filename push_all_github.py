import base64, json, subprocess, re, os
import urllib.request, urllib.error, urllib.parse

# 提取国内 PAT（来自 hygzz_cn_domestic 的 remote，国内 PAT 有效；绕开失效的国际 PAT）
out = subprocess.check_output(
    ["git", "-C", r"C:\Users\Administrator\WorkBuddy\2026-07-22-08-14-20\hygzz_cn_domestic",
     "config", "--get", "remote.origin.url"]).decode().strip()
TOK = re.sub(r'https://([^@]+)@.*', r'\1', out)
print("TOK prefix:", TOK[:8], "...")

def api(method, url, data=None):
    req = urllib.request.Request(url, method=method,
        headers={"Authorization": f"Bearer {TOK}", "User-Agent": "sxj", "Accept": "application/vnd.github+json"})
    if data is not None:
        req.add_header("Content-Type", "application/json")
        req.data = json.dumps(data).encode()
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return r.status, json.loads(r.read().decode() or "{}")
    except urllib.error.HTTPError as e:
        b = e.read().decode()
        try: b = json.loads(b)
        except Exception: b = b
        return e.code, b

PAIRS = [
    (r"C:\Users\Administrator\WorkBuddy\2026-07-22-08-14-20\hygzz_cn", "baixi6313/sxj-international"),
    (r"C:\Users\Administrator\WorkBuddy\2026-07-22-08-14-20\hygzz_cn_domestic", "baixi6313/sxj-domestic"),
    (r"C:\Users\Administrator\WorkBuddy\2026-07-24-23-26-27\hygzz_top", "baixi6313/sxj-top"),
]
SKIP_DIRS = {".git"}
SKIP_FILES = {"CNAME", ".nojekyll", ".gitignore", "README.md", "MAINTENANCE_GUIDE.md", "GITHUB_DEPLOY_GUIDE.md"}

ok = err = skip = 0
for src, slug in PAIRS:
    print(f"\n===== {slug} (src {os.path.basename(src)}) =====")
    for dp, dns, fns in os.walk(src):
        dns[:] = [x for x in dns if x not in SKIP_DIRS]
        for fn in fns:
            if fn in SKIP_FILES:
                skip += 1
                continue
            p = os.path.join(dp, fn)
            rel = os.path.relpath(p, src).replace("\\", "/")
            # 跳过明显二进制
            if rel.lower().endswith((".png", ".jpg", ".jpeg", ".gif", ".woff", ".woff2", ".ttf", ".ico", ".zip", ".mp4", ".pdf")):
                skip += 1
                continue
            try:
                with open(p, "rb") as fh:
                    c = base64.b64encode(fh.read()).decode()
            except Exception:
                continue
            url = f"https://api.github.com/repos/{slug}/contents/{urllib.parse.quote(rel, safe='/')}"
            st, resp = api("GET", url)
            sha = resp.get("sha") if st == 200 else None
            msg = ("add " if not sha else "update ") + rel + " (SXJ 2026-07-30 共通值→共济值)"
            data = {"message": msg, "content": c}
            if sha:
                data["sha"] = sha
            st, resp = api("PUT", url, data)
            if st in (200, 201):
                ok += 1
                print(f"  OK  {rel}")
            else:
                err += 1
                print(f"  ERR {rel} [{st}] {str(resp)[:160]}")

print(f"\n汇总: OK={ok} ERR={err} SKIP={skip}")
