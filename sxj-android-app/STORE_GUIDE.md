# 事现鉴 App · 商店上架指南（华为应用市场 / 应用宝）

本目录是一个**可直接上架的真实安卓原生工程**（包名 `cn.hygzz.sxj`，应用名「事现鉴」）。

- 当前版本：**v1.1.0**
- v1.1.0 视觉：恢复旧版「事现鉴 · SXJ」红圈 logo；首屏采用「世界地图 + 左顶点光锥 + ρ 热力点」；底部 4 Tab（共济值 / 贡献值 / 摆事现 / 包裹）。
- 功能：光锥坐标事现记录、本地 SHA-256 哈希指纹、验证流（支持/质疑）、人类裁定、自包含 HTML 证书导出。
- 技术：Kotlin Android 原生壳 + 本地 WebView 渲染 UI（可上架；如需完全原生 UI，可二期用 Jetpack Compose 重写）。

> 沙箱环境无 Java/Android SDK，无法在此直接编译 APK。请用下方「路径 A（推荐，自动出包）」或「路径 B（Android Studio）」获取安装包。

---

## 一、获取可安装的 APK（二选一）

### 路径 A：GitHub Actions 自动构建（推荐，无需本地装环境）
1. 在 GitHub 新建一个仓库（如 `sxj-android-app`）。
2. 把本目录全部文件推送到该仓库（需要你提供一个有 `repo` 权限的 GitHub Personal Access Token；当前仓库的 PAT 已失效，需你重新生成）。
3. 进入仓库 **Actions → Build Android APK → Run workflow**。
4. 构建完成后，在 **Artifacts** 里下载 `sxj-app-debug.apk`，即可安装到手机测试。

### 路径 B：Android Studio 本地构建
1. 安装 [Android Studio](https://developer.android.com/studio)（含 SDK）。
2. Open → 选择本目录 `sxj-android-app`。
3. 等待 Gradle 同步完成。
4. 菜单 **Build → Build Bundle(s) / APK(s) → Build APK(s)**。
5. 产物在 `app/build/outputs/apk/debug/app-debug.apk`。

---

## 二、正式发布签名（上架商店必须）

商店要求**签名后的发布版**（建议 AAB 或签名 APK）。

### 1) 生成签名密钥（一次）
```bash
keytool -genkeypair -v -keystore sxj-release.keystore -alias sxj \
  -keyalg RSA -keysize 2048 -validity 10000
```
请妥善保存 `sxj-release.keystore` 与密码（丢失无法更新应用）。

### 2) 在 `app/build.gradle` 的 `android { }` 内加入（勿提交密钥明文，用环境变量）：
```gradle
signingConfigs {
    release {
        storeFile file(System.getenv("KEYSTORE_PATH") ?: "sxj-release.keystore")
        storePassword System.getenv("KEYSTORE_PWD")
        keyAlias System.getenv("KEY_ALIAS") ?: "sxj"
        keyPassword System.getenv("KEY_PWD")
    }
}
buildTypes {
    release {
        signingConfig signingConfigs.release
        minifyEnabled false
    }
}
```
并在 GitHub 仓库 **Settings → Secrets** 配置 `KEYSTORE_PATH/KEYSTORE_PWD/KEY_ALIAS/KEY_PWD`（或本地构建时 export 这些变量）。

### 3) 产出发布包
- 本地：`gradlew assembleRelease`（或 `bundleRelease` 出 AAB）。
- CI：可把上面的 build.yml 的 `arguments` 改为 `assembleRelease` 并加签名 secret 步骤。

---

## 三、华为应用市场（华为应用市场 / AppGallery）提交

1. 注册 **[华为开发者联盟](https://developer.huawei.com/consumer/cn/)** 帐号（实名认证，个人/企业均可）。
2. 控制台 → 应用服务 → 我的应用 → 创建应用，填：
   - 应用名称：**事现鉴**
   - 包名：`cn.hygzz.sxj`
   - 分类：工具 / 教育（或「图书与参考」）
   - 一句话简介：共创论公共事实验证工具
3. 上传 **签名 APK 或 AAB**。
4. 上传：**应用图标**（已生成于 `app/src/main/res/mipmap-*`）、**至少 3-5 张截图**（手机端首页/事件簿/详情）、**应用介绍**（见第四节文案）。
5. 填写 **隐私政策网址**（见第五节，可托管在 `https://hygzz.cn/privacy`）。
6. 提交审核。华为审核通常 1–3 个工作日。

> 注：华为新机推 HarmonyOS，但 Android APK 仍可在华为设备运行并上架 AppGallery。如需原生鸿蒙版，需另用 ArkUI 重写（后续可排期）。

---

## 四、应用宝（腾讯 MyApp）提交

1. 注册 **[腾讯开放平台 / 应用宝](https://open.qq.com/)** 开发者帐号（实名认证）。
2. 管理中心 → 创建应用，填名称/包名/分类（同上）。
3. 上传 **签名 APK**（应用宝目前主要收 APK）。
4. 上传图标、截图、简介（同第三节）。
5. 填写隐私政策网址。
6. 提交审核（通常 1–3 个工作日）。

---

## 五、隐私政策（模板，可托管到 hygzz.cn/privacy.html）

> **事现鉴隐私政策（摘要）**
> 1. 本应用为离线工具，所有「事现」记录仅保存在本机（SharedPreferences / 本地存储），**不上传任何服务器**。
> 2. 本应用不收集姓名、手机号、位置等个人信息；仅声明 INTERNET 权限以兼容后续联网验证，当前版本不发起任何网络请求。
> 3. 用户可随时在「我的 → 清空我的新增」删除本地记录。
> 4. 应用内容为共创论框架推演与公开事现记录，已为正式发布版。
> 5. 联系：见官网 hygzz.cn。

---

## 六、商店文案（可直接复制）

**中文简介**
事现鉴是共创论（Co-creation Theory）的公共事实验证工具。它以「共济值 / 贡献值 / 负贡献」三值体系，记录并交叉验证公共事实现场，辅以 SHA-256 哈希指纹保证记录不可篡改。内置共创论总论、白皮书、概念树、知识树等理论内容，以及已记录的真实与推演事现案例。当前为正式版 v1.0.1，离线可用。

**English**
Shixianjian (SXJ) is a public-fact verification tool based on Co-creation Theory. It records and cross-verifies public facts using a three-value system (Co-survival / Contribution / Negative Contribution), with SHA-256 fingerprints for tamper-evidence. Includes the theory of co-creation, whitepaper, concept/knowledge trees, and recorded cases. Stable release, works offline.

---

## 七、当前能力边界（如实告知）
- 已是**真实可安装安卓 App**，非 PWA、非空壳。
- 事现记录目前为**单机演示**：新增/查看/哈希链可用；多人验证团共识需接入云端（参考小程序 sxj-mini 的云开发）后启用。
- 联网验证、跨设备同步为后续版本迭代项。
