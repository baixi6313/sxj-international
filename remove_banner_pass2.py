#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Pass 2: remove leftover '测试版 BETA' / '非实地实施产品' body labels + orphaned banner CSS."""
import os, re

CUR = "C:/Users/Administrator/WorkBuddy/2026-07-24-23-26-27"
OLD = "C:/Users/Administrator/WorkBuddy/2026-07-22-08-14-20"

# orphaned banner sub-element CSS rules (e.g. .beta-banner .b1 { ... })
ORPHAN_CSS = re.compile(r'\.beta-banner\s+\.[a-z0-9-]+\s*\{[^}]*\}', re.S)

# body-text BETA labels
LABEL1 = re.compile(r' · 测试版 BETA')          # leading separator form
LABEL2 = re.compile(r'测试版 BETA')
LABEL3 = re.compile(r'非实地实施产品')
# tidy leftover double separators / trailing separator before punctuation
TIDY1 = re.compile(r'( · ){2,}')                 # " ·  · " -> " · "
TIDY2 = re.compile(r' · (?=[。.])')              # " · 。" -> "。"

SKIP_DIRS = {".git", "node_modules", "__pycache__", ".workbuddy"}

def walk(root):
    for dp, dns, fns in os.walk(root):
        dns[:] = [d for d in dns if d not in SKIP_DIRS]
        for fn in fns:
            yield os.path.join(dp, fn)

def process(path):
    ext = os.path.splitext(path)[1].lower()
    if ext not in (".html", ".htm", ".wxml", ".wxss", ".css"):
        return False
    try:
        s = open(path, encoding="utf-8").read()
    except Exception:
        return False
    orig = s
    if ext in (".wxss", ".css"):
        s = ORPHAN_CSS.sub("", s)
    else:
        s = LABEL1.sub("", s)
        s = LABEL2.sub("", s)
        s = LABEL3.sub("", s)
        s = TIDY1.sub(" · ", s)
        s = TIDY2.sub("", s)
    if s != orig:
        open(path, "w", encoding="utf-8").write(s)
        return True
    return False

roots = [CUR, os.path.join(OLD, "hygzz_cn"), os.path.join(OLD, "hygzz_cn_domestic")]
changed = []
for r in roots:
    if not os.path.isdir(r):
        continue
    for p in walk(r):
        if process(p):
            changed.append(p.replace(CUR, "<CUR>").replace(OLD, "<OLD>"))

print(f"Changed {len(changed)} files (pass 2):")
for p in changed:
    print("  ", p)
