# -*- coding: utf-8 -*-
"""将 hygzz_cn(.com) 首页的蓝色品牌主题改为与其他三站一致的红金主题。
只动品牌蓝相关 token；语义色（红/绿/紫/橙/青/金）保留。"""
import io

F = "hygzz_cn/index.html"
s = io.open(F, "r", encoding="utf-8").read()

REPS = [
    # :root 底色/卡片（仅精准替换，不动全文 #fff）
    ("--bg:#ffffff", "--bg:#fafaf9"),
    ("--card:#f8f9fa", "--card:#fff"),
    # 品牌蓝 -> 红金
    ("#0066ff", "#A32D2D"),          # 主品牌蓝 -> 品牌红
    ("#e8f0ff", "#fef0f0"),          # 浅蓝底 -> 浅红底
    ("#0052cc", "#8a2424"),          # 深蓝 hover -> 深红 hover
    ("#f0f2f5", "#f7f3f0"),          # 灰蓝底 -> 暖灰底
    ("%230066ff", "%23A32D2D"),      # favicon 蓝 -> 红
]
for a, b in REPS:
    n = s.count(a)
    s = s.replace(a, b)
    print(f"{n:3d}  {a} -> {b}")

# 在 :root 内补一对金，供强调使用（紧跟 accent-hover 之后）
anchor = "--accent-hover:#8a2424;"
if anchor in s and "--gold:#C9A24B" not in s:
    s = s.replace(anchor, anchor + "--gold:#C9A24B;--gold-light:#fef8e8;", 1)
    print("   + injected --gold / --gold-light")

io.open(F, "w", encoding="utf-8").write(s)
print("DONE ->", F)
