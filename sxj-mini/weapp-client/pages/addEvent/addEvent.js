const app = getApp();
const store = require('../../utils/store');

Page({
  data: {
    form: {
      title: '',
      typeIndex: 0,
      date: '',
      location: '',
      description: '',
      evidence: '',
      recorder: ''
    },
    types: app.globalData.types,
    today: ''
  },

  onLoad() {
    const today = new Date().toISOString().split('T')[0];
    this.setData({ 'form.date': today, today });
  },

  onTitleInput(e) { this.setData({ 'form.title': e.detail.value }); },
  onLocationInput(e) { this.setData({ 'form.location': e.detail.value }); },
  onDescInput(e) { this.setData({ 'form.description': e.detail.value }); },
  onEvidenceInput(e) { this.setData({ 'form.evidence': e.detail.value }); },
  onRecorderInput(e) { this.setData({ 'form.recorder': e.detail.value }); },

  onTypeChange(e) {
    this.setData({ 'form.typeIndex': parseInt(e.detail.value) });
  },

  onDateChange(e) {
    this.setData({ 'form.date': e.detail.value });
  },

  async submit() {
    const { form, types } = this.data;
    if (!form.title.trim()) {
      wx.showToast({ title: '请填写标题', icon: 'none' });
      return;
    }
    if (!form.description.trim()) {
      wx.showToast({ title: '请填写描述', icon: 'none' });
      return;
    }

    const typeKey = types[form.typeIndex].key;
    const newEvent = {
      id: 'evt_' + Date.now(),
      title: form.title.trim(),
      type: typeKey,
      date: form.date,
      location: form.location.trim() || '未填写',
      description: form.description.trim(),
      evidence: form.evidence.trim() || '暂无',
      recorder: form.recorder.trim() || '匿名',
      status: 'recording',
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
      verifyGroup: []
    };

    await store.createEvent(newEvent);

    wx.showToast({ title: '已记录', icon: 'success' });
    setTimeout(() => {
      wx.navigateBack();
    }, 800);
  }
});
