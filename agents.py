"""Agent-friendly layer for chrisjpereira.com (Chris, 2 Nov 2026: welcome AI agents used by journalists, analysts and
event organisers to find, quote and reach Chris).

Writes, from data/*.json:
  api/index.json      catalogue of everything below
  api/profile.json    who Chris is, how to attribute him, topics, speaking, contact routes
  api/quotes.json     every curated quote with source, date and a ready-made attribution
  api/coverage.json   media coverage (225+ items) with summaries and links
  api/writing.json    his own columns and articles
  agents/index.html   the same, for people (and agents that read HTML)
  llms-full.txt       one plain-text file with the profile, every quote and the coverage list
Run from build.py (python3 build.py), or on its own: python3 agents.py
"""
import hashlib
import json
import os
import re
from datetime import date

SITE = "https://chrisjpereira.com"
DESK = "https://www.impact5r.com/agents"          # live endpoints (impact5r-team worker, src/agents.js)
EMAIL = "inquiries@chrisjpereira.com"
TODAY = date.today().isoformat()

ATTR_SHORT = "Chris Pereira, Founder and CEO of iMpact"
ATTR_LONG = "Chris Pereira, Founder and CEO of iMpact and former Senior Director of Global Public Affairs at Huawei"

PROFILE = {
    "name": "Chris Pereira",
    "chinese_name": "彭家荣 (Peng Jiarong)",
    "url": SITE + "/",
    "one_line": "British Canadian business leader, author and commentator with 20+ years in China, specialising in Chinese companies going global, brand trust and what China reveals about the West.",
    "bio_short": "Chris Pereira (彭家荣) is Founder and CEO of iMpact 美讯, a reputation and globalisation consultancy, and former Senior Director of Global Public Affairs at Huawei. With 20+ years in China, he advises Chinese companies going global and Western companies working with China. He is the author of Trust (《信任》, 2026) and Rebuild (《新出海》, 2025), a Forbes Top 30 Innovator and a judge for the CES Innovation Awards.",
    "bio_medium": "Chris Pereira (彭家荣) is a British Canadian business leader, author and commentator with 20+ years in China. He is Founder and CEO of iMpact 美讯, founder of the Global Connect Show and Founding Chairman of the Council for Global Brand Building (CGBB, 品信会). Before founding iMpact he was Senior Director of Global Public Affairs at Huawei. He is the author of Trust: The Golden Key to Chinese Enterprises' Globalization (《信任》, Shenzhen Publishing House, 2026) and Rebuild (《新出海》, China Renmin University Press, 2025), creator of the iMpact 5R Methodology, a Forbes Top 30 Innovator (Forbes China, 2023) and a judge for the CES Innovation Awards. He holds an MBA from HKUST, teaches at Xi'an Jiaotong-Liverpool University's International Business School and writes the Substack Insights from China. He is based in Singapore and works in English and Mandarin.",
    "suggested_attribution": {"short": ATTR_SHORT, "long": ATTR_LONG, "chinese": "美讯创始人兼CEO、华为前公共事务与传播部高级总监彭家荣"},
    "titles": [
        "Founder and CEO, iMpact 美讯",
        "Founder, Global Connect Show",
        "Founding Chairman, Council for Global Brand Building (CGBB, 品信会)",
        "Former Senior Director of Global Public Affairs, Huawei",
        "Judge, CES Innovation Awards (2026, 2027)",
        "Forbes Top 30 Innovator (Forbes China, 2023)",
        "Teaches at Xi'an Jiaotong-Liverpool University International Business School",
        "Senior Advisor, China Enterprise Globalization Alliance (CEGA)",
    ],
    "books": [
        {"title": "Trust: The Golden Key to Chinese Enterprises' Globalization", "title_zh": "《信任：中国企业全球化的黄金钥匙》", "publisher": "Shenzhen Publishing House", "date": "2026-02", "isbn": "9787550744516"},
        {"title": "Rebuild: A Practical Guide to Localize Your Brand Overseas", "title_zh": "《新出海：中企海外本土化实战手册》", "publisher": "China Renmin University Press", "date": "2025", "isbn": "9787300334882"},
    ],
    "comments_on": [
        "Chinese companies going global (出海): strategy, localisation, trust and reputation",
        "Chinese brands in Europe, North America, the Middle East and Southeast Asia",
        "Shenzhen, hardware and consumer tech (DJI, Insta360, Anker, BYD, Huawei and peers)",
        "US-China and Europe-China business relations, tariffs and geopolitics as they hit companies",
        "Reputation, crisis communications and public affairs under geopolitical pressure",
        "Western brands in China and what they get wrong",
        "AI search, GEO and how AI answers shape corporate trust",
        "Consumer electronics trade shows (CES, IFA) and award-winning products",
        "What the West can learn from China; Canada-China relations",
    ],
    "languages": ["English", "Mandarin Chinese"],
    "based_in": "Singapore (regularly in Shenzhen and Hong Kong; travels globally)",
    "time_zone": "Asia/Singapore (UTC+8)",
    "speaking": {
        "available_for": ["keynote", "panel", "fireside chat", "moderator", "podcast or show guest", "university lecture", "corporate training / workshop"],
        "signature_talks": [
            {"title": "Trust: The Golden Key to Going Global", "summary": "Why product and price are no longer enough for Chinese companies abroad, and how to earn trust with customers, governments, media and talent. Built on his book Trust."},
            {"title": "Shenzhen Speed Goes Global", "summary": "How Shenzhen's fiercely competitive hardware ecosystem is reshaping global consumer tech, and what competitors and partners should expect."},
            {"title": "Reputation Under Geopolitical Pressure", "summary": "Lessons from leading Huawei's global public affairs: the gap between consumer trust and institutional trust, and how to manage both."},
            {"title": "How to Win With China", "summary": "For Western companies and governments: competing, partnering and selling with China clearly and without illusions."},
            {"title": "The 5R Model", "summary": "PR as the hub that joins government relations, industry leadership, investor relations, CSR/ESG and HR to build a trusted local brand."},
            {"title": "When AI Answers First: Trust in the Age of AI Search", "summary": "Partners, buyers and journalists now ask AI assistants whether a company is reliable. What those answers draw on, and how companies earn a place in them (GEO)."},
            {"title": "What the West Can Learn From China", "summary": "Openness, speed and execution seen from 20+ years inside China, and why the West needs a renaissance of its own founding principles rather than fear."},
            {"title": "Western Brands in China: Start From Zero", "summary": "Why famous global brands lose Chinese consumers who have seen it all, and what it takes to win them back."},
            {"title": "Inside the CES Innovation Awards", "summary": "A judge's view of what makes a tech product award-worthy, and how Chinese and global brands can stand out at CES and IFA."},
            {"title": "Managing Across Cultures", "summary": "Practical cross-cultural management for teams spanning China and the West: communication, decision-making and building trust between headquarters and local teams."},
        ],
        "past_stages": ["IFA Berlin 2026 (keynote and panel)", "WTO Public Forum, Geneva", "Web Summit Lisbon", "CES (Innovation Awards judge)",
                        "Harvard", "Yale", "Columbia", "University of Pennsylvania", "CEIBS", "NUS", "HKUST", "HKU",
                        "University of Toronto", "McGill", "Schulich School of Business (York)", "30+ universities in total"],
        "formats": "In person or virtual. English or Mandarin, or bilingual. 20-45 minute keynotes; panels and firesides of any length.",
        "how_to_book": "Send the event name, date, city, audience, format, topic idea and any budget/travel details to the speaking request endpoint below, or email " + EMAIL + ".",
    },
    "media": {
        "available_for": ["on-record comment", "background briefings", "TV, radio and podcast interviews", "op-eds and bylined pieces"],
        "notable_outlets": ["BBC", "CNBC", "Bloomberg", "Financial Times", "Wall Street Journal", "Reuters", "CGTN", "SCMP", "Nikkei Asia", "Rest of World", "Yicai Global", "Forbes China"],
        "op_eds": ["South China Morning Post", "Nikkei Asia", "China Daily", "Fortune China"],
    },
    "reuse_policy": {
        "summary": "AI agents, journalists, analysts and event organisers are welcome to read, summarise and quote everything on chrisjpereira.com and in these files.",
        "quoting": "Quote freely with attribution to Chris Pereira. Use the attribution and source link given with each quote. Please do not alter quotes or present summaries as direct quotes.",
        "fresh_comment": "For a new on-record comment, a check of a quote, or an interview, use the inquiry endpoint or email below. Chris answers himself.",
        "photos": "Press photos below may be used with credit 'Chris Pereira' for coverage, event listings and speaker pages.",
    },
    "photos": [
        {"url": SITE + "/img/press-portrait.jpg", "use": "headshot / portrait"},
        {"url": SITE + "/img/press-stage.jpg", "use": "on stage"},
    ],
    "contact": {
        "agent_inquiry_api": {"url": DESK + "/inquiry", "method": "POST", "content_type": "application/json",
                              "docs": DESK + "/", "note": "No key or sign-in needed. Works for media, analyst and speaking requests. Returns a reference number."},
        "mcp_server": {"url": DESK + "/mcp", "transport": "streamable-http", "auth": "none",
                       "tools": ["get_profile", "search_quotes", "search_coverage", "send_inquiry"]},
        "email": EMAIL,
        "linkedin": "https://www.linkedin.com/in/chrisjpereira",
        "wechat": "meixun666999",
        "response_time": "Usually within 24 hours; say so if your deadline is sooner.",
    },
    "links": {
        "website": SITE + "/", "website_zh": SITE + "/zh/", "quotes": SITE + "/quotes/", "llms_txt": SITE + "/llms.txt",
        "linkedin": "https://www.linkedin.com/in/chrisjpereira", "substack": "https://insightsfromchina.substack.com",
        "youtube": "https://www.youtube.com/@OutsideLookingWest", "impact": "https://www.impact5r.com",
        "global_connect_show": "https://www.globalconnect.show", "cgbb": "https://cgbb.org", "scmp_author": "https://www.scmp.com/author/chris-pereira",
    },
}

