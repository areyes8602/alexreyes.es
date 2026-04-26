#!/usr/bin/env python3
"""Add a course year to an archived (non-active) subject — TRILINGUAL.

For a given subject + year, generates 3 language versions of the year hub
and the year info subpage:

  /docencia/<subject>/<year>/index.html         (ES year hub)
  /docencia/<subject>/<year>/info/index.html    (ES info subpage)
  /ca/docencia/<subject>/<year>/index.html      (CA year hub)
  /ca/docencia/<subject>/<year>/info/index.html (CA info subpage)
  /en/docencia/<subject>/<year>/index.html      (EN year hub)
  /en/docencia/<subject>/<year>/info/index.html (EN info subpage)

And updates the centralized data file:
  /assets/data/archive/<subject>.json

Usage:
  python3 scripts/add_archived_year.py <subject> <year> [--center "..."] [--note "..."]

Examples:
  python3 scripts/add_archived_year.py eso-3 2015-16 --center "Escola Meritxell"
  python3 scripts/add_archived_year.py ccss-2btl 2017-18 --center "Escola Meritxell" --note "Cap d'estudis"
"""
import argparse
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
ARCHIVE_DATA = REPO / "assets" / "data" / "archive"

LANGS = ["es", "ca", "en"]

# Per-subject configuration (must match build_archived_subjects.py)
SUBJECTS = {
    "eso-1": {
        "title": {"es": "Matemàtiques 1r ESO", "ca": "Matemàtiques 1r ESO", "en": "Maths 1st ESO"},
        "block": {"es": "ESO", "ca": "ESO", "en": "ESO"},
        "curs":  {"es": "1º ESO", "ca": "1r ESO", "en": "1st ESO"},
    },
    "eso-3": {
        "title": {"es": "Matemàtiques 3r ESO", "ca": "Matemàtiques 3r ESO", "en": "Maths 3rd ESO"},
        "block": {"es": "ESO", "ca": "ESO", "en": "ESO"},
        "curs":  {"es": "3º ESO", "ca": "3r ESO", "en": "3rd ESO"},
    },
    "eso-4": {
        "title": {"es": "Matemàtiques 4t ESO", "ca": "Matemàtiques 4t ESO", "en": "Maths 4th ESO"},
        "block": {"es": "ESO", "ca": "ESO", "en": "ESO"},
        "curs":  {"es": "4º ESO", "ca": "4t ESO", "en": "4th ESO"},
    },
    "ccss-2btl": {
        "title": {"es": "Mat. Aplicadas CCSS 2º BTL",
                  "ca": "Mat. Aplicades CCSS 2n BTL",
                  "en": "Applied Math. Social Sciences 2nd BTL"},
        "block": {"es": "Bachillerato", "ca": "Batxillerat", "en": "Bachillerato"},
        "curs":  {"es": "2º Bachillerato", "ca": "2n Batxillerat", "en": "2nd Bachillerato"},
    },
    "cientific-1btl": {
        "title": {"es": "Matemáticas 1º BTL Científico",
                  "ca": "Matemàtiques 1r BTL Científic",
                  "en": "Mathematics 1st BTL Science"},
        "block": {"es": "Bachillerato", "ca": "Batxillerat", "en": "Bachillerato"},
        "curs":  {"es": "1º Bachillerato", "ca": "1r Batxillerat", "en": "1st Bachillerato"},
    },
    "cientific-2btl": {
        "title": {"es": "Matemáticas 2º BTL Científico",
                  "ca": "Matemàtiques 2n BTL Científic",
                  "en": "Mathematics 2nd BTL Science"},
        "block": {"es": "Bachillerato", "ca": "Batxillerat", "en": "Bachillerato"},
        "curs":  {"es": "2º Bachillerato", "ca": "2n Batxillerat", "en": "2nd Bachillerato"},
    },
}

