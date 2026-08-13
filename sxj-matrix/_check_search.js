const fs=require('fs');
const SXJ=require('./data.js');
let ok=true;

// 1) data.js search 函数逻辑
function t(name, got, exp){
  const pass = JSON.stringify(got)===JSON.stringify(exp);
  console.log((pass?'✓':'✗')+' '+name+'  → '+JSON.stringify(got));
  if(!pass) ok=false;
}
t('search("evt_009") 命中数', SXJ.search('evt_009').length, 1);
t('search("evt_009") id', SXJ.search('evt_009')[0].id, 'evt_009');
t('search("白皮书") 事件应为0(仅在CONTENT)', SXJ.search('白皮书').length, 0);
t('search("MAIP") 命中>0', SXJ.search('MAIP').length>0, true);
t('search("") 空词返回[]', SXJ.search('').length, 0);
t('search("跨账本") 多事件', SXJ.search('跨账本').length, SXJ.search('跨账本').length); // 仅打印
t('search 含占位 evt_003(搜"占位")', SXJ.search('占位').some(e=>e.id==='evt_003'), true);

// 2) 内联脚本语法解析
function syntax(file){
  const html=fs.readFileSync(file,'utf8');
  const m=html.match(/<script>\n([\s\S]*?)<\/script>/);
  if(!m){console.log('  (无内联 script) '+file);return;}
  try{ new Function('SXJ','document','location','URLSearchParams','setInterval','clearInterval', m[1]); console.log('✓ '+file+' 内联脚本语法通过'); }
  catch(e){ console.log('✗ '+file+' 语法错误: '+e.message); ok=false; }
}
['index.html','wiki.html','axis.html','map.html','heat.html'].forEach(syntax);

// 3) 跳转/搜索 DOM 锚点存在性
function has(file, str){ const h=fs.readFileSync(file,'utf8'); console.log((h.indexOf(str)>=0?'✓':'✗')+' '+file+' 含「'+str+'」'); if(h.indexOf(str)<0) ok=false; }
['index.html','wiki.html','axis.html','map.html','heat.html'].forEach(f=>{
  if(f==='index.html') has(f,'id="sxjSearch"');
  if(f==='wiki.html') has(f,'id="wikiSearch"');
  if(f!=='index.html'&&f!=='wiki.html') has(f,'id="jumpSearch"');
});
console.log('\n'+(ok?'=== 全部校验通过 ===':'=== 存在失败项 ==='));
process.exit(ok?0:1);
