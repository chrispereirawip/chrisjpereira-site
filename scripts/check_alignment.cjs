// alignment check: the two edition cards must line up row by row
// Run before every push of shop.py changes: python3 -m http.server 8766 in the repo, then node scripts/check_alignment.cjs (needs Playwright).
const { chromium } = require('/home/claude/.npm-global/lib/node_modules/playwright');
(async()=>{const b=await chromium.launch();
for (const [path,w] of [['/books/',1366],['/zh/books/',1366],['/books/',1100],['/books/',920]]) {
const p=await b.newPage({viewport:{width:w,height:900}});
await p.route('https://www.globalconnect.show/api/pay/**',r=>r.fulfill({json:{ok:true,books:[{id:'trust-zh',status:'sale',open:true,currency:'cny',price:6500,maxQty:10,shipping:[{id:'cn',en:'Mainland China',zh:'中国大陆',amount:1500}]},{id:'trust-en',status:'waitlist'}]}}));
await p.goto('http://localhost:8766'+path);await p.waitForTimeout(500);
const r=await p.evaluate(()=>{const g=(id,sel)=>{const e=document.querySelector('#'+id+' '+sel);return e?Math.round(e.getBoundingClientRect().top):null};
 return ['.vis','h2','.emeta','.rA','.rB','.rB label','.go','.go .btn'].map(s=>[s,g('chinese',s),g('english',s)]).concat([['card bottom',Math.round(document.querySelector('#chinese').getBoundingClientRect().bottom),Math.round(document.querySelector('#english').getBoundingClientRect().bottom)]])});
const bad=r.filter(x=>x[1]!==x[2]);console.log(path,w,bad.length?'MISALIGNED '+JSON.stringify(bad):'aligned ('+r.length+' checks)');}
await b.close();})();
