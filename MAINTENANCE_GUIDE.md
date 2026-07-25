# SXJ 网站维护手册

> 本手册让你在没有 AI 积分的情况下也能独立维护和更新网站。
> 最后更新：2026-07-25

## 一、文件位置

- 国际版：`C:\Users\Administrator\WorkBuddy\2026-07-22-08-14-20\hygzz_cn\index.html`
- 线上地址：https://hygzz.com（国际版）、https://hygzz.cn（暂同国际版）
- 部署方式：Cloudflare Pages（手动上传 index.html）

## 二、部署流程（改完代码后怎么上线）

1. 修改本地 `index.html`
2. 登录 Cloudflare Dashboard → Pages → 找到 hygzz 项目
3. 上传新的 index.html（或通过 git push 触发自动部署）
4. 几秒后线上生效

## 三、常见修改操作（不需要 AI）

### 3.1 修改 Hero 标题文字
搜索 `class="hero"` 找到 Hero 区域，直接改 `<h1>` 和 `<h2>` 里的文字。

### 3.2 修改/添加导航栏板块
搜索 `class="section-nav"` 找到导航栏。
- 添加板块：在 nav 里加 `<a href="#新id">New Section</a>`
- 在页面里加 `<section class="content-section" id="新id">...</section>`

### 3.3 修改 CV 排行榜数据
搜索 `var leaderboard` 找到数据数组。
每条格式：
```javascript
{name:'名字', role:'角色', cv:数值, bar:百分比,
 bd:[{l:'项目名',v:数值}, ...]}
```
直接改数值即可，页面会自动验证求和是否等于 cv。

### 3.4 修改默认记录数据
搜索 `var defaultRecords` 找到默认记录数组。
每条格式：
```javascript
{hash:'...', time:'时间', text:'内容', type:'类型', verified:true/false}
```

### 3.5 修改 AI 聊天回复
搜索 `var faq` 找到 FAQ 数据。
每条格式：
```javascript
'关键词': {text:'回复内容', link:'链接或null'}
```

### 3.6 修改颜色主题
搜索 `:root{` 找到 CSS 变量。
```css
--accent:#0066ff;  /* 主色调，改这个就全局变色 */
--bg:#ffffff;       /* 背景色 */
--text:#1a1a2e;     /* 文字色 */
```

### 3.7 修改理论板块内容
搜索 `id="theory"` 找到共创论理论板块。
- 三值体系卡片：搜索 `value-card`
- 分形评估：搜索 `fractal-section`
- 理论演进时间线：搜索 `evolution-tl`

### 3.8 修改跨国社保计算器
搜索 `function calcSecurity` 找到计算逻辑。
- 修改国家列表：搜索 `country-sel` 的 `<option>` 标签
- 修改计算公式：在 calcSecurity 函数内修改

### 3.9 修改 CV 计算器
搜索 `function calcCV` 找到计算逻辑。
- 修改权重系数：直接改函数内的数字
- 修改贡献类型：搜索 `contrib-type` 的 `<option>` 标签

### 3.10 修改对联内容
搜索 `topbar-couplet` 找到对联区域。
- 上联在第一个 `couplet-row`
- 下联在第二个 `couplet-row`

## 四、免费替代工具（不消耗 WorkBuddy 积分）

### 4.1 日常修改 — 免费AI工具
- **DeepSeek 网页版**（chat.deepseek.com）— 免费，把代码贴进去让它帮你改
- **通义千问**（tongyi.aliyun.com）— 免费，支持长文本
- **豆包**（doubao.com）— 免费，响应快
- **Kimi**（kimi.moonshot.cn）— 免费，支持超长上下文

用法：把 index.html 相关部分贴给这些 AI，描述你要改什么，它会给你修改后的代码。

### 4.2 代码编辑器
- **VS Code**（免费）— 直接编辑 index.html
- 安装插件：Live Server（本地预览）、HTML CSS Support（代码提示）

### 4.3 部署托管
- **Cloudflare Pages**（免费）— 当前已在使用
- **GitHub Pages**（免费）— 备选方案
- **Vercel**（免费）— 备选方案

### 4.4 域名续费
- hygzz.com / hygzz.cn / hygzz.top — 每年约 ¥50-80/个
- hygzz.中国 — 每年约 ¥200-300

## 五、网站架构概览（方便定位）

```
index.html 结构：
├── <head> (1-627行)
│   ├── SEO meta 标签
│   ├── Favicon (内联SVG)
│   └── <style> 全部CSS (7-627行)
│       ├── CSS变量 :root
│       ├── 布局 .main-wrap .left-col .right-col
│       ├── 组件 .card .sidebar-card .lb-item
│       ├── 理论板块 .value-card .fractal-section
│       ├── 计算器 .calc-box .calc-result
│       ├── 动画 @keyframes .reveal
│       └── 响应式 @media
│
├── <body> (628-2868行)
│   ├── Topbar (对联+语言切换+地区切换)
│   ├── Hero (Canvas动画+标题+输入框+统计)
│   ├── Section Nav (导航栏)
│   ├── Main Content
│   │   ├── Left Column (记录卡片网格)
│   │   │   ├── Records 区域
│   │   │   └── 10个内容板块
│   │   │       1. Manifesto
│   │   │       2. How It Works
│   │   │       3. Verified Cases
│   │   │       4. Submit/Verify (含计算器)
│   │   │       5. Contributors & Governance
│   │   │       6. Co-Creation Theory (完整理论)
│   │   │       7. Blog/Updates
│   │   │       8. API/Developers
│   │   │       9. Community/Contact
│   │   │      10. Roadmap
│   │   └── Right Column (侧边栏)
│   │       ├── CV Verification & Settlement
│   │       ├── CV 计算器
│   │       └── 推广卡片
│   ├── Lightbox (图片查看)
│   ├── AI Chat (浮动聊天窗)
│   └── <script> 全部JS
│       ├── 数据：defaultRecords, leaderboard, faq
│       ├── 渲染：renderAll, renderLeaderboard
│       ├── 计算：generateRecord, calcSecurity, calcCV
│       ├── 交互：点赞/评论/转发/附件/自荐
│       ├── 动画：Canvas哈希链, IntersectionObserver
│       └── 导航：scroll-spy, smooth scroll
│
└── 总计约2869行
```

## 六、紧急情况处理

### 6.1 网站白屏
- 检查 `</style>` 标签是否存在（之前出过这个bug）
- 用浏览器F12 → Console 看报错
- 把 index.html 贴给 DeepSeek 问"哪里有语法错误"

### 6.2 Cloudflare 部署失败
- 检查 index.html 文件大小是否正常（应该约170KB）
- 在 Cloudflare Pages 查看部署日志

### 6.3 域名打不开
- 检查 Cloudflare DNS 记录是否正确
- 检查 Pages 自定义域名绑定状态

## 七、长期可持续方案

### 阶段一（现在-免费维持）
- 用免费AI工具做日常修改
- 本地 VS Code 编辑
- Cloudflare Pages 免费托管

### 阶段二（有收入后）
- WorkBuddy 积分用于复杂开发
- 日常维护用免费工具
- 考虑购买 GitHub Copilot（$10/月）做日常开发

### 阶段三（规模化）
- 建立开发者社区，吸引贡献者
- 开源到 GitHub，接受 PR
- 申请公益基金/资助
