const store = require('./utils/store');

// 核心演示种子：固定 id，首次播种或补齐时复用。
// 真实网络公开事件：evt_001 南京博物院、evt_002 小红书期权、evt_004 耿同学学术打假
// AI 共同演绎推演框架：evt_005 红旗驿站（五卡模式·贡献值B）；evt_003 南山区保险为录入占位
function CORE_SEED_EVENTS(now) {
  return [
    {
      id: 'evt_001',
      title: '南京博物院《江南春》等藏品流向拍卖',
      type: 'common',
      date: '2026-02-09',
      location: '南京',
      description: '捐赠藏品被质疑失踪后现身拍卖，公众交叉验证后推动省级调查组通报，24人被查、4幅追回。',
      evidence: '工信部备案 / 媒体报道 / 拍卖记录',
      recorder: '事现鉴',
      status: 'accounted',
      createdAt: now,
      updatedAt: now,
      verifyGroup: ['ver_001']
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
      status: 'tracking',
      createdAt: now,
      updatedAt: now,
      verifyGroup: []
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
      status: 'recording',
      createdAt: now,
      updatedAt: now,
      verifyGroup: []
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
      status: 'verified',
      createdAt: now,
      updatedAt: now,
      verifyGroup: []
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
      status: 'verifying',
      createdAt: now,
      updatedAt: now,
      verifyGroup: []
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
      status: 'recording',
      createdAt: now,
      updatedAt: now,
      verifyGroup: []
    },
    {
      id: 'evt_007',
      title: '彬县卷烟厂退休职工社保断缴（陕西省中烟工业公司 · 负贡献原型 · evt_BX_1998_001）',
      type: 'negative',
      date: '1998',
      location: '陕西·咸阳·彬县',
      description: '1998 年国企改制后，彬县卷烟厂部分退休职工社保断缴、档案缺失。政府内部困境：劳动监察想追缴没预算、社保局想补缴没档案、纪委想查证灭失、信访无执法权。事现鉴在此充当第三方尺——当事人冻结证据＝不是上访是「记账」；多人独立陈述互相印证＝不是聚众是「共识收敛」；事实经第三方核查确立＝不是闹访是「事实确立」；内部支持者引用＝不是翻旧账是「按协议执行」。⚠️ 当前状态：记录中。本条目目前仅有记录人一方口述与一份群聊线索，尚无当事人独立结构化举证、亦未经无利害关系第三方核查，不构成已验证事实。下一步：开放当事人（退休职工及家属）留言举证，再交验证团逐条核查。亲历举证：2025 年 12 月，白玺陪同母亲（彬县卷烟厂买断职工）及母亲的几位同事，从咸阳坐地铁前往陕西省中烟工业公司反映情况；现场由对方工作人员接待了带头人，具体答复内容不详；白玺本人仅在场陪同，未参与交涉；已知后续多次前往，目前尚未取得可记录结果。群聊线索：微信群「烟厂买断职工群」截图显示，2025 年 12 月 19-22 日间成员持续讨论省中烟公司、咸阳卷烟厂、破产公司相关话题，可证明该群体真实存在并在持续跟进同一事件。',
      evidence: '来源：用户与 WorkBuddy 对话 2026-07-31（白玺亲历口述+群聊截图，属有利害关系方举证）；附件：evidence/wechat-group-bx-2025-12.jpg',
      recorder: '白玺',
      status: 'recording',
      createdAt: now,
      updatedAt: now,
      verifyGroup: []
    }
  ];
}

