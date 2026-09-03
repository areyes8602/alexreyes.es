#!/usr/bin/env python3
"""Build the full weekly class timetable of group 2n ESO E.

Genera, en los tres idiomas del sitio:
  /docencia/tutoria-2eso/horari/index.html      (ES)
  /ca/docencia/tutoria-2eso/horari/index.html   (CA)
  /en/docencia/tutoria-2eso/horari/index.html   (EN)

Es la parte pública de la tutoría: el horario del grupo entero, con todas
las materias y el profesorado de cada una. No hay datos de alumnos aquí.

La página se imprime a PDF desde el propio navegador (@media print +
window.print()), igual que /tutoria/imprimir/. No se sube ninguna imagen:
la rejilla es HTML, así que es accesible, traducible y buscable.

Fuente: horario Untis del curso 2026-27 (2n ESO E), Maristes Sants-Les Corts.
Reejecutar tras editar SUBJECTS / GRID para regenerar los tres idiomas.
"""
import re
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
CODE = "tutoria-2eso"
SLUG = "horari"
GRUP = "2n ESO E"
YEAR = "2026–27"
LANGS = ["es", "ca", "en"]

# ─── Materias: nombre por idioma + profesorado ───────────────────
# "meu": la imparto yo (se resalta en la rejilla).
SUBJECTS = {
    "angles":    {"es": "Inglés", "ca": "Anglès", "en": "English",
                  "prof": ["Rubio, Enric"]},
    "musica":    {"es": "Música", "ca": "Música", "en": "Music",
                  "prof": ["Zaidín, Lluïsa"]},
    "castella":  {"es": "Castellano", "ca": "Castellà", "en": "Spanish",
                  "prof": ["Ruedas, Mónica"]},
    "tutoria":   {"es": "Tutoría", "ca": "Tutoria", "en": "Form tutor",
                  "prof": ["Reyes, Àlex"], "meu": True},
    "catala":    {"es": "Catalán", "ca": "Català", "en": "Catalan",
                  "prof": ["Navarro, Montse"]},
    "natacio":   {"es": "Natación", "ca": "Natació", "en": "Swimming",
                  "prof": ["Barrero, Oriol", "Boch, Xavier"]},
    "religio":   {"es": "Religión", "ca": "Religió", "en": "Religion",
                  "prof": ["Alcolea, Mireia"]},
    "socials":   {"es": "Sociales", "ca": "Socials", "en": "Social Sciences",
                  "prof": ["Ríos, Jaume"]},
    "ef":        {"es": "Educación Física", "ca": "Educació Física",
                  "en": "Physical Education", "prof": ["Barrero, Oriol"]},
    "mates":     {"es": "Matemáticas", "ca": "Matemàtiques", "en": "Mathematics",
                  "prof": ["Reyes, Àlex"], "meu": True},
    "fq":        {"es": "Física y Química", "ca": "Física i Química",
                  "en": "Physics & Chemistry", "prof": ["Ramos, Mayte"]},
    "robotica":  {"es": "Taller de Robótica", "ca": "Taller de Robòtica",
                  "en": "Robotics workshop",
                  "prof": ["González, David", "Villena, Jorge"]},
    "tecnologia": {"es": "Tecnología", "ca": "Tecnologia", "en": "Technology",
                   "prof": ["González, David"]},
    "tallerlab": {"es": "Taller / Laboratorio", "ca": "Taller / Laboratori",
                  "en": "Workshop / Lab",
                  "prof": ["González, David", "Ramos, Mayte"]},
    "projectes": {"es": "Proyectos", "ca": "Projectes", "en": "Projects",
                  "prof": ["Reyes, Àlex"], "meu": True},
}

# ─── Rejilla semanal ─────────────────────────────────────────────
# Cada franja: (hora, [lun, mar, mié, jue, vie]) con la clave de SUBJECTS,
# o ("break", clave_de_etiqueta, hora) para patio y mediodía.
GRID = [
    ("9:00", "10:00", ["angles", "musica", "castella", "tutoria", "castella"]),
    ("10:00", "11:00", ["catala", "natacio", "religio", "catala", "socials"]),
    ("break", "pati", ("11:00", "11:30")),
    ("11:30", "12:25", ["ef", "angles", "socials", "socials", "mates"]),
    ("12:25", "13:20", ["fq", "mates", "fq", "robotica", "tecnologia"]),
    ("break", "migdia", ("13:20", "15:30")),
    ("15:30", "16:30", ["tecnologia", "robotica", "mates", "tallerlab", "projectes"]),
    ("16:30", "17:30", ["musica", "catala", "angles", "tallerlab", "projectes"]),
]

