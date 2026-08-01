# hygzz03 优化方案（Optimizer Proposals）

- **优化师**：hygzz03（Optimizer）
- **输入**：`pm/ygzz01_record.md`（修改记录本）+ `pm/ygzz02_audit.md`（审查报告）
- **产出时间**：2026-08-01
- **工作区**：`C:\Users\Administrator\WorkBuddy\2026-07-24-23-26-27\`
- **声明**：本文档**未修改任何源码**，仅做只读复核与方案设计。所有代码块均为「建议实施内容」，尚未落盘。

---

## 〇、复核结论与新增发现

我对 hygzz02 的五条问题逐一做了只读复现，**全部属实**。在此基础上，另发现 **4 项审查未覆盖的问题**，其中 2 项为 P1，且有 1 项会直接放大审查建议的执行风险。

### 0.1 审查结论复现情况

| 审查项 | 级别 | 复现结果 |
|--------|------|----------|
| M-01 `profile.wxml` 标签不配平 | P1 | ✅ 复现：`<view` 开 21 / `</view>` 闭 22 |
| K-01 v1.2 三站未部署 | P2 | ✅ 复现：`hygzz.cn`、`hygzz.top` 线上仍 `知识树 v1.1` |
| A-01 tag 与版本错位 | P2 | ✅ 复现：`build.yml:62` 硬编码 `gh release upload v1.0` |
| K-01 页脚自述不符 | P3 | ✅ 复现：`knowledge_tree.html:577`「本树为已上传官网…」 |
| 全局改动未提交 git | P3 | ✅ 复现：78 个 `M` + 52 个 `??` |

### 0.2 新增发现（审查未覆盖）

| 编号 | 级别 | 问题 | 证据 |
|------|------|------|------|
| **NEW-1** | **P1** | **线上仍存在活的 BETA 文案**：`https://hygzz.top/version.json` 实际返回 `"version": "1.0.0"` 与 `"notes": "事现鉴 App v1.0 BETA"`。W-01「六端点全清」结论**存在盲区**——`verify_all.py` 只扫 HTML 页面，未扫 `.json` 等非页面资源 | `curl https://hygzz.top/version.json` 实测 |
| **NEW-2** | **P1** | **12 个未跟踪 `.py` 脚本内含明文 GitHub PAT**，且 `.gitignore` 未覆盖。若按审查 P3 建议直接 `git add -A` 归档，**会把 12 份可用令牌提交入库** | `gh_release.py:3`、`github_clean_push.py:7`、`push_android.py:3` 等 |
| **NEW-3** | P2 | 应用商店文案 `STORE_GUIDE.md` 仍 3 处写「BETA 测试版」/「BETA, works offline」，将随上架把 BETA 重新暴露给用户 | `sxj-android-app/STORE_GUIDE.md:97,105,108` |
| **NEW-4** | P2 | **误伤正则存在第二份副本**：`github_clean_push.py:16` 与 `remove_banner.py:17` 是同一条 buggy 正则。只修一处，下次跑另一个脚本仍会再次误删 | 两文件比对一致 |

### 0.3 部署拓扑澄清（影响后续所有部署动作）

审查第 2.1 节与 `github_clean_push.py:4` 注释对回源平台的描述**互相矛盾**。实测响应头判定如下：

| 端点 | `Server` | 关键头 | 真实回源 | URL 形态 |
|------|----------|--------|----------|----------|
| hygzz.cn | `cloudflare` | 无 GitHub 头 | **CF Pages（Direct Upload）** | clean URL |
| hygzz.com | `cloudflare` | `x-github-request-id` | **GitHub Pages + CF 代理层** | clean URL |
| hygzz.top | `tencent-cos` | `x-cos-request-id` | **腾讯云 COS 直出** | **必须带 `.html`** |

> **关键推论**：`hygzz.com` 是「GitHub Pages 套 Cloudflare 代理」。推完 GitHub Pages 后 **CF 边缘缓存不会立刻失效**，若不purge 缓存就验证，会误判为「部署失败」。这正是本轮容易踩的坑，已写入 OPT-4 步骤。

---

## 一、优化动作总览

