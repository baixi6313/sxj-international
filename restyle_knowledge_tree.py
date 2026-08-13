# -*- coding: utf-8 -*-
"""把知识树（手绘牛皮纸+楷体）重写成浅色红金整体风（与 index 页一致）。"""
import io, sys

FILES = [
    r"c:\Users\Administrator\WorkBuddy\2026-07-24-23-26-27\knowledge_tree.html",
    r"c:\Users\Administrator\WorkBuddy\2026-07-24-23-26-27\hygzz-top-site\knowledge_tree.html",
    r"c:\Users\Administrator\WorkBuddy\2026-07-24-23-26-27\hygzz-top-site\app\theory\knowledge_tree.html",
    r"c:\Users\Administrator\WorkBuddy\2026-07-24-23-26-27\sxj-android-app\app\src\main\assets\www\theory\knowledge_tree.html",
]

REPS = [
    # --- :root 变量整体换浅色红金 ---
    ("  :root{\n    --paper:#f7f1e3; --ink:#2b2b2b; --ink2:#5a5048; --line:#3a342c;\n    --accent:#8a5a2b; --blue:#2f6f8f; --green:#3f7a4a; --red:#a23b32; --amber:#b07a1e;\n    --dashed:#9a8f7a;\n  }",
     "  :root{\n    --paper:#fafaf9; --ink:#1a1a2e; --ink2:#555; --line:#e8e0d8;\n    --accent:#A32D2D; --blue:#2f6f8f; --green:#2d8a4e; --red:#A32D2D; --amber:#b07a1e;\n    --dashed:#e8e0d8; --gold:#C9A24B;\n  }",
     "root-vars"),
    # --- body 字体 + 去网格底纹 ---
    ('font-family:"Kaiti SC","STKaiti","KaiTi","楷体","Comic Sans MS",cursive,sans-serif;',
     'font-family:-apple-system,"PingFang SC","Microsoft YaHei",sans-serif;',
     "body-font"),
    ("    background:var(--paper);\n    background-image:\n      repeating-linear-gradient(0deg, transparent 0 27px, rgba(120,100,70,.06) 27px 28px),\n      repeating-linear-gradient(90deg, transparent 0 27px, rgba(120,100,70,.06) 27px 28px);\n    color:var(--ink);",
     "    background:var(--paper);\n    color:var(--ink);",
     "body-grid"),
    # --- .hd / .hd2 去手绘 ---
    ("    background:#fffdf6;border:2px solid var(--line);\n    border-radius:255px 12px 225px 12px/12px 225px 12px 255px;\n    box-shadow:2px 3px 0 rgba(60,50,30,.10);",
     "    background:#fff;border:1px solid var(--line);\n    border-radius:12px;box-shadow:0 1px 3px rgba(0,0,0,.04);",
     "hd"),
    ("    background:#fffdf6;border:2px solid var(--line);\n    border-radius:14px 225px 14px 220px/220px 14px 225px 14px;\n    box-shadow:2px 3px 0 rgba(60,50,30,.10);",
     "    background:#fff;border:1px solid var(--line);\n    border-radius:12px;box-shadow:0 1px 3px rgba(0,0,0,.04);",
     "hd2"),
    # --- details.cat 去手绘 ---
    ("  details.cat{background:#fffdf6;border:2px solid var(--line);border-radius:18px 9px 18px 9px/9px 18px 9px 18px;\n    box-shadow:2px 3px 0 rgba(60,50,30,.10);overflow:hidden;margin:0 0 12px}",
     "  details.cat{background:#fff;border:1px solid var(--line);border-radius:12px;\n    box-shadow:0 1px 3px rgba(0,0,0,.04);overflow:hidden;margin:0 0 12px}",
     "cat"),
    # --- summary 背景棕->红 ---
    ("    display:flex;align-items:center;gap:10px;background:rgba(138,90,43,.07)}",
     "    display:flex;align-items:center;gap:10px;background:rgba(163,45,45,.05)}",
     "summary-bg"),
    # --- .node 去手绘旋转 ---
    ("  .node{border:1.6px solid var(--line);border-radius:12px 20px 12px 20px/20px 12px 20px 12px;\n    padding:11px 14px;margin:10px 0;background:#fffef9;box-shadow:1px 2px 0 rgba(60,50,30,.07);transform:rotate(-.25deg)}\n  .node:nth-child(even){transform:rotate(.25deg)}",
     "  .node{border:1px solid var(--line);border-radius:10px;\n    padding:11px 14px;margin:10px 0;background:#fff;box-shadow:0 1px 2px rgba(0,0,0,.03)}",
     "node"),
    # --- .node .d b 强调色 ---
    ("  .node .d b{color:var(--ink)}", "  .node .d b{color:var(--accent)}", "node-b"),
    # --- 标签配色 ---
    ("  .t-m{background:rgba(138,90,43,.12);color:var(--accent)}", "  .t-m{background:rgba(163,45,45,.10);color:var(--accent)}", "t-m"),
    ("  .t-r{background:rgba(162,59,50,.12);color:var(--red)}", "  .t-r{background:rgba(163,45,45,.14);color:var(--red)}", "t-r"),
    ("  .t-k{background:rgba(90,80,72,.10);color:var(--ink2)}", "  .t-k{background:rgba(85,85,85,.10);color:var(--ink2)}", "t-k"),
    # --- legend / note 底色 ---
    ("  .legend span{font-size:12px;background:#fffdf6;border:1.5px solid var(--line);padding:3px 11px;border-radius:20px}",
     "  .legend span{font-size:12px;background:#fff;border:1px solid var(--line);padding:3px 11px;border-radius:20px}",
     "legend"),
    ("  .note{margin:26px auto 0;max-width:920px;background:#fffdf6;border:2px solid var(--line);\n    border-left:6px solid var(--accent);border-radius:14px;padding:16px 20px;font-size:14px;line-height:1.8;color:var(--ink2)}",
     "  .note{margin:26px auto 0;max-width:920px;background:#fff;border:1px solid var(--line);\n    border-left:6px solid var(--accent);border-radius:14px;padding:16px 20px;font-size:14px;line-height:1.8;color:var(--ink2)}",
     "note"),
    # --- hover / pulse 配色 ---
    ("  .sk-limb a:hover rect{fill:#f3e9d2}", "  .sk-limb a:hover rect{fill:#fef8e8}", "hover"),
    ("  @keyframes pulse{0%,100%{box-shadow:0 0 0 0 rgba(162,59,50,.0)}50%{box-shadow:0 0 0 4px rgba(162,59,50,.18)}}",
     "  @keyframes pulse{0%,100%{box-shadow:0 0 0 0 rgba(163,45,45,0)}50%{box-shadow:0 0 0 4px rgba(163,45,45,.18)}}",
     "pulse"),
    # --- 内联变更盒子（深色字->浅底可见） ---
    ('<div style="margin:16px 0;padding:14px 18px;border:1px solid #e0a458;border-radius:12px;background:rgba(224,164,88,.12);font-size:13.5px;line-height:1.75;color:#e6edf3">\n  <b style="color:#e0a458">概念变更 · 2026-07-30</b>　A 值「共通值」正式定名为「<b style="color:#5ec8d8">共济值</b>」。<br>',
     '<div style="margin:16px 0;padding:14px 18px;border:1px solid #C9A24B;border-radius:12px;background:rgba(201,162,75,.12);font-size:13.5px;line-height:1.75;color:#1a1a2e">\n  <b style="color:#C9A24B">概念变更 · 2026-07-30</b>　A 值「共通值」正式定名为「<b style="color:#A32D2D">共济值</b>」。<br>',
     "inline-box"),
    # --- .sk-limb text SVG 字体（楷体->干净无衬线） ---
    ('  .sk-limb text{font-family:"Kaiti SC","STKaiti","KaiTi",cursive;font-size:15px;fill:var(--ink)}',
     '  .sk-limb text{font-family:-apple-system,"PingFang SC","Microsoft YaHei",sans-serif;font-size:15px;fill:var(--ink)}',
     "sk-limb-font"),
]

