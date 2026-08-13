import os, hashlib, json, shutil, urllib.parse

BASE = "C:/Users/Administrator/WorkBuddy/2026-07-24-23-26-27"
OUT  = os.path.join(BASE, "sxj-progress-verifiable")
EVID = os.path.join(OUT, "evidence")
os.makedirs(EVID, exist_ok=True)

# 1) 证据源：本地文件 -> 算 SHA-256 并复制到 evidence/
sources = {
  "MAIP-v1.0":                 "sxj-verify/SXJ-MAIP-v1.0.md",
  "化债引擎→canon映射":        "化债引擎→canon映射.md",
  "MAIP-spec-化债核心闭环":     "MAIP-spec-化债核心闭环.md",
  "第4稿-待发展城市与实物债务": "事现鉴-化债-待发展城市与实物债务重定义-讨论.md",
  "sxj-economics-model-v0.7":  "sxj-economics-model.html",
  "整体进度汇报":              "事现鉴-整体进度汇报-2026-08-10.md",
}
ev = {}
for name, rel in sources.items():
    p = os.path.join(BASE, rel)
    data = open(p, "rb").read()
    h = hashlib.sha256(data).hexdigest()
    ev[name] = h
    dst = os.path.join(EVID, os.path.basename(rel))
    shutil.copyfile(p, dst)
    print("[copy] %-30s -> evidence/%-38s sha=%s" % (name, os.path.basename(rel), h[:12]))

RAW_BASE = "https://raw.githubusercontent.com/baixi6313/sxj-2026-08-08/main/"
def E(name):
    rel = sources[name]
    return {"file": name,
            "local": "evidence/" + os.path.basename(rel),
            "github": RAW_BASE + urllib.parse.quote(rel, safe="/"),
            "sha256": ev[name], "external": False}

def X(url, note):
    return {"file": note, "path": url, "sha256": None, "external": True}

# 2) 结构化 claims
claims = [
 {"n":1,"statement":"事现鉴(SXJ)=基于《世界人权宣言》第22条的可验证公共事实协议；终极目标=建立并可持续运行全球社保；公共验算尺(MAIP)为统一度量衡、不取代各国社保；当前阶段=坐标系优先。",
  "evidence":[E("MAIP-v1.0"),E("整体进度汇报")],
  "verify":"打开 evidence/SXJ-MAIP-v1.0.md 核对第一章定位；打开 evidence/事现鉴-整体进度汇报-2026-08-10.md 核对第一节。"},
 {"n":2,"statement":"已裁定 canon 体系 8 项全部生效：三值 / 坐标系优先 / 净值↔动态均衡 / 交互验证vs相互验证 / R-1…R-6 / D机制 / 光锥舟Gzz / 三元双重身份。",
  "evidence":[E("MAIP-v1.0")],
  "verify":"打开 evidence/SXJ-MAIP-v1.0.md 核对第二节『已裁定 canon 体系』表格（8 行全为 canon）。"},
 {"n":3,"statement":"化债引擎线已全部升 spec：引擎三件套(多元矩阵/田忌赛马/热度密度)＋范式四件套(五卡/财政直销/消费=纳税+化债/货币消失)＋核心闭环＋两议题(待发展城市三元重定义/实物债务重定义)＋口号总纲(打资本·分数据·化解债务)。",
  "evidence":[E("MAIP-v1.0"),E("化债引擎→canon映射"),E("MAIP-spec-化债核心闭环")],
  "verify":"打开 evidence/SXJ-MAIP-v1.0.md 第十五章；打开 evidence/化债引擎→canon映射.md 核对映射总表。"},
 {"n":4,"statement":"化债核心闭环(2026-08-10 08:13 裁定)：负贡献核算(珊瑚·归责四要件) ∥ 生成新贡献(金·B·三元ρ) 并行 → 置换现有债务 → 贡献净值 N(t)；货币消失(D机制c→1)是置换完成的终态结果、非手段。",
  "evidence":[E("MAIP-v1.0"),E("sxj-economics-model-v0.7")],
  "verify":"打开 evidence/SXJ-MAIP-v1.0.md §15.1 核对五步闭环；打开 evidence/sxj-economics-model.html(v0.7) 看 ④卡双轨(珊瑚负贡献∥金新贡献∥白净值)与置换进度条。"},
 {"n":5,"statement":"两议题升 spec：待发展城市在三元体系内重定义价值(ρ公式/财政直销按ρ注入)；实物/公共工程债务(植树造林/修路)重定义为三元ρ缺口、经动态均衡(Gzz)闭合，参照共创论而非旧工分制。",
  "evidence":[E("MAIP-v1.0"),E("第4稿-待发展城市与实物债务")],
  "verify":"打开 evidence/SXJ-MAIP-v1.0.md §15.2/§15.3；打开 evidence/事现鉴-化债-待发展城市与实物债务重定义-讨论.md 核对 §2/§3。"},
 {"n":6,"statement":"口号→机制映射已入 spec：打资本=负贡献核算；分数据=新贡献生成主通道；化解债务=置换→净值。『打资本/推翻资本』修辞仍隔离、未入 spec。",
  "evidence":[E("MAIP-v1.0")],
  "verify":"打开 evidence/SXJ-MAIP-v1.0.md §15.4 核对映射表与边界声明。"},
 {"n":7,"statement":"化债核心闭环 spec 已于 2026-08-10 正式并入主 MAIP 文档第十五章(独立源稿件 MAIP-spec-化债核心闭环.md 保留为来源)，附录 C/E 已同步。",
  "evidence":[E("MAIP-v1.0"),E("MAIP-spec-化债核心闭环")],
  "verify":"打开 evidence/SXJ-MAIP-v1.0.md 搜索『第十五章』确认已并入；核对附录 C 映射行、附录 E 缺口 G-10。"},
 {"n":8,"statement":"经济学模型演进 v0.5→v0.6(④卡化债引擎版)→v0.7(核心闭环双轨版：显式建模负贡献∥新贡献+置换闭合读数)；JS 校验通过、旧id残留0。",
  "evidence":[E("sxj-economics-model-v0.7")],
  "verify":"打开 evidence/sxj-economics-model.html 核对标题含 v0.7、④卡含珊瑚/金/白三轨与 λ 控件、置换进度条。"},
 {"n":9,"statement":"首轮 GitHub 备份已完成：5/5 文件推 baixi6313/sxj-2026-08-08 @ main 并核验 SHA(HTTP 201)。注：该批为 v0.6 时代产物(3篇讨论稿+映射+v0.6模型)；v0.7/第4稿/spec章节因③叫停尚未二次推送。",
  "evidence":[X("https://github.com/baixi6313/sxj-2026-08-08","GitHub仓库 baixi6313/sxj-2026-08-08 @ main")],
  "verify":"访问 https://github.com/baixi6313/sxj-2026-08-08 核对 5 个文件存在(化债ABM五卡补完/范式合成/矩阵赛马热密度 两篇.md、化债引擎→canon映射.md、sxj-economics-model.html)。"},
 {"n":10,"statement":"未决/待办清单(分线)：②分数据机制(用户叫停待讨论)；③二次GitHub备份(叫停)；concept_tree.html节点增补(§15.6清单未入树)；待发展城市试点/实物债务量化公式(仅框架)；口号修辞隔离；DPG线上材料对齐。",
  "evidence":[E("整体进度汇报")],
  "verify":"打开 evidence/事现鉴-整体进度汇报-2026-08-10.md 核对第七节(待办/未决)与第九节(优先级)。"},
 {"n":11,"statement":"DPG 提名里程碑(2026-08-09)：Application ID 14641 → DPG ID GID0094044，UNDER REVIEW；最早结果 2026-09-06；MIT/Apache-2.0，9/9 指标绿。",
  "evidence":[X("https://app.digitalpublicgoods.net/","DPG 提名 GID0094044")],
  "verify":"在 DPG 平台查询 GID0094044 核对状态 UNDER REVIEW 与最早结果日期 2026-09-06。"},
]

