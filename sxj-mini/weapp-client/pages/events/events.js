const app = getApp();
const store = require('../../utils/store');

Page({
  data: {
    events: [],
    filter: 'all',
    types: app.globalData.types,
    statuses: app.globalData.statuses
  },

  onShow() {
    this.loadData();
  },

  loadData() {
    const sortTop = (list) => {
      const arr = list.map(e => this.enrich(e));
      arr.sort((a, b) => (a.id === 'evt_007' ? -1 : (b.id === 'evt_007' ? 1 : 0)));
      return arr;
    };
    this.setData({ events: sortTop(store.getEventsSync()) });
    store.refresh().then(() => {
      this.setData({ events: sortTop(store.getEventsSync()) });
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

  onFilterChange(e) {
    this.setData({ filter: e.currentTarget.dataset.type });
  },

  goDetail(e) {
    const id = e.currentTarget.dataset.id;
    wx.navigateTo({ url: '/pages/eventDetail/eventDetail?id=' + id });
  },

  goAdd() {
    wx.navigateTo({ url: '/pages/addEvent/addEvent' });
  }
});
