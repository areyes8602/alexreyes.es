#!/usr/bin/env python3
"""build_feed.py — Genera /feed.xml (RSS 2.0) a partir de las noticias de la home.

Lee la sección <section class="news-section"> de index.html (versión ES), extrae
cada noticia (fecha, enlace, texto y columna Docencia/Doctorado) y produce un
feed RSS válido en la raíz. Re-ejecutable: sobrescribe feed.xml.

Uso:
    python3 scripts/build_feed.py

Cuándo: después de actualizar las noticias de la home.
"""
import html as htmllib
import re
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
BASE = "https://alexreyes.es"
HOME = REPO / "index.html"
OUT = REPO / "feed.xml"
MAX_ITEMS = 50

MONTHS = {
    "ene": 1, "feb": 2, "mar": 3, "abr": 4, "may": 5, "jun": 6,
    "jul": 7, "ago": 8, "sep": 9, "set": 9, "oct": 10, "nov": 11, "dic": 12,
}

SECTION_RE = re.compile(r'<section class="news-section">(.*?)</section>', re.S)
COL_RE = re.compile(
    r'<h3 class="news-col-title">.*?</span>([^<]+)</h3>(.*?)(?=<h3 class="news-col-title">|$)',
    re.S,
)
ITEM_RE = re.compile(
    r'<span class="news-date">(.*?)</span>\s*'
    r'<a href="([^"]+)"[^>]*class="news-text">(.*?)</a>',
    re.S,
)


def strip_tags(s):
    return re.sub(r"\s+", " ", htmllib.unescape(re.sub(r"<[^>]+>", "", s))).strip()


def parse_date(s):
    s = strip_tags(s).lower()
    m = re.search(r"(?:(\d{1,2})\s+)?([a-zà-ÿ]{3})\.?\s+(\d{4})", s)
    if not m:
        return None
    day = int(m.group(1)) if m.group(1) else 1
    mon = MONTHS.get(m.group(2)[:3])
    if not mon:
        return None
    try:
        return datetime(int(m.group(3)), mon, day, 12, 0, 0, tzinfo=timezone.utc)
    except ValueError:
        return None


def rfc822(dt):
    return dt.strftime("%a, %d %b %Y %H:%M:%S +0000")


def xml_escape(s):
    return (s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))


def collect_items():
    text = HOME.read_text(encoding="utf-8")
    ms = SECTION_RE.search(text)
    if not ms:
        return []
    section = ms.group(1)
    items = []
    for cat, body in COL_RE.findall(section):
        category = strip_tags(cat)
        for date_s, href, raw in ITEM_RE.findall(body):
            dt = parse_date(date_s)
            title = strip_tags(raw)
            if not title or not href:
                continue
            link = href if href.startswith("http") else BASE + href
            items.append({
                "title": title,
                "link": link,
                "category": category,
                "dt": dt or datetime(1970, 1, 1, tzinfo=timezone.utc),
                "html": raw.strip(),
            })
    # más recientes primero; estables dentro de la misma fecha
    items.sort(key=lambda x: x["dt"], reverse=True)
    return items[:MAX_ITEMS]


def build():
    items = collect_items()
    now = rfc822(datetime.now(timezone.utc))
    last = rfc822(items[0]["dt"]) if items else now
    parts = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">',
        "<channel>",
        "<title>alexreyes.es — Novedades</title>",
        f"<link>{BASE}/</link>",
        "<description>Apuntes, ejercicios y exámenes de matemáticas, y avances del doctorado (Collatz). Por Àlex Reyes.</description>",
        "<language>es</language>",
        f'<atom:link href="{BASE}/feed.xml" rel="self" type="application/rss+xml"/>',
        f"<lastBuildDate>{last}</lastBuildDate>",
        f"<pubDate>{last}</pubDate>",
    ]
    for it in items:
        parts += [
            "<item>",
            f"<title>{xml_escape(it['title'])}</title>",
            f"<link>{xml_escape(it['link'])}</link>",
            f'<guid isPermaLink="true">{xml_escape(it["link"])}</guid>',
            f"<category>{xml_escape(it['category'])}</category>",
            f"<pubDate>{rfc822(it['dt'])}</pubDate>",
            f"<description><![CDATA[{it['html']}]]></description>",
            "</item>",
        ]
    parts += ["</channel>", "</rss>", ""]
    OUT.write_text("\n".join(parts), encoding="utf-8")
    print(f"feed.xml generado: {len(items)} items → {OUT.relative_to(REPO)}")


if __name__ == "__main__":
    build()