App({
  onLaunch() {
    store.initCloud();

    // 优先从云端拉取；云端有数据就用云端的，没有才写入示例种子
    store.refresh().then(ok => {
      const events = wx.getStorageSync('sxj_events') || [];
      const verifiers = wx.getStorageSync('sxj_verifiers') || [];
      if (!events.length && !verifiers.length) {
        this.seedData();
      } else {
        // 已部署过的用户：确保核心演示种子（含红旗驿站、耿同学）补齐，不重复造
        this.ensureCoreSeeds();
      }
    });
  },

  // 核心演示种子：固定 id，本地去重后补齐，避免历史重复数据累积
  ensureCoreSeeds() {
    const now = new Date().toISOString();
    let events = wx.getStorageSync('sxj_events') || [];
    // 去重：同一 id 只保留第一条（数组前面的更新）
    const seen = new Set();
    events = events.filter(e => { if (seen.has(e.id)) return false; seen.add(e.id); return true; });
    const existing = new Set(events.map(e => e.id));
    const missing = CORE_SEED_EVENTS(now).filter(seed => !existing.has(seed.id));
    if (missing.length) {
      events = missing.concat(events);
    }
    wx.setStorageSync('sxj_events', events);
    // 静默尝试云端同步 missing（失败不阻塞）
    if (missing.length && wx.cloud && wx.cloud.database) {
      missing.forEach(seed => {
        try {
          wx.cloud.database().collection('events').add({ data: seed }).catch(() => {});
        } catch (e) {}
      });
    }
  },

  seedData() {
    const now = new Date().toISOString();
    // 去重：同一 id 只保留一条
    const seen = new Set();
    const demoEvents = CORE_SEED_EVENTS(now).filter(e => { if (seen.has(e.id)) return false; seen.add(e.id); return true; });
    const demoVerifiers = [
      {
        id: 'ver_001',
        name: '白玺',
        role: '记录发起人',
        contact: '',
        weight: 1.0,
        createdAt: now
      }
    ];
    const demoEvidences = [
      { _id: 'ed_001', eventId: 'evt_001', kind: 'progress', content: '省级调查组通报：24人被查，4幅藏品追回', author: '事现鉴', createdAt: now },
      { _id: 'ed_002', eventId: 'evt_001', kind: 'evidence', content: '工信部备案信息可查 / 多家媒体报道截图留存', author: '验证团', createdAt: now },
      { _id: 'ed_003', eventId: 'evt_002', kind: 'clue', content: '当事人已公开期权协议关键页，待更多前员工交叉印证', author: '验证团', createdAt: now }
    ];
    const demoVerifications = [
      { _id: 'vf_001', eventId: 'evt_001', verdict: 'support', content: '线索可互证，建议认定为共济值已达成', author: '白玺', createdAt: now }
    ];
    wx.setStorageSync('sxj_events', demoEvents);
    wx.setStorageSync('sxj_verifiers', demoVerifiers);
    wx.setStorageSync('sxj_evidences', demoEvidences);
    wx.setStorageSync('sxj_verifications', demoVerifications);

    // 云环境就绪时，把种子数据直接写入云端（不经过 createEvent，避免重复 unshift 本地缓存）
    if (store.ENV_ID && wx.cloud && wx.cloud.database) {
      const db = wx.cloud.database();
      demoEvents.forEach(evt => { try { db.collection('events').add({ data: evt }).catch(() => {}); } catch (e) {} });
      demoVerifiers.forEach(v => { try { db.collection('verifiers').add({ data: v }).catch(() => {}); } catch (e) {} });
      demoEvidences.forEach(e => { try { db.collection('evidences').add({ data: e }).catch(() => {}); } catch (e) {} });
      demoVerifications.forEach(v => { try { db.collection('verifications').add({ data: v }).catch(() => {}); } catch (e) {} });
    }
  },

  globalData: {
    types: [
      { key: 'common', label: '共济值', desc: '公众知情权 / 基本事实' },
      { key: 'contribution', label: '贡献值', desc: '谁创造了什么 / 该得什么' },
      { key: 'negative', label: '负贡献', desc: '损害 / 追责' }
    ],
    statuses: [
      { key: 'recording', label: '记录中', color: '#999' },
      { key: 'verifying', label: '验证中', color: '#e6a23c' },
      { key: 'verified', label: '已验证', color: '#67c23a' },
      { key: 'accounted', label: '已归责', color: '#a23b32' },
      { key: 'resolved', label: '已解决', color: '#409eff' },
      { key: 'invalid', label: '未成立', color: '#909399' }
    ],
    testVersion: '2026-07-30 11:30',
    provenanceNote: '站内所记事现中，仅「南京博物院藏品流向」「耿同学学术打假」「小红书前员工期权」三件为网络公开、可独立核实的真实事件；其余所有事现（含「红旗驿站」等）均为白玺与 AI 共同演绎生成（附时间戳可验证），仅供框架推演，非既成事实。'
  }
});
