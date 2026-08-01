# hygzz02 审查报告（Auditor Report）

- **审查员**：hygzz02（Auditor）
- **审查对象**：hygzz01 记录本 `pm/ygzz01_record.md` 中 W-01 / M-01 / A-01 / K-01 四条记录
- **审查时间**：2026-08-01
- **工作区**：`C:\Users\Administrator\WorkBuddy\2026-07-24-23-26-27\`
- **审查方式**：源码只读核查（Read / Grep）+ 线上实地抽查（curl）+ 线上产物反解（APK 解包）
- **声明**：本次审查未修改任何源码，仅做只读核查。

---

## 一、结论总表

| 编号 | 记录内容 | 源码 | 线上部署 | 综合结论 |
|------|----------|------|----------|----------|
| W-01 | 六端点清除 BETA 横幅 | ✅ 无残留 | ✅ 6/6 端点已生效 | **IMPLEMENTED** |
| M-01 | 小程序 1.0.1 + 去 BETA | ✅ 全部达成 | ⚠️ 未发布（需手动） | **IMPLEMENTED（源码）／未上线**，另发现 1 处结构性缺陷 |
| A-01 | 安卓升 1.0.1 + 自动发版 | ✅ 全部达成 | ✅ APK 已上线且确为 1.0.1 | **IMPLEMENTED**，但发版 tag 命名有隐患 |
| K-01 | 知识树升级 v1.2 | ✅ 4 处副本全同步 | ❌ 三站均仍为 v1.1 | **PARTIAL（仅源码，未部署）** |

**一句话总览**：W-01、A-01 已真正落地到线上；M-01、K-01 属「只改了源码、尚未上线」。此外发现 1 个记录本未提及的**小程序页面结构被误删**缺陷。

---

## 二、W-01 网站六端点清除 BETA 横幅 → **IMPLEMENTED**

### 2.1 端点可达性

| 端点 | HTTP | 说明 |
|------|------|------|
| hygzz.cn | 200 | Cloudflare Pages（clean URL） |
| www.hygzz.cn | 200 | 同上 |
| hygzz.com | 200 | GitHub Pages（clean URL） |
| www.hygzz.com | 200 | 首探曾出现一次 `000`，连续 3 次复测均 200，判定为瞬时抖动 |
| hygzz.top | 200 | 腾讯云 COS，**直出 .html，非 clean URL** |
| www.hygzz.top | 200 | 同上 |

### 2.2 线上横幅扫描（关键词：`beta-banner` / `测试版 BETA` / `⚠️ 测试版`）

**首页（6/6 端点）**：命中数全部为 **0**。

```
hygzz.cn      | 158741 字节 | 命中 0
www.hygzz.cn  | 158741 字节 | 命中 0
hygzz.com     | 238714 字节 | 命中 0
www.hygzz.com | 238714 字节 | 命中 0
hygzz.top     |  11126 字节 | 命中 0
www.hygzz.top |  11126 字节 | 命中 0
```

**子页面抽查**：

- cn / com 双域（clean URL）：`knowledge_tree`、`whitepaper`、`events`、`co_creation`、`concept_tree`、`framework_glossary`、`qualitative_analysis`、`ai_understanding`、`critical_synthesis_report` → 命中全部为 0。
- top 双域（补 `.html` 后缀重测）：`knowledge_tree.html`、`whitepaper.html`、`events.html`、`co_creation.html`、`concept_tree.html`、`cv.html` → 均 HTTP 200，命中全部为 0。

> **方法学修正**：任务书提示「CF Pages 用 clean URL」。实测 cn/com 确为 clean URL，但 **hygzz.top（腾讯云 COS）恰恰相反，必须带 `.html`**。首轮对 top 用无后缀路径探测得到的 404 属探测方式错误，补测后 6 端点子页面全部可达且干净。

### 2.3 源码侧核查

对全工作区 `*.html / *.wxml / *.wxss / *.css`（排除 `node_modules`、`_archive`）扫描 `beta-banner|测试版 BETA|⚠️ 测试版`：

```
（无任何命中）
```

### 2.4 结论

线上 6 端点 + 源码两侧均无 BETA 横幅残留，**与记录本「✅ 已部署」相符，认定 IMPLEMENTED**。

---

## 三、M-01 微信小程序 1.0.1 + 去 BETA → **IMPLEMENTED（源码）／未上线**，含 1 处缺陷

### 3.1 声明项逐条核验（全部达成）

**① 版本号** — `sxj-mini/weapp-client/project.miniapp.json:4-5`

```json
"version": "1.0.1",
"versionCode": 101,
```

**② 版本文案** — `sxj-mini/weapp-client/pages/profile/profile.wxml:18`

```
小程序版本 1.0.1 · 正式版
```

位于「关于」卡片内，带 `color:#8a5a2b;font-weight:700` 强调样式。

