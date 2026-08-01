const store = require('../../utils/store.js');

Page({
  data: { ranking: [] },
  onShow() { this.setData({ ranking: store.getRanking() }); }
});
