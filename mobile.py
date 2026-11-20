"""Simplified phone layout (<=700px) for index.html and zh/index.html. Run after build.py."""
import re
CSS = """
.menubtn,.bar .nav .mcontact,.mmore{display:none}
@media (max-width:700px){
 .bar .nav,.bar .langsw+.btn{display:none}
 .menubtn{display:inline-flex;align-items:center;gap:6px;margin-left:8px;font:600 14px var(--display);color:var(--ink);background:none;border:1px solid var(--hair);border-radius:999px;padding:6px 12px;cursor:pointer}
 .menubtn svg{width:16px;height:16px;stroke:currentColor;stroke-width:2;fill:none}
 .bar.open .nav{display:flex;order:3;width:100%;flex-direction:column;gap:0;padding:6px 0 10px;font-size:17px;white-space:normal;overflow:visible;letter-spacing:0}
 .bar.open .nav a{padding:11px 2px;border-top:1px solid var(--hair)}
 .bar .nav .mcontact{display:block;color:var(--red);font-weight:600}
 .hero .label,.hero .identity{display:none}
 .hero .copy{padding-block:24px 4px}
 .hero .cta{display:flex;gap:8px;flex-wrap:wrap}
 .hero .cta .btn{flex:1 1 0;justify-content:center;text-align:center;padding:10px 12px;font-size:14px}
 .seen .wrap{padding-inline:16px}
 .outlets{flex-wrap:nowrap!important;overflow-x:auto;white-space:nowrap;scrollbar-width:none}
 .outlets::-webkit-scrollbar{display:none}
 .finder .label,.finder .ftop p,.fchips,.ftiles{display:none!important}
 .finder h2{font-size:22px;margin-bottom:10px}
 .head .lede,.picks,.gallery .g2,.speak .venues,.speak>div:last-child,.logowall,.bklaunch,.aboutphoto,.venture>p,.tr span,.trhead p{display:none!important}
 .mcap>li:nth-child(n+4){display:none!important}
 #talks-list.mcap>li:nth-child(n+2){display:none!important}
 .mmore{display:block;margin:14px 0 0;font:600 15px var(--display);color:var(--red);background:none;border:1px solid var(--red);border-radius:999px;padding:9px 18px;cursor:pointer}
 .mhide{display:none!important}
 section{padding-block:32px}
}
"""
JS = """
(function(){if(!window.matchMedia('(max-width:700px)').matches)return;var L=document.documentElement.lang.indexOf('zh')===0;
var bar=document.querySelector('header.bar'),nav=bar&&bar.querySelector('.nav');if(bar&&nav){var b=document.createElement('button');b.type='button';b.className='menubtn';b.setAttribute('aria-expanded','false');b.innerHTML='<svg viewBox="0 0 24 24"><path d="M4 7h16M4 12h16M4 17h16"/></svg>'+(L?'菜单':'Menu');var c=document.createElement('a');c.className='mcontact';c.href='#contact';c.textContent=L?'联系':'Contact';nav.appendChild(c);bar.querySelector('.wrap').appendChild(b);b.onclick=function(){var o=bar.classList.toggle('open');b.setAttribute('aria-expanded',o?'true':'false')};nav.addEventListener('click',function(e){if(e.target.closest('a')){bar.classList.remove('open');b.setAttribute('aria-expanded','false')}})}
[['.ideas',L?'展开全部观点':'All ideas',null],['#writing-list',L?'展开更多':'Show more','#wmore'],['#media-list',L?'展开更多':'Show more','.mbtns'],['#talks-list',L?'更多演讲':'More talks',null]].forEach(function(x){var u=document.querySelector(x[0]);if(!u||u.children.length<2)return;u.classList.add('mcap');var o=x[2]&&document.querySelector(x[2]);if(o)o.classList.add('mhide');var m=document.createElement('button');m.type='button';m.className='mmore';m.textContent=x[1];u.parentNode.insertBefore(m,u.nextSibling);m.onclick=function(){u.classList.remove('mcap');m.remove();if(o)o.classList.remove('mhide')}});
})();
"""
BLOCK = "<!--mobile--><style>" + CSS.strip() + "</style><script>" + JS.strip() + "</script><!--/mobile-->"
for f in ["index.html", "zh/index.html"]:
    s = open(f, encoding="utf-8").read()
    s = re.sub(r"<!--mobile-->.*?<!--/mobile-->", "", s, flags=re.S)
    s = s.replace("</body>", BLOCK + "\n</body>", 1)
    open(f, "w", encoding="utf-8").write(s)
print("ok")