# i18n strings
LABELS = {
    "es": {
        "html_lang": "es",
        "home": "Inicio", "docencia": "Docencia",
        "doctorado_nav": "Doctorado", "notas_nav": "Notas", "cv_nav": "CV", "contacto_nav": "Contacto",
        "back_year": "Volver al hub del curso",
        "back_subject": "Volver a la asignatura",
        "info_title": "Información de la asignatura",
        "info_subtitle": "Horario, criterios de evaluación, temario, calendario y material necesario de aquel curso.",
        "info_subpage_title": "Información de la asignatura",
        "units_h2": "Unidades didácticas",
        "units_help": "Cada unidad contiene los apuntes de clase, las fichas de ejercicios con sus soluciones, y los exámenes realizados sobre la unidad.",
        "no_units_h": "Todavía no he añadido unidades de este curso",
        "no_units_p": "Iré subiendo material a medida que lo recupere.",
        "globals_h2": "Exámenes globales",
        "globals_help": "Globales de evaluación, simulacros, recuperaciones y exámenes finales.",
        "globals_empty": "Todavía no hay exámenes globales de este curso.",
        "info_block_horari": "Horario de clase",
        "info_block_aval": "Evaluación y criterios",
        "info_block_docs": "Documentos del curso",
        "info_block_mat": "Material necesario",
        "info_empty": "Todavía no he subido esta información.",
        "curs_label": "Curso",
        "year_label": "Curso académico",
        "footer_brand": "Matemáticas, docencia y doctorado",
    },
    "ca": {
        "html_lang": "ca",
        "home": "Inici", "docencia": "Docència",
        "doctorado_nav": "Doctorat", "notas_nav": "Notes", "cv_nav": "CV", "contacto_nav": "Contacte",
        "back_year": "Tornar al hub del curs",
        "back_subject": "Tornar a l'assignatura",
        "info_title": "Informació de l'assignatura",
        "info_subtitle": "Horari, criteris d'avaluació, temari, calendari i material necessari d'aquell curs.",
        "info_subpage_title": "Informació de l'assignatura",
        "units_h2": "Unitats didàctiques",
        "units_help": "Cada unitat conté els apunts de classe, les fitxes d'exercicis amb les seves solucions, i els exàmens realitzats sobre la unitat.",
        "no_units_h": "Encara no he afegit unitats d'aquest curs",
        "no_units_p": "Aniré pujant material a mesura que el recuperi.",
        "globals_h2": "Exàmens globals",
        "globals_help": "Globals d'avaluació, simulacres, recuperacions i exàmens finals.",
        "globals_empty": "Encara no hi ha exàmens globals d'aquest curs.",
        "info_block_horari": "Horari de classe",
        "info_block_aval": "Avaluació i criteris",
        "info_block_docs": "Documents del curs",
        "info_block_mat": "Material necessari",
        "info_empty": "Encara no he pujat aquesta informació.",
        "curs_label": "Curs",
        "year_label": "Curs acadèmic",
        "footer_brand": "Matemàtiques, docència i doctorat",
    },
    "en": {
        "html_lang": "en",
        "home": "Home", "docencia": "Teaching",
        "doctorado_nav": "PhD", "notas_nav": "Notes", "cv_nav": "CV", "contacto_nav": "Contact",
        "back_year": "Back to the year hub",
        "back_subject": "Back to the subject",
        "info_title": "Subject information",
        "info_subtitle": "Schedule, assessment criteria, syllabus, calendar and required material for that academic year.",
        "info_subpage_title": "Subject information",
        "units_h2": "Teaching units",
        "units_help": "Each unit contains the class notes, exercise sheets with solutions, and exams from that unit.",
        "no_units_h": "No units added yet for this year",
        "no_units_p": "I'll upload material as I recover it from my archive.",
        "globals_h2": "Comprehensive exams",
        "globals_help": "Term-final exams, mocks, retakes and final exams.",
        "globals_empty": "No comprehensive exams added for this year yet.",
        "info_block_horari": "Class schedule",
        "info_block_aval": "Assessment criteria",
        "info_block_docs": "Course documents",
        "info_block_mat": "Required material",
        "info_empty": "Information not uploaded yet.",
        "curs_label": "Year",
        "year_label": "Academic year",
        "footer_brand": "Mathematics, teaching and research",
    },
}


def lang_prefix(lang):
    return "" if lang == "es" else f"/{lang}"


def nav_path(lang, page):
    pre = lang_prefix(lang)
    return f"{pre}/{page}/"


