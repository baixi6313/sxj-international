# SXJ 网站部署到 GitHub Pages 完整指南

## 为什么选择 GitHub Pages？

| 对比项 | GitHub Pages | Cloudflare Pages | WorkBuddy |
|--------|-------------|-----------------|-----------|
| 费用 | 永久免费 | 永久免费 | 消耗积分 |
| 自动部署 | push即更新 | push即更新 | 需手动操作 |
| 自定义域名 | 支持 | 支持 | 不支持 |
| 版本控制 | 内置git历史 | 连接git仓库 | 无 |
| 流量限制 | 100GB/月 | 无限 | - |
| 存储限制 | 1GB | 500MB | - |
| 适合场景 | **长期托管** | **CDN加速** | **开发编辑** |

**推荐方案：GitHub 仓库 → 同时触发 GitHub Pages + Cloudflare Pages 部署**

---

## 第一步：注册 GitHub 账号（5分钟）

1. 打开 https://github.com/signup
2. 填写用户名、邮箱、密码
3. 验证邮箱
4. 选择 Free 免费计划

> 如果已有账号，跳过此步

---

## 第二步：在 GitHub 上创建仓库（2分钟）

1. 登录 GitHub，点击右上角 **+** → **New repository**
2. 填写信息：
   - Repository name: `sxj-international`
   - Description: `SXJ 事现鉴国际版 - 基于UDHR第二十二条的可验证公共事实协议`
   - 选择 **Public**（免费版必须公开）
   - **不要**勾选 "Add a README file"（已有本地README）
   - **不要**勾选 ".gitignore"（已有本地.gitignore）
3. 点击 **Create repository**

创建后，GitHub 会显示仓库地址，类似：
```
https://github.com/你的用户名/sxj-international.git
```

**记下这个地址！**

---

## 第三步：创建个人访问令牌（PAT）（3分钟）

GitHub 已不支持密码推送，需要创建令牌：

1. 点击右上角头像 → **Settings**
2. 左侧菜单最底部 → **Developer settings**
3. → **Personal access tokens** → **Tokens (classic)**
4. 点击 **Generate new token** → **Generate new token (classic)**
5. 填写：
   - Note: `SXJ部署`
   - Expiration: 选 `90 days` 或 `No expiration`
   - 勾选 `repo` （全部repo权限）
6. 点击 **Generate token**
7. **立即复制令牌**（页面关闭后无法再看到！）

---

## 第四步：关联远程仓库并推送（2分钟）

打开命令行（CMD或PowerShell），进入项目目录：

```cmd
cd C:\Users\Administrator\WorkBuddy\2026-07-22-08-14-20\hygzz_cn
```

关联远程仓库（把"你的用户名"替换成实际用户名）：
```cmd
git remote add origin https://github.com/你的用户名/sxj-international.git
```

首次推送：
```cmd
git push -u origin main
```

系统会弹出认证窗口：
- Username: 输入你的 GitHub 用户名
- Password: **粘贴刚才的令牌**（不是GitHub密码！）

推送成功后你会看到类似输出：
```
Enumerating objects: 15, done.
...
To https://github.com/你的用户名/sxj-international.git
 * [new branch]      main -> main
```

---

## 第五步：开启 GitHub Pages（1分钟）

1. 打开仓库页面 → **Settings** 标签
2. 左侧菜单 → **Pages**
3. Source 选择 **GitHub Actions**
4. 完成！仓库里的 `.github/workflows/deploy.yml` 会自动处理部署

约 1-2 分钟后，网站就会上线：
- 默认地址：`https://你的用户名.github.io/sxj-international/`
- 查看部署状态：仓库 → **Actions** 标签

---

## 第六步：绑定自定义域名（可选，3分钟）

### 方式A：用 GitHub Pages（推荐长期方案）

1. 仓库 → **Settings** → **Pages**
2. Custom domain 输入：`hygzz.com`
3. 勾选 **Enforce HTTPS**
4. 到 Cloudflare DNS 面板添加记录：

| 类型 | 名称 | 内容 | 代理状态 |
|------|------|------|---------|
| CNAME | @ | 你的用户名.github.io | 仅DNS(灰云) |
| CNAME | www | 你的用户名.github.io | 仅DNS(灰云) |

> 注意：如果之前有A记录指向Cloudflare Pages，需要删除或修改

### 方式B：继续用 Cloudflare Pages（保留CDN加速）

1. Cloudflare Pages → 连接你的 GitHub 仓库
2. 每次push到main分支，GitHub Pages 和 Cloudflare Pages **同时自动部署**
3. 域名指向Cloudflare Pages（橙云代理，有CDN加速）

**推荐同时使用A+B**：GitHub Pages作为永久备份，Cloudflare Pages作为CDN加速主站。

---

## 以后如何更新网站？

### 方法一：双击 push.bat（最简单）

1. 用任何编辑器（记事本、VS Code等）修改 `index.html`
2. 双击项目目录下的 `push.bat`
3. 输入说明，回车
4. 1-2分钟后网站自动更新

### 方法二：命令行

```cmd
cd C:\Users\Administrator\WorkBuddy\2026-07-22-08-14-20\hygzz_cn
git add -A
git commit -m "更新说明"
git push
```

### 方法三：直接在 GitHub 网页编辑

1. 打开仓库 → 点击 `index.html`
2. 点铅笔图标编辑
3. Commit changes
4. 自动部署

---

## 多域名部署方案

| 域名 | 部署平台 | 说明 |
|------|---------|------|
| hygzz.com | GitHub Pages + Cloudflare | 国际验算尺（主站） |
| hygzz.cn | Cloudflare Pages | 国内金融财政验证 |
| hygzz.top | GitHub Pages | CV验证平台 |
| hygzz.中国 | GitHub Pages | 中文案例库 |

每个域名可以创建独立的 GitHub 仓库，或用同一个仓库的不同分支。

---

## 常见问题

### Q: push时提示认证失败？
A: 令牌过期了，回到第三步重新生成。或者运行：
```cmd
git credential reject https://github.com
```
然后重新push时会提示输入新令牌。

### Q: GitHub Pages部署失败？
A: 检查 Actions 标签的报错信息。常见原因：
- workflow文件格式错误（检查缩进用空格不是tab）
- 仓库Settings → Pages → Source没有选"GitHub Actions"

### Q: 自定义域名不生效？
A: DNS传播需要时间（最长48小时，通常几分钟）。检查：
```cmd
nslookup hygzz.com
```
确认指向 `你的用户名.github.io`

### Q: 网站打开是404？
A: 等待 Actions 完成部署（绿色勾✓）。如果CNAME文件内容和Pages设置不一致也会404。

### Q: 想让别人帮忙维护怎么办？
A: GitHub仓库 → Settings → Collaborators → 添加协作者。对方也能push更新。

---

## 紧急回滚

如果更新后网站出问题：

```cmd
# 查看历史版本
git log --oneline

# 回退到上一个版本
git revert HEAD
git push

# 或者回退到指定版本（把abc1234换成commit哈希）
git reset --hard abc1234
git push -f
```

GitHub 网页也能操作：仓库 → Settings → 不支持直接回滚，但可以找到历史commit → Browse files → Restore。

---

## 总结

部署到 GitHub Pages 后：
- 网站永久免费运行，不消耗任何积分
- 修改网站只需修改文件 + push，1-2分钟自动上线
- 完整版本历史，随时回滚
- 任何人都能通过GitHub协作
- 同时保留Cloudflare Pages的CDN加速

**你只需要做一次第四步的推送，之后所有更新都自动完成。**
