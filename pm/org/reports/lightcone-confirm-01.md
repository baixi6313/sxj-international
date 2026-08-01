# 光锥运维部 · 第一号确认报告（lightcone-confirm-01）

- **部门**：光锥运维部（横向支撑 · 日常维护闭环：记录 → 审查 → 优化）
- **报告编号**：LC-CFM-01
- **报告日期**：2026-08-01
- **报告人**：光锥运维部负责人
- **呈送**：PM（决策层）→ 始创者·白玺（决定层）
- **审计范围**：2026-08-01 当日全部已执行操作（7 大项）
- **取证方式**：源码只读核查（Read / Grep / find）+ 线上实地探测（curl 实测）+ 线上产物反解（GitHub API）
- **声明**：**本次审计未修改任何源码、未执行任何部署动作**，全部为只读取证。

---

## 〇、总表：七项确认结论

| # | 确认项 | 结论 | 关键证据摘要 |
|---|--------|------|--------------|
| 1 | BETA 横幅清理（6 网站 + 安卓 + 小程序） | **部分落实** | HTML 层 6/6 端点命中 0；但 **JS 资源层 3 端点线上仍有 `版本 1.0 (BETA)`** |
| 2 | 小程序 1.0.1 + profile.wxml 修复 + WXML 配平 | **已落实**（源码） | 1.0.1/101；hero 与「已记录」已复原；10 文件全配平，profile 31/31 |
| 3 | 知识树 v1.2 源码改完 | **已落实** | 4 份副本全 148KB 级，权力栈=3 / v1.2=1 / Wrangler=3 / 去BETA=3 |
| 4 | 部署落地（cn/www.cn、com、安卓 1.0.2） | **已落实**（本项范围内 4/4） | cn 149273B v1.2；com 147684B v1.2；Release v1.0.2 APK HTTP 200 |
| 5 | 全站同步 A（top→cn，wrangler 直连） | **已落实**，但有副作用 | canonical=hygzz.cn、cv.html 200、v1.2 就位；**同步把 top 的 BETA 带入 cn** |
| 6 | 四部门建立 + 组织架构图 | **部分落实** | 4 份 dept 文档齐备、SVG 含决定层×4/决策层×4；**架构图未嵌入任何官网 HTML** |
| 7 | GitHub 禁令落实 | **部分落实** | roles.md / dept-01 / dept-04 已写入；**dept-02、dept-03 缺条款** |

> **一句话总览**：四项主体工程（小程序源码、知识树 v1.2、三平台部署、全站同步 A）已真实落地并经线上验证；**BETA 清理、组织架构图上线、GitHub 禁令覆盖三项为「部分落实」**，另发现 **1 处新的线上活体 BETA 残留** 与 **1 条版本元数据死链**，详见第八节。

---

## 一、确认项 1：BETA 横幅清理 → **部分落实**

### 1.1 网站 HTML 层：6/6 端点已清（✅ 已落实）

线上实测（`curl -sL`，关键词 `beta-banner|测试版 BETA|⚠️ 测试版`）：

```
hygzz.cn      | HTTP 200 |  12271 字节 | 横幅命中 0
www.hygzz.cn  | HTTP 200 |  12271 字节 | 横幅命中 0
hygzz.com     | HTTP 200 | 238714 字节 | 横幅命中 0
www.hygzz.com | HTTP 200 |    ——      | 横幅命中 0   ← 首探 000，连测 3 次均 200
hygzz.top     | HTTP 200 |  11126 字节 | 横幅命中 0
www.hygzz.top | HTTP 200 |  11126 字节 | 横幅命中 0
```

> `www.hygzz.com` 首次探测返回 `000`，连续 3 次复测均为 `200`，与 hygzz02 审查报告 §2.1 记录的现象一致，判定为沙箱 DNS 缓存导致的**瞬时抖动**，非故障。

### 1.2 ⚠️ 新发现（P1）：JS 资源层线上仍有活体 BETA

W-01 的验证口径（`verify_all.py`）**只扫 HTML 页面**，未覆盖 `.js`。本次扩大口径后实测：

