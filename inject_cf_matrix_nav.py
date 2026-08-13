# -*- coding: utf-8 -*-
"""把三元矩阵套件并入 Cloudflare/GitHub 源仓库(hygzz_cn -> .com, hygzz_cn_domestic -> .cn)
并在红底 sticky 导航注入「三元坐标场」入口。"""
import os, shutil

BASE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(BASE, "sxj-matrix")
MATRIX_FILES = ["index.html", "axis.html", "wiki.html", "map.html", "heat.html", "data.js", "style.css"]

REPOS = {
    "hygzz_cn": "三元坐标场",
    "hygzz_cn_domestic": "三元坐标场",
}

LINK_STYLE = 'color:#FFE6A8;text-decoration:none;padding:4px 8px;font-weight:700;'

for repo, label in REPOS.items():
    rdir = os.path.join(BASE, repo)
    if not os.path.isdir(rdir):
        print("跳过(目录不存在):", repo)
        continue
    # 1) 复制套件
    dest = os.path.join(rdir, "matrix")
    os.makedirs(dest, exist_ok=True)
    for f in MATRIX_FILES:
        shutil.copy(os.path.join(SRC, f), os.path.join(dest, f))
    print(f"[{repo}] 已复制 {len(MATRIX_FILES)} 个套件文件到 matrix/")
    # 2) 注入导航（仅根目录含红底导航的 html）
    for fn in sorted(os.listdir(rdir)):
        if not fn.endswith(".html"):
            continue
        p = os.path.join(rdir, fn)
        with open(p, encoding="utf-8") as fh:
            txt = fh.read()
        if 'href="./matrix/"' in txt:
            continue  # 已注入
        idx = txt.find("background:#A32D2D")
        if idx < 0:
            continue
        end = txt.find("</nav>", idx)
        if end < 0:
            continue
        link = '  <a href="./matrix/" style="%s">%s</a>\n' % (LINK_STYLE, label)
        new = txt[:end] + link + txt[end:]
        with open(p, "w", encoding="utf-8") as fh:
            fh.write(new)
        print(f"[{repo}] 注入导航入口 -> {fn}")
print("完成。")
