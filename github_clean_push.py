#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Fetch each GitHub Pages repo's current files, remove BETA banner, push back.
Origin of live hygzz.cn/.com = GitHub Pages (baixi6313/sxj-domestic, sxj-international)."""
import os, base64, json, re, urllib.request, urllib.error

PAT = __import__("os").environ.get("GH_PAT", "")
API = "https://api.github.com"
REPOS = [("baixi6313", "sxj-domestic"), ("baixi6313", "sxj-international")]

HTML_STYLE = re.compile(r'<style>\.beta-banner\{.*?</style>', re.S)
HTML_DIV = re.compile(r'<div class="beta-banner">.*?</div>', re.S)
PROTOTYPE_BETA = re.compile(r'<span class="beta">.*?</span>', re.S)
PROTOTYPE_NOTE = re.compile(r'<div class="note">.*?</div>', re.S)
WXML_BETA = re.compile(r'<view class="beta-banner"[^>]*>(?:.*?</view>){1,6}\s*</view>', re.S)
WXML_PROV = re.compile(r'<view class="prov-note">.*?</view>', re.S)
CSS_SEL = re.compile(r'\.(?:beta-banner|bb-row|bb-badge|bb-text|bb-sub|prov-note)(?:\s+\.hl)?\s*\{[^}]*\}', re.S)
CSS_COMMENT = re.compile(r'/\*[^*]*?测试版 BETA 横幅.*?\*/', re.S)
ORPHAN_CSS = re.compile(r'\.beta-banner\s+\.[a-z0-9-]+\s*\{[^}]*\}', re.S)
LABEL1 = re.compile(r' · 测试版 BETA')
LABEL2 = re.compile(r'测试版 BETA')
LABEL3 = re.compile(r'非实地实施产品')
TIDY1 = re.compile(r'( · ){2,}')
TIDY2 = re.compile(r' · (?=[。.])')

def clean(text, ext):
    if ext in (".html", ".htm"):
        text = HTML_STYLE.sub("", text)
        text = HTML_DIV.sub("", text)
        if "sxj-app-prototype" in text:
            text = PROTOTYPE_BETA.sub("", text)
            text = PROTOTYPE_NOTE.sub("", text)
    elif ext == ".wxml":
        text = WXML_BETA.sub("", text)
        text = WXML_PROV.sub("", text)
    elif ext in (".wxss", ".css"):
        text = CSS_SEL.sub("", text)
        text = CSS_COMMENT.sub("", text)
        text = ORPHAN_CSS.sub("", text)
    else:
        return text
    # body-text BETA labels (html/wxml/css)
    text = LABEL1.sub("", text)
    text = LABEL2.sub("", text)
    text = LABEL3.sub("", text)
    text = TIDY1.sub(" · ", text)
    text = TIDY2.sub("", text)
    return text

def api(method, path, data=None):
    url = API + path
    headers = {"Authorization": f"Bearer {PAT}", "Accept": "application/vnd.github+json", "User-Agent": "sxj-cleaner"}
    body = json.dumps(data).encode() if data is not None else None
    req = urllib.request.Request(url, data=body, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return r.status, json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        try:
            return e.code, json.loads(e.read().decode())
        except Exception:
            return e.code, {}

for owner, repo in REPOS:
    print(f"\n##### {owner}/{repo} #####")
    st, tree = api("GET", f"/repos/{owner}/{repo}/git/trees/main?recursive=1")
    if st != 200:
        print("  tree fetch failed:", st, tree.get("message")); continue
    files = [t["path"] for t in tree.get("tree", []) if t["type"] == "blob"
             and os.path.splitext(t["path"])[1].lower() in (".html", ".htm", ".wxml", ".wxss", ".css")]
    print(f"  candidate files: {len(files)}")
    updated = 0
    for path in files:
        st, data = api("GET", f"/repos/{owner}/{repo}/contents/{path}")
        if st != 200:
            print("  GET FAIL", path, st); continue
        sha = data["sha"]
        content = base64.b64decode(data["content"]).decode("utf-8")
        ext = os.path.splitext(path)[1].lower()
        new = clean(content, ext)
        if new != content:
            b64 = base64.b64encode(new.encode("utf-8")).decode()
            st2, _ = api("PUT", f"/repos/{owner}/{repo}/contents/{path}",
                         {"message": f"chore: remove BETA banner from {path}", "content": b64, "sha": sha})
            print(f"  UPDATED {path} -> HTTP {st2}")
            updated += 1
        else:
            print(f"  clean   {path}")
    print(f"  >>> {updated} file(s) updated in {repo}")
