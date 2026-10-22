#!/usr/bin/env python3
"""Pre-render the Writing and Commentary lists into index.html and zh/index.html.

data/writing.json and data/media.json are the single source of truth (one entry per line).
Run this after editing either file:  python3 build.py
It rewrites the <ul id="writing-list"> and <ul id="media-list"> contents on both
pages so every entry, summary and quote is in the static HTML (readable by search
engines and AI crawlers without running JavaScript), and regenerates the
coverage structured data (<script id="ld-coverage">) on the English page.
"""
import html, json, re, sys

SITE = "https://chrisjpereira.com"
PERSON = SITE + "/#person"
WLIMIT, MLIMIT = 8, 12
MON = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]


def esc(s):
    return html.escape(s or "", quote=True)


def grab(src, name):
    i = src.index("var " + name + "=[")
    i = src.index("[", i)
    j = src.index("\n];", i)
    return json.loads(src[i:j + 2])


def has_zh(s):
    return bool(re.search(r"[一-鿿]", s or ""))


def d_en(d):
    p = d.split("-")
    return (str(int(p[2])) + " " if len(p) > 2 else "") + MON[int(p[1]) - 1] + " " + p[0]


def d_zh(d):
    p = d.split("-")
    return p[0] + "年" + str(int(p[1])) + "月" + (str(int(p[2])) + "日" if len(p) > 2 else "")


def kind(url, typ):
    if re.search(r"podcast", typ or "", re.I) or re.search(r"podcast|spotify|apple\.com/podcast", url or "", re.I):
        return "p"
    if re.match(r"^(tv|video)$", typ or "", re.I) or re.search(
            r"youtube\.com|youtu\.be|bilibili\.com|weibo\.com|dailymotion\.com|channels\.weixin", url or "", re.I):
        return "v"
    return "a"


LBL = {
    "en": {"a": "Read the full article ↗", "v": "Watch the full video ↗", "p": "Listen to the full episode ↗"},
    "zh": {"a": "阅读全文 ↗", "v": "观看完整视频 ↗", "p": "收听完整节目 ↗"},
}
UI = {
    "en": {"sum": "Short summary", "wmore": "Show more", "more": "Show all {n}",
           "wx": 'WeChat does not allow its articles to be linked from outside the app. For the full article, please <a href="#contact">contact me</a>.'},
    "zh": {"sum": "摘要", "wmore": "查看更多", "more": "查看全部 {n} 条",
           "wx": '微信公众号文章无法在站外提供链接。如需阅读全文，请<a href="#contact">与我联系</a>。'},
}


def is_quote_line(x):
    x = x.strip()
    return x[:1] in ('"', "“") or x.startswith("Paraphrased:") or x.startswith("转述：")


def attribution(m, lang):
    outlet, typ, date = m[2], (m[4] or "").lower(), m[0]
    if lang == "zh":
        return "彭家荣（Chris Pereira）· " + outlet + " · " + d_zh(date)
    verb = {"interview": "interviewed by", "tv": "speaking on", "video": "speaking on", "podcast": "speaking on",
            "speaking": "speaking at", "column": "writing in", "reprint": "writing in",
            "feature": "featured in"}.get(typ, "quoted in")
    return "Chris Pereira (彭家荣), " + verb + " " + outlet + ", " + d_en(date)


def sum_p(t):
    out = []
    for x in [l for l in t.split("\n") if l.strip()]:
        if x.startswith("EN: "):
            out.append('<p class="en">' + esc(x[4:]) + "</p>")
        else:
            out.append("<p" + (' class="zh"' if has_zh(x) else "") + ">" + esc(x) + "</p>")
    return "".join(out)


def eid(prefix, key):
    import hashlib
    return prefix + "-" + hashlib.sha1(key.encode("utf-8")).hexdigest()[:8]


def media_id(m):
    return eid("m", m[6] or (m[2] + m[3]))


def writing_id(w):
    return eid("w", w[4] or (w[1] + w[2]))


