"""Simpler homepage (all widths) for index.html and zh/index.html. Run after mobile.py.
Nothing is removed from the HTML: long blocks open short and expand in place.
- finder: one slim search row, shortcut tiles become a link row
- ideas: titles only, click a title to open the argument
- writing / commentary: 5 and 6 latest rows, the existing button shows the rest
- speaking: judging, past stages, logo wall and training fold under one-line headings
- about: current roles open on click
"""
import re
CSS = """
.finder .label,.finder .ftop p{display:none}
.finder .wrap{padding-block:18px 18px;gap:12px}
.ftiles{display:flex;flex-wrap:wrap;gap:6px 26px}
.ftiles a{display:inline;border:0;padding:0;background:none}
.ftiles b{font-size:14.5px}
.ftiles span{display:none}
.ideas.acc li{padding:15px 0;cursor:pointer}
.ideas.acc h3{font-size:20px;display:flex;justify-content:space-between;gap:14px;align-items:baseline}
.ideas.acc h3::after{content:"+";font:400 22px var(--display);color:var(--red);flex:none;line-height:1}
.ideas.acc li.sx h3::after{content:"\\2212"}
.ideas.acc li:not(.sx) p{display:none}
.ideas.acc li:hover h3{color:var(--red)}
.ideas.acc .n{display:none}
.ideas.acc li{grid-template-columns:minmax(0,1fr)}
.ideas.acc h3{text-wrap:wrap}
.ideas.acc h3>*{text-wrap:wrap}
.ideas.acc .imore{display:none!important}
.sall{font:600 14px var(--display);color:var(--red);background:none;border:0;padding:0;margin:12px 0 0;cursor:pointer;text-decoration:underline;text-underline-offset:3px}
.scap>li:nth-child(n+6){display:none!important}
#media-list.scap>li:nth-child(n+7){display:none!important}
.tlist p{display:-webkit-box;-webkit-line-clamp:3;-webkit-box-orient:vertical;overflow:hidden;cursor:pointer}
.tlist li.sx p{display:block}
.speak.one{grid-template-columns:1fr;gap:0}
.speak.one .topics{margin-bottom:0}
.folds{margin-top:28px;border-top:1px solid var(--ink)}
.fold{border-bottom:1px solid var(--hair)}
.foldh{display:flex;justify-content:space-between;align-items:baseline;gap:16px;width:100%;padding:15px 0;background:none;border:0;cursor:pointer;text-align:left;font:600 18px var(--display);color:var(--ink)}
.foldh small{font:400 14.5px var(--display);color:var(--muted);margin-left:12px}
.foldh::after{content:"+";font:400 22px var(--display);color:var(--red);flex:none;line-height:1}
.fold.sx>.foldh::after{content:"\\2212"}
.foldh:hover{color:var(--red)}
.fold:not(.sx)>.foldb{display:none}
.foldb{padding:2px 0 22px}
.foldb>.label,.foldb .logowall>.label,.foldb .trhead h3,.foldb>dl.venues>dt:first-child{display:none}
.foldb .logowall,.foldb .training{margin:0;padding:0;border:0}
.foldb .logowall ul{margin-top:0}
.foldb .venues{margin-top:0}
.foldb .trhead p{margin:0}
.venture.vacc{cursor:pointer;padding:15px 20px}
.venture.vacc:not(.sx)>p{display:none}
.venture.vacc{position:relative;padding-right:46px}
.venture.vacc b::after{content:"+";font:400 20px var(--display);color:var(--red);position:absolute;right:20px;top:50%;transform:translateY(-50%);line-height:1}
.venture.vacc.sx b::after{content:"\\2212"}
@media (max-width:700px){.ideas.acc h3{font-size:18px}.foldh{font-size:16.5px}.foldh small{display:none}.ftiles{display:none}}
"""
JS = """
(function(){var L=document.documentElement.lang.indexOf('zh')===0,M=window.matchMedia('(max-width:700px)').matches,$=function(s,r){return (r||document).querySelector(s)};
function key(el,fn){el.setAttribute('tabindex','0');el.addEventListener('keydown',function(e){if(e.key==='Enter'||e.key===' '){if(e.target.closest('a,button')&&e.target!==el)return;e.preventDefault();fn()}})}
var ideas=$('ol.ideas');if(ideas){ideas.classList.add('acc');var lis=[].slice.call(ideas.children);lis.forEach(function(li){var t=function(){li.classList.toggle('sx')};li.addEventListener('click',function(e){if(e.target.closest('a'))return;t()});key(li,t)});
 var b=document.createElement('button');b.type='button';b.className='sall';var all=false;var lab=function(){b.textContent=all?(L?'收起全部':'Close all'):(L?'展开全部观点':'Open all ideas')};lab();b.onclick=function(){all=!all;lis.forEach(function(li){li.classList.toggle('sx',all)});lab()};ideas.parentNode.insertBefore(b,ideas.nextSibling)}
if(!M){[['#writing-list','#wmore'],['#media-list','#more']].forEach(function(x){var u=$(x[0]),m=$(x[1]);if(!u||!m)return;u.classList.add('scap');m.addEventListener('click',function(){u.classList.remove('scap')},true)})}
[].forEach.call(document.querySelectorAll('.tlist li'),function(li){var p=$('p',li);if(p)p.addEventListener('click',function(){li.classList.toggle('sx')})});
function fold(el,title,sub){if(!el)return null;var f=document.createElement('div');f.className='fold';var h=document.createElement('button');h.type='button';h.className='foldh';h.setAttribute('aria-expanded','false');var s=document.createElement('span');s.textContent=title;if(sub){var sm=document.createElement('small');sm.textContent=sub;s.appendChild(sm)}h.appendChild(s);var b=document.createElement('div');b.className='foldb';b.appendChild(el);f.appendChild(h);f.appendChild(b);h.onclick=function(){var o=f.classList.toggle('sx');h.setAttribute('aria-expanded',o?'true':'false')};return f}
var sp=$('#speaking .speak');if(sp&&sp.children.length>1){var left=sp.children[0],right=sp.children[1],box=document.createElement('div');box.className='folds';
 var items=[[ $('dl.venues',left), L?'评审与导师':'Judging and mentorship', L?'CES 创新奖评审、Plug and Play、港科大、西交利物浦':'CES Innovation Awards, Plug and Play, HKUST, XJTLU'],
  [right, L?'过往讲台与顾问职务':'Past stages and advisory roles', L?'哈佛、耶鲁、沃顿、WTO、APEC、Web Summit':'Harvard, Yale, Wharton, WTO, APEC, Web Summit'],
  [$('#speaking .logowall'), L?'合作讲台、院校与客户':'Stages, schools and clients', L?'16 家机构':'16 logos'],
  [$('#training'), L?'企业培训':'Corporate training', L?'7 门课程，半天或全天':'7 sessions, half-day or full-day']];
 items.forEach(function(x){var f=fold(x[0],x[1],x[2]);if(f)box.appendChild(f)});sp.classList.add('one');sp.parentNode.insertBefore(box,sp.nextSibling)}
[].forEach.call(document.querySelectorAll('.ventures .venture'),function(v){v.classList.add('vacc');var t=function(){v.classList.toggle('sx')};v.addEventListener('click',function(e){if(e.target.closest('a'))return;t()});key(v,t)});
function reveal(hash){if(!hash||hash.length<2)return;var el;try{el=document.getElementById(decodeURIComponent(hash.slice(1)))}catch(e){}if(!el)return;var p=el,hit=false;while(p&&p!==document.body){if(p.classList){if(p.classList.contains('fold')&&!p.classList.contains('sx')){p.classList.add('sx');var h=p.querySelector('.foldh');if(h)h.setAttribute('aria-expanded','true');hit=true}if(p.classList.contains('scap')){p.classList.remove('scap');hit=true}}p=p.parentNode}
 if(el.matches&&el.matches('.ideas.acc li,.venture.vacc'))el.classList.add('sx');if(hit)setTimeout(function(){el.scrollIntoView({block:'start'})},0)}
document.addEventListener('click',function(e){var a=e.target.closest&&e.target.closest('a[href^="#"]');if(a)reveal(a.getAttribute('href'))},true);
var fr=$('#fres');if(fr)fr.addEventListener('click',function(e){var a=e.target.closest('a[data-id]');if(a&&a.dataset.id.indexOf('idea-')===0){var li=document.getElementById(a.dataset.id);if(li)li.classList.add('sx')}});
window.addEventListener('hashchange',function(){reveal(location.hash)});reveal(location.hash);
})();
"""
BLOCK = "<!--simple--><style>" + CSS.strip() + "</style><script>" + JS.strip() + "</script><!--/simple-->"
for f in ["index.html", "zh/index.html"]:
    s = open(f, encoding="utf-8").read()
    s = re.sub(r"<!--simple-->.*?<!--/simple-->\n?", "", s, flags=re.S)
    s = s.replace("</body>", BLOCK + "\n</body>", 1)
    open(f, "w", encoding="utf-8").write(s)
print("simple ok")
