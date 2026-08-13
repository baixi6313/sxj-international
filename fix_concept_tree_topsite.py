# -*- coding: utf-8 -*-
import io, sys

path = r"C:\Users\Administrator\WorkBuddy\2026-07-24-23-26-27\hygzz-top-site\concept_tree.html"

with io.open(path, "r", encoding="utf-8") as f:
    txt = f.read()

before = txt.count("共通值")

# Protected rename-announcement phrases (keep 共通值 as historical record)
PROTECT = [
    'A 值「共通值」正式定名为「共济值」',
    '「共助」（第四阶·国际联动）保持不变。本档案历史条目中的“共通值”为彼时术语，请对照阅读。',
    '本档案历史条目中的"共通值"为彼时术语，请对照阅读。',
]

# 1) replace all
txt2 = txt.replace("共通值", "共济值")

# 2) restore protected phrases
for p in PROTECT:
    p_new = p.replace("共通值", "共济值")
    if p_new in txt2:
        txt2 = txt2.replace(p_new, p)

after = txt2.count("共通值")

with io.open(path, "w", encoding="utf-8") as f:
    f.write(txt2)

print("before occurrences:", before)
print("after occurrences :", after)
print("replaced          :", before - after)
print("remaining lines   :")
for i, line in enumerate(txt2.splitlines(), 1):
    if "共通值" in line:
        print("  L%d: %s" % (i, line.strip()[:120]))
