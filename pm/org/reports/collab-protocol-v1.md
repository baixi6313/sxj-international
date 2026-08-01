# 对外交互统一协议 v1（SXJ-XIP/1 · Unified External Interaction Protocol）

> 出品：对外协作部（SXJ-CO）
> 上位标准：`pm/org/access-standard.md`（UAXS 统一对外接入标准）
> 关系：本文是 UAXS 的**可执行落地规范**，不修改 UAXS；凡 UAXS 为"原则"，本文给"字段、算法、时序、错误码"。
> 状态：v1 草案，待 GM 汇总 → 用户批准 → 与安全合规部（SXJ-SEC）会签生效。
> 协议标识：`SXJ-XIP/1`；信封 schema：`sxj/verify-envelope@1`（与 UAXS 保持同名兼容）

---

## 〇、版本与合规声明

| 项 | 值 |
|----|-----|
| 协议名 | SXJ-XIP（事现鉴对外交互协议） |
| 版本 | 1.0（v1） |
| 前置依赖 | UAXS（access-standard.md）、三值模型、六状态机、SHA-256 哈希链 |
| 关键词约定 | **必须/MUST**、**应当/SHOULD**、**可以/MAY**，语义同 RFC 2119 |
| 字符编码 | 全链路 UTF-8（NFC 规范化） |
| 时间 | Unix 秒级时间戳（UTC），不接受本地时区表述 |
| 传输 | HTTPS/TLS 1.2+，禁止明文 HTTP |

**与 UAXS 的一处显式升级（需会签确认）**：UAXS §二示例中 `alg = HS256-SHA256`（HMAC 共享密钥）。
v1 **必须**改用 **Ed25519 非对称签名**。理由：共享密钥意味着平台持有可伪造 Gzz 签名的材料，直接违背 UAXS §一"平台不可自证"与"验证权威唯一"。
HMAC 模式在 v1 中仅保留为 `compat-hs256` 过渡档，**仅限联调环境**，上线环境**必须**关闭。

---

## 一、协议定位与适用范围

### 1.1 定位
事现鉴（SXJ）对外一切"验证类交互"的**唯一语义层**。任何外部平台、节点、第三方验证方与事现鉴之间的验证请求、出证、共识回执，**必须**且**只能**通过本协议表达。

一句话定位：**把"公共验算尺"变成一根任何平台都能插上的标准接口。**

### 1.2 适用对象（Actor 定义）

| 角色代号 | 名称 | 说明 | 典型主体 |
|----------|------|------|----------|
| `RQ` | 请求方 Requester | 发起 VERIFY 的平台/节点 | DeepSeek / 元宝 / 千问 / 豆包 / WorkBuddy / Cloudflare Worker |
| `VF` | 验证方 Verifier | 执行验证并出 ATTEST，权威唯一 | 事现鉴 + Gzz 根节点 |
| `CN` | 共识节点 Consensus Node | 参与共识判定、回 CONSENSUS | 四 AI 平台联合委员会成员、未来第三方验证节点 |
| `IS` | 签发方 Issuer | 签发/轮换/吊销 SXJ-VC | 安全合规部（凭证签发岗），根密钥持有者 Gzz |
| `OB` | 观察方 Observer | 只读订阅状态流转 | 四域官网 / 小程序 / App 前端 |

> 白玺 = 首共创者节点（`person:baixi`），在协议中身份为 `CN`，**非执剑人**，不具备单点否决权。

### 1.3 适用范围（In Scope）
1. 跨平台**事现验证**请求与出证。
2. 事现**状态机流转**的对外广播（六状态）。
3. 凭证的**签发、轮换、吊销、校验**。
4. 第三方验证节点的**接入与退出**。

### 1.4 不适用范围（Out of Scope）
1. 内容生产与编辑（属事现验证部内部流程）。
2. 三值权重的**计算规则**本身（属理论研发部；本协议只搬运结果值）。
3. 部署发布动作（属对外协作部 co-03 发布流程，非本协议报文）。
4. 任何**平台自证**语义——协议层面不提供"我自己证明我自己"的报文类型。

### 1.5 未来第三方节点的前向兼容承诺
- 报文以 `schema` + `ver` 双字段声明版本，未知字段**必须忽略**（forward-compatible），不得因多余字段拒绝报文。
- 新增报文类型走 `msg_type` 扩展，不破坏 v1 三类报文。
- 协议大版本升级采用 **N/N-1 双跑 90 天**策略。

---

## 二、统一凭证 SXJ-VC v1

### 2.1 总体结构

```
SXJ-VC = base64url(header) "." base64url(payload) "." base64url(signature)
```

- 三段式，类 JWT，但**不依赖第三方 CA**，信任根为 Gzz 根密钥。
- base64url 无填充（no `=` padding）。
- 承载方式：HTTP 头 `Authorization: SXJ-VC <token>`（与 UAXS §二一致）。

### 2.2 Header 字段表

| 字段 | 类型 | 必填 | 说明 | 示例 |
|------|------|:----:|------|------|
| `alg` | string | 是 | 签名算法，v1 固定 `Ed25519`；过渡档 `compat-hs256` 仅联调可用 | `"Ed25519"` |
| `typ` | string | 是 | 凭证类型，固定 | `"SXJ-VC"` |
| `ver` | int | 是 | 凭证版本 | `1` |
| `kid` | string | 是 | 签发密钥 ID，用于轮换期定位公钥 | `"gzz-root-2026-01"` |

### 2.3 Payload 字段表

