"""Book shop pages: /books/ (English) and /zh/books/ (Simplified Chinese). 2026-11-02.

Chris: "set up a page for people to buy my English and Chinese version books, and pay with Stripe", using the GCS Stripe account.
Redesigned the same evening after his review: the two editions sit side by side as equal cards, a real product photo instead of
the old skewed cover scan, full-width layout, and a clear "notify me" for the English edition.
The page is static; prices, shipping and checkout come from the GCS site's API (www.globalconnect.show/api/pay/books, see
gcs-site functions/lib/books.js), so a price change never needs a rebuild here. Run: python3 shop.py (build.py calls it too).
"""
import json
import os

API = "https://www.globalconnect.show/api/pay"
HERE = os.path.dirname(os.path.abspath(__file__))

T = {
    "en": {
        "lang": "en", "home": "/", "path": "/books/", "other": "/zh/books/", "other_label": "中文", "img": "/img/",
        "title": "Books by Chris Pereira | Trust 《信任》",
        "desc": "Order a signed copy of Trust 《信任》 by Chris Pereira (Chinese edition, Shenzhen Publishing House, 2026), posted within mainland China. The English edition is coming soon.",
        "nav": [("/#writing", "Writing"), ("/#media", "Commentary"), ("/#speaking", "Speaking"), ("/#training", "Training"), ("/books/", "Books"), ("/#about", "About")],
        "contact": "Contact", "label": "Books",
        "h1": "Trust <span class=\"zh\" lang=\"zh-Hans\">《信任》</span>",
        "sub": "The Golden Key to Chinese Enterprises' Globalization",
        "lede": "How Chinese companies earn trust in foreign markets, drawn from more than 20 years in China, from Huawei's global public affairs to the brands Chris advises today. The Chinese edition is out now, signed by the author. The English edition, rewritten for readers outside China, is coming soon.",
        "facts": [("Author", "Chris Pereira <span lang=\"zh-Hans\">彭家荣</span>"), ("Publisher", "Shenzhen Publishing House <span lang=\"zh-Hans\">深圳出版社</span>"), ("Published", "February 2026")],
        "zh_tag": "Available now", "zh_h": "Chinese edition", "zh_title": "<span lang=\"zh-Hans\"><span class=\"hang\">《</span>信任》</span>",
        "zh_meta": "Paperback · signed by the author · ships within mainland China",
        "qty": "Copies", "ded": "Dedication (optional)", "ded_ph": "e.g. To Anna", "name": "Your name", "email": "Email",
        "ship_note": "Shipping to mainland China", "sum_book": "Trust 《信任》, signed", "total": "Total", "buy": "Buy a signed copy", "secure": "Secure checkout by Stripe. You'll add your delivery address on the next step.",
        "loading": "…", "closed": "Orders open shortly. To reserve a copy, email", "err": "Something went wrong. Please try again, or email",
        "busy": "Opening secure checkout…", "fix": "Please add ",
        "fields": {"name": "your name", "email": "your email", "qty": "copies", "zone": "where to ship", "dedication": "the dedication"},
        "paid_h": "Thank you, your order is confirmed.", "paid_p": "A confirmation is on its way to your inbox. We'll email you the tracking number once your signed copy is posted.",
        "pend_p": "We're confirming your payment with Stripe. This will update in a moment.", "cancel_p": "Checkout was cancelled. You haven't been charged.",
        "en_tag": "Coming soon", "en_h": "English edition", "en_title": "Trust",
        "en_meta": "Rewritten for readers outside China",
        "en_blurb": "What Western companies can learn from how China's best brands build trust across borders. Leave your email and we'll tell you the day it goes on sale.",
        "join": "Notify me when it's out", "join_note": "One email when the English edition launches. No payment, no newsletter.",
        "joined": "Thanks. We'll email you the day the English edition goes on sale.", "already": "You're already signed up. We'll email you when it's out.",
        "about_h": "About the book",
        "about": ["<i>Trust</i> argues that for Chinese companies going global, trust is the asset that decides whether a brand is welcomed or resisted abroad, and that it can be built deliberately.",
                  "It brings together the lessons from Chris's years leading global public affairs at Huawei and from iMpact's work with hundreds of Chinese brands entering new markets."],
        "launch_cap": "At the launch of <i>Trust</i> <span lang=\"zh-Hans\">《信任》</span>",
        "also": "Also by Chris", "rebuild": "<i>Rebuild</i> <span lang=\"zh-Hans\">《新出海》</span>", "rebuild_p": "A Practical Guide to Localizing Your Brand Overseas · China Renmin University Press, 2025",
        "q": "Questions about an order? Email", "foot": "Books",
        "photo_alt": "Copies of Trust 《信任》 by Chris Pereira stacked on a table",
    },
    "zh": {
        "lang": "zh-CN", "home": "/zh/", "path": "/zh/books/", "other": "/books/", "other_label": "EN", "img": "/img/",
        "title": "彭家荣著作 | 《信任》作者签名版",
        "desc": "订购彭家荣《信任：中国企业全球化的黄金钥匙》作者签名版（深圳出版社，2026），寄送范围为中国大陆。英文版即将出版。",
        "nav": [("/zh/#writing", "文章"), ("/zh/#media", "媒体评论"), ("/zh/#speaking", "演讲"), ("/zh/#training", "培训"), ("/zh/books/", "书籍"), ("/zh/#about", "关于")],
        "contact": "联系", "label": "书籍",
        "h1": "<span class=\"hang\">《</span>信任》",
        "sub": "中国企业全球化的黄金钥匙",
        "lede": "中国企业如何在海外市场赢得信任。本书凝结了作者在中国二十多年的经验，从华为全球公共事务到今天服务的出海品牌。中文版现已上市，均为作者亲笔签名；面向海外读者重新撰写的英文版即将出版。",
        "facts": [("作者", "彭家荣 Chris Pereira"), ("出版社", "深圳出版社"), ("出版时间", "2026年2月")],
        "zh_tag": "现已上市", "zh_h": "中文版", "zh_title": "<span class=\"hang\">《</span>信任》",
        "zh_meta": "平装 · 作者亲笔签名 · 仅限中国大陆寄送",
        "qty": "数量", "ded": "签名题字（选填）", "ded_ph": "例如：致小明", "name": "您的姓名", "email": "邮箱",
        "ship_note": "中国大陆运费", "sum_book": "《信任》签名版", "total": "合计", "buy": "购买签名版", "secure": "由 Stripe 安全支付，下一步填写收货地址。",
        "loading": "…", "closed": "即将开放订购。如需预留，请发邮件至", "err": "出了点问题，请重试，或发邮件至",
        "busy": "正在打开安全支付页面…", "fix": "请填写",
        "fields": {"name": "姓名", "email": "邮箱", "qty": "数量", "zone": "寄送地区", "dedication": "题字"},
        "paid_h": "感谢订购，订单已确认。", "paid_p": "确认邮件已发送至您的邮箱。签名书寄出后，我们会再发邮件告知快递单号。",
        "pend_p": "正在向 Stripe 确认付款，稍后自动更新。", "cancel_p": "已取消支付，未产生任何费用。",
        "en_tag": "即将出版", "en_h": "英文版", "en_title": "Trust",
        "en_meta": "面向海外读者重新撰写",
        "en_blurb": "西方企业可以从中国顶尖品牌跨境建立信任的方式中学到什么。留下邮箱，新书开售当天我们会通知您。",
        "join": "上市时通知我", "join_note": "英文版上市时只发一封邮件，无需付款，不订阅任何简报。",
        "joined": "谢谢！英文版开售当天我们会邮件通知您。", "already": "您已登记，英文版上市时我们会通知您。",
        "about_h": "关于本书",
        "about": ["《信任》认为，对出海的中国企业而言，信任是决定品牌在海外被接纳还是被抵触的关键资产，而且可以有意识地建立。",
                  "书中汇集了作者多年负责华为全球公共事务的经验，以及美讯服务数百家中国品牌进入新市场的实践。"],
        "launch_cap": "《信任》新书发布会",
        "also": "作者另著", "rebuild": "《新出海》", "rebuild_p": "中企海外本土化实战手册 · 中国人民大学出版社，2025",
        "q": "订单问题请联系", "foot": "书籍",
        "photo_alt": "彭家荣《信任》新书摆放在桌上",
    },
}