def lang_switch_html(lang, code, year, suffix=""):
    """suffix = '' for hub, 'info/' for info subpage."""
    paths = {
        "es": f"/docencia/{code}/{year}/{suffix}",
        "ca": f"/ca/docencia/{code}/{year}/{suffix}",
        "en": f"/en/docencia/{code}/{year}/{suffix}",
    }
    parts = []
    for code_lang in ("es", "ca", "en"):
        cls = ' class="lang-active"' if code_lang == lang else ""
        parts.append(f'<a href="{paths[code_lang]}"{cls}>{code_lang.upper()}</a>')
    return '<span class="lang-sep">&middot;</span>'.join(parts)


def nav_block(lang):
    L = LABELS[lang]
    nav_links = (
        f'<a href="{nav_path(lang,"docencia")}" class="nav-active">{L["docencia"]}</a>'
        f'<a href="{nav_path(lang,"doctorado")}">{L["doctorado_nav"]}</a>'
        f'<a href="{nav_path(lang,"notas")}">{L["notas_nav"]}</a>'
        f'<a href="{nav_path(lang,"cv")}">{L["cv_nav"]}</a>'
        f'<a href="{nav_path(lang,"contacto")}">{L["contacto_nav"]}</a>'
    )
    return nav_links


def render_year_hub(code, year, lang, center, note):
    L = LABELS[lang]
    s = SUBJECTS[code]
    title = s["title"][lang]
    block = s["block"][lang]
    curs = s["curs"][lang]
    base_url = f"{lang_prefix(lang)}/docencia/{code}/{year}/"
    info_url = f"{base_url}info/"
    parent_url = f"{lang_prefix(lang)}/docencia/{code}/"
    canonical = f"https://alexreyes.es{base_url}"
    es_canon = f"https://alexreyes.es/docencia/{code}/{year}/"
    ca_canon = f"https://alexreyes.es/ca/docencia/{code}/{year}/"
    en_canon = f"https://alexreyes.es/en/docencia/{code}/{year}/"

    center_html = f'<span class="tag tag-gray">{center}</span>' if center else ''
    note_html = f'<p style="font-size:0.88rem;color:var(--text-faint);margin-top:0.4rem">{note}</p>' if note else ''

    breadcrumb = (
        f'<a href="{lang_prefix(lang)}/">{L["home"]}</a>'
        f'<span class="sep">/</span>'
        f'<a href="{nav_path(lang,"docencia")}">{L["docencia"]}</a>'
        f'<span class="sep">/</span>'
        f'<a href="{parent_url}">{title}</a>'
        f'<span class="sep">/</span>'
        f'<span class="current">{year}</span>'
    )

    return f"""<!DOCTYPE html>
<html lang="{L['html_lang']}">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title} ({year}) — Àlex Reyes</title>
<meta name="description" content="{title} — {L['year_label']} {year}.">
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
  .info-cta {{ display:flex; align-items:center; gap:1.2rem; padding:1.2rem 1.5rem; background:var(--bg-subtle); border:1px solid var(--border); border-radius:var(--radius); text-decoration:none; color:inherit; transition:border-color 0.15s, transform 0.15s; margin-bottom:2rem; }}
  .info-cta:hover {{ border-color:var(--border-strong); transform:translateY(-1px); }}
  .info-cta-icon {{ font-size:2rem; flex:0 0 auto; }}
  .info-cta-body {{ flex:1; min-width:0; }}
  .info-cta-body h3 {{ margin:0 0 0.25rem; font-size:1.05rem; font-weight:600; color:var(--text); }}
  .info-cta-body p {{ margin:0; font-size:0.88rem; color:var(--text-soft); }}
  .info-cta-arrow {{ font-size:1.2rem; color:var(--text-faint); flex:0 0 auto; }}
  .empty-state {{ text-align:center; padding:2rem 1.5rem; background:var(--bg-subtle); border:1px dashed var(--border); border-radius:var(--radius); }}
  .empty-state h3 {{ margin:0 0 0.4rem; font-size:0.95rem; font-weight:600; color:var(--text); }}
  .empty-state p {{ margin:0; font-size:0.88rem; color:var(--text-soft); }}
</style>
</head>
<body>
<nav>
  <div class="nav-inner">
    <a href="{lang_prefix(lang)}/" class="nav-brand">alexreyes.es</a>
    <div class="nav-links">{nav_block(lang)}</div>
    <div class="nav-right">
      <div class="lang-sw">{lang_switch_html(lang, code, year)}</div>
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
        <span class="tag tag-orange">{year}</span>
        {center_html}
      </div>
      <h1 style="margin:0.3rem 0 0.6rem">{title}</h1>
      <p style="font-size:0.98rem;color:var(--text-soft)">{L['year_label']} {year}.</p>
      {note_html}
    </div>

    <div class="info-grid">
      <div class="info-card"><div class="info-card-label">{L['curs_label']}</div><div class="info-card-value">{curs}</div></div>
      <div class="info-card"><div class="info-card-label">{L['year_label']}</div><div class="info-card-value">{year}</div></div>
    </div>

    <a href="{info_url}" class="info-cta">
      <span class="info-cta-icon">📋</span>
      <div class="info-cta-body">
        <h3>{L['info_title']}</h3>
        <p>{L['info_subtitle']}</p>
      </div>
      <span class="info-cta-arrow">→</span>
    </a>

    <h2 style="font-size:1.1rem;margin:2.5rem 0 0.4rem">{L['units_h2']}</h2>
    <p style="color:var(--text-soft);font-size:0.92rem;margin-bottom:1rem">{L['units_help']}</p>
    <div class="empty-state">
      <h3>{L['no_units_h']}</h3>
      <p>{L['no_units_p']}</p>
    </div>

    <section style="margin-top:3rem">
      <h2 style="font-size:1.2rem;margin:0 0 0.4rem">{L['globals_h2']}</h2>
      <p style="color:var(--text-soft);font-size:0.92rem;margin-bottom:1rem">{L['globals_help']}</p>
      <p style="color:var(--text-faint);font-size:0.9rem;padding:0.5rem 0">{L['globals_empty']}</p>
    </section>

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
</script>
</body>
</html>
"""


