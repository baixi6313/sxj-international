var model = require('../../utils/model.js');

var STATUS_LABEL = {
  pending: '待验证',
  reached: '已共识',
  disputed: '有争议',
  contested: '拉锯中'
};

function short(h) { return h.slice(0, 14) + '…' + h.slice(-6); }

Page({
  data: {
    event: null,
    consensus: null,
    members: [],
    chain: [],
    rootHash: '',
    rootShort: ''
  },
  onLoad: function (options) {
    var ev = model.getEventById(options.id);
    if (!ev) {
      wx.showToast({ title: '事件不存在', icon: 'none' });
      return;
    }
    var consensus = model.computeConsensus(ev);
    var chainInfo = model.computeChain(ev);
    var members = ev.participants.map(function (p) {
      var cv = model.computeMemberCV(p);
      return {
        name: p.name,
        city: p.city,
        role: p.role,
        action: p.action,
        cv: cv.cv,
        ncv: cv.ncv,
        net: cv.net,
        isNeg: p.delta < 0
      };
    });
    var chain = chainInfo.chain.map(function (r) {
      return {
        seq: r.seq,
        actor: r.actor,
        role: r.role,
        action: r.action,
        delta: r.delta,
        prevShort: short(r.prevHash),
        hashShort: short(r.hash)
      };
    });
    this.setData({
      event: {
        title: ev.title, type: ev.type, date: ev.date,
        summary: ev.summary, statusLabel: STATUS_LABEL[ev.status] || ev.status
      },
      consensus: consensus,
      members: members,
      chain: chain,
      rootHash: chainInfo.rootHash,
      rootShort: short(chainInfo.rootHash)
    });
    wx.setNavigationBarTitle({ title: '验证团' });
  }
});