CSS = """:root{--paper:#F6F2E9;--surface:#FFFFFF;--ink:#151313;--muted:#626060;--hair:#E2DCD0;--red:#A40706;--red-deep:#7A0504;--ok:#0B6B4F;--navy:#13305a;
--display:"Jost","Avenir Next","Helvetica Neue",Arial,sans-serif;--body:"Times New Roman","Tinos",Times,serif;--head:"Playfair Display","Times New Roman",Georgia,serif;
--zh:"PingFang SC","Hiragino Sans GB","Microsoft YaHei","Noto Sans SC",sans-serif}
*{box-sizing:border-box}
html{scroll-behavior:smooth}
body{margin:0;background:var(--paper);color:var(--ink);font-family:var(--body);font-size:17px;line-height:1.6;-webkit-font-smoothing:antialiased}
html[lang="zh-CN"] body{font-family:var(--body),"Songti SC","Noto Serif SC",serif}
a{color:var(--red);text-underline-offset:3px}
img{max-width:100%;display:block}
.wrap{max-width:1080px;margin:0 auto;padding:0 24px}
.bar{position:sticky;top:0;z-index:5;background:rgba(246,242,233,.94);backdrop-filter:blur(8px);border-bottom:1px solid var(--hair)}
.bar .wrap{display:flex;align-items:center;gap:18px;min-height:64px}
.mark{display:flex;align-items:center;gap:10px;font-family:var(--display);font-weight:600;font-size:18px;color:var(--ink);text-decoration:none;margin-right:auto}
.seal{background:var(--red);color:#fff;font-size:14px;padding:4px 7px;border-radius:3px}
.nav{display:flex;gap:22px}.nav a{font-family:var(--display);font-weight:500;font-size:15px;color:var(--ink);text-decoration:none}.nav a[aria-current]{color:var(--red)}
.langsw{font-family:var(--zh);font-size:14px;font-weight:500;color:var(--ink);text-decoration:none;border:1px solid var(--hair);border-radius:999px;padding:6px 12px;white-space:nowrap}
.langsw:hover{color:var(--red);border-color:var(--red)}
.btn{display:inline-flex;align-items:center;justify-content:center;gap:8px;font-family:var(--display);font-weight:600;font-size:15px;padding:11px 20px;border-radius:999px;text-decoration:none;border:1.5px solid var(--red);background:var(--red);color:#fff;cursor:pointer;transition:background .15s,border-color .15s}
.btn:hover{background:var(--red-deep);border-color:var(--red-deep)}
.btn[disabled]{opacity:.5;cursor:default}
.btn.ghost{background:transparent;color:var(--ink);border-color:var(--ink)}
.btn.ghost:hover{background:var(--ink);color:#fff;border-color:var(--ink)}
.label{font-family:var(--display);font-size:12.5px;font-weight:600;letter-spacing:.16em;text-transform:uppercase;color:var(--red)}
h1,h2,h3{font-family:var(--head);margin:0;font-weight:700;letter-spacing:-.01em;text-wrap:balance}
.zh{font-family:var(--zh);font-weight:600}
.hang{margin-left:-.5em}

/* intro */
.intro{padding:52px 0 36px;display:grid;grid-template-columns:minmax(0,1.05fr) minmax(0,1fr);gap:24px 56px;align-items:end;border-bottom:1px solid var(--ink)}
.intro h1{font-size:clamp(40px,5.2vw,64px);line-height:1.02;margin:10px 0 0}
.intro .sub{font-family:var(--head);font-style:italic;font-weight:400;font-size:clamp(19px,2vw,23px);color:var(--muted);margin:10px 0 0;line-height:1.3}
html[lang="zh-CN"] .intro .sub{font-family:var(--zh);font-style:normal;font-weight:500}
.lede{margin:0;font-size:17.5px;line-height:1.65;color:#2e2b2b}
.facts{display:grid;grid-template-columns:auto auto auto;justify-content:start;gap:8px 32px;margin:18px 0 0;padding:0;list-style:none;font-family:var(--display);font-size:13.5px}
.facts li{display:flex;flex-direction:column}
.facts b{font-size:11px;font-weight:600;letter-spacing:.14em;text-transform:uppercase;color:var(--muted)}
.notice{grid-column:1/-1;margin:0;padding:16px 20px;border-radius:12px;background:var(--surface);border:1px solid var(--hair);border-left:4px solid var(--ok);font-family:var(--display);font-size:15px}
.notice.warn{border-left-color:var(--red)}

/* the two editions */
.eds{display:grid;grid-template-columns:1fr 1fr;gap:28px;padding:40px 0 56px;align-items:stretch}
.ed{background:var(--surface);border:1px solid var(--hair);border-radius:16px;overflow:hidden;display:flex;flex-direction:column;box-shadow:0 1px 0 rgba(21,19,19,.03),0 18px 40px -28px rgba(21,19,19,.35)}
.vis{position:relative;aspect-ratio:4/3;overflow:hidden;background:#0d1b33}
.vis img{width:100%;height:100%;object-fit:cover}
.tag{position:absolute;top:16px;left:16px;font-family:var(--display);font-size:11.5px;font-weight:600;letter-spacing:.14em;text-transform:uppercase;padding:6px 11px;border-radius:999px;background:rgba(255,255,255,.94);color:var(--ink)}
.tag.live{background:var(--red);color:#fff}
.ebody{padding:26px 28px 28px;display:flex;flex-direction:column;flex:1}
.ehead{display:flex;justify-content:space-between;align-items:flex-start;gap:16px}
.ekicker{font-family:var(--display);font-size:12.5px;font-weight:600;letter-spacing:.16em;text-transform:uppercase;color:var(--red)}
.ed h2{font-size:30px;line-height:1.1;margin:6px 0 0}
.ed h2 [lang]{font-family:var(--zh);font-weight:600}
.price{font-family:var(--display);font-weight:600;font-size:30px;line-height:1;color:var(--ink);white-space:nowrap;margin-top:22px}
.price small{display:block;font-size:12px;font-weight:500;color:var(--muted);letter-spacing:.02em;margin-top:6px;text-align:right}
.emeta{font-family:var(--display);font-size:14px;color:var(--muted);margin:8px 0 0}
.eblurb{margin:14px 0 0;font-size:17px;line-height:1.6}
form{margin-top:22px;display:flex;flex-direction:column;flex:1}
.row{display:grid;grid-template-columns:110px 1fr;gap:12px}
.row2{display:grid;grid-template-columns:1fr 1fr;gap:12px;margin-top:12px}
label{display:block;font-family:var(--display);font-size:12px;font-weight:600;letter-spacing:.06em;text-transform:uppercase;color:var(--muted);margin:0 0 6px}
html[lang="zh-CN"] label{text-transform:none;letter-spacing:0;font-size:13px}
input,select{width:100%;font:16px var(--display);padding:11px 13px;border:1px solid #D6CFC1;border-radius:10px;background:#FBFAF7;color:var(--ink);transition:border-color .15s,background .15s}
input:focus,select:focus{outline:none;border-color:var(--red);background:#fff;box-shadow:0 0 0 3px rgba(164,7,6,.12)}
.sum{margin:18px 0 0;padding:14px 0 0;border-top:1px solid var(--hair);font-family:var(--display);font-size:14px;color:var(--muted)}
.sum div{display:flex;justify-content:space-between;padding:3px 0}
.sum .tot{color:var(--ink);font-weight:600;font-size:17px;padding-top:8px}
.go{margin-top:auto;padding-top:20px}
.go .btn{width:100%;font-size:16px;padding:14px 22px}
.small{font-family:var(--display);font-size:12.5px;color:var(--muted);margin:10px 0 0;text-align:center}
.msg{font-family:var(--display);font-size:14px;margin:8px 0 0;min-height:0;text-align:center}
.msg:empty{display:none}
.msg.bad{color:var(--red)}.msg.good{color:var(--ok);font-weight:500}
.hp{position:absolute;left:-9999px}

/* English edition cover, drawn (the real English cover isn't final yet) */
.encov{position:absolute;inset:0;display:flex;align-items:center;justify-content:center;background:radial-gradient(120% 90% at 30% 10%,#2a5ba0 0%,#173a6e 45%,#0d1f3d 100%)}
.encov .bk{width:46%;aspect-ratio:2/3;background:linear-gradient(180deg,#1f5db5 0%,#2e74cf 58%,#e8792e 58%,#f08a3a 100%);border-radius:3px 6px 6px 3px;box-shadow:-6px 0 0 rgba(0,0,0,.18) inset,0 26px 50px -18px rgba(0,0,0,.6);transform:rotate(-4deg);display:flex;flex-direction:column;align-items:center;padding:12% 8%;text-align:center;color:#fff}
.encov .bk i{font-style:normal;font-family:var(--display);font-size:8.5px;line-height:1.35;letter-spacing:.04em;opacity:.9;max-width:90%}
.encov .bk b{font-family:var(--display);font-weight:700;font-size:clamp(28px,3.4vw,40px);letter-spacing:.04em;color:#f6b37d;margin-top:14%;line-height:1}
.encov .bk em{font-style:normal;font-family:var(--display);font-size:11px;letter-spacing:.06em;margin-top:8%;opacity:.95}
.encov .bk span{font-family:var(--display);font-size:10px;letter-spacing:.14em;margin-top:auto;text-transform:uppercase;color:#fff}
.join-note{font-family:var(--display);font-size:12.5px;color:var(--muted);margin:10px 0 0;text-align:center}

/* about */
.about{display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1fr);gap:48px;align-items:center;padding:56px 0;border-top:1px solid var(--hair)}
.about figure{margin:0}
.about img{border-radius:12px;width:100%;height:auto;box-shadow:0 18px 40px -26px rgba(21,19,19,.45)}
.about figcaption{font-family:var(--display);font-size:13px;color:var(--muted);margin-top:10px}
.about h2{font-size:clamp(26px,2.8vw,34px);margin:8px 0 14px}
.about p{margin:0 0 14px;font-size:17.5px;line-height:1.65}
.also{display:flex;gap:16px;align-items:center;margin-top:24px;padding-top:20px;border-top:1px solid var(--hair)}
.also img{width:64px;height:auto;border-radius:2px 4px 4px 2px;box-shadow:0 8px 18px -8px rgba(40,20,10,.45)}
.also b{display:block;font-family:var(--head);font-size:19px}
.also b [lang]{font-family:var(--zh);font-weight:600}
.also span{font-family:var(--display);font-size:13px;color:var(--muted)}
.also .k{font-family:var(--display);font-size:11px;font-weight:600;letter-spacing:.14em;text-transform:uppercase;color:var(--red)}
.qline{font-family:var(--display);font-size:14px;color:var(--muted);padding:0 0 48px}
footer{border-top:1px solid var(--hair);padding:22px 0 40px;font-family:var(--display);font-size:13px;color:var(--muted)}
footer .wrap{display:flex;justify-content:space-between;gap:12px;flex-wrap:wrap}

@media (max-width:900px){.intro{grid-template-columns:1fr;align-items:start;padding-top:36px}.eds{grid-template-columns:1fr;gap:22px;padding-top:28px}.about{grid-template-columns:1fr;gap:28px;padding:40px 0}}
@media (max-width:760px){.nav{display:none}.langsw{margin-left:auto;padding:5px 9px;font-size:13px}.wrap{padding:0 16px}.ebody{padding:22px 20px 22px}.row{grid-template-columns:88px 1fr}.row2{grid-template-columns:1fr}.facts{grid-template-columns:1fr 1fr}.ed h2,.price{font-size:26px}}
"""

