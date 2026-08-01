import os, re, shutil

WS = "C:/Users/Administrator/WorkBuddy/2026-07-24-23-26-27"
OLD = "C:/Users/Administrator/WorkBuddy/2026-07-22-08-14-20/hygzz_cn_domestic"
snippet = open(os.path.join(WS, "_corpus_table_snippet.html"), encoding='utf-8').read()

# inject into both knowledge_tree.html files (before </body>)
for f in [os.path.join(WS, "knowledge_tree.html"), os.path.join(OLD, "knowledge_tree.html")]:
    if not os.path.exists(f):
        print("MISS", f); continue
    s = open(f, encoding='utf-8').read()
    if 'corpus-timeline' in s:
        print("SKIP(injected)", os.path.relpath(f, WS)); continue
    if '</body>' in s:
        s = s.replace('</body>', snippet + '</body>', 1)
    else:
        s = s + snippet
    open(f, 'w', encoding='utf-8').write(s)
    print("INJECTED", os.path.relpath(f, WS))

# archive raw corpus + theory + old tree versions
arch = os.path.join(WS, "_archive")
os.makedirs(arch, exist_ok=True)
to_archive = [
    "deepseek_dialogues_index.html","yuanbao_corpus_index.html","qianwen_corpus_index.html",
    "doubao_corpus_index.html","zhihu_corpus_index.html","weibo_corpus_index.html",
    "theory_deepseek.html","theory_yuanbao.html","theory_qianwen.html","theory_doubao.html",
    "knowledge_tree_v2.html","knowledge_tree_v3.html","knowledge_tree_v4.html",
]
moved = []
for fn in to_archive:
    src = os.path.join(WS, fn)
    if os.path.exists(src):
        shutil.move(src, os.path.join(arch, fn))
        moved.append(fn)
print("ARCHIVED", len(moved), moved)

# also delete live v4 (orphan) to keep single tree on hygzz.cn
live_v4 = os.path.join(OLD, "knowledge_tree_v4.html")
if os.path.exists(live_v4):
    os.remove(live_v4)
    print("DELETED live", os.path.relpath(live_v4, OLD))

# archive readme
readme = os.path.join(arch, "README.md")
open(readme, 'w', encoding='utf-8').write(
    "# 归档说明（历史数据）\n\n"
    "本目录存放事现鉴 / 共创论项目的**历史语料与旧版知识树**，于 2026-07-30 整合时归档。\n\n"
    "## 整合结果\n"
    "- 四平台语料（DeepSeek / 元宝 / 千问 / 豆包 / 微博 / 知乎）已整合为**唯一一张「语料时间线（时间/内容）」表**，位于 `knowledge_tree.html#corpus-timeline`。\n"
    "- 原始分平台网页不再单独提供，仅作史料留存于此。\n\n"
    "## 文件清单\n" + "\n".join(f"- {fn}" for fn in moved) + "\n"
)
print("archived readme written")
