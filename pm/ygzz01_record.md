# hygzz01 修改记录本（Recorder Log）

> 由 PM 在用户每次提出修改时追加。状态：待实施 / 已改源码 / 已部署 / 未部署 / 阻塞。

## 2026-08-01（初始化基线 · 来自当日会话）

### [W-01] 网站六端点清除 BETA 横幅
- 平台：web（hygzz.cn / www.hygzz.cn / hygzz.com / www.hygzz.com / hygzz.top / www.hygzz.top）
- 内容：移除全部 6 个端点的 BETA 测试版横幅，保留「非实地实施」诚实声明。
- 提出人：用户
- 状态：✅ 已部署（CF Pages 重部署 + GitHub Pages + 腾讯云 COS；verify_all.py 全站扫描 banner_hits={} 通过）

### [M-01] 微信小程序标注版本 1.0.1 + 去 BETA
- 平台：小程序（sxj-mini/weapp-client）
- 内容：project.miniapp.json version 0.0.1→1.0.1、versionCode 100→101；profile.wxml「关于」区块加「小程序版本 1.0.1 · 正式版」；源码无 BETA 残留。
- 提出人：用户
- 状态：✅ 已改源码，⚠️ 未部署（需在微信开发者工具手动上传发布，沙箱无微信密钥、非 git 仓库）

### [A-01] 安卓 App 升 1.0.1 + 去 BETA + 自动发版 → **已迭代至 1.0.2**
- 平台：App（sxj-android-app）
- 内容：删 (BETA)；build.gradle versionName 1.0.1、versionCode 3；build.yml 改为「按 versionName 动态建 Release tag」（根治覆盖式发版）；内嵌知识树升 v1.2；云端重建 success，APK 已发 **Release v1.0.2**（含四层权力栈图，反解 versionName=1.0.2、内嵌树命中 3）。
- 提出人：用户
- 状态：✅ 已部署（APK 下载：https://github.com/baixi6313/sxj-android-app/releases/download/v1.0.2/app-debug.apk）

### [K-01] 知识树升级 v1.2（含层级图 + 新知识）
- 平台：web 源文件（knowledge_tree.html 及 3 处镜像）
- 内容：嵌入四层权力栈图（base64 内联）；新增 Cloudflare Token 三层界面 / Wrangler 部署陷阱 / 全平台去 BETA 实践节点；落地层更新为「官网双域 + 小程序 + App（v1.0.2）」；页脚记 v1.2。
- 提出人：用户
- 状态：
  - ✅ hygzz.cn（Cloudflare Pages）已部署 v1.2（149KB，权力栈命中 3）
  - ✅ hygzz.com（GitHub Pages）已部署 v1.2（148KB，权力栈命中 3）
  - ⛔ hygzz.top（腾讯云 COS）**未部署**：本会话无 TENCENT_SECRET_ID/KEY，需用户供密钥或运行 `tcb_upload.py upload`
  - ✅ 安卓 1.0.2 内嵌知识树已含 v1.2（见 A-01）

### [M-01 补充] 小程序 profile.wxml 结构缺陷已修复
- 早前 `remove_banner.py` 贪婪正则误删 hero 区块与「已记录」统计项，已恢复；`<view>` 配平 28/28；版本标注 1.0.1 保留。
- 状态：✅ 源码修复完成，⚠️ 仍待用户在微信开发者工具手动上传发布（沙箱无微信密钥）。