| 编号 | 动作 | 优先级 | 工作量 | 依赖 |
|------|------|--------|--------|------|
| OPT-1 | 修复 `profile.wxml` 结构缺陷 + 收紧横幅正则（双副本） | **P1** | 小 | — |
| OPT-2 | git 归档**安全前置**：密钥隔离 + `.gitignore` 加固 + 分批提交 | **P1** | 小 | 须早于任何 `git add` |
| OPT-3 | 线上与仓库的 BETA / 版本元数据残留清理 | **P1** | 小 | — |
| OPT-4 | 知识树 v1.2 一键部署三站 + 安卓 1.0.2 重建 | P2 | 中 | OPT-3 |
| OPT-5 | 安卓发版 tag 规范化（按 versionName 动态建 tag） | P2 | 小 | 建议先于 OPT-4 的重建 |
| OPT-6 | 跨平台版本号单一真相源（VERSIONS.json） | P2 | 中 | OPT-5 |

**建议执行序**：`OPT-2 → OPT-1 → OPT-3 → OPT-5 → OPT-6 → OPT-4`

> 为何 OPT-2 排第一：它是**安全闸门**。在密钥仍散落在工作区的状态下执行任何归档动作都可能造成令牌泄漏，且一旦提交进 git 历史，清理成本远高于事前隔离。

---

## OPT-1　修复 profile.wxml 结构缺陷 + 收紧横幅正则

- **优先级**：P1　**工作量**：小　**对应**：需求 ①④，审查 P1，新增 NEW-4

### 1.1 问题与根因

`remove_banner.py:17` 的正则：

```python
WXML_BETA = re.compile(r'<view class="beta-banner"[^>]*>(?:.*?</view>){1,6}\s*</view>', re.S)
```

`(?:...){1,6}` 是**贪婪重复**，会优先尝试匹配 6 次。回溯过程实际吞掉的范围远超横幅本体：

```
<view class="beta-banner">      ← 匹配起点
  ├ </view>  ×1  bb-row 闭合        ← 横幅内部，应删
  ├ </view>  ×2  bb-sub 闭合        ← 横幅内部，应删
  ├ </view>  ×3  beta-banner 闭合   ← 横幅边界，应删（正确终点在此）
  ├ </view>  ×4  hero-title 闭合    ← 越界！
  ├ </view>  ×5  hero-desc  闭合    ← 越界！
  ├ </view>  ×6  hero      闭合     ← 越界！
  └ \s*</view>   为满足尾部约束继续回溯，最终吃到
                 stats-bar 首个 stat-item 的闭合         ← 匹配终点
```

净效果：横幅 + `hero` 整块 + `stats-bar` 开标签 + 第一个 `stat-item`（「已记录」）被一并删除，遗留一个孤立 `</view>`（现 `profile.wxml:7`）。

**同一条 buggy 正则在 `github_clean_push.py:16` 存在第二份副本**（NEW-4），必须同步修复，否则该脚本下次执行会再度误删。

### 1.2 预期收益

- 恢复个人页标题区与「已记录」统计项，消除 WXML 标签不配平的渲染异常风险；
- 解除 M-01 的发布阻塞，使小程序具备上传条件；
- 根治误删机制，避免后续任何一次横幅清理重蹈覆辙。

### 1.3 执行步骤

**Step 1｜恢复 `profile.wxml` 结构**

以 git 基线 `a378fb8` 为准，恢复被误删的三段，**仅删除 `beta-banner` 本体**，同时保留现有的 1.0.1 版本文案（现 17–19 行）。目标头部形态：

```wxml
<view class="container">
  <view class="hero">
    <view class="hero-title">大家的事现</view>
    <view class="hero-desc">事现鉴 · 客户端输入端</view>
  </view>

  <view class="stats-bar">
    <view class="stat-item">
      <view class="stat-num">{{stats.events}}</view>
      <view class="stat-label">已记录</view>
    </view>
    <view class="stat-item">
      <view class="stat-num">{{stats.verifiers}}</view>
      <view class="stat-label">验证人</view>
    </view>
  </view>
```

参考基线内容可用只读方式取出，避免手抄出错：

```bash
git show a378fb8:sxj-mini/weapp-client/pages/profile/profile.wxml > /tmp/profile.baseline.wxml
```

**Step 2｜验证配平**（修复后必须为 24 / 24）

