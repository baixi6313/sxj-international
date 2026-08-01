const store = require('../../utils/store');

const KINDS = [
  { key: 'evidence', label: '证据' },
  { key: 'clue', label: '线索' },
  { key: 'progress', label: '进展' }
];

Page({
  data: {
    eventId: '',
    kinds: KINDS,
    kindIndex: 0,
    content: '',
    author: ''
  },

  onLoad(options) {
    this.setData({ eventId: options.id || '' });
  },

  onKindChange(e) {
    this.setData({ kindIndex: parseInt(e.detail.value) });
  },
  onContentInput(e) { this.setData({ content: e.detail.value }); },
  onAuthorInput(e) { this.setData({ author: e.detail.value }); },

  async submit() {
    const { eventId, kinds, kindIndex, content, author } = this.data;
    if (!content.trim()) {
      wx.showToast({ title: '请填写内容', icon: 'none' });
      return;
    }
    await store.createEvidence({
      eventId,
      kind: kinds[kindIndex].key,
      content: content.trim(),
      author: author.trim() || '匿名',
      createdAt: new Date().toISOString()
    });
    store.callConsensus(eventId); // 第三层共识自动重算
    wx.showToast({ title: '已追加', icon: 'success' });
    setTimeout(() => wx.navigateBack(), 800);
  }
});
