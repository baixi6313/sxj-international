const store = require('../../utils/store.js');

Page({
  data: {
    reasons: ['忘记了', '取水不便', '身体原因（如尿频/服药）', '水不好喝', '没时间', '其他'],
    selected: '',
    detail: '',
    feedback: [],
    todayTotal: 0,
    target: 2000
  },
  onShow() {
    var p = store.getProfile();
    this.setData({
      feedback: store.getFeedback().slice().reverse(),
      todayTotal: store.getTodayTotal(),
      target: store.getTarget(p.age)
    });
  },
  pick(e) { this.setData({ selected: e.currentTarget.dataset.r }); },
  onDetail(e) { this.setData({ detail: e.detail.value }); },
  submit() {
    if (!this.data.selected) { wx.showToast({ title: '请选择一个原因', icon: 'none' }); return; }
    store.addFeedback(this.data.selected, (this.data.detail || '').trim());
    this.setData({ selected: '', detail: '' });
    wx.showToast({ title: '已提交', icon: 'success' });
    this.onShow();
  }
});