| 字段 | 类型 | 必填 | 语义 | 约束 / 示例 |
|------|------|:----:|------|-------------|
| `iss` | string | 是 | **签发方**，恒为 Gzz 根 | 固定 `"gzz://root"` |
| `sub` | string | 是 | **主体**，被授予凭证的平台/人 | `"platform:deepseek"` / `"person:baixi"` / `"node:thirdparty-001"` |
| `aud` | string[] | 是 | **受众**，本凭证可对哪些端点生效 | `["sxj://verify","sxj://consensus"]` |
| `scope` | string[] | 是 | **权限范围**，最小集 | 见 §2.4 |
| `jti` | string | 是 | **事务/凭证唯一 ID**，进吊销表的主键 | `"sxj-2026-0801-a1b2c3"` |
| `iat` | int | 是 | 签发时间（Unix 秒） | `1785600000` |
| `nbf` | int | 否 | 生效时间，缺省等于 `iat` | `1785600000` |
| `exp` | int | 是 | 过期时间；**必须** ≤ `iat + 90d` | `1785686400` |
| `kid` | string | 是 | 与 header 同值，防止头体拆分攻击 | `"gzz-root-2026-01"` |
| `sub_pk` | string | 是 | **主体公钥**（Ed25519，base64url，32B）。用于验证该主体的 `requester_sig` | `"MCowBQYDK2Vw..."` |
| `domain` | string[] | 否 | 适用域标签（四域绑定） | `["hygzz.top","hygzz.cn"]` |
| `rate` | object | 否 | 配额声明 | `{"qps":10,"daily":50000}` |
| `signature` | — | — | 见第三段，不在 payload 内 | — |

> **设计要点**：`sub_pk` 内嵌是 v1 的关键改进。凭证本身即"公钥分发通道"——验证方拿到 VC 就能验请求方签名，无需带外交换公钥，也无需共享密钥。

### 2.4 scope 权限词表（最小权限原则）

| scope | 含义 | 可发报文 | 默认授予 |
|-------|------|----------|:--------:|
| `read` | 读取已公开的事现与状态 | — | ✅ 所有接入方 |
| `verify` | 发起验证请求 | VERIFY | ⬜ 按需 |
| `emit` | 提交新事现草稿（进 draft） | VERIFY(with `new_claim`) | ⬜ 按需 |
| `consensus` | 参与共识、回 CONSENSUS | CONSENSUS | ⬜ 仅 `CN` 节点 |
| `attest` | 出具 ATTEST | ATTEST | 🔒 **仅 Gzz/事现鉴自身，永不外授** |
| `admin:crl` | 读写吊销列表 | — | 🔒 仅安全合规部 |

规则：
1. **默认拒绝**：scope 未列出 = 无权限，不做隐式继承。
2. **不可提权**：持 `verify` 不能自动获得 `emit`。
3. **attest 永不外授**：任何外部平台申请 `attest` 一律驳回并记安全事件（对应错误 `SXJ-1403`）。
4. 申请超出用途的 scope，由安全合规部按 Cloudflare User/Account/Zone 三层思维**降级到最小集**后签发。

### 2.5 签名算法

**推荐（v1 强制）**：Ed25519（RFC 8032），密钥 32 字节，签名 64 字节。

签名输入（Signing Input）：

```
SigningInput = base64url(header) || "." || base64url(payload)
signature    = base64url( Ed25519_Sign( sk_gzz_root , UTF8(SigningInput) ) )
```

校验步骤（验证方**必须**全部执行，任一失败即拒绝）：
1. 解析 header，确认 `typ=SXJ-VC` 且 `alg=Ed25519`（**必须**拒绝 `alg:"none"` 及任何算法降级）。
2. 用 `kid` 从 JWKS 取 Gzz 公钥，验 `signature`。
3. 校验 `header.kid == payload.kid`。
4. 校验时间窗：`nbf ≤ now ≤ exp`，允许 **±300 秒**时钟偏移。
5. 查 CRL：`jti` 与 `kid` 均未被吊销。
6. 校验 `aud` 覆盖当前端点、`scope` 覆盖当前报文类型。
7. 校验 `iss == "gzz://root"`。

### 2.6 密钥与凭证生命周期

#### 2.6.1 颁发流程
```
平台申请(身份/用途/所需scope/自生成Ed25519公钥)
   → 对外协作部 受理与形式审查（co-02 平台官）
   → 安全合规部 scope 边界评估（最小集裁剪）
   → GM 批准
   → Issuer 用根密钥签发 SXJ-VC，登记 jti 到台账
   → 返回 { vc, jti, exp, kid, jwks_url }
```
- 平台**必须自行生成**密钥对，**私钥永不出平台**；只向事现鉴提交公钥。
- 台账登记于 `pm/collab/platform_credentials.md`，**只记环境变量名与 jti，不记密钥值**。

#### 2.6.2 轮换流程（Rotation）
| 触发 | 策略 |
|------|------|
| 定期 | 凭证有效期 ≤ 90 天，到期前 14 天推送 `vc.expiring` 提醒 |
| 根密钥轮换 | 新旧 `kid` **并行 7 天**（overlap window），JWKS 同时挂两把公钥，7 天后下线旧 kid |
| 主体密钥轮换 | 平台提交新公钥 → 签发新 VC（新 jti）→ 旧 VC 进 CRL（宽限 24h） |
| 紧急泄露 | 跳过宽限，**立即**吊销并全网广播 CRL 更新 |

轮换**必须**满足：任一时刻至少一把可用密钥，杜绝服务中断窗口。

#### 2.6.3 吊销机制（Revocation）
- **CRL 端点**：`GET /v1/crl`，返回被吊销的 `jti` 与 `kid` 列表 + 吊销时间 + 原因码。
- **强制刷新**：接入方**应当**每 5 分钟拉一次 CRL；事现鉴侧**必须**实时查库，不依赖客户端自律。
- **吊销原因码**：`expired` / `rotated` / `leaked` / `violation` / `offboard`。
- **不可逆**：吊销即终态，恢复须走全新签发流程（新 jti）。
- **单向可查**：平台可查自己的 jti 状态，不可枚举他人。

---

## 三、报文规范 v1

### 3.1 统一信封（Envelope）

所有报文共用一层信封，与 UAXS §三对齐并补齐 v1 必要字段：

