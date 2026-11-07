"""One footer for every page of chrisjpereira.com (Chris, 2026-11-02: "if there is something there, it should have a reason and objective").
Each item earns its place: the copyright line says whose words and photos these are; the email is the one contact route; LinkedIn,
Substack, the LinkedIn newsletter (Insights from China, launched 2026-11-03) and YouTube are where to follow him; "For AI agents" sends agents to the data and contact desk. Used by build.py (quotes),
shop.py (books), agents.py and inserted into index.html / zh/index.html by sync()."""
import re

LINKS = {
    "en": [("mailto:inquiries@chrisjpereira.com", "inquiries@chrisjpereira.com"), ("https://www.linkedin.com/in/chrisjpereira", "LinkedIn"),
           ("https://insightsfromchina.substack.com", "Substack"), ("https://www.linkedin.com/newsletters/insights-from-china-7523031887427301376/", "LinkedIn newsletter"), ("https://www.youtube.com/@OutsideLookingWest", "YouTube"), ("/agents/", "For AI agents")],
    "zh": [("mailto:inquiries@chrisjpereira.com", "inquiries@chrisjpereira.com"), ("https://www.linkedin.com/in/chrisjpereira", "领英 LinkedIn"),
           ("https://insightsfromchina.substack.com", "Substack"), ("https://www.linkedin.com/newsletters/insights-from-china-7523031887427301376/", "领英专栏"), ("https://www.youtube.com/@OutsideLookingWest", "YouTube"), ("/agents/", "AI 智能体接入")],
}
CSS = ("footer{background:var(--red-deep);color:#fff}"
       "footer .wrap{padding-top:18px;padding-bottom:18px;display:flex;justify-content:space-between;align-items:center;gap:8px 24px;flex-wrap:wrap;font-family:var(--display);font-size:13px}"
       ".fnav{display:flex;flex-wrap:wrap;gap:6px 20px}.fnav a{color:#fff;opacity:.85;text-decoration:none}.fnav a:hover{opacity:1;text-decoration:underline;text-underline-offset:3px}"
       ".cgbb-badge{display:inline-block;line-height:0;}.cgbb-badge:hover{opacity:1}.cgbb-badge img{width:234px;height:auto;display:block}"
       "@media (max-width:640px){.cgbb-badge img{width:200px}}")


def html(lang="en"):
    who = "© 2026 Chris Pereira <span lang=\"zh-Hans\">彭家荣</span>" if lang == "en" else "© 2026 彭家荣 <span lang=\"en\">Chris Pereira</span>"
    label = "Contact and channels" if lang == "en" else "联系方式与频道"
    links = "".join(f'<a href="{h}"{" rel=\"me\"" if h.startswith("https://") else ""}>{t}</a>' for h, t in LINKS[lang])
    # CGBB Website Trust Credential (Chris, 2026-11-07): the badge links to the live record on cgbb.org, so anyone can check it
    alt = "CGBB Member · Website Trust Credential. Verify at cgbb.org" if lang == "en" else "CGBB 会员 · 网站信任凭证，点击在 cgbb.org 核验"
    tip = "Verify at cgbb.org" if lang == "en" else "在 cgbb.org 核验"
    badge = (f'<a class="cgbb-badge" href="https://cgbb.org/verify/?d=chrisjpereira.com" target="_blank" rel="noopener" title="{tip}">'
             f'<img src="https://api.cgbb.org/badge/chrisjpereira.com.svg" alt="{alt}" height="74" loading="lazy"></a>')
    return f'<footer><div class="wrap"><span>{who}</span><nav class="fnav" aria-label="{label}">{links}</nav>{badge}</div></footer>'


def sync(path, lang):
    """swap the footer (and its CSS) in a hand-maintained page"""
    s = open(path, encoding="utf-8").read()
    s = re.sub(r"<footer>.*?</footer>", lambda m: html(lang), s, count=1, flags=re.S)
    s = re.sub(r"footer\{background:var\(--red-deep\);color:#fff\}\s*footer \.wrap\{[^}]*\}(\.fnav[^\n]*?\}(?=\n|\s*[^.]))?", lambda m: CSS, s, count=1)
    if ".fnav{" not in s:
        s = s.replace("</style>", CSS + "\n</style>", 1)
    open(path, "w", encoding="utf-8").write(s)


if __name__ == "__main__":
    sync("index.html", "en")
    sync("zh/index.html", "zh")