**③ BETA 残留** — 扫描 `weapp-client` 全目录，仅 3 处命中，均为第三方依赖版本号，非用户可见文案：

```
cloudfunctions/conserve/package-lock.json:29   "@cloudbase/signature-nodejs": "1.0.0-beta.0"
cloudfunctions/conserve/package-lock.json:47   "version": "1.0.0-beta.0"
cloudfunctions/conserve/package-lock.json:1348 "@cloudbase/signature-nodejs": "^1.0.0-beta.0"
```

判定：**无用户可见 BETA 残留**，达标。

### 3.2 ⚠️ 新发现缺陷（记录本未提及）：横幅删除误伤页面结构

`profile.wxml` 当前标签不配平：

```
总行数 44 ｜ <view 开标签 21 个 ｜ </view> 闭标签 22 个   ← 多出 1 个闭合标签
```

对比 git 基线 `a378fb8` 的原始版本，除 BETA 横幅外，以下内容被**一并误删**：

| 被删内容 | 原始位置 | 现状 |
|----------|----------|------|
| `<view class="hero">` 整块（大家的事现 / 事现鉴 · 客户端输入端） | 原 6-9 行 | 已消失 |
| `<view class="stats-bar">` 开标签 | 原第 11 行 | 已消失（其闭合标签遗留） |
| 第一个 `stat-item`（`{{stats.events}}` / 「已记录」） | 原 12-15 行 | 已消失 |

当前文件开头残留形态：

```wxml
<view class="container">
  
    <view class="stat-item">
      <view class="stat-num">{{stats.verifiers}}</view>
      <view class="stat-label">验证人</view>
    </view>
  </view>          ← 孤立闭合标签
```

**根因定位**：`remove_banner.py:17`

```python
WXML_BETA = re.compile(r'<view class="beta-banner"[^>]*>(?:.*?</view>){1,6}\s*</view>', re.S)
```

该正则贪婪跨越至多 6 个 `</view>`，越过了横幅自身边界，连带吞掉 hero 区块、stats-bar 开标签与首个统计项。

**影响**：个人页丢失标题区与「已记录」统计项，且 WXML 标签不配平，存在渲染异常风险。**建议在发布前修复**（不属本次审查改动范围）。

### 3.3 部署状态

小程序无法通过 curl 验证线上态，需微信开发者工具手动上传发布。记录本已标注「⚠️ 未部署（沙箱无微信密钥、非 git 仓库）」，与实际相符。

工作区 git 状态显示改动**尚未提交**：

```
 M sxj-mini/weapp-client/pages/profile/profile.wxml
 M sxj-mini/weapp-client/project.miniapp.json
```

### 3.4 结论

三项声明内容均已在源码落实（**IMPLEMENTED**），但**尚未上线**；并存在上述 P1 级结构缺陷，建议修复后再发布。

---

## 四、A-01 安卓 App 升 1.0.1 + 去 BETA + 自动发版 → **IMPLEMENTED**（含线上），tag 命名有隐患

### 4.1 版本号（本地 + 远端一致）

**本地** `sxj-android-app/app/build.gradle:13-14`

```gradle
versionCode 2
versionName "1.0.1"
```

**GitHub 远端**（`main` 与 `master` 分支 raw 均已核对，各 1194 字节）：`versionCode 2` / `versionName "1.0.1"` — 确认源码已推送。

**version.json**（本地与远端内容一致）：

