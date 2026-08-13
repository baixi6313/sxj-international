# -*- coding: utf-8 -*-
"""把概念树（暗夜青色 #0f1419）重写成浅色红金整体风（与 index 页一致）。
用于：hygzz-top-site/app/theory/concept_tree.html 与安卓 app 内副本。"""
import io

FILES = [
    r"c:\Users\Administrator\WorkBuddy\2026-07-24-23-26-27\hygzz-top-site\app\theory\concept_tree.html",
    r"c:\Users\Administrator\WorkBuddy\2026-07-24-23-26-27\sxj-android-app\app\src\main\assets\www\theory\concept_tree.html",
]

REPS = [
    # --- :root 变量 暗夜->浅色红金 ---
    ("  :root{\n    --bg:#0f1419; --panel:#161d26; --panel2:#1c2530; --line:#2a3645;\n    --txt:#e6edf3; --dim:#9bb0c3; --acc:#5ec8d8; --acc2:#e0a458;\n    --red:#e06c75; --green:#7ec699; --amber:#e5c07b; --blue:#6cb6ff; --purple:#c792ea;\n  }",
     "  :root{\n    --bg:#fafaf9; --card:#fff; --panel:#fff; --panel2:#fbf7f1; --line:#e8e0d8;\n    --txt:#1a1a2e; --dim:#555; --acc:#A32D2D; --acc2:#C9A24B;\n    --red:#A32D2D; --green:#2d8a4e; --amber:#b07a1e; --blue:#2f6f8f; --purple:#7a5aa6;\n  }",
     "root-vars"),
    # --- h1 红色 ---
    ("  h1{font-size:25px;letter-spacing:.5px;margin-bottom:6px}",
     "  h1{font-size:25px;letter-spacing:.5px;margin-bottom:6px;color:var(--acc)}",
     "h1"),
    # --- legend 底色 ---
    ("  .legend span{font-size:11.5px;padding:2px 9px;border-radius:20px;border:1px solid var(--line)}",
     "  .legend span{font-size:11.5px;padding:2px 9px;border-radius:20px;border:1px solid var(--line);background:var(--card)}",
     "legend"),
    # --- details.cat 阴影 ---
    ("  details.cat{margin:0 0 12px;border:1px solid var(--line);border-radius:12px;background:var(--panel);overflow:hidden}",
     "  details.cat{margin:0 0 12px;border:1px solid var(--line);border-radius:12px;background:var(--card);overflow:hidden;box-shadow:0 1px 3px rgba(0,0,0,.04)}",
     "cat"),
    # --- summary 渐变 青->红 ---
    ("  details.cat>summary{cursor:pointer;padding:13px 16px;font-size:15.5px;font-weight:600;color:var(--acc);list-style:none;display:flex;align-items:center;gap:9px;background:linear-gradient(90deg,rgba(94,200,216,.07),transparent)}",
     "  details.cat>summary{cursor:pointer;padding:13px 16px;font-size:15.5px;font-weight:600;color:var(--acc);list-style:none;display:flex;align-items:center;gap:9px;background:linear-gradient(90deg,rgba(163,45,45,.06),transparent)}",
     "summary"),
    # --- 11 个 pill 配色 ---
    ("  .pill.meta{background:rgba(199,146,234,.18);color:var(--purple)}", "  .pill.meta{background:rgba(122,90,166,.14);color:var(--purple)}", "pill-meta"),
    ("  .pill.axi{background:rgba(108,182,255,.18);color:var(--blue)}", "  .pill.axi{background:rgba(47,111,143,.14);color:var(--blue)}", "pill-axi"),
    ("  .pill.val{background:rgba(126,198,153,.18);color:var(--green)}", "  .pill.val{background:rgba(45,138,78,.14);color:var(--green)}", "pill-val"),
    ("  .pill.ver{background:rgba(94,200,216,.18);color:var(--acc)}", "  .pill.ver{background:rgba(163,45,45,.10);color:var(--acc)}", "pill-ver"),
    ("  .pill.dis{background:rgba(229,192,123,.18);color:var(--amber)}", "  .pill.dis{background:rgba(176,122,30,.16);color:var(--amber)}", "pill-dis"),
    ("  .pill.gov{background:rgba(224,108,117,.16);color:var(--red)}", "  .pill.gov{background:rgba(163,45,45,.14);color:var(--red)}", "pill-gov"),
    ("  .pill.tec{background:rgba(155,176,195,.18);color:var(--dim)}", "  .pill.tec{background:rgba(85,85,85,.12);color:var(--dim)}", "pill-tec"),
    ("  .pill.app{background:rgba(94,200,216,.12);color:var(--acc)}", "  .pill.app{background:rgba(163,45,45,.08);color:var(--acc)}", "pill-app"),
    ("  .pill.crit{background:rgba(224,108,117,.18);color:var(--red)}", "  .pill.crit{background:rgba(163,45,45,.16);color:var(--red)}", "pill-crit"),
    ("  .pill.evo{background:rgba(229,192,123,.16);color:var(--amber)}", "  .pill.evo{background:rgba(176,122,30,.14);color:var(--amber)}", "pill-evo"),
    ("  .pill.conf{background:rgba(224,108,117,.22);color:var(--red);border:1px solid var(--red)}", "  .pill.conf{background:rgba(163,45,45,.18);color:var(--red);border:1px solid var(--red)}", "pill-conf"),
    # --- .root 渐变 青金->红金 ---
    ("  .root{background:linear-gradient(135deg,rgba(94,200,216,.14),rgba(224,164,88,.08));border:1px solid var(--acc2);border-radius:12px;padding:16px 18px;margin-bottom:18px}",
     "  .root{background:linear-gradient(135deg,rgba(163,45,45,.10),rgba(201,162,75,.08));border:1px solid var(--acc2);border-radius:12px;padding:16px 18px;margin-bottom:18px}",
     "root"),
    # --- a 链接 蓝->红 ---
    ("  a{color:var(--blue);text-decoration:none}", "  a{color:var(--acc);text-decoration:none}", "a"),
    # --- 内联变更盒子 暗字->浅底可见 ---
    ('  <div style="margin:16px 0;padding:14px 18px;border:1px solid #e0a458;border-radius:12px;background:rgba(224,164,88,.12);font-size:13.5px;line-height:1.75;color:#e6edf3">\n  <b style="color:#e0a458">概念变更 · 2026-07-30</b>　A 值「共济值」正式定名为「<b style="color:#5ec8d8">共济值</b>」。<br>',
     '  <div style="margin:16px 0;padding:14px 18px;border:1px solid #C9A24B;border-radius:12px;background:rgba(201,162,75,.12);font-size:13.5px;line-height:1.75;color:#1a1a2e">\n  <b style="color:#C9A24B">概念变更 · 2026-07-30</b>　A 值「共济值」正式定名为「<b style="color:#A32D2D">共济值</b>」。<br>',
     "inline-box"),
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
    with io.open(fp, "w", encoding="utf-8") as f:
        f.write(s)
    print("== %s ==" % fp)
    print("  " + "  ".join(report))
print("DONE")