```bash
f=sxj-mini/weapp-client/pages/profile/profile.wxml
echo "开: $(grep -o '<view' $f | wc -l)  闭: $(grep -o '</view>' $f | wc -l)"
```

**Step 3｜用「平衡扫描」替换正则**（`remove_banner.py` 与 `github_clean_push.py` **两处同改**）

正则天然无法处理嵌套同名标签，建议改为深度计数，确定性删除：

```python
def cut_balanced_view(s: str, cls: str) -> str:
    """删除 class=cls 的 <view> 块（含其全部嵌套子节点），按标签深度精确配平。"""
    open_pat = re.compile(r'<view\b[^>]*class="[^"]*\b%s\b[^"]*"[^>]*>' % re.escape(cls))
    tag_pat = re.compile(r'<view\b[^>]*?(/?)>|</view>')
    while True:
        m = open_pat.search(s)
        if not m:
            return s
        depth, i = 0, m.start()
        for t in tag_pat.finditer(s, m.start()):
            if t.group(0).startswith('</'):
                depth -= 1
            elif not t.group(1):          # 排除自闭合 <view ... />
                depth += 1
            if depth == 0:
                i = t.end()
                break
        else:
            raise ValueError(f'unbalanced <view class="{cls}">')
        s = s[:m.start()] + s[i:]
```

调用点相应改为 `s = cut_balanced_view(s, "beta-banner")` / `cut_balanced_view(s, "prov-note")`。

**Step 4｜加装写入前自检护栏**

在 `process()` 写盘前插入不变量校验，让脚本**宁可报错也不写坏文件**：

```python
if ext == ".wxml":
    if s.count("<view") != s.count("</view>"):
        print(f"[ABORT] 标签不配平，跳过写入: {path}")
        return False
```

**Step 5｜新增 `--dry-run` 模式**：先输出将删除的片段与行数差，人工确认后再实际写盘。

**验收标准**：`profile.wxml` 24/24 配平；页面含 `hero`、`已记录`、`验证人`、`小程序版本 1.0.1 · 正式版`；两个脚本对已清理文件重跑均为 0 改动（幂等）。

---

## OPT-2　git 归档安全前置：密钥隔离 + .gitignore 加固 + 分批提交

- **优先级**：P1　**工作量**：小　**对应**：需求 ⑤，审查 P3，新增 NEW-2
- ⚠️ **本动作必须先于任何 `git add` 执行**

### 2.1 问题

审查 P3 建议「提交归档」，方向正确，但**当前直接执行会造成密钥泄漏**。实测工作区 12 个**未跟踪**脚本硬编码了明文 GitHub PAT：

```
gh_release.py:3            gh_update_icons.py:3       gh_update_release.py:3
gh_update_release_v3.py:3  gh_upload.py:3             gh_upload2.py:3
gh_upload_new_apk.py:3     github_clean_push.py:7     poll_and_verify.py:3
push_android.py:3          push_icons_a.py:5          push_icons_c.py:5
```

现有 `.gitignore` 只覆盖了 `wrangler-tmp/`、`*.log`、`.workbuddy/`、小程序私钥，**不覆盖这批脚本**。同时 `npm_cache/`（182 MB）也未被忽略。

当前待归档规模：**78 个 `M` + 52 个 `??`**，一次性 `git add -A` 既会吞入令牌，也会吞入约 180 MB 缓存。

### 2.2 预期收益

- 阻断 12 份可用令牌进入 git 历史（一旦提交，需 filter-repo 重写历史 + 全量吊销，成本极高）；
- 让归档动作从「高风险」变为「可安全重复执行」；
- 仓库瘦身，避免 180 MB 无关产物污染。

### 2.3 执行步骤

**Step 1｜吊销并改造密钥使用方式**

1. 前往 GitHub → Settings → Developer settings → Personal access tokens，**吊销上述脚本中出现的 PAT**（明文散落在文件系统中，应视为已泄漏）；
2. 重新签发一枚最小权限 PAT，通过环境变量注入，脚本内改为：

```python
import os, sys
TOKEN = os.environ.get("GH_TOKEN", "")
if not TOKEN:
    sys.exit("ERROR: 请设置环境变量 GH_TOKEN")
```

