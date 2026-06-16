#!/usr/bin/env python3
"""build_cronologia.py — Genera la cronología del doctorado (es/ca/en).

Página autocontenida: lee assets/data/cronologia-doctorado.json y escribe las
tres versiones completas:

    doctorado/cronologia/index.html        (es)
    ca/doctorado/cronologia/index.html     (ca)
    en/doctorado/cronologia/index.html     (en)

Línea del tiempo vertical y graduada por años. Tramo year_start..split en color
principal (indigo); split+1..year_end en color de prórroga (ámbar, discontinuo).
El hito con type "now" marca el momento actual. Edita el JSON y re-ejecuta.
"""
import json
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
DATA = REPO / "assets/data/cronologia-doctorado.json"

NOW = {"es": "Ahora", "ca": "Ara", "en": "Now"}
CFG = {
    "es": {"path": "doctorado/cronologia/index.html", "lang": "es", "loc": "es_ES", "alts": ["ca_ES", "en_US"],
           "title": "Cronología — Doctorado — Àlex Reyes",
           "desc": "Cronología del doctorado de Àlex Reyes: hitos, periodo 2026–2033 (tiempo parcial) y posible prórroga.",
           "skip": "Saltar al contenido", "brand": "/", "slabel": "Investigación doctoral", "h1": "Cronología",
           "crumb": [("Inicio", "/"), ("Doctorado", "/doctorado/"), ("Cronología", "/doctorado/cronologia/")],
           "links": [("/docencia/", "Docencia"), ("/doctorado/", "Doctorado"), ("/notas/", "Notas"), ("/cv/", "CV"), ("/contacto/", "Contacto")],
           "footer": '<span><strong>Àlex Reyes</strong> &middot; Matemáticas, docencia y doctorado</span>\n      <span>Barcelona &middot; &copy; 2026 Àlex Reyes &middot; <a href="/assets/NOTICES.txt" style="color:inherit">Licencias</a></span>'},
    "ca": {"path": "ca/doctorado/cronologia/index.html", "lang": "ca", "loc": "ca_ES", "alts": ["es_ES", "en_US"],
           "title": "Cronologia — Doctorat — Àlex Reyes",
           "desc": "Cronologia del doctorat d'Àlex Reyes: fites, període 2026–2033 (temps parcial) i possible pròrroga.",
           "skip": "Salta al contingut", "brand": "/ca/", "slabel": "Recerca doctoral", "h1": "Cronologia",
           "crumb": [("Inici", "/ca/"), ("Doctorat", "/ca/doctorado/"), ("Cronologia", "/ca/doctorado/cronologia/")],
           "links": [("/ca/docencia/", "Docència"), ("/ca/doctorado/", "Doctorat"), ("/ca/notas/", "Notes"), ("/ca/cv/", "CV"), ("/ca/contacto/", "Contacte")],
           "footer": '<span><strong>Àlex Reyes</strong> &middot; Matemàtiques, docència i doctorat</span>\n      <span>Barcelona &middot; &copy; 2026 Àlex Reyes &middot; <a href="/assets/NOTICES.txt" style="color:inherit">Licencias</a></span>'},
    "en": {"path": "en/doctorado/cronologia/index.html", "lang": "en", "loc": "en_US", "alts": ["es_ES", "ca_ES"],
           "title": "Timeline — PhD — Àlex Reyes",
           "desc": "Timeline of Àlex Reyes's PhD: milestones, 2026–2033 period (part-time) and a possible extension.",
           "skip": "Skip to content", "brand": "/en/", "slabel": "Doctoral research", "h1": "Timeline",
           "crumb": [("Home", "/en/"), ("PhD", "/en/doctorado/"), ("Timeline", "/en/doctorado/cronologia/")],
           "links": [("/en/docencia/", "Teaching"), ("/en/doctorado/", "PhD"), ("/en/notas/", "Notes"), ("/en/cv/", "CV"), ("/en/contacto/", "Contact")],
           "footer": '<span><strong>Àlex Reyes</strong> &middot; Mathematics, teaching and research</span>\n      <span>Barcelona &middot; 2026</span>'},
}
CANON = {"es": "/doctorado/cronologia/", "ca": "/ca/doctorado/cronologia/", "en": "/en/doctorado/cronologia/"}
BASE = "https://alexreyes.es"

