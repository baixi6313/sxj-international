# 发布检查清单（RELEASE CHECKLIST · GOV-2）

> 每次发布/部署前逐项打勾。任一项不过，阻断发布。可由 `pm/tools/preflight.py` 串联自动化。
> 来源：hygzz03 优化方案 GOV-2。本轮 9 个已暴露问题中，至少 7 个可被本清单在发布前拦截。

## 发布前必查（9 项）
- [ ] 1. **结构完整性**：WXML/HTML 标签配平（`<view` 开闭相等；`<div` 开闭相等）。脚本写盘前应有不变量护栏。
- [ ] 2. **版本一致性**：`verify_versions.py`（或人工比对）确认 App / 小程序 / 网站 / 知识树 版本号与 `VERSIONS.json` 单一真相源一致。
- [ ] 3. **密钥安全**：暂存区无 `ghp_` / `github_pat_` / `cfat_` / `AKID` / `TENCENT_SECRET` 命中（用 `secret_scan.py` 闸门）。
- [ ] 4. **BETA 清洁度**：HTML + JSON + MD 全类型扫描 `BETA / 测试版 / beta-banner` 0 命中（不只扫 HTML）。
- [ ] 5. **部署生效**：三站 curl 命中预期版本串（hygzz.top 验证**必须带 .html** 后缀）。
- [ ] 6. **缓存刷新**：hygzz.com（GitHub Pages 套 Cloudflare 代理）已 `purge_cache`，否则线上仍旧版。
- [ ] 7. **产物校验**：APK 反解 `versionName` 正确、内嵌知识树版本正确（解包 `assets/www/theory/knowledge_tree.html` 查标记）。
- [ ] 8. **版本化归档**：Release tag 与 `versionName` 一致（v1.0.1 应有独立 `v1.0.1` Release，禁止覆盖式 `--clobber` 到旧 tag）。
- [ ] 9. **git 归档**：改动已分批提交，提交信息语义清晰（禁用 `git add -A` 一把梭）。

## 已知坑（发布前必读）
- Cloudflare Pages 部署须 `--branch main`，否则只上 preview 分支、生产域名仍旧版。
- Wrangler 经 bash 调 `.bin/wrangler`（shell 包装），勿用 `node.exe` 直接调。
- 横幅删除脚本正则须用"深度计数"而非贪婪 `{1,6}`，且写盘前校验配平。
- COS 站（hygzz.top）直出 `.html`，非 clean URL；GitHub/CFF 站用 clean URL。
- 密钥一律走环境变量（GH_PAT / TENCENT_SECRET_ID / TENCENT_SECRET_KEY / CF_API_TOKEN），不落盘、不入库。