> 参考正例：`deploy_pages.py:7-13` 已采用 `os.environ.get` + 缺失即退出的写法，可直接对齐该风格。

**Step 2｜加固 `.gitignore`**（在现有内容后追加）

```gitignore
# ---- 密钥与凭证 ----
*.pem
*.key
.env
.env.*

# ---- 构建产物 / 缓存 ----
npm_cache/
npm_tmp/
sxj-apk-output*/
sxj-apk-artifact*.zip
*.apk
__pycache__/

# ---- 一次性抓取产物 ----
aud_*.html
qw_*.json
```

**Step 3｜提交前密钥扫描（强制闸门）**

```bash
git diff --cached -U0 | grep -nE "ghp_[A-Za-z0-9]{20,}|github_pat_|cfat_|AKID[A-Za-z0-9]{20,}" \
  && { echo "❌ 检测到疑似密钥，已阻断提交"; exit 1; } || echo "✅ 无密钥泄漏"
```

建议固化为 `.git/hooks/pre-commit`，实现常态化拦截。

**Step 4｜按主题分批提交**（禁用 `git add -A`，保证历史可读、可回滚）

```bash
# 批次 1：知识树 v1.2（4 份副本）
git add knowledge_tree.html \
        hygzz-top-site/knowledge_tree.html \
        hygzz-top-site/app/theory/knowledge_tree.html \
        sxj-android-app/app/src/main/assets/www/theory/knowledge_tree.html
git commit -m "docs(kt): 知识树升级 v1.2（四层权力栈图 + CF/Wrangler/去BETA 节点）"

# 批次 2：小程序 1.0.1 + 结构修复
git add sxj-mini/weapp-client/project.miniapp.json \
        sxj-mini/weapp-client/pages/profile/profile.wxml
git commit -m "fix(mini): 恢复 profile hero/统计项误删，标注版本 1.0.1"

# 批次 3：安卓版本与发版流程
git add sxj-android-app/app/build.gradle \
        sxj-android-app/.github/workflows/build.yml \
        sxj-android-app/version.json
git commit -m "build(android): 1.0.1 + 发版 tag 规范化"

# 批次 4：脚本去密钥化 + gitignore
git add .gitignore remove_banner.py github_clean_push.py
git commit -m "chore(scripts): 正则收紧 + 密钥改环境变量注入"
```

**验收标准**：`git log` 出现 4 条语义清晰提交；`git grep -nE "ghp_[A-Za-z0-9]{20,}" $(git rev-list --all)` 无命中；`git count-objects -vH` 无异常膨胀。

---

## OPT-3　线上与仓库的 BETA / 版本元数据残留清理

- **优先级**：P1　**工作量**：小　**对应**：需求 ④ 延伸，审查 P3，新增 NEW-1 / NEW-3

### 3.1 问题

W-01 被判为 IMPLEMENTED，但验证口径**只覆盖 HTML 页面**，遗漏了非页面资源与仓库文案：

| 位置 | 现状 | 性质 |
|------|------|------|
| `https://hygzz.top/version.json`（**线上活体**） | `"version": "1.0.0"` / `"notes": "事现鉴 App v1.0 BETA"` | **用户可达的 BETA 残留 + 版本落后两级** |
| `hygzz-top-site/version.json`（源） | 同上，且为未跟踪文件 | 线上残留的源头 |
| `sxj-android-app/STORE_GUIDE.md:97,105,108` | 「标注为 BETA 测试版」/「当前为 BETA 测试版」/「BETA, works offline」 | 上架文案，会把 BETA 带回商店页 |
| `knowledge_tree.html:577` | 「本树为已上传官网与白皮书之定版内容」 | 对 v1.2 不成立（审查 P3） |

> `sxj-android-app/version.json` 是 App 的更新检查源（`assets/www/js/app.js:22` 拉取 raw main 分支），内容已是 1.0.1；而 `hygzz-top-site/version.json` 是**网站侧的陈旧副本**，两者已漂移——这也是 OPT-6 要解决的根本问题。

### 3.2 预期收益

- 清除最后一处**用户可直接访问**的 BETA 文案，让「全平台去 BETA」真正闭环；
- 消除商店上架时 BETA 文案回流；
- 让知识树自述与部署事实一致，维护对外表述可信度。

