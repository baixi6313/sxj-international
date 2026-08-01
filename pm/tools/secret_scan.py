#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""提交前密钥扫描闸门（光锥运维部 · 安全合规前置）。
扫描给定目录/文件，命中疑似密钥则非零退出，阻断提交。
用法：python secret_scan.py [path]   （默认扫描当前仓库）
"""
import os, sys, re, subprocess

PATTERNS = [
    re.compile(r'ghp_[A-Za-z0-9]{20,}'),
    re.compile(r'github_pat_[A-Za-z0-9_]{30,}'),
    re.compile(r'cfat_[A-Za-z0-9]{20,}'),
    re.compile(r'cfut_[A-Za-z0-9]{20,}'),
    re.compile(r'AKID[A-Za-z0-9]{20,}'),
    re.compile(r'TENCENT_SECRET_ID\s*=\s*["\']?[A-Za-z0-9]{10,}'),
    re.compile(r'TENCENT_SECRET_KEY\s*=\s*["\']?[A-Za-z0-9/+=]{20,}'),
    re.compile(r'SecretId\s*=\s*["\']?[A-Za-z0-9]{10,}'),
    re.compile(r'SecretKey\s*=\s*["\']?[A-Za-z0-9/+=]{20,}'),
]

SKIP_DIRS = {".git", "node_modules", "__pycache__", ".workbuddy", "wrangler-tmp"}
SKIP_EXT = {".png", ".jpg", ".jpeg", ".gif", ".pdf", ".zip", ".apk", ".keystore", ".key"}

def scan(root):
    hits = []
    for dp, dns, fns in os.walk(root):
        dns[:] = [d for d in dns if d not in SKIP_DIRS]
        for fn in fns:
            if os.path.splitext(fn)[1].lower() in SKIP_EXT:
                continue
            p = os.path.join(dp, fn)
            try:
                with open(p, encoding="utf-8", errors="ignore") as f:
                    for i, line in enumerate(f, 1):
                        for pat in PATTERNS:
                            m = pat.search(line)
                            if m:
                                hits.append((p, i, m.group(0)[:8] + "…"))
            except Exception:
                pass
    return hits

def main():
    root = sys.argv[1] if len(sys.argv) > 1 else "."
    print(f"🔍 扫描密钥：{root}")
    hits = scan(root)
    if not hits:
        print("✅ 无密钥泄漏")
        sys.exit(0)
    print(f"❌ 检测到 {len(hits)} 处疑似密钥，已阻断：")
    for p, i, frag in hits:
        print(f"   {p}:{i}  {frag}")
    sys.exit(1)

if __name__ == "__main__":
    main()