LABELS = {
    "es": {
        "html_lang": "es",
        "skip": "Saltar al contenido",
        "home": "Inicio", "docencia": "Docencia",
        "doctorado_nav": "Doctorado", "notas_nav": "Notas", "cv_nav": "CV",
        "contacto_nav": "Contacto",
        "section_label": "Tutoría",
        "title": "Horario de clase 2n ESO E",
        "h1": "Horario de clase",
        "intro": "Horario semanal completo del grupo <strong>2n ESO E</strong> "
                 "durante el curso 2026–2027, con el profesorado de cada materia.",
        "days": ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes"],
        "days_short": ["Lun", "Mar", "Mié", "Jue", "Vie"],
        "hora": "Hora",
        "pati": "Patio",
        "migdia": "Mediodía",
        "print_btn": "Descargar en PDF",
        "print_help": "Se abre el diálogo de impresión del navegador: elige "
                      "«Guardar como PDF». Recomendado en horizontal.",
        "back": "Volver a Tutoría 2n ESO E",
        "meu_legend": "Materias que imparto yo",
        "subjects_h2": "Materias y profesorado",
        "subject_col": "Materia",
        "prof_col": "Profesorado",
        "hours_col": "Sesiones",
        "meta_desc": "Horario semanal del grupo 2n ESO E, curso 2026–2027, "
                     "con las materias y el profesorado de cada franja.",
        "curs_label": "Curso", "curs_value": "2º ESO · grupo E",
        "year_label": "Año académico",
        "sessions_label": "Sesiones/semana",
        "footer_brand": "Matemáticas, docencia y doctorado",
        "print_title": "Horario 2n ESO E · curso 2026–2027",
    },
    "ca": {
        "html_lang": "ca",
        "skip": "Salta al contingut",
        "home": "Inici", "docencia": "Docència",
        "doctorado_nav": "Doctorat", "notas_nav": "Notes", "cv_nav": "CV",
        "contacto_nav": "Contacte",
        "section_label": "Tutoria",
        "title": "Horari de classe 2n ESO E",
        "h1": "Horari de classe",
        "intro": "Horari setmanal complet del grup <strong>2n ESO E</strong> "
                 "durant el curs 2026–2027, amb el professorat de cada matèria.",
        "days": ["Dilluns", "Dimarts", "Dimecres", "Dijous", "Divendres"],
        "days_short": ["Dl", "Dt", "Dc", "Dj", "Dv"],
        "hora": "Hora",
        "pati": "Pati",
        "migdia": "Migdia",
        "print_btn": "Descarregar en PDF",
        "print_help": "S'obre el diàleg d'impressió del navegador: tria "
                      "«Desa com a PDF». Recomanat en horitzontal.",
        "back": "Tornar a Tutoria 2n ESO E",
        "meu_legend": "Matèries que imparteixo jo",
        "subjects_h2": "Matèries i professorat",
        "subject_col": "Matèria",
        "prof_col": "Professorat",
        "hours_col": "Sessions",
        "meta_desc": "Horari setmanal del grup 2n ESO E, curs 2026–2027, "
                     "amb les matèries i el professorat de cada franja.",
        "curs_label": "Curs", "curs_value": "2n ESO · grup E",
        "year_label": "Any acadèmic",
        "sessions_label": "Sessions/setmana",
        "footer_brand": "Matemàtiques, docència i doctorat",
        "print_title": "Horari 2n ESO E · curs 2026–2027",
    },
    "en": {
        "html_lang": "en",
        "skip": "Skip to content",
        "home": "Home", "docencia": "Teaching",
        "doctorado_nav": "PhD", "notas_nav": "Notes", "cv_nav": "CV",
        "contacto_nav": "Contact",
        "section_label": "Form tutor",
        "title": "Class timetable 2n ESO E",
        "h1": "Class timetable",
        "intro": "Full weekly timetable for group <strong>2n ESO E</strong> "
                 "during the 2026–2027 academic year, with the teacher of each subject.",
        "days": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"],
        "days_short": ["Mon", "Tue", "Wed", "Thu", "Fri"],
        "hora": "Time",
        "pati": "Break",
        "migdia": "Lunch",
        "print_btn": "Download as PDF",
        "print_help": "This opens the browser print dialog: choose "
                      "“Save as PDF”. Landscape is recommended.",
        "back": "Back to Form tutor 2n ESO E",
        "meu_legend": "Subjects I teach",
        "subjects_h2": "Subjects and teachers",
        "subject_col": "Subject",
        "prof_col": "Teacher",
        "hours_col": "Sessions",
        "meta_desc": "Weekly timetable for group 2n ESO E, 2026–2027, "
                     "listing every subject and its teacher.",
        "curs_label": "Year", "curs_value": "2nd ESO · group E",
        "year_label": "Academic year",
        "sessions_label": "Sessions/week",
        "footer_brand": "Mathematics, teaching and research",
        "print_title": "Timetable 2n ESO E · 2026–2027",
    },
}


