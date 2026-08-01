// 事现鉴 App 主体逻辑：事件簿（主功能）+ 理论 + 我的。纯前端，数据经 SxjBridge 持久化。
(function () {
  var TYPES = [
    { key: 'common', label: '共济值', desc: '公众知情权 / 基本事实' },
    { key: 'contribution', label: '贡献值', desc: '谁创造了什么 / 该得什么' },
    { key: 'negative', label: '负贡献', desc: '损害 / 追责' }
  ];
  var STATUSES = [
    { key: 'recording', label: '记录中', color: '#999' },
    { key: 'verifying', label: '验证中', color: '#e6a23c' },
    { key: 'verified', label: '已验证', color: '#67c23a' },
    { key: 'accounted', label: '已归责', color: '#a23b32' },
    { key: 'resolved', label: '已解决', color: '#409eff' },
    { key: 'invalid', label: '未成立', color: '#909399' },
    { key: 'tracking', label: '追踪中', color: '#a855f7' }
  ];
  var TYPE_LABEL = {}, STATUS_MAP = {};
  TYPES.forEach(function (t) { TYPE_LABEL[t.key] = t.label; });
  STATUSES.forEach(function (s) { STATUS_MAP[s.key] = s; });

  var state = { tab: 'events', filter: 'all', events: [] };
  var view = document.getElementById('view');
  var modalRoot = document.getElementById('modal-root');

  function esc(s) {
    return String(s == null ? '' : s)
      .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;').replace(/'/g, '&#39;');
  }
  function chainHash(e) {
    var canon = [e.id, e.type, e.title, e.date, e.location, e.description, e.status].join('|');
    return sha256Hex(canon);
  }
  function load() {
    var ev = Store.getEvents();
    if (!ev || !ev.length) {
      ev = SEED_EVENTS.map(function (e) { return Object.assign({ createdAt: '2026-07-30T11:30:00Z', updatedAt: '2026-07-30T11:30:00Z' }, e); });
      Store.setEvents(ev);
    }
    state.events = ev;
  }
  function save() { Store.setEvents(state.events); }

  function render() {
    if (state.tab === 'events') renderEvents();
    else if (state.tab === 'theory') renderTheory();
    else renderMine();
  }

  function renderEvents() {
    var list = state.events.slice();
    if (state.filter !== 'all') list = list.filter(function (e) { return e.type === state.filter; });
    var html = '<div class="sec-title">事现记录 · 共 ' + state.events.length + ' 条</div>';
    html += '<div class="chips">';
    html += '<span class="chip ' + (state.filter === 'all' ? 'active' : '') + '" data-f="all">全部</span>';
    TYPES.forEach(function (t) {
      html += '<span class="chip ' + (state.filter === t.key ? 'active' : '') + '" data-f="' + t.key + '">' + t.label + '</span>';
    });
    html += '</div>';
    if (!list.length) {
      html += '<div class="empty">暂无该类事现，点右下角 ＋ 新增一条。</div>';
    }
    list.forEach(function (e) {
      var st = STATUS_MAP[e.status] || { label: e.status, color: '#999' };
      var tl = TYPE_LABEL[e.type] || e.type;
      html += '<div class="card" data-id="' + esc(e.id) + '">'
        + '<h3>' + esc(e.title) + '</h3>'
        + '<div class="meta">'
        + '<span class="pill ' + e.type + '">' + tl + '</span>'
        + '<span class="st" style="color:' + st.color + ';border-color:' + st.color + '">' + st.label + '</span>'
        + (e.location ? '<span class="loc">' + esc(e.location) + '</span>' : '')
        + (e.date ? '<span class="loc">' + esc(e.date) + '</span>' : '')
        + '</div>'
        + (e.description ? '<div class="desc">' + esc(e.description).slice(0, 60) + (e.description.length > 60 ? '…' : '') + '</div>' : '')
        + '</div>';
    });
    view.innerHTML = html;
    view.querySelectorAll('.chip').forEach(function (c) {
      c.onclick = function () { state.filter = c.getAttribute('data-f'); renderEvents(); };
    });
    view.querySelectorAll('.card').forEach(function (c) {
      c.onclick = function () { openDetail(c.getAttribute('data-id')); };
    });
  }

  function renderTheory() {
    var pages = [
      { f: 'theory/co_creation.html', t: '共创论总论' },
      { f: 'theory/whitepaper.html', t: '白皮书' },
      { f: 'theory/concept_tree.html', t: '概念树' },
      { f: 'theory/knowledge_tree.html', t: '知识树' },
      { f: 'theory/events.html', t: '事件簿（网页版案例库）' }
    ];
    var html = '<div class="sec-title">理论阅读</div><div class="theory-list">';
    pages.forEach(function (p) {
      html += '<div class="card"><div><div style="font-weight:700">' + p.t + '</div>'
        + '<div class="loc">本地离线可读</div></div>'
        + '<a href="' + p.f + '">打开 ›</a></div>';
    });
    html += '</div>';
    view.innerHTML = html;
  }

  function renderMine() {
    var added = state.events.filter(function (e) { return e.id.indexOf('local_') === 0; }).length;
    var html = ''
      + '<div class="sec-title">我的</div>'
      + '<div class="info"><b>事现鉴</b> · 共创论公共事实验证工具<br>版本 1.0.2 · 正式版 · 数据更新 2026-08-01</div>'
      + '<div class="info">本地事现总数：<b>' + state.events.length + '</b> 条<br>其中你新增：<b>' + added + '</b> 条</div>'
      + '<div class="info">数据保存在本机（SharedPreferences / 浏览器本地）。本 App 为离线工具，未联网上传。</div>'
      + '<div class="row" style="margin-top:6px">'
      + '<button class="btn ghost" id="btn-export">导出全部</button>'
      + '<button class="btn ghost" id="btn-clear">清空我的新增</button>'
      + '</div>'
      + '<div class="info" style="margin-top:12px">验证权威：仅「事现鉴 + Gzz」。<br>治理消失条件：全球共济值 ≥ 50%。</div>';
    view.innerHTML = html;
    document.getElementById('btn-export').onclick = function () {
      var blob = 'data:application/json;charset=utf-8,' + encodeURIComponent(JSON.stringify(state.events, null, 2));
      var a = document.createElement('a'); a.href = blob; a.download = 'sxj_events.json'; a.click();
    };
    document.getElementById('btn-clear').onclick = function () {
      if (!confirm('确定清空你新增的事现？（预置 5 条种子保留）')) return;
      state.events = state.events.filter(function (e) { return e.id.indexOf('local_') !== 0; });
      save(); render();
    };
  }

  function openDetail(id) {
    var e = state.events.filter(function (x) { return x.id === id; })[0];
    if (!e) return;
    var st = STATUS_MAP[e.status] || { label: e.status, color: '#999' };
    var tl = TYPE_LABEL[e.type] || e.type;
    var html = '<div class="mask" data-close="1"><div class="sheet" onclick="event.stopPropagation()">'
      + '<button class="close" data-close="1">×</button>'
      + '<h2>' + esc(e.title) + '</h2>'
      + '<div class="meta"><span class="pill ' + e.type + '">' + tl + '</span>'
      + '<span class="st" style="color:' + st.color + ';border-color:' + st.color + '">' + st.label + '</span></div>'
      + (e.location || e.date ? '<div class="loc" style="margin-top:6px">' + esc(e.location) + (e.date ? ' · ' + esc(e.date) : '') + '</div>' : '')
      + (e.description ? '<p class="desc" style="margin-top:10px">' + esc(e.description) + '</p>' : '')
      + (e.evidence ? '<div class="field" style="margin-top:10px"><label>证据 / 来源</label><div class="desc">' + esc(e.evidence) + '</div></div>' : '')
      + '<div class="field"><label>SHA-256 哈希指纹（可独立复算验证）</label><div class="hash">' + chainHash(e) + '</div></div>'
      + '<div class="info" style="margin-top:10px">共识状态：当前为单机演示，验证团共识需多人交叉核验后写入。本链仅为内容指纹，证明「该记录未被篡改」。</div>'
      + '</div></div>';
    modalRoot.innerHTML = html;
    modalRoot.querySelectorAll('[data-close]').forEach(function (el) {
      el.onclick = function () { modalRoot.innerHTML = ''; };
    });
  }

  function openAdd() {
    var typeOpts = TYPES.map(function (t) { return '<option value="' + t.key + '">' + t.label + '</option>'; }).join('');
    var html = '<div class="mask" data-close="1"><div class="sheet" onclick="event.stopPropagation()">'
      + '<button class="close" data-close="1">×</button>'
      + '<h2>新增事现</h2>'
      + '<div class="field"><label>标题</label><input id="a-title" placeholder="一句话描述事现"></div>'
      + '<div class="field"><label>类型</label><select id="a-type">' + typeOpts + '</select></div>'
      + '<div class="field"><label>地点</label><input id="a-loc" placeholder="如：西安 / 网络"></div>'
      + '<div class="field"><label>日期</label><input id="a-date" placeholder="2026-07-30"></div>'
      + '<div class="field"><label>经过 / 描述</label><textarea id="a-desc" placeholder="记录事实经过"></textarea></div>'
      + '<div class="field"><label>证据 / 来源</label><input id="a-ev" placeholder="链接、截图、文件等"></div>'
      + '<button class="btn" id="a-save">保存事现</button>'
      + '</div></div>';
    modalRoot.innerHTML = html;
    modalRoot.querySelectorAll('[data-close]').forEach(function (el) {
      el.onclick = function () { modalRoot.innerHTML = ''; };
    });
    document.getElementById('a-save').onclick = function () {
      var title = document.getElementById('a-title').value.trim();
      if (!title) { alert('请填写标题'); return; }
      var now = new Date().toISOString();
      var e = {
        id: 'local_' + Date.now(),
        title: title,
        type: document.getElementById('a-type').value,
        date: document.getElementById('a-date').value.trim(),
        location: document.getElementById('a-loc').value.trim(),
        description: document.getElementById('a-desc').value.trim(),
        evidence: document.getElementById('a-ev').value.trim(),
        recorder: '本机用户',
        status: 'recording',
        createdAt: now, updatedAt: now
      };
      state.events.unshift(e);
      save();
      modalRoot.innerHTML = '';
      render();
    };
  }

  // 底部 tab + FAB
  document.querySelectorAll('.tabbar button').forEach(function (b) {
    b.onclick = function () {
      document.querySelectorAll('.tabbar button').forEach(function (x) { x.classList.remove('active'); });
      b.classList.add('active');
      state.tab = b.getAttribute('data-tab');
      render();
    };
  });
  document.getElementById('fab').onclick = openAdd;

  load();
  render();
})();
