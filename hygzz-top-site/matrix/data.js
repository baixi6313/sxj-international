/* ============================================================
 * 事现鉴 SXJ · 矩阵统一数据模型 (data.js)
 * ------------------------------------------------------------
 * 唯一数据源：坐标轴 / 维基 / 地图 / 热力密度图 四视图共用。
 *
 * 依据：
 *   SXJ-wiki-map-design.md §8「矩阵作为统一数据模型（坐标优先）」
 *   贡献值-社会资源三元-讨论稿.md §「三元 × 三档」矩阵
 *   SXJ-verification-ledger.md 第三章 事件簿（evt_001–010）
 *
 * 坐标定义：
 *   x = 三元（自然 / 人力 / 数字）
 *   y = 三档（上·系统制度级 / 中·专业组织级 / 下·个人日常级）
 *   z = 组织层级（验证元数据：谁在桌上）
 *   j = 法域（中国含港澳台 / 国外）
 *   t = 时间
 *   ρ = 可验证密度
 *
 * 坐标系优先原则：本文件只定义坐标 + 落点 + ρ，
 *   不预置任何聚合 / 计分。聚合留给查询时的投影。
 * ============================================================ */

var SXJ = (function () {
  'use strict';

  /* ---------- 0. 元信息 ---------- */
  var META = {
    protocol: 'SXJ-MAIP/1.0',
    specSource: 'SXJ-wiki-map-design.md §8（2026-08-08 增补）',
    rhoMin: 0.85,            // ρ 门槛（待校准）
    generated: '2026-08-11',
    note: '本数据为 spec 示范落点，非中央内容库。SXJ 只定义格式，不存内容。'
  };

  /* ---------- 1. 三值（配色权威定义） ---------- */
  var VALUES = {
    A: { key: 'A', name: '共济值', en: 'Commonweal', color: '#2F6FED',
         def: '按需 · 生存权 · 钱解决不了的非物公共品（真相 / 确权 / 互助 / 共识）' },
    B: { key: 'B', name: '贡献值', en: 'Contribution', color: '#D99A2B',
         def: '按劳 · 净值 = 正贡献 − 负贡献；共济值之上的兴趣驱动贡献' },
    C: { key: 'C', name: '负贡献', en: 'Negative', color: '#D85A30',
         def: '追责 · 天花板；须同时满足归责四条件（主体性 / 因果性 / 可避免性 / 修复性）' }
  };

  /* ---------- 2.5 SCA：社会确权资产（Social Confirmation Asset） ----------
   *
   * 来源：白玺 2026-08-11 深夜 AI 对话截图（DeepSeek / DuMate 跨平台验证）
   * 定位：使财政直接兑换价值发挥作用的关键机制。
   *   将一个人的全部核实贡献——从劳动产出、生态修复、社区服务和信用亮度——
   *   量化为一个单一的资产指标。当 SCA ≥ 债务时，系统自动触发补偿，
   *   而不需要资金实际流动。
   *
   * 公式：
   *   f_SCA = Σ(优点卡积分 × V) + 生态卡资产 + 信用卡亮度 × 乘数
   *
   * 三维度（权重和 = 100%）：
   *   ① 生存复原力 (35%) → 自然枝 ρ    — 碳减排/灾害应对/核安全/生态修复
   *   ② 创新贡献 (30%) → 人文枝 ρ    — 基础研究/开源项目/制度创新/专业劳动
   *   ③ 全民福利 (35%) → 共济值 A     — 社保/生存权/社区服务/互助
   *
   * 与化债引擎衔接：
   *   SCA 是「财政直销」的度量尺——按 ρ（可验证密度）而非旧财政收入注入基值。
   *   待发展城市（如彬州市）凭三元 ρ 跑通 SCA → 反证"仅限发达省市"假设。
   *   核心闭环：负贡献核算(C) ∥ 新贡献生成(B/SCA) → 置换现有债务 → 净值 N(t)
   */
  var SCA = {
    fullName: 'Social Confirmation Asset',
    cnName: '社会确权资产',
    shortName: 'SCA',
    version: '1.0',
    source: '白玺 2026-08-11 AI 跨平台对话验证（DeepSeek + DuMate 截图存证）',
    status: 'spec', /* spec = 正式规范，待实地量测校准 */

    /* 公式 */
    formula: {
      text: 'f_SCA = Σ(优点卡积分 × V) + 生态卡资产 + 信用卡亮度 × 乘数',
      vars: {
        meritPoints: { name: '优点卡积分', desc: '个人累积的优点卡积分（劳动/创新/互助行为认证）', unit: '分', type: 'number' },
        V: { name: 'V 系数', desc: '积分兑换系数（由法域/层级决定，待校准）', unit: '无量纲', type: 'float', default: 1.0 },
        ecoCard: { name: '生态卡资产', desc: '生态修复/碳汇/植树造林等存量资产折算值', unit: '元/SCA单位', type: 'number' },
        creditBrightness: { name: '信用卡亮度', desc: '信用评级/社区声誉/历史履约记录综合指数', unit: '无量纲(0-1)', type: 'float' },
        multiplier: { name: '乘数', desc: '信用亮度的放大因子（组织层级/法域调节）', unit: '无量纲', type: 'float', default: 1.0 }
      }
    },

    /* 三维度（与 SXJ 三元映射） */
    dimensions: [
      {
        key: 'resilience',
        name: '生存复原力',
        weight: 0.35,
        color: '#2d8a4e', /* 绿 = 自然枝同色 */
        icon: '🛡️',
        mapsTo: 'natural', /* → SXJ TRIAD[0] */
        scope: '系统的风险抵御能力是否加强？碳减排、灾害应对、核安全。',
        indicators: ['碳汇增量(GEP)', '灾害响应能力指数', '生态修复面积', '环境安全等级'],
        examples: ['植树造林存量折算', '垃圾分类减量记录', '社区防灾志愿时长'],
        note: '35% 权重反映：没有生存安全基础，一切贡献都是空中楼阁。'
      },
      {
        key: 'innovation',
        name: '创新贡献',
        weight: 0.30,
        color: '#A32D2D', /* 红 = 人文枝同色 */
        icon: '💡',
        mapsTo: 'human', /* → SXJ TRIAD[1] */
        scope: '是否推动了知识、技术或治理领域的前沿发展？基础研究、开源项目、制度创新。',
        indicators: ['专利/开源贡献', '基础研究参与度', '制度设计提案采纳率', '专业技能认证'],
        examples: ['医/教/研专业劳动', '开源标准制定', '专利创造', '探戈式双向验证（方法论创新）'],
        note: '30% 权重：创新是发展的引擎，但不是唯一——避免"唯创新论"挤压生存权。'
      },
      {
        key: 'welfare',
        name: '全民福利',
        weight: 0.35,
        color: '#2F6FED', /* 蓝 = 共济值A同色 */
        icon: '🤝',
        mapsTo: 'A', /* → SXJ VALUES.A */
        scope: '社会保障、生存权保障、社区互助的可及性与质量。',
        indicators: ['社保覆盖率', '社区服务参与度', '互助网络密度', '基本生活保障水平'],
        examples: ['养老护理服务', '日常互助记录', '志愿服务时长', '社保断缴补缴追踪'],
        note: '35% 权重=生存复原力同等权重：福利不是"剩余项"，而是与生存安全并列的基础维度。'
      }
    ],

    /* 触发条件 */
    trigger: {
      condition: 'SCA ≥ 债务',
      effect: '系统自动触发补偿，无需资金实际流动',
      mechanism: '正贡献价值直接抵消负贡献价值。没有空转，没有中间人。',
      debtEngineLink: '化债引擎核心闭环 §1：负贡献核算(C) ∥ 新贡献生成(B/SCA) 并行 → 置换 → 净值 N(t)'
    },

    /* 计算（示例——待接入真实数据源） */
    calculate: function(opt) {
      opt = opt || {};
      var r = (opt.resilience || 0) * this.dimensions[0].weight;
      var i = (opt.innovation || 0) * this.dimensions[1].weight;
      var w = (opt.welfare || 0) * this.dimensions[2].weight;
      var base = r + i + w;
      var bonus = (opt.creditBrightness || 0) * (opt.multiplier || 1.0);
      return {
        total: base + bonus,
        breakdown: { resilience: r, innovation: i, welfare: w, creditBonus: bonus },
        normalized: Math.min(1, base + bonus), /* 归一化到 0-1 */
        meetsDebt: (base + bonus) >= (opt.debtThreshold || 0)
      };
    },

    /* 城市级 SCA 映射（彬州/深圳模板） */
    cityTemplate: function(cityKey) {
      var templates = {
        binzhou: {
          name: '彬州市',
          dims: { resilience: 0.4, innovation: 0.2, welfare: 0.5 }, /* 待量测ρ */
          note: '待发展城市试点候选：自然(生态修复)强、人文(养老护理人力)中等、A(社保缺口→高需求)',
          evtId: 'evt_011'
        },
        shenzhen: {
          name: '深圳市',
          dims: { resilience: 0.5, innovation: 0.8, welfare: 0.3 }, /* 待量测ρ */
          note: 'AI 验证节点聚集地：数字/创新极强、但全民福利(高房价压力)偏低',
          evtId: 'evt_012'
        }
      };
      return templates[cityKey] || null;
    }
  };
  var TRIAD = [
    { key: 'natural', name: '自然 / 环境', short: '自然', icon: '🌱', color: '#2d8a4e',
      scope: '生态贡献、自然资源保育',
      anchor: '中国国家级 GEP（生态系统生产总值）+ 生态积分',
      open: true,
      openNote: '已有国家权威度量，可直接对接' },
    { key: 'human', name: '人文', short: '人文', icon: '🤝', color: '#A32D2D',
      scope: '体力劳动 + 脑力劳动、制度设计、公共知识',
      anchor: '国家级劳动统计（中等权威）',
      open: true,
      openNote: '待建本地度量模板，不急于全球统一' },
    { key: 'digital', name: '数字 / 资产', short: '数字', icon: '🔗', color: '#4a5c8a',
      scope: '资产增值、知识产权、数据资本',
      anchor: '暂无跨国共识',
      open: false,
      openNote: '最敏感，田忌赛马「下马」→ 主动挂起，不挡全局' }
  ];

  /* ---------- 3. y 轴：三档 ---------- */
  var TIER = [
    { key: 'up',  name: '上 · 系统 / 制度级', short: '上', weightNote: '影响面最广，但具体权重各法域自定' },
    { key: 'mid', name: '中 · 专业 / 组织级', short: '中', weightNote: '组织与专业层' },
    { key: 'low', name: '下 · 个人 / 日常级', short: '下', weightNote: '个人日常层' }
  ];

  /* ---------- 4. 3 × 3 矩阵格位（权威内容） ---------- */
  var CELLS = [
    { x: 'natural', y: 'up',
      title: '国家级 GEP · 跨省生态补偿 · 碳市场制度',
      examples: ['国家级 GEP 核算', '跨省生态补偿机制', '全国碳排放权交易市场'],
      verifier: '环保 / 生态主管部门 · 环保组织',
      status: 'open', statusText: '已开放验证（有国家权威度量）' },
    { x: 'natural', y: 'mid',
      title: '地方生态修复 · 企业碳中和 · 行业减污',
      examples: ['地方生态修复工程', '企业碳中和披露', '行业减污降碳'],
      verifier: '地方生态环境局 · 行业协会 · 第三方核查机构',
      status: 'open', statusText: '已开放验证' },
    { x: 'natural', y: 'low',
      title: '个人生态积分 · 垃圾分类 · 植树护水',
      examples: ['个人生态积分', '垃圾分类记录', '植树造林 / 护水志愿'],
      verifier: '社区 · 环保组织',
      status: 'open', statusText: '已开放验证' },

    { x: 'human', y: 'up',
      title: '社保 / 制度设计 · 开源标准与协议制定 · 公共知识基石',
      examples: ['社保制度设计', '开源标准 / 协议制定', '公共知识基石建设'],
      verifier: '人社部门 · 标准组织 · 学术共同体',
      status: 'open', statusText: '已开放验证' },
    { x: 'human', y: 'mid',
      title: '专业劳动（医 / 教 / 研）· 专利创造 · 组织管理',
      examples: ['医疗 / 教育 / 科研专业劳动', '专利创造', '组织管理'],
      verifier: '工会 · 行业主管 · 专业学会',
      status: 'open', statusText: '已开放验证' },
    { x: 'human', y: 'low',
      title: '日常互助 · 志愿服务 · 社区照护 · 探戈式双向验证',
      examples: ['日常互助', '志愿服务时长', '社区照护', '探戈式双向验证'],
      verifier: '社区 · 志愿组织 · 互助小组',
      status: 'open', statusText: '已开放验证' },

    { x: 'digital', y: 'up',
      title: '生产资料社会化（公有制 / 合作社规模）· 公共资源平台',
      examples: ['生产资料社会化', '合作社规模化', '公共资源平台 / 基础设施'],
      verifier: '数据信托 · 公共平台治理机构',
      status: 'hold', statusText: '挂起（无跨国共识，逐格裁定）' },
    { x: 'digital', y: 'mid',
      title: '生产性资产社会复用 · 企业数字外溢 · 开放数据',
      examples: ['生产性资产社会复用', '企业数字外溢', '开放数据'],
      verifier: '数据信托 · 开放数据联盟',
      status: 'hold', statusText: '挂起（资产增值是否计入 = 该格开不开放验证）' },
    { x: 'digital', y: 'low',
      title: '闲置资源匹配 · 技能共享 · 个人数据授权复用',
      examples: ['闲置资源匹配', '技能共享', '个人数据授权复用'],
      verifier: '数据信托 · 平台合作社',
      status: 'open', statusText: '已开放验证（个人授权层）' }
  ];

  /* ---------- 5. z 轴：组织层级（验证元数据） ---------- */
  var ORG_LEVEL = [
    { key: 'individual', name: '个人', desc: '当事人本人落点' },
    { key: 'group',      name: '群体 / 社区', desc: '同类当事人集合' },
    { key: 'org',        name: '组织 / 企业', desc: '法人主体' },
    { key: 'juris',      name: '法域 / 制度', desc: '国家或地区制度层' },
    { key: 'cross',      name: '跨法域 / 全球', desc: '跨国联动（四阶助法之「共助」）' }
  ];

  /* ---------- 6. j 轴：法域 ---------- */
  var JURIS = [
    { key: 'CN',   name: '中国（含港澳台）', color: '#A32D2D',
      note: '台湾、香港、澳门是中国的一部分' },
    { key: 'INTL', name: '国外', color: '#4a5c8a', note: '其他法域' }
  ];

  /* ---------- 7. 状态枚举 ---------- */
  var STATUS = {
    recording: { name: '记录中', color: '#8892a0' },
    verifying: { name: '验证中', color: '#C9A24B' },
    verified:  { name: '已验证', color: '#2d8a4e' },
    accounted: { name: '已归责', color: '#A32D2D' },
    tracking:  { name: '追踪中', color: '#4a5c8a' },
    placeholder: { name: '占位·非事现', color: '#b9b2a6' }
  };

  /* ============================================================
   * 8. 事现条目（维基层数据）
   *    字段严格对齐 SXJ-wiki-map-design.md §3.1：
   *    条目坐标 / 多当事人三值归因 / 验证包裹 / 来源链 / 版本史
   * ============================================================ */
  var EVENTS = [
    {
      id: 'evt_001', ledgerAlias: 'seed1',
      title: '南京博物院受赠文物流向拍卖',
      x: 'human', y: 'up', z: 'org', j: 'CN',
      t: '2026-02-09',
      geo: { lon: 118.80, lat: 32.06, place: '江苏南京', precision: 'city' },
      rho: null, rhoNote: '未按 MAIP 信封量测',
      status: 'accounted',
      summary: '捐赠人赠予博物院的《江南春》等文物出现在拍卖市场，院方称「依规处置伪作」。核心争点是受赠文物的处置制度与公共文化资产确权。',
      parties: [
        { who: '捐赠人及公众', value: 'A', note: '公共文化资产的确权与真相属共济值（非物公共品）' },
        { who: '处置责任方', value: 'C', note: '负贡献待裁定：归责四条件（主体性/因果性/可避免性/修复性）尚未逐条闭合' }
      ],
      pkg: { sha256: null, cert: null, note: '验证包裹未生成' },
      sources: [
        { label: '公开报道（事件进入公众视野）', type: 'media', verifiable: 'partial' },
        { label: '院方回应「依规处置伪作」', type: 'statement', verifiable: 'partial' }
      ],
      versions: [
        { t: '2025-12-17', text: '网页账本以 seed1 录入，日期记为 2025-12-17。' },
        { t: '2026-02-09', text: '小程序账本录入 evt_001，状态 accounted（已归责）。' }
      ],
      discrepancy: 'D1/D3：网页账本日期 2025-12-17 与小程序账本 2026-02-09 不一致，两账本尚未调和。'
    },

    {
      id: 'evt_002', ledgerAlias: 'seed3',
      title: '小红书原员工期权归属争议',
      x: 'human', y: 'mid', z: 'org', j: 'CN',
      t: '2026-07-28',
      geo: { lon: 121.47, lat: 31.23, place: '上海', precision: 'city' },
      rho: null, rhoNote: '未按 MAIP 信封量测',
      status: 'tracking',
      summary: '原员工主张其在职期间的劳动贡献应对应为已承诺的期权权益。是「贡献值 B 的集体确认」的典型样本：记录的贡献应可兑现为应得权益。',
      parties: [
        { who: '原员工', value: 'B', note: '劳动贡献 → 应得权益，属贡献值 B 的兑现主张' },
        { who: '用人方', value: 'C', note: '负贡献待裁定，尚无独立第三方核查' }
      ],
      pkg: { sha256: null, cert: null, note: '验证包裹未生成' },
      sources: [
        { label: '当事人公开陈述', type: 'statement', verifiable: 'partial' }
      ],
      versions: [
        { t: '2026-02-01', text: '网页账本以 seed3 录入。' },
        { t: '2026-07-28', text: '小程序账本录入 evt_002，状态 tracking（追踪中）。' }
      ],
      discrepancy: 'D3：两账本日期不一致（2026-02-01 / 2026-07-28）。'
    },

    {
      id: 'evt_003',
      title: '南山区保险案件（占位录入）',
      x: 'human', y: 'mid', z: 'individual', j: 'CN',
      t: null,
      geo: { lon: 113.93, lat: 22.53, place: '广东深圳南山', precision: 'district' },
      rho: null, rhoNote: '不适用（非真实事现）',
      status: 'placeholder',
      placeholder: true,
      summary: '经事现验证部明确判定为占位示例、非真实事现（verification-report-01.md VF-08）。仅用于演示录入流程，不计入已验证事现总数。',
      parties: [],
      pkg: { sha256: null, cert: null, note: '不适用' },
      sources: [],
      versions: [
        { t: '—', text: '录入为演示占位；事现验证部 VF-08 判定为非事现并显式标注。' }
      ],
      discrepancy: 'D2（存在性不对称）：仅小程序账本有，网页账本无。'
    },

    {
      id: 'evt_004', ledgerAlias: 'seed2',
      title: '耿同学学术打假事件',
      x: 'human', y: 'up', z: 'group', j: 'CN',
      t: '2026-03-20',
      geo: { lon: 116.40, lat: 39.90, place: '中国（学术共同体）', precision: 'approx' },
      rho: null, rhoNote: '未按 MAIP 信封量测',
      status: 'verifying',
      summary: '一人牵头、集体核验，学术不端被坐实。这是设计稿 §3.1「多当事人三值归因」的标准范例：同一事件对不同当事人并存共济值 A 与负贡献 C。',
      parties: [
        { who: '耿同学（举报方）', value: 'A', note: '护真相 = 共济值 A（非物公共品）' },
        { who: '被揭露方', value: 'C', note: '学术不端 = 负贡献，归责四条件基本闭合' }
      ],
      pkg: { sha256: null, cert: null, note: '验证包裹未生成' },
      sources: [
        { label: '集体核验过程公开记录', type: 'collective', verifiable: 'yes' }
      ],
      versions: [
        { t: '2026-01-10', text: '网页账本以 seed2 录入，类型记为「负贡献」。' },
        { t: '2026-03-20', text: '小程序账本录入 evt_004，类型记为「共济值」，状态 verified。' },
        { t: '2026-08-01', text: '账本展望：是否由「已验证」降级为「验证中」待第三方复核。本视图取保守值 verifying。' }
      ],
      discrepancy: 'D1（类型冲突）：两账本一记「共济值」一记「负贡献」。按设计稿 §3.2 判定，此非矛盾而是多当事人并存——已在三值归因中枚举全部当事人分别归值。'
    },

    {
      id: 'evt_005', ledgerAlias: 'seed4',
      title: '红旗驿站：城市贡献者安居（五卡模式 · AI 共同演绎）',
      x: 'human', y: 'up', z: 'group', j: 'CN',
      t: '2026-03-13',
      geo: { lon: 108.94, lat: 34.34, place: '陕西（示意位置）', precision: 'approx' },
      rho: null, rhoNote: '未按 MAIP 信封量测',
      status: 'verifying',
      summary: '事现提案：三位一体框架 + 时间银行 + 三方共担，进入集体验证与社区落地追踪。属制度设计层（五卡模式）的贡献落点。',
      parties: [
        { who: '城市贡献者', value: 'B', note: '劳动与在地贡献 → 贡献值 B' },
        { who: '社会 / 公共侧', value: 'A', note: '安居属生存权范畴 → 共济值 A' }
      ],
      pkg: { sha256: null, cert: null, note: '验证包裹未生成' },
      sources: [
        { label: '事现提案文本 + AI 共同演绎记录', type: 'proposal', verifiable: 'partial' }
      ],
      versions: [
        { t: '2026-03-13', text: '小程序账本录入 evt_005，状态 verifying。' },
        { t: '2026-07-30', text: '网页账本以 seed4 录入「城市贡献者安居」。' },
        { t: '2026-08-01', text: '账本展望：evt_005 与 seed4 是否合并，待裁定。' }
      ],
      discrepancy: 'D2（存在性不对称）：「城市贡献者安居」仅网页账本有；两账本是否为同一事现待裁定。地理位置为示意，非精确落点。'
    },

    {
      id: 'evt_006', ledgerAlias: 'seed5',
      title: 'Kimi 分享链接异常',
      x: 'digital', y: 'mid', z: 'org', j: 'CN',
      t: '2026-07-31',
      geo: { lon: 116.40, lat: 39.90, place: '中国（平台侧）', precision: 'approx' },
      rho: null, rhoNote: '未按 MAIP 信封量测（后并入 evt_009 统一量测）',
      status: 'recording',
      summary: '截图留存：Kimi 分享链接功能异常，单点平台无法保证记录可携带。是 G-9「运输层断裂」的早期单点样本。',
      parties: [
        { who: '记录者', value: 'A', note: '暴露公共基础设施缺陷 → 共济值 A' },
        { who: '平台方', value: null, note: '不记负贡献：能力缺陷未满足归责四条件之「可避免性 / 修复性」' }
      ],
      pkg: { sha256: null, cert: null, note: '截图证据留存，未封包' },
      sources: [
        { label: '异常截图留存', type: 'screenshot', verifiable: 'yes' }
      ],
      versions: [
        { t: '2026-07-31', text: '录入并留存截图；标注单点平台不可作为可携带记录载体。' }
      ],
      discrepancy: null
    },

    {
      id: 'evt_007', ledgerAlias: 'seed6',
      title: '彬县卷烟厂退休职工社保断缴',
      x: 'human', y: 'up', z: 'group', j: 'CN',
      t: '1998',
      geo: { lon: 108.08, lat: 35.03, place: '陕西彬州', precision: 'city' },
      rho: null, rhoNote: '未按 MAIP 信封量测',
      status: 'recording',
      summary: '买断职工社保断缴，属生存权 / 社保制度层的历史遗留。本条最重要的价值不在结论，而在其版本史——它是事现鉴「不能自证」自我约束的实证。',
      parties: [
        { who: '断缴职工群体', value: 'A', note: '社保 = 生存权 → 共济值 A（UDHR 第 22/25 条）' },
        { who: '责任主体', value: 'C', note: '负贡献待第三方核查，归责四条件尚未闭合' }
      ],
      pkg: { sha256: null, cert: null, note: '亲历举证 + 群聊线索，未封包' },
      sources: [
        { label: '记录人单方口述（2025-12 陪同前往陕西省中烟工业公司反映情况）', type: 'testimony', verifiable: 'weak' },
        { label: '微信群「烟厂买断职工群」2025-12-19~22 讨论截图（证明群体真实存在并持续跟进）', type: 'screenshot', verifiable: 'partial' }
      ],
      versions: [
        { t: '—', text: '负贡献原型入册：政府第三方尺，让内部想干事的人有尺可量。' },
        { t: '—', text: '状态更正：由「已验证」降回「记录中」。理由：仅有记录人单方口述，无当事人独立举证、无第三方核查。事现鉴不能自证。' },
        { t: '2025-12', text: '亲历举证补录：白玺陪同母亲及其同事从咸阳前往陕西省中烟工业公司反映情况；带头人被接待，具体答复不详；白玺仅在场陪同未参与交涉；后续多次前往，尚无可记录结果。' }
      ],
      discrepancy: null
    },

    {
      id: 'evt_008', ledgerAlias: 'seed7',
      title: '百度搭子无法生成分享链接',
      x: 'digital', y: 'mid', z: 'org', j: 'CN',
      t: '2026-08-02',
      geo: { lon: 116.40, lat: 39.90, place: '中国（平台侧）', precision: 'approx' },
      rho: null, rhoNote: '未按 MAIP 信封量测（并入 evt_009 统一量测）',
      status: 'recording',
      summary: '尝试生成对话分享链接时系统提示「Share url is missing」，无法获得可携带、可审计的链接。与 evt_006 同类，共同支撑 G-9 的成立。',
      parties: [
        { who: '记录者', value: 'A', note: '暴露平台能力缺陷 → 共济值 A' },
        { who: '平台方', value: null, note: '不记负贡献：未满足归责四条件' }
      ],
      pkg: { sha256: null, cert: null, note: '截图证据留存，未封包' },
      sources: [
        { label: '「Share url is missing」错误截图', type: 'screenshot', verifiable: 'yes' }
      ],
      versions: [
        { t: '2026-08-02', text: '录入；确认该平台不能作为事现鉴交互验证的独立节点。' }
      ],
      discrepancy: null
    },

    {
      id: 'evt_009', ledgerAlias: 'seed8',
      title: '跨平台 AI 分享链接不可用性（G-9 公共事现）',
      x: 'digital', y: 'up', z: 'cross', j: 'CN',
      t: '2026-08-02',
      geo: { lon: 116.40, lat: 39.90, place: '中国（发布地）· 事实跨平台', precision: 'approx' },
      rho: 0.5355,
      rhoBreakdown: { conf: 0.85, sourceIndep: 0.90, evidenceGrade: 0.70, roleWeight: 1.00 },
      rhoNote: '第一个真实 ρ 测量点。0.85 × 0.90 × 0.70 × 1.00 = 0.5355 < ρ_min 0.85，待校准。',
      status: 'recording',
      milestone: true,
      summary: '两张跨平台实证表记录 6–7 家主流 AI 平台（WorkBuddy / 千问 / 百度搭子 / 元宝 / DeepSeek / Kimi / 豆包）原生分享链接的生成或渲染失败。结论：依靠各平台原生分享链接作为跨 AI 验证通道，在当前基础设施下不可行——「运输层断裂」是「可验证」当下真正的瓶颈。',
      parties: [
        { who: '记录者 / 公众', value: 'A', note: '公共基础设施风险的揭示 → 共济值 A' },
        { who: '各平台', value: null, note: '不记负贡献：系统性能力缺陷，非可归责主体行为' }
      ],
      pkg: { sha256: null, cert: '按 SXJ-MAIP/1.0 信封格式记录', note: '已按 MAIP 信封计算 ρ' },
      sources: [
        { label: '百度搭子 App URL 分享页实证表', type: 'table', verifiable: 'yes' },
        { label: '快速模式共创论白皮书解读页实证表', type: 'table', verifiable: 'yes' },
        { label: '微博公开发布（白玺-寰宇光锥舟）', type: 'public', verifiable: 'yes' }
      ],
      versions: [
        { t: '2026-08-02', text: '两张实证表公开记录，G-9 由「观察」升级为「已记录公共事现 evt_009」。' },
        { t: '2026-08-02', text: '按 MAIP 信封格式计算可验证密度 ρ = 0.5355（conf 0.85 × 来源独立度 0.90 × 证据等级 0.70 × 角色权重 1.00）。' }
      ],
      discrepancy: null
    },

    {
      id: 'evt_010', ledgerAlias: 'seed9',
      title: '境外委托复测 G-9（跨境验证模式出现）',
      x: 'digital', y: 'up', z: 'cross', j: 'INTL',
      t: '2026-08-02',
      geo: null,
      geoNote: '境外·具体位置未指明，不臆造落点',
      rho: 0.2700,
      rhoBreakdown: { conf: 0.75, sourceIndep: 0.80, evidenceGrade: 0.45, roleWeight: 1.00 },
      rhoNote: '0.75 × 0.80 × 0.45 × 1.00 = 0.2700，远低于 ρ_min 0.85。明确不升级 evt_009。',
      status: 'recording',
      summary: '委托境外朋友在外国大模型上复测 G-9，结论与国内一致。但证据链为「我→朋友→境外 AI→朋友→我」，含多个不可复核跳转，不能算境外平台直接生成物。本条只记录「跨境验证模式」的出现，以及事现鉴「只记录可验证事实、不美化证据」的自我约束。',
      parties: [
        { who: '委托方 / 受托方', value: 'A', note: '跨境复核尝试 → 共济值 A，但证据等级低' }
      ],
      pkg: { sha256: null, cert: '按 SXJ-MAIP/1.0 信封格式记录', note: '低置信度辅助事现' },
      sources: [
        { label: '朋友转述结论（多跳不可复核）', type: 'hearsay', verifiable: 'weak' },
        { label: '微信截图：Microsoft Copilot 读取 agentos-app.net 链接首次失败需重来', type: 'screenshot', verifiable: 'partial' }
      ],
      versions: [
        { t: '2026-08-02', text: '境外委托复测完成，结论与国内一致；因链过长记为低置信度辅助事现 evt_010，不升级 evt_009。' },
        { t: '2026-08-02', text: '按 MAIP 信封格式计算 ρ = 0.2700。' }
      ],
      discrepancy: null
    },

    /* ---- 城市坐标定位（2026-08-11 新增 · 重点任务） ---- */

    {
      id: 'evt_011',
      title: '彬州市·待发展城市三元重定义（SCA 映射坐标 · 化债试点候选）',
      x: 'human', y: 'up', z: 'juris', j: 'CN',
      t: '2026-08-10',
      geo: { lon: 108.08, lat: 35.03, place: '陕西彬州', precision: 'city' },
      rho: null, rhoNote: '待按 MAIP 信封量测（需实地三元 ρ 核查）',
      status: 'verifying',
      cityProfile: true,
      summary: '彬州市作为「待发展城市」在共创论三元体系内的重定义坐标。旧透镜下以 GDP/财政收入度量→「欠发达」；共创论透镜下按三元(自然ρ+人文ρ+数字ρ)重定义价值。对应 SCA（社会确权资产）三维度映射：①生存复原力35%→自然枝（生态资产/碳汇/植树造林存量）②创新贡献30%→人力枝（劳动力/养老护理人力/社区资本）③全民福利35%→共济值A（社保/生存权）。本条同时承接 evt_007（彬县卷烟厂退休职工社保断缴，1998）的历史经纬——同一城市的「负贡献历史」与「三元重定义未来」并存于坐标系中，正是光锥时空事件点的意义。财政直销注入共济值A基值按 ρ 而非旧财政收入定，若连待发展城市都能凭三元ρ跑通「财政直销+五卡+数字人民币」，则「仅限发达省市」的假设被反证破除。',
      parties: [
        { who: '彬州市居民（含 evt_007 断缴职工群体）', value: 'A', note: '社保=生存权→共济值A（UDHR第22/25条）；三元重定义后应得匹配的A基值' },
        { who: '地方责任主体（历史）', value: 'C', note: ' evt_007 社保断缴的负贡献待裁定；归责四条件尚未闭合' },
        { who: '彬州市（三元重定义后）', value: 'B', note: '生态修复/植树造林/社区服务→贡献值B（主动抉择层）；待量测ρ' }
      ],
      pkg: { sha256: null, cert: null, note: '验证包裹待生成——需实地核查三元ρ（自然GEP/人文劳动/数字数据资产）' },
      sources: [
        { label: '事现鉴-化债-待发展城市与实物债务重定义-讨论.md §1-§3', type: 'doc', verifiable: 'yes' },
        { label: 'evt_007 亲历举证 + 群聊线索（2025-12）', type: 'testimony', verifiable: 'weak' },
        { label: '白玺 2026-08-10 裁定原话（讨论稿§1引用）', type: 'statement', verifiable: 'partial' },
        { label: 'SCA 社会确权资产三维度卡片（截图存证）', type: 'screenshot', verifiable: 'partial' }
      ],
      versions: [
        { t: '1998', text: 'evt_007 时间起点：彬县卷烟厂退休职工社保断缴开始（人力枝负贡献历史线）。' },
        { t: '2025-12', text: '白玺亲历陪同前往陕西省中烟工业公司反映情况；群聊证据留存。' },
        { t: '2026-08-10', text: '白玺裁定：彬州市作为待发展城市示例纳入化债讨论稿；三元重定义框架确立。' },
        { t: '2026-08-11', text: '录入城市坐标定位 evt_011：SCA三维度→SXJ三元映射完成；待实地ρ量测。' }
      ],
      discrepancy: null,
      scaMapping: {
        source: 'Social Confirmation Asset (社会确权资产) 截图卡片',
        formula: 'f_SCA = Σ(优点卡积分×V) + 生态卡资产 + 信用卡亮度×乘数',
        dims: [
          { name: '生存复原力', weight: 0.35, mapsTo: 'natural', note: '碳减排/灾害应对/核安全 → 自然枝ρ' },
          { name: '创新贡献', weight: 0.30, mapsTo: 'human', note: '基础研究/开源项目/制度创新 → 人力枝ρ' },
          { name: '全民福利', weight: 0.35, mapsTo: 'A(共济值)', note: '社保/生存权/社区服务 → 共济值A' }
        ]
      }
    },

    {
      id: 'evt_012',
      title: '深圳市·AI 验证节点聚集与数字枝落地（SCA 映射坐标）',
      x: 'digital', y: 'up', z: 'cross', j: 'CN',
      t: '2026-08-11',
      geo: { lon: 114.06, lat: 22.55, place: '广东深圳', precision: 'city' },
      rho: null, rhoNote: '待按 MAIP 信封量测（需各平台独立ρ核算）',
      status: 'verifying',
      cityProfile: true,
      summary: '深圳市作为「AI 验证节点聚集地」与「数字枝核心城市」的坐标定位。当前已坐上桌的节点：WorkBuddy(seated)、腾讯元宝(seated)——两家均位于深圳。深圳同时也是 evt_003 南山区保险案件（占位非事现）的地理所在地。从 SCA 视角看：深圳的创新贡献维度(30%)高度密集——AI平台、开源项目、前沿技术企业聚集；但生存复原力(35%)和全民福利(35%)的ρ分布不均（高房价/高生活成本对共济值A的挤压是已知张力）。本条将深圳从「evt_003占位点」升级为「真实城市坐标」：数字枝 up 档（系统级AI基础设施），z=cross（跨法域联动潜力——香港毗邻、国际资本/技术通道）。',
      parties: [
        { who: 'WorkBuddy / 元宝等已 seated 节点', value: 'B', note: 'AI平台技术贡献→贡献值B；交互验证参与方' },
        { who: '深圳居民（高房价/生活成本承压群体）', value: 'A', note: '住房/生存成本压力→共济值A诉求；待量测ρ' },
        { who: 'Kimi（北京总部 / 深圳有业务）', value: null, note: 'partial 状态；分享链接异常 evt_006' }
      ],
      pkg: { sha256: null, cert: null, note: '验证包裹待生成——需各AI平台独立ρ核算+城市级三元ρ审计' },
      sources: [
        { label: 'NODES 数据：WorkBuddy(seated)+元宝(seated) 位于深圳', type: 'data', verifiable: 'yes' },
        { label: 'evt_003 南山区保险案件（占位标记）', type: 'record', verifiable: 'partial' },
        { label: 'evt_006 Kimi 分享链接异常 / evt_009 G-9 实证表', type: 'evidence', verifiable: 'yes' },
        { label: 'SCA 社会确权资产截图（创新贡献30%维度）', type: 'screenshot', verifiable: 'partial' }
      ],
      versions: [
        { t: '2026-07-28', text: 'evt_003 占位录入：南山区保险案件（判定为非事现占位）。' },
        { t: '2026-08-02', text: 'evt_009 G-9 公共事现：跨平台分享链接不可用性实证（含深圳节点数据）。' },
        { t: '2026-08-11', text: '录入城市坐标定位 evt_012：从占位点升级为真实城市坐标；SCA映射完成。' }
      ],
      discrepancy: 'D2（存在性不对称）：evt_003 占位与 evt_012 真实坐标共存于同一地理区域；前者标记为非事现、后者为城市级综合定位。',
      scaMapping: {
        source: 'Social Confirmation Asset (社会确权资产) 截图卡片',
        formula: 'f_SCA = Σ(优点卡积分×V) + 生态卡资产 + 信用卡亮度×乘数',
        dims: [
          { name: '创新贡献', weight: 0.30, mapsTo: 'digital', note: 'AI平台/开源/前沿技术 → 数字枝ρ（深圳最强维度）' },
          { name: '生存复原力', weight: 0.35, mapsTo: 'natural', note: '灾害应对/城市韧性 → 自然枝ρ（待评估）' },
          { name: '全民福利', weight: 0.35, mapsTo: 'A(共济值)', note: '住房/社保/社区服务 → 共济值A（高成本压力下的ρ缺口待测）' }
        ]
      }
    }
  ];

  /* ============================================================
   * 8b. 验证节点（地图层：谁已坐到桌上、谁还没来）
   *     依据 SXJ-wiki-map-design.md §4.3
   * ============================================================ */
  var NODE_STATE = {
    seated:  { name: '已坐上桌', color: '#2d8a4e', desc: '已回应交互验证并留下可核对记录' },
    partial: { name: '部分参与', color: '#C9A24B', desc: '有参与痕迹但证据链不完整' },
    review:  { name: '审核中',   color: '#4a5c8a', desc: '已提交，等待对方裁定' },
    absent:  { name: '未到场',   color: '#b9b2a6', desc: '尝试接入失败或未回应' }
  };

  var NODES = [
    { name: 'WorkBuddy', kind: 'AI 平台', j: 'CN', lon: 114.06, lat: 22.55, place: '深圳',
      state: 'seated', note: '多轮交互验证参与方；原生分享链接生成失败（G-9）' },
    { name: '腾讯元宝', kind: 'AI 平台', j: 'CN', lon: 113.94, lat: 22.54, place: '深圳',
      state: 'seated', note: '已回应；分享链接渲染异常（G-9）' },
    { name: '通义千问', kind: 'AI 平台', j: 'CN', lon: 120.16, lat: 30.27, place: '杭州',
      state: 'seated', note: '已回应；分享链接不可用（G-9）' },
    { name: 'DeepSeek', kind: 'AI 平台', j: 'CN', lon: 120.20, lat: 30.25, place: '杭州',
      state: 'seated', note: '已回应；分享链接不可用（G-9）' },
    { name: 'Kimi', kind: 'AI 平台', j: 'CN', lon: 116.31, lat: 39.98, place: '北京',
      state: 'partial', note: '分享链接功能异常，已记为 evt_006' },
    { name: '豆包', kind: 'AI 平台', j: 'CN', lon: 116.48, lat: 39.92, place: '北京',
      state: 'seated', note: '已回应；分享链接不可用（G-9）' },
    { name: '百度搭子', kind: 'AI 平台', j: 'CN', lon: 116.30, lat: 40.05, place: '北京',
      state: 'partial', note: '「Share url is missing」，已记为 evt_008' },
    { name: 'Microsoft Copilot', kind: 'AI 平台', j: 'INTL', lon: -122.12, lat: 47.67, place: 'Redmond',
      state: 'absent', note: '读取外部链接首次失败需重来，未成为独立验证节点（evt_010）' },
    { name: 'DPGA 数字公共产品联盟', kind: '国际机构', j: 'INTL', lon: 10.75, lat: 59.91, place: 'Oslo',
      state: 'review', note: 'DPG 提名 GID0094044 · UNDER REVIEW · 最早结果 2026-09-06' }
  ];

  /* ============================================================
   * 9. 投影 / 查询工具（只做投影，不做计分）
   * ============================================================ */

  function cellKey(x, y) { return x + ':' + y; }

  function getCell(x, y) {
    for (var i = 0; i < CELLS.length; i++) {
      if (CELLS[i].x === x && CELLS[i].y === y) return CELLS[i];
    }
    return null;
  }

  function triad(key) {
    for (var i = 0; i < TRIAD.length; i++) if (TRIAD[i].key === key) return TRIAD[i];
    return null;
  }

  function tier(key) {
    for (var i = 0; i < TIER.length; i++) if (TIER[i].key === key) return TIER[i];
    return null;
  }

  function orgLevel(key) {
    for (var i = 0; i < ORG_LEVEL.length; i++) if (ORG_LEVEL[i].key === key) return ORG_LEVEL[i];
    return null;
  }

  function juris(key) {
    for (var i = 0; i < JURIS.length; i++) if (JURIS[i].key === key) return JURIS[i];
    return null;
  }

  function byId(id) {
    for (var i = 0; i < EVENTS.length; i++) if (EVENTS[i].id === id) return EVENTS[i];
    return null;
  }

  /** 投影：按 (三元, 三档, 法域) 筛选事现。任一参数传 null / 'all' 即不约束。 */
  function project(opt) {
    opt = opt || {};
    return EVENTS.filter(function (e) {
      if (opt.x && opt.x !== 'all' && e.x !== opt.x) return false;
      if (opt.y && opt.y !== 'all' && e.y !== opt.y) return false;
      if (opt.j && opt.j !== 'all' && e.j !== opt.j) return false;
      if (opt.z && opt.z !== 'all' && e.z !== opt.z) return false;
      if (opt.includePlaceholder === false && e.placeholder) return false;
      if (opt.untilYear) {
        var y = eventYear(e);
        if (y === null || y > opt.untilYear) return false;
      }
      return true;
    });
  }

  /** 取事现年份（t 可能是 'YYYY' 或 'YYYY-MM-DD' 或 null） */
  function eventYear(e) {
    if (!e.t) return null;
    var m = String(e.t).match(/^(\d{4})/);
    return m ? parseInt(m[1], 10) : null;
  }

  /**
   * 格子密度读数（诚实投影，不计分）：
   * 返回 { count, measured, rhoAvg, rhoMax, region }
   * - count    落在该格的事现数（不含占位）
   * - measured 其中已按 MAIP 量测出 ρ 的条数
   * - rhoAvg   已量测条目的 ρ 均值；无量测则为 null
   * - region   'balance' 平衡区(ρ≥ρ_min) / 'cross' 交叉区(ρ<ρ_min) / 'unmeasured' 未量测 / 'empty' 空格
   */
  function cellDensity(x, y, opt) {
    opt = opt || {};
    var list = project({ x: x, y: y, j: opt.j, z: opt.z, untilYear: opt.untilYear, includePlaceholder: false });
    var withRho = list.filter(function (e) { return typeof e.rho === 'number'; });
    var sum = 0;
    var max = null;
    withRho.forEach(function (e) {
      sum += e.rho;
      if (max === null || e.rho > max) max = e.rho;
    });
    var avg = withRho.length ? sum / withRho.length : null;
    var region;
    if (!list.length) region = 'empty';
    else if (!withRho.length) region = 'unmeasured';
    else if (avg >= META.rhoMin) region = 'balance';
    else region = 'cross';
    return {
      count: list.length,
      measured: withRho.length,
      rhoAvg: avg,
      rhoMax: max,
      region: region,
      events: list
    };
  }

  /** 区域判据配色：平衡区 蓝金 / 交叉区 红 / 未量测 灰 */
  function regionColor(region) {
    switch (region) {
      case 'balance':    return { fill: '#2F6FED', label: '平衡区', desc: '光锥内部高 ρ 稳定轨迹' };
      case 'cross':      return { fill: '#D85A30', label: '交叉区', desc: '光锥边界低 / 过渡 ρ 的碰撞' };
      case 'unmeasured': return { fill: '#b9b2a6', label: '未量测', desc: '已落点但尚未按 MAIP 量出 ρ' };
      default:           return { fill: '#e8e0d8', label: '空格',   desc: '尚无事现落于此坐标' };
    }
  }

  /** ρ 渐变色：灰 → 金 → 红（沿用 App 原型 rhoColor） */
  function rhoColor(rho) {
    if (typeof rho !== 'number') return '#c9c3b8';
    var lo = [154, 160, 166], mid = [201, 162, 75], hi = [216, 90, 48], c;
    if (rho < 0.5) {
      var k = rho / 0.5;
      c = lo.map(function (v, i) { return Math.round(v + (mid[i] - v) * k); });
    } else {
      var k2 = (rho - 0.5) / 0.5;
      c = mid.map(function (v, i) { return Math.round(v + (hi[i] - v) * k2); });
    }
    return 'rgb(' + c[0] + ',' + c[1] + ',' + c[2] + ')';
  }

  /** 全库统计（诚实读数） */
  function stats() {
    var real = EVENTS.filter(function (e) { return !e.placeholder; });
    var measured = real.filter(function (e) { return typeof e.rho === 'number'; });
    var years = real.map(eventYear).filter(function (y) { return y !== null; });
    return {
      total: real.length,
      placeholder: EVENTS.length - real.length,
      measured: measured.length,
      unmeasured: real.length - measured.length,
      aboveRhoMin: measured.filter(function (e) { return e.rho >= META.rhoMin; }).length,
      minYear: years.length ? Math.min.apply(null, years) : null,
      maxYear: years.length ? Math.max.apply(null, years) : null,
      cellsOccupied: CELLS.filter(function (c) {
        return project({ x: c.x, y: c.y, includePlaceholder: false }).length > 0;
      }).length
    };
  }

  // 通用搜索：在事件（编号/标题/摘要/当事人/来源/坐标/法域/状态）中做不区分大小写匹配
  // 多词以空格分隔时取 AND（全部命中才算）。返回匹配的事件数组（保留 placeholder 标记）。
  function search(q) {
    var term = String(q || '').trim().toLowerCase();
    if (!term) return [];
    var hits = [];
    EVENTS.forEach(function (e) {
      var tri = triad(e.x), ti = tier(e.y), j = juris(e.j), st = STATUS[e.status];
      var hay = [
        e.id, e.title, e.summary || '',
        (e.parties || []).map(function (p) { return (p.who || '') + ' ' + (p.note || ''); }).join(' '),
        (e.sources || []).map(function (s) { return (s.x || '') + ' ' + (s.note || ''); }).join(' '),
        (e.geo && e.geo.place) ? e.geo.place : '', (e.geoNote || ''),
        tri.name, tri.short, ti.name, ti.short, j.name, (st ? st.name : '')
      ].join(' ').toLowerCase();
      var tokens = term.split(/\s+/);
      if (tokens.every(function (t) { return hay.indexOf(t) >= 0; })) hits.push(e);
    });
    return hits;
  }

  return {
    META: META, VALUES: VALUES, SCA: SCA, TRIAD: TRIAD, TIER: TIER, CELLS: CELLS,
    ORG_LEVEL: ORG_LEVEL, JURIS: JURIS, STATUS: STATUS, EVENTS: EVENTS,
    NODES: NODES, NODE_STATE: NODE_STATE,
    cellKey: cellKey, getCell: getCell, triad: triad, tier: tier,
    orgLevel: orgLevel, juris: juris, byId: byId,
    project: project, eventYear: eventYear, cellDensity: cellDensity,
    regionColor: regionColor, rhoColor: rhoColor, stats: stats, search: search
  };
})();

if (typeof module !== 'undefined' && module.exports) { module.exports = SXJ; }
