# -*- coding: utf-8 -*-
"""把 .top 双语源站复制为 .com 国际版源站 hygzz-com-site/。
排除 .top 专属部署配置(.git/.github/.wrangler)，并把 CNAME 内容改为 hygzz.com。
用法: python make_com_site.py
"""
import os, shutil

ROOT = r"C:\Users\Administrator\WorkBuddy\2026-07-24-23-26-27"
SRC = os.path.join(ROOT, "hygzz-top-site")
DST = os.path.join(ROOT, "hygzz-com-site")

EXCLUDE_DIRS = {".git", ".github", ".wrangler", ".wrangler-cache", "node_modules", "__pycache__"}

def walk():
    n = 0
    for dp, dns, fns in os.walk(SRC):
        dns[:] = [d for d in dns if d not in EXCLUDE_DIRS]
        rel = os.path.relpath(dp, SRC)
        for fn in fns:
            s = os.path.join(dp, fn)
            t = os.path.join(DST, rel, fn)
            os.makedirs(os.path.dirname(t), exist_ok=True)
            if fn.lower() == "cname":
                # 改为 .com 的 CNAME（COS 用不到，仅供将来 GitHub Pages 参考）
                with open(t, "w", encoding="utf-8") as f:
                    f.write("hygzz.com\n")
                print("CNAME -> hygzz.com")
            else:
                shutil.copy2(s, t)
            n += 1
    return n

if os.path.exists(DST):
    shutil.rmtree(DST)
print("复制文件数:", walk())
print("目标源站:", DST)
