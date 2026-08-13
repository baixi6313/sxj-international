// 验证团数据模型（基于《验证团定义 v2》锁定稿）
// 三层：原始记录(event·冻结) / 验证层(participants·可追加) / 公共共识(consensus·社区热点驱动)
// 三值：共济值 A(集体·共识) / 贡献值 B(个人·CV账本) / 负贡献(归责·修复)

var crypto = require('./crypto.js');

// 本地数据版本戳：所有预置数据更新至该时刻
var DATA_VERSION = '2026-07-30 11:30';

// 预置 3 个真实种子案例（已达集体需求「共济值」的事现鉴）
var EVENTS = [
  {
    id: 'seed1',
    title: '南京博物院《江南春》等受赠文物流失事件',
    type: '共济值',
    date: '2025-12-17',
    summary: '公众自发取证、交叉验证、形成共识：受赠文物去向成谜。省级通报 24 人被查、4 幅追回（已归责）。',
    status: 'reached',
    evidenceCount: 18,
    votes: { support: 31, oppose: 2, doubt: 3 },
    participants: [
      { name: '李某', city: '南京', role: '证据提供者', action: '上传馆藏调拨单据照片', delta: 12 },
      { name: '张某', city: '北京', role: '质疑者', action: '追问文物出境审批记录', delta: 8 },
      { name: '网友·沪', city: '上海', role: '确认者', action: '投票支持·交叉比对', delta: 3 },
      { name: '网友·穗', city: '广州', role: '确认者', action: '投票支持', delta: 3 },
      { name: '王某', city: '南京', role: '被归责', action: '失职致文物流失', delta: -40 },
      { name: '赵某', city: '南京', role: '被归责', action: '伪造保管台账', delta: -55 }
    ]
  },
  {
    id: 'seed2',
    title: '耿同学学术打假事件',
    type: '共济值',
    date: '2026-01-08',
    summary: '当事人公开实验原始数据自证，评审与网友交叉验证，形成对造假结论的共识性推翻。',
    status: 'reached',
    evidenceCount: 22,
    votes: { support: 44, oppose: 1, doubt: 2 },
    participants: [
      { name: '耿同学', city: '西安', role: '证据提供者', action: '公开实验原始数据与日志', delta: 20 },
      { name: '评审·刘', city: '武汉', role: '确认者', action: '独立复核并背书', delta: 10 },
      { name: '网友·蓉', city: '成都', role: '质疑者', action: '要求公开原始记录', delta: 6 },
      { name: '网友·杭', city: '杭州', role: '确认者', action: '投票支持', delta: 3 },
      { name: '某导师', city: '北京', role: '被归责', action: '数据造假·署名不当', delta: -60 }
    ]
  },
  {
    id: 'seed3',
    title: '小红书前员工期权纠纷',
    type: '共济值',
    date: '2026-02-09',
    summary: '前员工公开期权协议截图引发公众验证，公司回应前后矛盾，共识仍在拉锯（disputed 边缘）。',
    status: 'contested',
    evidenceCount: 15,
    votes: { support: 28, oppose: 5, doubt: 4 },
    participants: [
      { name: '前员工·林', city: '上海', role: '证据提供者', action: '公开期权协议截图', delta: 15 },
      { name: 'HR·陈', city: '上海', role: '被归责', action: '否认协议效力', delta: -30 },
      { name: '网友·深', city: '深圳', role: '确认者', action: '投票支持', delta: 3 },
      { name: '网友·京', city: '北京', role: '质疑者', action: '要求公司正式回应', delta: 7 }
    ]
  },
  {
    id: 'seed4',
    title: '红旗驿站：城市贡献者安居与社区治理方案（五卡模式·贡献值B）',
    type: '贡献值',
    date: '2026-03-13',
    summary: '五卡模式·贡献值（B）的城市治理落地案例：城市贡献者（建筑工／环卫／快递／骑手）安居与社区治理方案。以「精神传承 + 市场运营 + 社会治理」三位一体为骨架，叠加「时间银行」，由「财政 / 企业 / 群众」三方共担成本，深圳南山 2026-2027 试点，共创论在城市治理的首个落地方案。⚠️ 本事现为白玺与 AI 共同演绎生成的策划／推演框架（来源 QvTl71Vzv），非实地实施。',
    status: 'contested',
    evidenceCount: 26,
    votes: { support: 52, oppose: 3, doubt: 6 },
    participants: [
      { name: '建筑工·老周', city: '西安', role: '贡献者', action: '提供安居申请与工时凭证', delta: 18 },
      { name: '环卫工·阿梅', city: '成都', role: '贡献者', action: '登记时间银行服务时长', delta: 15 },
      { name: '快递员·小吴', city: '深圳', role: '贡献者', action: '参与社区议事会提案', delta: 12 },
      { name: '区住建·财政', city: '西安', role: '公助主体', action: '配建保障性租赁住房+补贴', delta: 20 },
      { name: '物流公司', city: '深圳', role: '企业共担', action: '按用工缴存安居基金', delta: 16 },
      { name: '社区志愿者', city: '成都', role: '群众互助', action: '时间银行跨代际兑付', delta: 8 },
      { name: '居委会', city: '西安', role: '治理协同', action: '组织贡献者议事会', delta: 10 },
      { name: '网友·质疑', city: '北京', role: '质疑者', action: '追问企业缴存落实', delta: 5 },
      { name: '某企业HR', city: '深圳', role: '被归责', action: '未履行用工缴存义务', delta: -25 }
    ]
  }
];

function getEventById(id) {
  for (var i = 0; i < EVENTS.length; i++) {
    if (EVENTS[i].id === id) return EVENTS[i];
  }
  return null;
}

// 事件层共识（靠人数 / 社区热点）
function computeConsensus(ev) {
  var S = ev.votes.support, O = ev.votes.oppose, D = ev.votes.doubt;
  var total = S + O + D;
  var recognition = total > 0 ? S / total : 0;
  var E = ev.evidenceCount;
  var credibility = Math.min(100, Math.round(recognition * 100) + Math.min(E, 10) * 2);
  // 共济值 A = 共识高度（社区热点驱动 · 纵轴）
  var gongjiA = credibility;
  return {
    E: E, S: S, O: O, D: D,
    recognition: recognition,
    recognitionPct: Math.round(recognition * 100),
    credibility: credibility,
    gongjiA: gongjiA,
    status: ev.status
  };
}

// 个人层 CV 账本（跟人走）：贡献值 B 净值 = 正减负；负贡献照扣
function computeMemberCV(p) {
  var cv = p.delta >= 0 ? p.delta : 0;
  var ncv = p.delta < 0 ? p.delta : 0;
  return { cv: cv, ncv: ncv, net: p.delta };
}

// SHA-256 哈希链（双向回路）：prevHash + 记录 → hash
function computeChain(ev) {
  var prev = '0';
  var chain = [];
  for (var i = 0; i < ev.participants.length; i++) {
    var p = ev.participants[i];
    var rec = {
      seq: i + 1,
      actor: p.name,
      city: p.city,
      role: p.role,
      action: p.action,
      delta: p.delta,
      prevHash: prev
    };
    var hash = crypto.hashText(prev + '|' + p.name + '|' + p.role + '|' + p.action + '|' + p.delta);
    rec.hash = hash;
    chain.push(rec);
    prev = hash;
  }
  return { chain: chain, rootHash: prev };
}

module.exports = {
  EVENTS: EVENTS,
  getEventById: getEventById,
  computeConsensus: computeConsensus,
  computeMemberCV: computeMemberCV,
  computeChain: computeChain
};
