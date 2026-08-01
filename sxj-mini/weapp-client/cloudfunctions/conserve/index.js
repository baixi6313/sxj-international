// 云函数 consensus —— 第三层「公共层·自动写入」
// 职责：读取第一层 events + 第二层 evidences / verifications，
//       实时计算共识状态、公信力分、SHA-256 哈希链，写入 consensus 集合。
// 权限：consensus 集合对普通用户 read:true, create/update/delete:false，
//       只有本云函数（admin 权限）能写入，用户无法直接篡改汇总结果。

const cloud = require('wx-server-sdk');
const crypto = require('crypto');

cloud.init({ env: cloud.DYNAMIC_CURRENT_ENV });
const db = cloud.database();
const _ = db.command;

const MAX = 1000; // 云函数端单次读取上限

// 计算单个事件的共识记录
async function calcOne(eventId) {
  // 以 id 或 _id 定位事件
  let evt = null;
  const byId = await db.collection('events').where({ id: eventId }).limit(1).get();
  if (byId.data && byId.data.length) {
    evt = byId.data[0];
  } else {
    try {
      const r = await db.collection('events').doc(eventId).get();
      evt = r.data;
    } catch (e) {}
  }
  if (!evt) return null;

  const edRes = await db.collection('evidences').where({ eventId }).limit(MAX).get();
  const vfRes = await db.collection('verifications').where({ eventId }).limit(MAX).get();
  const evidences = edRes.data || [];
  const verifications = vfRes.data || [];

  const stats = { support: 0, oppose: 0, doubt: 0 };
  verifications.forEach(v => { if (stats[v.verdict] !== undefined) stats[v.verdict]++; });
  const total = stats.support + stats.oppose + stats.doubt;
  const evidenceCount = evidences.length;

  // 共识状态判定
  let consensusStatus = 'pending'; // 待验证
  if (total >= 3) {
    if (stats.support > stats.oppose && stats.support >= total * 0.6) consensusStatus = 'reached';      // 共识达成
    else if (stats.oppose >= stats.support) consensusStatus = 'disputed';                                // 争议/反驳成立
    else consensusStatus = 'contested';                                                              // 存疑未决
  }

  // 公信力分：支持占比为主，证据数量加权，封顶 100
  let score = total > 0 ? (stats.support / total) * 100 : 0;
  score = score + Math.min(evidenceCount, 10) * 2;
  score = Math.max(0, Math.min(100, Math.round(score)));

  // SHA-256 哈希链：把事件 + 全部证据 + 全部验证按内容稳定排序后串联
  const chainInput = [evt, ...evidences, ...verifications]
    .map(x => JSON.stringify(x))
    .sort()
    .join('|');
  const chainHash = crypto.createHash('sha256').update(chainInput).digest('hex');

  const now = new Date().toISOString();
  return {
    eventId,
    eventTitle: evt.title || '',
    type: evt.type || '',
    support: stats.support,
    oppose: stats.oppose,
    doubt: stats.doubt,
    totalVerifications: total,
    evidenceCount,
    consensusStatus,
    credibilityScore: score,
    chainHash,
    updatedAt: now
  };
}

// 写入（upsert by eventId）
async function upsert(record) {
  const exist = await db.collection('consensus').where({ eventId: record.eventId }).limit(1).get();
  if (exist.data && exist.data.length) {
    await db.collection('consensus').doc(exist.data[0]._id).update({ data: record });
  } else {
    await db.collection('consensus').add({ data: record });
  }
}

// 遍历全部事件重算（定时触发器调用）
async function recalcAll() {
  const evRes = await db.collection('events').limit(MAX).get();
  const list = evRes.data || [];
  let ok = 0;
  for (const e of list) {
    const eventId = e.id || e._id;
    const rec = await calcOne(eventId);
    if (rec) { await upsert(rec); ok++; }
  }
  return { ok, total: list.length };
}

exports.main = async (event) => {
  try {
    if (!event || !event.eventId) {
      // 无 eventId：全量重算（兜底定时任务）
      const r = await recalcAll();
      return { ok: true, mode: 'recalcAll', ...r };
    }
    const rec = await calcOne(event.eventId);
    if (!rec) return { ok: false, msg: 'event not found: ' + event.eventId };
    await upsert(rec);
    return { ok: true, mode: 'one', record: rec };
  } catch (e) {
    return { ok: false, error: String(e && e.message ? e.message : e) };
  }
};
