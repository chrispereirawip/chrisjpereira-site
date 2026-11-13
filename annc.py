"""Site-wide announcement bar (Chris, 2026-11-13): a thin, dismissible line above the header that points to the
English e-book of Trust. Chosen instead of an entry pop-up, which would block the page for journalists and organisers.
Edit TEXT to change or retire the announcement; set KEY to a new value so people who dismissed the old one see the new one.
build.py calls sync() for every page that has the site header. Not shown on the Books pages themselves."""
import re

KEY = "annc-trust-en-2026-11"
TEXT = {
    "en": ("/books/", "New: <b>Trust</b>, the English edition, is out.", "Get the e-book →", "Dismiss"),
    "zh": ("/zh/books/", "新书：《信任》英文版电子书已上线。", "前往购买 →", "关闭"),
}
CSS = (".annc{background:var(--red-deep);color:#fff;font-family:var(--display);font-size:13.5px;line-height:1.35}"
       ".annc .wrap{display:flex;align-items:center;justify-content:center;gap:6px 14px;padding-top:7px;padding-bottom:7px;position:relative;flex-wrap:wrap;text-align:center}"
       ".annc p{margin:0;padding:0 34px}.annc a{color:#fff;font-weight:600;text-underline-offset:3px;white-space:nowrap}"
       ".annc button{position:absolute;right:8px;top:50%;transform:translateY(-50%);background:none;border:0;color:#fff;opacity:.8;font-size:18px;line-height:1;padding:6px 8px;cursor:pointer}"
       ".annc button:hover{opacity:1}")


def html(lang="en"):
    href, msg, cta, close = TEXT[lang]
    return ('<!--annc--><style>' + CSS + '</style><div class="annc" id="annc" role="region" aria-label="' + ("Announcement" if lang == "en" else "公告") + '">'
            '<div class="wrap"><p>' + msg + ' <a href="' + href + '">' + cta + '</a></p>'
            '<button type="button" aria-label="' + close + '" title="' + close + '">×</button></div></div>'
            '<script>(function(){var a=document.getElementById("annc"),k="' + KEY + '";'
            'try{if(localStorage.getItem(k)){a.hidden=true;return}}catch(e){}'
            'a.querySelector("button").addEventListener("click",function(){a.hidden=true;try{localStorage.setItem(k,"1")}catch(e){}})})();</script><!--/annc-->')


def sync(path, lang):
    s = open(path, encoding="utf-8").read()
    s = re.sub(r"<!--annc-->.*?<!--/annc-->\n?", "", s, flags=re.S)
    assert s.count("<body>") == 1, path
    s = s.replace("<body>", "<body>\n" + html(lang), 1)
    open(path, "w", encoding="utf-8").write(s)


PAGES = (("index.html", "en"), ("zh/index.html", "zh"), ("quotes/index.html", "en"))

if __name__ == "__main__":
    for p, l in PAGES:
        sync(p, l)