### 3.3 执行步骤

**Step 1｜修正 `hygzz-top-site/version.json`**，与安卓侧对齐（tag 取值依 OPT-5 结果）：

```json
{
  "version": "1.0.1",
  "url": "https://github.com/baixi6313/sxj-android-app/releases/download/v1.0.1/app-debug.apk",
  "notes": "事现鉴 App v1.0.1 正式版"
}
```

**Step 2｜清理 `STORE_GUIDE.md`** 三处 BETA 表述，替换为「正式版 v1.0.1」；英文 `BETA, works offline.` → `Stable release, works offline.`。

**Step 3｜修正知识树页脚自述**（4 份副本同改）。二选一：
- 方案 A（推荐，配合 OPT-4 部署后）：保留原句，部署完成后该句自然成立；
- 方案 B（若暂不部署）：改为「v1.1 已上线三站，v1.2 待部署」。

**Step 4｜扩大验证口径**：升级 `verify_all.py`，把非 HTML 资源纳入扫描：

```python
urls += [
    "https://hygzz.top/version.json",
    "https://hygzz.cn/version.json",
    "https://hygzz.com/version.json",
]
# 关键词表补充 json 场景
KEYS = ["beta-banner", "测试版", "BETA", "v1.0 BETA"]
```

**验收标准**：`curl -s https://hygzz.top/version.json | grep -i beta` 无输出；`verify_all.py` 输出 `ALL CLEAN: True`；仓库内 `grep -rn "BETA" --include=*.json --include=*.md`（排除依赖锁文件）无用户可见命中。

---

## OPT-4　知识树 v1.2 一键部署三站 + 安卓 1.0.2 重建

- **优先级**：P2　**工作量**：中　**对应**：需求 ②，审查 P2

### 4.1 问题

v1.2 源码 4 份副本 100% 就绪（148 KB，含 base64 权力栈图），线上 0% 生效：三站均为 v1.1（约 72 KB），安卓 APK 内嵌树为 59,618 字节旧版且**未推送到安卓远端仓库**。

时间线根因：知识树 v1.2 完成于 10:39–10:42，而 APK 构建于 10:17 —— **构建早于内容就绪 22 分钟**，属典型的「改完堆着、未触发部署」（见 GOV-1）。

### 4.2 预期收益

- 四层权力栈图与三个技术节点真正对外可见，K-01 从 PARTIAL 转为 IMPLEMENTED；
- App 与官网内容一致，消除「App 内知识树比官网旧一版」的体验割裂；
- 沉淀一份可复用的三站部署脚本，后续知识树更新从「多平台手工操作」降为一条命令。

### 4.3 执行步骤

**前置检查**（务必先确认，避免白跑）

```bash
# 三站当前版本基线
for u in "https://hygzz.cn/knowledge_tree" "https://hygzz.com/knowledge_tree" "https://hygzz.top/knowledge_tree.html"; do
  echo "$u -> $(curl -sL --max-time 25 "$u" | grep -o '知识树 v1\.[0-9]' | sort -u | tail -1)"
done
```

同时确认凭证到位：`CF_TOKEN`（**需 Pages:Edit 权限**——历史上曾因令牌被降权为仅 Zone/DNS/SSL 而部署失败）、GitHub PAT、COS 密钥。

**Step 1｜hygzz.cn（Cloudflare Pages，Direct Upload）**

```bash
export CF_TOKEN="<token>"; export ACCT="f26b8425a338a0e385a391781198f360"
python deploy_pages.py            # 复用现成脚本，项目名 hygzz-cn
```

**Step 2｜hygzz.com（GitHub Pages，仓库 `baixi6313/sxj-international`）**

推送更新后的 `knowledge_tree.html`，等待 Pages 构建完成。

> ⚠️ **本轮最易踩的坑**：`hygzz.com` 是 **GitHub Pages 套 Cloudflare 代理**（实测响应头同时含 `Server: cloudflare` 与 `x-github-request-id`）。Pages 构建成功后 **CF 边缘缓存仍会返回旧版**。必须 purge：

```bash
curl -X POST "https://api.cloudflare.com/client/v4/zones/<ZONE_ID>/purge_cache" \
  -H "Authorization: Bearer $CF_TOKEN" -H "Content-Type: application/json" \
  --data '{"purge_everything":true}'
```

