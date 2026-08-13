# -*- coding: utf-8 -*-
import shutil, os

ROOT = r"C:\Users\Administrator\WorkBuddy\2026-07-24-23-26-27"
SITE = os.path.join(ROOT, "hygzz-top-site")

jobs = [
    # 今日讨论产物
    ("sxj-progress-model.html", "sxj-progress-model.html"),
    ("2026-08-08-问题整理.md", "2026-08-08-问题整理.md"),
    ("贡献值-社会资源三元-讨论稿.md", "贡献值-社会资源三元-讨论稿.md"),
    ("SXJ-wiki-map-design.md", "SXJ-wiki-map-design.md"),
    # 同步两棵树（解决 A4 副本未同步）
    ("knowledge_tree.html", "knowledge_tree.html"),
    ("knowledge_tree.html", "app/theory/knowledge_tree.html"),
    ("concept_tree.html", "concept_tree.html"),
    ("concept_tree.html", "app/theory/concept_tree.html"),
]

ok = 0
for src, dst in jobs:
    s = os.path.join(ROOT, src)
    d = os.path.join(SITE, dst)
    if not os.path.exists(s):
        print("MISSING SRC:", s); continue
    os.makedirs(os.path.dirname(d), exist_ok=True)
    shutil.copy2(s, d)
    ok += 1
    print("COPY", dst, os.path.getsize(s), "bytes")

print("DONE %d/%d" % (ok, len(jobs)))
