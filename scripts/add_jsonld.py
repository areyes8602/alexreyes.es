#!/usr/bin/env python3
"""Inyecta datos estructurados schema.org (JSON-LD) en las páginas del sitio.

Genera, según el tipo de página:
  - BreadcrumbList  → en toda página con <div class="breadcrumb"> (lo deriva del
    propio breadcrumb, sin inventar nada). Da migas de pan en Google.
  - LearningResource → en las hojas de /aula/ (apuntes, exámenes, ejercicios):
    name, description, inLanguage, url, autor.
  - WebSite          → en las home (raíz, /ca/, /en/).

Idempotente: si la página ya tiene un <script type="application/ld+json">, no la
toca. Pensado como PASO FINAL del pipeline (después de los build_* y de
add_og_tags.py). Re-correrlo no duplica nada.

Uso:
    python3 scripts/add_jsonld.py [--dry-run] [--only path/to/file.html]
"""
import json
import re
import sys
import html as htmllib
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
BASE = "https://alexreyes.es"
AUTHOR = {"@type": "Person", "name": "Àlex Reyes", "url": f"{BASE}/cv/"}
SKIP_DIRS = {"node_modules", ".git", "templates", "editor", "scripts", "assets"}

LANG_RE = re.compile(r'<html\s+[^>]*lang="([^"]+)"', re.I)
TITLE_RE = re.compile(r"<title>(.*?)</title>", re.S)
DESC_RE = re.compile(r'<meta\s+name="description"\s+content="([^"]*)"')
CANON_RE = re.compile(r'<link\s+rel="canonical"\s+href="([^"]*)"')
CRUMB_BLOCK_RE = re.compile(r'<div class="breadcrumb">(.*?)</div>', re.S)
CRUMB_LINK_RE = re.compile(r'<a\s+href="([^"]+)"[^>]*>(.*?)</a>', re.S)
CRUMB_CURRENT_RE = re.compile(r'<span class="current">(.*?)</span>', re.S)


def strip_tags(s):
    return htmllib.unescape(re.sub(r"<[^>]+>", "", s)).strip()


def get_lang(t):
    m = LANG_RE.search(t)
    return m.group(1).strip().lower().split("-")[0] if m else "es"


def get_url(t, p):
    m = CANON_RE.search(t)
    if m:
        return m.group(1)
    rel = p.relative_to(REPO).as_posix()
    if rel.endswith("index.html"):
        rel = rel[: -len("index.html")]
    return BASE + "/" + rel.lstrip("/")


def abs_url(href):
    if href.startswith("http"):
        return href
    return BASE + href if href.startswith("/") else f"{BASE}/{href}"


def breadcrumb_schema(t, page_url):
    mb = CRUMB_BLOCK_RE.search(t)
    if not mb:
        return None
    block = mb.group(1)
    items = []
    pos = 1
    for href, label in CRUMB_LINK_RE.findall(block):
        name = strip_tags(label)
        if not name:
            continue
        items.append({
            "@type": "ListItem",
            "position": pos,
            "name": name,
            "item": abs_url(href),
        })
        pos += 1
    mc = CRUMB_CURRENT_RE.search(block)
    if mc:
        name = strip_tags(mc.group(1))
        if name:
            items.append({
                "@type": "ListItem",
                "position": pos,
                "name": name,
                "item": page_url,
            })
    if len(items) < 2:
        return None
    return {"@type": "BreadcrumbList", "itemListElement": items}