**Step 3｜hygzz.top（腾讯云 COS）**

用 `tcb_upload.py` / `push_top.py` 上传 `hygzz-top-site/`。注意 **COS 直出 `.html`，非 clean URL**，验证时必须带后缀。同时把 OPT-3 修正后的 `version.json` 一并上传。

**Step 4｜安卓 1.0.2 重建**

1. 将 v1.2 知识树推送到 `baixi6313/sxj-android-app` 的 `assets/www/theory/knowledge_tree.html`（当前远端仍为 59,618 字节旧版）；
2. `build.gradle` → `versionCode 3` / `versionName "1.0.2"`（建议由 OPT-6 的 `sync_versions.py` 生成）；
3. 推送触发 Actions，按 OPT-5 的动态 tag 发布至 `v1.0.2`；
4. 同步更新两处 `version.json` 的 `version` 与 `url`。

**Step 5｜统一验收**

```bash
# Web 三站（注意 top 带 .html）
for u in "https://hygzz.cn/knowledge_tree" "https://hygzz.com/knowledge_tree" "https://hygzz.top/knowledge_tree.html"; do
  b=$(curl -sL --max-time 30 "$u"); \
  echo "$u | $(echo "$b" | wc -c) 字节 | $(echo "$b" | grep -c '四层权力栈') 权力栈 | $(echo "$b" | grep -o '知识树 v1\.[0-9]' | sort -u | tail -1)"
done

# APK 内嵌树
curl -sL "https://github.com/baixi6313/sxj-android-app/releases/download/v1.0.2/app-debug.apk" > online.apk
unzip -o -q online.apk "assets/www/theory/knowledge_tree.html" -d apkx
grep -c '四层权力栈' apkx/assets/www/theory/knowledge_tree.html
```

**验收标准**：三站响应体积约 148 KB（而非 72 KB）、`四层权力栈` 命中 3、版本串为 `知识树 v1.2`；APK 内嵌树 `四层权力栈` ≥ 1。

---

## OPT-5　安卓发版 tag 规范化

- **优先级**：P2　**工作量**：小　**对应**：需求 ③，审查 P2

### 5.1 问题

`build.yml:62` 把 tag 写死：

```yaml
run: gh release upload v1.0 app/build/outputs/apk/debug/app-debug.apk --clobber --repo baixi6313/sxj-android-app
```

后果：1.0.1 的 APK 覆盖式上传到 `v1.0` 之下，仓库中不存在 `v1.0.1` Release。功能可用（用户能取到 1.0.1），但**历史版本被物理覆盖、无法回滚**；`--clobber` 使每次发版都销毁前一版产物。发 1.0.2 时问题会继续放大。

### 5.2 预期收益

- 每个版本拥有独立 Release，可追溯、可回滚、可对外给出稳定的版本化下载链；
- 消除人工改 yml 的环节，杜绝「版本升了但 tag 忘了改」；
- 为 OPT-6 的自动化版本流水线提供落点。

### 5.3 执行步骤

**Step 1｜从 `build.gradle` 提取 versionName 并动态建 tag**，替换 `build.yml` 末尾步骤：

```yaml
      - name: Resolve version
        id: ver
        run: |
          V=$(grep -oP 'versionName\s+"\K[^"]+' app/build.gradle)
          echo "version=$V" >> $GITHUB_OUTPUT
          echo "解析到 versionName = $V"

      - name: Publish APK to versioned Release
        env:
          GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        run: |
          TAG="v${{ steps.ver.outputs.version }}"
          gh release view "$TAG" --repo baixi6313/sxj-android-app >/dev/null 2>&1 \
            || gh release create "$TAG" --title "事现鉴 App $TAG" --notes "自动构建发布 $TAG" --repo baixi6313/sxj-android-app
          gh release upload "$TAG" app/build/outputs/apk/debug/app-debug.apk --clobber --repo baixi6313/sxj-android-app
```

**Step 2｜补建历史 Release**：为已发布的 1.0.1 补一个 `v1.0.1` tag 与 Release，把现有 APK 归位（保留 `v1.0` 不动，维持旧链接可用）。