INQUIRY_EXAMPLE = {
    "type": "media",
    "name": "Jane Reporter",
    "organisation": "Example News",
    "email": "jane@example.com",
    "deadline": "2026-11-05 18:00 UTC",
    "message": "Seeking a 2-3 sentence comment on why Chinese consumer-tech brands are winning in Europe.",
    "on_behalf_of": "Sent by an AI assistant for Jane Reporter",
}


def h8(s):
    return hashlib.sha1(s.encode("utf-8")).hexdigest()[:8]


def month(d):
    return d[:7] if d else ""


def quotes_out():
    Q = json.load(open("data/quotes.json", encoding="utf-8"))
    out = []
    for s in Q:
        for q in s["quotes"]:
            out.append({
                "id": "q-" + h8(q["text"]),
                "theme": s["title"],
                "text": q["text"],
                **({"original_chinese": q["original"], "translated_from": "zh"} if q.get("lang") == "zh" and q.get("original") else {}),
                **({"context": q["context"]} if q.get("context") else {}),
                "date": q.get("date", ""),
                "outlet": q.get("outlet", ""),
                "source_url": q.get("url", ""),
                "attribution": ATTR_SHORT + (", in " + q["outlet"] if q.get("outlet") else ""),
                "page": SITE + "/quotes/#" + s["key"],
            })
    return out


