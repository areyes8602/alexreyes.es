#!/usr/bin/env python3
"""Build archived (non-active) subject landings in 3 languages.

For each archived subject, generates:
  /docencia/<code>/index.html        (Spanish landing)
  /ca/docencia/<code>/index.html     (Catalan landing)
  /en/docencia/<code>/index.html     (English landing)

And ensures a centralized data file exists:
  /assets/data/archive/<code>.json   (single source of truth for years)

The landings fetch the centralized years.json and render a card grid
per language. Year cards link to the same-language year hub.

Re-run after editing the SUBJECTS or LABELS dicts to keep all 3 langs in sync.
"""
import json
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
ARCHIVE_DATA = REPO / "assets" / "data" / "archive"

# ─── Per-subject configuration ───────────────────────────────────
SUBJECTS = [
    {
        "code": "eso-1",
        "block": "ESO",
        "title": {"es": "Matemàtiques 1r ESO", "ca": "Matemàtiques 1r ESO", "en": "Maths 1st ESO"},
        "h1":    {"es": "Matemàtiques 1r ESO", "ca": "Matemàtiques 1r ESO", "en": "Maths 1st ESO"},
        "desc":  {"es": "Primer de ESO &mdash; currículum LOMLOE.",
                  "ca": "Primer d'ESO &mdash; currículum LOMLOE.",
                  "en": "1st year of ESO &mdash; LOMLOE curriculum."},
        "curs":  {"es": "1º ESO", "ca": "1r ESO", "en": "1st ESO"},
    },
    {
        "code": "eso-3",
        "block": "ESO",
        "title": {"es": "Matemàtiques 3r ESO", "ca": "Matemàtiques 3r ESO", "en": "Maths 3rd ESO"},
        "h1":    {"es": "Matemàtiques 3r ESO", "ca": "Matemàtiques 3r ESO", "en": "Maths 3rd ESO"},
        "desc":  {"es": "Tercero de ESO &mdash; currículum LOMLOE.",
                  "ca": "Tercer d'ESO &mdash; currículum LOMLOE.",
                  "en": "3rd year of ESO &mdash; LOMLOE curriculum."},
        "curs":  {"es": "3º ESO", "ca": "3r ESO", "en": "3rd ESO"},
    },
    {
        "code": "eso-4",
        "block": "ESO",
        "title": {"es": "Matemàtiques 4t ESO", "ca": "Matemàtiques 4t ESO", "en": "Maths 4th ESO"},
        "h1":    {"es": "Matemàtiques 4t ESO", "ca": "Matemàtiques 4t ESO", "en": "Maths 4th ESO"},
        "desc":  {"es": "Cuarto de ESO &mdash; currículum LOMLOE.",
                  "ca": "Quart d'ESO &mdash; currículum LOMLOE.",
                  "en": "4th year of ESO &mdash; LOMLOE curriculum."},
        "curs":  {"es": "4º ESO", "ca": "4t ESO", "en": "4th ESO"},
    },
    {
        "code": "ccss-2btl",
        "block": {"es": "Bachillerato", "ca": "Batxillerat", "en": "Bachillerato"},
        "title": {"es": "Mat. Aplicadas CCSS 2º BTL",
                  "ca": "Mat. Aplicades CCSS 2n BTL",
                  "en": "Applied Math. Social Sciences 2nd BTL"},
        "h1":    {"es": "Mat. Aplicadas a las CCSS",
                  "ca": "Mat. Aplicades a les CCSS",
                  "en": "Applied Maths for Social Sciences"},
        "desc":  {"es": "2&ordm; de Bachillerato &mdash; Modalidad Ciencias Sociales.",
                  "ca": "2n de Batxillerat &mdash; Modalitat Ciències Socials.",
                  "en": "2nd year of Bachillerato &mdash; Social Sciences track."},
        "curs":  {"es": "2º Bachillerato", "ca": "2n Batxillerat", "en": "2nd Bachillerato"},
    },
    {
        "code": "cientific-1btl",
        "block": {"es": "Bachillerato", "ca": "Batxillerat", "en": "Bachillerato"},
        "title": {"es": "Matemáticas 1º BTL Científico",
                  "ca": "Matemàtiques 1r BTL Científic",
                  "en": "Mathematics 1st BTL Science"},
        "h1":    {"es": "Matemáticas 1º BTL Científico",
                  "ca": "Matemàtiques 1r BTL Científic",
                  "en": "Mathematics 1st BTL Science"},
        "desc":  {"es": "1&ordm; de Bachillerato &mdash; Modalidad Ciencias y Tecnología.",
                  "ca": "1r de Batxillerat &mdash; Modalitat Ciències i Tecnologia.",
                  "en": "1st year of Bachillerato &mdash; Science &amp; Technology track."},
        "curs":  {"es": "1º Bachillerato", "ca": "1r Batxillerat", "en": "1st Bachillerato"},
    },
    {
        "code": "cientific-2btl",
        "block": {"es": "Bachillerato", "ca": "Batxillerat", "en": "Bachillerato"},
        "title": {"es": "Matemáticas 2º BTL Científico",
                  "ca": "Matemàtiques 2n BTL Científic",
                  "en": "Mathematics 2nd BTL Science"},
        "h1":    {"es": "Matemáticas 2º BTL Científico",
                  "ca": "Matemàtiques 2n BTL Científic",
                  "en": "Mathematics 2nd BTL Science"},
        "desc":  {"es": "2&ordm; de Bachillerato &mdash; Modalidad Ciencias y Tecnología.",
                  "ca": "2n de Batxillerat &mdash; Modalitat Ciències i Tecnologia.",
                  "en": "2nd year of Bachillerato &mdash; Science &amp; Technology track."},
        "curs":  {"es": "2º Bachillerato", "ca": "2n Batxillerat", "en": "2nd Bachillerato"},
    },
]

