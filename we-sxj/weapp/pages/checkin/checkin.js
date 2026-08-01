const store = require('../../utils/store.js');

Page({
  data: {
    checkedToday: false,
    streak: 0,
    total: 0,
    credentials: [],
    todayTotal: 0,
    target: 2000,
    waterPct: 0
  },

  onShow() { this.refresh(); },

  refresh() {
    var st = store.checkinState();
    var p = store.getProfile();
    var target = store.getTarget(p.age);
    var today = store.getTodayTotal();
    var pct = target > 0 ? Math.min(100, Math.round(today / target * 100)) : 0;
    this.setData({
      checkedToday: st.checkedToday,
      streak: st.streak,
      total: st.total,
      credentials: st.credentials.slice().reverse(),
      todayTotal: today,
      target: target,
      waterPct: pct
    });
  },

  doCheckin() {
    var r = store.doCheckin();
    if (r.already) {
      wx.showToast({ title: '今日已签到', icon: 'none' });
    } else {
      wx.showToast({ title: '签到成功 · 连续 ' + r.state.streak + ' 天', icon: 'success' });
      if (r.newCredential) {
        var cred = r.newCredential;
        setTimeout(function () {
          wx.showModal({ title: '获得共济值凭证', content: cred.label, showCancel: false });
        }, 700);
      }
    }
    this.refresh();
  },

  goRecord() { wx.switchTab({ url: '/pages/record/record' }); },
  goAbout() { wx.navigateTo({ url: '/pages/about/about' }); }
});
