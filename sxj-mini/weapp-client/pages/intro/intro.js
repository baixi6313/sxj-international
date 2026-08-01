Page({
  start() {
    // 标记已看过引导，避免下次启动重复弹出
    wx.setStorageSync('sxj_intro_seen', true);
    // 返回主页（引导页是从主页 navigateTo 进来的，index 在栈底）
    wx.navigateBack({
      fail: () => {
        wx.reLaunch({ url: '/pages/index/index' });
      }
    });
  }
});