def render_year_info(code, year, lang):
    L = LABELS[lang]
    s = SUBJECTS[code]
    title = s["title"][lang]
    block = s["block"][lang]
    base_url = f"{lang_prefix(lang)}/docencia/{code}/{year}/info/"
    canonical = f"https://alexreyes.es{base_url}"
    es_canon = f"https://alexreyes.es/docencia/{code}/{year}/info/"
    ca_canon = f"https://alexreyes.es/ca/docencia/{code}/{year}/info/"
    en_canon = f"https://alexreyes.es/en/docencia/{code}/{year}/info/"
    parent_year_url = f"{lang_prefix(lang)}/docencia/{code}/{year}/"
    parent_subject_url = f"{lang_prefix(lang)}/docencia/{code}/"

    breadcrumb = (
        f'<a href="{lang_prefix(lang)}/">{L["home"]}</a>'
        f'<span class="sep">/</span>'
        f'<a href="{nav_path(lang,"docencia")}">{L["docencia"]}</a>'
        f'<span class="sep">/</span>'
        f'<a href="{parent_subject_url}">{title}</a>'
        f'<span class="sep">/</span>'
        f'<a href="{parent_year_url}">{year}</a>'
        f'<span class="sep">/</span>'
        f'<span class="current">{L["info_subpage_title"]}</span>'
    )

    return f"""<!DOCTYPE html>
<html lang="{L['html_lang']}">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{L['info_subpage_title']} — {title} ({year})</title>
<meta name="description" content="{L['info_subpage_title']} — {title} {year}.">
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
  .info-block {{ background:var(--bg-subtle); border:1px solid var(--border); border-radius:var(--radius); padding:1.4rem 1.6rem; margin-bottom:1.5rem; }}
  .info-block > h3 {{ margin:0 0 0.9rem; font-size:1rem; font-weight:600; color:var(--text); display:flex; align-items:center; gap:0.5rem; }}
  .empty-line {{ font-size:0.85rem; color:var(--text-faint); margin:0.5rem 0 0; }}
</style>
</head>
<body>
<nav>
  <div class="nav-inner">
    <a href="{lang_prefix(lang)}/" class="nav-brand">alexreyes.es</a>
    <div class="nav-links">{nav_block(lang)}</div>
    <div class="nav-right">
      <div class="lang-sw">{lang_switch_html(lang, code, year, "info/")}</div>
      <button class="nav-hamburger" onclick="toggleMenu()" aria-label="Menu"><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><line x1="4" y1="7" x2="20" y2="7"/><line x1="4" y1="12" x2="20" y2="12"/><line x1="4" y1="17" x2="20" y2="17"/></svg></button>
      <button class="theme-btn" onclick="toggleTheme()" aria-label="Toggle theme">
        <svg class="icon-sun" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="5"/></svg>
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
        <span class="tag tag-orange">{year}</span>
      </div>
      <h1 style="margin:0.3rem 0 0.6rem">{L['info_subpage_title']}</h1>
      <p style="font-size:0.98rem;color:var(--text-soft)">{title} — {L['year_label']} {year}.</p>
    </div>

    <div class="info-block">
      <h3>🗓️ {L['info_block_horari']}</h3>
      <p class="empty-line">{L['info_empty']}</p>
    </div>

    <div class="info-block">
      <h3>📊 {L['info_block_aval']}</h3>
      <p class="empty-line">{L['info_empty']}</p>
    </div>

    <div class="info-block">
      <h3>📄 {L['info_block_docs']}</h3>
      <p class="empty-line">{L['info_empty']}</p>
    </div>

    <div class="info-block">
      <h3>🎒 {L['info_block_mat']}</h3>
      <p class="empty-line">{L['info_empty']}</p>
    </div>

    <p style="margin-top:2rem;text-align:center">
      <a href="{parent_year_url}" style="font-size:0.9rem;color:var(--text-faint);text-decoration:none">← {L['back_year']}</a>
    </p>

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
</script>
</body>
</html>
"""