# SVG 概览图配色（replace_all）
SVG_COLORS = [
    ("#3a342c", "#A32D2D"),   # 手绘描边 -> 品牌红
    ("#fffdf6", "#fff"),       # 节点填充 -> 白
    ("#2b2b2b", "#1a1a2e"),   # 文字 -> 深墨
    ("#5a5048", "#555"),       # 副文字 -> 灰
    ("#fdeccb", "#fef8e8"),   # 根矩形 -> 金浅
    ("#f3e9d2", "#fef8e8"),   # hover -> 金浅
]

for fp in FILES:
    with io.open(fp, "r", encoding="utf-8") as f:
        s = f.read()
    report = []
    for old, new, label in REPS:
        c = s.count(old)
        if c:
            s = s.replace(old, new)
        report.append("%-12s %d" % (label, c))
    for old, new in SVG_COLORS:
        c = s.count(old)
        if c:
            s = s.replace(old, new)
        report.append("svg %-9s %d" % (old, c))
    # 移除手绘 filter
    fc = s.count(' filter="url(#rough)"')
    if fc:
        s = s.replace(' filter="url(#rough)"', '')
    report.append("filter-rm    %d" % fc)
    with io.open(fp, "w", encoding="utf-8") as f:
        f.write(s)
    print("== %s ==" % fp)
    print("  " + "  ".join(report))
print("DONE")