JS = r"""(function(){
var API=%(api)s, L=%(l)s, T=%(t)s, SEP=L==='zh'?'、':', ';
var $=function(id){return document.getElementById(id)};
var book=null, fmt=function(minor,cur){return (cur==='cny'?'¥':cur.toUpperCase()+' ')+(minor/100).toFixed(2).replace(/\.00$/,'')};
var EM=/^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/;
function zone(){return book.shipping.filter(function(x){return x.id===$('zone').value})[0]||book.shipping[0]}
function total(){if(!book)return;var q=+$('qty').value||1,z=zone();$('sBook').textContent=fmt(book.price*q,book.currency);$('sShip').textContent=fmt(z.amount,book.currency);$('tot').textContent=fmt(book.price*q+z.amount,book.currency)}
function say(id,text,cls){var m=$(id);m.className='msg'+(cls?' '+cls:'');m.textContent=text}
function sayMail(id,lead){var m=$(id);m.className='msg bad';m.textContent=lead+' ';var a=document.createElement('a');a.href='mailto:inquiries@chrisjpereira.com';a.textContent='inquiries@chrisjpereira.com';m.appendChild(a)}
fetch(API+'/books').then(function(r){return r.json()}).then(function(j){
  book=(j.books||[]).filter(function(b){return b.id==='trust-zh'})[0];
  if(!book||!book.open){$('buy').disabled=true;$('price').textContent='';sayMail('bmsg',T.closed);return}
  $('price').firstChild.textContent=fmt(book.price,book.currency);
  var q=$('qty');q.innerHTML='';for(var i=1;i<=book.maxQty;i++){var o=document.createElement('option');o.value=i;o.textContent=i;q.appendChild(o)}
  var z=$('zone');z.innerHTML='';book.shipping.forEach(function(s){var o=document.createElement('option');o.value=s.id;o.textContent=(L==='zh'?s.zh:s.en);z.appendChild(o)});
  $('zoneBox').hidden=book.shipping.length<2;$('buy').disabled=false;total();
}).catch(function(){$('buy').disabled=true;sayMail('bmsg',T.err)});
document.addEventListener('change',function(e){if(e.target.id==='qty'||e.target.id==='zone')total()});
$('order').addEventListener('submit',function(e){e.preventDefault();if(!book)return;
  var miss=[];if(!$('bname').value.trim())miss.push(T.fields.name);if(!EM.test($('bemail').value.trim()))miss.push(T.fields.email);
  if(miss.length){say('bmsg',T.fix+miss.join(SEP),'bad');return}var b=$('buy');b.disabled=true;say('bmsg',T.busy);
  fetch(API+'/book',{method:'POST',headers:{'content-type':'application/json'},body:JSON.stringify({book:'trust-zh',qty:+$('qty').value,zone:zone().id,dedication:$('ded').value,name:$('bname').value,email:$('bemail').value,lang:L,website:$('bweb').value})})
  .then(function(r){return r.json()}).then(function(j){if(j.ok&&j.url){location.href=j.url;return}b.disabled=false;
    if(j.fields)say('bmsg',T.fix+j.fields.map(function(f){return T.fields[f]||f}).join(SEP),'bad');else sayMail('bmsg',T.err)})
  .catch(function(){b.disabled=false;sayMail('bmsg',T.err)})});
$('wait').addEventListener('submit',function(e){e.preventDefault();
  if(!EM.test($('wemail').value.trim())){say('wmsg',T.fix+T.fields.email,'bad');return}var b=$('wbtn');b.disabled=true;
  fetch(API+'/book-waitlist',{method:'POST',headers:{'content-type':'application/json'},body:JSON.stringify({book:'trust-en',name:$('wname').value,email:$('wemail').value,lang:L,website:$('wweb').value})})
  .then(function(r){return r.json()}).then(function(j){if(j.ok){say('wmsg',j.already?T.already:T.joined,'good');return}b.disabled=false;
    if(j.fields)say('wmsg',T.fix+j.fields.map(function(f){return T.fields[f]||f}).join(SEP),'bad');else sayMail('wmsg',T.err)})
  .catch(function(){b.disabled=false;sayMail('wmsg',T.err)})});
var p=new URLSearchParams(location.search), id=p.get('p'), n=$('notice');
if(id&&p.get('cancelled')){n.hidden=false;n.className='notice warn';n.textContent=T.cancel}
else if(id){n.hidden=false;n.innerHTML='<b></b> <span></span>';n.querySelector('b').textContent=T.paidH;n.querySelector('span').textContent=T.pend;
  var tries=0;(function check(){fetch(API+'/book-status?p='+encodeURIComponent(id)).then(function(r){return r.json()}).then(function(j){
    if(j.status==='paid'){n.querySelector('span').textContent=T.paidP}else if(j.status==='pending'&&++tries<10){setTimeout(check,3000)}else if(j.status!=='pending'){n.className='notice warn';n.textContent=T.cancel}})})();
  try{history.replaceState(null,'',location.pathname)}catch(e){}}
})();"""


