const store = require('../../utils/store');

Page({
  data: {
    verifiers: [],
    form: { name: '', role: '', contact: '', weight: '1.0' }
  },

  onShow() {
    this.loadData();
  },

  loadData() {
    const verifiers = store.getVerifiersSync();
    this.setData({ verifiers });
    store.refresh().then(() => {
      this.setData({ verifiers: store.getVerifiersSync() });
    });
  },

  onNameInput(e) { this.setData({ 'form.name': e.detail.value }); },
  onRoleInput(e) { this.setData({ 'form.role': e.detail.value }); },
  onContactInput(e) { this.setData({ 'form.contact': e.detail.value }); },
  onWeightInput(e) { this.setData({ 'form.weight': e.detail.value }); },

  async addVerifier() {
    const { form } = this.data;
    if (!form.name.trim()) {
      wx.showToast({ title: '请填写姓名', icon: 'none' });
      return;
    }
    const weight = parseFloat(form.weight) || 1.0;
    await store.saveVerifier({
      id: 'ver_' + Date.now(),
      name: form.name.trim(),
      role: form.role.trim() || '验证人',
      contact: form.contact.trim(),
      weight: weight,
      createdAt: new Date().toISOString()
    });
    this.setData({
      verifiers: store.getVerifiersSync(),
      form: { name: '', role: '', contact: '', weight: '1.0' }
    });
    wx.showToast({ title: '已添加', icon: 'success' });
  },

  removeVerifier(e) {
    const id = e.currentTarget.dataset.id;
    wx.showModal({
      title: '确认移除',
      content: '移除后该验证人不再参与新事件验证',
      success: async (res) => {
        if (res.confirm) {
          await store.removeVerifier(id);
          this.setData({ verifiers: store.getVerifiersSync() });
        }
      }
    });
  }
});