STYLE = """<style>
.tl-intro{font-size:1rem;color:var(--text-soft)}
.tl{margin:1.8rem 0 0}
.tl-year{position:relative;padding:0 0 0 1.6rem;border-left:2px solid #6366f1}
.tl-year[data-seg="ext"]{border-left-style:dashed;border-left-color:#d97706}
.tl-tick{position:absolute;left:0;top:-0.55rem;transform:translateX(-50%);background:var(--bg);padding:0 0.35rem;font-family:'JetBrains Mono',ui-monospace,monospace;font-size:0.8rem;font-weight:600;color:var(--text-faint)}
.tl-events{padding:0.5rem 0 1.5rem}
.tl-events:empty{padding:0.7rem 0}
.tl-event{position:relative;margin:0 0 0.95rem}
.tl-event:last-child{margin-bottom:0}
.tl-event::before{content:'';position:absolute;left:calc(-1.6rem - 1px);top:0.3rem;width:10px;height:10px;border-radius:50%;background:#6366f1;border:2px solid var(--bg);transform:translateX(-50%)}
.tl-event[data-seg="ext"]::before{background:#d97706}
.tl-event.tl-now::before{background:#10b981;box-shadow:0 0 0 4px rgba(16,185,129,.18)}
.tl-date{font-family:'JetBrains Mono',ui-monospace,monospace;font-size:0.8rem;font-weight:600;color:#6366f1}
.tl-event[data-seg="ext"] .tl-date{color:#d97706}
.tl-now .tl-date{color:#10b981}
.tl-now-label{display:inline-block;font-size:0.68rem;font-weight:600;color:#10b981;border:1px solid #10b981;border-radius:999px;padding:0 0.5rem;margin-left:0.45rem;vertical-align:middle}
.tl-event p{margin:0.2rem 0 0;color:var(--text-soft);font-size:0.95rem;line-height:1.5}
</style>"""

KATEX = """<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/katex.min.css" integrity="sha384-n8MVd4RsNIU0tAv4ct0nTaAbDJwPJzDEaqSD1odI+WdtXRGWt2kTvGFasHpSy3SV" crossorigin="anonymous" media="print" onload="this.media='all'"><noscript><link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/katex.min.css" integrity="sha384-n8MVd4RsNIU0tAv4ct0nTaAbDJwPJzDEaqSD1odI+WdtXRGWt2kTvGFasHpSy3SV" crossorigin="anonymous"></noscript>
<script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/katex.min.js" integrity="sha384-XjKyOOlGwcjNTAIQHIpgOno0Hl1YQqzUOEleOLALmuqehneUG+vnGctmUb0ZY0l8" crossorigin="anonymous"></script>
<script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/contrib/auto-render.min.js" integrity="sha384-+VBxd3r6XgURycqtZ117nYw44OOcIax56Z4dCRWbxyPt0Koah1uHoK0o4+/RRE05" crossorigin="anonymous" onload="renderMathInElement(document.body,{delimiters:[{left:'$$',right:'$$',display:true},{left:'\\\\[',right:'\\\\]',display:true},{left:'$',right:'$',display:false},{left:'\\\\(',right:'\\\\)',display:false}],throwOnError:false})"></script>"""

ICONS = ('<button class="nav-hamburger" onclick="toggleMenu()" aria-label="Menu"><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><line x1="4" y1="7" x2="20" y2="7"/><line x1="4" y1="12" x2="20" y2="12"/><line x1="4" y1="17" x2="20" y2="17"/></svg></button>\n'
         '      <button class="theme-btn" onclick="toggleTheme()" aria-label="Toggle theme">\n'
         '        <svg class="icon-sun" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="5"/><line x1="12" y1="1" x2="12" y2="3"/><line x1="12" y1="21" x2="12" y2="23"/><line x1="4.22" y1="4.22" x2="5.64" y2="5.64"/><line x1="18.36" y1="18.36" x2="19.78" y2="19.78"/><line x1="1" y1="12" x2="3" y2="12"/><line x1="21" y1="12" x2="23" y2="12"/><line x1="4.22" y1="19.78" x2="5.64" y2="18.36"/><line x1="18.36" y1="5.64" x2="19.78" y2="4.22"/></svg>\n'
         '        <svg class="icon-moon" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/></svg>\n      </button>')


def langsw(active):
    parts = []
    for code, path in (("ES", "/doctorado/cronologia/"), ("CA", "/ca/doctorado/cronologia/"), ("EN", "/en/doctorado/cronologia/")):
        cls = ' class="lang-active"' if code == active else ''
        parts.append(f'<a href="{path}"{cls}>{code}</a>')
    return '<span class="lang-sep">&middot;</span>'.join(parts)


def nav(c, active_code):
    # marca activo el enlace de Doctorado
    rows = []
    for h, t in c["links"]:
        cls = ' class="nav-active"' if h == c["crumb"][1][1] else ''
        rows.append(f'      <a href="{h}"{cls}>{t}</a>')
    links = "\n".join(rows)
    return ('<nav>\n  <div class="nav-inner">\n'
            f'    <a href="{c["brand"]}" class="nav-brand">alexreyes.es</a>\n'
            f'    <div class="nav-links">\n{links}\n    </div>\n'
            '    <div class="nav-right">\n'
            f'      <div class="lang-sw">\n        {langsw(active_code.upper())}\n      </div>\n'
            f'      {ICONS}\n    </div>\n  </div>\n</nav>')