def media_li(m, i, lang):
    zh = " zh" if m[5] == "中文" else ""
    d = ('<a class="what' + zh + '" href="' + esc(m[6]) + '" target="_blank" rel="noopener">' + esc(m[3]) + "</a>") if m[6] \
        else '<span class="what' + zh + '">' + esc(m[3]) + "</span>"
    if len(m) > 8 and m[8]:
        d = '<span class="tcell">' + d + '<span class="en">' + esc(m[8]) + "</span></span>"
    q = m[7] if len(m) > 7 else ""
    b = ('<button type="button" class="sumbtn" aria-expanded="false">' + UI[lang]["sum"] + "</button>") if q else "<span></span>"
    sm = ""
    if q:
        links = ""
        if m[6]:
            links += '<a href="' + esc(m[6]) + '" target="_blank" rel="noopener">' + LBL[lang][kind(m[6], m[4])] + "</a>"
        if len(m) > 9 and m[9]:
            links += '<a href="' + esc(m[9]) + '" target="_blank" rel="noopener">' + LBL[lang][kind(m[9], "video")] + "</a>"
        attr = ('<p class="attr">' + esc(attribution(m, lang)) + "</p>") if any(is_quote_line(l) for l in q.split("\n")) else ""
        pic = ""
        if len(m) > 10 and m[10]:
            pic = '<img class="mthumb" src="' + ("" if lang == "en" else "../") + esc(m[10]) + '" alt="' + esc(("Chris Pereira interviewed by " + ({"第一财经": "Yicai"}.get(m[2], m[2]))) if lang == "en" else ("彭家荣接受" + m[2] + "采访")) + '" width="900" height="704" loading="lazy">'
        sm = '<div class="sum" hidden>' + pic + sum_p(q) + attr + links + "</div>"
    date = d_en(m[0]) if lang == "en" else d_zh(m[0])
    cls = ' class="x"' if i >= MLIMIT else ""
    return ("<li" + cls + ' id="' + media_id(m) + '"><time datetime="' + m[0] + '">' + date + '</time><span class="outlet" title="' + esc(m[2]) + '">'
            + esc(m[2]) + "</span>" + d + b + sm + "</li>")


def src_label(s, lang):
    if lang == "zh":
        return {"WeChat": "公众号", "LinkedIn": "领英", "Qizan": "奇赞"}.get(s, s)
    return s


def writing_li(w, i, lang):
    zh = " zh" if has_zh(w[2]) else ""
    t = ('<a class="what' + zh + '" href="' + esc(w[4]) + '" target="_blank" rel="noopener">' + esc(w[2]) + "</a>") if w[4] \
        else '<span class="what' + zh + '">' + esc(w[2]) + "</span>"
    if len(w) > 6 and w[6]:
        t = '<span class="tcell">' + t + '<span class="en">' + esc(w[6]) + "</span></span>"
    b = ('<button type="button" class="sumbtn" aria-expanded="false">' + UI[lang]["sum"] + "</button>") if w[5] else "<span></span>"
    sm = ""
    if w[5]:
        tail = ('<a href="' + esc(w[4]) + '" target="_blank" rel="noopener">' + LBL[lang]["a"] + "</a>") if w[4] \
            else ('<p class="wxnote">' + UI[lang]["wx"] + "</p>" if w[1] == "WeChat" else "")
        sm = '<div class="sum" hidden><p>' + esc(w[5]) + "</p>" + tail + "</div>"
    date = d_en(w[0]) if lang == "en" else d_zh(w[0])
    cls = ' class="x"' if i >= WLIMIT else ""
    return ("<li" + cls + ' id="' + writing_id(w) + '"><time datetime="' + w[0] + '">' + date + '</time><span class="src" title="' + esc(w[1]) + '">'
            + esc(src_label(w[1], lang)) + "</span>" + t + '<span class="dek">' + esc(w[3]) + "</span>" + b + sm + "</li>")


def put_list(page, ul_id, items_html):
    pat = re.compile(r'(<ul class="[^"]*" id="' + ul_id + r'">)(.*?)(</ul>)', re.S)
    assert len(pat.findall(page)) == 1, ul_id
    return pat.sub(lambda mo: mo.group(1) + "\n" + "\n".join(items_html) + "\n      " + mo.group(3), page)


def put_btn(page, btn_id, text, hide):
    pat = re.compile(r'<button class="btn" type="button" id="' + btn_id + r'"[^>]*>[^<]*</button>')
    assert len(pat.findall(page)) == 1, btn_id
    return pat.sub('<button class="btn" type="button" id="' + btn_id + '"' + (" hidden" if hide else "") + ">" + text + "</button>", page)


