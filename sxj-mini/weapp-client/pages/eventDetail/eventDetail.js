const app = getApp();
const store = require('../../utils/store');
const sha256 = require('../../utils/sha256');

Page({
  data: {
    event: null,
    evidences: [],
    verifications: [],
    verdictStats: { support: 0, oppose: 0, doubt: 0 },
    consensus: null,
    shareAnchor: '',
    replies: [],
    replyText: '',
    replyAuthor: '',
    types: app.globalData.types,
    statuses: app.globalData.statuses
  },

  onLoad(options) {
    this.eventId = options.id;
    wx.showShareMenu({ menus: ['shareAppMessage', 'shareTimeline'] });
    this.loadData();
  },

  onShow() {
    if (this.eventId) this.loadData();
  },

  mapEvidences(list) {
    const L = { progress: '进展', evidence: '证据', clue: '线索' };
    return list.map(e => ({ ...e, kindLabel: L[e.kind] || e.kind }));
  },

  mapVerifications(list) {
    const L = { support: '支持', oppose: '反对', doubt: '存疑' };
    return list.map(v => ({ ...v, verdictLabel: L[v.verdict] || v.verdict }));
  },

  loadData() {
    const evt = store.getEventById(this.eventId);
    if (!evt) {
      wx.showToast({ title: '事件不存在', icon: 'none' });
      wx.navigateBack();
      return;
    }
    const anchor = this.calcAnchor(evt);
    const evidences = this.mapEvidences(store.getEvidencesByEvent(this.eventId));
    const verifications = this.mapVerifications(store.getVerificationsByEvent(this.eventId));
    const stats = this.calcStats(verifications);
    const enriched = this.enrich(evt);
    const consensus = store.getConsensusById(this.eventId);
    const replies = this.mapReplies(store.getRepliesByEvent(this.eventId));
    this.setData({ event: enriched, evidences, verifications, verdictStats: stats, consensus: this.mapConsensus(consensus), shareAnchor: anchor, replies });

    // 从云刷新（事件冻结不可改，但他人的证据/验证/跟贴会新增）
    store.refresh().then(() => {
      const e2 = store.getEventById(this.eventId);
      if (!e2) return;
      const anchor2 = this.calcAnchor(e2);
      const ev2 = this.mapEvidences(store.getEvidencesByEvent(this.eventId));
      const vf2 = this.mapVerifications(store.getVerificationsByEvent(this.eventId));
      const c2 = store.getConsensusById(this.eventId);
      const rp2 = this.mapReplies(store.getRepliesByEvent(this.eventId));
      this.setData({
        event: this.enrich(e2),
        evidences: ev2,
        verifications: vf2,
        verdictStats: this.calcStats(vf2),
        consensus: this.mapConsensus(c2),
        shareAnchor: anchor2,
        replies: rp2
      });
    });
  },

  // 事件冻结指纹：同一份记录永远算出同一个锚点，接收方据此验真
  calcAnchor(e) {
    return sha256(JSON.stringify({
      id: e.id, title: e.title, type: e.type, status: e.status,
      createdAt: e.createdAt, updatedAt: e.updatedAt, recorder: e.recorder
    }));
  },

  mapReplies(list) {
    return list.map(r => ({
      ...r,
      hashShort: (r.hash || '').slice(0, 10),
      tsShort: (r.ts || '').replace('T', ' ').slice(0, 19)
    }));
  },

  mapConsensus(c) {
    if (!c) return null;
    const S = {
      pending: '待验证',
      reached: '共识达成',
      disputed: '争议成立',
      contested: '存疑未决'
    };
    return { ...c, statusLabel: S[c.consensusStatus] || c.consensusStatus };
  },

  calcStats(list) {
    const s = { support: 0, oppose: 0, doubt: 0 };
    list.forEach(v => { if (s[v.verdict] !== undefined) s[v.verdict]++; });
    return s;
  },

  enrich(e) {
    const t = this.data.types.find(x => x.key === e.type);
    const s = this.data.statuses.find(x => x.key === e.status);
    return {
      ...e,
      typeLabel: t ? t.label : e.type,
      statusLabel: s ? s.label : e.status
    };
  },

  goAddEvidence() {
    wx.navigateTo({ url: '/pages/addEvidence/addEvidence?id=' + this.eventId });
  },

  goAddVerification() {
    wx.navigateTo({ url: '/pages/addVerification/addVerification?id=' + this.eventId });
  },

  // 转发：携带锚点的分享卡，接收方比对即可验真、防篡改断章取义
  onShareAppMessage() {
    const e = this.data.event;
    return {
      title: '【事现鉴】' + (e ? e.title : '一条公共事现'),
      path: '/pages/eventDetail/eventDetail?id=' + this.eventId + '&anchor=' + this.data.shareAnchor
    };
  },

  onShareTimeline() {
    const e = this.data.event;
    return { title: '【事现鉴】' + (e ? e.title : '一条公共事现') };
  },

  copyShareLink() {
    const e = this.data.event;
    const url = 'https://hygzz.top/events.html#' + this.eventId + '?anchor=' + this.data.shareAnchor;
    const text = '【事现鉴事现】' + (e ? e.title : '') + '\nID: ' + this.eventId +
      '\n锚点(SHA-256): ' + this.data.shareAnchor + '\n链接: ' + url;
    wx.setClipboardData({
      data: text,
      success: () => wx.showToast({ title: '分享信息已复制', icon: 'success' })
    });
  },

  onReplyAuthor(e) { this.setData({ replyAuthor: e.detail.value }); },
  onReplyInput(e) { this.setData({ replyText: e.detail.value }); },

  // 跟贴·讨论：进入哈希链、可回溯，但不计入证据与验证投票
  postReply() {
    const content = (this.data.replyText || '').trim();
    if (!content) { wx.showToast({ title: '说点什么再发', icon: 'none' }); return; }
    const author = (this.data.replyAuthor || '').trim() || '匿名见证人';
    const replies = store.getRepliesByEvent(this.eventId);
    const prevHash = replies.length ? replies[replies.length - 1].hash : this.data.shareAnchor;
    const ts = new Date().toISOString();
    const payload = prevHash + '|' + this.eventId + '|' + author + '|' + content + '|' + ts;
    const hash = sha256(payload);
    const reply = { id: 'rp_' + Date.now(), eventId: this.eventId, author, content, ts, prevHash, hash };
    store.createReply(reply).then(() => {
      this.setData({ replyText: '', replies: this.mapReplies(store.getRepliesByEvent(this.eventId)) });
      wx.showToast({ title: '跟贴已上链', icon: 'success' });
    });
  },

  copyId() {
    wx.setClipboardData({
      data: this.eventId,
      success: () => wx.showToast({ title: 'ID已复制', icon: 'success' })
    });
  }
});