def learning_resource_schema(rel, t, title, desc, lang, url):
    parts = rel.parts
    if not (len(parts) and parts[0] == "aula"):
        # también /ca/aula y /en/aula
        if not (len(parts) > 1 and parts[0] in ("ca", "en") and parts[1] == "aula"):
            return None
    seg = set(parts)
    if "apuntes" in seg:
        rtype = "Apuntes"
    elif "examenes" in seg:
        rtype = "Examen"
    elif "ejercicios" in seg:
        rtype = "Ejercicio"
    else:
        return None
    # nombre: la miga actual si existe, si no el <title>
    name = title
    mc = CRUMB_CURRENT_RE.search(t)
    mb = CRUMB_BLOCK_RE.search(t)
    if mb:
        mc = CRUMB_CURRENT_RE.search(mb.group(1))
        if mc:
            cur = strip_tags(mc.group(1))
            if cur:
                name = cur
    res = {
        "@type": "LearningResource",
        "name": name,
        "url": url,
        "inLanguage": lang,
        "learningResourceType": rtype,
        "isAccessibleForFree": True,
        "author": AUTHOR,
        "publisher": {"@type": "Person", "name": "Àlex Reyes"},
    }
    if desc:
        res["description"] = desc
    return res


def website_schema(rel, title, desc, lang, url):
    homes = {"index.html", "ca/index.html", "en/index.html"}
    if rel.as_posix() not in homes:
        return None
    res = {
        "@type": "WebSite",
        "name": "alexreyes.es",
        "url": url,
        "inLanguage": lang,
        "author": AUTHOR,
    }
    if desc:
        res["description"] = desc
    return res


def build_jsonld(p, t):
    rel = p.relative_to(REPO)
    lang = get_lang(t)
    url = get_url(t, p)
    mt = TITLE_RE.search(t)
    title = strip_tags(mt.group(1)) if mt else "alexreyes.es"
    md = DESC_RE.search(t)
    desc = htmllib.unescape(md.group(1)).strip() if md else ""

    graph = []
    bc = breadcrumb_schema(t, url)
    if bc:
        graph.append(bc)
    lr = learning_resource_schema(rel, t, title, desc, lang, url)
    if lr:
        graph.append(lr)
    ws = website_schema(rel, title, desc, lang, url)
    if ws:
        graph.append(ws)
    if not graph:
        return None
    if len(graph) == 1:
        data = {"@context": "https://schema.org", **graph[0]}
    else:
        data = {"@context": "https://schema.org", "@graph": graph}
    return data


def main():
    args = sys.argv[1:]
    dry = "--dry-run" in args
    only = None
    if "--only" in args:
        i = args.index("--only")
        if i + 1 < len(args):
            only = args[i + 1]

    files = [REPO / only] if only else list(REPO.rglob("*.html"))
    added = skipped_has = skipped_none = skipped_err = 0
    by_type = {"BreadcrumbList": 0, "LearningResource": 0, "WebSite": 0}

    for p in files:
        if any(part in SKIP_DIRS for part in p.relative_to(REPO).parts[:-1]):
            continue
        try:
            t = p.read_text(encoding="utf-8")
        except Exception:
            skipped_err += 1
            continue
        if "application/ld+json" in t:
            skipped_has += 1
            continue
        if "</head>" not in t:
            skipped_err += 1
            continue
        data = build_jsonld(p, t)
        if not data:
            skipped_none += 1
            continue
        # contar tipos
        types = [data["@type"]] if "@type" in data else [g["@type"] for g in data["@graph"]]
        for ty in types:
            by_type[ty] = by_type.get(ty, 0) + 1
        block = (
            '<script type="application/ld+json">'
            + json.dumps(data, ensure_ascii=False, separators=(",", ":"))
            + "</script>\n"
        )
        if dry:
            added += 1
            continue
        t = t.replace("</head>", block + "</head>", 1)
        try:
            p.write_text(t, encoding="utf-8")
            added += 1
        except Exception:
            skipped_err += 1

    pfx = "[DRY-RUN] " if dry else ""
    print(f"{pfx}JSON-LD añadido: {added}")
    print(f"  por tipo: {by_type}")
    print(f"  ya tenían (sin tocar): {skipped_has}")
    print(f"  sin schema aplicable: {skipped_none}")
    print(f"  omitidos (no legibles / sin </head>): {skipped_err}")


if __name__ == "__main__":
    main()
