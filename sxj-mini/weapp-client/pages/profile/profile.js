Page({
  data: {
    stats: { events: 0, verifiers: 0 }
  },

  onShow() {
    const store = require('../../utils/store');
    const events = store.getEventsSync();
    const verifiers = store.getVerifiersSync();
    this.setData({
      stats: { events: events.length, verifiers: verifiers.length }
    });
  },

  clearData() {
    wx.showModal({
      title: '清空所有数据',
      content: '这会删除本机记录的所有事现和验证人，不可恢复。',
      confirmColor: '#a23b32',
      success: (res) => {
        if (res.confirm) {
          wx.removeStorageSync('sxj_events');
          wx.removeStorageSync('sxj_verifiers');
          wx.showToast({ title: '已清空', icon: 'success' });
          this.setData({ stats: { events: 0, verifiers: 0 } });
        }
      }
    });
  },

  copyLink(e) {
    const link = (e && e.currentTarget && e.currentTarget.dataset && e.currentTarget.dataset.link) || 'https://hygzz.top';
    wx.setClipboardData({
      data: link,
      success: () => wx.showToast({ title: '链接已复制', icon: 'success' })
    });
  },

  goTheory() {
    wx.navigateTo({ url: '/pages/theory/theory' });
  }
});