def main():
    parser = argparse.ArgumentParser(description="Add a course year (3 languages) to an archived subject.")
    parser.add_argument("subject", choices=SUBJECTS.keys(), help="Subject code")
    parser.add_argument("year", help="Year code, e.g. 2014-15")
    parser.add_argument("--center", default=None, help="Center where it was taught (e.g. 'Escola Meritxell')")
    parser.add_argument("--note", default=None, help="Optional short note")
    parser.add_argument("--force", action="store_true", help="Overwrite existing files")
    args = parser.parse_args()

    # Build output paths for each language
    outputs = []
    for lang in LANGS:
        if lang == "es":
            year_dir = REPO / "docencia" / args.subject / args.year
        else:
            year_dir = REPO / lang / "docencia" / args.subject / args.year
        outputs.append((lang, year_dir, year_dir / "index.html", year_dir / "info" / "index.html"))

    # Safety: avoid overwriting existing
    if not args.force:
        for lang, _, hub, _ in outputs:
            if hub.exists():
                print(f"  ✗ {hub.relative_to(REPO)} already exists. Use --force to overwrite.", file=sys.stderr)
                sys.exit(1)

    # Generate all 6 files (3 langs × 2 pages)
    for lang, year_dir, hub_path, info_path in outputs:
        year_dir.mkdir(parents=True, exist_ok=True)
        (year_dir / "info").mkdir(parents=True, exist_ok=True)
        hub_path.write_text(render_year_hub(args.subject, args.year, lang, args.center, args.note), encoding="utf-8")
        info_path.write_text(render_year_info(args.subject, args.year, lang), encoding="utf-8")
        print(f"  ✓ {hub_path.relative_to(REPO)}")
        print(f"  ✓ {info_path.relative_to(REPO)}")

    # Update centralized years.json
    json_path = ARCHIVE_DATA / f"{args.subject}.json"
    json_path.parent.mkdir(parents=True, exist_ok=True)
    if json_path.exists():
        data = json.loads(json_path.read_text(encoding="utf-8"))
    else:
        data = {"years": []}
    years = [y for y in data.get("years", []) if y.get("year") != args.year]
    entry = {"year": args.year}
    if args.center: entry["center"] = args.center
    if args.note:   entry["note"] = args.note
    years.append(entry)
    years.sort(key=lambda y: y.get("year", ""), reverse=True)
    data["years"] = years
    json_path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"  ✓ {json_path.relative_to(REPO)}  ({len(years)} year{'s' if len(years)!=1 else ''})")

    print()
    print(f"  Open ES: https://alexreyes.es/docencia/{args.subject}/{args.year}/")
    print(f"  Open CA: https://alexreyes.es/ca/docencia/{args.subject}/{args.year}/")
    print(f"  Open EN: https://alexreyes.es/en/docencia/{args.subject}/{args.year}/")


if __name__ == "__main__":
    main()
