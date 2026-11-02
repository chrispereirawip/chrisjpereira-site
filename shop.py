import json
"""Book shop pages: /books/ (English) and /zh/books/ (Simplified Chinese). 2026-11-02.

Chris: "set up a page for people to buy my English and Chinese version books, and pay with Stripe", using the GCS Stripe account.
The page is static; prices, shipping and checkout come from the GCS site's API (www.globalconnect.show/api/pay/books, see
gcs-site functions/lib/books.js), so a price change never needs a rebuild here. Run: python3 shop.py (build.py calls it too).
"""
import os

API = "https://www.globalconnect.show/api/pay"
HERE = os.path.dirname(os.path.abspath(__file__))

T = {
    "en": {
        "lang": "en", "home": "/", "path": "/books/", "other": "/zh/books/", "other_label": "中文",
        "title": "Buy Trust 《信任》 by Chris Pereira | Books",
        "desc": "Order a signed copy of Trust 《信任》 (Chinese edition, Shenzhen Publishing House, 2026) by Chris Pereira, posted within mainland China. The English edition is coming soon.",
        "nav": ['<a href="/#writing">Writing</a>', '<a href="/#media">Commentary</a>', '<a href="/#speaking">Speaking</a>', '<a href="/#about">About</a>', '<a href="/books/" aria-current="page">Books</a>'],
        "contact": "Contact", "label": "Books", "h1": "Signed copies of Trust 《信任》",
        "lede": "The Golden Key to Chinese Enterprises' Globalization. Signed copies of the Chinese edition, posted within mainland China. The English edition is coming soon.",
        "zh_h": "Chinese edition", "zh_sub": "《信任》 · Shenzhen Publishing House 深圳出版社, 2026 · signed",
        "zh_blurb": "Twenty years of lessons on how Chinese companies earn trust abroad, from Huawei to the brands Chris advises today. Every copy is signed; add a name if you'd like a dedication.",
        "qty": "Copies", "zone": "Ship to", "ded": "Sign it to (optional)", "ded_ph": "e.g. To Anna", "name": "Your name", "email": "Email",
        "total": "Total", "incl": "incl. shipping", "buy": "Buy now", "secure": "Secure payment by Stripe. You'll enter your postal address on the next page.",
        "loading": "Loading price…", "closed": "Orders open shortly. To reserve a copy now, email", "err": "Something went wrong. Please try again, or email",
        "busy": "Opening secure checkout…", "fix": "Please check: ",
        "fields": {"name": "your name", "email": "your email", "qty": "copies", "zone": "where to ship", "dedication": "the dedication"},
        "paid_h": "Thank you, your order is confirmed.", "paid_p": "A confirmation is on its way to your inbox. We'll email the tracking number once your signed copy is posted.",
        "pend_p": "We're confirming your payment with Stripe. This page will update in a moment.", "cancel_p": "Checkout was cancelled. Nothing was charged.",
        "en_h": "English edition", "en_sub": "Trust · coming soon",
        "en_blurb": "Rewritten for readers outside China: what Western companies can learn from how China's best brands build trust across borders. Join the list and we'll email you the day it goes on sale. No payment now.",
        "join": "Join the list", "joined": "You're on the list. We'll email you when it's out.", "already": "You're already on the list.",
        "rebuild": "Also by Chris: <i>Rebuild</i> 《新出海》 (China Renmin University Press, 2025), available from Chinese bookstores.",
        "updated": "Books", "q": "Questions about an order?",
    },
    "zh": {
        "lang": "zh-CN", "home": "/zh/", "path": "/zh/books/", "other": "/books/", "other_label": "English",
        "title": "购买彭家荣《信任》签名版 | 书籍",
        "desc": "订购彭家荣《信任：中国企业全球化的黄金钥匙》作者签名版（深圳出版社，2026），或登记英文版上市通知。",
        "nav": ['<a href="/zh/#writing">文章</a>', '<a href="/zh/#media">评论</a>', '<a href="/zh/#speaking">演讲</a>', '<a href="/zh/#about">关于</a>', '<a href="/zh/books/" aria-current="page">书籍</a>'],
        "contact": "联系", "label": "书籍", "h1": "《信任》作者签名版",
        "lede": "《信任：中国企业全球化的黄金钥匙》。中文版签名书，寄送范围仅限中国大陆。英文版即将出版。",
        "zh_h": "中文版", "zh_sub": "《信任》 · 深圳出版社，2026 · 作者签名",
        "zh_blurb": "二十年经验：中国企业如何在海外赢得信任，从华为到今天的出海品牌。每本书均由作者亲笔签名，如需题字，请填写受赠人姓名。",
        "qty": "数量", "zone": "寄送地区", "ded": "签名题字给（选填）", "ded_ph": "例如：致小明", "name": "您的姓名", "email": "邮箱",
        "total": "合计", "incl": "含运费", "buy": "立即购买", "secure": "由 Stripe 安全支付，下一页填写收货地址。",
        "loading": "正在加载价格…", "closed": "即将开放订购。如需预留，请发邮件至", "err": "出了点问题，请重试，或发邮件至",
        "busy": "正在打开安全支付页面…", "fix": "请检查：",
        "fields": {"name": "姓名", "email": "邮箱", "qty": "数量", "zone": "寄送地区", "dedication": "题字"},
        "paid_h": "感谢订购，订单已确认。", "paid_p": "确认邮件已发送至您的邮箱。签名书寄出后，我们会再发邮件告知快递单号。",
        "pend_p": "正在向 Stripe 确认付款，页面稍后会自动更新。", "cancel_p": "已取消支付，未产生任何费用。",
        "en_h": "英文版", "en_sub": "Trust · 即将出版",
        "en_blurb": "面向海外读者重新撰写：西方企业可以从中国顶尖品牌跨境建立信任的方式中学到什么。登记后，新书开售当天我们会邮件通知您，现在无需付款。",
        "join": "登记通知", "joined": "已登记，新书上市时我们会邮件通知您。", "already": "您已经登记过了。",
        "rebuild": "作者另著：《新出海：中企海外本土化实战手册》（中国人民大学出版社，2025），各大书店有售。",
        "updated": "书籍", "q": "订单问题请联系",
    },
}