| 端点 | HTTP | BETA 命中 | 实际内容 |
|------|------|-----------|----------|
| `https://hygzz.cn/app/js/app.js` | 200 | **1** | `版本 1.0 (BETA) · 数据更新 2026-07-30` |
| `https://www.hygzz.cn/app/js/app.js` | 200 | **1** | 同上 |
| `https://hygzz.top/app/js/app.js` | 200 | **1** | 同上 |
| `https://hygzz.com/app/js/app.js` | 404 | 0 | 该路径不存在（国际版无 PWA 子应用） |

源头定位：`hygzz-top-site/app/js/app.js:108`

```js
+ '<div class="info"><b>事现鉴</b> · 共创论公共事实验证工具<br>版本 1.0 (BETA) · 数据更新 2026-07-30</div>'
```

**性质**：该字符串渲染在 PWA 子应用（`/app/`）的信息栏，**用户可直接看到**，属真实未清理项，而非误报。
**扩散路径**：`pm/tools/sync_top_to_cn.py` 全站同步时将其从 `hygzz-top-site` 复制到 `hygzz_cn_domestic/app/js/app.js:108`，再经 wrangler 部署上线 → **确认项 5 的同步动作把这处 BETA 引入了 hygzz.cn**（详见 §5.3）。

### 1.3 安卓 App：✅ 已落实

- 源码 `assets/www/js/app.js` 的 `(BETA)` 版本标签已删（hygzz02 §4.2 已核）。
- 线上产物：Release **v1.0.2**，APK 236910 字节，`updated_at=2026-08-01T04:25:46Z`，下载 HTTP 200。
- 远端 `build.gradle` = `versionCode 3` / `versionName "1.0.2"`，与本地一致。

### 1.4 小程序：主程序 ✅ / 第二小程序遗留死代码（P3）

- **主程序 `sxj-mini/weapp-client`**：全目录扫描无用户可见 BETA 残留（仅 `package-lock.json` 中第三方依赖版本号 `1.0.0-beta.0`，非文案）。✅
- **⚠️ `verify-group-mini/app.wxss:33`** 仍保留 `/* 测试版横幅（全站顶部） */` 注释及其样式规则。经核查该小程序 WXML 中**已无对应 DOM 节点**，属**孤立死 CSS**，用户不可见，定级 P3（清洁度问题，非功能缺陷）。

### 1.5 工作区源码整体扫描

全工作区（排除 `node_modules` / `_archive` / `npm_cache` / `.git`）命中 14 个文件，逐一甄别后**全部为非交付物**：

| 类别 | 文件 | 判定 |
|------|------|------|
| 检测/清理脚本本身 | `remove_banner.py`、`remove_banner_pass2.py`、`verify_all.py`、`verify_banner_sources.py`、`verify_cn.py`、`github_clean_push.py`、`poll_and_verify.py` | 正则模式串，**必须保留** |
| 注入脚本（历史） | `inject_beta.py`、`inject_beta_current.py` | 历史工具，建议归档或删除 |
| 记忆与报告 | `.workbuddy/memory/*.md`、`pm/RELEASE_CHECKLIST.md`、`pm/ygzz02_audit.md`、`pm/ygzz03_proposals.md` | 审计记录，**必须保留** |

**交付物类型（html/wxml/wxss/css/js/json/md）实际命中仅 2 处**，即 §1.2 与 §1.4 所述两项。

### 1.6 本项结论

> **部分落实**。HTML 层与安卓、小程序主程序已达成；**JS 资源层 3 个线上端点存在用户可达的 BETA 残留（P1）**，第二小程序有死 CSS（P3）。
> 记录本 W-01 标注的「✅ 已部署」在**其原定 HTML 口径内成立**，但作为「全平台去 BETA」的整体结论**尚不能闭环**。

---

## 二、确认项 2：小程序 1.0.1 + profile.wxml 修复 + WXML 配平 → **已落实（源码）**

### 2.1 版本标注 ✅

`sxj-mini/weapp-client/project.miniapp.json:4-5`
```json
"version": "1.0.1",
"versionCode": 101,
```

`pages/profile/profile.wxml:27`
```
小程序版本 1.0.1 · 正式版
```

