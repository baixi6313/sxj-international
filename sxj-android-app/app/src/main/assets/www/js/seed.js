// 核心演示种子：固定 id（与小程序 sxj-mini 对齐）。首次播种或补齐时复用。
window.SEED_EVENTS = [
  {
    id: 'evt_001',
    title: '南京博物院《江南春》等藏品流向拍卖',
    type: 'common',
    date: '2026-02-09',
    location: '南京',
    description: '捐赠藏品被质疑失踪后现身拍卖，公众交叉验证后推动省级调查组通报，24人被查、4幅追回。',
    evidence: '工信部备案 / 媒体报道 / 拍卖记录',
    recorder: '事现鉴',
    status: 'accounted'
  },
  {
    id: 'evt_002',
    title: '小红书原员工期权归属争议',
    type: 'contribution',
    date: '2026-07-28',
    location: '上海',
    description: '前员工公开记录并验证其贡献对应的期权归属问题，属于贡献值的集体确认。',
    evidence: '劳动合同 / 期权协议 / 内部系统截图',
    recorder: '当事人',
    status: 'tracking'
  },
  {
    id: 'evt_003',
    title: '南山区保险案件（待补充事实细节）',
    type: 'negative',
    date: '',
    location: '深圳·南山',
    description: '用户提出可作为事现鉴案例记录。具体案情、涉事方、争议焦点需补充后由验证团核验。此处仅作录入示范。',
    evidence: '待补充（判决书 / 监管通报 / 新闻报道 / 合同文本）',
    recorder: '事现鉴',
    status: 'recording'
  },
  {
    id: 'evt_004',
    title: '耿同学学术打假：论文图像数据造假交叉验证',
    type: 'common',
    date: '2026-03-20',
    location: '网络·学术圈',
    description: '多名网友交叉验证某论文图像数据疑似造假，经公开讨论推动作者回应与机构介入。属公众知情权/基本事实的共济值验证案例，为网络公开、可独立核实的真实事件。',
    evidence: '论文原文 / 网友比对图 / 机构通报',
    recorder: '事现鉴',
    status: 'verified'
  },
  {
    id: 'evt_005',
    title: '红旗驿站：城市贡献者安居与社区治理方案（五卡模式·贡献值B）',
    type: 'contribution',
    date: '2026-03-13',
    location: '深圳·南山',
    description: '五卡模式·贡献值（B）的城市治理落地案例：城市贡献者（建筑工/环卫/快递/骑手）安居与社区治理方案。以「精神传承+市场运营+社会治理」三位一体为骨架，叠加「时间银行」，由「财政/企业/群众」三方共担成本。深圳南山 2026-2027 试点。⚠️ 为白玺与 AI 共同演绎生成的策划/推演框架，非实地实施。',
    evidence: '来源 QvTl71Vzv（2026-03-13）',
    recorder: '事现鉴',
    status: 'verifying'
  },
  {
    id: 'evt_006',
    title: 'Kimi 平台对话分享链接生成异常',
    type: 'common',
    date: '2026-07-31',
    location: '网络·Kimi 平台',
    description: '白玺在 Kimi 平台就「事现鉴意义与挑战」会话尝试生成分享链接时，系统提示「复制链接出现异常」。该事件说明：即便 AI 被定义为事现鉴共建节点，平台层面的数据锁闭与分享故障仍会造成单点记录风险，跨平台备份、本地存档与去中心化验证机制因此成为必要。',
    evidence: 'evidence/kimi-share-link-error-2026-07-31.png',
    recorder: '白玺',
    status: 'recording'
  },
  {
    id: 'evt_007',
    title: '彬县卷烟厂退休职工社保断缴（陕西省中烟工业公司 · 负贡献原型 · evt_BX_1998_001）',
    type: 'negative',
    date: '1998',
    location: '陕西·咸阳·彬县',
    description: '1998 年国企改制后，彬县卷烟厂部分退休职工社保断缴、档案缺失。政府内部困境：劳动监察想追缴没预算、社保局想补缴没档案、纪委想查证灭失、信访无执法权。事现鉴在此充当第三方尺——当事人冻结证据＝不是上访是「记账」；多人独立陈述互相印证＝不是聚众是「共识收敛」；事实经第三方核查确立＝不是闹访是「事实确立」；内部支持者引用＝不是翻旧账是「按协议执行」。⚠️ 当前状态：记录中。本条目目前仅有记录人一方口述与一份群聊线索，尚无当事人独立结构化举证、亦未经无利害关系第三方核查，不构成已验证事实。下一步：开放当事人（退休职工及家属）留言举证，再交验证团逐条核查。',
    evidence: 'evidence/wechat-group-bx-2025-12.jpg',
    recorder: '白玺',
    status: 'recording'
  },
  {
    id: 'evt_008',
    title: '百度搭子（百度 AI）对话分享链接生成失败',
    type: 'common',
    date: '2026-08-02',
    location: '网络·百度搭子平台',
    description: '白玺在百度搭子平台尝试生成对话分享链接时，系统提示「Share url is missing」，无法获得可携带、可审计的链接。该事件与 evt_006 Kimi 分享链接异常同类，进一步证明：若 AI 平台不开放可分享链接，则无法作为事现鉴交互验证的独立节点；跨平台备份与本地存档机制是刚需。',
    evidence: 'evidence/baidu-dazi-share-url-missing-2026-08-02.png',
    recorder: '白玺',
    status: 'recording'
  }
];