CSS = """:root{--paper:#F6F2E9;--surface:#FFFFFF;--ink:#151313;--muted:#626060;--hair:#E2DCD0;--red:#A40706;--red-deep:#7A0504;--ok:#0B6B4F;
--display:"Jost","Avenir Next","Helvetica Neue",Arial,sans-serif;--body:"Times New Roman","Tinos",Times,serif;--head:"Playfair Display","Times New Roman",Georgia,serif}
*{box-sizing:border-box}
body{margin:0;background:var(--paper);color:var(--ink);font-family:var(--body);font-size:17px;line-height:1.6}
:lang(zh-CN) body,body:lang(zh-CN){font-family:"Times New Roman","Tinos","Songti SC","Noto Serif SC",serif}
a{color:var(--red);text-underline-offset:3px}
.wrap{max-width:1080px;margin:0 auto;padding:0 24px}
.bar{position:sticky;top:0;z-index:5;background:rgba(246,242,233,.94);backdrop-filter:blur(8px);border-bottom:1px solid var(--hair)}
.bar .wrap{display:flex;align-items:center;gap:18px;min-height:64px}
.mark{display:flex;align-items:center;gap:10px;font-family:var(--display);font-weight:600;font-size:18px;color:var(--ink);text-decoration:none;margin-right:auto}
.seal{background:var(--red);color:#fff;font-size:14px;padding:4px 7px;border-radius:3px}
.nav{display:flex;gap:22px}.nav a{font-family:var(--display);font-weight:500;font-size:15px;color:var(--ink);text-decoration:none}.nav a[aria-current]{color:var(--red)}
.lang{font-family:var(--display);font-size:14px;color:var(--muted);text-decoration:none}
.btn{display:inline-flex;align-items:center;justify-content:center;gap:8px;font-family:var(--display);font-weight:600;font-size:15px;padding:11px 20px;border-radius:999px;text-decoration:none;border:1.5px solid var(--red);background:var(--red);color:#fff;cursor:pointer}
.btn:hover{background:var(--red-deep);border-color:var(--red-deep)}
.btn[disabled]{opacity:.55;cursor:default}
.btn.big{font-size:17px;padding:14px 26px;width:100%}
.label{font-family:var(--display);font-size:12.5px;font-weight:600;letter-spacing:.16em;text-transform:uppercase;color:var(--red)}
h1,h2{font-family:var(--head);margin:0;font-weight:700;letter-spacing:-.01em;text-wrap:balance}
h1{font-size:clamp(30px,4vw,42px);line-height:1.08;margin:8px 0 0}
h2{font-size:clamp(22px,2.4vw,26px);font-weight:600;line-height:1.15}
.intro{padding-top:40px;padding-bottom:8px}
.lede{margin:12px 0 0;max-width:62ch;color:var(--muted);font-size:16.5px;line-height:1.55}
.notice{margin:22px 0 0;padding:16px 18px;border-radius:10px;background:var(--surface);border:1px solid var(--hair);border-left:4px solid var(--ok)}
.notice.warn{border-left-color:var(--red)}
.notice b{font-family:var(--display)}
.book{display:grid;grid-template-columns:260px minmax(0,1fr);gap:36px;padding:32px 0;border-bottom:1px solid var(--hair);align-items:start}
.book:last-of-type{border-bottom:0}
.cover{width:100%;height:auto;border-radius:4px;box-shadow:0 14px 34px rgba(21,19,19,.18)}
.soon{aspect-ratio:400/604;background:linear-gradient(160deg,#1d3d6b,#0f2342);color:#fff;display:flex;flex-direction:column;justify-content:center;align-items:center;gap:10px;text-align:center;padding:20px}
.soon b{font-family:var(--head);font-size:44px;line-height:1}.soon span{font-family:var(--display);font-size:15px;letter-spacing:.06em}.soon .yr{opacity:.7;font-size:13px}
.sub{font-family:var(--display);font-size:14px;color:var(--muted);margin:6px 0 12px}
.blurb{margin:0 0 18px;max-width:60ch}
form.card{background:var(--surface);border:1px solid var(--hair);border-radius:12px;padding:20px;max-width:560px}
.grid2{display:grid;grid-template-columns:1fr 1fr;gap:12px 14px}
.full{grid-column:1/-1}
label{display:block;font-family:var(--display);font-size:13px;font-weight:600;color:var(--muted);margin:0 0 4px}
input,select{width:100%;font:16px var(--display);padding:10px 12px;border:1px solid #CFC8BA;border-radius:8px;background:#fff;color:var(--ink)}
input:focus,select:focus{outline:2px solid var(--red);outline-offset:1px;border-color:var(--red)}
.totline{display:flex;justify-content:space-between;align-items:baseline;margin:16px 0 12px;font-family:var(--display)}
.totline b{font-size:22px}
.small{font-family:var(--display);font-size:13px;color:var(--muted);margin:10px 0 0}
.msg{font-family:var(--display);font-size:14px;margin:10px 0 0;min-height:1em}
.msg.bad{color:var(--red)}.msg.good{color:var(--ok)}
.hp{position:absolute;left:-9999px}
.also{font-size:15.5px;color:var(--muted);padding:6px 0 30px}
footer{border-top:1px solid var(--hair);padding:22px 0 40px;font-family:var(--display);font-size:13px;color:var(--muted)}
footer .wrap{display:flex;justify-content:space-between;gap:12px;flex-wrap:wrap}
@media (max-width:760px){.nav{display:none}.book{grid-template-columns:1fr;gap:18px}.cover{max-width:220px;margin:0 auto}.grid2{grid-template-columns:1fr}.wrap{padding:0 16px}}
"""

