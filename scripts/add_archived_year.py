#!/usr/bin/env python3
"""Add a course year to an archived (non-active) subject.

Creates:
  /docencia/<subject>/<year>/index.html        — year hub (units + exams + info card)
  /docencia/<subject>/<year>/info/index.html   — year info subpage (horario, avaluació, ...)

And updates:
  /docencia/<subject>/years.json               — adds an entry for this year

Usage:
  python3 scripts/add_archived_year.py <subject> <year> [--center "Maristes Sants—Les Corts"] [--note "Suplencia"]

Examples:
  python3 scripts/add_archived_year.py eso-3 2014-15 --center "Escola Meritxell"
  python3 scripts/add_archived_year.py ccss-2btl 2017-18 --center "Escola Meritxell" --note "Cap d'estudis"
"""
import argparse
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent

# Subject metadata (must match rebuild_archived_landings.py)
SUBJECTS = {
    "eso-1":          {"title": "Matemàtiques 1r ESO",        "lang": "ca", "badge": "ESO",          "curs_label": "Curs",  "curs": "1r ESO"},
    "eso-3":          {"title": "Matemàtiques 3r ESO",        "lang": "ca", "badge": "ESO",          "curs_label": "Curs",  "curs": "3r ESO"},
    "eso-4":          {"title": "Matemàtiques 4t ESO",        "lang": "ca", "badge": "ESO",          "curs_label": "Curs",  "curs": "4t ESO"},
    "ccss-2btl":      {"title": "Mat. Aplicadas CCSS 2º BTL", "lang": "es", "badge": "Bachillerato", "curs_label": "Curso", "curs": "2º Bachillerato"},
    "cientific-1btl": {"title": "Matemáticas 1º BTL Científico", "lang": "es", "badge": "Bachillerato", "curs_label": "Curso", "curs": "1º Bachillerato"},
    "cientific-2btl": {"title": "Matemáticas 2º BTL Científico", "lang": "es", "badge": "Bachillerato", "curs_label": "Curso", "curs": "2º Bachillerato"},
}

I18N = {
    "ca": {
        "home": "Inici", "docencia": "Docència",
        "back_subject": "Tornar a l'assignatura",
        "back_year": "Tornar al hub del curs",
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
    },
    "es": {
        "home": "Inicio", "docencia": "Docencia",
        "back_subject": "Volver a la asignatura",
        "back_year": "Volver al hub del curso",
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
    },
}

NAV_HTML = '''<nav>
  <div class="nav-inner">
    <a href="/" class="nav-brand">alexreyes.es</a>
    <div class="nav-links">
      <a href="/docencia/" class="nav-active">Docencia</a>
      <a href="/doctorado/">Doctorado</a>
      <a href="/notas/">Notas</a>
      <a href="/cv/">CV</a>
      <a href="/contacto/">Contacto</a>
    </div>
    <div class="nav-right">
      <button class="nav-hamburger" onclick="toggleMenu()" aria-label="Menu"><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><line x1="4" y1="7" x2="20" y2="7"/><line x1="4" y1="12" x2="20" y2="12"/><line x1="4" y1="17" x2="20" y2="17"/></svg></button>
      <button class="theme-btn" onclick="toggleTheme()" aria-label="Toggle theme">
        <svg class="icon-sun" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="5"/><line x1="12" y1="1" x2="12" y2="3"/><line x1="12" y1="21" x2="12" y2="23"/><line x1="4.22" y1="4.22" x2="5.64" y2="5.64"/><line x1="18.36" y1="18.36" x2="19.78" y2="19.78"/><line x1="1" y1="12" x2="3" y2="12"/><line x1="21" y1="12" x2="23" y2="12"/><line x1="4.22" y1="19.78" x2="5.64" y2="18.36"/><line x1="18.36" y1="5.64" x2="19.78" y2="4.22"/></svg>
        <svg class="icon-moon" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/></svg>
      </button>
    </div>
  </div>
</nav>'''