def asset_version():
    """?v= de cache-busting vigente en el sitio (mismo criterio que el resto)."""
    ref = REPO / "docencia" / "index.html"
    if ref.exists():
        m = re.search(r"/style\.css\?v=(\d+)", ref.read_text(encoding="utf-8"))
        if m:
            return "?v=" + m.group(1)
    return ""


def lang_prefix(lang):
    return "" if lang == "es" else f"/{lang}"


def nav_path(lang, page):
    return f"{lang_prefix(lang)}/{page}/"


def session_counts():
    """Sesiones semanales por materia, para la tabla de resumen."""
    counts = {}
    for row in GRID:
        if row[0] == "break":
            continue
        for key in row[2]:
            counts[key] = counts.get(key, 0) + 1
    return counts


def render_grid(L, lang):
    """Rejilla semanal: una fila por franja, una columna por día."""
    head = "".join(
        f'<th scope="col"><span class="d-long">{L["days"][i]}</span>'
        f'<span class="d-short">{L["days_short"][i]}</span></th>'
        for i in range(5)
    )
    rows = []
    for row in GRID:
        if row[0] == "break":
            _, key, (ini, fi) = row
            rows.append(
                f'<tr class="row-break"><th scope="row" class="hora">{ini}<span>{fi}</span></th>'
                f'<td colspan="5">{L[key]}</td></tr>'
            )
            continue
        ini, fi, cells = row
        tds = ""
        for key in cells:
            s = SUBJECTS[key]
            profs = "".join(f'<span class="prof">{p}</span>' for p in s["prof"])
            cls = " cell-meu" if s.get("meu") else ""
            tds += (f'<td class="cell{cls}"><span class="mat">{s[lang]}</span>'
                    f'<span class="profs">{profs}</span></td>')
        rows.append(
            f'<tr><th scope="row" class="hora">{ini}<span>{fi}</span></th>{tds}</tr>'
        )
    return (
        '<div class="horari-wrap">\n'
        '  <table class="horari">\n'
        f'    <caption class="print-only">{L["print_title"]}</caption>\n'
        f'    <thead><tr><th scope="col" class="hora-h">{L["hora"]}</th>{head}</tr></thead>\n'
        '    <tbody>\n      ' + "\n      ".join(rows) + '\n    </tbody>\n'
        '  </table>\n'
        '</div>'
    )


def render_subject_table(L, lang):
    """Resumen: materia, profesorado y sesiones semanales, ordenado A-Z."""
    counts = session_counts()
    order = sorted(SUBJECTS.items(), key=lambda kv: kv[1][lang].lower())
    rows = ""
    for key, s in order:
        profs = " &middot; ".join(s["prof"])
        cls = ' class="mat-meu"' if s.get("meu") else ""
        rows += (f'<tr><th scope="row"{cls}>{s[lang]}</th>'
                 f'<td>{profs}</td><td class="num">{counts.get(key, 0)}</td></tr>')
    return (
        '<div class="horari-wrap mat-taula-wrap">\n'
        '  <table class="mat-taula">\n'
        f'    <thead><tr><th scope="col">{L["subject_col"]}</th>'
        f'<th scope="col">{L["prof_col"]}</th>'
        f'<th scope="col" class="num">{L["hours_col"]}</th></tr></thead>\n'
        f'    <tbody>{rows}</tbody>\n'
        '  </table>\n'
        '</div>'
    )


