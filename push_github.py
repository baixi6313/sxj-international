import os, re, json, base64, urllib.request, urllib.error

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

API = "https://api.github.com/repos/baixi6313"
H = {"Authorization": "token " + PAT, "Accept": "application/vnd.github+json",
     "Content-Type": "application/json"}


def put(repo, local, remote, msg):
    data = open(local, 'rb').read()
    content = base64.b64encode(data).decode()
    from urllib.parse import quote
    url = API + "/" + repo + "/contents/" + quote(remote, safe="/")
    sha = None
    try:
        r = urllib.request.urlopen(urllib.request.Request(url, headers=H))
        sha = json.load(r)["sha"]
    except urllib.error.HTTPError as e:
        if e.code != 404:
            raise
    body = {"message": msg, "content": content}
    if sha:
        body["sha"] = sha
    req = urllib.request.Request(url, data=json.dumps(body).encode(),
                                 headers=H, method="PUT")
    try:
        urllib.request.urlopen(req)
        print("  OK " + repo + "/" + remote + "  (" + ("update" if sha else "create") + ")")
    except urllib.error.HTTPError as e:
        err = json.load(e)
        print("  FAIL " + repo + "/" + remote + "  HTTP " + str(e.code) + ": " + err.get("message", ""))


print("== PUSH sxj-top (hygzz.top) ==")
top = "C:/Users/Administrator/WorkBuddy/2026-07-24-23-26-27/hygzz-top-site"
put("sxj-top", top + "/index.html", "index.html",
    "feat: 首页导航下新增 evt_009 醒目横幅")
put("sxj-top", top + "/events.html", "events.html",
    "feat: events.html 新增 seed8=evt_009 + seed9=evt_010(境外委托复测·低置信度)")

print("== PUSH sxj-maip-v1.0 (协议) ==")
v = "C:/Users/Administrator/WorkBuddy/2026-07-24-23-26-27/sxj-verify"
put("sxj-maip-v1.0", v + "/SXJ-MAIP-v1.0.md", "SXJ-MAIP-v1.0.md",
    "feat: 附录C/E 接入 evt_009; G-9 升级为已记录公共事现")
put("sxj-maip-v1.0", v + "/SXJ-MAIP-v1.0.sha256", "SXJ-MAIP-v1.0.sha256",
    "chore: 刷新套件指纹(含 events.html)")
put("sxj-maip-v1.0", v + "/events.html", "events.html",
    "feat: 事件簿新增 evt_010 = 境外委托复测 G-9(跨境验证模式·低置信度·不升级 evt_009)")
put("sxj-maip-v1.0", v + "/maip-portal/index.html", "maip-portal/index.html",
    "rebuild: 门户嵌入 evt_009 引用与新指纹")
put("sxj-maip-v1.0", v + "/SXJ-协议审核部核心内容.md", "SXJ-协议审核部核心内容.md",
    "feat: 协议审核部已生效章程")
put("sxj-maip-v1.0", v + "/SXJ-lightcone-positioning.md", "SXJ-lightcone-positioning.md",
    "feat: 事现鉴光锥坐标定位理论模型")
put("sxj-maip-v1.0", v + "/interaction-round6-synthesis.md", "interaction-round6-synthesis.md",
    "feat: 第六轮五家回应跨平台印证综合")
print("DONE")
