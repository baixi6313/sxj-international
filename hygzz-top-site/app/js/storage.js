// 存储桥：优先用原生 SxjBridge（SharedPreferences），否则退化为 localStorage。
window.Store = (function () {
  var KEY = 'sxj_events';
  var hasBridge = (typeof SxjBridge !== 'undefined');
  function save(key, val) {
    var s = (typeof val === 'string') ? val : JSON.stringify(val);
    if (hasBridge) { SxjBridge.save(key, s); } else { localStorage.setItem(key, s); }
  }
  function load(key) {
    return hasBridge ? SxjBridge.load(key) : localStorage.getItem(key);
  }
  function remove(key) {
    if (hasBridge) { SxjBridge.remove(key); } else { localStorage.removeItem(key); }
  }
  return {
    getEvents: function () {
      var s = load(KEY);
      if (!s) return [];
      try { return JSON.parse(s); } catch (e) { return []; }
    },
    setEvents: function (arr) { save(KEY, arr); },
    clear: function () { remove(KEY); }
  };
})();