def coverage_ld(MEDIA, WRITING):
    graph, subj = [], []
    for m in MEDIA:
        url = m[6]
        if not url:
            continue
        k = kind(url, m[4])
        node = {"@type": "CreativeWork", "@id": url, "url": url, "name": m[3],
                "genre": {"v": "Video", "p": "Podcast"}.get(k, "News coverage"),
                "datePublished": m[0], "inLanguage": "zh" if m[5] == "中文" else ("en" if m[5] == "EN" else m[5].lower()),
                "publisher": {"@type": "Organization", "name": m[2]}, "mentions": {"@id": PERSON}}
        if len(m) > 8 and m[8]:
            node["alternativeHeadline"] = m[8]
        graph.append(node)
        subj.append({"@id": url})
        for line in (m[7] or "").split("\n"):
            s = line.strip()
            if s[:1] in ('"', "“"):
                graph.append({"@type": "Quotation", "text": s.strip('"“”'), "creator": {"@id": PERSON}, "isPartOf": {"@id": url}})
    for w in WRITING:
        if not w[4]:
            continue
        node = {"@type": "CreativeWork", "@id": w[4], "url": w[4], "name": w[2], "genre": "Article",
                "datePublished": w[0], "author": {"@id": PERSON}, "inLanguage": "zh" if has_zh(w[2]) else "en"}
        if w[5]:
            node["abstract"] = w[5]
        graph.append(node)
    graph.insert(0, {"@id": PERSON, "subjectOf": subj})
    return json.dumps({"@context": "https://schema.org", "@graph": graph}, ensure_ascii=False, separators=(",", ":"))


TOGGLE_JS = {
    "en": ('function sumToggle(e){var t=e.target.closest(".sumbtn");if(!t)return;var sm=t.parentNode.querySelector(".sum"),open=sm.hidden;'
           'sm.hidden=!open;t.setAttribute("aria-expanded",open?"true":"false");t.textContent=open?"Hide summary":"Short summary"}',
           "Show less"),
    "zh": ('function sumToggle(e){var t=e.target.closest(".sumbtn");if(!t)return;var sm=t.parentNode.querySelector(".sum"),open=sm.hidden;'
           'sm.hidden=!open;t.setAttribute("aria-expanded",open?"true":"false");t.textContent=open?"收起摘要":"摘要"}',
           "收起"),
}


OUTLET_MAP = {"Financial Times": ["Financial Times"], "金融时报": ["Financial Times"],
    "Wall Street Journal": ["Wall Street Journal"], "华尔街日报": ["Wall Street Journal"],
    "BBC": ["BBC", "BBC Global News"], "Bloomberg": ["Bloomberg"], "彭博社": ["Bloomberg"],
    "Reuters": ["Reuters"], "路透社": ["Reuters"], "CNBC": ["CNBC"], "Nikkei Asia": ["Nikkei Asia"], "日经亚洲": ["Nikkei Asia"],
    "SCMP": ["SCMP"], "南华早报": ["SCMP"], "CCTV": ["CCTV 央视网", "CCTV-13《新闻直播间》", "CCTV-13《朝闻天下》"], "央视": ["CCTV 央视网", "CCTV-13《新闻直播间》", "CCTV-13《朝闻天下》"],
    "CGTN": ["CGTN", "CGTN Europe", "CGTN, The Heat", "CGTN Global Business"], "Phoenix TV": ["凤凰卫视"], "凤凰卫视": ["凤凰卫视"],
    "Xinhua": ["新华社", "Xinhua", "新华网", "新华国际"], "新华社": ["新华社", "Xinhua", "新华网", "新华国际"]}


