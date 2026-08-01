// utils/store.js
// 事现鉴·大家的事现 —— 统一数据层
// 设计原则（与云数据库安全规则一致）：
//   events       原始记录：只新建，不可改、不可删（冻结）
//   evidences    证据/线索/进展：任何人可追加新记录，不可改、不可删
//   verifications验证意见：任何人可追加新记录，不可改、不可删
//   verifiers    验证团：可登记，可改/删自己
// 云开发优先，本地 storage 兜底。

const ENV_ID = 'cloudbase-d6gtguv2rd874f564';

let _cloudInited = false;

function initCloud() {
  if (_cloudInited) return;
  if (ENV_ID && wx.cloud) {
    try {
      wx.cloud.init({ env: ENV_ID, traceUser: true });
      _cloudInited = true;
    } catch (e) {
      _cloudInited = false;
    }
  }
}

function cloudOk() {
  return !!(ENV_ID && wx.cloud && _cloudInited);
}

function db() {
  return wx.cloud.database();
}

const K = {
  events: 'sxj_events',
  verifiers: 'sxj_verifiers',
  evidences: 'sxj_evidences',
  verifications: 'sxj_verifications',
  consensus: 'sxj_consensus',
  replies: 'sxj_replies'
};

function getSync(k) { return wx.getStorageSync(k) || []; }
function setLocal(k, v) { wx.setStorageSync(k, v); }

// —— 刷新：从云拉全部集合写入本地缓存 ——
async function refresh() {
  if (!cloudOk()) return false;
  try {
    const ev = await db().collection('events').orderBy('createdAt', 'desc').limit(100).get();
    const ve = await db().collection('verifiers').limit(100).get();
    const ed = await db().collection('evidences').orderBy('createdAt', 'asc').limit(300).get();
    const vf = await db().collection('verifications').orderBy('createdAt', 'asc').limit(300).get();
    const cs = await db().collection('consensus').limit(300).get();
    if (ev.data && ev.data.length) setLocal(K.events, ev.data);
    if (ve.data && ve.data.length) setLocal(K.verifiers, ve.data);
    if (ed.data) setLocal(K.evidences, ed.data);
    if (vf.data) setLocal(K.verifications, vf.data);
    if (cs.data) setLocal(K.consensus, cs.data);
    return true;
  } catch (e) {
    return false;
  }
}

// —— 创建事件（仅新建，冻结不可改）——
async function createEvent(evt) {
  const list = getSync(K.events);
  list.unshift(evt);
  setLocal(K.events, list);
  if (cloudOk()) {
    try {
      const res = await db().collection('events').add(evt);
      if (res && res._id) { evt._id = res._id; if (!evt.id) evt.id = res._id; }
    } catch (e) {}
  }
  return evt;
}

// —— 追加证据 / 线索 / 进展（仅新建）——
async function createEvidence(ev) {
  const list = getSync(K.evidences);
  list.unshift(ev);
  setLocal(K.evidences, list);
  if (cloudOk()) {
    try {
      const res = await db().collection('evidences').add(ev);
      if (res && res._id) { ev._id = res._id; if (!ev.id) ev.id = res._id; }
    } catch (e) {}
  }
  return ev;
}

// —— 追加验证意见（仅新建）——
async function createVerification(vf) {
  const list = getSync(K.verifications);
  list.unshift(vf);
  setLocal(K.verifications, list);
  if (cloudOk()) {
    try {
      const res = await db().collection('verifications').add(vf);
      if (res && res._id) { vf._id = res._id; if (!vf.id) vf.id = res._id; }
    } catch (e) {}
  }
  return vf;
}

// —— 追加跟贴·讨论（仅新建；非证据、不进验证投票）——
async function createReply(reply) {
  const list = getSync(K.replies);
  list.unshift(reply);
  setLocal(K.replies, list);
  if (cloudOk()) {
    try {
      const res = await db().collection('replies').add(reply);
      if (res && res._id) { reply._id = res._id; if (!reply.id) reply.id = res._id; }
    } catch (e) {}
  }
  return reply;
}

// 读取某事件的跟贴（按时间升序，便于展示哈希链顺序）
function getRepliesByEvent(eventId) {
  return getSync(K.replies)
    .filter(r => r.eventId === eventId)
    .sort((a, b) => (a.ts || '').localeCompare(b.ts || ''));
}

// 兼容旧接口（验证团管理）
async function saveVerifier(v) {
  const list = getSync(K.verifiers);
  const idx = list.findIndex(x => x.id === v.id);
  if (idx >= 0) list[idx] = v; else list.unshift(v);
  setLocal(K.verifiers, list);
  if (cloudOk()) {
    try { await db().collection('verifiers').doc(v.id).set(v); } catch (e) {}
  }
  return v;
}

async function removeVerifier(id) {
  let list = getSync(K.verifiers).filter(x => x.id !== id);
  setLocal(K.verifiers, list);
  if (cloudOk()) {
    try { await db().collection('verifiers').doc(id).remove(); } catch (e) {}
  }
}

// —— 查询辅助 ——
function getEventById(id) {
  const all = getSync(K.events);
  return all.find(e => e.id === id || e._id === id) || null;
}
function getEvidencesByEvent(eventId) {
  return getSync(K.evidences).filter(e => e.eventId === eventId);
}
function getVerificationsByEvent(eventId) {
  return getSync(K.verifications).filter(v => v.eventId === eventId);
}

// —— 第三层共识：从本地缓存读取某事件的共识汇总 ——
function getConsensusById(eventId) {
  const all = getSync(K.consensus);
  return all.find(c => c.eventId === eventId) || null;
}

// —— 触发共识云函数（第三层自动写入）——
// 提交证据/验证后调用，请云函数重算该事件的共识并写回 consensus 集合。
// 注：云端函数实际名为 conserve（创建时手误），本地目录已同步为 conserve。
function callConsensus(eventId) {
  if (!cloudOk()) return Promise.resolve(null);
  return wx.cloud.callFunction({
    name: 'conserve',
    data: { eventId }
  }).then(res => res && res.result ? res.result : null).catch(() => null);
}

module.exports = {
  ENV_ID,
  initCloud,
  refresh,
  createEvent,
  createEvidence,
  createVerification,
  saveVerifier,
  removeVerifier,
  getEventById,
  getEvidencesByEvent,
  getVerificationsByEvent,
  getConsensusById,
  createReply,
  getRepliesByEvent,
  callConsensus,
  // 兼容别名：读取时按 id 去重，防御历史重复数据
  getEventsSync: () => {
    const list = getSync(K.events);
    const seen = new Set();
    return list.filter(e => { if (seen.has(e.id)) return false; seen.add(e.id); return true; });
  },
  getVerifiersSync: () => getSync(K.verifiers)
};
