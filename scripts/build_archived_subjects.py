#!/usr/bin/env python3
"""Build simple subject landings in 3 languages.

Cubre dos casos, distinguidos por la clave "status" de cada asignatura:
  - "archived" (por defecto): materia impartida en cursos anteriores.
  - "active": materia que imparto este curso pero que todavía no tiene
    temario publicado (o cuyo material vive en el archivo por años).
    Requiere la clave "year" (p. ej. "2026–27").

For each subject, generates:
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
import re
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
    {
        "code": "projectes-2eso",
        # Bloque doble de viernes tarde: 15:30–17:30 seguidas.
        "schedule": [(4, "15:30–16:30"), (4, "16:30–17:30")],
        "grup": "2n ESO E",
        "block": "ESO",
        "title": {"es": "Projectes 2n ESO", "ca": "Projectes 2n ESO", "en": "Projects 2nd ESO"},
        "h1":    {"es": "Projectes 2n ESO", "ca": "Projectes 2n ESO", "en": "Projects 2nd ESO"},
        "desc":  {"es": "Segundo de ESO &mdash; trabajo por proyectos interdisciplinares.",
                  "ca": "Segon d'ESO &mdash; treball per projectes interdisciplinaris.",
                  "en": "2nd year of ESO &mdash; interdisciplinary project-based work."},
        "curs":  {"es": "2º ESO", "ca": "2n ESO", "en": "2nd ESO"},
        "status": "active",
        "year": "2026–27",
    },
    {
        "code": "tutoria-2eso",
        "privat_url": "/tutoria/",
        "horari_url": "horari/",
        "schedule": [(3, "9:00–10:00")],
        "grup": "2n ESO E",
        "block": "ESO",
        "title": {"es": "Tutoría 2n ESO E", "ca": "Tutoria 2n ESO E", "en": "Form tutor 2nd ESO E"},
        "h1":    {"es": "Tutoría 2n ESO E", "ca": "Tutoria 2n ESO E", "en": "Form tutor 2nd ESO E"},
        "desc":  {"es": "Tutoría del grupo 2n ESO E &mdash; acción tutorial y acompañamiento.",
                  "ca": "Tutoria del grup 2n ESO E &mdash; acció tutorial i acompanyament.",
                  "en": "Form tutor for group 2n ESO E &mdash; tutorial and pastoral work."},
        "curs":  {"es": "2º ESO &middot; grupo E", "ca": "2n ESO &middot; grup E", "en": "2nd ESO &middot; group E"},
        "status": "active",
        "year": "2026–27",
    },
]

LANGS = ["es", "ca", "en"]

LABELS = {
    "es": {
        "html_lang": "es",
        "skip": "Saltar al contenido",
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
        "estado_value_active": "Activa",
        "no_years_h_active": "Curso en marcha",
        "no_years_p_active": "Estoy impartiendo esta asignatura durante el curso 2026\u20132027. El material se ir\u00e1 publicando a lo largo del a\u00f1o.",
        "meta_desc_archived": "hist\u00f3rico docente.",
        "meta_desc_active": "curso 2026\u20132027.",
        "courses_label": "Cursos",
        "curs_label": "Curso",
        "days": ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes"],
        "horari_h2": "Horario",
        "horari_help": "Sesiones semanales del curso 2026\u201327.",
        "grup_label": "Grupo",
        "privat_h": "Área privada",
        "horari_classe_h": "Horario de clase",
        "horari_classe_p": "Rejilla semanal completa del grupo, con todas las materias y su profesorado. Se puede descargar en PDF.",
        "hores_label": "Horas/semana",
        "footer_brand": "Matemáticas, docencia y doctorado",
    },
    "ca": {
        "html_lang": "ca",
        "skip": "Salta al contingut",
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
        "estado_value_active": "Activa",
        "no_years_h_active": "Curs en marxa",
        "no_years_p_active": "Estic impartint aquesta assignatura durant el curs 2026\u20132027. El material es publicar\u00e0 al llarg de l'any.",
        "meta_desc_archived": "hist\u00f2ric docent.",
        "meta_desc_active": "curs 2026\u20132027.",
        "courses_label": "Cursos",
        "curs_label": "Curs",
        "days": ["Dilluns", "Dimarts", "Dimecres", "Dijous", "Divendres"],
        "horari_h2": "Horari",
        "horari_help": "Sessions setmanals del curs 2026\u201327.",
        "grup_label": "Grup",
        "privat_h": "\u00c0rea privada",
        "horari_classe_h": "Horari de classe",
        "horari_classe_p": "Graella setmanal completa del grup, amb totes les matèries i el seu professorat. Es pot descarregar en PDF.",
        "hores_label": "Hores/setmana",
        "footer_brand": "Matemàtiques, docència i doctorat",
    },
    "en": {
        "html_lang": "en",
        "skip": "Skip to content",
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
        "estado_value_active": "Active",
        "no_years_h_active": "Course in progress",
        "no_years_p_active": "I am teaching this subject during the 2026\u20132027 academic year. Material will be published throughout the year.",
        "meta_desc_archived": "teaching history.",
        "meta_desc_active": "2026\u20132027 academic year.",
        "courses_label": "Years",
        "curs_label": "Year",
        "days": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"],
        "horari_h2": "Timetable",
        "horari_help": "Weekly sessions for the 2026\u201327 academic year.",
        "grup_label": "Group",
        "privat_h": "Private area",
        "horari_classe_h": "Class timetable",
        "horari_classe_p": "Full weekly grid for the group, with every subject and its teacher. Downloadable as PDF.",
        "hores_label": "Hours/week",
        "footer_brand": "Mathematics, teaching and research",
    },
}


def asset_version():
    """?v= de cache-busting vigente en el sitio.

    Se lee de /docencia/index.html en vez de fijarlo aquí, para que las
    landings generadas queden alineadas con el resto de páginas sin tener
    que correr bump-css-version.py sobre todo el repo.
    """
    ref = REPO / "docencia" / "index.html"
    if ref.exists():
        m = re.search(r"/style\.css\?v=(\d+)", ref.read_text(encoding="utf-8"))
        if m:
            return "?v=" + m.group(1)
    return ""


def lang_prefix(lang):
    """URL prefix for a given language. ES is at root, others nested."""
    return "" if lang == "es" else f"/{lang}"


def nav_path(lang, page):
    """Build absolute URL for a nav target in a given language."""
    pre = lang_prefix(lang)
    return f"{pre}/{page}/"


def merge_slots(schedule):
    """Franjas contiguas del mismo día como un solo bloque.

    Projectes son dos sesiones seguidas el viernes: se muestran como
    "15:30–17:30", no como dos filas. El recuento de horas/semana sigue
    usando la lista sin fusionar.
    """
    per_day = {}
    for di, hora in schedule:
        ini, fi = hora.split("\u2013")
        per_day.setdefault(di, []).append((ini.strip(), fi.strip()))
    out = []
    for di in sorted(per_day):
        blocs = []
        for ini, fi in sorted(per_day[di], key=lambda t: _minuts(t[0])):
            if blocs and blocs[-1][1] == ini:
                blocs[-1] = (blocs[-1][0], fi)
            else:
                blocs.append((ini, fi))
        out.extend((di, f"{a}\u2013{b}") for a, b in blocs)
    return out


def _minuts(hhmm):
    h, m = hhmm.split(":")
    return int(h) * 60 + int(m)


def render_landing(s, lang):
    L = LABELS[lang]
    code = s["code"]
    title = s["title"][lang]
    h1 = s["h1"][lang]
    desc = s["desc"][lang]
    curs = s["curs"][lang]
    block = s["block"][lang] if isinstance(s["block"], dict) else s["block"]
    is_active = s.get("status") == "active"
    # Materia activa: chip verde con el curso; archivada: chip gris "Archivada".
    status_tag = (f'<span class="tag tag-green">{s["year"]}</span>' if is_active
                  else f'<span class="tag tag-gray">{L["archived_tag"]}</span>')
    estado_value = L["estado_value_active"] if is_active else L["estado_value"]
    empty_h = L["no_years_h_active"] if is_active else L["no_years_h"]
    empty_p = L["no_years_p_active"] if is_active else L["no_years_p"]
    meta_desc = L["meta_desc_active"] if is_active else L["meta_desc_archived"]
    v = asset_version()
    # Horario semanal (solo asignaturas activas que lo tienen cargado)
    # Botón al área privada (solo tutoría), junto al título. El contenido no
    # está aquí: vive tras el gate de servidor de functions/tutoria/.
    # Sin botón, el título va suelto como en el resto de asignaturas; con él,
    # comparten fila y se apilan en pantallas estrechas.
    titol_html = f'<h1 style="margin:0.3rem 0 0.6rem">{h1}</h1>'
    if s.get("privat_url"):
        # La derecha del título queda reservada al área privada, y solo a eso.
        privat_btn = (
            f'<a href="{s["privat_url"]}" class="btn btn-secondary" rel="nofollow" '
            f'style="flex:none;text-decoration:none">'
            f'<span aria-hidden="true">🔒</span>{L["privat_h"]}</a>'
        )
        titol_html = (
            '<div style="display:flex;align-items:center;justify-content:space-between;'
            'gap:1rem;flex-wrap:wrap;margin:0.3rem 0 0.6rem">'
            f'<h1 style="margin:0">{h1}</h1>{privat_btn}</div>'
        )

    # El horario de clase del grupo va en el cuerpo, como tarjeta enlazada,
    # no como botón de cabecera: no es una zona restringida, es contenido.
    def _link_card(url, icona, titol, text):
        return f"""
    <a href="{url}" class="link-card">
      <span class="link-card-icon" aria-hidden="true">{icona}</span>
      <span class="link-card-body">
        <strong>{titol}</strong>
        <span>{text}</span>
      </span>
      <span class="link-card-arrow" aria-hidden="true">&rarr;</span>
    </a>