### 2.2 误删区块已完整恢复 ✅

hygzz02 §3.2 报告的 P1 缺陷（hero 区块、stats-bar 开标签、首个 `stat-item`「已记录」被贪婪正则误删）经复核**已全部复原**：

| 被删内容 | 当前位置 | 状态 |
|----------|----------|------|
| `<view class="hero">` | `profile.wxml:2` | ✅ 已恢复 |
| `hero-title` 大家的事现 | `profile.wxml:3` | ✅ 已恢复 |
| `hero-desc` 事现鉴 · 客户端输入端 | `profile.wxml:4` | ✅ 已恢复 |
| `<view class="stats-bar">` | `profile.wxml:7` | ✅ 已恢复 |
| 「已记录」统计项 | `profile.wxml:10` | ✅ 已恢复 |
| 「验证人」统计项 | `profile.wxml:14` | ✅ 保留 |

### 2.3 全站 WXML 配平 ✅（10/10 文件通过）

```
OK  3/3   pages/addEvent/addEvent.wxml
OK  1/1   pages/addEvidence/addEvidence.wxml
OK  1/1   pages/addVerification/addVerification.wxml
OK 74/74  pages/eventDetail/eventDetail.wxml
OK  9/9   pages/events/events.wxml
OK 29/29  pages/index/index.wxml
OK 23/23  pages/intro/intro.wxml
OK 31/31  pages/profile/profile.wxml     ← 记录本记 28/28，现为 31/31
OK 19/19  pages/theory/theory.wxml
OK 11/11  pages/verifyGroup/verifyGroup.wxml
```

> **差异说明（非缺陷）**：`profile.wxml` 由 28/28 增至 31/31，原因是同步 A 阶段「相关站点」区块由 1 条扩为**四域官网 4 条链接**（hygzz.com / cn / top / 中国），新增 3 对 `<view>`。开闭仍严格相等，配平成立。

### 2.4 本项结论

> **已落实（源码层 100%）**。发布状态为**未上线**——需始创者在微信开发者工具手动上传，运维部无微信账号/上传密钥，且该目录非 git 仓库。此为已知约束，非执行缺失。

---

## 三、确认项 3：知识树 v1.2 源码 → **已落实**

### 3.1 四份副本全同步 ✅

| 文件 | 字节 | 四层权力栈 | 知识树 v1.2 | Wrangler | 去 BETA 节点 |
|------|------|-----------|-------------|----------|--------------|
| `knowledge_tree.html`（主） | 148336 | 3 | 1 | 3 | 3 |
| `hygzz-top-site/knowledge_tree.html` | 148336 | 3 | 1 | 3 | 3 |
| `hygzz-top-site/app/theory/knowledge_tree.html` | 148336 | 3 | 1 | 3 | 3 |
| `sxj-android-app/.../assets/www/theory/knowledge_tree.html` | 148497 | 3 | 1 | 3 | 3 |

> 安卓副本多 161 字节，为底部 service worker 注册脚本（与记忆日志「App 副本保留 sw 注册」记载一致），非内容差异。

### 3.2 权力栈图资产 ✅

```
assets/knowledge_tree/sxj-power-stack-2026-08-01.jpg          55198 字节
assets/knowledge_tree/sxj-power-stack-2026-08-01.base64.txt   73625 字节
```

base64 内联是文件体积由 ~72KB 增至 ~148KB 的直接原因，与 hygzz02 §5.1 交叉印证一致。

### 3.3 本项结论

> **已落实**。四层权力栈图 + Cloudflare/Wrangler/去BETA 三个技术节点 + 页脚 v1.2 版本标记，四份副本 100% 就位。

---

## 四、确认项 4：部署落地 → **已落实（本项列举范围 4/4）**

### 4.1 hygzz.cn / www.hygzz.cn（wrangler · Cloudflare Pages）✅

```
https://hygzz.cn/knowledge_tree      | 149273 字节 | 四层权力栈 3 | 知识树 v1.2
https://www.hygzz.cn/knowledge_tree  | 149273 字节 | 四层权力栈 3 | 知识树 v1.2
```