LANGS = ["es", "ca", "en"]

LABELS = {
    "es": {
        "html_lang": "es",
        "home": "Inicio", "docencia": "Docencia",
        "doctorado_nav": "Doctorado", "notas_nav": "Notas", "cv_nav": "CV", "contacto_nav": "Contacto",
        "lang_label": "ES",
        "no_years_h": "Todavía no he añadido cursos de esta asignatura",
        "no_years_p": "Esta materia forma parte de mi histórico docente. Iré subiendo material de los cursos en que la impartí.",
        "years_h2": "Cursos impartidos",
        "years_help": "Cada curso contiene los apuntes, fichas, soluciones y exámenes de aquel año académico.",
        "loading": "Cargando…",
        "section_label": "Información general",
        "archived_tag": "Archivada",
        "estado_label": "Estado",
        "estado_value": "Archivada",
        "courses_label": "Cursos",
        "curs_label": "Curso",
        "footer_brand": "Matemáticas, docencia y doctorado",
    },
    "ca": {
        "html_lang": "ca",
        "home": "Inici", "docencia": "Docència",
        "doctorado_nav": "Doctorat", "notas_nav": "Notes", "cv_nav": "CV", "contacto_nav": "Contacte",
        "lang_label": "CA",
        "no_years_h": "Encara no he afegit cursos d'aquesta assignatura",
        "no_years_p": "Aquesta matèria forma part del meu històric docent. Aviat aniré pujant material dels cursos en què la vaig impartir.",
        "years_h2": "Cursos impartits",
        "years_help": "Cada curs conté els apunts, fitxes, solucions i exàmens d'aquell any acadèmic.",
        "loading": "Carregant…",
        "section_label": "Informació general",
        "archived_tag": "Arxivada",
        "estado_label": "Estat",
        "estado_value": "Arxivada",
        "courses_label": "Cursos",
        "curs_label": "Curs",
        "footer_brand": "Matemàtiques, docència i doctorat",
    },
    "en": {
        "html_lang": "en",
        "home": "Home", "docencia": "Teaching",
        "doctorado_nav": "PhD", "notas_nav": "Notes", "cv_nav": "CV", "contacto_nav": "Contact",
        "lang_label": "EN",
        "no_years_h": "No academic years added yet for this subject",
        "no_years_p": "This subject is part of my teaching history. I'll progressively upload material from the years I taught it.",
        "years_h2": "Years taught",
        "years_help": "Each year contains the notes, exercise sheets, solutions and exams for that academic year.",
        "loading": "Loading…",
        "section_label": "General information",
        "archived_tag": "Archived",
        "estado_label": "Status",
        "estado_value": "Archived",
        "courses_label": "Years",
        "curs_label": "Year",
        "footer_brand": "Mathematics, teaching and research",
    },
}


