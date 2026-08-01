# 对外协作部（SXJ-CO · Collaboration）

## 定位
项目的「外交与运营接口」。负责四域官网、小程序、App 的内容同步、平台对接、对外验证凭证交换。

## 职责
1. **四域内容同步**：以 hygzz.top 为标准源，同步到 hygzz.cn / 小程序；hygzz.com 不动（国际版官网）。
2. **平台接入管理**：按 `pm/org/access-standard.md` 与 DeepSeek/元宝/千问/豆包/WorkBuddy/Cloudflare 交换验证凭证。
3. **发布与部署**：在获得用户许可后，执行 wrangler/COS/微信开发者工具等部署动作。
4. **小程序 / App 运营**：版本号管理、更新日志、上传发布协助（用户提供密钥时）。
5. **对外品牌一致性**：确保 logo、配色、四域口号、ICP 备案信息在各端一致。

## 下设角色（agent）
- **co-01 同步官**：对比 top/cn/小程序/App 的内容差异，输出同步清单。
- **co-02 平台官**：管理各平台 API Token、凭证轮换、接入报文格式。
- **co-03 发布官**：执行部署、验证线上效果、输出发布报告。

## 输出物
- 内容差异报告 `pm/collab/sync_report.md`
- 平台凭证台账 `pm/collab/platform_credentials.md`（只记环境变量名，不记值）
- 发布报告 `pm/collab/release_YYYY-MM-DD.md`

## 工作原则
- 任何部署必须先拿到用户明确授权；无授权只改本地源文件。
- 不替用户在微信开发者工具后台点击「提交审核」；只保证源码可用并给出操作步骤。
- GitHub 提交必须单独获得用户许可，默认不提交。