### 4.2 hygzz.com（GitHub Pages + CF 代理）✅

```
https://hygzz.com/knowledge_tree     | 147684 字节 | 四层权力栈 3 | 知识树 v1.2
```

> 未出现 hygzz03 §0.3 预警的「CF 边缘缓存返回旧版」误判，线上已吃新内容。

### 4.3 安卓 1.0.2（含 v1.2 树）✅

| 核验点 | 实测值 |
|--------|--------|
| Release 列表 | `v1.0.2`（2026-08-01T04:25:46Z，236910B）、`v1.0`（04:20:57Z，176055B） |
| v1.0.2 APK 下载 | HTTP **200** |
| 远端 `build.gradle` | `versionCode 3` / `versionName "1.0.2"` |
| 远端 `version.json` | `1.0.2` / url→v1.0.2 / notes 含「内嵌知识树 v1.2」 |
| APK 内嵌树 | 记录本与 hygzz01 已反解验证：`versionName=1.0.2`、四层权力栈命中 3 |

> APK 体积由 176KB 增至 236KB（+60KB），与内嵌 base64 权力栈图的体积增量吻合，**交叉印证 v1.2 确已打包进 APK**。

### 4.4 ⛔ hygzz.top（腾讯云 COS）**未部署**

```
https://hygzz.top/knowledge_tree.html | 72240 字节 | 四层权力栈 0 | 知识树 v1.1
```

原因：本会话及上一会话均无 `TENCENT_SECRET_ID` / `TENCENT_SECRET_KEY` 环境变量（`tcb_api.py` 从环境变量读取，安全不落盘）。**此项已在记录本 K-01 明确登记为阻塞，非遗漏**。

> **口径说明**：确认项 4 列举的四项（cn/www.cn、com、安卓 1.0.2）**全部达成**；hygzz.top 不在本项列举范围内，但作为「知识树 v1.2 全量上线」的整体目标，仍是**未闭环的一站**（见待办 T-03）。

### 4.5 ⚠️ 新发现（P1）：网站侧 version.json 版本漂移 + 下载死链

| 位置 | version | url 指向 | 实际可用性 |
|------|---------|----------|------------|
| `sxj-android-app/version.json`（本地+远端） | `1.0.2` | `/download/v1.0.2/` | ✅ HTTP 200 |
| `hygzz-top-site/version.json`（源） | `1.0.1` | `/download/v1.0.1/` | ❌ **HTTP 404** |
| `hygzz_cn_domestic/version.json`（源） | `1.0.1` | `/download/v1.0.1/` | ❌ **HTTP 404** |
| `https://hygzz.cn/version.json`（**线上活体**） | `1.0.1` | `/download/v1.0.1/` | ❌ **HTTP 404** |
| `https://hygzz.top/version.json`（**线上活体**） | **`1.0.0`** | `/download/v1.0/` | ⚠️ 200，但 notes=**「事现鉴 App v1.0 BETA」** |
| `https://hygzz.com/version.json` | — | — | 404（该路径不存在，正常） |

**两个独立问题**：

1. **死链**：GitHub Releases 实际只有 `v1.0` 与 `v1.0.2`，**从不存在 `v1.0.1` Release**（hygzz02 §4.4 已记录 1.0.1 被 `--clobber` 覆盖到 v1.0 之下）。网站侧 version.json 却写死 `v1.0.1` → 任何依此下载的用户会**得到 404**。
2. **hygzz.top 线上仍是 1.0.0 + BETA 文案**：hygzz03 的 NEW-1 至今**未闭环**——源文件已修为 1.0.1，但因 §4.4 的 COS 未部署，线上仍是旧值。

> **根因**：正是 hygzz03 OPT-6 指出的「缺少版本号单一真相源」。App 已迭代到 1.0.2，网站侧三处副本停留在 1.0.1/1.0.0，且无人反查 Release 是否真的存在。

---

## 五、确认项 5：全站同步 A（hygzz.top → hygzz.cn） → **已落实**，但带入 1 处副作用

### 5.1 同步机制核验 ✅

