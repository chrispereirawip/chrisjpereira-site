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
        sm = '<div class="sum" hidden>' + sum_p(q) + attr + links + "</div>"
    date = d_en(m[0]) if lang == "en" else d_zh(m[0])
    cls = ' class="x"' if i >= MLIMIT else ""
    return ("<li" + cls + '><time datetime="' + m[0] + '">' + date + '</time><span class="outlet" title="' + esc(m[2]) + '">'
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
    return ("<li" + cls + '><time datetime="' + w[0] + '">' + date + '</time><span class="src" title="' + esc(w[1]) + '">'
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


def lists_js(lang, wmore, more):
    fn, less = TOGGLE_JS[lang]
    return ("<script>/* lists are pre-rendered by build.py */\n(function(){" + fn +
            'function wire(ul,btn,sec,label){ul=document.getElementById(ul);btn=document.getElementById(btn);ul.addEventListener("click",sumToggle);'
            'if(!btn)return;btn.addEventListener("click",function(){var on=ul.classList.toggle("all");btn.textContent=on?"' + less + '":label;'
            'if(!on)document.getElementById(sec).scrollIntoView({behavior:"smooth"})})}'
            'wire("writing-list","wmore","writing",' + json.dumps(wmore, ensure_ascii=False) + ');'
            'wire("media-list","more","media",' + json.dumps(more, ensure_ascii=False) + ");})();\n</script>")


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
