"""Chris's best lines (金句) from the iMpact Academy Desk, merged into the quotes page.

The Academy team records each event's recap on the Academy Desk (impact5r.com/team/academy/),
including Chris's best lines. Claude picks the lines fit for external sharing there, translates
them and names the setting (closed-door client trainings are anonymised, e.g. "a training in
Singapore for Chinese executives"). scripts/pull_talks.py saves that feed daily as
data/academy_lines.json; this module merges it into data/quotes.json's themes, skipping any line
already on the page. Hand-curated quotes in data/quotes.json always win.
"""
import json, os, re

FEED_FILE = "data/academy_lines.json"


def norm(s):
    return re.sub(r"[\W_]+", "", (s or "").lower())


def quotes():
    Q = json.load(open("data/quotes.json", encoding="utf-8"))
    if not os.path.exists(FEED_FILE):
        return Q
    seen = set()
    for s in Q:
        for q in s["quotes"]:
            seen.add(norm(q.get("original"))), seen.add(norm(q["text"]))
    seen.discard("")
    by_key = {s["key"]: s for s in Q}
    for x in json.load(open(FEED_FILE, encoding="utf-8")):
        s = by_key.get(x.get("theme"))
        if not s or not x.get("text"):
            continue
        keys = {norm(x.get("original")), norm(x["text"])} - {""}
        if keys & seen:
            continue
        seen |= keys
        s["quotes"].append({k: v for k, v in x.items() if k in ("text", "lang", "original", "outlet", "where", "date", "type", "url") and v})
    return Q
