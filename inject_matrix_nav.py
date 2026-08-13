# -*- coding: utf-8 -*-
"""把「三元坐标场」入口注入 hygzz-top-site 各页的红色统一导航。
识别锚点：导航里的 事件簿 链接行；在其后插入金色胶囊入口。幂等：已含 matrix/ 的页跳过。
"""
import os, re, io

SITE = r"C:\Users\Administrator\WorkBuddy\2026-07-24-23-26-27\hygzz-top-site"
LINK = '  <a href="./matrix/" style="color:#3a2a00;background:#C9A24B;font-weight:700;text-decoration:none;padding:4px 10px;border-radius:5px;">三元坐标场</a>\n'

# 匹配红色导航里的「事件簿」行
PAT = re.compile(r'(^[ \t]*<a href="\./events\.html"[^>]*>事件簿</a>[ \t]*\n)', re.M)

changed, skipped, failed = [], [], []
for fn in sorted(os.listdir(SITE)):
    if not fn.endswith(".html"):
        continue
    p = os.path.join(SITE, fn)
    with io.open(p, encoding="utf-8") as f:
        s = f.read()
    if "组织架构一览" not in s:
        continue
    if 'href="./matrix/"' in s or 'href="matrix/"' in s:
        skipped.append(fn)
        continue
    m = PAT.search(s)
    if not m:
        failed.append(fn)
        continue
    s2 = s[:m.end(1)] + LINK + s[m.end(1):]
    with io.open(p, "w", encoding="utf-8") as f:
        f.write(s2)
    changed.append(fn)

print("注入成功 %d 页: %s" % (len(changed), ", ".join(changed) if changed else "-"))
print("已存在跳过 %d 页: %s" % (len(skipped), ", ".join(skipped) if skipped else "-"))
print("未找到锚点 %d 页: %s" % (len(failed), ", ".join(failed) if failed else "-"))