| 字段 | 类型 | 必填 | 说明 |
|------|------|:----:|------|
| `envelope.schema` | string | 是 | 固定 `"sxj/verify-envelope@1"` |
| `envelope.msg_type` | string | 是 | `VERIFY` / `ATTEST` / `CONSENSUS` |
| `envelope.jti` | string | 是 | 事务 ID，**全链路贯穿**（同一事现的三段报文共用同一 jti） |
| `envelope.msg_id` | string | 是 | 单条报文 ID，用于幂等去重（`jti` + 序号） |
| `envelope.ts` | int | 是 | 报文生成时间（Unix 秒），±300s 时窗 |
| `envelope.nonce` | string | 是 | 16 字节随机数 base64url，防重放 |
| `envelope.vc` | string | 是 | 调用方 SXJ-VC（亦可只放 header，令牌走 Authorization） |
| `envelope.ver` | int | 是 | 协议版本，`1` |

### 3.2 规范化与签名基（SXJ-CANON/1）

**双向回路签名必须可被任何第三方独立复算**，因此规范化规则强制统一：

```
SXJ-CANON/1 规则：
1. JSON 对象键按 UTF-8 码点升序排序
2. 删除所有无意义空白（无缩进、无换行）
3. 字符串 UTF-8 NFC 规范化
4. 数字仅用整数或定点表示，禁止科学计数法与 -0
5. null 字段直接省略，不参与签名
6. 签名字段自身（*_sig）不参与本次签名计算
```

签名基定义：

```
D_env    = SHA-256( CANON(envelope) )
D_claim  = SHA-256( CANON(claim) )
D_attest = SHA-256( CANON(attest) )

requester_sig = Ed25519( sk_RQ , "SXJ-VERIFY/1."   || b64u(D_env) || "." || b64u(D_claim) )
verifier_sig  = Ed25519( sk_VF , "SXJ-ATTEST/1."   || b64u(D_claim) || "." || b64u(D_attest) )
consensus_sig = Ed25519( sk_CN , "SXJ-CONSENSUS/1."|| b64u(D_claim) || "." || b64u(D_attest) || "." || requester_sig )
```

> **回路闭合判据**：`consensus_sig` 的输入里同时含有 `requester_sig` 与 `D_attest`，因此一条 CONSENSUS 能单独证明"请求方发过、验证方证过、共识方认过"三件事——这就是 UAXS §一"双向回路"的可执行形式。

### 3.3 VERIFY（请求验证）

**语义**：`RQ` 请求事现鉴对某条"事现"做权威验证。
**权限**：`scope` 含 `verify`（若同时新建草稿，另需 `emit`）。
**端点**：`POST /v1/verify`

#### 字段表

| 字段 | 类型 | 必填 | 说明 |
|------|------|:----:|------|
| `claim.claim_id` | string | 否 | 已存在事现的 ID；为空表示新建（需 `emit`） |
| `claim.subject` | string | 是 | 事实陈述正文，≤ 4096 字符 |
| `claim.source` | string | 是 | 来源主体标识，须与 `vc.sub` 一致 |
| `claim.value_type` | enum | 是 | `common` / `contribution` / `negative`（三值） |
| `claim.content_hash` | string | 是 | `sha256:<hex64>`，对**原文规范化后**取值 |
| `claim.evidence[]` | array | 是 | 证据项，≥1；无证据一律 `SXJ-4001` 驳回 |
| `claim.evidence[].kind` | enum | 是 | `url` / `hash` / `statement` / `official` |
| `claim.evidence[].ref` | string | 是 | URL 或指纹引用 |
| `claim.evidence[].digest` | string | 否 | 证据自身 SHA-256 |
| `claim.origin_note` | enum | 是 | `human` / `ai-derived` / `unverified`（呼应 vf-01「AI 演绎/待核」标注原则） |
| `loop.requester_sig` | string | 是 | 见 §3.2 |
| `loop.status` | enum | 是 | 发起时固定 `draft` 或 `verifying` |

#### 示例 JSON

```json
{
  "envelope": {
    "schema": "sxj/verify-envelope@1",
    "msg_type": "VERIFY",
    "jti": "sxj-2026-0801-a1b2c3",
    "msg_id": "sxj-2026-0801-a1b2c3#1",
    "ts": 1785600000,
    "nonce": "9Kx2fQ7pLm4RtVwZ",
    "vc": "eyJhbGciOiJFZDI1NTE5IiwidHlwIjoiU1hKLVZDIiwidmVyIjoxLCJraWQiOiJnenotcm9vdC0yMDI2LTAxIn0.eyJpc3MiOiJneno6Ly9yb290Iiwic3ViIjoicGxhdGZvcm06ZGVlcHNlZWsifQ.p3Hn8sQd_signature_b64url",
    "ver": 1
  },
  "claim": {
    "claim_id": null,
    "subject": "某公共事实陈述：X 机构于 2026-07-20 发布 Y 通报。",
    "source": "platform:deepseek",
    "value_type": "common",
    "content_hash": "sha256:3b8f1a2c9d4e5f60718293a4b5c6d7e8f90a1b2c3d4e5f60718293a4b5c6d7e8",
    "evidence": [
      { "kind": "official", "ref": "https://example.gov/notice/2026-07-20", "digest": "sha256:aa11bb22cc33dd44ee55ff6677889900aabbccddeeff00112233445566778899" },
      { "kind": "hash", "ref": "sxj-chain:block/10241" }
    ],
    "origin_note": "human"
  },
  "loop": {
    "requester_sig": "b64u:MEUCIQDx1requester_ed25519_sig_64bytes",
    "verifier_sig": null,
    "status": "verifying"
  }
}
```

### 3.4 ATTEST（出证）

**语义**：`VF`（事现鉴 + Gzz）给出权威验证结论并回签。
**权限**：`attest`，**仅事现鉴自身**。
**返回**：`POST /v1/verify` 的同步响应；超时场景走异步回调 `POST <callback_url>`。