`pm/tools/sync_top_to_cn.py` 声明的规则与实际一致：

- 源：`.../2026-07-24-23-26-27/hygzz-top-site`
- 目标：`.../2026-07-22-08-14-20/hygzz_cn_domestic`
- 排除：`.git`、`.github`、`.wrangler`、`CNAME`、`.gitignore`、`.pagesignore`、`push.bat`、`README.md`、`*.txt`（站点验证文件）
- 域名替换：`https://hygzz.top` → `https://hygzz.cn`
- **`hygzz.com` 不动**（国际版官网）✅

### 5.2 线上同步效果验证 ✅

| 验证点 | 实测 | 判定 |
|--------|------|------|
| cn 首页体积 | 12271 字节（top 为 11126） | ✅ 已被 top 简洁版覆盖（原 cn 完整版约 157KB） |
| cn canonical | `href="https://hygzz.cn"` | ✅ 域名替换生效 |
| `hygzz.cn/cv.html` | HTTP **200** | ✅ top 特有页已同步过来 |
| cn 知识树 | 149273 字节 / v1.2 / 权力栈 3 | ✅ |
| 部署通道 | wrangler 直连 CF Pages（`--branch main`） | ✅ **未走 GitHub**，符合禁令 |

> 体积差 1145 字节来自域名字符串替换与 cn 侧保留文件，属预期。

### 5.3 ⚠️ 副作用：同步把 top 的 BETA 带进了 cn

`app/js/app.js` 在 top 源中含 `版本 1.0 (BETA)`（§1.2），同步脚本按「全站替换 A」原样复制，wrangler 部署后 **hygzz.cn / www.hygzz.cn 线上新增了这处 BETA**。

> **运维部判断**：这不是同步脚本的缺陷，而是**「标准源本身不干净」**的问题。以 top 为唯一标准源的策略正确，但**标准源必须先通过清洁度闸门**，否则同步会成为缺陷的放大器。此点建议写入发布检查清单（见建议 R-05）。

### 5.4 本项结论

> **已落实**。全站替换 A 已按用户确认范围执行并经线上验证，wrangler 直连未触碰 GitHub。副作用为标准源污染传导，随 T-01 修复后自动消除。

---

## 六、确认项 6：四部门建立 + 组织架构图 → **部分落实**

### 6.1 四部门文档齐备 ✅

| 文件 | 字节 | 部门 | 五要素完整性 |
|------|------|------|--------------|
| `pm/org/dept-01-security.md` | 1441 | 安全合规部 SXJ-SC | ✅ 定位/职责/下设角色/输出物/工作原则 |
| `pm/org/dept-02-verification.md` | 1502 | 事现验证部 SXJ-VF | ✅ 同上 |
| `pm/org/dept-03-theory.md` | 1457 | 理论研发部 SXJ-TH | ✅ 同上 |
| `pm/org/dept-04-collaboration.md` | 1587 | 对外协作部 SXJ-CO | ✅ 同上 |

配套文档同样就位：`lightcone-ops.md`（部门章程）、`org-structure.md`（GM 提案）、`access-standard.md`（UAXS 统一接入标准）。

**部门已开始实际产出**（横向印证组织已运转，非空壳）：
- `pm/org/reports/security-report-01.md`（16323 字节，安全合规部第一号报告）
- `pm/org/reports/collab-protocol-v1.md`（41805 字节，对外协作部 SXJ-XIP/1 协议）

### 6.2 组织架构图（始创者-白玺版）已产出 ✅

`assets/org/sxj-org-structure.svg`（6394 字节，13:19 更新）内容核验：

```
决定层        × 4 处
决策层        × 4 处
始创者 · 白玺  × 1
光锥运维部 / 安全合规部 / 事现验证部 / 理论研发部 / 对外协作部  均在图
无障碍描述：「始创者-白玺为决定层，PM 项目经理为决策层，决定层同意后决策层执行；
              横向光锥运维部支撑，纵向四部门为安全合规、事现验证、理论研发、对外协作。」
```

层级定义与 `pm/roles.md:8-11` 完全一致。

### 6.3 ⚠️ 架构图尚未上线

