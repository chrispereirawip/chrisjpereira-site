"""Ideas page: /ideas/ and /zh/ideas/ (Chris, 25 Nov 2026: Ideas is a separate page, not on the homepage).

The content lives in data/ideas_en.html and data/ideas_zh.html (one <section id="ideas">).
The page shell (head styles, header, footer, phone layout) is taken from the built homepage,
so the page always matches the rest of the site. Run after the homepages are built.
"""
import os
import re

SITE = "https://chrisjpereira.com"
PAGES = {
    "en": dict(home="index.html", data="data/ideas_en.html", out="ideas/index.html", base="/", path="/ideas/",
               title="Ideas | Chris Pereira 彭家荣",
               desc="What China taught me: Chris Pereira's main arguments on China, the West, competition and trust."),
    "zh": dict(home="zh/index.html", data="data/ideas_zh.html", out="zh/ideas/index.html", base="/zh/", path="/zh/ideas/",
               title="观点 | 彭家荣 Chris Pereira",
               desc="彭家荣的核心观点：信任、出海与本土化，来自在中国生活和工作的20多年。"),
}
EXTRA = ('<style>main#top{min-height:60vh}#ideas .ideas.mcap>li{display:grid!important}#ideas .mmore{display:none!important}'
         '@media (max-width:700px){#ideas .head .lede{display:block!important}}</style>')
JS = ('<script>(function(){var L=document.documentElement.lang.indexOf("zh")===0;'
      'document.querySelectorAll(".ideas>li").forEach(function(li,i){li.id=li.id||("idea-"+(i+1));var d=li.querySelector(":scope>div");'
      'if(d&&!d.querySelector(".imore")){var s=document.createElement("span");s.className="imore";s.textContent=(L?"展开":"Read more")+" ▾";d.appendChild(s)}'
      'li.addEventListener("click",function(e){if(e.target.closest("a"))return;li.classList.add("open")})});'
      'if(/^#idea-/.test(location.hash)){var t=document.getElementById(location.hash.slice(1));if(t){t.classList.add("open");t.scrollIntoView({block:"center"})}}'
      '})();</script>')


def build():
    for lang, p in PAGES.items():
        home = open(p["home"], encoding="utf-8").read()
        head = home[:home.index("</head>")]
        url = SITE + p["path"]
        head = re.sub(r"<title>.*?</title>", lambda _: "<title>" + p["title"] + "</title>", head, count=1, flags=re.S)
        head = re.sub(r'(<meta name="description" content=")[^"]*(")', lambda m: m.group(1) + p["desc"] + m.group(2), head, count=1)
        head = re.sub(r'(<link rel="canonical" href=")[^"]*(")', lambda m: m.group(1) + url + m.group(2), head, count=1)
        head = re.sub(r'(<meta property="og:url" content=")[^"]*(")', lambda m: m.group(1) + url + m.group(2), head, count=1)
        head = re.sub(r'(<meta property="og:title" content=")[^"]*(")', lambda m: m.group(1) + p["title"] + m.group(2), head, count=1)
        head = re.sub(r'(<meta property="og:description" content=")[^"]*(")', lambda m: m.group(1) + p["desc"] + m.group(2), head, count=1)
        head = re.sub(r'<link rel="alternate" hreflang="[^"]*" href="[^"]*">\n?', "", head)
        head += ('<link rel="alternate" hreflang="en" href="' + SITE + '/ideas/">\n<link rel="alternate" hreflang="zh-CN" href="' + SITE
                 + '/zh/ideas/">\n<link rel="alternate" hreflang="x-default" href="' + SITE + '/ideas/">\n')
        head = re.sub(r'<script type="application/ld\+json"[^>]*>.*?</script>\n?', "", head, flags=re.S)  # homepage-only data
        top = home[home.index("<body>"):home.index("<main")]
        top = top.replace('href="#', 'href="' + p["base"] + "#")  # section links go back to the homepage
        top = top.replace('class="langsw" href="/zh/"', 'class="langsw" href="/zh/ideas/"').replace('class="langsw" href="/"', 'class="langsw" href="/ideas/"')
        foot = home[home.index("<footer"):home.index("</footer>") + len("</footer>")]
        tail = ""
        for a, b in (("<!--mobile-->", "<!--/mobile-->"), ("<!--simple-->", "<!--/simple-->")):
            if a in home and b in home:
                tail += home[home.index(a):home.index(b) + len(b)] + "\n"
        body = open(p["data"], encoding="utf-8").read()
        page = (head + EXTRA + "</head>\n" + top + '<main id="top">\n' + body + "</main>\n\n" + foot
                + '\n<script defer src="/a.js"></script>\n' + JS + "\n" + tail + "</body>\n</html>\n")
        os.makedirs(os.path.dirname(p["out"]), exist_ok=True)
        open(p["out"], "w", encoding="utf-8").write(page)
    print("ideas pages ok")


if __name__ == "__main__":
    build()