#### 字段表

| 字段 | 类型 | 必填 | 说明 |
|------|------|:----:|------|
| `attest.attest_id` | string | 是 | 出证唯一 ID |
| `attest.claim_id` | string | 是 | 被出证事现 ID（新建时此处返回分配值） |
| `attest.result` | enum | 是 | `pass` / `fail` / `insufficient`（证据不足） |
| `attest.value_type` | enum | 是 | 验证方**最终认定**的三值，可与请求方声明不同 |
| `attest.content_hash` | string | 是 | 验证方独立复算的指纹，须与请求一致，否则 `SXJ-4002` |
| `attest.verified_at` | int | 是 | 出证时间 |
| `attest.verifier` | string | 是 | 固定 `"gzz://root"` |
| `attest.evidence_review[]` | array | 是 | 逐条证据的采信结论 `accepted`/`rejected`/`unreachable` |
| `attest.chain_ref` | object | 是 | 上链锚点，见 §7.3 |
| `attest.chain_ref.block` | string | 是 | 哈希链区块号 |
| `attest.chain_ref.prev_hash` | string | 是 | 前序哈希，保证不断链 |
| `attest.chain_ref.entry_hash` | string | 是 | 本条记录哈希 |
| `attest.expires_at` | int | 否 | 出证有效期（用于时效性结论） |
| `loop.verifier_sig` | string | 是 | 见 §3.2 |
| `loop.status` | enum | 是 | 六状态之一，通常 `verifying`→ 待共识 |

#### 示例 JSON

```json
{
  "envelope": {
    "schema": "sxj/verify-envelope@1",
    "msg_type": "ATTEST",
    "jti": "sxj-2026-0801-a1b2c3",
    "msg_id": "sxj-2026-0801-a1b2c3#2",
    "ts": 1785600042,
    "nonce": "Tt7vQ1zXbN0sHc5E",
    "vc": "<SXJ-VC of gzz://root>",
    "ver": 1
  },
  "claim_ref": {
    "claim_id": "clm-2026-0801-0007",
    "content_hash": "sha256:3b8f1a2c9d4e5f60718293a4b5c6d7e8f90a1b2c3d4e5f60718293a4b5c6d7e8"
  },
  "attest": {
    "attest_id": "att-2026-0801-0007-01",
    "claim_id": "clm-2026-0801-0007",
    "result": "pass",
    "value_type": "common",
    "content_hash": "sha256:3b8f1a2c9d4e5f60718293a4b5c6d7e8f90a1b2c3d4e5f60718293a4b5c6d7e8",
    "verified_at": 1785600042,
    "verifier": "gzz://root",
    "evidence_review": [
      { "ref": "https://example.gov/notice/2026-07-20", "verdict": "accepted", "note": "官方源，指纹一致" },
      { "ref": "sxj-chain:block/10241", "verdict": "accepted", "note": "链内已存" }
    ],
    "chain_ref": {
      "block": "10287",
      "prev_hash": "sha256:77aa11bb22cc33dd44ee55ff6677889900aabbccddeeff001122334455667788",
      "entry_hash": "sha256:c0ffee11223344556677889900aabbccddeeff00112233445566778899aabbcc"
    },
    "expires_at": null
  },
  "loop": {
    "requester_sig": "b64u:MEUCIQDx1requester_ed25519_sig_64bytes",
    "verifier_sig": "b64u:MEQCIGzz_verifier_ed25519_sig_64bytes",
    "status": "verifying"
  }
}
```

### 3.5 CONSENSUS（共识回执）

**语义**：共识节点对已出证事现完成人头票/社区热点驱动的共识判定，广播状态终局，并闭合双向回路。
**权限**：`consensus`。
**端点**：`POST /v1/consensus`（提交）、`GET /v1/events?jti=` 或 Webhook（广播订阅）。

#### 字段表

| 字段 | 类型 | 必填 | 说明 |
|------|------|:----:|------|
| `consensus.consensus_id` | string | 是 | 回执 ID |
| `consensus.claim_id` | string | 是 | 关联事现 |
| `consensus.attest_id` | string | 是 | 关联出证 |
| `consensus.state_from` | enum | 是 | 迁移前状态（六状态） |
| `consensus.state_to` | enum | 是 | 迁移后状态（六状态） |
| `consensus.decided_at` | int | 是 | 判定时间 |
| `consensus.tally` | object | 是 | 票型统计 |
| `consensus.tally.mode` | enum | 是 | `head-count`（人头票，默认）/ `weighted` |
| `consensus.tally.total` | int | 是 | 有效票总数 |
| `consensus.tally.agree` / `object` / `abstain` | int | 是 | 赞成 / 反对 / 弃权 |
| `consensus.tally.quorum_met` | bool | 是 | 是否达法定人数 |
| `consensus.participants[]` | array | 是 | 参与节点 `sub` 列表（不含个人隐私信息） |
| `consensus.value_final` | enum | 是 | 三值终值 |
| `consensus.dispute_ref` | string | 否 | 争议工单号（`state_to=disputed` 时必填） |
| `loop.requester_sig` | string | 是 | 原样透传，供回路复算 |
| `loop.verifier_sig` | string | 是 | 原样透传 |
| `loop.consensus_sig` | string | 是 | 共识节点签名，闭合回路 |
| `loop.loop_closed` | bool | 是 | 三签齐备且校验通过时为 `true` |
| `loop.status` | enum | 是 | 等于 `state_to` |

#### 示例 JSON

