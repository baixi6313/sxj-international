// We+SXJ local data store.
// Records are kept in device storage and linked into a SHA-256 hash chain,
// mirroring the "事现鉴" bidirectional verification idea (verifiable, not tamperable).

const { sha256 } = require('./sha256.js');

const KEY_PROFILE  = 'wsxj_profile';
const KEY_RECORDS  = 'wsxj_records';   // self / assisted water records (chained)
const KEY_ASSIST   = 'wsxj_assist';    // assist claims (pending/confirmed/rejected)
const KEY_FEEDBACK = 'wsxj_feedback';
const KEY_CHAIN    = 'wsxj_chain';     // last hash, for chaining
const KEY_CHECKIN  = 'wsxj_checkin';  // 每日签到日期列表
const KEY_CRED     = 'wsxj_credential'; // 共济值凭证（签到里程碑 / 饮水达标）

function get(key, def) {
  try { var v = wx.getStorageSync(key); return (v === '' || v === undefined || v === null) ? def : v; }
  catch (e) { return def; }
}
function set(key, val) {
  try { wx.setStorageSync(key, val); } catch (e) {}
}

function pad(n) { return ('0' + n).slice(-2); }
function todayStr() {
  var d = new Date();
  return d.getFullYear() + '-' + pad(d.getMonth() + 1) + '-' + pad(d.getDate());
}
function yesterdayStr() {
  var d = new Date(); d.setDate(d.getDate() - 1);
  return d.getFullYear() + '-' + pad(d.getMonth() + 1) + '-' + pad(d.getDate());
}
// 返回 dateStr 的前一天（YYYY-MM-DD）
function prevDay(dateStr) {
  var p = dateStr.split('-');
  var d = new Date(Number(p[0]), Number(p[1]) - 1, Number(p[2]));
  d.setDate(d.getDate() - 1);
  return d.getFullYear() + '-' + pad(d.getMonth() + 1) + '-' + pad(d.getDate());
}

// 60+ target 2500ml/day; others 2000ml/day
function getTarget(age) {
  return (age && !isNaN(age) && Number(age) >= 60) ? 2500 : 2000;
}

function chainHash(dataObj, prevHash) {
  return sha256(JSON.stringify(dataObj) + '|' + (prevHash || '0'));
}

// 唯一 id：时间戳 + 自增序号 + 随机数，避免同一毫秒内两条记录 id 碰撞
// （碰撞会导致 confirmAssist 误匹配已确认记录，使另一条永远留在待确认）
var _seq = 0;
function uid(prefix) {
  _seq = (_seq + 1) % 1000000;
  return prefix + Date.now() + '_' + _seq + '_' + Math.floor(Math.random() * 1e6);
}

// ---- profile ----
function getProfile() { return get(KEY_PROFILE, { name: '', age: '' }); }
function saveProfile(p) { set(KEY_PROFILE, p); }

// ---- self / assisted water records ----
function getSelfRecords() { return get(KEY_RECORDS, []); }
function getPrevHash() { return get(KEY_CHAIN, '0'); }

function pushRecord(rec) {
  var recs = getSelfRecords();
  var prev = getPrevHash();
  rec.prevHash = prev;
  rec.hash = chainHash(rec, prev);
  recs.push(rec);
  set(KEY_RECORDS, recs);
  set(KEY_CHAIN, rec.hash);
  return rec;
}

// 自我记录（本人饮水）
function addSelfRecord(ml) {
  var ts = Date.now();
  var rec = { id: uid('s'), date: todayStr(), ts: ts, ml: ml, source: 'self' };
  pushRecord(rec);
  maybeGrantWaterCred();   // 达标即发共济值凭证
  return rec;
}

// 协助记录：assistant 协助 target 喝了 ml。
// target 默认=本机用户（"别人帮我"）；也可填他人（"我帮别人"），使排名人数有意义。
function addAssistClaim(assistant, target, ml) {
  var p = getProfile();
  var t = (target && ('' + target).trim()) ? ('' + target).trim() : (p.name || '我');
  var a = getAssist();
  var ts = Date.now();
  var rec = { id: uid('a'), date: todayStr(), ts: ts, assistant: assistant, target: t, ml: ml, status: 'pending' };
  rec.hash = sha256(JSON.stringify(rec));
  a.push(rec);
  set(KEY_ASSIST, a);
  return rec;
}

// 被协助人确认：双方各得凭证。
// 仅当被协助人=本机用户时，才把这份共济值饮水记入本机今日总量（他人设备各自记各自的）。
function confirmAssist(id) {
  var a = getAssist();
  var found = null;
  for (var i = 0; i < a.length; i++) { if (a[i].id === id) { found = a[i]; break; } }
  if (!found || found.status !== 'pending') return null;
  found.status = 'confirmed';
  var me = getProfile().name || '我';
  if (found.target === me) {
    var ts = Date.now();
    var rec = { id: uid('c'), date: found.date, ts: ts, ml: found.ml, source: 'assist', assistant: found.assistant, target: found.target };
    pushRecord(rec);          // 本机用户获共济值饮水凭证
    maybeGrantWaterCred();   // 达标即发共济值凭证
  }
  set(KEY_ASSIST, a);        // 协助人正贡献计数（排名统计）
  return found;
}

function rejectAssist(id) {
  var a = getAssist();
  for (var i = 0; i < a.length; i++) { if (a[i].id === id) { a[i].status = 'rejected'; break; } }
  set(KEY_ASSIST, a);
}