def lang_prefix(lang):
    """URL prefix for a given language. ES is at root, others nested."""
    return "" if lang == "es" else f"/{lang}"


def nav_path(lang, page):
    """Build absolute URL for a nav target in a given language."""
    pre = lang_prefix(lang)
    return f"{pre}/{page}/"


def render_landing(s, lang):
    L = LABELS[lang]
    code = s["code"]
    title = s["title"][lang]
    h1 = s["h1"][lang]
    desc = s["desc"][lang]
    curs = s["curs"][lang]
    block = s["block"][lang] if isinstance(s["block"], dict) else s["block"]
    base_url = f"{lang_prefix(lang)}/docencia/{code}/"
    canonical = f"https://alexreyes.es{base_url}"
    es_canon = f"https://alexreyes.es/docencia/{code}/"
    ca_canon = f"https://alexreyes.es/ca/docencia/{code}/"
    en_canon = f"https://alexreyes.es/en/docencia/{code}/"
    # Lang switcher links (this same page in other langs)
    lang_switch = (
        f'<a href="/docencia/{code}/" class="{ "lang-active" if lang=="es" else "" }">ES</a><span class="lang-sep">&middot;</span>'
        f'<a href="/ca/docencia/{code}/" class="{ "lang-active" if lang=="ca" else "" }">CA</a><span class="lang-sep">&middot;</span>'
        f'<a href="/en/docencia/{code}/" class="{ "lang-active" if lang=="en" else "" }">EN</a>'
    )

    nav_links = (
        f'<a href="{nav_path(lang,"docencia")}" class="nav-active">{L["docencia"]}</a>'
        f'<a href="{nav_path(lang,"doctorado")}">{L["doctorado_nav"]}</a>'
        f'<a href="{nav_path(lang,"notas")}">{L["notas_nav"]}</a>'
        f'<a href="{nav_path(lang,"cv")}">{L["cv_nav"]}</a>'
        f'<a href="{nav_path(lang,"contacto")}">{L["contacto_nav"]}</a>'
    )
    nav_brand = f'<a href="{lang_prefix(lang)}/" class="nav-brand">alexreyes.es</a>'

    breadcrumb = (
        f'<a href="{lang_prefix(lang)}/">{L["home"]}</a>'
        f'<span class="sep">/</span>'
        f'<a href="{nav_path(lang,"docencia")}">{L["docencia"]}</a>'
        f'<span class="sep">/</span>'
        f'<span class="current">{title}</span>'
    )

    return f"""<!DOCTYPE html>
<html lang="{L['html_lang']}">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title} — Àlex Reyes</title>
<meta name="description" content="{title} — històric docent.">
<script>(function(){{var s=localStorage.getItem('theme');if(s)document.documentElement.setAttribute('data-theme',s);else document.documentElement.setAttribute('data-theme','light');}})();</script>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
<link rel="stylesheet" href="/style.css">
<link rel="icon" type="image/svg+xml" href="/favicon.svg">
<link rel="canonical" href="{canonical}">
<link rel="alternate" hreflang="es" href="{es_canon}">
<link rel="alternate" hreflang="ca" href="{ca_canon}">
<link rel="alternate" hreflang="en" href="{en_canon}">
<link rel="alternate" hreflang="x-default" href="{es_canon}">
<style>
  .year-grid {{ display:grid; grid-template-columns:repeat(auto-fill,minmax(220px,1fr)); gap:1rem; }}
  .year-card {{ background:var(--bg-subtle); border:1px solid var(--border); border-radius:var(--radius); padding:1.1rem 1.25rem; text-decoration:none; color:inherit; transition:border-color 0.15s, transform 0.15s; display:flex; flex-direction:column; gap:0.4rem; }}
  .year-card:hover {{ border-color:var(--border-strong); transform:translateY(-1px); }}
  .year-card-head {{ display:flex; align-items:center; justify-content:space-between; gap:0.5rem; }}
  .year-card-year {{ font-family:var(--mono); font-size:1.05rem; font-weight:600; color:var(--text); }}
  .year-card-meta {{ font-size:0.78rem; color:var(--text-faint); }}
  .year-card-center {{ font-size:0.85rem; color:var(--text-soft); margin:0; }}
  .year-card-arrow {{ font-size:0.9rem; color:var(--text-faint); }}
  .empty-state {{ text-align:center; padding:2.5rem 1.5rem; background:var(--bg-subtle); border:1px dashed var(--border); border-radius:var(--radius); }}
  .empty-state h3 {{ margin:0 0 0.5rem; font-size:1rem; font-weight:600; color:var(--text); }}
  .empty-state p {{ margin:0; font-size:0.9rem; color:var(--text-soft); max-width:36rem; margin-left:auto; margin-right:auto; }}
</style>
</head>
<body>
<nav>
  <div class="nav-inner">
    {nav_brand}
    <div class="nav-links">{nav_links}</div>
    <div class="nav-right">
      <div class="lang-sw">{lang_switch}</div>
      <button class="nav-hamburger" onclick="toggleMenu()" aria-label="Menu"><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><line x1="4" y1="7" x2="20" y2="7"/><line x1="4" y1="12" x2="20" y2="12"/><line x1="4" y1="17" x2="20" y2="17"/></svg></button>
      <button class="theme-btn" onclick="toggleTheme()" aria-label="Toggle theme">
        <svg class="icon-sun" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="5"/><line x1="12" y1="1" x2="12" y2="3"/><line x1="12" y1="21" x2="12" y2="23"/><line x1="4.22" y1="4.22" x2="5.64" y2="5.64"/><line x1="18.36" y1="18.36" x2="19.78" y2="19.78"/><line x1="1" y1="12" x2="3" y2="12"/><line x1="21" y1="12" x2="23" y2="12"/><line x1="4.22" y1="19.78" x2="5.64" y2="18.36"/><line x1="18.36" y1="5.64" x2="19.78" y2="4.22"/></svg>
        <svg class="icon-moon" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/></svg>
      </button>
    </div>
  </div>
</nav>

<main>
  <div class="container" style="padding-top:3rem;padding-bottom:5rem">

    <div class="breadcrumb">{breadcrumb}</div>

    <div class="page-header">
      <div style="display:flex;align-items:center;gap:0.6rem;margin-bottom:0.6rem;flex-wrap:wrap">
        <span class="section-label">{block}</span>
        <span class="tag tag-gray">{L['archived_tag']}</span>
      </div>
      <h1 style="margin:0.3rem 0 0.6rem">{h1}</h1>
      <p style="font-size:0.98rem;color:var(--text-soft)">{desc}</p>
    </div>

    <div class="info-grid">
      <div class="info-card"><div class="info-card-label">{L['curs_label']}</div><div class="info-card-value">{curs}</div></div>
      <div class="info-card"><div class="info-card-label">{L['estado_label']}</div><div class="info-card-value" style="font-size:0.88rem">{L['estado_value']}</div></div>
      <div class="info-card"><div class="info-card-label">{L['courses_label']}</div><div class="info-card-value" id="years-count">—</div></div>
    </div>

    <h2 style="font-size:1.1rem;margin:2.5rem 0 0.4rem">{L['years_h2']}</h2>
    <p style="color:var(--text-soft);font-size:0.92rem;margin-bottom:1rem">{L['years_help']}</p>
    <div id="years-container">
      <p style="color:var(--text-faint);font-size:0.9rem;padding:0.5rem 0">{L['loading']}</p>
    </div>

  </div>
</main>

<footer>
  <div class="container">
    <div class="footer-inner">
      <span><strong>Àlex Reyes</strong> &middot; {L['footer_brand']}</span>
      <span>Barcelona &middot; 2026</span>
    </div>
  </div>
</footer>

<script>
function toggleMenu(){{document.querySelector("nav").classList.toggle("open");}}
function toggleTheme(){{var h=document.documentElement,n=h.getAttribute('data-theme')==='dark'?'light':'dark';h.setAttribute('data-theme',n);localStorage.setItem('theme',n);}}
function escHtml(s){{ return String(s||'').replace(/[&<>"']/g, c => ({{'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}}[c])); }}

const NO_YEARS_H = {json.dumps(L['no_years_h'])};
const NO_YEARS_P = {json.dumps(L['no_years_p'])};
const BASE_URL = {json.dumps(base_url)};

fetch('/assets/data/archive/{code}.json', {{ cache: 'no-cache' }})
  .then(r => r.ok ? r.json() : Promise.reject(r.status))
  .then(data => {{
    const years = (data.years || []).slice().sort((a,b) => (b.year||'').localeCompare(a.year||''));
    document.getElementById('years-count').textContent = years.length || '0';
    const cont = document.getElementById('years-container');
    if (years.length === 0) {{
      cont.innerHTML = `<div class="empty-state"><h3>${{escHtml(NO_YEARS_H)}}</h3><p>${{escHtml(NO_YEARS_P)}}</p></div>`;
      return;
    }}
    cont.innerHTML = '<div class="year-grid">' + years.map(y => {{
      const center = y.center ? `<p class="year-card-center">${{escHtml(y.center)}}</p>` : '';
      const note = y.note ? `<span class="year-card-meta">${{escHtml(y.note)}}</span>` : '';
      return `
        <a href="${{BASE_URL}}${{escHtml(y.year)}}/" class="year-card">
          <div class="year-card-head">
            <span class="year-card-year">${{escHtml(y.year)}}</span>
            <span class="year-card-arrow">→</span>
          </div>
          ${{center}}
          ${{note}}
        </a>`;
    }}).join('') + '</div>';
  }})
  .catch(err => {{
    document.getElementById('years-count').textContent = '0';
    document.getElementById('years-container').innerHTML = `<div class="empty-state"><h3>${{escHtml(NO_YEARS_H)}}</h3><p>${{escHtml(NO_YEARS_P)}}</p></div>`;
    console.error('archive years:', err);
  }});
</script>
</body>
</html>
"""


