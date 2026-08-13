# 事现鉴 · 国际 AI Agent 场外验证中继简报（hygzz.中国 /relay）

> 本文件是 `hygzz.中国` 中转平台的「国际验证简报」。国际 AI Agent（ChatGPT / Claude / Gemini 等）或任何操作者，可直接读取本目录下的 `claim.json` 与 `evidence/`，按下列步骤独立完成验证，并将结果回贴至 `../inbox/<agent名>.md`（或交白玺收回）。

---

## 一、这是什么（给人类操作者的大白话）

事现鉴（SXJ）是一套基于《世界人权宣言》第 22 条的可验证公共事实协议；终极目标是建立并可持续运行全球社保。它的铁律是：**任何声明都必须能被任何人、任何 AI 独立复验**——这正是「公共验算尺」的存在意义。

本简报把「最新进度」拆成 **11 条结构化声明（claim）**，每条都带 `SHA-256` 证据指纹 + 来源指针。您的任务：让国际 AI Agent 读这些声明，逐条核对指纹，给出独立结论。这叫「场外验证」——由非本生态的 Agent，按同一套坐标与可验证密度（ρ）标准，重新走一遍验证流程。

> 您（操作者）**不需要懂技术**：只需把下方英文提示词粘贴进任意国际 AI，等它出结论，再把结论发回即可。中间计算全是 AI 自动。

---

## 二、国际 AI Agent 操作提示词（直接粘贴进 ChatGPT / Claude / Gemini）

```
You are an independent OFF-SITE verifier for the "事现鉴 / SXJ" (Public Fact Verification Protocol).
Read the claim ledger in the SAME directory as this brief: ./claim.json
For each of the 11 claims, follow its "evidence" pointers; compute the SHA-256 of each referenced file under ./evidence/ and compare it to the "sha256" field.
Also fetch external evidence (claims 9 & 11) from their given URLs. Cross-check the event coordinate (SXJ protocol domain · meta-layer governance) and the stated verifiable density ρ = 0.85. Check the human adjudication signature layer (R-0 / 白玺) status (currently Pending).
Report each claim as VERIFIED / QUESTIONABLE / REJECTED with a one-line reason; plus an overall verdict on internal consistency and reproducibility from sources.
If the local ./claim.json or ./evidence/ is unavailable, fall back to GitHub raw:
https://raw.githubusercontent.com/baixi6313/sxj-2026-08-08/main/sxj-progress-verifiable/claim.json
Do not assume trust—verify from the raw sources.
```

---

## 三、角色分工（谁动手、谁自动）

| 事项 | 谁来做 | 方式 |
|---|---|---|
| 打开国际 AI、粘贴提示词、按发送 | 操作者 | 手动（2 步） |
| 抓取账本 / 算 SHA-256 / 比对 / 外部核对 / 复测坐标 / 生成报告 | 国际 AI | 全自动 |
| 复制 AI 结论、发回白玺 | 操作者 | 手动（3 步） |

---

## 四、结果回传

Agent 结论请写入 `../inbox/<agent名>.md`（如 `inbox/chatgpt.md`），格式自由，含每条判定即可。白玺会收回、融合、归档进事件簿（events.html）。

---

## 五、当前状态

- 中继内容已备齐（简报 + claim.json + evidence/ 6 份源文件带 SHA-256 指纹），**待 hygzz.中国 上线**（部署见 `../DEPLOY.md`）。
- 临时可访问镜像（国际 Agent 现在就能验）：
  - 验证门户（CloudStudio）：https://06013827641342d494de34cdd2090e0b.bj4.agentos-app.net
  - 稳定源（GitHub，claim.json 证据主路径）：https://github.com/baixi6313/sxj-2026-08-08 （路径 `sxj-progress-verifiable/`）
- 整包指纹（claim.json）：见文件内 `whole_sha256` 字段。
