const store = require('../../utils/store.js');

Page({
  data: {
    profile: { name: '', age: '' },
    avatar: '我',
    ageText: '未设置年龄',
    target: 2000,
    todayTotal: 0,
    percent: 0,
    records: [],
    mlInput: '',
    assistantInput: '',
    targetInput: '我',
    assistMlInput: ''
  },

  onShow() { this.refresh(); },

  refresh() {
    var p = store.getProfile();
    var target = store.getTarget(p.age);
    var total = store.getTodayTotal();
    var pct = target > 0 ? Math.min(100, Math.round(total / target * 100)) : 0;
    var recs = store.getSelfRecords().slice(-8).reverse();
    this.setData({
      profile: p,
      avatar: p.name ? p.name.charAt(0) : '我',
      ageText: (p.age && !isNaN(p.age)) ? (Number(p.age) >= 60 ? '60岁以上' : p.age + '岁') : '未设置年龄',
      target: target,
      todayTotal: total,
      percent: pct,
      records: recs
    });
  },

  editProfile() { this.promptProfile(); },

  promptProfile() {
    var that = this;
    wx.showModal({
      title: '设置姓名', editable: true, placeholderText: '如 老王',
      success(res) {
        if (!res.confirm) return;
        var name = (res.content || '').trim();
        wx.showModal({
          title: '设置年龄', editable: true, placeholderText: '如 65（60岁以上目标2500ml）',
          success(res2) {
            if (!res2.confirm) return;
            var age = parseInt(res2.content);
            if (isNaN(age)) age = '';
            store.saveProfile({ name: name, age: age });
            that.refresh();
          }
        });
      }
    });
  },

  onMlInput(e) { this.setData({ mlInput: e.detail.value }); },
  onAssistantInput(e) { this.setData({ assistantInput: e.detail.value }); },
  onTargetInput(e) { this.setData({ targetInput: e.detail.value }); },
  onAssistMlInput(e) { this.setData({ assistMlInput: e.detail.value }); },

  quickAdd(e) { this.doAdd(parseInt(e.currentTarget.dataset.ml)); },
  addSelf() { this.doAdd(parseInt(this.data.mlInput) || 0); },

  doAdd(ml) {
    if (!ml || ml <= 0) { wx.showToast({ title: '请输入有效水量', icon: 'none' }); return; }
    store.addSelfRecord(ml);
    this.setData({ mlInput: '' });
    wx.showToast({ title: '已记录', icon: 'success' });
    this.refresh();
  },

  addAssist() {
    var name = (this.data.assistantInput || '').trim();
    var target = (this.data.targetInput || '').trim() || '我';
    var ml = parseInt(this.data.assistMlInput) || 0;
    if (!name) { wx.showToast({ title: '请输入协助人姓名', icon: 'none' }); return; }
    if (!ml || ml <= 0) { wx.showToast({ title: '请输入有效水量', icon: 'none' }); return; }
    store.addAssistClaim(name, target, ml);
    this.setData({ assistantInput: '', targetInput: '我', assistMlInput: '' });
    wx.showToast({ title: '已提交，请去确认', icon: 'none' });
    this.refresh();
  }
});