def main():
    ARCHIVE_DATA.mkdir(parents=True, exist_ok=True)
    for s in SUBJECTS:
        # 1) Centralized years.json (preserve existing data if present)
        json_path = ARCHIVE_DATA / f"{s['code']}.json"
        if not json_path.exists():
            # Try to migrate from old per-language location
            old = REPO / "docencia" / s["code"] / "years.json"
            if old.exists():
                data = json.loads(old.read_text(encoding="utf-8"))
            else:
                data = {"years": []}
            json_path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

        # 2) Generate landing in 3 languages
        for lang in LANGS:
            if lang == "es":
                out = REPO / "docencia" / s["code"] / "index.html"
            else:
                out = REPO / lang / "docencia" / s["code"] / "index.html"
            out.parent.mkdir(parents=True, exist_ok=True)
            out.write_text(render_landing(s, lang), encoding="utf-8")
            print(f"  ✓ {out.relative_to(REPO)}")

        # 3) Remove obsolete per-language years.json (now centralized)
        for lang in LANGS:
            old_yj = (REPO / "docencia" / s["code"] / "years.json") if lang == "es" \
                     else (REPO / lang / "docencia" / s["code"] / "years.json")
            # We keep the ES path's years.json deletion to "later" (manual cleanup)


if __name__ == "__main__":
    main()
