#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""prepare_nav.py — 复制 SVG/内容页到各站点，并注入导航条。"""
import os, shutil, sys, re, glob

WS = r"C:\Users\Administrator\WorkBuddy\2026-07-24-23-26-27"
CN = r"C:\Users\Administrator\WorkBuddy\2026-07-22-08-14-20\hygzz_cn_domestic"
TOP = os.path.join(WS, "hygzz-top-site")
APPWWW = os.path.join(WS, "sxj-android-app", "app", "src", "main", "assets", "www")
COM = r"C:\Users\Administrator\WorkBuddy\2026-07-22-08-14-20\hygzz_cn"  # .com 源（国际）

NAV_ZH = '''
<!-- SXJ_NAV -->
<nav style="position:sticky;top:0;z-index:999;display:flex;flex-wrap:wrap;gap:4px;align-items:center;background:#A32D2D;padding:8px 14px;font-family:-apple-system,Segoe UI,Roboto,Helvetica,Arial,sans-serif;">
  <a href="./" style="color:#fff;font-weight:700;text-decoration:none;margin-right:10px;">事现鉴</a>
  <a href="./events.html" style="color:#f4e9c9;text-decoration:none;padding:4px 8px;">事件簿</a>
  <a href="./knowledge_tree.html" style="color:#f4e9c9;text-decoration:none;padding:4px 8px;">知识树</a>
  <a href="./org.html" style="color:#f4e9c9;text-decoration:none;padding:4px 8px;">组织架构一览</a>
  <a href="./history.html" style="color:#f4e9c9;text-decoration:none;padding:4px 8px;">发展历史</a>
</nav>
'''
NAV_EN = '''
<!-- SXJ_NAV -->
<nav style="position:sticky;top:0;z-index:999;display:flex;flex-wrap:wrap;gap:4px;align-items:center;background:#A32D2D;padding:8px 14px;font-family:-apple-system,Segoe UI,Roboto,Helvetica,Arial,sans-serif;">
  <a href="./" style="color:#fff;font-weight:700;text-decoration:none;margin-right:10px;">SXJ</a>
  <a href="./events.html" style="color:#f4e9c9;text-decoration:none;padding:4px 8px;">Events</a>
  <a href="./knowledge_tree.html" style="color:#f4e9c9;text-decoration:none;padding:4px 8px;">Knowledge Tree</a>
  <a href="./org_en.html" style="color:#f4e9c9;text-decoration:none;padding:4px 8px;">Organization</a>
  <a href="./history_en.html" style="color:#f4e9c9;text-decoration:none;padding:4px 8px;">History</a>
</nav>
'''

def add_nav(path, nav):
    s = open(path, 'r', encoding='utf-8').read()
    if '<!-- SXJ_NAV -->' in s:
        return False
    m = re.search(r'<body[^>]*>', s, re.IGNORECASE)
    if not m:
        return False
    s = s[:m.end()] + nav + s[m.end():]
    open(path, 'w', encoding='utf-8').write(s)
    return True

def prep(src_dir, nav, copy_pages, en_pages=False):
    od = os.path.join(src_dir, 'assets', 'org')
    os.makedirs(od, exist_ok=True)
    # SVG（跳过自拷贝）
    for svg in ('sxj-org-structure.svg', 'sxj-org-structure-en.svg'):
        src = os.path.join(WS, 'assets', 'org', svg)
        dst = os.path.join(od, svg)
        if os.path.abspath(src) != os.path.abspath(dst):
            shutil.copy(src, dst)
    # 内容页
    if copy_pages:
        for p in ('org.html', 'history.html'):
            shutil.copy(os.path.join(WS, p), os.path.join(src_dir, p))
    if en_pages:
        for p in ('org_en.html', 'history_en.html'):
            shutil.copy(os.path.join(WS, p), os.path.join(src_dir, p))
    n = 0
    for f in sorted(glob.glob(os.path.join(src_dir, '**', '*.html'), recursive=True)):
        base = os.path.basename(f)
        if base in ('org.html', 'history.html') and nav is NAV_EN:
            continue
        if base in ('org_en.html', 'history_en.html'):
            continue
        if add_nav(f, nav):
            n += 1
            print('  + nav:', f)
    print(f'  [{src_dir}] injected {n}')

print("CN (zh):")
prep(CN, NAV_ZH, True)
print("TOP (zh):")
prep(TOP, NAV_ZH, True)
print("APP www (zh):")
prep(APPWWW, NAV_ZH, True)
print("COM = hygzz_cn (en):")
prep(COM, NAV_EN, False, en_pages=True)
print("DONE")