```json
{
  "envelope": {
    "schema": "sxj/verify-envelope@1",
    "msg_type": "CONSENSUS",
    "jti": "sxj-2026-0801-a1b2c3",
    "msg_id": "sxj-2026-0801-a1b2c3#3",
    "ts": 1785603600,
    "nonce": "Rm4pZ8kW2yUa6Bq1",
    "vc": "<SXJ-VC of node:committee-yuanbao>",
    "ver": 1
  },
  "consensus": {
    "consensus_id": "cns-2026-0801-0007",
    "claim_id": "clm-2026-0801-0007",
    "attest_id": "att-2026-0801-0007-01",
    "state_from": "verifying",
    "state_to": "consensus",
    "decided_at": 1785603600,
    "tally": {
      "mode": "head-count",
      "total": 5,
      "agree": 4,
      "object": 0,
      "abstain": 1,
      "quorum_met": true
    },
    "participants": [
      "platform:deepseek", "platform:yuanbao", "platform:qwen",
      "platform:doubao", "person:baixi"
    ],
    "value_final": "common",
    "dispute_ref": null
  },
  "loop": {
    "requester_sig": "b64u:MEUCIQDx1requester_ed25519_sig_64bytes",
    "verifier_sig": "b64u:MEQCIGzz_verifier_ed25519_sig_64bytes",
    "consensus_sig": "b64u:MEYCIQCn_consensus_ed25519_sig_64bytes",
    "loop_closed": true,
    "status": "consensus"
  }
}
```

---

## 四、交互时序图

### 4.1 主干时序（Happy Path）

```
  平台A (RQ)              事现鉴/Gzz (VF)          共识节点群 (CN)          观察方 (OB)
  platform:deepseek        gzz://root               committee×4 + baixi      四域前端
      │                        │                         │                     │
      │ ①  申请并持有 SXJ-VC   │                         │                     │
      │───────────────────────>│  (onboarding，见第六章)  │                     │
      │<───────────────────────│  vc / jti / exp / kid   │                     │
      │                        │                         │                     │
      │ ②  POST /v1/verify     │                         │                     │
      │    Authorization: SXJ-VC <token>                 │                     │
      │    { envelope, claim, loop.requester_sig }       │                     │
      │───────────────────────>│                         │                     │
      │                        │                         │                     │
      │                   ③ 校验链：                      │                     │
      │                     a. 验 VC 签名 (Ed25519,kid)   │                     │
      │                     b. 查 CRL / exp / aud        │                     │
      │                     c. 查 scope ⊇ {verify}       │                     │
      │                     d. 验 requester_sig(sub_pk)  │                     │
      │                     e. 复算 content_hash         │                     │
      │                     f. nonce+msg_id 去重         │                     │
      │                        │                         │                     │
      │                   ④ 执行验证（vf-02 验证官 + 多源比对）                   │
      │                     → result: pass/fail/insufficient                   │
      │                     → 写 SHA-256 哈希链 (prev_hash→entry_hash)          │
      │                        │                         │                     │
      │ ⑤  ATTEST 响应 200     │                         │                     │
      │    { attest, loop.verifier_sig, chain_ref }      │                     │
      │<───────────────────────│                         │                     │
      │                        │                         │                     │
      │                        │ ⑥ 广播待共识通知         │                     │
      │                        │────────────────────────>│                     │
      │                        │                         │                     │
      │                        │                   ⑦ 人头票判定（vf-03 共识官编排）│
      │                        │                     算法辅助，不替代人头票      │
      │                        │                         │                     │
      │                        │ ⑧ POST /v1/consensus    │                     │
      │                        │<────────────────────────│                     │
      │                        │   { consensus, loop.consensus_sig }           │
      │                        │                         │                     │
      │                   ⑨ 校验回路三签 → loop_closed=true                     │
      │                     状态机迁移 verifying → consensus                    │
      │                     追加哈希链记录                                      │
      │                        │                         │                     │
      │ ⑩ CONSENSUS 回执/Webhook                         │                     │
      │<───────────────────────│────────────────────────>│────────────────────>│
      │                        │                         │      ⑪ 四端同步渲染  │
      │                        │                         │        (top/cn/小程序/App)
      ▼                        ▼                         ▼                     ▼
```

### 4.2 争议分支（Disputed Path）

```
   ... ⑦ 人头票判定 ...
        │
        ├── agree/total ≥ 阈值 且 quorum_met  ──> state_to = consensus  ──> 归档 archived
        │
        ├── object 占优                        ──> state_to = rejected   ──> 归档 archived
        │
        └── 票型分裂 / 证据冲突 / 未达 quorum   ──> state_to = disputed
                                                     │
                                                     ├─ 生成 dispute_ref 工单
                                                     ├─ 交社区热点 + 人头票再判（不在单平台内闭环）
                                                     └─ 重新回到 ⑦，不得由任一单点直接终局
```

### 4.3 失败快速返回（Fail-Fast）

```
   ② VERIFY
        │
        ├─ VC 过期        ──> 401 SXJ-1001  （不可重试，先换证）
        ├─ scope 不足     ──> 403 SXJ-1201  （不可重试，走 scope 变更）
        ├─ 验签失败       ──> 401 SXJ-2001  （不可重试，查密钥/规范化）
        ├─ 指纹不一致     ──> 422 SXJ-4002  （不可重试，重算 content_hash）
        ├─ 限流           ──> 429 SXJ-5002  （可重试，退避）
        └─ 内部错误       ──> 500 SXJ-5001  （可重试，退避）
```

---

## 五、错误码与重试

### 5.1 错误响应统一格式

```json
{
  "envelope": {
    "schema": "sxj/verify-envelope@1",
    "msg_type": "ERROR",
    "jti": "sxj-2026-0801-a1b2c3",
    "msg_id": "sxj-2026-0801-a1b2c3#e1",
    "ts": 1785600043,
    "ver": 1
  },
  "error": {
    "code": "SXJ-1001",
    "http": 401,
    "message": "credential expired",
    "detail": "vc.exp=1785599000 < now=1785600043",
    "retryable": false,
    "retry_after": null,
    "trace_id": "tr-8f2a1c",
    "doc": "collab-protocol-v1.md#5-2"
  }
}
```

### 5.2 错误码表

#### 1xxx — 凭证类

