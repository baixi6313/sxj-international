Page({
  data: {},
  copyWebUrl() {
    wx.setClipboardData({
      data: 'https://bfda2106.sxj-mini.pages.dev',
      success() {
        wx.showToast({ title: '链接已复制，请在浏览器打开', icon: 'none', duration: 2500 });
      }
    });
  }
});