def render_page(lang):
    L = LABELS[lang]
    v = asset_version()
    title = L["title"]
    total = sum(1 for r in GRID if r[0] != "break") * 5

    base_url = f"{lang_prefix(lang)}/docencia/{CODE}/{SLUG}/"
    canonical = f"https://alexreyes.es{base_url}"
    es_canon = f"https://alexreyes.es/docencia/{CODE}/{SLUG}/"
    ca_canon = f"https://alexreyes.es/ca/docencia/{CODE}/{SLUG}/"
    en_canon = f"https://alexreyes.es/en/docencia/{CODE}/{SLUG}/"

    def _lsw(code_lang, href):
        cls = ' class="lang-active"' if lang == code_lang else ''
        return f'<a href="{href}"{cls}>{code_lang.upper()}</a>'

    lang_switch = '<span class="lang-sep">&middot;</span>'.join([
        _lsw("es", es_canon.replace("https://alexreyes.es", "")),
        _lsw("ca", ca_canon.replace("https://alexreyes.es", "")),
        _lsw("en", en_canon.replace("https://alexreyes.es", "")),
    ])

    nav_links = (
        f'<a href="{nav_path(lang,"docencia")}" class="nav-active">{L["docencia"]}</a>'
        f'<a href="{nav_path(lang,"doctorado")}">{L["doctorado_nav"]}</a>'
        f'<a href="{nav_path(lang,"notas")}">{L["notas_nav"]}</a>'
        f'<a href="{nav_path(lang,"cv")}">{L["cv_nav"]}</a>'
        f'<a href="{nav_path(lang,"contacto")}">{L["contacto_nav"]}</a>'
    )
    hub_url = f"{lang_prefix(lang)}/docencia/{CODE}/"
    breadcrumb = (
        f'<a href="{lang_prefix(lang)}/">{L["home"]}</a><span class="sep">/</span>'
        f'<a href="{nav_path(lang,"docencia")}">{L["docencia"]}</a>'
        f'<span class="sep">/</span>'
        f'<a href="{hub_url}">{L["section_label"]} {GRUP}</a>'
        f'<span class="sep">/</span><span class="current">{L["h1"]}</span>'
    )

    return f"""<!DOCTYPE html>
<html lang="{L['html_lang']}">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title} — Àlex Reyes</title>
<meta name="description" content="{L['meta_desc']}">
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
  .print-only {{ display:none; }}
  .horari-wrap {{ overflow-x:auto; -webkit-overflow-scrolling:touch; border:1px solid var(--border); border-radius:var(--radius); background:var(--bg); }}
  table.horari, table.mat-taula {{ width:100%; border-collapse:collapse; font-size:0.86rem; }}
  table.horari {{ min-width:660px; table-layout:fixed; }}
  table.horari th, table.horari td, table.mat-taula th, table.mat-taula td {{ border:1px solid var(--border); padding:0.5rem 0.55rem; text-align:left; vertical-align:top; }}
  table.horari thead th, table.mat-taula thead th {{ background:var(--bg-subtle); font-size:0.72rem; text-transform:uppercase; letter-spacing:0.05em; color:var(--text-soft); font-weight:600; text-align:center; }}
  table.horari .hora-h {{ width:5.2rem; }}
  th.hora {{ width:5.2rem; font-family:var(--mono); font-size:0.76rem; font-weight:500; color:var(--text-soft); background:var(--bg-subtle); white-space:nowrap; }}
  th.hora span {{ display:block; color:var(--text-faint); }}
  td.cell {{ line-height:1.3; }}
  .mat {{ display:block; font-weight:600; color:var(--text); font-size:0.84rem; }}
  .profs {{ display:block; margin-top:0.2rem; }}
  .prof {{ display:block; font-size:0.72rem; color:var(--text-faint); }}
  td.cell-meu {{ background:var(--bg-subtle); box-shadow:inset 3px 0 0 var(--focus); }}
  td.cell-meu .mat {{ color:var(--focus); }}
  tr.row-break td {{ text-align:center; font-size:0.74rem; text-transform:uppercase; letter-spacing:0.08em; color:var(--text-faint); background:var(--bg-subtle); }}
  .d-short {{ display:none; }}
  table.mat-taula th[scope="row"] {{ font-weight:500; font-size:0.86rem; }}
  table.mat-taula .mat-meu {{ color:var(--focus); font-weight:600; }}
  table.mat-taula .num {{ text-align:center; font-family:var(--mono); width:5rem; }}
  .horari-actions {{ display:flex; align-items:center; gap:0.75rem; flex-wrap:wrap; margin:0 0 0.5rem; }}
  .legend {{ display:flex; align-items:center; gap:0.4rem; font-size:0.8rem; color:var(--text-soft); }}
  .legend i {{ width:0.9rem; height:0.9rem; border-radius:3px; background:var(--bg-subtle); border:1px solid var(--border); box-shadow:inset 3px 0 0 var(--focus); display:inline-block; flex:none; }}
  @media (max-width:560px) {{
    table.horari {{ min-width:560px; font-size:0.78rem; }}
    .d-long {{ display:none; }} .d-short {{ display:inline; }}
    .prof {{ font-size:0.66rem; }}
  }}
  @media print {{
    @page {{ size:A4 landscape; margin:10mm; }}
    nav, footer, .breadcrumb, .horari-actions, .no-print, .curso-banner,
    .gs-fab, .gs-ov {{ display:none !important; }}
    .print-only {{ display:table-caption; }}
    html, body {{ height:auto; min-height:0; }}
    body {{ background:#fff; color:#000; }}
    main, .container {{ padding:0 !important; margin:0 !important; max-width:none !important; }}
    .page-header {{ margin:0 0 3mm !important; padding:0 !important; border:none !important; }}
    .page-header h1 {{ font-size:15pt; margin:0; }}
    .page-header p, .info-grid {{ display:none !important; }}
    .horari-wrap {{ overflow:visible; border:none; border-radius:0; }}
    table.horari {{ min-width:0; width:100%; font-size:8.5pt; page-break-inside:avoid; }}
    table.horari caption {{ font-size:11pt; font-weight:700; text-align:left; padding:0 0 3mm; }}
    table.horari th, table.horari td {{ border:0.4pt solid #999; padding:1.6mm 1.4mm; }}
    table.horari thead th {{ background:#eee !important; color:#000; -webkit-print-color-adjust:exact; print-color-adjust:exact; }}
    th.hora, tr.row-break td {{ background:#f6f6f6 !important; color:#000; -webkit-print-color-adjust:exact; print-color-adjust:exact; }}
    td.cell-meu {{ background:#f0f0f0 !important; box-shadow:none; -webkit-print-color-adjust:exact; print-color-adjust:exact; }}
    td.cell-meu .mat, .mat {{ color:#000; }}
    .prof {{ color:#444; font-size:7pt; }}
    .d-long {{ display:inline; }} .d-short {{ display:none; }}
    h2, .mat-taula, .legend, .mat-taula-wrap {{ display:none !important; }}
  }}
</style>
<script defer src="/assets/js/curso-banner.js{v}"></script>
</head>
<body>
<a class="skip-link" href="#main">{L['skip']}</a>
<nav>
  <div class="nav-inner">
    <a href="{lang_prefix(lang)}/" class="nav-brand">alexreyes.es</a>
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
        <span class="section-label">{L['section_label']} {GRUP}</span>
        <span class="tag tag-green">{YEAR}</span>
      </div>
      <h1 style="margin:0.3rem 0 0.6rem">{L['h1']} &middot; {GRUP}</h1>
      <p style="font-size:0.98rem;color:var(--text-soft)">{L['intro']}</p>
    </div>

    <div class="info-grid">
      <div class="info-card"><div class="info-card-label">{L['curs_label']}</div><div class="info-card-value" style="font-size:0.88rem">{L['curs_value']}</div></div>
      <div class="info-card"><div class="info-card-label">{L['year_label']}</div><div class="info-card-value" style="font-size:0.88rem">{YEAR}</div></div>
      <div class="info-card"><div class="info-card-label">{L['sessions_label']}</div><div class="info-card-value">{total}</div></div>
    </div>

    <div class="horari-actions" style="margin-top:2.5rem">
      <button type="button" class="btn btn-primary" onclick="window.print()">
        <span aria-hidden="true">🖨️</span> {L['print_btn']}
      </button>
      <span class="legend"><i aria-hidden="true"></i>{L['meu_legend']}</span>
    </div>
    <p class="no-print" style="font-size:0.82rem;color:var(--text-faint);margin:0 0 1.1rem">{L['print_help']}</p>

{render_grid(L, lang)}

    <h2 style="font-size:1.1rem;margin:2.5rem 0 1rem">{L['subjects_h2']}</h2>
{render_subject_table(L, lang)}

    <p class="no-print" style="margin-top:2.5rem">
      <a href="{hub_url}" style="font-size:0.9rem">&larr; {L['back']}</a>
    </p>

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
</script>
<script defer src="/assets/js/search.js{v}"></script>
</body>
</html>
"""


def main():
    for lang in LANGS:
        if lang == "es":
            out = REPO / "docencia" / CODE / SLUG / "index.html"
        else:
            out = REPO / lang / "docencia" / CODE / SLUG / "index.html"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(render_page(lang), encoding="utf-8")
        print(f"  ✓ {out.relative_to(REPO)}")
    print(f"\n{len(LANGS)} pages · {GRUP} · {YEAR}")


if __name__ == "__main__":
    main()
