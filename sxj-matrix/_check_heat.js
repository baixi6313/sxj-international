const fs = require('fs');
const SXJ = require('./data.js');

// 1) 抽出 heat.html 内联脚本做语法解析
const html = fs.readFileSync('heat.html', 'utf8');
const m = html.match(/<script>\n([\s\S]*?)<\/script>/);
if (!m) { console.log('!! 未找到内联脚本'); process.exit(1); }
try {
  new Function('SXJ', 'document', 'location', 'setInterval', 'clearInterval', m[1]);
  console.log('OK  heat.html 内联脚本语法通过');
} catch (e) {
  console.log('ERR 语法错误:', e.message); process.exit(1);
}

// 2) 标签平衡粗检
const oD = (html.match(/<div\b/g) || []).length, cD = (html.match(/<\/div>/g) || []).length;
const oB = (html.match(/<button\b/g) || []).length, cB = (html.match(/<\/button>/g) || []).length;
console.log('    div  ' + oD + ' / ' + cD + (oD === cD ? '  OK' : '  (含JS模板串,人工判读)'));
console.log('    button ' + oB + ' / ' + cB + (oB === cB ? '  OK' : '  (含JS模板串,人工判读)'));

function dens(x, y, o) { return SXJ.cellDensity(x, y, o || {}); }
const f = (v, n) => (v === null || v === undefined) ? '-' : v.toFixed(n);

console.log('\n--- 全量切片 (j=all, z=all) 九格读数 ---');
SXJ.CELLS.forEach(c => {
  const d = dens(c.x, c.y);
  const H = (d.rhoAvg === null) ? null : d.count * d.rhoAvg;
  console.log('  ' + (c.x + ':' + c.y).padEnd(14) +
    ' n=' + d.count + ' 量测=' + d.measured +
    ' rhoAvg=' + f(d.rhoAvg, 4) + ' rhoMax=' + f(d.rhoMax, 4) +
    ' H=' + f(H, 2) + ' [' + SXJ.regionColor(d.region).label + ']' +
    (c.status === 'hold' ? ' 挂起' : ''));
});

console.log('\n--- 切片 j=CN ---');
SXJ.CELLS.forEach(c => { const d = dens(c.x, c.y, { j: 'CN' }); if (d.count) console.log('  ' + c.x + ':' + c.y + ' n=' + d.count + ' rhoAvg=' + f(d.rhoAvg, 4)); });
console.log('--- 切片 j=INTL ---');
SXJ.CELLS.forEach(c => { const d = dens(c.x, c.y, { j: 'INTL' }); if (d.count) console.log('  ' + c.x + ':' + c.y + ' n=' + d.count + ' rhoAvg=' + f(d.rhoAvg, 4)); });

console.log('\n--- 时间回放 (累计 落点/已量测) ---');
const s = SXJ.stats();
let line = '  ';
for (let y = s.minYear; y <= s.maxYear; y++) {
  const all = SXJ.project({ untilYear: y, includePlaceholder: false });
  if (!all.length) continue;
  const mm = all.filter(e => typeof e.rho === 'number');
  line += y + ':n' + all.length + '/m' + mm.length + '  ';
}
console.log(line);

const measured = SXJ.EVENTS.filter(e => !e.placeholder && typeof e.rho === 'number');
console.log('\nrho 轴点位: ' + measured.map(e => e.id + '=' + e.rho).join(', '));
console.log('跨门槛(>=' + SXJ.META.rhoMin + '): ' + measured.filter(e => e.rho >= SXJ.META.rhoMin).length);
console.log('占格: ' + SXJ.CELLS.filter(c => dens(c.x, c.y).count > 0).length + ' / 9');

// 3) 四页文件互链完整性
console.log('\n--- 四视图互链检查 ---');
['index.html', 'axis.html', 'wiki.html', 'map.html', 'heat.html'].forEach(fn => {
  const t = fs.readFileSync(fn, 'utf8');
  const need = ['index.html', 'axis.html', 'wiki.html', 'map.html', 'heat.html'].filter(x => x !== fn);
  const miss = need.filter(x => t.indexOf(x) === -1);
  const hasData = t.indexOf('data.js') > -1 || fn === 'index.html';
  console.log('  ' + fn.padEnd(12) + (miss.length ? ' 缺链: ' + miss.join(',') : ' 互链完整') + (hasData ? ' | data.js OK' : ' | !! 未引 data.js'));
});
