import os, re

BANNER_CSS = ('<style>.beta-banner{background:linear-gradient(90deg,#fff3cd,#ffe8a3);'
 'border-bottom:2px solid #c9a24b;color:#5a4f3e;font-size:13px;line-height:1.55;'
 'padding:8px 14px;z-index:9999;font-family:inherit}'
 '.beta-banner strong{color:#a23b32;margin-right:8px;letter-spacing:1px}'
 '.beta-banner .prov{display:block;margin-top:3px;color:#7a6a4a;font-size:12px}</style>\n')

BANNER_DIV = ('<div class="beta-banner"><strong>⚠️ 测试版 BETA</strong>'
 '<span>事现鉴 / 共创论 · 验证与推演工具（非实地实施产品）· 数据更新 2026-07-30 11:30</span>'
 '<span class="prov">站内所记「事现」中，仅「南京博物院文物流失」「耿同学学术打假」「小红书前员工期权」三件为网络公开、可独立核实的真实事件；其余所有事现均为白玺与 AI 共同演绎生成（附时间戳可验证），仅供框架推演，非既成事实。</span></div>\n')

WS = "C:/Users/Administrator/WorkBuddy/2026-07-24-23-26-27"
files = ["knowledge_tree.html","concept_tree.html","whitepaper.html","qualitative_analysis.html",
         "critical_synthesis_report.html","framework_glossary.html","ai_understanding.html",
         "dialogue_record_sxj.html","article_mapping_analysis.html","events.html",
         "hygzz_top/index.html"]
for fn in files:
    f = os.path.join(WS, fn)
    if not os.path.exists(f):
        print("MISS", fn); continue
    s = open(f, encoding='utf-8').read()
    if 'beta-banner' in s:
        print("SKIP(has)", fn); continue
    if '</head>' in s:
        s = s.replace('</head>', BANNER_CSS + '</head>', 1)
    else:
        s = BANNER_CSS + s
    m = re.search(r'<body[^>]*>', s)
    if m:
        s = s[:m.end()] + '\n' + BANNER_DIV + s[m.end():]
    else:
        s = BANNER_DIV + s
    open(f, 'w', encoding='utf-8').write(s)
    print("OK", fn)
