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
.tl{position:relative;max-width:780px;margin:2.2rem auto 0}
.tl-band{position:relative;min-height:6rem}
.tl-band::before{content:'';position:absolute;left:50%;top:0;bottom:0;width:3px;margin-left:-1.5px;background:#6366f1;z-index:0}
.tl-band.ext::before{background:#d97706}
.tl-yr{position:relative;z-index:3;text-align:center;padding:0.4rem 0 0.7rem}
.tl-yr span{background:var(--bg);border:1px solid var(--border-strong);border-radius:999px;padding:0.12rem 0.65rem;font-family:'JetBrains Mono',ui-monospace,monospace;font-size:0.75rem;font-weight:600;color:var(--text-faint)}
.tl-band.ext .tl-yr span{border-color:#d97706;color:#d97706}
.tl-item{position:relative;width:50%;box-sizing:border-box;padding:0.35rem 2.2rem 0.95rem;opacity:0;transform:translateY(14px);transition:opacity .5s ease,transform .5s ease}
.tl-item.in{opacity:1;transform:none}
.tl-item.left{left:0}
.tl-item.right{left:50%}
.tl-card{position:relative;z-index:1;background:var(--bg-subtle);border:1px solid var(--border);border-radius:10px;padding:0.7rem 0.95rem;transition:transform .15s,box-shadow .15s,border-color .15s}
.tl-card:hover{transform:translateY(-3px);box-shadow:0 6px 18px rgba(0,0,0,.09);border-color:var(--border-strong)}
.tl-item::after{content:'';position:absolute;top:0.95rem;width:15px;height:15px;border-radius:50%;background:#6366f1;border:3px solid var(--bg);z-index:2;transition:transform .15s}
.tl-item:hover::after{transform:scale(1.25)}
.tl-item.left::after{right:-7.5px}
.tl-item.right::after{left:-7.5px}
.tl-band.ext .tl-item::after{background:#d97706}
.tl-item.now::after{background:#10b981;animation:tlPulse 2s infinite}
@keyframes tlPulse{0%{box-shadow:0 0 0 0 rgba(16,185,129,.5)}70%{box-shadow:0 0 0 12px rgba(16,185,129,0)}100%{box-shadow:0 0 0 0 rgba(16,185,129,0)}}
.tl-card::before{content:'';position:absolute;top:0.85rem;border:8px solid transparent}
.tl-item.left .tl-card::before{right:-15px;border-left-color:var(--bg-subtle)}
.tl-item.right .tl-card::before{left:-15px;border-right-color:var(--bg-subtle)}
.tl-date{font-family:'JetBrains Mono',ui-monospace,monospace;font-size:0.78rem;font-weight:600;color:#6366f1}
.tl-band.ext .tl-date{color:#d97706}
.tl-item.now .tl-date{color:#10b981}
.tl-now-label{display:inline-block;font-size:0.66rem;font-weight:600;color:#10b981;border:1px solid #10b981;border-radius:999px;padding:0 0.45rem;margin-left:0.4rem;vertical-align:middle}
.tl-card p{margin:0.25rem 0 0;color:var(--text-soft);font-size:0.92rem;line-height:1.5}
@media(prefers-reduced-motion:reduce){.tl-item{opacity:1;transform:none;transition:none}.tl-item.now::after{animation:none}}
@media(max-width:640px){
.tl-band::before{left:8px;margin-left:0}
.tl-yr{text-align:left;padding-left:0}
.tl-item,.tl-item.left,.tl-item.right{width:100%;left:0;padding:0.35rem 0 0.95rem 2.2rem}
.tl-item::after,.tl-item.left::after,.tl-item.right::after{left:1px;right:auto}
.tl-card::before,.tl-item.left .tl-card::before,.tl-item.right .tl-card::before{left:-15px;right:auto;border-right-color:var(--bg-subtle);border-left-color:transparent}
}
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
    bands = []
    idx = 0
    for y in range(ys, ye + 1):
        band_cls = " ext" if y > sp else ""
        items = ""
        for h in by_year.get(y, []):
            is_now = h["type"] == "now"
            side = "left" if idx % 2 == 0 else "right"
            idx += 1
            nowlbl = f'<span class="tl-now-label">{NOW[lang]}</span>' if is_now else ""
            items += (f'<div class="tl-item {side}{" now" if is_now else ""}">'
                      f'<div class="tl-card"><span class="tl-date">{h["date"][lang]}</span>{nowlbl}'
                      f'<p>{h["text"][lang]}</p></div></div>')
        bands.append(f'<div class="tl-band{band_cls}"><div class="tl-yr"><span>{y}</span></div>{items}</div>')
    return '<div class="tl">' + "".join(bands) + "</div>"


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
(function(){{var items=document.querySelectorAll('.tl-item');if(!('IntersectionObserver' in window)){{items.forEach(function(i){{i.classList.add('in');}});return;}}var io=new IntersectionObserver(function(es){{es.forEach(function(e){{if(e.isIntersecting){{e.target.classList.add('in');io.unobserve(e.target);}}}});}},{{threshold:0.15}});items.forEach(function(i){{io.observe(i);}});}})();
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