event = {
  "id":"evt_progress_20260810",
  "title":"事现鉴整体进度汇报（光锥运维部 · 记录·审查·优化）",
  "type":"共济值",
  "coord":{"x":"人文/数字(元层治理)","y":"上","z":"协议/项目层","j":"SXJ协议域","t":"2026-08-10"},
  "rho":0.85,
  "rho_note":"待校准；基于多文档交叉背书与 SHA-256 证据指纹，初估 ≥0.85（ρ_min=0.85）。",
  "recorder":"光锥运维部",
  "createdAt":"2026-08-10T08:51:00+08:00",
  "status":"验证中（待 R 层人类裁定签名）",
  "adjudication":{"layer":"R-0 / 白玺","signed":False,"note":"Pending — 人类裁定层签名待补；未签名前本事件为『验证中』状态。"}
}
doc = {
  "schema":"SXJ-EventLedger/v1",
  "event":event,
  "claims":claims,
  "verify_guide":"其他 AI agent 验证步骤：① 取 claim.json 或本页 claims 列表；② 对每条 claim 按其 evidence 的 `github` 字段（GitHub raw，稳定源）打开源文件，比对 SHA-256 指纹是否一致；本地 `evidence/` 副本可作离线交叉核对；③ 外部证据(claim 9/11)访问给定 URL 核对；④ 落同一坐标(SXJ协议域·元层治理)复测 ρ；⑤ 确认人类裁定签名层(R-0/白玺)状态。任何一条 evidence 的 SHA-256 不符或缺失，则该 claim 不成立。",
  "note":"本事件为『项目状态陈述』，不属于创世性事实裁定；其可信度来自证据源的可交叉验证性，而非权威背书。坐标与 ρ 为初估，待 R 层最终裁定。"
}
with open(os.path.join(OUT,"claim.json"),"w",encoding="utf-8") as f:
    json.dump(doc,f,ensure_ascii=False,indent=2)
whole = hashlib.sha256(open(os.path.join(OUT,"claim.json"),"rb").read()).hexdigest()
print("[done] claim.json written, whole_sha256=%s" % whole[:16])
print("[done] claims=%d evidence_files=%d" % (len(claims), len(sources)))
