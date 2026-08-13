const SXJ=require('./data.js');
console.log('事件总数:', SXJ.EVENTS.length);
const counts={};
SXJ.EVENTS.forEach(e=>{
  const k=e.x+':'+e.y;
  counts[k]=counts[k]||{n:0,measured:0,placeholder:0};
  counts[k].n++;
  if(e.placeholder) counts[k].placeholder++;
  if(typeof e.rho==='number') counts[k].measured++;
});
console.log('各格占点:');
for(const k in counts){const c=counts[k];console.log('  '+k+'  n='+c.n+'  量测='+c.measured+'  占位='+c.placeholder);}
console.log('\n事件清单:');
SXJ.EVENTS.forEach(e=>console.log('  '+e.id+'  '+e.x+':'+e.y+'  j='+e.j+'  '+(e.placeholder?'[占位]':'')+'  rho='+(typeof e.rho==='number'?e.rho:'—')+'  '+e.title));