def link_highlights(page, MEDIA, lang):
    def latest(names):
        for m in MEDIA:
            if m[2] in names:
                return "#" + media_id(m)
        return "#media"
    def outlets(mo):
        names = re.findall(r"<(?:span|a)[^>]*>([^<]+)</(?:span|a)>", mo.group(1))
        return '<div class="outlets">' + "".join('<a href="' + latest(OUTLET_MAP.get(n, [n])) + '">' + esc(n) + "</a>" for n in names) + "</div>"
    page = re.sub(r'<div class="outlets">(.*?)</div>', outlets, page, count=1, flags=re.S)
    forbes = next((m for m in MEDIA if "1787878427776611768" in (m[6] or "")), None)
    work = "https://www.impact5r.com/work/" if lang == "en" else "https://www.impact5r.com/zh/work/"
    targets = ['href="#about"', 'href="' + ("#" + media_id(forbes) if forbes else "#about") + '"', 'href="#books"', 'href="' + work + '" target="_blank" rel="noopener"']
    blocks = re.findall(r'<(?:div|a) class="f"[^>]*>.*?</(?:div|a)>(?=\s*(?:<(?:div|a) class="f"|</div>))', page, flags=re.S)
    for b, t in zip(blocks[:4], targets):
        inner = re.sub(r'^<(?:div|a) class="f"[^>]*>|</(?:div|a)>$', "", b)
        page = page.replace(b, '<a class="f" ' + t + ">" + inner + "</a>", 1)
    page = page.replace('<div class="books">', '<div class="books" id="books">', 1)
    return page


def lists_js(lang, wmore, more):
    fn, less = TOGGLE_JS[lang]
    return ("<script>/* lists are pre-rendered by build.py */\n(function(){" + fn +
            'function wire(ul,btn,sec,label){ul=document.getElementById(ul);btn=document.getElementById(btn);ul.addEventListener("click",sumToggle);'
            'if(!btn)return;btn.addEventListener("click",function(){var on=ul.classList.toggle("all");btn.textContent=on?"' + less + '":label;'
            'if(!on)document.getElementById(sec).scrollIntoView({behavior:"smooth"})})}'
            'wire("writing-list","wmore","writing",' + json.dumps(wmore, ensure_ascii=False) + ');'
            'wire("media-list","more","media",' + json.dumps(more, ensure_ascii=False) + ");"
            'function deep(){var h=location.hash.slice(1);if(!/^[mw]-[0-9a-f]{8}$/.test(h))return;var li=document.getElementById(h);if(!li)return;'
            'var ul=li.parentNode;if(li.classList.contains("x")&&!ul.classList.contains("all")){ul.classList.add("all");var b=document.getElementById(ul.id==="media-list"?"more":"wmore");if(b)b.textContent="' + less + '"}'
            'var sb=li.querySelector(".sumbtn"),sm=li.querySelector(".sum");if(sb&&sm&&sm.hidden)sb.click();'
            'li.classList.add("hit");setTimeout(function(){li.scrollIntoView({block:"center"})},60);setTimeout(function(){li.classList.remove("hit")},2600)}'
            'deep();window.addEventListener("hashchange",deep);'
            "})();\n</script>")


def main():
    en = open("index.html", encoding="utf-8").read()
    zh = open("zh/index.html", encoding="utf-8").read()
    WRITING = json.load(open("data/writing.json", encoding="utf-8"))
    MEDIA = json.load(open("data/media.json", encoding="utf-8"))
    for page_name, lang in (("en", "en"), ("zh", "zh")):
        page = en if lang == "en" else zh
        page = put_list(page, "writing-list", [writing_li(w, i, lang) for i, w in enumerate(WRITING)])
        page = put_list(page, "media-list", [media_li(m, i, lang) for i, m in enumerate(MEDIA)])
        wmore, more = UI[lang]["wmore"], UI[lang]["more"].format(n=len(MEDIA))
        page = put_btn(page, "wmore", wmore, len(WRITING) <= WLIMIT)
        page = put_btn(page, "more", more, len(MEDIA) <= MLIMIT)
        page = link_highlights(page, MEDIA, lang)
        page = re.sub(r"<script>/\* lists are pre-rendered by build\.py \*/.*?</script>", lambda _: lists_js(lang, wmore, more), page, flags=re.S)
        if lang == "en":
            ld = '<script type="application/ld+json" id="ld-coverage">' + coverage_ld(MEDIA, WRITING) + "</script>"
            page = re.sub(r'<script type="application/ld\+json" id="ld-coverage">.*?</script>', lambda _: ld, page, flags=re.S)
            en = page
        else:
            zh = page
    open("index.html", "w", encoding="utf-8").write(en)
    open("zh/index.html", "w", encoding="utf-8").write(zh)
    print("built: writing", len(WRITING), "media", len(MEDIA))


