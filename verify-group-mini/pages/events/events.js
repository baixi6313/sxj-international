var model = require('../../utils/model.js');

var STATUS_LABEL = {
  pending: '待验证',
  reached: '已共识',
  disputed: '有争议',
  contested: '拉锯中'
};

Page({
  data: {
    filter: 'all',
    filters: [
      { key: 'all', label: '全部' },
      { key: '共济值', label: '共济值' },
      { key: '贡献值', label: '贡献值' },
      { key: '负贡献', label: '负贡献' }
    ],
    list: []
  },
  onLoad: function () {
    this.refresh('all');
  },
  onFilterChange: function (e) {
    this.refresh(e.currentTarget.dataset.type);
  },
  refresh: function (f) {
    var all = model.EVENTS.map(function (ev) {
      return {
        id: ev.id,
        title: ev.title,
        type: ev.type,
        date: ev.date,
        status: ev.status,
        statusLabel: STATUS_LABEL[ev.status] || ev.status,
        summary: ev.summary
      };
    });
    var list = f === 'all' ? all : all.filter(function (x) { return x.type === f; });
    this.setData({ filter: f, list: list });
  },
  openGroup: function (e) {
    var id = e.currentTarget.dataset.id;
    wx.navigateTo({ url: '/pages/group/group?id=' + id });
  }
});
