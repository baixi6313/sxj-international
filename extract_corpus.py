import re, os, shutil, datetime

WS = "C:/Users/Administrator/WorkBuddy/2026-07-24-23-26-27"
weibo = os.path.join(WS, "weibo_corpus_index.html")
s = open(weibo, encoding='utf-8').read()

# extract weibo timeline rows: date / title / url
pat = re.compile(r'<div class="ev">.*?<div class="d">([^<]+)</div>.*?<div class="ti">([^<]+)</div>.*?<a href="([^"]+)"', re.S)
rows = []
for m in pat.finditer(s):
    d, t, u = m.group(1).strip(), m.group(2).strip(), m.group(3).strip()
    rows.append((d, t, u))
rows.sort(key=lambda r: r[0])
print("weibo timeline rows:", len(rows))

# count entries in each raw corpus file
def count(fname, marker):
    p = os.path.join(WS, fname)
    if not os.path.exists(p): return 0
    return len(re.findall(marker, open(p, encoding='utf-8').read()))
counts = {
    "DeepSeek 对话索引 (deepseek_dialogues_index.html)": max(0, count("deepseek_dialogues_index.html", r'<tr') - 1),
    "元宝语料 (yuanbao_corpus_index.html)": count("yuanbao_corpus_index.html", r'<td class="t">'),
    "千问语料 (qianwen_corpus_index.html)": count("qianwen_corpus_index.html", r'<td class="t">'),
    "豆包语料 (doubao_corpus_index.html)": count("doubao_corpus_index.html", r'<td class="t">'),
    "知乎语料 (zhihu_corpus_index.html)": count("zhihu_corpus_index.html", r'<td class="t">'),
    "微博语料 (weibo_corpus_index.html)": count("weibo_corpus_index.html", r'<div class="ev">'),
}
print("counts:", counts)

# build consolidated table HTML
trs = "\n".join(
    f'      <tr><td style="white-space:nowrap">{d}</td><td style="max-width:140px">{t}</td>'
    f'<td><a href="{u}" target="_blank" rel="noopener" style="font-size:11px;word-break:break-all">{u}</a></td></tr>'
    for d, t, u in rows
)
archive_li = "\n".join(f"      <li>{k}：约 {v} 条 · 已存 _archive/</li>" for k, v in counts.items())

html = f'''<!-- ===== 语料时间线（四平台整合 · 单一时间/内容表） ===== -->
<section class="content-section" id="corpus-timeline" style="margin-top:30px">
  <div class="section-icon">🗂️</div>
  <div class="section-title">语料时间线 — DeepSeek / 元宝 / 千问 / 豆包 整合</div>
  <div class="section-subtitle">本表为四平台语料的<strong>唯一整合视图（时间 / 内容）</strong>。原始分平台网页已归档至 <code>_archive/</code>，不再单独提供。⚠️ 以下语料均为白玺与 AI 对话的<strong>推演记录</strong>，非既成事实，附时间戳可验证。</div>
  <div class="section-body">
    <div style="overflow-x:auto">
    <table style="width:100%;border-collapse:collapse;font-size:13px">
      <thead><tr style="background:#f3e9d8;text-align:left">
        <th style="padding:6px 8px;border:1px solid #e3d6c2">时间</th>
        <th style="padding:6px 8px;border:1px solid #e3d6c2">内容（跨平台里程碑）</th>
        <th style="padding:6px 8px;border:1px solid #e3d6c2">原始链接</th>
      </tr></thead>
      <tbody>
{trs}
      </tbody>
    </table>
    </div>
    <p style="font-size:12.5px;color:#8a7d68;margin-top:12px"><b>原始分平台语料（已存档，仅作史料）：</b></p>
    <ul style="font-size:12.5px;color:#8a7d68">
{archive_li}
    </ul>
  </div>
</section>
'''

open(os.path.join(WS, "_corpus_table_snippet.html"), "w", encoding='utf-8').write(html)
print("snippet written, bytes:", len(html))