```bash
grep -rln 'sxj-org-structure' --include="*.html" .   →  （无任何命中）
```

架构图**未嵌入任何官网页面**。记忆日志已将其登记为「待用户确认后嵌入 hygzz.cn / hygzz.top」，属**待决定层拍板**，非执行遗漏。

### 6.4 本项结论

> **部分落实**。四部门定义 + 架构图**产出已完成**（这是本项的核心交付），**上线待决定层确认**。

---

## 七、确认项 7：GitHub 禁令落实 → **部分落实**

### 7.1 条款覆盖情况

| 文件 | 是否含禁令 | 原文 |
|------|-----------|------|
| `pm/roles.md:11` | ✅ | 「**铁律**：未经决定层许可，不将任何资源提交至 GitHub；不替用户在微信后台点击发布；所有部署需决定层授权。」 |
| `pm/org/dept-01-security.md:25` | ✅ | 「未经用户书面/口头许可，不将任何资源提交至 GitHub。」 |
| `pm/org/dept-02-verification.md` | ❌ **缺** | 全文 0 处提及 GitHub |
| `pm/org/dept-03-theory.md` | ❌ **缺** | 全文 0 处提及 GitHub |
| `pm/org/dept-04-collaboration.md:26` | ✅ | 「GitHub 提交必须单独获得用户许可，默认不提交。」 |

> 缺失的两部门中，理论研发部（SXJ-TH）输出物为 `knowledge_tree.html` / `whitepaper.html`，事现验证部（SXJ-VF）输出物为 `events.html` —— **两者均是会推送到 hygzz.com（GitHub Pages）的内容资产**，客观上存在触碰禁令的路径。建议补齐（R-06）。

### 7.2 行为合规性核验 ✅

- **全站同步 A 的 cn 部署**：wrangler 直连 CF Pages，**未经 GitHub**，符合禁令。
- **安卓 1.0.2 推送（12:11 前后）经 GitHub Contents API 执行**：经查时间线，禁令由用户在 **13:18 架构升级会话**中明确提出，安卓推送发生在**禁令确立之前**，**不构成违规**。
- 禁令确立后至本次审计，**未发现任何新的 GitHub 提交动作**。

### 7.3 ⚠️ 结构性矛盾（需决定层裁决）

禁令生效后，以下两条发布链路**事实上被冻结**，因为它们**唯一的发布通道就是 GitHub**：

| 资产 | 发布通道 | 禁令后状态 |
|------|----------|------------|
| **hygzz.com**（国际版官网） | GitHub Pages（仓库 `sxj-international`） | **无替代通道**，内容无法更新 |
| **安卓 App** | GitHub Actions 云端构建 + Releases 分发 | **无替代通道**，无法发新版 |

> 对比：hygzz.cn 有 wrangler、hygzz.top 有 COS、小程序有微信后台，均不依赖 GitHub。**唯独 .com 与 App 无路可走**。此非执行问题，而是**策略与技术现实的冲突**，必须提请决定层裁决（见建议 R-01）。

### 7.4 本项结论

> **部分落实**。核心文档（roles.md）与两个高相关部门已写入，**行为层面无违规**；但 dept-02 / dept-03 条款缺失，且存在 .com 与 App 的通道冻结矛盾待裁决。

---

## 八、仍待办 / 有风险项清单

按风险等级排序。**P0 = 安全高危，P1 = 用户可见缺陷，P2 = 功能/流程缺陷，P3 = 清洁度**。

