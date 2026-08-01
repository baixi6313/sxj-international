const store = require('../../utils/store');

const VERDICTS = [
  { key: 'support', label: '支持' },
  { key: 'oppose', label: '反对' },
  { key: 'doubt', label: '存疑' }
];

Page({
  data: {
    eventId: '',
    verdicts: VERDICTS,
    verdictIndex: 0,
    content: '',
    author: ''
  },

  onLoad(options) {
    this.setData({ eventId: options.id || '' });
  },

  onVerdictChange(e) {
    this.setData({ verdictIndex: parseInt(e.detail.value) });
  },
  onContentInput(e) { this.setData({ content: e.detail.value }); },
  onAuthorInput(e) { this.setData({ author: e.detail.value }); },

  async submit() {
    const { eventId, verdicts, verdictIndex, content, author } = this.data;
    if (!content.trim()) {
      wx.showToast({ title: '请填写理由', icon: 'none' });
      return;
    }
    await store.createVerification({
      eventId,
      verdict: verdicts[verdictIndex].key,
      content: content.trim(),
      author: author.trim() || '匿名',
      createdAt: new Date().toISOString()
    });
    store.callConsensus(eventId); // 第三层共识自动重算
    wx.showToast({ title: '已提交', icon: 'success' });
    setTimeout(() => wx.navigateBack(), 800);
  }
});