**Step 3｜同步 `version.json` 的 `url`** 指向 `/download/v1.0.1/app-debug.apk`（两处副本，见 OPT-3 / OPT-6）。

**Step 4｜考虑 latest 稳定链**：若希望下载地址长期不变，可用 `releases/latest/download/app-debug.apk`，兼顾稳定链接与版本化归档。

**验收标准**：Releases 列表出现 `v1.0.1`（后续 `v1.0.2`）；旧 `v1.0` 资产未被破坏；`version.json` 的 url 可直接下载到对应版本。

---

## OPT-6　跨平台版本号单一真相源

- **优先级**：P2　**工作量**：中　**对应**：需求 ⑥

### 6.1 问题

版本号目前分散在**至少 6 处**手工维护，已实际发生漂移：

| 位置 | 当前值 | 状态 |
|------|--------|------|
| `sxj-android-app/app/build.gradle` | `versionName "1.0.1"` / `versionCode 2` | ✅ |
| `sxj-android-app/version.json` | `1.0.1` | ✅ |
| `hygzz-top-site/version.json` | **`1.0.0` + BETA** | ❌ **已漂移** |
| `sxj-mini/weapp-client/project.miniapp.json` | `1.0.1` / `101` | ✅ |
| `sxj-mini/.../profile.wxml:18` | `小程序版本 1.0.1 · 正式版` | ✅ 但为硬编码文案 |
| `knowledge_tree.html` 页脚（×4 副本） | `v1.2` / 落地层 `v1.0.1` | ✅ 但需人工同步 4 份 |

本轮的 A-01 / K-01 两处不一致（APK 内嵌旧树、website version.json 落后）**根本原因都是缺少单一真相源**。

### 6.2 预期收益

- 一处改、多处生成，从机制上消除版本漂移；
- 发版前可自动校验一致性，把「人工记得改 6 个地方」变成「一条命令 + 一次断言」；
- 与 OPT-5 的动态 tag 组合，形成完整的版本化发布链路。

### 6.3 执行步骤

**Step 1｜建立 `VERSIONS.json`（仓库根，唯一真相源）**

```json
{
  "app":          { "versionName": "1.0.2", "versionCode": 3 },
  "miniprogram":  { "version": "1.0.1", "versionCode": 101 },
  "knowledgeTree":{ "version": "1.2", "updated": "2026-08-01" },
  "web":          { "version": "1.0.1" },
  "releaseNotes": "事现鉴 App v1.0.2 正式版（内嵌知识树 v1.2）"
}
```

**Step 2｜编写 `sync_versions.py` 生成器**，从 `VERSIONS.json` 回写全部下游：

| 下游文件 | 注入字段 |
|----------|----------|
| `sxj-android-app/app/build.gradle` | `versionCode` / `versionName` |
| `sxj-android-app/version.json` | `version` / `url`(含 tag) / `notes` |
| `hygzz-top-site/version.json` | 同上 |
| `sxj-mini/weapp-client/project.miniapp.json` | `version` / `versionCode` |
| `profile.wxml` | 「小程序版本 X · 正式版」文案 |
| `knowledge_tree.html` ×4 | 页脚版本串与落地层版本 |

实现要点：对 `profile.wxml` 与知识树页脚采用**锚点标记替换**而非裸正则（吸取 OPT-1 教训）。建议在模板中埋注释锚点：

```wxml
<!-- SXJ:VERSION:START -->小程序版本 1.0.1 · 正式版<!-- SXJ:VERSION:END -->
```

替换时只作用于锚点之间，杜绝越界误伤。

**Step 3｜编写 `verify_versions.py` 一致性断言**，反向读取全部下游并与 `VERSIONS.json` 比对，任一不符即非零退出，接入发布检查清单（GOV-2）。

**Step 4｜知识树 4 副本改为「主文件 + 分发」**：以根目录 `knowledge_tree.html` 为唯一源，由脚本 `cp` 到其余 3 处，彻底消除「改了 3 份漏 1 份」的可能。

**验收标准**：改 `VERSIONS.json` 一处 → 运行 `sync_versions.py` → `git diff` 显示全部下游同步更新；`verify_versions.py` 退出码为 0。

---

## 二、治理 / 流程层优化

### GOV-1　把「已部署」写进完成定义（Definition of Done）