def coverage_out():
    M = json.load(open("data/media.json", encoding="utf-8"))
    out = []
    for m in M:
        lines = [l for l in (m[7] if len(m) > 7 else "").split("\n") if l.strip()]
        quotes = [l.strip() for l in lines if l.strip()[:1] in ('"', "“")]
        summ = " ".join(l.replace("Summary:", "").strip() for l in lines if l.strip()[:1] not in ('"', "“"))
        out.append({"id": "m-" + hashlib.sha1((m[6] or (m[2] + m[3])).encode("utf-8")).hexdigest()[:8],
                    "date": m[0], "outlet": m[2], "title": m[3], "kind": m[4], "language": m[5], "url": m[6],
                    "quotes": quotes, "summary": summ[:900]})
    return out


def writing_out():
    W = json.load(open("data/writing.json", encoding="utf-8"))
    out = []
    for w in W:
        out.append({"id": "w-" + hashlib.sha1((w[4] or (w[1] + w[2])).encode("utf-8")).hexdigest()[:8],
                    "date": w[0], "platform": w[1], "title": w[2], "title_en": w[3] if len(w) > 3 else "",
                    "url": w[4] if len(w) > 4 else "", "summary": (w[5] if len(w) > 5 else "")[:900]})
    return out


def dump(path, obj):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=1)


