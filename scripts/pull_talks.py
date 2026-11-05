#!/usr/bin/env python3
"""Pull Chris's latest talks from the iMpact Academy Desk and save them for build.py.

The Academy team records each talk after the event (summary, Chris's lines, photos) at
impact5r.com/team/academy/, and Claude writes the bilingual entry there. This script reads the
published feed, saves the cover photo of each talk as img/talks/talk-<id>.webp and rewrites
data/talks.json. Also saves Chris's vetted best lines (金句) as data/academy_lines.json.
Run by .github/workflows/talks.yml once a day, then build.py.
"""
import io, json, os, sys, urllib.request
from PIL import Image

FEED = os.environ.get("TALKS_FEED", "https://www.impact5r.com/team/api/academy/public/talks.json")
LINES = os.environ.get("LINES_FEED", "https://www.impact5r.com/team/api/academy/public/lines.json")
UA = {"User-Agent": "chrisjpereira-site/1.0"}


def get(url):
    with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=60) as r:
        return r.read()


def main():
    feed = json.loads(get(FEED))
    if not feed.get("ok"):
        sys.exit("feed not ok")
    out, keep = [], set()
    for t in feed["talks"]:
        if not (t.get("title_en") or t.get("title_zh")):
            continue
        if t.get("chris") is False:  # the Academy feed has talks by every iMpact speaker; this site shows Chris's only
            continue
        img = ""
        photos = t.get("photos") or []
        cover = next((p for p in photos if p.get("cover")), photos[0] if photos else None)
        if cover:
            name = "talk-%d.webp" % t["id"]
            try:
                im = Image.open(io.BytesIO(get(cover["url"]))).convert("RGB")
                im.thumbnail((1200, 1200))
                im.save(os.path.join("img", "talks", name), "WEBP", quality=82)
                img, keep = name, keep | {name}
            except Exception as e:  # keep the entry without a photo
                print("photo failed", t["id"], e)
        out.append({k: t.get(k, "") for k in ("id", "date", "event", "organizer", "city", "type",
                                              "title_en", "title_zh", "summary_en", "summary_zh", "quote_en", "quote_zh")}
                   | {"img": img, "caption": (cover or {}).get("caption", "")})
    for f in os.listdir(os.path.join("img", "talks")):
        if f.startswith("talk-") and f not in keep:
            os.remove(os.path.join("img", "talks", f))
    out.sort(key=lambda x: x["date"] or "", reverse=True)
    json.dump(out, open("data/talks.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("talks:", len(out))
    pull_lines()


def pull_lines():
    """Chris's best lines from every recap, already vetted for external sharing on the Academy Desk (academy_lines.py merges them)."""
    try:
        feed = json.loads(get(LINES))
    except Exception as e:  # keep the last good copy
        print("lines feed unavailable:", e)
        return
    if not feed.get("ok"):
        print("lines feed not ok")
        return
    keep = ("text", "lang", "original", "outlet", "where", "date", "type", "url", "theme", "event_id")
    lines = [{k: x.get(k, "") for k in keep} for x in feed.get("lines", []) if x.get("text") and x.get("theme")]
    json.dump(lines, open("data/academy_lines.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("academy lines:", len(lines))


if __name__ == "__main__":
    main()
