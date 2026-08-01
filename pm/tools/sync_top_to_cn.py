# -*- coding: utf-8 -*-
"""
以 hygzz.top 为标准源，全站同步到 hygzz.cn 源目录（hygzz_cn_domestic）。
不修改 hygzz.top 本身，也不动 hygzz.com。
注意：CNAME 等域名特定文件不覆盖；复制后把 https://hygzz.top 替换为 https://hygzz.cn，
但保留四域口号中的裸 hygzz.top（四域之一）。
"""
import os, shutil

TOP = r"C:\Users\Administrator\WorkBuddy\2026-07-24-23-26-27\hygzz-top-site"
CN  = r"C:\Users\Administrator\WorkBuddy\2026-07-22-08-14-20\hygzz_cn_domestic"

# 不同步的域名/部署特定文件（保留目标目录的版本）
EXCLUDE_NAMES = {".git", ".github", ".wrangler", "CNAME", ".gitignore",
                 ".pagesignore", "push.bat", "README.md"}
EXCLUDE_EXT = {".txt"}  # 站点验证随机文件不跨域复制

def sync_dir(src, dst, recursive=True):
    for name in os.listdir(src):
        if name in EXCLUDE_NAMES:
            continue
        s = os.path.join(src, name)
        d = os.path.join(dst, name)
        if os.path.isdir(s):
            if recursive:
                os.makedirs(d, exist_ok=True)
                sync_dir(s, d, recursive=True)
        else:
            if os.path.splitext(name)[1].lower() in EXCLUDE_EXT:
                continue
            shutil.copy2(s, d)
            print("copied", os.path.relpath(d, CN))

def fix_domain():
    # 复制后把 https://hygzz.top 改成 https://hygzz.cn（不影响四域口号中的裸 hygzz.top）
    cnt = 0
    for root, dirs, files in os.walk(CN):
        if os.path.basename(root) in (".git", ".github", ".wrangler"):
            continue
        for f in files:
            if f.lower().endswith((".html", ".json", ".webmanifest", ".js", ".css")):
                p = os.path.join(root, f)
                try:
                    s = open(p, "r", encoding="utf-8").read()
                except Exception:
                    continue
                if "https://hygzz.top" in s:
                    s2 = s.replace("https://hygzz.top", "https://hygzz.cn")
                    open(p, "w", encoding="utf-8").write(s2)
                    cnt += s.count("https://hygzz.top")
    print(f"domain fix: replaced {cnt} https://hygzz.top -> https://hygzz.cn")

if __name__ == "__main__":
    print("=== sync top -> cn (content) ===")
    sync_dir(TOP, CN)
    print("=== fix domain refs in cn ===")
    fix_domain()
    print("=== done ===")