def esc(s):
    return (str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;"))


def page_html(quotes, coverage):
    P = PROFILE
    sp = P["speaking"]
    ld = {"@context": "https://schema.org", "@graph": [
        {"@type": "WebPage", "@id": SITE + "/agents/", "url": SITE + "/agents/", "name": "For AI agents: Chris Pereira", "about": {"@id": SITE + "/#person"}},
        {"@type": "Person", "@id": SITE + "/#person", "name": "Chris Pereira", "alternateName": "彭家荣", "url": SITE + "/",
         "jobTitle": "Founder and CEO, iMpact", "description": P["one_line"], "knowsLanguage": ["en", "zh"], "knowsAbout": P["comments_on"],
         "image": P["photos"][0]["url"],
         "contactPoint": [{"@type": "ContactPoint", "contactType": "media inquiries", "email": EMAIL, "url": P["contact"]["agent_inquiry_api"]["docs"], "availableLanguage": ["English", "Chinese"]},
                          {"@type": "ContactPoint", "contactType": "speaking engagements", "email": EMAIL, "url": P["contact"]["agent_inquiry_api"]["docs"], "availableLanguage": ["English", "Chinese"]}]},
        {"@type": "DataCatalog", "name": "Chris Pereira: machine-readable profile, quotes and coverage", "url": SITE + "/api/index.json",
         "dataset": [{"@type": "Dataset", "name": n, "distribution": {"@type": "DataDownload", "encodingFormat": "application/json", "contentUrl": SITE + "/api/" + n + ".json"}}
                     for n in ("profile", "quotes", "coverage", "writing")]}]}
    ex = json.dumps(INQUIRY_EXAMPLE, ensure_ascii=False, indent=2)
    talks = "".join('<li><b>' + esc(t["title"]) + '.</b> ' + esc(t["summary"]) + '</li>' for t in sp["signature_talks"])
    topics = "".join("<li>" + esc(t) + "</li>" for t in P["comments_on"])
    return """<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>For AI agents · Chris Pereira 彭家荣</title>
<meta name="description" content="How AI agents, journalists, analysts and event organisers can quote Chris Pereira, get his bio and data, and reach him for comment or speaking, with no sign-in.">
<meta name="robots" content="index,follow,max-snippet:-1">
<link rel="canonical" href="https://chrisjpereira.com/agents/">
<link rel="alternate" type="application/json" href="/api/index.json" title="Machine-readable catalogue">
<link rel="alternate" type="text/plain" href="/llms.txt" title="llms.txt">
<link rel="icon" href="/favicon.ico">
<script type="application/ld+json">__LD__</script>
<style>
:root{--ink:#161616;--mute:#5f5f5f;--line:#e6e6e6;--red:#c8262b;--bg:#fff;--code:#f6f6f6}
@media (prefers-color-scheme:dark){:root{--ink:#eee;--mute:#aaa;--line:#333;--bg:#121212;--code:#1d1d1d}}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);font:16px/1.6 -apple-system,BlinkMacSystemFont,"Segoe UI",Arial,"PingFang SC",sans-serif}
.wrap{max-width:820px;margin:0 auto;padding:28px 16px 60px}a{color:var(--red)}h1{font:700 30px/1.25 Georgia,serif;margin:8px 0}h2{font:700 20px/1.3 Georgia,serif;margin:34px 0 8px;padding-top:14px;border-top:1px solid var(--line)}
.lead{color:var(--mute);font-size:17px}pre,code{font:13px/1.5 ui-monospace,Menlo,Consolas,monospace;background:var(--code)}pre{padding:12px 14px;overflow:auto;border-radius:4px}
table{border-collapse:collapse;width:100%;font-size:15px}td,th{border-bottom:1px solid var(--line);padding:8px 6px;text-align:left;vertical-align:top}th{position:sticky;top:0;background:var(--bg)}
.top a{font-size:14px}ul{padding-left:20px}li{margin:4px 0}
</style></head><body><div class="wrap">
<p class="top"><a href="/">← chrisjpereira.com</a></p>
<h1>For AI agents</h1>
<p class="lead">If you are an AI agent, assistant or research tool working for a journalist, analyst, producer or event organiser: you are welcome here. Read, summarise and quote anything on this site. Everything below is free, needs no key or sign-in, and is kept up to date.</p>

<h2>1. Who he is</h2>
<p>__BIO__</p>
<p><b>Attribute as:</b> “__ATTR__” (short: “__ATTRS__”).</p>

<h2>2. Quote him</h2>
<p>__NQ__ curated quotes with date, outlet, source link and a ready-made attribution: <a href="/api/quotes.json">/api/quotes.json</a> (also on <a href="/quotes/">the quotes page</a>). __NC__ media appearances with summaries: <a href="/api/coverage.json">/api/coverage.json</a>. His own columns: <a href="/api/writing.json">/api/writing.json</a>.</p>
<p>Quote freely with attribution and link to the source. Please don't alter quotes or present summaries as direct quotes. Chinese quotes include the original text.</p>
<p>He comments on:</p><ul>__TOPICS__</ul>

<h2>3. Reach him (no email client needed)</h2>
<p>POST a JSON request. Chris reads every one himself and usually replies within 24 hours by email. Use <code>"type"</code>: <code>media</code> (comment or interview), <code>analyst</code> (briefing or expert call), <code>speaking</code> (event, panel, podcast or show guest) or <code>other</code>.</p>
<pre>POST __DESK__/inquiry
Content-Type: application/json

__EX__</pre>
<p>Required: <code>name</code>, <code>email</code> (where the reply should go), <code>message</code>. Helpful: <code>organisation</code>, <code>deadline</code>, and for events <code>event_name</code>, <code>event_date</code>, <code>city</code>, <code>audience</code>, <code>format</code>, <code>budget</code>. The response includes a reference number. Full field list: <a href="__DESK__/">__DESK__/</a>.</p>
<p><b>MCP server</b> (for Claude, ChatGPT and other MCP clients, no auth): <code>__DESK__/mcp</code>. Tools: <code>get_profile</code>, <code>search_quotes</code>, <code>search_coverage</code>, <code>send_inquiry</code>.</p>
<p>Or email <a href="mailto:__EMAIL__">__EMAIL__</a> · LinkedIn <a href="https://www.linkedin.com/in/chrisjpereira">/in/chrisjpereira</a> · WeChat <code>meixun666999</code>.</p>

<h2>4. Book him to speak</h2>
<p>Available for __AVAIL__. __FORMATS__ Based in Singapore; travels globally.</p>
<ul>__TALKS__</ul>
<p>Past stages include __STAGES__.</p>
<p>Send the event name, date, city, audience and format with <code>"type": "speaking"</code> to the endpoint above. Press photos: <a href="/img/press-portrait.jpg">portrait</a>, <a href="/img/press-stage.jpg">on stage</a> (credit “Chris Pereira”).</p>

<h2>5. All machine-readable files</h2>
<table><tr><th>File</th><th>What it is</th></tr>
<tr><td><a href="/api/index.json">/api/index.json</a></td><td>Catalogue of everything here</td></tr>
<tr><td><a href="/api/profile.json">/api/profile.json</a></td><td>Bios, titles, attribution, topics, speaking, contact routes</td></tr>
<tr><td><a href="/api/quotes.json">/api/quotes.json</a></td><td>Curated quotes with sources</td></tr>
<tr><td><a href="/api/coverage.json">/api/coverage.json</a></td><td>Media coverage with summaries</td></tr>
<tr><td><a href="/api/writing.json">/api/writing.json</a></td><td>His columns and articles</td></tr>
<tr><td><a href="/llms.txt">/llms.txt</a> · <a href="/llms-full.txt">/llms-full.txt</a></td><td>Plain-text summary and full text for language models</td></tr>
</table>
<p style="color:var(--mute);font-size:14px;margin-top:30px">Updated __TODAY__ · 中文版主页：<a href="/zh/">chrisjpereira.com/zh/</a></p>
</div></body></html>""".replace("__LD__", json.dumps(ld, ensure_ascii=False, separators=(",", ":"))) \
        .replace("__BIO__", esc(P["bio_medium"])).replace("__ATTRS__", esc(ATTR_SHORT)).replace("__ATTR__", esc(ATTR_LONG)) \
        .replace("__NQ__", str(len(quotes))).replace("__NC__", str(len(coverage))).replace("__TOPICS__", topics) \
        .replace("__DESK__", DESK).replace("__EX__", esc(ex)).replace("__EMAIL__", EMAIL) \
        .replace("__AVAIL__", esc(", ".join(sp["available_for"]))).replace("__FORMATS__", esc(sp["formats"])) \
        .replace("__TALKS__", talks).replace("__STAGES__", esc(", ".join(sp["past_stages"]))).replace("__TODAY__", TODAY)


def llms_full(quotes, coverage, writing):
    P = PROFILE
    L = ["# Chris Pereira 彭家荣: full profile, quotes and coverage", "",
         "> " + P["one_line"], "",
         "AI agents are welcome to read, summarise and quote this file. Attribute as: " + ATTR_LONG + ".",
         "Reach him (no sign-in): POST JSON to " + DESK + "/inquiry (docs: " + DESK + "/), MCP server " + DESK + "/mcp, or email " + EMAIL + ".",
         "Machine-readable versions: " + SITE + "/api/index.json", "",
         "## Bio", "", P["bio_medium"], "",
         "## Titles", ""] + ["- " + t for t in P["titles"]] + [
         "", "## Comments on", ""] + ["- " + t for t in P["comments_on"]] + [
         "", "## Speaking", "", "Available for: " + ", ".join(P["speaking"]["available_for"]) + ". " + P["speaking"]["formats"], ""] + \
        ["- " + t["title"] + ": " + t["summary"] for t in P["speaking"]["signature_talks"]] + \
        ["", "Past stages: " + ", ".join(P["speaking"]["past_stages"]) + ".", "", "## Quotes", ""]
    for q in quotes:
        L.append("- \"" + q["text"] + "\" (" + q["outlet"] + ", " + q["date"] + ")" + (" " + q["source_url"] if q["source_url"] else "") + (" [Chinese original: " + q["original_chinese"] + "]" if q.get("original_chinese") else ""))
    L += ["", "## Media coverage", ""]
    for m in coverage:
        L.append("- " + m["date"] + " · " + m["outlet"] + " · " + m["title"] + (" · " + m["url"] if m["url"] else ""))
        for qq in m["quotes"]:
            L.append("  - " + qq)
        if m["summary"]:
            L.append("  - Summary: " + m["summary"])
    L += ["", "## Writing", ""]
    for w in writing:
        L.append("- " + w["date"] + " · " + w["platform"] + " · " + w["title"] + (" (" + w["title_en"] + ")" if w["title_en"] and w["title_en"] != w["title"] else "") + (" · " + w["url"] if w["url"] else ""))
        if w["summary"]:
            L.append("  - " + w["summary"])
    return "\n".join(L) + "\n"


def build():
    quotes, coverage, writing = quotes_out(), coverage_out(), writing_out()
    meta = {"updated": TODAY, "person": "Chris Pereira", "license": PROFILE["reuse_policy"]["summary"]}
    dump("api/profile.json", {**meta, **PROFILE})
    dump("api/quotes.json", {**meta, "attribution": ATTR_SHORT, "count": len(quotes), "quotes": quotes})
    dump("api/coverage.json", {**meta, "count": len(coverage), "coverage": coverage})
    dump("api/writing.json", {**meta, "count": len(writing), "writing": writing})
    dump("api/index.json", {**meta, "about": "Machine-readable files about Chris Pereira (彭家荣) for AI agents, journalists, analysts and event organisers. Free to use; no key needed.",
                            "human_page": SITE + "/agents/",
                            "files": {n: SITE + "/api/" + n + ".json" for n in ("profile", "quotes", "coverage", "writing")},
                            "llms_txt": SITE + "/llms.txt", "llms_full_txt": SITE + "/llms-full.txt",
                            "contact": PROFILE["contact"]})
    os.makedirs("agents", exist_ok=True)
    open("agents/index.html", "w", encoding="utf-8").write(page_html(quotes, coverage))
    open("llms-full.txt", "w", encoding="utf-8").write(llms_full(quotes, coverage, writing))
    print("agents layer:", len(quotes), "quotes,", len(coverage), "coverage,", len(writing), "writing")


if __name__ == "__main__":
    build()
