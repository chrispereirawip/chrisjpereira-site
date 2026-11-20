"""Small homepage overrides for index.html and zh/index.html. Run after mobile.py.
20 Nov 2026: the fold/accordion layer was removed at Chris's request (everything back to full size).
What remains: the ideas list has no 01-09 numbers (Chris: "looks super AI")."""
import re
CSS = """
.ideas .n{display:none}
.ideas li{grid-template-columns:minmax(0,1fr)}
"""
BLOCK = "<!--simple--><style>" + CSS.strip() + "</style><!--/simple-->"
for f in ["index.html", "zh/index.html"]:
    s = open(f, encoding="utf-8").read()
    s = re.sub(r"<!--simple-->.*?<!--/simple-->\n?", "", s, flags=re.S)
    s = s.replace("</body>", BLOCK + "\n</body>", 1)
    open(f, "w", encoding="utf-8").write(s)
print("simple ok")