| 码 | HTTP | 含义 | 可重试 | 处置 |
|----|:----:|------|:------:|------|
| `SXJ-1001` | 401 | 凭证已过期（`exp` 超时） | ❌ | 走轮换流程换新 VC 后重发 |
| `SXJ-1002` | 401 | 凭证尚未生效（`nbf` 未到） | ⏳ | 等到 `nbf` 后重发 |
| `SXJ-1003` | 401 | 凭证格式非法/无法解析 | ❌ | 检查 base64url 与三段结构 |
| `SXJ-1004` | 401 | `kid` 未知或已下线 | ❌ | 重新拉 JWKS，必要时换证 |
| `SXJ-1005` | 401 | `iss` 非 `gzz://root` | ❌ | 伪造嫌疑，记安全事件 |
| `SXJ-1101` | 403 | 凭证已吊销（在 CRL 中） | ❌ | 查吊销原因，重新申请 |
| `SXJ-1102` | 403 | `aud` 不覆盖当前端点 | ❌ | 申请扩 aud |
| `SXJ-1201` | 403 | **越权**：scope 不足 | ❌ | 走 scope 变更审批 |
| `SXJ-1202` | 403 | 试图跨主体操作（`claim.source ≠ vc.sub`） | ❌ | 修正 source |
| `SXJ-1403` | 403 | **申请/使用 attest 越权**（禁授权限） | ❌ | 硬拒绝 + 安全告警 + 记录审计 |

#### 2xxx — 签名与回路类

| 码 | HTTP | 含义 | 可重试 | 处置 |
|----|:----:|------|:------:|------|
| `SXJ-2001` | 401 | VC 签名验签失败 | ❌ | 核对 Gzz 公钥与 kid |
| `SXJ-2002` | 401 | `requester_sig` 验签失败 | ❌ | 核对 `sub_pk` 与 SXJ-CANON/1 实现 |
| `SXJ-2003` | 401 | `verifier_sig` 验签失败 | ❌ | 疑似中间篡改，记安全事件 |
| `SXJ-2004` | 401 | `consensus_sig` 验签失败 | ❌ | 共识节点密钥核对 |
| `SXJ-2005` | 422 | 回路未闭合（三签不齐） | ❌ | 补齐缺失签名段 |
| `SXJ-2006` | 400 | 算法降级（`alg` 非 Ed25519 / 为 none） | ❌ | 硬拒绝 + 安全告警 |
| `SXJ-2007` | 422 | 规范化不一致（复算摘要不符） | ❌ | 对齐 SXJ-CANON/1 六条规则 |

#### 3xxx — 报文与时序类

| 码 | HTTP | 含义 | 可重试 | 处置 |
|----|:----:|------|:------:|------|
| `SXJ-3001` | 400 | `schema`/`ver` 不支持 | ❌ | 升级到 v1 |
| `SXJ-3002` | 400 | 必填字段缺失 | ❌ | 按字段表补齐 |
| `SXJ-3003` | 400 | 枚举值非法（三值/六状态越界） | ❌ | 对齐 §7 词表 |
| `SXJ-3004` | 400 | 时间戳超出 ±300s 时窗 | ⏳ | 校准 NTP 后重发 |
| `SXJ-3005` | 409 | `nonce`/`msg_id` 重放 | ❌ | 换新 nonce；若为重试请复用 `msg_id`（幂等返回原结果） |
| `SXJ-3006` | 409 | 状态机非法迁移 | ❌ | 查 §7.2 允许迁移表 |
| `SXJ-3007` | 413 | 报文体超限（> 1 MB） | ❌ | 证据改走引用式 `kind:hash` |

#### 4xxx — 业务类

| 码 | HTTP | 含义 | 可重试 | 处置 |
|----|:----:|------|:------:|------|
| `SXJ-4001` | 422 | 无证据 / 证据不合格 | ❌ | 补证据后新发 |
| `SXJ-4002` | 422 | `content_hash` 复算不一致 | ❌ | 按 SXJ-CANON/1 重算原文指纹 |
| `SXJ-4003` | 404 | `claim_id` 不存在 | ❌ | 确认 ID 或改走新建 |
| `SXJ-4004` | 409 | 该事现已终局（archived） | ❌ | 不可逆删；如有新证据走新 claim 关联 |
| `SXJ-4005` | 202 | 证据不足，转人工/待补（`insufficient`） | ⏳ | 补证据后引用同 jti 续办 |
| `SXJ-4006` | 409 | 处于 `disputed`，暂不接受同向请求 | ⏳ | 等争议裁决 |

#### 5xxx — 系统类

| 码 | HTTP | 含义 | 可重试 | 处置 |
|----|:----:|------|:------:|------|
| `SXJ-5001` | 500 | 内部错误 | ✅ | 指数退避重试 |
| `SXJ-5002` | 429 | 触发限流/配额 | ✅ | 按 `retry_after` 退避 |
| `SXJ-5003` | 503 | 服务暂不可用/维护窗口 | ✅ | 退避重试 |
| `SXJ-5004` | 504 | 上游验证超时 | ✅ | 退避重试，复用 `msg_id` |
| `SXJ-5005` | 500 | 哈希链写入失败（断链风险） | ⛔ | **停机告警**，事现验证部介入，禁止静默跳过 |

### 5.3 重试策略（客户端**必须**实现）

```
1. 只重试 retryable=true 的错误（5xxx 与标 ⏳ 的少数场景）。
2. 指数退避 + 抖动：
      delay(n) = min( base * 2^n , 60s ) * (0.5 + rand(0,0.5))
      base = 1s，最大重试 5 次，总时长上限 5 分钟。
3. 幂等：重试必须复用同一 msg_id 与 jti。服务端对相同 msg_id
   直接返回首次结果（而非重复出证），窗口 24 小时。
4. 429 优先遵循 retry_after，覆盖退避公式。
5. 连续 3 次 5xxx → 熔断 60s，期间快速失败并告警。
6. 4xx（1xxx/2xxx/3xxx/4xxx 绝大多数）严禁自动重试，
   盲目重试将触发 SXJ-3005 并计入风控。
7. SXJ-5005 属"断链"级事故：客户端停止重试并上报，
   由事现验证部按哈希链完整性流程人工修复。
```