def page(k):
    t = T[k]
    js = JS % {"api": json.dumps(API), "l": json.dumps("zh" if k == "zh" else "en"), "t": json.dumps({
        "closed": t["closed"], "err": t["err"], "busy": t["busy"], "fix": t["fix"], "fields": t["fields"], "paidH": t["paid_h"], "paidP": t["paid_p"],
        "pend": t["pend_p"], "cancel": t["cancel_p"], "joined": t["joined"], "already": t["already"]}, ensure_ascii=False)}
    csp = ("default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; font-src 'self' https://fonts.gstatic.com data:; "
           "img-src 'self' data: https:; connect-src 'self' https://stats.chrisjpereira.com https://www.globalconnect.show; object-src 'none'; base-uri 'self'; "
           "form-action 'self'; upgrade-insecure-requests")
    url = "https://chrisjpereira.com" + t["path"]
    nav = "".join(f'<a href="{h}"{" aria-current=\"page\"" if h == t["path"] else ""}>{x}</a>' for h, x in t["nav"])
    facts = "".join(f"<li><b>{a}</b><span>{b}</span></li>" for a, b in t["facts"])
    ld = json.dumps({"@context": "https://schema.org", "@type": "Book", "name": "信任：中国企业全球化的黄金钥匙", "alternateName": "Trust: The Golden Key to Chinese Enterprises' Globalization",
                     "inLanguage": "zh-CN", "bookFormat": "https://schema.org/Paperback", "author": {"@type": "Person", "name": "Chris Pereira", "alternateName": "彭家荣", "url": "https://chrisjpereira.com/"},
                     "publisher": {"@type": "Organization", "name": "Shenzhen Publishing House 深圳出版社"}, "datePublished": "2026-02", "image": "https://chrisjpereira.com/img/trust-books.webp", "url": url}, ensure_ascii=False)
    return f"""<!doctype html>
<html lang="{t['lang']}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<meta http-equiv="Content-Security-Policy" content="{csp}">
<meta name="referrer" content="strict-origin-when-cross-origin">
<title>{t['title']}</title>
<meta name="description" content="{t['desc']}">
<meta name="robots" content="index,follow">
<meta name="theme-color" content="#A40706">
<link rel="canonical" href="{url}">
<link rel="alternate" hreflang="en" href="https://chrisjpereira.com/books/">
<link rel="alternate" hreflang="zh-CN" href="https://chrisjpereira.com/zh/books/">
<meta property="og:type" content="website">
<meta property="og:title" content="{t['title']}">
<meta property="og:description" content="{t['desc']}">
<meta property="og:image" content="https://chrisjpereira.com/img/trust-books.webp">
<meta property="og:url" content="{url}">
<link rel="icon" href="/favicon.ico" sizes="any">
<link rel="apple-touch-icon" sizes="180x180" href="/apple-touch-icon.png">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Jost:wght@400;500;600;700&family=Playfair+Display:ital,wght@0,600;0,700;1,400&family=Tinos:ital,wght@0,400;0,700;1,400&display=swap">
<script type="application/ld+json">{ld}</script>
<style>{CSS}</style>
</head>
<body>
<header class="bar"><div class="wrap">
  <a class="mark" href="{t['home']}"><span class="seal" lang="zh-Hans">彭家荣</span>Chris Pereira</a>
  <nav class="nav" aria-label="Sections">{nav}</nav>
  <a class="langsw" href="{t['other']}">{t['other_label']}</a>
  <a class="btn" href="{t['home']}#contact">{t['contact']}</a>
</div></header>
<main class="wrap">
  <section class="intro">
    <div>
      <span class="label">{t['label']}</span>
      <h1>{t['h1']}</h1>
      <p class="sub">{t['sub']}</p>
    </div>
    <div>
      <p class="lede">{t['lede']}</p>
      <ul class="facts">{facts}</ul>
    </div>
    <div class="notice" id="notice" role="status" hidden></div>
  </section>

  <section class="eds">
    <article class="ed" id="chinese">
      <div class="vis"><img src="{t['img']}trust-books.webp" width="1000" height="750" alt="{t['photo_alt']}"><span class="tag live">{t['zh_tag']}</span></div>
      <div class="ebody">
        <div class="ehead">
          <div><span class="ekicker">{t['zh_h']}</span><h2>{t['zh_title']}</h2></div>
          <div class="price" id="price"><span>{t['loading']}</span></div>
        </div>
        <p class="emeta">{t['zh_meta']}</p>
        <form id="order" novalidate>
          <div class="row">
            <div><label for="qty">{t['qty']}</label><select id="qty"><option>1</option></select></div>
            <div><label for="ded">{t['ded']}</label><input id="ded" maxlength="80" placeholder="{t['ded_ph']}"></div>
          </div>
          <div id="zoneBox" hidden style="margin-top:12px"><label for="zone">Ship to</label><select id="zone"></select></div>
          <div class="row2">
            <div><label for="bname">{t['name']}</label><input id="bname" autocomplete="name" maxlength="120" required></div>
            <div><label for="bemail">{t['email']}</label><input id="bemail" type="email" autocomplete="email" maxlength="200" required></div>
          </div>
          <input class="hp" id="bweb" tabindex="-1" autocomplete="off" aria-hidden="true">
          <div class="sum"><div><span>{t['sum_book']}</span><span id="sBook">–</span></div><div><span>{t['ship_note']}</span><span id="sShip">–</span></div><div class="tot"><span>{t['total']}</span><span id="tot">–</span></div></div>
          <div class="go"><button class="btn" id="buy" type="submit" disabled>{t['buy']}</button>
          <p class="small">{t['secure']}</p><p class="msg" id="bmsg" role="status"></p></div>
        </form>
      </div>
    </article>

    <article class="ed" id="english">
      <div class="vis"><div class="encov" aria-hidden="true"><div class="bk"><i>The Golden Key to Chinese Enterprises' Globalization</i><b>TRUST</b><em>Chris Pereira</em><span>English edition</span></div></div><span class="tag">{t['en_tag']}</span></div>
      <div class="ebody">
        <div class="ehead"><div><span class="ekicker">{t['en_h']}</span><h2>{t['en_title']}</h2></div></div>
        <p class="emeta">{t['en_meta']}</p>
        <p class="eblurb">{t['en_blurb']}</p>
        <form id="wait" novalidate>
          <div class="row2" style="margin-top:0">
            <div><label for="wname">{t['name']}</label><input id="wname" autocomplete="name" maxlength="120"></div>
            <div><label for="wemail">{t['email']}</label><input id="wemail" type="email" autocomplete="email" maxlength="200" required></div>
          </div>
          <input class="hp" id="wweb" tabindex="-1" autocomplete="off" aria-hidden="true">
          <div class="go"><button class="btn ghost" id="wbtn" type="submit">{t['join']}</button>
          <p class="join-note">{t['join_note']}</p><p class="msg" id="wmsg" role="status"></p></div>
        </form>
      </div>
    </article>
  </section>

  <section class="about">
    <figure><img src="{t['img']}trust-launch.webp" width="900" height="696" loading="lazy" alt="Chris Pereira holding Trust 《信任》 at the book launch"><figcaption>{t['launch_cap']}</figcaption></figure>
    <div>
      <h2>{t['about_h']}</h2>
      {''.join(f'<p>{x}</p>' for x in t['about'])}
      <div class="also"><img src="{t['img']}book-rebuild.webp" width="400" height="581" loading="lazy" alt="Cover of Rebuild 《新出海》 by Chris Pereira"><div><span class="k">{t['also']}</span><b>{t['rebuild']}</b><span>{t['rebuild_p']}</span></div></div>
    </div>
  </section>
  <p class="qline">{t['q']} <a href="mailto:inquiries@chrisjpereira.com">inquiries@chrisjpereira.com</a></p>
</main>
<footer><div class="wrap"><span>Chris Pereira <span lang="zh-Hans">彭家荣</span></span><span>{t['foot']}</span></div></footer>
<script>{js}</script>
<script defer src="/a.js"></script>
</body>
</html>
"""


def build():
    for k, d in (("en", "books"), ("zh", os.path.join("zh", "books"))):
        os.makedirs(os.path.join(HERE, d), exist_ok=True)
        with open(os.path.join(HERE, d, "index.html"), "w", encoding="utf-8") as f:
            f.write(page(k))


if __name__ == "__main__":
    build()
