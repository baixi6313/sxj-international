const store = require('../../utils/store.js');

Page({
  data: { pending: [] },
  onShow() { this.refresh(); },
  refresh() {
    this.setData({ pending: store.getPending().slice().reverse() });
  },
  confirm(e) {
    var id = e.currentTarget.dataset.id;
    store.confirmAssist(id);
    wx.showToast({ title: '已确认·双向凭证生成', icon: 'none' });
    this.refresh();
  },
  reject(e) {
    var id = e.currentTarget.dataset.id;
    store.rejectAssist(id);
    wx.showToast({ title: '已拒绝', icon: 'none' });
    this.refresh();
  }
});