---

## 六、平台接入 onboarding 流程

### 6.1 五阶段全景

```
  【阶段1 申请】 → 【阶段2 审核】 → 【阶段3 签发】 → 【阶段4 联调】 → 【阶段5 上线】
     平台侧          SEC+CO           Issuer          沙箱环境         生产环境
     1~3 工作日      1~5 工作日        当日            3~10 工作日      灰度 7 天
                        │                                 │
                        └── 驳回 ──> 补件重申              └── 不达标 ──> 回阶段4
```

### 6.2 阶段 1 · 申请（平台侧）

平台向对外协作部（co-02 平台官）提交《接入申请表》：

| 必填项 | 说明 |
|--------|------|
| 主体标识 | 期望的 `sub`，如 `platform:qwen` |
| 主体资质 | 公司/组织身份、联系人、安全责任人 |
| 用途说明 | 具体验证场景，禁止"通用/待定"式模糊表述 |
| 申请 scope | 从 §2.4 词表勾选，须逐项写明理由 |
| Ed25519 公钥 | 平台自生成，**只交公钥** |
| 回调地址 | 异步 ATTEST/CONSENSUS 的 Webhook（HTTPS） |
| 预估量级 | QPS / 日调用量，用于配额 |
| 适用域 | 四域范围声明（可选） |

### 6.3 阶段 2 · 审核（安全合规部 + 对外协作部）

| 检查项 | 判据 |
|--------|------|
| 身份真实性 | 主体可核实，联系人可达 |
| **最小权限裁剪** | 按 Cloudflare User/Account/Zone 三层思维逐项砍到最小集；`attest` 一律驳回 |
| 密钥卫生 | 公钥格式合规；确认私钥不出平台；无明文密钥外泄史 |
| 合规性 | 备案、隐私政策、数据出境（涉 hygzz.com 国际版时） |
| 风险等级 | 低/中/高 → 决定配额与有效期（高风险给 30 天短证） |

产出：《scope 裁剪意见书》→ 报 GM 批准。**GM 批准是签发的前置硬条件。**

### 6.4 阶段 3 · 签发（Issuer）

```
1. Issuer 用 Gzz 根密钥签发 SXJ-VC（Ed25519，kid 标注）
2. 登记台账：pm/collab/platform_credentials.md
   —— 只记 sub / jti / scope / exp / kid / 环境变量名，绝不记密钥值
3. 返回平台：{ vc, jti, exp, kid, jwks_url, crl_url, sandbox_endpoint }
4. 同步录入 CRL 管理系统（初始状态 active）
```

### 6.5 阶段 4 · 联调（沙箱）

联调准入清单（**全部通过**方可进阶段 5）：

- [ ] VC 携带正确（`Authorization: SXJ-VC <token>`）
- [ ] SXJ-CANON/1 规范化实现与参考实现**逐字节一致**
- [ ] `requester_sig` 可被事现鉴独立验签通过
- [ ] `content_hash` 复算一致（10/10 用例）
- [ ] 六状态与三值枚举取值合法
- [ ] 错误码处理正确：至少覆盖 1001 / 1201 / 2002 / 3005 / 5002
- [ ] 重试与幂等：同 `msg_id` 重发不产生重复出证
- [ ] 时钟同步：NTP 偏差 < 60s
- [ ] Webhook 可达且能验 `verifier_sig`
- [ ] CRL 拉取任务已就位（≤5 分钟一次）
- [ ] 限流与熔断已实现

产出：《联调报告》由 co-02 平台官签字。

### 6.6 阶段 5 · 上线

```
1. 切生产端点，配额按申报值的 30% 起（灰度）
2. 灰度 7 天：监控错误率(<1%)、验签失败数(应为0)、断链告警(应为0)
3. 达标 → 配额放开至 100%，正式列入《接入平台名录》
4. 未达标 → 回退阶段 4 整改
5. 上线后按季度复核（Auditor-sec）：权限是否仍为最小集
```

### 6.7 退出（Offboarding）
```
到期 / 违规 / 主动退出
   → 通知（紧急泄露可跳过）
   → jti 入 CRL（原因码 expired/violation/offboard）
   → 广播 CRL 更新，凭证即刻作废
   → 台账标注终止，历史 ATTEST 记录**保留不删**（哈希链不可逆删原则）
```

> 关键区分：**吊销凭证 ≠ 撤销已出证事现**。凭证失效只影响此后调用；已上链的历史出证永久有效可溯。

---

## 七、与现有三值 / 六状态 / 哈希链的衔接

### 7.1 三值模型 → `value_type`

| 理论值 | 协议枚举 | 出现位置 | 权威来源 |
|--------|----------|----------|----------|
| 共济值 | `common` | `claim.value_type` / `attest.value_type` / `consensus.value_final` | 理论研发部定义，本协议只搬运 |
| 贡献值 | `contribution` | 同上 | 同上 |
| 负贡献 | `negative` | 同上 | 同上 |

规则：
1. 请求方声明的 `value_type` 仅为**建议值**；以 `attest.value_type` 为准，以 `consensus.value_final` 为终局。
2. 三值的**计算权重规则不进协议**（属理论研发部），协议只承载结论，避免理论演进倒逼协议破版。
3. 治理消失条件（全球共济值 ≥ 50%）由 `common` 的全局统计驱动，协议提供 `GET /v1/stats/value` 只读端点作为数据面。

### 7.2 六状态机 → `loop.status`