**问题**：本轮 4 条记录中 **2 条卡在「已改源码、未部署」**（M-01、K-01）。K-01 的 APK 之所以内嵌旧树，正因内容就绪比构建晚 22 分钟——**改动完成与发布触发之间没有强制衔接**。

**方案**：

1. **记录本状态机收敛为四态**，并规定 `已改源码` **不是**终态：
   `待实施 → 已改源码 → 已部署 → 已验证`
2. **「已验证」必须附线上证据**（curl 命中数 / APK 反解结果），禁止仅凭本地 diff 判定完成。这一点 hygzz02 的审查方法已经建立了很好的范式，应固化为常规要求而非事后审查。
3. **内容类改动即时触发部署**：知识树等静态内容改完立即跑部署脚本；若因凭证缺失无法部署，必须在记录本登记为**阻塞项**并写明所缺凭证（如「CF Token 缺 Pages:Edit」），而非默默留在「已改源码」。
4. **构建顺序约束**：涉及内嵌资源的 App 发版，遵循「先同步资源 → 再升版本号 → 最后触发构建」，避免再次出现构建早于内容就绪。

### GOV-2　发布检查清单 + 一键校验脚本

**问题**：本轮暴露的问题高度同质——正则误伤无人校验、tag 与版本错位无人比对、线上 `version.json` 无人扫描。缺的不是能力，是**固定的出口检查**。

**方案**：建立 `pm/RELEASE_CHECKLIST.md`，每次发布逐项打勾：

```
□ 1. 结构完整性：WXML/HTML 标签配平（<view> 开闭相等）
□ 2. 版本一致性：verify_versions.py 退出码 0
□ 3. 密钥安全：暂存区无 ghp_/cfat_/AKID 命中
□ 4. BETA 清洁度：HTML + JSON + MD 全类型扫描 0 命中
□ 5. 部署生效：三站 curl 命中预期版本串（top 记得带 .html）
□ 6. 缓存刷新：hygzz.com 已 purge CF 缓存
□ 7. 产物校验：APK 反解 versionName 与内嵌知识树版本正确
□ 8. 版本化归档：Release tag 与 versionName 一致
□ 9. git 归档：改动已分批提交，提交信息语义清晰
```

进一步可合并为一条命令 `python preflight.py`，串联 `verify_versions.py` + 密钥扫描 + `verify_all.py`，任一失败即阻断发布。

**预期收益**：把「靠人记得」变成「机器兜底」。本轮 9 个问题中，至少 7 个可被上述清单在发布前拦截。

---

## 三、落地路线（建议分三批）

| 批次 | 内容 | 目标状态 |
|------|------|----------|
| **第一批（安全与阻塞）** | OPT-2 密钥隔离 → OPT-1 结构修复 → OPT-3 元数据清理 | 消除令牌泄漏风险；小程序具备上传条件；线上再无 BETA |
| **第二批（发布链路）** | OPT-5 tag 规范化 → OPT-6 单一真相源 | 版本可追溯、不漂移 |
| **第三批（内容上线）** | OPT-4 三站部署 + 安卓 1.0.2 重建 | K-01 转 IMPLEMENTED，全平台内容对齐 |
| **贯穿** | GOV-1 完成定义 + GOV-2 检查清单 | 问题不再复发 |

---

## 四、风险提示

| 风险 | 影响 | 缓解 |
|------|------|------|
| 直接 `git add -A` 归档 | **12 份 PAT 入库**，需重写历史 + 全量吊销 | 严格执行 OPT-2，pre-commit 钩子强制拦截 |
| CF Token 权限不足（历史已发生） | 部署静默失败，误判为已上线 | 部署前先验权；以 curl 实测结果为准，不信脚本自报成功 |
| 忘记 purge `hygzz.com` 的 CF 缓存 | 内容已推送但线上仍旧版，误判部署失败并重复操作 | 纳入 GOV-2 第 6 项 |
| 只修 `remove_banner.py` 未修 `github_clean_push.py` | 下次运行再次误删页面结构 | OPT-1 Step 3 明确双副本同改 |
| 用 `.top` 的 clean URL 探测 | 误报 404 / 误判未部署 | COS 站验证一律带 `.html` |

---

*—— hygzz03（Optimizer），2026-08-01*
