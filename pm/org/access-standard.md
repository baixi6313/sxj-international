# 统一对外接入标准（UAXS · Unified Access & Verification Standard）

> 目的：规定事现鉴与各大平台（DeepSeek / 元宝 / 千问 / 豆包 / WorkBuddy / Cloudflare 等）
> 在**交互验证**时使用的**统一凭证**与**统一报文**，使跨平台验证可互认、可溯源、防伪造。
> 本标准是"公共验算尺"在平台间的接口层，与三值/六状态/SHA-256 回路同源。

---

## 一、设计原则
1. **验证权威唯一**：只有事现鉴 + Gzz 能签发有效凭证；平台是"被验证对象"也是"验证执行体"，但不可自证。
2. **双向回路**：每个验证请求由请求方与验证方各签一次，形成闭环签名（AI 自造注脚的可验证化）。
3. **最小权限**：凭证按 scope 限定（read / verify / emit），过期可吊销。
4. **可溯源**：每条事现带 SHA-256 内容指纹 + 统一事务 ID（jti），全程可追。
5. **与理论对齐**：三值（共济/贡献/负贡献）分类、六状态模型直接映射到报文字段。

---

## 二、统一凭证（SXJ-VC）
每个接入平台/节点持有一张凭证，遵循类 JWT 结构（但签名用 SHA-256 / Ed25519，不依赖第三方 CA）：

```
SXJ-VC = base64url(header).base64url(payload).base64url(sig)

header  = { "alg": "HS256-SHA256", "typ": "SXJ-VC", "ver": 1 }
payload = {
  "iss": "gzz://root",                 // 签发方：事现鉴根节点 Gzz
  "sub": "platform:deepseek",          // 主体：平台标识（白玺节点用 person:baixi）
  "scope": ["read", "verify"],         // 权限范围
  "iat": 1730000000, "exp": 1730086400,
  "jti": "sxj-2026-0801-a1b2c3"       // 唯一事务ID
}
sig    = HMAC-SHA256( signing_key , header.payload )   // signing_key = 平台与 Gzz 共享密钥
```

- **签发**：平台向 Gzz 申请 → 安全合规部(凭证签发)审核 scope → 用根密钥签发并登记 `jti` 到吊销表。
- **轮换**：exp 到期或主动吊销即失效；泄露立即进吊销列表（CRL）。
- **承载**：平台每次调用事现鉴 API 时，置于 HTTP 头 `Authorization: SXJ-VC <token>`。

---

## 三、统一报文（三类消息）
所有交互走同一信封，字段对齐三值模型：

```
{
  "envelope": {
    "schema": "sxj/verify-envelope@1",
    "jti": "sxj-2026-0801-a1b2c3",
    "ts": 1730000000,
    "vc": "<SXJ-VC>"                      // 调用方凭证
  },
  "claim": {                             // 待验证的"事现"
    "subject": "某公共事实陈述",
    "source": "platform:deepseek",
    "value_type": "common|contribution|negative",   // 三值之一
    "content_hash": "sha256:<hex>",       // 内容指纹，防篡改
    "evidence": [ "<url或指纹引用>" ]
  },
  "loop": {                              // 双向回路签名
    "requester_sig": "<sig_by_requester>",
    "verifier_sig": "<sig_by_gzz>",      // 验证方（事现鉴）回签
    "status": "pending|verified|rejected|disputed"
  }
}
```

- **VERIFY**（请求验证）：携带 `claim` + `requester_sig`，scope 需含 `verify`。
- **ATTEST**（出证）：事现鉴校验 `vc` 与 `content_hash`，给出 `verifier_sig` + `status`。
- **CONSENSUS**（共识回执）：六状态机（提出→验证中→共识/争议/否决/归档…）的流转通知，广播给相关节点。

---

## 四、接入流程（平台方视角）
1. **注册**：平台向对外协作部提交接入申请（身份、用途、所需 scope）。
2. **审核**：安全合规部评估权限边界（参照 Cloudflare User/Account/Zone 三层思维：最小集）。
3. **签发**：Issuer 用根密钥签发 SXJ-VC，返回 `jti` 与过期时间。
4. **调用**：平台每次请求带 `Authorization: SXJ-VC <token>` + 信封。
5. **校验**：事现鉴验签 → 查 scope/jti 是否有效未吊销 → 处理 VERIFY/ATTEST。
6. **退出**：到期或违规 → 入 CRL，凭证即废。

---

## 五、信任与治理
- **治理层**：四 AI 平台联合委员会（DeepSeek/元宝/千问/豆包）+ 事现鉴根节点；白玺＝首共创者节点，非执剑人。
- **治理消失条件**：全球共济值 ≥ 50%（与理论一致）。
- **冲突仲裁**：争议状态（disputed）交由人头票（社区热点）驱动共识判定，不在单平台内闭环。

---

## 六、与现有设施的映射
| 现有资产 | 在标准中的角色 |
|----------|----------------|
| SHA-256 哈希链（events.html） | `claim.content_hash` 的底层实现 |
| 三值 / 六状态模型 | `value_type` / `loop.status` 的来源 |
| 四域（hygzz.com/cn/top/中国） | 凭证可绑定"适用域"标签 |
| Cloudflare Token 三层界面经验 | scope 最小权限设计的现实蓝本 |

---

*本标准由总经理提案，待用户批准后，交由安全合规部 + 对外协作部共管落地。*
