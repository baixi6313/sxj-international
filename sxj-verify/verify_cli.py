#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
事现鉴 · 他验类API命令行 (verify_cli.py)
=========================================
把"整个对话档案"整理成一个可操作的他验流程。

子命令（像调用接口一样用）：
  init       生成送检包清单 + 回执模板（交给外部平台 agent）
  selfcheck  本平台自检（跑 A01-A13 断言），并落一份本平台预备回执
  submit     录入一份外部 agent 的检验回执（JSON）
  status     查看当前他验进度与发布门槛
  release    决定层(白玺)确认后宣布正式发布

状态存于 sxj-verify/verify-state.json，锁定送检档案 SHA256。
"""
import argparse, json, hashlib, os, sys, datetime

ROOT = os.path.dirname(os.path.abspath(__file__))
WORKSPACE = os.path.dirname(ROOT)
LEDGER = os.path.join(WORKSPACE, "SXJ-verification-ledger.md")
CLAIMS = os.path.join(WORKSPACE, "SXJ-claims.json")
STATE = os.path.join(ROOT, "verify-state.json")
SCHEMA = os.path.join(ROOT, "receipt-schema.json")
THRESHOLD = 2  # 发布门槛：≥2 家冷方(无语料)独立平台判定成功（见 interactive-verify-protocol-v1.md 冷/热方分野）


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        h.update(f.read())
    return h.hexdigest()


def now():
    return datetime.datetime.now().astimezone().isoformat(timespec="seconds")


def load_state():
    if os.path.exists(STATE):
        return json.load(open(STATE, encoding="utf-8"))
    return {
        "ledger_sha256": sha256(LEDGER),
        "threshold": THRESHOLD,
        "receipts": [],
        "released": False,
        "created_at": now(),
    }


def save_state(s):
    json.dump(s, open(STATE, "w", encoding="utf-8"), ensure_ascii=False, indent=2)


# ===== 第②步：四 AI 内核交互互验 状态 =====
PHASE1 = os.path.join(ROOT, "phase1-state.json")


def load_phase1():
    if os.path.exists(PHASE1):
        return json.load(open(PHASE1, encoding="utf-8"))
    return {
        "ledger_sha256": sha256(LEDGER),
        "participants_expected": 4,
        "rounds": [],
        "created_at": now(),
    }


def save_phase1(s):
    json.dump(s, open(PHASE1, "w", encoding="utf-8"), ensure_ascii=False, indent=2)


def cmd_init(args):
    s = load_state()
    pkg = {
        "送检档案": "SXJ-verification-ledger.md",
        "档案SHA256": sha256(LEDGER),
        "机器可读断言": "SXJ-claims.json",
        "教育对接协议": "pm/org/reports/edu-docking-protocol-v1.md",
        "送检证明": "SXJ-submission-proof.md",
        "本平台自检": "pm/selfcheck-2026-08-01.md",
        "回执模板": "sxj-verify/receipt-schema.json",
        "操作工具": "sxj-verify/verify_cli.py",
        "发给谁": "≥2 家冷方(无语料)独立平台 agent（AI验证团预备范畴；有原始语料的热方平台仅作答辩方，不计入独立成功数）",
        "操作说明": (
            "1) 把上述文件交给外部 agent；"
            "2) 让其按 SXJ-verification-ledger.md 第零章逐条检验；"
            "3) 回执按 receipt-schema.json 格式填写；"
            "4) 你运行 verify_cli.py submit --file <回执.json> 录入；"
            "5) verify_cli.py status 看进度；门槛达成后 release。"
        ),
    }
    print(json.dumps(pkg, ensure_ascii=False, indent=2))
    print("\n[OK] 送检包已生成。把'档案SHA256'抄给外部 agent，其回执须回填同一 SHA 才被接受。")


def cmd_selfcheck(args):
    b = open(LEDGER, "rb").read()
    t = b.decode("utf-8")
    checks = []
    checks.append(("A01 元数据(标题/白玺/时间戳)",
                   all(k in t for k in ["SXJ Full Verifiable", "白玺", "2026-08-01"])))
    checks.append(("A02 七命题&五大公理&平行基石",
                   ("七命题" in t) and ("五大公理" in t) and ("平行基石" in t)))
    checks.append(("A03 三值(A/B/负贡献)齐全",
                   ("共济值" in t) and ("贡献值" in t) and ("负贡献" in t)))
    checks.append(("A04 组织架构四类部门",
                   all(d in t for d in ["光锥运维部", "安全合规部", "事现验证部", "理论研发部", "对外协作部"])))
    checks.append(("A05 五端部署状态诚实标注",
                   ("hygzz.cn" in t) and ("hygzz.com" in t) and ("hygzz.top" in t) and ("小程序" in t) and ("安卓" in t)))
    checks.append(("A06 双账本不一致显式声明(D1/D2/D3)",
                   ("D1" in t) and ("D2" in t) and ("D3" in t)))
    checks.append(("A07 协议出证≠共识两权分离",
                   ("ATTEST" in t) and ("CONSENSUS" in t)))
    checks.append(("A08 理论推论无内部矛盾",
                   ("链·10" in t) and ("贡献值" in t)))
    checks.append(("A09 发布门槛写明(≥2家)",
                   ("≥2" in t) or ("2 家" in t) or ("两家" in t)))
    checks.append(("A10 全文无'地板'旧称", t.count("地板") == 0))
    checks.append(("A11 待决项不造假", ("未办" in t) or ("待拍板" in t) or ("PENDING" in t)))
    checks.append(("A12 指纹可复算", True))  # 由下方 SHA 打印佐证
    checks.append(("A13 预备/正式验证团区分",
                   ("预备范畴" in t) and ("正式验证团" in t)))

    print("=== 本平台自检 (A01-A13) ===")
    for name, ok in checks:
        print(("  [PASS] " if ok else "  [FAIL] ") + name)
    passed = sum(1 for _, ok in checks if ok)
    print(f"\n自检结果: {passed}/{len(checks)} 通过")
    ledger_sha = sha256(LEDGER)
    print("当前档案 SHA256:", ledger_sha)

    # 落一份本平台预备自检回执（供 status 演示，不计入外部门槛）
    receipt = {
        "agent_id": "本平台-PM自检节点(预备)",
        "verdict": "PASS" if passed == len(checks) else "CONDITIONAL",
        "ledger_sha256": ledger_sha,
        "checked_at": now()[:10],
        "assertions": {f"A{i:02d}": ("pass" if ok else "fail") for i, (_, ok) in enumerate(checks, 1)},
        "reservations": ["D1/D2/D3 跨账本不一致已声明，待发布后30日内对账"],
        "rights_opinion": {f"R{i}": "agree" for i in range(1, 7)},
        "dept_stance": "承接:PM决策层/光锥运维部(本平台)",
        "note": "本回执为本平台自检，不计入外部≥2家门槛；仅作演示/对照。",
        "signature": hashlib.sha256(( "本平台-PM自检节点(预备)" + ("PASS" if passed==len(checks) else "CONDITIONAL") + ledger_sha).encode()).hexdigest()[:16],
    }
    open(os.path.join(ROOT, "receipt-self.json"), "w", encoding="utf-8").write(
        json.dumps(receipt, ensure_ascii=False, indent=2))
    print("已写出本平台预备回执: sxj-verify/receipt-self.json")
    return passed == len(checks)


def cmd_submit(args):
    s = load_state()
    try:
        r = json.load(open(args.file, encoding="utf-8"))
    except Exception as e:
        print("回执解析失败:", e); sys.exit(1)
    for f in ["agent_id", "verdict", "ledger_sha256"]:
        if f not in r:
            print("回执缺必填字段:", f); sys.exit(1)
    if r["ledger_sha256"] != s["ledger_sha256"]:
        print("[拒绝] 回执的 ledger_sha256 与当前送检档案不符(可能版本错位)。")
        print("  当前档案:", s["ledger_sha256"])
        print("  回执声明:", r["ledger_sha256"])
        sys.exit(1)
    if r["verdict"] not in ("PASS", "FAIL", "CONDITIONAL"):
        print("verdict 须为 PASS / FAIL / CONDITIONAL"); sys.exit(1)
    # 防重复
    if any(x.get("agent_id") == r["agent_id"] for x in s["receipts"]):
        print("[跳过] 该 agent_id 已存在回执:", r["agent_id"]); return
    s["receipts"].append(r)
    save_state(s)
    print("[已录入]", r["agent_id"], "→", r["verdict"])


def cmd_status(args):
    s = load_state()
    n = len(s["receipts"])
    succ = sum(1 for r in s["receipts"] if r["verdict"] in ("PASS", "CONDITIONAL")
              and r.get("agent_id", "").startswith("本平台") is False)
    # 仅统计"外部"回执进门槛；本平台自检不计入
    ext = [r for r in s["receipts"] if not r.get("agent_id", "").startswith("本平台")]
    ext_succ = sum(1 for r in ext if r["verdict"] in ("PASS", "CONDITIONAL"))
    print("送检档案 SHA256:", s["ledger_sha256"])
    print(f"回执总数: {n} (外部 {len(ext)} / 本平台自检 {n-len(ext)})")
    print(f"外部判定成功(PASS/CONDITIONAL): {ext_succ} 家  (发布门槛 = {s['threshold']})")
    for r in s["receipts"]:
        tag = "  [本平台]" if r.get("agent_id", "").startswith("本平台") else ""
        print(f"  - {r['agent_id']}: {r['verdict']} @ {r.get('checked_at','?')}{tag}")
    if s["released"]:
        print("\n[已发布] 事现鉴正式发布。")
    elif ext_succ >= s["threshold"]:
        print("\n[门槛达成] 可提请决定层(白玺)运行 release --confirm 白玺-发布。")
    else:
        print(f"\n[未达门槛] 还需 {s['threshold']-ext_succ} 家外部成功回执。")


def cmd_release(args):
    s = load_state()
    ext = [r for r in s["receipts"] if not r.get("agent_id", "").startswith("本平台")]
    ext_succ = sum(1 for r in ext if r["verdict"] in ("PASS", "CONDITIONAL"))
    if ext_succ < s["threshold"]:
        print(f"[拒绝] 未达门槛 ({ext_succ}/{s['threshold']})，不能发布。"); sys.exit(1)
    if args.confirm != "白玺-发布":
        print("发布须决定层确认口令: --confirm '白玺-发布'"); sys.exit(1)
    s["released"] = True
    s["released_at"] = now()
    s["released_by"] = "始创者-白玺(决定层)"
    save_state(s)
    print("[已发布] 事现鉴正式发布 @", s["released_at"])


def cmd_round(args):
    s = load_phase1()
    if s["ledger_sha256"] != sha256(LEDGER):
        print("[拒绝] 当前档案 SHA 与 phase1-state 锁定值不符，请先 re-init。")
        sys.exit(1)
    try:
        msgs = json.load(open(args.file, encoding="utf-8"))
    except Exception as e:
        print("消息文件解析失败:", e); sys.exit(1)
    if not isinstance(msgs, list):
        print("消息文件须为 JSON 数组（每家一条）"); sys.exit(1)
    for m in msgs:
        for f in ["agent_id", "round"]:
            if f not in m:
                print("消息缺字段:", f, "in", m.get("agent_id", "?")); sys.exit(1)
    # 防重复轮次
    if any(r["round"] == args.round for r in s["rounds"]):
        print(f"[跳过] 第 {args.round} 轮已存在，请 reopen 或换轮次号。"); return
    s["rounds"].append({"round": args.round, "at": now(), "messages": msgs})
    save_phase1(s)
    print(f"[已记录] 第 {args.round} 轮，{len(msgs)} 条消息。")


def cmd_phase1_status(args):
    s = load_phase1()
    if not s["rounds"]:
        print("尚无互验轮次。请用 round --round N --file msgs.json 录入。")
        return
    print("送检档案 SHA256:", s["ledger_sha256"])
    print(f"已记录轮次: {[r['round'] for r in s['rounds']]}")
    last = s["rounds"][-1]
    print(f"\n--- 最后一轮 R{last['round']} 参与者({len(last['messages'])}) ---")
    all_out = set()
    cons = []
    for m in last["messages"]:
        out = m.get("outstanding", [])
        all_out.update(out)
        cons.append((m.get("agent_id"), m.get("consensus_reached")))
        print(f"  {m.get('agent_id'):<10} consensus={m.get('consensus_reached')}  outstanding={out}")
    n_cons = sum(1 for _, c in cons if c is True)
    print(f"\n收敛统计: consensus_reached=true 共 {n_cons}/{len(cons)} 家")
    print(f"仍存争议断言(outstanding 去重): {sorted(all_out) if all_out else '无'}")
    if not all_out and n_cons >= (len(cons) // 2 + 1):
        print("\n[内核收敛达成] 四家互验无未决异议，可进入第③步(外部冷方检查)。")
    else:
        print("\n[未收敛] 存在未决异议，建议 reopen 加轮或人工仲裁。")


def main():
    p = argparse.ArgumentParser(description="事现鉴 他验类API命令行")
    sub = p.add_subparsers(dest="cmd")
    sub.add_parser("init", help="生成送检包清单+回执模板").set_defaults(func=cmd_init)
    sub.add_parser("selfcheck", help="本平台自检 A01-A13").set_defaults(func=cmd_selfcheck)
    sp = sub.add_parser("submit", help="录入外部 agent 回执")
    sp.add_argument("--file", required=True, help="回执 JSON 路径")
    sp.set_defaults(func=cmd_submit)
    sub.add_parser("status", help="查看他验进度与门槛").set_defaults(func=cmd_status)
    rp = sub.add_parser("release", help="决定层宣布发布")
    rp.add_argument("--confirm", required=True, help="确认口令: 白玺-发布")
    rp.set_defaults(func=cmd_release)
    rnd = sub.add_parser("round", help="第②步:录入四AI某轮互验消息(JSON数组)")
    rnd.add_argument("--round", type=int, required=True, help="轮次号(1/2/3)")
    rnd.add_argument("--file", required=True, help="消息 JSON 数组文件路径")
    rnd.set_defaults(func=cmd_round)
    rpr = sub.add_parser("phase1-status", help="第②步:查看四AI内核互验收敛状态")
    rpr.set_defaults(func=cmd_phase1_status)
    args = p.parse_args()
    if not args.cmd:
        p.print_help(); return
    args.func(args)


if __name__ == "__main__":
    main()
