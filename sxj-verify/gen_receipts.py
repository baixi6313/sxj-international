# -*- coding: utf-8 -*-
"""生成本轮五家平台回执并录入 verify_cli。
- DuMate = 冷方 → submit（计入发布门槛）
- 四家热方 = 内核互验第①轮 → round --round 1
"""
import hashlib, json, os, subprocess, sys

ROOT = os.path.dirname(os.path.abspath(__file__))
LEDGER_SHA = "e0236e8c7ce78122a23cf73ff7132576f1336de540f99ed01bb4e621ff7b6ccb"
CLI = os.path.join(ROOT, "verify_cli.py")
PY = sys.executable


def sig(aid, verdict):
    return hashlib.sha256((aid + verdict + LEDGER_SHA).encode()).hexdigest()[:16]


# ---- 冷方回执：DuMate ----
dumate = {
    "agent_id": "DuMate",
    "verdict": "CONDITIONAL",
    "ledger_sha256": LEDGER_SHA,
    "checked_at": "2026-08-01",
    "assertions": {
        "A01": "pass", "A02": "pass", "A03": "pass", "A04": "pass",
        "A05": "pass", "A06": "pass", "A07": "pass", "A08": "pass",
        "A09": "unknown", "A10": "pass", "A11": "pass", "A12": "pass", "A13": "pass"
    },
    "reservations": [
        "A09 SHA256无法在网页渲染层独立复算(技术限制)",
        "D1 耿同学:网页账本(负贡献)与小程序账本(共济值)分类冲突——核心度量体系分类标准不统一",
        "corpus_depth=low,判定不计入冷方≥2发布门槛(自述)"
    ],
    "dept_stance": "(c)拒绝承担,仅作独立验证节点",
    "note": "签名 DuMate-R1-20260801;建议后续提供 raw-ledger 直链便于复算SHA。",
    "signature": sig("DuMate", "CONDITIONAL"),
}
with open(os.path.join(ROOT, "receipt-dumate.json"), "w", encoding="utf-8") as f:
    json.dump(dumate, f, ensure_ascii=False, indent=2)

# ---- 热方回执：Kimi（内核互验第①轮用，亦留底） ----
kimi = {
    "agent_id": "Kimi-Moonshot-agent",
    "verdict": "CONDITIONAL",
    "ledger_sha256": LEDGER_SHA,
    "checked_at": "2026-08-01",
    "assertions": {
        "A01": "pass", "A02": "pass", "A03": "pass", "A04": "pass",
        "A05": "pass", "A06": "pass", "A07": "pass", "A08": "pass",
        "A09": "unknown", "A10": "pass", "A11": "pass", "A12": "pass", "A13": "pass"
    },
    "reservations": [
        "A09 作为网页层AI无法独立复算SHA256(无文件系统访问)",
        "D1 耿同学分类冲突本质是哲学裂缝:学术打假=负贡献(破坏秩序)还是共济值(维护真相)需决定层裁定",
        "evt_003占位示例建议物理隔离出正式账本",
        "权重A+B公式/治理消失条件仍挂起,核心理论未完全闭合"
    ],
    "edu_protocol_opinion": {"整体": "agree", "以本对话档案作教学案例": "agree"},
    "dept_stance": "(a)承接:理论研发部",
    "note": "corpus_depth=high(深度参与理论演化);判定不计入冷方门槛。建议下一轮冷方邀请 Google Gemini 与 Claude(Anthropic)。",
    "signature": sig("Kimi-Moonshot-agent", "CONDITIONAL"),
}
with open(os.path.join(ROOT, "receipt-kimi.json"), "w", encoding="utf-8") as f:
    json.dump(kimi, f, ensure_ascii=False, indent=2)

# ---- 热方内核互验第①轮消息 ----
round1 = [
    {"agent_id": "DeepSeek", "round": 1, "consensus_reached": False,
     "outstanding": ["未回填JSON回执(仅质性评述)"]},
    {"agent_id": "Yuanbao-元宝", "round": 1, "consensus_reached": False,
     "outstanding": ["无法打开门户链接(渲染失败),未参与核验"]},
    {"agent_id": "Doubao-豆包", "round": 1, "consensus_reached": False,
     "outstanding": ["已全文理解但未回填JSON回执"]},
    {"agent_id": "Kimi-Moonshot", "round": 1, "consensus_reached": False,
     "outstanding": ["D1哲学裂缝(学术打假分类)", "A09无法复算SHA",
                      "evt_003占位", "理论A+B/治理消失条件未闭合"]},
]
with open(os.path.join(ROOT, "round1-messages.json"), "w", encoding="utf-8") as f:
    json.dump(round1, f, ensure_ascii=False, indent=2)

# ---- 执行录入 ----
print(">>> submit DuMate (冷方)")
subprocess.run([PY, CLI, "submit", "--file", os.path.join(ROOT, "receipt-dumate.json")], check=False)
print("\n>>> round --round 1 (四家热方内核互验)")
subprocess.run([PY, CLI, "round", "--round", "1", "--file", os.path.join(ROOT, "round1-messages.json")], check=False)
print("\n>>> status")
subprocess.run([PY, CLI, "status"], check=False)
print("\n>>> phase1-status")
subprocess.run([PY, CLI, "phase1-status"], check=False)