| 编号 | 级别 | 事项 | 现状证据 | 阻塞方 |
|------|------|------|----------|--------|
| **T-01** | **P1** | **线上 JS 活体 BETA**：cn / www.cn / top 的 `app/js/app.js` 含「版本 1.0 (BETA)」 | 3 端点 curl 实测命中各 1 | 运维部可改源码；上线需 CF+COS |
| **T-02** | **P1** | **version.json 死链**：cn/top 源与 cn 线上写 url→`v1.0.1`，该 Release **不存在（404）** | Releases 仅 v1.0 / v1.0.2 | 运维部可改；上线需部署 |
| **T-03** | **P1** | **hygzz.top COS 未部署**：知识树仍 v1.1、version.json 仍 1.0.0+BETA | top 线上 72240B / 权力栈 0 | **缺 `TENCENT_SECRET_ID/KEY`** |
| **T-04** | **P0** | **12 脚本明文 PAT 未吊销**，`.gitignore` 已加固但**不覆盖这批 `.py`** | 13 文件命中（含 `secret_scan.py` 检测器，实际 12 个泄漏点） | **始创者需登录 GitHub 吊销** |
| **T-05** | **P0** | **git 未归档且带雷**：79 个 `M` + 45 个 `??`，此时 `git add -A` 会把 12 份 PAT 入库 | `git status --porcelain` 实测 | 运维部（须先做 T-04） |
| **T-06** | **P2** | **小程序需手动上传**：主程序 `sxj-mini` 源码已就绪（1.0.1）；`verify-group-mini` 亦未发布 | 无微信密钥、非 git 仓库 | **仅始创者可操作** |
| **T-07** | **P2** | **.com / App 发布通道被禁令冻结**，无替代路径 | §7.3 | **需决定层裁决** |
| **T-08** | **P2** | **v1.0.1 Release 缺失**，版本归档断档（v1.0 → v1.0.2），历史版本不可回滚 | GitHub Releases 实测 | 受 T-07 约束 |
| **T-09** | **P2** | **组织架构图未上线**，未嵌入任何官网 HTML | `grep sxj-org-structure` 无命中 | **待决定层确认** |
| **T-10** | **P3** | **dept-02 / dept-03 缺 GitHub 禁令条款** | §7.1 | 运维部可补 |
| **T-11** | **P3** | `verify-group-mini/app.wxss:33` 遗留「测试版横幅」死 CSS | 无对应 DOM，用户不可见 | 运维部可清 |
| **T-12** | **P3** | 历史工具 `inject_beta.py` / `inject_beta_current.py` 仍在工作区 | 误运行会重新注入横幅 | 运维部建议删除/归档 |

---

## 九、光锥运维部建议

### R-01（最高优先 · 呈决定层裁决）：解决 .com 与 App 的通道冻结

GitHub 禁令与「hygzz.com、安卓 App 唯一发布通道是 GitHub」构成硬冲突。**请决定层三选一**：

- **方案甲**：对 `sxj-international`（.com）与 `sxj-android-app` 两个**特定仓库**授予**常设例外**，其余一律禁止。运维部每次推送前在记录本登记。（**推荐**：改动最小，保留发布能力）
- **方案乙**：**逐次授权**——每次推送前单独报批。安全性最高，但发版节奏受限。
- **方案丙**：**迁移通道**——.com 内容迁至腾讯云 COS + 自有证书（同 top 模式）；App 改本地构建 + 自建分发页。彻底摆脱 GitHub，但工作量大、需新的证书与分发方案。

> 在决定层裁决前，运维部**默认按最严格口径执行：不推送任何内容到 GitHub**，T-02 / T-08 相应挂起。

### R-02（P0 · 请始创者立即执行）：吊销 PAT

安全合规部 `security-report-01.md` 已取证：**12 个脚本中是同一枚 PAT**，且**未进入 git 历史、未推送公开远端**。

> **意味着：吊销这 1 枚 token 即可一次性关闭全部 12 个暴露面，成本极低。**

建议动作顺序：① 始创者登录 GitHub → Settings → Developer settings → 吊销 `ghp_8fJT…`；② 如仍需 GitHub 能力（取决于 R-01 裁决），重签**最小权限**新 PAT，仅经 `GH_PAT` 环境变量注入；③ 运维部随后把 12 个脚本统一改为 `os.environ.get` 读取（对齐 `pm/tools/github_put.py` 的正确写法）。

### R-03（P1 · 一次修复三站）：清理 BETA 与版本元数据

**在标准源 `hygzz-top-site` 一处改，再同步下发**：