if __name__ == "__main__":
    main()


# ---------------------------------------------------------------- quotes page
OUTLET_EN = {"美讯彭家荣": "WeChat 美讯彭家荣", "新浪财经": "Sina Finance 新浪财经", "福布斯中国": "Forbes China 福布斯中国", "36氪（授权转载）": "36Kr 36氪",
             "新华网": "Xinhua 新华网", "亿邦动力": "Ebrun 亿邦动力", "国际在线": "CRI Online 国际在线",
             "观察者网": "Guancha 观察者网", "深圳特区报": "Shenzhen Special Zone Daily 深圳特区报",
             "姐夫李": "姐夫李 (WeChat)", "深圳卫视": "Shenzhen TV 深圳卫视", "搜狐": "Sohu 搜狐", "虎嗅": "Huxiu 虎嗅"}


def quote_attr(q):
    outlet = OUTLET_EN.get(q["outlet"], q["outlet"])
    t = (q.get("type") or "").lower()
    verb = {"interview": "interviewed by", "tv": "speaking on", "video": "speaking on", "podcast": "speaking on",
            "speaking": "speaking at", "column": "writing in", "reprint": "writing in", "feature": "featured in"}.get(t, "quoted in")
    return "Chris Pereira, " + verb + " " + outlet + ", " + d_en(q["date"])


