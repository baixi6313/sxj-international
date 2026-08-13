# -*- coding: utf-8 -*-
"""通过 GitHub Contents API 把三元矩阵套件【只增不删】推到远程 main:
   - 新增 matrix/ 目录(7 文件, 全新路径, 零冲突)
   - 在远程现有页面的红底导航【追加】一个「三元坐标场」链接(不改动其它内容)
   这样不会破坏本地与远程既有的分叉编辑。"""
import os, base64, json, urllib.request, urllib.error

TOKEN = os.environ.get("GH_TOKEN", "")
BASE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(BASE, "sxj-matrix")
MATRIX_FILES = ["index.html", "axis.html", "wiki.html", "map.html", "heat.html", "sca.html", "data.js", "style.css"]
API = "https://api.github.com"
OWNER = "baixi6313"
# (repo, [需要注入导航的页面])
TARGETS = {
    "sxj-international": ["index.html", "events.html", "knowledge_tree.html", "concept_tree.html",
                          "whitepaper.html", "critical_synthesis_report.html", "qualitative_analysis.html"],
    "sxj-domestic": ["index.html", "events.html", "knowledge_tree.html", "concept_tree.html",
                     "whitepaper.html", "critical_synthesis_report.html", "qualitative_analysis.html"],
}

def api(method, path, data=None):
    url = API + path
    headers = {"Authorization": f"Bearer {TOKEN}", "Accept": "application/vnd.github+json",
               "Content-Type": "application/json"}
    body = json.dumps(data).encode() if data else None
    req = urllib.request.Request(url, data=body, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=90) as r:
            return r.status, json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        try:
            return e.code, json.loads(e.read().decode())
        except Exception:
            return e.code, {"message": e.read().decode()[:200]}

def put_file(repo, path, content_bytes, sha=None, msg=""):
    b64 = base64.b64encode(content_bytes).decode()
    data = {"message": msg, "content": b64, "branch": "main"}
    if sha:
        data["sha"] = sha
    return api("PUT", f"/repos/{OWNER}/{repo}/contents/{path}", data)

BANNER = ('<div style="background:#A32D2D;padding:6px 14px;font-family:-apple-system,Segoe UI,'
          'Roboto,Helvetica,Arial,sans-serif;display:flex;gap:14px;flex-wrap:wrap;align-items:center;">'
          '<span style="color:#fff;font-weight:700;">三元坐标场</span>'
          '<a href="./matrix/" style="color:#FFE6A8;text-decoration:none;">中枢</a>'
          '<a href="./matrix/axis.html" style="color:#FFE6A8;text-decoration:none;">坐标轴</a>'
          '<a href="./matrix/wiki.html" style="color:#FFE6A8;text-decoration:none;">维基</a>'
          '<a href="./matrix/map.html" style="color:#FFE6A8;text-decoration:none;">地图</a>'
          '<a href="./matrix/heat.html" style="color:#FFE6A8;text-decoration:none;">热力密度图</a>'
          '</div>\n')

def inject_nav(html):
    """返回 (new_html, status). status: 'has' 已有 / 'red' 红底导航注入 / 'banner' 启动条兜底 / 'skip' 无法处理"""
    if 'href="./matrix/"' in html:
        return html, 'has'
    idx = html.find("background:#A32D2D")
    if idx >= 0:
        end = html.find("</nav>", idx)
        if end >= 0:
            link = '  <a href="./matrix/" style="color:#FFE6A8;text-decoration:none;padding:4px 8px;font-weight:700;">三元坐标场</a>\n'
            return html[:end] + link + html[end:], 'red'
    # 兜底：页面顶部加启动条
    bi = html.find("<body")
    if bi >= 0:
        be = html.find(">", bi)
        return html[:be + 1] + BANNER + html[be + 1:], 'banner'
    return BANNER + html, 'banner'

for repo, pages in TARGETS.items():
    print(f"\n##### {repo} #####")
    # 1) upsert matrix 目录（已存在则带 sha 更新，否则创建）
    for fn in MATRIX_FILES:
        p = os.path.join(SRC, fn)
        with open(p, "rb") as f:
            cb = f.read()
        st0, res0 = api("GET", f"/repos/{OWNER}/{repo}/contents/matrix/{fn}?ref=main")
        sha = res0.get("sha") if st0 == 200 else None
        st, res = put_file(repo, f"matrix/{fn}", cb, sha, f"upsert matrix/{fn} (三元坐标场套件 + 搜索栏)")
        if st in (201, 200):
            print(f"  ~ matrix/{fn}  -> {st} OK" + (" (update)" if sha else " (create)"))
        else:
            print(f"  ! matrix/{fn}  -> {st} {res.get('message')}")
    # 2) 在远程现有页面追加导航
    for pg in pages:
        st, res = api("GET", f"/repos/{OWNER}/{repo}/contents/{pg}?ref=main")
        if st != 200:
            print(f"  - {pg} 跳过(GET {st}: {res.get('message')})")
            continue
        sha = res["sha"]
        html = base64.b64decode(res["content"]).decode("utf-8")
        new_html, status = inject_nav(html)
        if status == 'has':
            print(f"  - {pg} 跳过(已含导航)")
            continue
        st2, res2 = put_file(repo, pg, new_html.encode("utf-8"), sha, f"inject 三元坐标场 nav into {pg}")
        if st2 == 200:
            print(f"  ~ {pg}  导航注入 OK [{status}]")
        else:
            print(f"  ! {pg}  注入失败 {st2} {res2.get('message')}")
print("\n全部完成。")
