# 云开发数据库初始化说明

## 三层数据模型（核心设计）

| 层级 | 集合 | 写入方 | 能否修改 | 读权限 |
|------|------|--------|----------|--------|
| **第一层 原始记录** | `events` | 记录人一次性写入 | **任何人不可改不可删** | 所有人可读 |
| **第二层 验证层** | `evidences` / `verifications` / `verifiers` | 用户追加、验证人登记 | 仅自己可改/删（原始记录不可动） | 所有人可读 |
| **第三层 公共层（自动写入）** | `consensus`（新建，由云函数维护） | **系统自动计算** | **任何用户不可写** | 所有人可读 |

设计要点：
- 第一层冻结：原始事现一旦记录就不能被任何人修改或删除，保证「原始事实」公信力。
- 第二层开放：任何人可追加证据/线索/进展、给出验证意见（支持/反对/存疑），验证团成员可登记/改/退自己的资料。每一层的追加记录本身也不可篡改（靠代码层只走 `add`）。
- 第三层自动：由云函数根据第一、二层实时计算共识状态（票数、SHA-256 哈希链、公信力分），普通用户无法直接写入，避免人为篡改汇总结果。

## 集合清单
在微信开发者工具 → 云开发 → 数据库中创建：
- `events`        事现原始记录（第一层，冻结）
- `evidences`     证据 / 线索 / 进展（第二层，可追加）
- `verifications` 验证意见（第二层，可追加）
- `verifiers`     验证团成员（第二层，可登记自己）
- `consensus`     共识汇总（第三层，云函数自动写入，用户不可写）

## 导入种子数据（JSON Lines 格式）
在云开发控制台 → 数据库 → 集合管理 → 选中集合 → 导入 → 选对应文件：
- `events.json`        → `events`
- `verifiers.json`     → `verifiers`
- `evidences.json`     → `evidences`
- `verifications.json` → `verifications`
- `consensus.json`     → `consensus`（可选，云函数会自动生成）

> 导入若报错「格式不正确」，确认选的是 JSON Lines（每行一条），不是 JSON 数组。

## 关键：设置自定义安全规则（防篡改核心）
下拉菜单里没有「只能新建不可改」选项，必须用「自定义安全规则」。
每个集合点「数据权限」→「自定义安全规则」，粘贴对应 JSON：

**第一层 events（所有人可读、仅可新建、不可改删）：**
```json
{
  "read": true,
  "create": true,
  "update": false,
  "delete": false
}
```

**第二层 evidences / verifications（所有人可读、可新建、仅能改/删自己）：**
```json
{
  "read": true,
  "create": true,
  "update": "doc._openid == auth.openid",
  "delete": "doc._openid == auth.openid"
}
```

**第二层 verifiers（所有人可读、可新建、仅能改/删自己）：**
```json
{
  "read": true,
  "create": true,
  "update": "doc._openid == auth.openid",
  "delete": "doc._openid == auth.openid"
}
```

**第三层 consensus（所有人可读、任何用户不可写，仅云函数 admin 可写）：**
```json
{
  "read": true,
  "create": false,
  "update": false,
  "delete": false
}
```

> 注意：`false` / `true` 是布尔值，**不要加引号**（不要写成 `"false"`）。

## 第三层为什么必须靠云函数
普通用户权限设为 `create:false / update:false / delete:false` 后，小程序前端无法直接写 `consensus`。
云函数运行在管理端，拥有 admin 权限，不受集合安全规则限制，因此由云函数读取 events+evidences+verifications，
实时算出每个事件的共识状态并写入 `consensus`，用户只能读不能改。

## 部署 consensus 云函数（第三层·自动写入）
目录：`cloudfunctions/consensus/`（含 index.js / package.json / config.json）
1. 微信开发者工具 → 左侧「云开发」→「云函数」→ 右键 `cloudfunctions/consensus` → **上传并部署（云端安装依赖）**
2. 部署成功后，在云函数列表点 `consensus` → 「测试」→ 参数填 `{"eventId":"evt_001"}` 可手动触发一次重算
3. 全量重算：测试参数留空 `{}`，会遍历所有事件写入 consensus（也由 config.json 的定时触发器每 5 分钟自动执行）
4. 前端已在「追加证据」「我来验证」提交成功后自动调用此云函数，无需手动触发

> 云函数计算逻辑：验证票数统计(support/oppose/doubt)、证据数、共识状态(pending/reached/disputed/contested)、
> 公信力分(支持占比+证据加权，封顶100)、SHA-256 哈希链(事件+全部证据+全部验证稳定排序后串联)。

## 验证是否成功
1. 预览 / 真机打开某条事件详情，应看到：原始记录 + 验证意见统计 + 证据链 + **公共共识卡片**（公信力分/共识状态/SHA-256）
2. 点「追加证据 / 线索」「我来验证」能提交，提交后共识卡片分数/状态应随之刷新
3. 用另一个微信号打开，能看到别人追加的内容（依赖上面权限设为可读）
4. 去云控制台 `consensus` 集合，能看到每个事件一条汇总记录，且用户无写入入口