def timeline(data, lang):
    ys, sp, ye = data["year_start"], data["split"], data["year_end"]
    by_year = {}
    for h in data["hitos"]:
        by_year.setdefault(h["year"], []).append(h)
    rows = []
    for y in range(ys, ye + 1):
        seg = "main" if y <= sp else "ext"
        evs = ""
        for h in by_year.get(y, []):
            is_now = h["type"] == "now"
            seg_e = "now" if is_now else ("ext" if y > sp else "main")
            nowlbl = f'<span class="tl-now-label">{NOW[lang]}</span>' if is_now else ""
            evs += (f'<div class="tl-event{" tl-now" if is_now else ""}" data-seg="{seg_e}">'
                    f'<span class="tl-date">{h["date"][lang]}</span>{nowlbl}'
                    f'<p>{h["text"][lang]}</p></div>')
        rows.append(f'<div class="tl-year" data-seg="{seg}"><span class="tl-tick">{y}</span>'
                    f'<div class="tl-events">{evs}</div></div>')
    return '<div class="tl">' + "".join(rows) + "</div>"


def page(c, lang, data):
    canon = BASE + CANON[lang]
    hreflang = "\n".join(
        f'<link rel="alternate" hreflang="{hl}" href="{BASE}{CANON[hl]}">'
        for hl in ("es", "ca", "en")) + f'\n<link rel="alternate" hreflang="x-default" href="{BASE}{CANON["es"]}">'
    crumb_ld = ",".join(
        '{"@type":"ListItem","position":%d,"name":"%s","item":"%s%s"}' % (i + 1, n, BASE, u)
        for i, (n, u) in enumerate(c["crumb"]))
    crumb_html = ('\n      <span class="sep">/</span>\n      '.join(
        ([f'<a href="{c["crumb"][0][1]}">{c["crumb"][0][0]}</a>',
          f'<a href="{c["crumb"][1][1]}">{c["crumb"][1][0]}</a>',
          f'<span class="current">{c["crumb"][2][0]}</span>'])))
    return f"""<!DOCTYPE html>
<html lang="{c['lang']}">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{c['title']}</title>
<meta name="description" content="{c['desc']}">
<script>(function(){{var s=localStorage.getItem('theme');if(s)document.documentElement.setAttribute('data-theme',s);else document.documentElement.setAttribute('data-theme','light');}})();</script>
<script src="/assets/js/lang-persist.js"></script>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap" media="print" onload="this.media='all'"><noscript><link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap"></noscript>
{KATEX}
<link rel="stylesheet" href="/style.css?v=202606161502">
<link rel="icon" type="image/svg+xml" href="/favicon.svg">
<link rel="canonical" href="{canon}">
{hreflang}
<meta property="og:type" content="website">
<meta property="og:url" content="{canon}">
<meta property="og:title" content="{c['title']}">
<meta property="og:description" content="{c['desc']}">
<meta property="og:image" content="{BASE}/og-image.jpg">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:locale" content="{c['loc']}">
<meta property="og:locale:alternate" content="{c['alts'][0]}">
<meta property="og:locale:alternate" content="{c['alts'][1]}">
<meta property="og:site_name" content="alexreyes.es">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{c['title']}">
<meta name="twitter:description" content="{c['desc']}">
<meta name="twitter:image" content="{BASE}/og-image.jpg">
<script type="application/ld+json">{{"@context":"https://schema.org","@type":"BreadcrumbList","itemListElement":[{crumb_ld}]}}</script>
{STYLE}
</head>
<body>
<a class="skip-link" href="#main">{c['skip']}</a>
{nav(c, lang)}

<main id="main">
  <div class="container" style="padding-top:3rem;padding-bottom:5rem">

    <div class="breadcrumb">
      {crumb_html}
    </div>

    <div class="page-header">
      <div style="display:flex;align-items:center;gap:0.6rem;margin-bottom:0.6rem;flex-wrap:wrap">
        <span class="section-label">{c['slabel']}</span>
        <span class="tag tag-purple">{c['h1']}</span>
      </div>
      <h1 style="margin:0.3rem 0 0.8rem">{c['h1']}</h1>
      <p class="tl-intro">{data['intro'][lang]}</p>
    </div>

    {timeline(data, lang)}

  </div>
</main>

<footer>
  <div class="container">
    <div class="footer-inner">
      {c['footer']}
    </div>
  </div>
</footer>

<script>
function toggleMenu(){{document.querySelector("nav").classList.toggle("open");}}function toggleTheme(){{var h=document.documentElement,n=h.getAttribute('data-theme')==='dark'?'light':'dark';h.setAttribute('data-theme',n);localStorage.setItem('theme',n);}}
</script>
<script defer src="/assets/js/search.js"></script>
</body>
</html>
"""


def main():
    data = json.loads(DATA.read_text(encoding="utf-8"))
    for lang, c in CFG.items():
        out = REPO / c["path"]
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(page(c, lang, data), encoding="utf-8")
    print(f"✓ cronología: {len(data['hitos'])} hitos × 3 idiomas (es, ca, en)")


if __name__ == "__main__":
    main()