FOOTER_HTML = '''<footer>
  <div class="container">
    <div class="footer-inner">
      <span><strong>Àlex Reyes</strong> &middot; Matemáticas, docencia y doctorado</span>
      <span>Barcelona &middot; 2026</span>
    </div>
  </div>
</footer>

<script>
function toggleMenu(){document.querySelector("nav").classList.toggle("open");}
function toggleTheme(){var h=document.documentElement,n=h.getAttribute('data-theme')==='dark'?'light':'dark';h.setAttribute('data-theme',n);localStorage.setItem('theme',n);}
</script>'''


def render_year_hub(s, year, center, note):
    L = I18N[s["lang"]]
    center_html = f'<span class="tag tag-gray">{center}</span>' if center else ''
    note_html = f'<p style="font-size:0.88rem;color:var(--text-faint);margin-top:0.4rem">{note}</p>' if note else ''
    return f"""<!DOCTYPE html>
<html lang="{s['lang']}">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{s['title']} ({year}) — Àlex Reyes</title>
<meta name="description" content="{s['title']} — curs {year}.">
<script>(function(){{var s=localStorage.getItem('theme');if(s)document.documentElement.setAttribute('data-theme',s);else document.documentElement.setAttribute('data-theme','light');}})();</script>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
<link rel="stylesheet" href="/style.css">
<link rel="icon" type="image/svg+xml" href="/favicon.svg">
<link rel="canonical" href="https://alexreyes.es/docencia/{s['code']}/{year}/">
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
{NAV_HTML}

<main>
  <div class="container" style="padding-top:3rem;padding-bottom:5rem">

    <div class="breadcrumb">
      <a href="/">{L['home']}</a>
      <span class="sep">/</span>
      <a href="/docencia/">{L['docencia']}</a>
      <span class="sep">/</span>
      <a href="/docencia/{s['code']}/">{s['title']}</a>
      <span class="sep">/</span>
      <span class="current">{year}</span>
    </div>

    <div class="page-header">
      <div style="display:flex;align-items:center;gap:0.6rem;margin-bottom:0.6rem;flex-wrap:wrap">
        <span class="section-label">{s['badge']}</span>
        <span class="tag tag-orange">{year}</span>
        {center_html}
      </div>
      <h1 style="margin:0.3rem 0 0.6rem">{s['title']}</h1>
      <p style="font-size:0.98rem;color:var(--text-soft)">Curs {year}.</p>
      {note_html}
    </div>

    <div class="info-grid">
      <div class="info-card"><div class="info-card-label">{s['curs_label']}</div><div class="info-card-value">{s['curs']}</div></div>
      <div class="info-card"><div class="info-card-label">Curs acadèmic</div><div class="info-card-value">{year}</div></div>
    </div>

    <a href="/docencia/{s['code']}/{year}/info/" class="info-cta">
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

{FOOTER_HTML}
</body>
</html>
"""