```json
{
  "version": "1.0.1",
  "url": "https://github.com/baixi6313/sxj-android-app/releases/download/v1.0/app-debug.apk",
  "notes": "事现鉴 App v1.0.1"
}
```

### 4.2 去 BETA

`app/src/main/res/values/strings.xml`：

```xml
<string name="app_name">事现鉴</string>
```

无 `(BETA)` 字样。全工程扫描 BETA 仅命中 `assets/www/theory/knowledge_tree.html` 中的**描述性文字**（如「全平台去 BETA 横幅与版本管理」节点标题），属知识树正文内容，非横幅，不构成残留。

### 4.3 自动发版

`.github/workflows/build.yml:59-62`

```yaml
- name: Publish debug APK to Release v1.0
  env:
    GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
  run: gh release upload v1.0 app/build/outputs/apk/debug/app-debug.apk --clobber --repo baixi6313/sxj-android-app
```

配套 `permissions: contents: write`（第 11-12 行）已具备。自动发版链路存在且已生效。

### 4.4 线上产物反解验证（最硬证据）

GitHub Releases API 查询结果：**仅存在一个 Release，tag 为 `v1.0`**，无 `v1.0.1`。其资产更新时间 `2026-08-01T02:17:32Z`，大小 176049 字节。

下载该线上 APK 并解包 `AndroidManifest.xml`，从二进制清单抽取版本字符串：

```
UTF-16 抽取到的版本样式字符串: ['1.0.1']
含 1.0.1 : True
```

**判定：线上可下载的 APK 确为 1.0.1 版本，A-01 已真实上线。**

### 4.5 ⚠️ 隐患：发版 tag 与版本号错位

- 1.0.1 的 APK 被 `--clobber` 覆盖上传到 **`v1.0`** 这个旧 tag 之下，仓库中**不存在 v1.0.1 的 Release/tag**。
- `version.json` 的下载 `url` 同样指向 `/download/v1.0/app-debug.apk`。

当前依靠「覆盖同名资产」使更新链路可用，功能上能取到 1.0.1，但语义错位：版本追溯困难，且一旦后续再发 1.0.2 仍覆盖 v1.0，将无法回滚到历史版本。建议改为按 `versionName` 动态创建 tag。

### 4.6 结论

版本号、去 BETA、自动发版三项全部达成，且**已验证线上 APK 确为 1.0.1**，认定 **IMPLEMENTED**。附带 tag 命名规范问题，建议整改。

---

## 五、K-01 知识树升级 v1.2 → **PARTIAL（源码完成，全部未部署）**

### 5.1 源码侧：4 处副本全部同步到 v1.2 ✅

| 文件 | 字节 | 四层权力栈 | v1.2 | Wrangler | 去BETA节点 |
|------|------|-----------|------|----------|-----------|
| `knowledge_tree.html`（主） | 148336 | 3 | 1 | 3 | 3 |
| `hygzz-top-site/knowledge_tree.html` | 148336 | 3 | 1 | 3 | 3 |
| `hygzz-top-site/app/theory/knowledge_tree.html` | 148336 | 3 | 1 | 3 | 3 |
| `sxj-android-app/app/src/main/assets/www/theory/knowledge_tree.html` | 148497 | 3 | 1 | 3 | 3 |

> 注：任务书列出 2 处镜像，实测共 **3 处镜像 + 1 主文件 = 4 份**，均已同步（记录本第 26 行「3 处镜像」的表述与实测一致）。

**① 四层权力栈图（真实内嵌图片，非纯文字）** — `knowledge_tree.html:207-210`

```html
<div class="node"><div class="h"><span class="tag t-m">元</span> 四层权力栈 · 事现鉴居根层</div>
...
<img src="data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQABAAD/..." 
     alt="四层权力栈：应用层/能力层/物理层/根层" ...>
```

确认为 base64 内联 JPEG，这也是文件体积由 ~72KB 增至 148KB 的直接原因。

**② 新增技术节点** — 三个节点均已就位：