1. `hygzz-top-site/app/js/app.js:108` → `版本 1.0.2 · 数据更新 2026-08-01`（去 BETA）；
2. `hygzz-top-site/version.json` → `version: 1.0.2`、url 指向 **v1.0.2**（现存且 200）、notes 去 BETA；
3. 重跑 `pm/tools/sync_top_to_cn.py` 下发到 cn；
4. 部署：cn 走 wrangler（**记得 `--branch main`**）；top 待 COS 密钥（T-03）。

> 一次动作同时闭环 T-01、T-02，并把 hygzz03 遗留的 NEW-1 彻底关掉。

### R-04（P1 · 请始创者提供）：解锁 hygzz.top

请授权二选一：① 提供 `TENCENT_SECRET_ID` / `TENCENT_SECRET_KEY`（运维部以环境变量注入，**不落盘、不入库**）；② 授权运维部运行 `tcb_upload.py upload`。
解锁后 top 可一次性补齐：知识树 v1.2 + version.json 修正 + app.js 去 BETA（T-01/T-02/T-03 三项同时闭环）。

### R-05（流程 · 立即生效）：标准源清洁度闸门

同步 A 的教训是**「标准源不干净 → 同步放大缺陷」**。建议在 `pm/RELEASE_CHECKLIST.md` 第 4 项后补一条：

```
□ 4b. 标准源闸门：以 hygzz.top 为源同步前，先对源目录做全类型扫描
       （html/js/json/css/wxml/md），0 命中方可同步。
       —— 依据：2026-08-01 同步 A 曾把 app.js 的 BETA 从 top 带入 cn。
```

同时将第 4 项「BETA 清洁度」的扫描范围**显式加入 `.js`**——本次两个 P1 发现（T-01、T-02）都藏在非 HTML 资源里，正是 `verify_all.py` 的口径盲区。

### R-06（P3 · 运维部自办）：补齐禁令条款与清理死代码

- 为 `dept-02-verification.md`、`dept-03-theory.md` 补「工作原则：未经决定层许可，不将任何资源提交至 GitHub」；
- 清理 `verify-group-mini/app.wxss` 死 CSS（T-11）；
- 归档或删除 `inject_beta*.py`（T-12），防止误运行重新注入横幅。

### R-07（治理 · 建议纳入 DoD）：版本单一真相源

T-02 的死链暴露了 hygzz03 OPT-6 未落地的代价：App 已到 1.0.2，网站侧三处副本还停在 1.0.1/1.0.0，**且无人反查 Release 是否真实存在**。建议：

1. 建 `VERSIONS.json` 唯一真相源 + `sync_versions.py` 下发；
2. 校验脚本增加一条**在线断言**：`version.json` 的 `url` 必须实际返回 **HTTP 200**——本次死链正是缺这一条才漏网。

---

## 十、运维部总体评价

1. **执行侧质量高**：确认项 2 / 3 / 4 / 5 四项主体工程均通过线上实测验证，无虚报。hygzz02 上一轮指出的 P1 缺陷（profile.wxml 误删）**已确认真实修复**，且脚本已加配平护栏，属**闭环良好**的整改。

2. **记录本诚实度高**：`ygzz01_record.md` 对 hygzz.top 未部署、小程序未上传两项**主动标注为阻塞**，未粉饰。经本次实地核查**全部属实**。

3. **本轮暴露的系统性短板是「验证口径」**：两个新增 P1（T-01 JS 层 BETA、T-02 死链）都**不在既有验证脚本的扫描范围内**。这与 hygzz03 提出 NEW-1 时的成因完全相同——**同一类问题第二次以同一方式漏网**。说明 RELEASE_CHECKLIST 第 4 项虽已写明「不只扫 HTML」，但**未落实到工具**。R-05 即针对此点。

4. **最大的非技术风险是 T-07（通道冻结）**：禁令本身正确且必要，但需要配套的替代路径或例外清单，否则 .com 与 App 将进入**长期无法更新**的静默状态——这种「因合规而僵死」的风险，比一次违规推送更难被察觉。

5. **P0 项（T-04 吊销 PAT）成本极低而收益极高**，且**只能由始创者本人完成**，是当前最应优先落地的一件事。

---

*—— 光锥运维部，2026-08-01*
*本报告仅作审计，未修改任何源码、未执行任何部署。*