def render_year_info(s, year):
    L = I18N[s["lang"]]
    return f"""<!DOCTYPE html>
<html lang="{s['lang']}">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{L['info_subpage_title']} — {s['title']} ({year})</title>
<meta name="description" content="{L['info_subpage_title']} — {s['title']} curs {year}.">
<script>(function(){{var s=localStorage.getItem('theme');if(s)document.documentElement.setAttribute('data-theme',s);else document.documentElement.setAttribute('data-theme','light');}})();</script>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
<link rel="stylesheet" href="/style.css">
<link rel="icon" type="image/svg+xml" href="/favicon.svg">
<link rel="canonical" href="https://alexreyes.es/docencia/{s['code']}/{year}/info/">
<style>
  .info-block {{ background:var(--bg-subtle); border:1px solid var(--border); border-radius:var(--radius); padding:1.4rem 1.6rem; margin-bottom:1.5rem; }}
  .info-block > h3 {{ margin:0 0 0.9rem; font-size:1rem; font-weight:600; color:var(--text); display:flex; align-items:center; gap:0.5rem; }}
  .empty-line {{ font-size:0.85rem; color:var(--text-faint); margin:0.5rem 0 0; }}
</style>
</head>
<body>
{NAV_HTML}

<main>
  <div class="container" style="padding-top:3rem;padding-bottom:5rem">

    <div class="breadcrumb">
      <a href="/">{L['home']}</a>
      <span class="sep">/</span>
      <a href="/docencia/">{L['docencia']}</a>
      <span class="sep">/</span>
      <a href="/docencia/{s['code']}/">{s['title']}</a>
      <span class="sep">/</span>
      <a href="/docencia/{s['code']}/{year}/">{year}</a>
      <span class="sep">/</span>
      <span class="current">{L['info_subpage_title']}</span>
    </div>

    <div class="page-header">
      <div style="display:flex;align-items:center;gap:0.6rem;margin-bottom:0.6rem;flex-wrap:wrap">
        <span class="section-label">{s['badge']}</span>
        <span class="tag tag-orange">{year}</span>
      </div>
      <h1 style="margin:0.3rem 0 0.6rem">{L['info_subpage_title']}</h1>
      <p style="font-size:0.98rem;color:var(--text-soft)">{s['title']} — curs {year}.</p>
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
      <a href="/docencia/{s['code']}/{year}/" style="font-size:0.9rem;color:var(--text-faint);text-decoration:none">← {L['back_year']}</a>
    </p>

  </div>
</main>

{FOOTER_HTML}
</body>
</html>
"""


def main():
    parser = argparse.ArgumentParser(description="Add a course year to an archived subject.")
    parser.add_argument("subject", choices=SUBJECTS.keys(), help="Subject code")
    parser.add_argument("year", help="Year code, e.g. 2014-15")
    parser.add_argument("--center", default=None, help="Center where it was taught (e.g. 'Escola Meritxell')")
    parser.add_argument("--note", default=None, help="Optional short note")
    parser.add_argument("--force", action="store_true", help="Overwrite existing files")
    args = parser.parse_args()

    s = dict(SUBJECTS[args.subject])
    s["code"] = args.subject

    year_dir = REPO / "docencia" / args.subject / args.year
    info_dir = year_dir / "info"
    hub_path = year_dir / "index.html"
    info_path = info_dir / "index.html"
    years_json_path = REPO / "docencia" / args.subject / "years.json"

    if hub_path.exists() and not args.force:
        print(f"  ✗ {hub_path.relative_to(REPO)} already exists. Use --force to overwrite.", file=sys.stderr)
        sys.exit(1)

    year_dir.mkdir(parents=True, exist_ok=True)
    info_dir.mkdir(parents=True, exist_ok=True)

    hub_path.write_text(render_year_hub(s, args.year, args.center, args.note), encoding="utf-8")
    info_path.write_text(render_year_info(s, args.year), encoding="utf-8")

    # Update years.json
    if years_json_path.exists():
        data = json.loads(years_json_path.read_text(encoding="utf-8"))
    else:
        data = {"years": []}
    years = data.get("years", [])
    # Replace existing entry with same year, or add
    years = [y for y in years if y.get("year") != args.year]
    entry = {"year": args.year}
    if args.center: entry["center"] = args.center
    if args.note:   entry["note"] = args.note
    years.append(entry)
    years.sort(key=lambda y: y.get("year", ""), reverse=True)
    data["years"] = years
    years_json_path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    print(f"  ✓ {hub_path.relative_to(REPO)}")
    print(f"  ✓ {info_path.relative_to(REPO)}")
    print(f"  ✓ {years_json_path.relative_to(REPO)}  ({len(years)} year{'s' if len(years)!=1 else ''})")
    print()
    print(f"  Open: https://alexreyes.es/docencia/{args.subject}/{args.year}/")


if __name__ == "__main__":
    main()
