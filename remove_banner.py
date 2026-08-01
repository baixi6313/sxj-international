#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Remove BETA banner from all source files (HTML / WXML / WXSS / CSS). Idempotent."""
import os, re

CUR = "C:/Users/Administrator/WorkBuddy/2026-07-24-23-26-27"
OLD = "C:/Users/Administrator/WorkBuddy/2026-07-22-08-14-20"

# ---- HTML: remove <style>.beta-banner{...}</style> and <div class="beta-banner">...</div>
HTML_STYLE = re.compile(r'<style>\.beta-banner\{.*?</style>', re.S)
HTML_DIV = re.compile(r'<div class="beta-banner">.*?</div>', re.S)
# prototype-specific: <span class="beta">BETA ...</span> and <div class="note">测试版本 ...</div>
PROTOTYPE_BETA = re.compile(r'<span class="beta">.*?</span>', re.S)
PROTOTYPE_NOTE = re.compile(r'<div class="note">.*?</div>', re.S)

# ---- WXML: remove <view class="beta-banner" ...>...</view> and <view class="prov-note">...</view>
WXML_BETA = re.compile(r'<view class="beta-banner"[^>]*>(?:.*?</view>){1,6}\s*</view>', re.S)
WXML_PROV = re.compile(r'<view class="prov-note">.*?</view>', re.S)

# ---- WXSS/CSS: remove .beta-banner / .bb-* / .prov-note rules and the banner comment
CSS_SEL = re.compile(r'\.(?:beta-banner|bb-row|bb-badge|bb-text|bb-sub|prov-note)(?:\s+\.hl)?\s*\{[^}]*\}', re.S)
CSS_COMMENT = re.compile(r'/\*[^*]*?测试版 BETA 横幅.*?\*/', re.S)

SKIP_DIRS = {".git", "node_modules", "__pycache__", ".workbuddy"}

def walk(root):
    for dp, dns, fns in os.walk(root):
        dns[:] = [d for d in dns if d not in SKIP_DIRS]
        for fn in fns:
            yield os.path.join(dp, fn)

def process(path):
    ext = os.path.splitext(path)[1].lower()
    try:
        with open(path, encoding="utf-8") as f:
            s = f.read()
    except Exception:
        return False
    orig = s
    if ext in (".html", ".htm"):
        s = HTML_STYLE.sub("", s)
        s = HTML_DIV.sub("", s)
        if "sxj-app-prototype" in path:
            s = PROTOTYPE_BETA.sub("", s)
            s = PROTOTYPE_NOTE.sub("", s)
    elif ext == ".wxml":
        s = WXML_BETA.sub("", s)
        s = WXML_PROV.sub("", s)
    elif ext in (".wxss", ".css"):
        s = CSS_SEL.sub("", s)
        s = CSS_COMMENT.sub("", s)
    else:
        return False
    if s != orig:
        # 护栏：WXML 标签不配平则宁可放弃写入，避免破坏页面结构（曾因贪婪正则误删区块）
        if ext == ".wxml" and s.count("<view") != s.count("</view>"):
            print(f"[ABORT] 标签不配平，跳过写入: {path}")
            return False
        with open(path, "w", encoding="utf-8") as f:
            f.write(s)
        return True
    return False

roots = [
    CUR,
    os.path.join(OLD, "hygzz_cn"),
    os.path.join(OLD, "hygzz_cn_domestic"),
]
changed = []
for r in roots:
    if not os.path.isdir(r):
        print("MISSDIR", r); continue
    for p in walk(r):
        if process(p):
            changed.append(p)

print(f"\nChanged {len(changed)} files:")
for p in changed:
    print("  ", p.replace(CUR, "<CUR>").replace(OLD, "<OLD>"))