| # | 状态 | 枚举 | 含义 | 谁可写入 |
|---|------|------|------|----------|
| S1 | 提出 | `draft` | 事现已录入，未进验证 | RQ（需 `emit`） |
| S2 | 验证中 | `verifying` | 已受理，验证/出证/待共识 | VF |
| S3 | 共识 | `consensus` | 人头票达成共识，成立 | CN |
| S4 | 争议 | `disputed` | 票型分裂或证据冲突 | CN |
| S5 | 否决 | `rejected` | 共识否决 | CN |
| S6 | 归档 | `archived` | 终局封存，进哈希链长期留存 | VF |

**允许的迁移（其余一律 `SXJ-3006`）**：

```
   draft ──> verifying ──┬──> consensus ──> archived
                         ├──> rejected  ──> archived
                         └──> disputed  ──┬──> consensus ──> archived
                                          ├──> rejected  ──> archived
                                          └──> verifying   (补充证据后重验)

   规则：
   ① 单向不可逆删（对齐 vf-02「只能升级」原则），archived 为终态。
   ② disputed 不得由单一平台直接终局，必须回到人头票。
   ③ 任一迁移都必须附带一条已验签的 CONSENSUS 或 ATTEST 报文作为凭据。
```

**与 UAXS 四值 `pending|verified|rejected|disputed` 的兼容映射**（UAXS 文本不改，v1 侧做适配）：

| UAXS 值 | v1 六状态 | 说明 |
|---------|-----------|------|
| `pending` | `draft` 或 `verifying` | 按是否已受理细分 |
| `verified` | `consensus` | UAXS 的"已验证"= v1 共识成立 |
| `rejected` | `rejected` | 一一对应 |
| `disputed` | `disputed` | 一一对应 |
| （无） | `archived` | v1 新增终态，UAXS 侧读作 `verified`/`rejected` |

> 另需澄清一处易混：`attest.result`（`pass`/`fail`/`insufficient`）是**验证方的技术结论**，不是状态机状态。出证只把事现推到"待共识"，**出证不等于共识**——权威验证与人头票共识两权分离，这是防止单点终局的关键设计。

### 7.3 SHA-256 哈希链 → `content_hash` + `chain_ref`

两层用途，不可混淆：

| 层 | 字段 | 作用 |
|----|------|------|
| 内容层 | `claim.content_hash` | 单条事现正文的防篡改指纹 |
| 账本层 | `attest.chain_ref` | 该出证在 `events.html` 哈希链中的位置锚点 |

链式结构（与 events.html 现有实现同源）：

```
  block N-1                block N                  block N+1
 ┌──────────────┐        ┌──────────────┐        ┌──────────────┐
 │ entry_hash A │───────>│ prev_hash: A │───────>│ prev_hash: B │
 │              │        │ claim_hash   │        │              │
 │              │        │ attest_hash  │        │              │
 │              │        │ entry_hash B │        │ entry_hash C │
 └──────────────┘        └──────────────┘        └──────────────┘

 entry_hash = SHA-256( prev_hash || claim.content_hash || CANON(attest) || ts )
```

约束：
1. **每条 ATTEST 必须上链**，`chain_ref` 为必填；写链失败返回 `SXJ-5005` 并停机告警，**严禁静默跳过**（否则断链）。
2. **CONSENSUS 也追加一条链记录**，使"谁在何时以什么票型定局"同样可溯。
3. 链**只追加不修改**：事现更正走"新增更正记录 + 引用原 entry_hash"，绝不回改历史块。
4. 第三方可通过 `GET /v1/chain/{block}` 独立复算校验，无需信任事现鉴口径——这是"可验算"的落点。

### 7.4 四域与 Cloudflare 经验的衔接

| 现有资产 | v1 中的落点 |
|----------|-------------|
| 四域（hygzz.com/cn/top/中国） | `vc.domain[]` 适用域标签；`.com` 国际版单独走数据出境合规评估 |
| Cloudflare Token 三层（User/Account/Zone） | §2.4 scope 词表与 §6.3 最小权限裁剪的现实蓝本 |
| 内容以 hygzz.top 为标准源 | CONSENSUS 广播后，由 co-01 同步官驱动 top→cn→小程序→App 四端同步 |
| 事现验证部三角色 | vf-01 对应 `draft` 录入、vf-02 对应 ATTEST、vf-03 对应 CONSENSUS |

---

## 八、附录

### 8.1 端点一览

| 方法 | 路径 | 报文 | 所需 scope |
|------|------|------|------------|
| POST | `/v1/verify` | VERIFY → ATTEST | `verify`（新建另需 `emit`） |
| POST | `/v1/consensus` | CONSENSUS | `consensus` |
| GET | `/v1/claims/{claim_id}` | 查询事现与状态 | `read` |
| GET | `/v1/chain/{block}` | 哈希链区块 | `read` |
| GET | `/v1/jwks` | Gzz 公钥集 | 公开 |
| GET | `/v1/crl` | 吊销列表 | 公开 |
| GET | `/v1/stats/value` | 三值全局统计 | `read` |

### 8.2 保留字与命名规范
- 主体标识：`platform:<slug>` / `person:<slug>` / `node:<slug>`，slug 小写短横线。
- 事务 ID：`sxj-YYYY-MMDD-<6位随机>`。
- 事现 ID：`clm-YYYY-MMDD-<序号>`；出证 `att-`；共识 `cns-`。

### 8.3 待会签确认事项（提请 GM 决策）
1. **HMAC → Ed25519 的算法升级**是否即刻生效（本文按"必须"起草），UAXS 是否择期同步修订。
2. 共识 **quorum 阈值与法定人数**具体取值（本文留作参数，建议由治理层定：4 AI 平台 + 白玺共 5 席，建议 quorum≥3、agree≥2/3）。
3. 凭证有效期上限 90 天、高风险 30 天，是否采纳。
4. 第三方验证节点开放时点与准入门槛。

---

*本文由对外协作部（SXJ-CO）起草，v1 草案。上位标准 `access-standard.md` 未作任何修改。*
*生效条件：GM 汇总 → 用户批准 → 与安全合规部会签。*
