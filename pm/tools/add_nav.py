#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
add_nav.py — 给目录下所有 .html 注入统一导航条（组织架构一览 / 发展历史）。
- 已注入过（含标记 <!-- SXJ_NAV -->）则跳过。
- lang=zh 用中文标签 + org.html/history.html；lang=en 用英文标签 + org_en.html/history_en.html。
- 注入位置：<body ...> 之后。
用法：python add_nav.py <dir> [zh|en]
"""
import sys, re, os, glob

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

def add_nav_to_file(path, nav):
    s = open(path, 'r', encoding='utf-8').read()
    if '<!-- SXJ_NAV -->' in s:
        return False
    m = re.search(r'<body[^>]*>', s, re.IGNORECASE)
    if not m:
        return False
    s = s[:m.end()] + nav + s[m.end():]
    open(path, 'w', encoding='utf-8').write(s)
    return True

def main():
    d = sys.argv[1] if len(sys.argv) > 1 else '.'
    lang = sys.argv[2] if len(sys.argv) > 2 else 'zh'
    nav = NAV_EN if lang == 'en' else NAV_ZH
    n = 0
    for f in sorted(glob.glob(os.path.join(d, '**', '*.html'), recursive=True)):
        if add_nav_to_file(f, nav):
            n += 1
            print('  + nav:', f)
    print(f'done: injected {n} file(s) [{lang}] in {d}')

if __name__ == '__main__':
    main()