JS = r"""(function(){
var API=%(api)s, L=%(l)s, T=%(t)s, SEP=L==='zh'?'、':', ';
var $=function(id){return document.getElementById(id)};
var book=null, fmt=function(minor,cur){return (cur==='cny'?'¥':cur.toUpperCase()+' ')+(minor/100).toFixed(2).replace(/\.00$/,'')};
function zoneLabel(z){return (L==='zh'?z.zh:z.en)+' · +'+fmt(z.amount,book.currency)}
function total(){if(!book)return;var q=+$('qty').value||1,z=book.shipping.filter(function(x){return x.id===$('zone').value})[0];$('tot').textContent=fmt(book.price*q+(z?z.amount:0),book.currency)}
function say(id,text,cls){var m=$(id);m.className='msg'+(cls?' '+cls:'');m.textContent=text}
function sayMail(id,lead){var m=$(id);m.className='msg bad';m.textContent=lead+' ';var a=document.createElement('a');a.href='mailto:inquiries@chrisjpereira.com';a.textContent='inquiries@chrisjpereira.com';m.appendChild(a)}
fetch(API+'/books').then(function(r){return r.json()}).then(function(j){
  book=(j.books||[]).filter(function(b){return b.id==='trust-zh'})[0];
  if(!book||!book.open){$('buy').disabled=true;$('price').textContent='';sayMail('bmsg',T.closed);return}
  $('price').textContent=fmt(book.price,book.currency);
  var q=$('qty');q.innerHTML='';for(var i=1;i<=book.maxQty;i++){var o=document.createElement('option');o.value=i;o.textContent=i;q.appendChild(o)}
  var z=$('zone');z.innerHTML='';book.shipping.forEach(function(s){var o=document.createElement('option');o.value=s.id;o.textContent=zoneLabel(s);z.appendChild(o)});
  if(L==='en'&&book.shipping.length>2)z.value='intl';
  $('buy').disabled=false;say('bmsg','');total();
}).catch(function(){$('buy').disabled=true;sayMail('bmsg',T.err)});
document.addEventListener('change',function(e){if(e.target.id==='qty'||e.target.id==='zone')total()});
$('order').addEventListener('submit',function(e){e.preventDefault();if(!book)return;
  var miss=[];if(!$('bname').value.trim())miss.push(T.fields.name);if(!/^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test($('bemail').value.trim()))miss.push(T.fields.email);
  if(miss.length){say('bmsg',T.fix+miss.join(SEP),'bad');return}var b=$('buy');b.disabled=true;say('bmsg',T.busy);
  fetch(API+'/book',{method:'POST',headers:{'content-type':'application/json'},body:JSON.stringify({book:'trust-zh',qty:+$('qty').value,zone:$('zone').value,dedication:$('ded').value,name:$('bname').value,email:$('bemail').value,lang:L,website:$('bweb').value})})
  .then(function(r){return r.json()}).then(function(j){if(j.ok&&j.url){location.href=j.url;return}b.disabled=false;
    if(j.fields)say('bmsg',T.fix+j.fields.map(function(f){return T.fields[f]||f}).join(SEP),'bad');else sayMail('bmsg',T.err)})
  .catch(function(){b.disabled=false;sayMail('bmsg',T.err)})});
$('wait').addEventListener('submit',function(e){e.preventDefault();
  if(!/^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test($('wemail').value.trim())){say('wmsg',T.fix+T.fields.email,'bad');return}var b=$('wbtn');b.disabled=true;
  fetch(API+'/book-waitlist',{method:'POST',headers:{'content-type':'application/json'},body:JSON.stringify({book:'trust-en',name:$('wname').value,email:$('wemail').value,lang:L,website:$('wweb').value})})
  .then(function(r){return r.json()}).then(function(j){if(j.ok){say('wmsg',j.already?T.already:T.joined,'good');return}b.disabled=false;
    if(j.fields)say('wmsg',T.fix+j.fields.map(function(f){return T.fields[f]||f}).join(SEP),'bad');else sayMail('wmsg',T.err)})
  .catch(function(){b.disabled=false;sayMail('wmsg',T.err)})});
var p=new URLSearchParams(location.search), id=p.get('p'), n=$('notice');
if(id&&p.get('cancelled')){n.hidden=false;n.className='notice warn';n.textContent=T.cancel}
else if(id){n.hidden=false;n.innerHTML='<b></b><br><span></span>';n.querySelector('b').textContent=T.paidH;n.querySelector('span').textContent=T.pend;
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
<meta property="og:type" content="product">
<meta property="og:title" content="{t['h1']}">
<meta property="og:description" content="{t['desc']}">
<meta property="og:image" content="https://chrisjpereira.com/img/trust-launch.webp">
<meta property="og:url" content="{url}">
<link rel="icon" href="/favicon.ico" sizes="any">
<link rel="apple-touch-icon" sizes="180x180" href="/apple-touch-icon.png">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Jost:wght@400;500;600;700&family=Playfair+Display:wght@600;700&family=Tinos:ital,wght@0,400;0,700;1,400&display=swap">
<script type="application/ld+json">{json.dumps({"@context": "https://schema.org", "@type": "Book", "name": "信任：中国企业全球化的黄金钥匙", "alternateName": "Trust: The Golden Key to Chinese Enterprises' Globalization", "inLanguage": "zh-CN", "author": {"@type": "Person", "name": "Chris Pereira", "alternateName": "彭家荣", "url": "https://chrisjpereira.com/"}, "publisher": {"@type": "Organization", "name": "Shenzhen Publishing House 深圳出版社"}, "datePublished": "2026-02", "image": "https://chrisjpereira.com/img/book-trust.webp", "url": url}, ensure_ascii=False)}</script>
<style>{CSS}</style>
</head>
<body>
<header class="bar"><div class="wrap">
  <a class="mark" href="{t['home']}"><span class="seal" lang="zh-Hans">彭家荣</span>Chris Pereira</a>
  <nav class="nav" aria-label="Sections">{''.join(t['nav'])}</nav>
  <a class="lang" href="{t['other']}">{t['other_label']}</a>
  <a class="btn" href="{t['home']}#contact">{t['contact']}</a>
</div></header>
<main>
  <div class="wrap intro">
    <span class="label">{t['label']}</span><h1>{t['h1']}</h1>
    <p class="lede">{t['lede']}</p>
    <div class="notice" id="notice" role="status" hidden></div>
  </div>
  <div class="wrap">
    <section class="book" id="chinese">
      <img class="cover" src="/img/book-trust.webp" width="400" height="604" alt="Cover of Trust 《信任》 by Chris Pereira">
      <div>
        <h2>{t['zh_h']} <span id="price" style="color:var(--red);font-family:var(--display);font-size:.8em;margin-left:6px">{t['loading']}</span></h2>
        <p class="sub">{t['zh_sub']}</p>
        <p class="blurb">{t['zh_blurb']}</p>
        <form class="card" id="order" novalidate>
          <div class="grid2">
            <div><label for="qty">{t['qty']}</label><select id="qty"><option>1</option></select></div>
            <div><label for="zone">{t['zone']}</label><select id="zone"></select></div>
            <div class="full"><label for="ded">{t['ded']}</label><input id="ded" maxlength="80" placeholder="{t['ded_ph']}"></div>
            <div><label for="bname">{t['name']}</label><input id="bname" autocomplete="name" maxlength="120" required></div>
            <div><label for="bemail">{t['email']}</label><input id="bemail" type="email" autocomplete="email" maxlength="200" required></div>
          </div>
          <input class="hp" id="bweb" tabindex="-1" autocomplete="off" aria-hidden="true">
          <div class="totline"><span>{t['total']} <span class="small">({t['incl']})</span></span><b id="tot">–</b></div>
          <button class="btn big" id="buy" type="submit" disabled>{t['buy']}</button>
          <p class="small">{t['secure']}</p>
          <p class="msg" id="bmsg" role="status"></p>
        </form>
      </div>
    </section>
    <section class="book" id="english">
      <div class="cover soon" aria-hidden="true"><span class="label" style="color:#fff">English edition</span><b>Trust</b><span>Chris Pereira</span><span class="yr">Coming soon</span></div>
      <div>
        <h2>{t['en_h']}</h2>
        <p class="sub">{t['en_sub']}</p>
        <p class="blurb">{t['en_blurb']}</p>
        <form class="card" id="wait" novalidate>
          <div class="grid2">
            <div><label for="wname">{t['name']}</label><input id="wname" autocomplete="name" maxlength="120"></div>
            <div><label for="wemail">{t['email']}</label><input id="wemail" type="email" autocomplete="email" maxlength="200" required></div>
          </div>
          <input class="hp" id="wweb" tabindex="-1" autocomplete="off" aria-hidden="true">
          <button class="btn big" id="wbtn" type="submit" style="margin-top:14px">{t['join']}</button>
          <p class="msg" id="wmsg" role="status"></p>
        </form>
      </div>
    </section>
    <p class="also">{t['rebuild']}<br>{t['q']} <a href="mailto:inquiries@chrisjpereira.com">inquiries@chrisjpereira.com</a></p>
  </div>
</main>
<footer><div class="wrap"><span>Chris Pereira <span lang="zh-Hans">彭家荣</span></span><span>{t['updated']}</span></div></footer>
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