```
:427  <span class="tag t-a">技术·坑</span> Cloudflare API Token 三层界面
:430  <span class="tag t-a">技术·坑</span> Wrangler v4 部署 CF Pages 三陷阱
:433  <span class="tag t-a">技术·实践</span> 全平台去 BETA 横幅与版本管理
```

**③ 版本标记** — `knowledge_tree.html:572`

```
… 语料归位更新：2026-07-31（知识树 v1.1）· 部署与权力栈更新：2026-08-01（知识树 v1.2）
```

变更说明见 574-576 行（新增权力栈图 / 技术踩坑节点 / 落地应用升 v1.0.1）。

### 5.2 线上侧：三站全部仍为 v1.1 ❌

| 端点 | 线上字节 | 线上版本 | 四层权力栈 | v1.2 | Wrangler |
|------|----------|----------|-----------|------|----------|
| hygzz.cn | 72763 | **知识树 v1.1** | 0 | 0 | 0 |
| hygzz.com | 71825 | **知识树 v1.1** | 0 | 0 | 0 |
| hygzz.top | 72241 | **知识树 v1.1** | 0 | 0 | 0 |
| （本地源码） | 148336 | 知识树 v1.2 | 3 | 1 | 3 |

线上体积约为本地的一半，与「未嵌入 base64 权力栈图」的事实吻合，交叉印证 v1.2 未部署。

### 5.3 安卓内嵌知识树同样为旧版 ❌

- 线上 APK 内 `assets/www/theory/knowledge_tree.html`：**59618 字节**，`四层权力栈`=0、`v1.2`=0、`Wrangler`=0。
- GitHub 远端同路径文件：**59618 字节**，`v1.2`=0 —— 说明 v1.2 知识树**根本未推送到安卓仓库**。

**时间线佐证**（北京时间）：

```
10:14:07  build.gradle / version.json 改为 1.0.1
10:17:32  GitHub Actions 构建并发布 APK（此时树仍为旧版）
10:39:57  主 knowledge_tree.html 升 v1.2
10:41:18  hygzz-top-site 镜像升 v1.2
10:42:02  安卓 assets 镜像升 v1.2
```

知识树 v1.2 完成时间**晚于** APK 构建时间约 22 分钟，因此已发布的 APK 必然内嵌旧树。此项与记录本第 23 行「⚠️ 内嵌知识树仍为 v1.1，需 v1.0.2 重建」的自述完全一致。

### 5.4 版本控制状态

四份 v1.2 文件在工作区 git 中**均为未提交状态**：

```
 M hygzz-top-site/app/theory/knowledge_tree.html
 M hygzz-top-site/knowledge_tree.html
 M knowledge_tree.html
 M sxj-android-app/app/src/main/assets/www/theory/knowledge_tree.html
?? hygzz-top-site/version.json
?? sxj-android-app/version.json
```

### 5.5 文案自述与事实不符（建议修正）

`knowledge_tree.html:577` 写道：

```
本树为已上传官网与白皮书之定版内容（见 hygzz.com / hygzz.cn / hygzz.top）。
```

而 v1.2 实际尚未上传至上述任一站点。该句对 v1.1 成立、对 v1.2 不成立，建议部署完成后再保留此表述。

### 5.6 结论

源码侧 100% 完成（图 + 3 节点 + 版本标记 + 4 副本同步），线上侧 0% 生效（Web 三站 + 安卓 APK 全部仍为 v1.1）。认定 **PARTIAL**。

---

## 六、「只改源码、未部署上线」清单（重点）

| 项 | 内容 | 现状 | 待办 |
|----|------|------|------|
| **K-01 / Web** | 知识树 v1.2（含权力栈图） | 本地 148KB v1.2；线上 ~72KB v1.1 | 重新部署 CF Pages（cn）、GitHub Pages（com）、腾讯云 COS（top） |
| **K-01 / App** | 安卓内嵌知识树 | 线上 APK 内为 59618 字节旧树，远端仓库亦未推送 | 推送 v1.2 资源 → 升 1.0.2 → 触发 Actions 重建发版 |
| **M-01** | 小程序 1.0.1 | 源码已改且未提交 git | 微信开发者工具手动上传发布（沙箱无密钥）；**发布前先修复 profile.wxml 结构缺陷** |
| 版本控制 | 上述全部改动 | 工作区 git 全部处于 `M` / `??` 未提交状态 | 建议提交归档，避免丢失 |

