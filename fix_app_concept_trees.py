# -*- coding: utf-8 -*-
import io

files = [
    r"C:\Users\Administrator\WorkBuddy\2026-07-24-23-26-27\hygzz-top-site\app\theory\concept_tree.html",
    r"C:\Users\Administrator\WorkBuddy\2026-07-24-23-26-27\sxj-android-app\app\src\main\assets\www\theory\concept_tree.html",
]

PROTECT = [
    'A 值「共通值」正式定名为「共济值」',
    '「共助」（第四阶·国际联动）保持不变。本档案历史条目中的“共通值”为彼时术语，请对照阅读。',
    '本档案历史条目中的"共通值"为彼时术语，请对照阅读。',
]

for path in files:
    with io.open(path, "r", encoding="utf-8") as f:
        txt = f.read()
    before = txt.count("共通值")
    txt2 = txt.replace("共通值", "共济值")
    for p in PROTECT:
        p_new = p.replace("共通值", "共济值")
        if p_new in txt2:
            txt2 = txt2.replace(p_new, p)
    after = txt2.count("共通值")
    with io.open(path, "w", encoding="utf-8") as f:
        f.write(txt2)
    print("FILE:", path)
    print("  before=%d after=%d replaced=%d" % (before, after, before - after))
    for i, line in enumerate(txt2.splitlines(), 1):
        if "共通值" in line:
            print("  REMAIN L%d: %s" % (i, line.strip()[:110]))