// ---- assist list ----
function getAssist() { return get(KEY_ASSIST, []); }
function getPending() { return getAssist().filter(function (x) { return x.status === 'pending'; }); }
function getConfirmedAssists() { return getAssist().filter(function (x) { return x.status === 'confirmed'; }); }

// ---- today total (仅本人饮水：self + 被协助人=我的协助饮水) ----
function getTodayTotal() {
  var t = todayStr();
  var sum = 0;
  getSelfRecords().forEach(function (r) { if (r.date === t) sum += r.ml; });
  return sum;
}

// ---- ranking: by number of distinct people assisted ----
// 现在 assistant 可协助不同 target，人数 = distinct(target) 才有意义。
function getRanking() {
  var confirmed = getConfirmedAssists();
  var map = {};
  confirmed.forEach(function (a) {
    if (!map[a.assistant]) map[a.assistant] = { name: a.assistant, times: 0, people: {}, ml: 0 };
    map[a.assistant].times++;
    map[a.assistant].people[a.target] = true;
    map[a.assistant].ml += a.ml;
  });
  var arr = Object.keys(map).map(function (k) {
    return { name: map[k].name, times: map[k].times, people: Object.keys(map[k].people).length, ml: map[k].ml };
  });
  arr.sort(function (x, y) { return (y.people - x.people) || (y.times - x.times) || (y.ml - x.ml); });
  return arr;
}

// ---- feedback ----
function getFeedback() { return get(KEY_FEEDBACK, []); }
function addFeedback(reason, detail) {
  var f = getFeedback();
  var ts = Date.now();
  f.push({ id: uid('f'), date: todayStr(), ts: ts, reason: reason, detail: detail });
  set(KEY_FEEDBACK, f);
}

// ================= 共济值凭证 =================
function getCredentials() { return get(KEY_CRED, []); }
function grantCredential(type, value, label) {
  var ts = Date.now();
  var obj = { type: type, value: value, label: label, date: todayStr(), ts: ts };
  obj.hash = sha256(JSON.stringify(obj));
  var list = getCredentials();
  list.push(obj);
  set(KEY_CRED, list);
  return obj;
}
// 饮水达标发共济值凭证（每天一次）
function maybeGrantWaterCred() {
  var p = getProfile();
  var target = getTarget(p.age);
  var total = getTodayTotal();
  if (target > 0 && total >= target) {
    var creds = getCredentials();
    var t = todayStr();
    if (!creds.some(function (c) { return c.type === 'water' && c.date === t; })) {
      return grantCredential('water', total, '今日饮水达标 ' + total + 'ml · 共济值凭证');
    }
  }
  return null;
}

// ================= 每日签到 =================
function getCheckins() { return get(KEY_CHECKIN, []); }

// 当前连续签到天数 + 是否已签 + 累计天数 + 凭证
function checkinState() {
  var list = getCheckins();
  var dates = [];
  list.forEach(function (c) { if (dates[dates.length - 1] !== c.date) dates.push(c.date); });
  dates.sort();
  var t = todayStr();
  var checkedToday = dates.length > 0 && dates[dates.length - 1] === t;
  var streak = 0;
  if (dates.length > 0) {
    var last = dates[dates.length - 1];
    // 仅当最近一次是今天或昨天，才算连续中
    if (last === t || last === yesterdayStr()) {
      var ci = dates.length - 1;
      if (dates[ci] === t) { streak = 1; ci--; }
      else if (dates[ci] === yesterdayStr()) { streak = 1; ci--; } // 数到昨天为止
      while (ci >= 0 && prevDay(dates[ci + 1]) === dates[ci]) { streak++; ci--; }
    }
  }
  return { checkedToday: checkedToday, streak: streak, total: dates.length, credentials: getCredentials() };
}

// 签到：返回 {already, state, newCredential}
function doCheckin() {
  var list = getCheckins();
  var t = todayStr();
  if (list.some(function (c) { return c.date === t; })) {
    return { already: true, state: checkinState(), newCredential: null };
  }
  list.push({ date: t, ts: Date.now() });
  set(KEY_CHECKIN, list);
  var state = checkinState();
  // 里程碑共济值凭证：7 / 30 / 100 天
  var milestones = [7, 30, 100];
  var newCred = null;
  milestones.forEach(function (m) {
    if (state.streak === m &&
        !getCredentials().some(function (c) { return c.type === 'checkin' && c.value === m; })) {
      newCred = grantCredential('checkin', m, '连续签到 ' + m + ' 天 · 共济值健康凭证');
    }
  });
  state.newCredential = newCred;
  return { already: false, state: state, newCredential: newCred };
}

module.exports = {
  getProfile: getProfile,
  saveProfile: saveProfile,
  getTarget: getTarget,
  addSelfRecord: addSelfRecord,
  addAssistClaim: addAssistClaim,
  confirmAssist: confirmAssist,
  rejectAssist: rejectAssist,
  getSelfRecords: getSelfRecords,
  getPending: getPending,
  getConfirmedAssists: getConfirmedAssists,
  getTodayTotal: getTodayTotal,
  getRanking: getRanking,
  getFeedback: getFeedback,
  addFeedback: addFeedback,
  // 凭证
  getCredentials: getCredentials,
  grantCredential: grantCredential,
  // 签到
  getCheckins: getCheckins,
  checkinState: checkinState,
  doCheckin: doCheckin
};