QUOTES_PAGE = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<title>Chris Pereira on China, Trust and Global Brands | Quotes</title>
<meta name="description" content="Selected quotes from Chris Pereira (彭家荣), founder and CEO of iMpact and author of Trust 《信任》, on trust, Chinese brands going global, localization, Shenzhen, Europe and China, and tariffs. Each quote links to its original source.">
<meta name="robots" content="__ROBOTS__">
<meta name="theme-color" content="#A40706">
<link rel="canonical" href="https://chrisjpereira.com/quotes/">
<meta property="og:type" content="website">
<meta property="og:title" content="Chris Pereira on China, trust and global brands">
<meta property="og:description" content="Selected quotes from Chris Pereira (彭家荣), with links to the original sources.">
<meta property="og:image" content="https://chrisjpereira.com/img/press-portrait.jpg">
<meta property="og:url" content="https://chrisjpereira.com/quotes/">
<link rel="icon" href="/favicon.ico" sizes="any">
<link rel="apple-touch-icon" sizes="180x180" href="/apple-touch-icon.png">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Jost:wght@400;500;600;700&family=Playfair+Display:wght@600;700&family=Tinos:ital,wght@0,400;0,700;1,400&display=swap">
<style>
:root{--paper:#F6F2E9;--surface:#FFFFFF;--ink:#151313;--muted:#626060;--hair:#E2DCD0;--red:#A40706;--red-deep:#7A0504;
--display:"Jost","Avenir Next","Helvetica Neue",Arial,sans-serif;--body:"Times New Roman","Tinos",Times,serif;--head:"Playfair Display","Times New Roman",Georgia,serif}
*{box-sizing:border-box}
body{margin:0;background:var(--paper);color:var(--ink);font-family:var(--body);font-size:17px;line-height:1.6}
a{color:var(--red);text-underline-offset:3px}
.wrap{max-width:1080px;margin:0 auto;padding:0 24px}
.bar{position:sticky;top:0;z-index:5;background:rgba(246,242,233,.94);backdrop-filter:blur(8px);border-bottom:1px solid var(--hair)}
.bar .wrap{display:flex;align-items:center;gap:18px;min-height:64px}
.mark{display:flex;align-items:center;gap:10px;font-family:var(--display);font-weight:600;font-size:18px;color:var(--ink);text-decoration:none;margin-right:auto}
.seal{background:var(--red);color:#fff;font-size:14px;padding:4px 7px;border-radius:3px}
.nav{display:flex;gap:22px}.nav a{font-family:var(--display);font-weight:500;font-size:15px;color:var(--ink);text-decoration:none}.nav a[aria-current]{color:var(--red)}
.btn{display:inline-flex;align-items:center;font-family:var(--display);font-weight:600;font-size:15px;padding:11px 20px;border-radius:999px;text-decoration:none;border:1.5px solid var(--red);background:var(--red);color:#fff}
.btn:hover{background:var(--red-deep);border-color:var(--red-deep)}
.label{font-family:var(--display);font-size:12.5px;font-weight:600;letter-spacing:.16em;text-transform:uppercase;color:var(--red)}
h1,h2{font-family:var(--head);margin:0;font-weight:700;letter-spacing:-.01em;text-wrap:balance}
h1{font-size:clamp(30px,4vw,42px);line-height:1.08;margin:8px 0 0}
h2{font-size:clamp(22px,2.4vw,26px);font-weight:600;line-height:1.15}
.intro{padding-top:40px;padding-bottom:6px}
.ihead{display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1fr);gap:12px 40px;align-items:end}
.lede{margin:0;max-width:56ch;color:var(--muted);font-size:16.5px;line-height:1.55}
.toc{position:sticky;top:64px;z-index:4;background:rgba(246,242,233,.96);backdrop-filter:blur(8px);margin:22px 0 0;border-top:1px solid var(--ink);border-bottom:1px solid var(--hair)}
.toc ul{display:flex;flex-wrap:wrap;gap:4px 22px;list-style:none;margin:0;padding:9px 0;scrollbar-width:none}
.toc ul::-webkit-scrollbar{display:none}
.toc a{font-family:var(--display);font-size:13.5px;font-weight:500;color:var(--ink);text-decoration:none;white-space:nowrap;padding:3px 0;border-bottom:1px solid transparent}
.toc a span{color:var(--muted);font-size:12px;margin-left:2px}
.toc a:hover{color:var(--red);border-bottom-color:var(--red)}
section.topic{padding:26px 0 22px;scroll-margin-top:112px}
.qs{list-style:none;margin:12px 0 0;padding:0;border-top:1px solid var(--ink)}
.qs li{display:grid;grid-template-columns:80px 196px minmax(0,1fr) 70px;gap:0 16px;padding:9px 0;border-bottom:1px solid var(--hair);align-items:baseline}
.qs li:nth-child(even){background:rgba(0,0,0,.018)}
.qs:not(.all)>li.x{display:none}
.qs time{font-family:var(--display);font-size:13.5px;color:var(--muted);white-space:nowrap}
.qs .outlet{font-family:var(--display);font-weight:600;font-size:14.5px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.qs blockquote{margin:0;font-size:16.5px;line-height:1.45}
.qs blockquote p{margin:0;display:-webkit-box;-webkit-line-clamp:1;-webkit-box-orient:vertical;overflow:hidden}
.qs li.open blockquote p{-webkit-line-clamp:unset;display:block}
.qs .more,.showall{font-family:var(--display);font-size:12.5px;font-weight:600;color:var(--red);background:transparent;border:1px solid var(--red);border-radius:999px;padding:3px 10px;cursor:pointer;justify-self:end;white-space:nowrap}
.qs .more:hover,.qs .more[aria-expanded="true"],.showall:hover{background:var(--red);color:#fff}
.qs .det{grid-column:3/5;margin:8px 0 4px;padding:10px 14px;background:var(--surface);border-left:3px solid var(--red);font-size:15px}
.qs .det p{margin:0 0 6px}.qs .det p:last-child{margin:0}
.qs .orig{font-family:"Noto Sans SC",system-ui,sans-serif;font-size:14.5px;color:var(--muted)}
.qs .attr{font-family:var(--display);font-size:13.5px;color:var(--muted)}
.qs .det a{font-family:var(--display);font-weight:600;font-size:13.5px;text-decoration:none}
.showall{margin-top:12px;font-size:13.5px;padding:6px 14px}
.note{font-family:var(--display);font-size:12.5px;color:var(--muted)}
.cta{padding-top:36px;padding-bottom:56px;margin-top:12px;border-top:1px solid var(--ink)}
.cta p{max-width:60ch;color:var(--muted);margin:8px 0 18px}
footer{background:var(--red-deep);color:#fff}
footer .wrap{padding-top:28px;padding-bottom:28px;display:flex;justify-content:space-between;gap:10px 24px;flex-wrap:wrap;font-family:var(--display);font-size:14px}
@media (max-width:760px){.wrap{padding:0 16px}.nav{display:none}.ihead{grid-template-columns:1fr}.toc{margin-left:-16px;margin-right:-16px;padding:0 16px}.toc ul{flex-wrap:nowrap;overflow-x:auto}.qs li{grid-template-columns:auto minmax(0,1fr) auto;gap:2px 10px}.qs blockquote{grid-column:1/4;order:3;font-size:16px}.qs .more{grid-column:3;grid-row:1}.qs .det{grid-column:1/4;order:4}}
</style>
<script type="application/ld+json">__LD__</script>
</head>
<body>
<header class="bar"><div class="wrap">
  <a class="mark" href="/"><span class="seal" lang="zh-Hans">彭家荣</span>Chris Pereira</a>
  <nav class="nav" aria-label="Sections"><a href="/#writing">Writing</a><a href="/#media">Commentary</a><a href="/#speaking">Speaking</a><a href="/#training">Training</a><a href="/#about">About</a></nav>
  <a class="btn" href="/#contact">Contact</a>
</div></header>
<main>
  <div class="wrap intro">
    <div class="ihead">
      <div><span class="label">Quotes</span><h1>Straight talk on China, trust and global brands</h1></div>
      <p class="lede">Selected quotes from Chris Pereira's interviews, talks and op-eds, each linked to the original source. Journalists are welcome to cite them with attribution.</p>
    </div>
    <nav class="toc" aria-label="Themes"><ul>__TOC__</ul></nav>
  </div>
__SECTIONS__
  <div class="wrap cta">
    <h2>Need a sharp take on China, fast?</h2>
    <p>Chris comments on Chinese brands going global, trust and localization, Shenzhen and consumer technology, and US, Europe and China business relations, in English and Mandarin.</p>
    <a class="btn" href="/#contact">Contact Chris</a>
  </div>
</main>
<footer><div class="wrap"><span>Chris Pereira <span lang="zh-Hans">彭家荣</span></span><span>Updated October 2026</span></div></footer>
<script>document.addEventListener("click",function(e){var m=e.target.closest(".more");if(m){var li=m.parentNode,d=li.querySelector(".det"),o=d.hidden;d.hidden=!o;li.classList.toggle("open",o);m.setAttribute("aria-expanded",o?"true":"false");m.textContent=o?"Less":"More";return}var b=e.target.closest(".showall");if(b){var ul=b.previousElementSibling,on=ul.classList.toggle("all");b.textContent=on?"Show less":b.dataset.label;if(!on)b.closest("section").scrollIntoView({behavior:"smooth"})}});</script>
</body>
</html>
"""


def norm_url(u):
    return re.sub(r"[?#].*$", "", (u or "").strip()).rstrip("/").lower()


def find_entry(q, MEDIA, WRITING):
    u = norm_url(q.get("url"))
    if u:
        for w in WRITING:
            if w[4] and norm_url(w[4]) == u:
                return "/#" + writing_id(w), "See it in Writing"
        for m in MEDIA:
            if (m[6] and norm_url(m[6]) == u) or (len(m) > 9 and m[9] and norm_url(m[9]) == u):
                return "/#" + media_id(m), "See it in Commentary"
    cands = [m for m in MEDIA if m[0][:7] == q["date"][:7] and (m[2] == q["outlet"] or OUTLET_EN.get(m[2], m[2]) == OUTLET_EN.get(q["outlet"], q["outlet"]))]
    if cands:
        best = next((m for m in cands if q["text"][:25].lower() in (m[7] if len(m) > 7 else "").lower()), cands[0])
        return "/#" + media_id(best), "See it in Commentary"
    return None, None


def build_quotes(QUOTES, robots):
    MEDIA = json.load(open("data/media.json", encoding="utf-8"))
    WRITING = json.load(open("data/writing.json", encoding="utf-8"))
    unmatched = []
    toc, secs, graph = [], [], []
    page = SITE + "/quotes/"
    for s in QUOTES:
        toc.append('<li><a href="#' + s["key"] + '">' + esc(s["title"]) + ' <span>' + str(len(s["quotes"])) + '</span></a></li>')
        cards = []
        for q in s["quotes"]:
            src = ('<a href="' + esc(q["url"]) + '" target="_blank" rel="noopener">Read the source ↗</a>') if q.get("url") else ""
            href, lbl = find_entry(q, MEDIA, WRITING)
            if href:
                src = '<a href="' + href + '">' + lbl + " →</a>" + (" · " + src if src else "")
            else:
                unmatched.append(q["outlet"] + " " + q["date"] + " " + q["text"][:40])
            orig = ""
            if q.get("lang") == "zh":
                orig = '<p class="orig" lang="zh-Hans">' + esc(q["original"]) + '</p><p class="note">Translated from the Chinese original above</p>'
            hide = ' class="x"' if len(cards) >= 4 else ""
            outlet = OUTLET_EN.get(q["outlet"], q["outlet"])
            cards.append('<li' + hide + '><time datetime="' + esc(q["date"]) + '">' + esc(d_en(q["date"])) + '</time>'
                         '<span class="outlet" title="' + esc(outlet) + '">' + esc(outlet) + '</span>'
                         '<blockquote' + (' cite="' + esc(q["url"]) + '"' if q.get("url") else "") + '><p>“' + esc(q["text"]) + '”</p></blockquote>'
                         '<button class="more" type="button" aria-expanded="false">More</button>'
                         '<div class="det" hidden>' + (('<p class="ctx">' + esc(q["context"]) + '</p>') if q.get("context") else "") + orig + '<p class="attr">' + esc(quote_attr(q)) + '</p>' + (src and '<p>' + src + '</p>') + '</div></li>')
            node = {"@type": "Quotation", "text": q["text"], "creator": {"@id": PERSON}, "about": s.get("topic", s["title"]), "dateCreated": q["date"]}
            if q.get("url"):
                node["isPartOf"] = {"@type": "CreativeWork", "@id": q["url"], "url": q["url"],
                                    "publisher": {"@type": "Organization", "name": OUTLET_EN.get(q["outlet"], q["outlet"])}}
            else:
                node["isPartOf"] = {"@type": "CreativeWork", "name": OUTLET_EN.get(q["outlet"], q["outlet"]), "dateCreated": q["date"], "creator": {"@id": PERSON}}
            if q.get("lang") == "zh":
                node["inLanguage"] = "en"
                node["translationOfWork"] = {"@type": "Quotation", "text": q["original"], "inLanguage": "zh"}
            graph.append(node)
        n = len(s["quotes"])
        allbtn = ('<button class="showall" type="button" data-label="Show all ' + str(n) + '">Show all ' + str(n) + '</button>') if n > 4 else ""
        secs.append('  <section class="topic" id="' + s["key"] + '"><div class="wrap"><h2>' + esc(s["title"]) +
                    '</h2><ul class="qs">' + "".join(cards) + "</ul>" + allbtn + "</div></section>")
    ld = {"@context": "https://schema.org", "@graph": [
        {"@type": "WebPage", "@id": page, "url": page, "name": "Chris Pereira on China, trust and global brands",
         "about": {"@id": PERSON}, "mainEntity": {"@id": page + "#quotes"}, "inLanguage": "en"},
        {"@type": "ItemList", "@id": page + "#quotes", "itemListElement": [{"@type": "ListItem", "position": i + 1, "item": g} for i, g in enumerate(graph)]},
        {"@type": "Person", "@id": PERSON, "name": "Chris Pereira", "alternateName": "彭家荣", "url": SITE + "/"}]}
    html_out = (QUOTES_PAGE.replace("__ROBOTS__", robots).replace("__TOC__", "".join(toc)).replace("__SECTIONS__", "\n".join(secs))
                .replace("__LD__", json.dumps(ld, ensure_ascii=False, separators=(",", ":"))))
    import os
    os.makedirs("quotes", exist_ok=True)
    open("quotes/index.html", "w", encoding="utf-8").write(html_out)
    print("quotes page:", sum(len(s["quotes"]) for s in QUOTES), "quotes,", robots)
    for x in unmatched: print("  no entry:", x)


if __name__ == "__main__":
    import os
    if os.path.exists("data/quotes.json"):
        cfg = json.load(open("data/quotes.json", encoding="utf-8"))
        build_quotes(cfg, "noindex,follow" if not os.path.exists("data/quotes.published") else "index,follow,max-snippet:-1")
