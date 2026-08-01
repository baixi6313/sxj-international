const app = getApp();
const store = require('../../utils/store');

Page({
  data: {
    stats: { events: 0, verifiers: 0 },
    recentEvents: []
  },

  onShow() {
    this.loadData();
    // 首次启动自动弹出「30秒了解」引导页（看过一次后不再弹）
    if (!wx.getStorageSync('sxj_intro_seen')) {
      wx.navigateTo({ url: '/pages/intro/intro' });
    }
  },

  loadData() {
    const sortTop = (list) => {
      const arr = list.map(e => this.enrich(e));
      // 彬县负贡献原型始终置顶展示
      arr.sort((a, b) => (a.id === 'evt_007' ? -1 : (b.id === 'evt_007' ? 1 : 0)));
      return arr;
    };
    const events = sortTop(store.getEventsSync());
    const verifiers = store.getVerifiersSync();
    this.setData({
      stats: { events: events.length, verifiers: verifiers.length },
      recentEvents: events.slice(0, 3)
    });
    // 异步从云刷新（无云环境时静默跳过）
    store.refresh().then(() => {
      const ev2 = sortTop(store.getEventsSync());
      const ve2 = store.getVerifiersSync();
      this.setData({
        stats: { events: ev2.length, verifiers: ve2.length },
        recentEvents: ev2.slice(0, 3)
      });
    });
  },

  enrich(e) {
    const t = app.globalData.types.find(x => x.key === e.type);
    const s = app.globalData.statuses.find(x => x.key === e.status);
    const typeColor = { common: '#2F6FED', contribution: '#D99A2B', negative: '#D85A30' }[e.type] || '#999';
    return {
      ...e,
      typeLabel: t ? t.label : e.type,
      statusLabel: s ? s.label : e.status,
      statusColor: s ? s.color : '#999',
      typeColor
    };
  },

  goAddEvent() {
    wx.navigateTo({ url: '/pages/addEvent/addEvent' });
  },

  goVerifyGroup() {
    wx.navigateTo({ url: '/pages/verifyGroup/verifyGroup' });
  },

  goEvents() {
    wx.navigateTo({ url: '/pages/events/events' });
  },

  goProfile() {
    wx.navigateTo({ url: '/pages/profile/profile' });
  },

  goTheory() {
    wx.navigateTo({ url: '/pages/theory/theory' });
  },

  goIntro() {
    wx.navigateTo({ url: '/pages/intro/intro' });
  },

  goDetail(e) {
    const id = e.currentTarget.dataset.id;
    wx.navigateTo({ url: '/pages/eventDetail/eventDetail?id=' + id });
  }
});