"""

    horari_link_html = ""
    if s.get("horari_url"):
        horari_link_html += _link_card(s["horari_url"], "🗓️",
                                       L["horari_classe_h"], L["horari_classe_p"])

    horari_html = ""
    hores_card = ""
    if s.get("schedule"):
        hores_card = (f'<div class="info-card"><div class="info-card-label">{L["hores_label"]}'
                      f'</div><div class="info-card-value">{len(s["schedule"])}</div></div>')
        rows = "".join(
            f'<div class="schedule-day"><span>{L["days"][di]}</span>'
            f'<strong>{hora}</strong></div>'
            for di, hora in merge_slots(s["schedule"])
        )
        horari_html = (
            f'\n    <h2 style="font-size:1.1rem;margin:2.5rem 0 0.4rem">{L["horari_h2"]}</h2>'
            f'\n    <p style="color:var(--text-soft);font-size:0.92rem;margin-bottom:1rem">'
            f'{L["horari_help"]}</p>'
            f'\n    <div class="schedule-grid"><div class="schedule-card">'
            f'<h4>{s.get("grup", curs)}</h4>{rows}</div></div>\n'
        )

    base_url = f"{lang_prefix(lang)}/docencia/{code}/"
    canonical = f"https://alexreyes.es{base_url}"
    es_canon = f"https://alexreyes.es/docencia/{code}/"
    ca_canon = f"https://alexreyes.es/ca/docencia/{code}/"
    en_canon = f"https://alexreyes.es/en/docencia/{code}/"
    # Lang switcher links (this same page in other langs)
    def _lsw(code_lang, href):
        cls = ' class="lang-active"' if lang == code_lang else ''
        return f'<a href="{href}"{cls}>{code_lang.upper()}</a>'

    lang_switch = '<span class="lang-sep">&middot;</span>'.join([
        _lsw("es", f"/docencia/{code}/"),
        _lsw("ca", f"/ca/docencia/{code}/"),
        _lsw("en", f"/en/docencia/{code}/"),
    ])

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
<meta name="description" content="{title} — {meta_desc}">
<script>(function(){{var s=localStorage.getItem('theme');if(s)document.documentElement.setAttribute('data-theme',s);else document.documentElement.setAttribute('data-theme','light');}})();</script>
<script src="/assets/js/lang-persist.js{v}"></script>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap" media="print" onload="this.media='all'"><noscript><link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap"></noscript>
<link rel="stylesheet" href="/style.css{v}">
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
  /* Horario — mismas reglas que las info pages de asignatura */
  .schedule-grid {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(220px,1fr)); gap:1rem; }}
  .schedule-card {{ background:var(--bg); border:1px solid var(--border); border-radius:var(--radius-sm); padding:0.9rem 1.1rem; }}
  .schedule-card h4 {{ margin:0 0 0.6rem; font-size:0.78rem; color:var(--text-soft); text-transform:uppercase; letter-spacing:0.05em; font-weight:600; }}
  .schedule-day {{ display:flex; justify-content:space-between; padding:0.3rem 0; font-size:0.92rem; border-bottom:1px solid var(--border); }}
  .schedule-day:last-child {{ border-bottom:none; }}
  .schedule-day strong {{ font-family:var(--mono); color:var(--text); }}
  /* Tarjeta de enlace del cuerpo (horario de clase del grupo) */
  .link-card {{ display:flex; align-items:center; gap:0.9rem; margin:1.6rem 0 0; padding:1rem 1.25rem; background:var(--bg-subtle); border:1px solid var(--border); border-radius:var(--radius); text-decoration:none; color:inherit; transition:border-color 0.15s, transform 0.15s; }}
  .link-card:hover {{ border-color:var(--border-strong); transform:translateY(-1px); opacity:1; }}
  .link-card-icon {{ font-size:1.35rem; line-height:1; flex:none; }}
  .link-card-body {{ display:flex; flex-direction:column; gap:0.15rem; flex:1; min-width:0; }}
  .link-card-body strong {{ font-size:0.95rem; font-weight:600; }}
  .link-card-body span {{ font-size:0.86rem; color:var(--text-soft); }}
  .link-card-arrow {{ flex:none; color:var(--text-faint); font-size:1rem; }}
</style>
<script defer src="/assets/js/curso-banner.js{v}"></script>
</head>
<body>
<a class="skip-link" href="#main">{L['skip']}</a>
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

<main id="main">
  <div class="container" style="padding-top:3rem;padding-bottom:5rem">

    <div class="breadcrumb">{breadcrumb}</div>

    <div class="page-header">
      <div style="display:flex;align-items:center;gap:0.6rem;margin-bottom:0.6rem;flex-wrap:wrap">
        <span class="section-label">{block}</span>
        {status_tag}
      </div>
      {titol_html}
      <p style="font-size:0.98rem;color:var(--text-soft)">{desc}</p>
    </div>

    <div class="info-grid">
      <div class="info-card"><div class="info-card-label">{L['curs_label']}</div><div class="info-card-value">{curs}</div></div>
      <div class="info-card"><div class="info-card-label">{L['estado_label']}</div><div class="info-card-value" style="font-size:0.88rem">{estado_value}</div></div>
      <div class="info-card"><div class="info-card-label">{L['courses_label']}</div><div class="info-card-value" id="years-count">—</div></div>
      {hores_card}
    </div>

{horari_html}{horari_link_html}
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
      <span>Barcelona &middot; &copy; 2026 Àlex Reyes &middot; <a href="/assets/NOTICES.txt" style="color:inherit">Licencias</a></span>
    </div>
  </div>
</footer>

<script>
function toggleMenu(){{document.querySelector("nav").classList.toggle("open");}}
function toggleTheme(){{var h=document.documentElement,n=h.getAttribute('data-theme')==='dark'?'light':'dark';h.setAttribute('data-theme',n);localStorage.setItem('theme',n);}}
function escHtml(s){{ return String(s||'').replace(/[&<>"']/g, c => ({{'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}}[c])); }}

const NO_YEARS_H = {json.dumps(empty_h)};
const NO_YEARS_P = {json.dumps(empty_p)};
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
<script defer src="/assets/js/search.js{v}"></script>
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