已真正上线、无需补动作：**W-01（六端点横幅）**、**A-01（安卓 1.0.1 APK）**。

---

## 七、审查发现的问题清单

| 级别 | 编号 | 问题 | 位置 | 建议 |
|------|------|------|------|------|
| **P1** | M-01 | 横幅删除正则误伤，删掉 hero 区块、stats-bar 开标签与首个统计项，`<view>` 标签 21 开 / 22 闭不配平 | `pages/profile/profile.wxml:1-7`；根因 `remove_banner.py:17` | 发布前恢复 hero 与「已记录」统计项，修正标签配平；收紧正则 |
| **P2** | K-01 | v1.2 四处源码就绪但三站 + APK 全未部署 | 见第五节 | 按第六节清单补部署 |
| **P2** | A-01 | 1.0.1 的 APK 发布在 `v1.0` tag 下，无 v1.0.1 Release；`version.json` url 亦指向 v1.0 | `build.yml:62`、`version.json` | 改为按 versionName 动态建 tag，避免覆盖式发版 |
| **P3** | K-01 | 页脚自述「已上传官网」与 v1.2 未部署事实不符 | `knowledge_tree.html:577` | 部署后再保留，或改为「v1.1 已上线，v1.2 待部署」 |
| **P3** | 全局 | 关键改动均未提交 git | 工作区根仓库 | 提交归档 |

**已排除的疑似问题**：首页 `href="$2"` 经核为 JS 中 Markdown 链接转换正则 `.replace(/\[(.*?)\]\((.*?)\)/g, '<a href="$2" …>')` 的一部分（`aud_hygzz.cn.html:2366`），属正常代码，非缺陷。

---

## 八、审查方法与可复现命令

```bash
# 1) 六端点可达性与首页横幅（沙箱 curl -o 可能失效，统一用 shell 重定向）
for d in hygzz.cn www.hygzz.cn hygzz.com www.hygzz.com hygzz.top www.hygzz.top; do
  curl -sL --max-time 25 "https://$d/" > "aud_$d.html"
  echo "$d | $(wc -c < aud_$d.html) | $(grep -c -i 'beta-banner\|测试版 BETA' aud_$d.html)"
done

# 2) 子页面：cn/com 用 clean URL（无 .html）；top 必须带 .html
curl -sL "https://hygzz.cn/knowledge_tree"      > a.html
curl -sL "https://hygzz.top/knowledge_tree.html" > b.html

# 3) 线上知识树版本判定
grep -o '知识树 v1\.[0-9]' a.html | sort -u

# 4) 线上 APK 版本反解
curl -sL "https://github.com/baixi6313/sxj-android-app/releases/download/v1.0/app-debug.apk" > online.apk
unzip -o -q online.apk AndroidManifest.xml -d apkx
python -c "import re;print(sorted(set(re.findall(r'\d+\.\d+(?:\.\d+)?',open('apkx/AndroidManifest.xml','rb').read().decode('utf-16-le','ignore')))))"

# 5) APK 内嵌知识树版本
unzip -o -q online.apk "assets/www/theory/knowledge_tree.html" -d apkx
grep -c '四层权力栈' apkx/assets/www/theory/knowledge_tree.html
```

---

## 九、总体评价

hygzz01 记录本的**自我记录准确度高**：W-01「已部署」、M-01「已改源码未部署」、A-01「已部署 + 内嵌树仍 v1.1」、K-01「已改源码未部署」四条状态标注，经实地核查**全部属实**，无夸大或虚报。

本次审查在此基础上补充两点记录本未覆盖的信息：

1. **M-01 存在未被记录的页面结构缺陷**（hero 区块与首个统计项被横幅删除脚本误伤），需在小程序发布前修复；
2. **A-01 的发版 tag 语义错位**（1.0.1 发布在 v1.0 之下），当前可用但不利于版本追溯。

*—— hygzz02（Auditor），2026-08-01*
