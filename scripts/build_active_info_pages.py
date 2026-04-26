#!/usr/bin/env python3
"""Build active subject INFO subpages in 3 languages.

Generates 12 info pages (4 subjects × 3 langs):
  - /docencia/<subject>/info/index.html
  - /ca/docencia/<subject>/info/index.html
  - /en/docencia/<subject>/info/index.html

For 2eso: real horari + avaluació + documents (translated).
For others: structured placeholders.
"""
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
LANGS = ["es", "ca", "en"]


# ─── i18n shared chrome ──────────────────────────────────────────
LABELS = {
    "es": {
        "html_lang": "es",
        "home": "Inicio", "docencia": "Docencia",
        "doctorado_nav": "Doctorado", "notas_nav": "Notas", "cv_nav": "CV", "contacto_nav": "Contacto",
        "info_subpage_title": "Información de la asignatura",
        "section_label": "Información general",
        "back_hub": "Volver al hub de la asignatura",
        "footer_brand": "Matemáticas, docencia y doctorado",
        "block_horari": "Horario de clase",
        "block_aval": "Evaluación y criterios",
        "block_docs": "Documentos del curso",
        "block_mat": "Material necesario",
        "block_aval_ib": "Evaluación IB",
        "block_calendar": "Calendario del curso",
        "block_program_ib": "Programa de estudios",
        "block_calc_ib": "Calculadora Casio CG-50",
        "horari_help": "Tres sesiones semanales por grupo.",
        "aval_help": "Pesos de cada prueba dentro de cada evaluación. La calculadora se puede usar durante las 3 evaluaciones.",
        "ev_1": "1ª evaluación",
        "ev_2": "2ª evaluación",
        "ev_3": "3ª evaluación",
        "fins": "hasta",
        "global_label": "Global",
        "prueba_label": "Prueba",
        "peso_label": "Peso",
        "total_label": "Total",
        "doc_temari": "Temario del curso (PDF)",
        "doc_temari_meta": "Unidades del libro y pesos de evaluación",
        "doc_calendari": "Calendario del curso (XLSX)",
        "doc_calendari_meta": "Temporalización de las 10 unidades — grupo E",
        "mat_empty": "Listado de material disponible próximamente.",
        "ib_aval_text": "HL: Paper 1, Paper 2 y Paper 3 + IA. SL: Paper 1, Paper 2 + IA.",
        "ib_pesos_pending": "Pesos detallados disponibles próximamente.",
        "ib_calendar_pending": "Calendario de exámenes parciales y mock exams — pendiente de publicar.",
        "ib_program_pending": "Subject Guide IB AI — pendiente de subir.",
        "ib_calc_text": "Calculadora gráfica obligatoria para los exámenes IB.",
        "ib_calc_pending": "Guía rápida de uso disponible próximamente.",
        "info_empty": "Disponible próximamente.",
        "days": ["Lunes","Martes","Miércoles","Jueves","Viernes"],
        "groups_label": "Grupos",
        "tag_year_word": "Curso",
        "official_exams": "Exámenes oficiales",
    },
    "ca": {
        "html_lang": "ca",
        "home": "Inici", "docencia": "Docència",
        "doctorado_nav": "Doctorat", "notas_nav": "Notes", "cv_nav": "CV", "contacto_nav": "Contacte",
        "info_subpage_title": "Informació de l'assignatura",
        "section_label": "Informació general",
        "back_hub": "Tornar al hub de l'assignatura",
        "footer_brand": "Matemàtiques, docència i doctorat",
        "block_horari": "Horari de classe",
        "block_aval": "Avaluació i criteris",
        "block_docs": "Documents del curs",
        "block_mat": "Material necessari",
        "block_aval_ib": "Avaluació IB",
        "block_calendar": "Calendari del curs",
        "block_program_ib": "Programa d'estudis",
        "block_calc_ib": "Calculadora Casio CG-50",
        "horari_help": "Tres sessions setmanals per grup.",
        "aval_help": "Pesos de cada prova dins de cada avaluació. La calculadora es pot fer servir durant les 3 avaluacions.",
        "ev_1": "1a avaluació",
        "ev_2": "2a avaluació",
        "ev_3": "3a avaluació",
        "fins": "fins",
        "global_label": "Global",
        "prueba_label": "Prova",
        "peso_label": "Pes",
        "total_label": "Total",
        "doc_temari": "Temari del curs (PDF)",
        "doc_temari_meta": "Unitats del llibre i pesos d'avaluació",
        "doc_calendari": "Calendari del curs (XLSX)",
        "doc_calendari_meta": "Temporització de les 10 unitats — grup E",
        "mat_empty": "Llistat de material disponible properament.",
        "ib_aval_text": "HL: Paper 1, Paper 2 i Paper 3 + IA. SL: Paper 1, Paper 2 + IA.",
        "ib_pesos_pending": "Pesos detallats disponibles properament.",
        "ib_calendar_pending": "Calendari d'exàmens parcials i mock exams — pendent de publicar.",
        "ib_program_pending": "Subject Guide IB AI — pendent de pujar.",
        "ib_calc_text": "Calculadora gràfica obligatòria per als exàmens IB.",
        "ib_calc_pending": "Guia ràpida d'ús disponible properament.",
        "info_empty": "Disponible properament.",
        "days": ["Dilluns","Dimarts","Dimecres","Dijous","Divendres"],
        "groups_label": "Grups",
        "tag_year_word": "Curs",
        "official_exams": "Exàmens oficials",
    },
    "en": {
        "html_lang": "en",
        "home": "Home", "docencia": "Teaching",
        "doctorado_nav": "PhD", "notas_nav": "Notes", "cv_nav": "CV", "contacto_nav": "Contact",
        "info_subpage_title": "Subject information",
        "section_label": "General information",
        "back_hub": "Back to the subject hub",
        "footer_brand": "Mathematics, teaching and research",
        "block_horari": "Class schedule",
        "block_aval": "Assessment criteria",
        "block_docs": "Course documents",
        "block_mat": "Required material",
        "block_aval_ib": "IB Assessment",
        "block_calendar": "Course calendar",
        "block_program_ib": "Subject Guide",
        "block_calc_ib": "Casio CG-50 calculator",
        "horari_help": "Three weekly sessions per group.",
        "aval_help": "Weight of each assessment within each term. Calculator allowed in all 3 terms.",
        "ev_1": "1st term",
        "ev_2": "2nd term",
        "ev_3": "3rd term",
        "fins": "until",
        "global_label": "Comprehensive",
        "prueba_label": "Assessment",
        "peso_label": "Weight",
        "total_label": "Total",
        "doc_temari": "Course syllabus (PDF)",
        "doc_temari_meta": "Book units and assessment weights",
        "doc_calendari": "Course calendar (XLSX)",
        "doc_calendari_meta": "Schedule for 10 units — group E",
        "mat_empty": "Material list coming soon.",
        "ib_aval_text": "HL: Paper 1, Paper 2 and Paper 3 + IA. SL: Paper 1, Paper 2 + IA.",
        "ib_pesos_pending": "Detailed weights coming soon.",
        "ib_calendar_pending": "Partial exams and mock exams calendar — pending publication.",
        "ib_program_pending": "IB AI Subject Guide — pending upload.",
        "ib_calc_text": "Graphic calculator required for IB exams.",
        "ib_calc_pending": "Quick guide coming soon.",
        "info_empty": "Coming soon.",
        "days": ["Monday","Tuesday","Wednesday","Thursday","Friday"],
        "groups_label": "Groups",
        "tag_year_word": "Year",
        "official_exams": "Official exams",
    },
}


# ─── Subject configs ─────────────────────────────────────────────
SUBJ_2ESO = {
    "code": "2eso",
    "title": {"es": "Matemàtiques 2n ESO", "ca": "Matemàtiques 2n ESO", "en": "Mathematics 2n ESO"},
    "section_label": "ESO",
    "tag_year": "2025–26",
    "subtitle_short": {"es": "Mat. 2n ESO", "ca": "Mat. 2n ESO", "en": "Maths 2n ESO"},
    "is_ib": False,
    # Schedule per group
    "schedule": [
        {"name": "Grup A", "days": [(0, "10:00"), (2, "12:25"), (4, "12:25")]},  # Mon, Wed, Fri (idx in days[])
        {"name": "Grup E", "days": [(1, "11:30"), (3, "16:30"), (4, "10:00")]},  # Tue, Thu, Fri
    ],
    # Evaluation breakdown per term
    "aval": [
        {"num": "1", "until": {"es": "3 dic", "ca": "3 des", "en": "3 Dec"}, "units_line": "U01–U04",
         "proves": [
            {"nom": {"es":"Fracciones (previo)","ca":"Fraccions (previ)","en":"Fractions (preview)"}, "pes": 20},
            {"nom": {"es":"Fracciones y decimales","ca":"Fraccions i decimals","en":"Fractions and decimals"}, "pes": 20},
            {"nom": {"es":"Probabilidad","ca":"Probabilitat","en":"Probability"}, "pes": 10},
            {"nom": {"es":"Proporcionalidad","ca":"Proporcionalitat","en":"Proportionality"}, "pes": 20},
            {"nom": {"es":"Global 1ª","ca":"Global 1a","en":"1st term comprehensive"}, "pes": 30, "global": True},
         ]},
        {"num": "2", "until": {"es": "13 mar", "ca": "13 mar", "en": "13 Mar"}, "units_line": "U05–U08",
         "proves": [
            {"nom": {"es":"Gráficas de funciones","ca":"Gràfiques de funcions","en":"Function graphs"}, "pes": 15},
            {"nom": {"es":"Funciones y funciones elementales","ca":"Funcions i funcions elementals","en":"Functions and elementary functions"}, "pes": 25},
            {"nom": {"es":"Pitágoras y poliedros","ca":"Pitàgores i poliedres","en":"Pythagoras and polyhedra"}, "pes": 20},
            {"nom": {"es":"Proyecto Monumento 3.0","ca":"Projecte Monument 3.0","en":"Monument 3.0 project"}, "pes": 10},
            {"nom": {"es":"Global 2ª","ca":"Global 2a","en":"2nd term comprehensive"}, "pes": 30, "global": True},
         ]},
        {"num": "3", "until": {"es": "5 jun", "ca": "5 jun", "en": "5 Jun"}, "units_line": "U09–U10",
         "proves": [
            {"nom": {"es":"Expresiones algebraicas (previo)","ca":"Expressions algebraiques (previ)","en":"Algebraic expressions (preview)"}, "pes": 20},
            {"nom": {"es":"Expresiones algebraicas","ca":"Expressions algebraiques","en":"Algebraic expressions"}, "pes": 25},
            {"nom": {"es":"Problemas de ecuaciones y sistemas","ca":"Problemes d'equacions i sistemes","en":"Equations and systems problems"}, "pes": 25},
            {"nom": {"es":"Global 3ª","ca":"Global 3a","en":"3rd term comprehensive"}, "pes": 30, "global": True},
         ]},
    ],
    "documents": [
        {"href": "/assets/docs/2eso/temari-2526.pdf", "icon": "📘", "title_key": "doc_temari", "meta_key": "doc_temari_meta"},
        {"href": "/assets/docs/2eso/calendari-2eso-e-2526.xlsx", "icon": "🗓️", "title_key": "doc_calendari", "meta_key": "doc_calendari_meta"},
    ],
}

SUBJ_1BTL = {
    "code": "ccss-1btl",
    "title": {"es": "Mat. Aplicadas CCSS 1º BTL", "ca": "Mat. Aplicades CCSS 1r BTL", "en": "Applied Math. Social Sciences 1st BTL"},
    "section_label": {"es": "Bachillerato", "ca": "Batxillerat", "en": "Bachillerato"},
    "tag_year": "2025–26",
    "is_ib": False,
    "schedule": None,  # placeholder
    "aval": None,
    "documents": None,
}

SUBJ_IB_2426 = {
    "code": "ib-ai/2024-2026",
    "title": {"es": "IB AI · Promoción 2024-2026", "ca": "IB AI · Promoció 2024-2026", "en": "IB AI · 2024-2026 Cohort"},
    "section_label": "IB Mathematics AI",
    "tag_year": "2024–2026",
    "is_ib": True,
    "exam_year": 2026,
    "extra_breadcrumb": True,
    "promo": "2024-2026",
}

SUBJ_IB_2527 = {
    "code": "ib-ai/2025-2027",
    "title": {"es": "IB AI · Promoción 2025-2027", "ca": "IB AI · Promoció 2025-2027", "en": "IB AI · 2025-2027 Cohort"},
    "section_label": "IB Mathematics AI",
    "tag_year": "2025–2027",
    "is_ib": True,
    "exam_year": 2027,
    "extra_breadcrumb": True,
    "promo": "2025-2027",
}

SUBJECTS = [SUBJ_2ESO, SUBJ_1BTL, SUBJ_IB_2426, SUBJ_IB_2527]


# ─── Helpers ─────────────────────────────────────────────────────
def lang_prefix(lang):
    return "" if lang == "es" else f"/{lang}"


def lang_switch(lang, code):
    parts = []
    for l in ("es", "ca", "en"):
        href = f"/docencia/{code}/info/" if l == "es" else f"/{l}/docencia/{code}/info/"
        cls = ' class="lang-active"' if l == lang else ""
        parts.append(f'<a href="{href}"{cls}>{l.upper()}</a>')
    return '<span class="lang-sep">&middot;</span>'.join(parts)


def nav_block(lang):
    L = LABELS[lang]
    return (
        f'<a href="{lang_prefix(lang)}/docencia/" class="nav-active">{L["docencia"]}</a>'
        f'<a href="{lang_prefix(lang)}/doctorado/">{L["doctorado_nav"]}</a>'
        f'<a href="{lang_prefix(lang)}/notas/">{L["notas_nav"]}</a>'
        f'<a href="{lang_prefix(lang)}/cv/">{L["cv_nav"]}</a>'
        f'<a href="{lang_prefix(lang)}/contacto/">{L["contacto_nav"]}</a>'
    )


def picker(field, lang):
    if isinstance(field, dict):
        return field.get(lang, field.get("en", ""))
    return field


def render_horari_block(s, L):
    if not s.get("schedule"):
        return f"""    <div class="info-block">
      <h3>🗓️ {L['block_horari']}</h3>
      <p class="empty-line">{L['info_empty']}</p>
    </div>"""
    days_list = L["days"]
    cards_html = ""
    for grp in s["schedule"]:
        rows = "".join(
            f'<div class="schedule-day"><span>{days_list[di]}</span><strong>{time}</strong></div>'
            for di, time in grp["days"]
        )
        cards_html += f"""        <div class="schedule-card">
          <h4>{grp['name']}</h4>
          {rows}
        </div>
"""
    return f"""    <div class="info-block">
      <h3>🗓️ {L['block_horari']}</h3>
      <p style="font-size:0.88rem;color:var(--text-soft);margin:0 0 1rem">{L['horari_help']}</p>
      <div class="schedule-grid">
{cards_html}      </div>
    </div>"""


def render_aval_block(s, L, lang):
    if not s.get("aval"):
        return f"""    <div class="info-block">
      <h3>📊 {L['block_aval']}</h3>
      <p class="empty-line">{L['info_empty']}</p>
    </div>"""
    # Map term number to its translated label
    ev_labels = {"1": L["ev_1"], "2": L["ev_2"], "3": L["ev_3"]}
    cards = ""
    for av in s["aval"]:
        rows = ""
        for p in av["proves"]:
            cls = ' class="global"' if p.get("global") else ""
            nom = picker(p["nom"], lang)
            rows += f'            <tr{cls}><td>{nom}</td><td class="pes">{p["pes"]}%</td></tr>\n'
        until = picker(av["until"], lang)
        cards += f"""        <div class="eval-card">
          <h4>{ev_labels[av['num']]} <span class="small">{L['fins']} {until}</span></h4>
          <p class="units-line">{av['units_line']}</p>
          <table class="eval-table">
{rows}          </table>
        </div>
"""
    return f"""    <div class="info-block">
      <h3>📊 {L['block_aval']}</h3>
      <p style="font-size:0.88rem;color:var(--text-soft);margin:0 0 1rem">{L['aval_help']}</p>
      <div class="eval-grid">
{cards}      </div>
    </div>"""


def render_docs_block(s, L):
    if not s.get("documents"):
        return f"""    <div class="info-block">
      <h3>📄 {L['block_docs']}</h3>
      <p class="empty-line">{L['info_empty']}</p>
    </div>"""
    cards = ""
    for d in s["documents"]:
        cards += f"""        <a href="{d['href']}" target="_blank" rel="noopener" class="doc-card">
          <span class="doc-card-icon">{d['icon']}</span>
          <div>
            <div class="doc-card-title">{L[d['title_key']]}</div>
            <div class="doc-card-meta">{L[d['meta_key']]}</div>
          </div>
        </a>
"""
    return f"""    <div class="info-block">
      <h3>📄 {L['block_docs']}</h3>
      <div class="doc-grid">
{cards}      </div>
    </div>"""


def render_ib_blocks(s, L):
    return f"""    <div class="info-block">
      <h3>📊 {L['block_aval_ib']}</h3>
      <p style="font-size:0.88rem;color:var(--text-soft);margin:0">{L['ib_aval_text']} {L['official_exams']} {{exam_word}} {s['exam_year']}.</p>
      <p class="empty-line">{L['ib_pesos_pending']}</p>
    </div>

    <div class="info-block">
      <h3>🗓️ {L['block_calendar']}</h3>
      <p class="empty-line">{L['ib_calendar_pending']}</p>
    </div>

    <div class="info-block">
      <h3>📘 {L['block_program_ib']}</h3>
      <p class="empty-line">{L['ib_program_pending']}</p>
    </div>

    <div class="info-block">
      <h3>🧮 {L['block_calc_ib']}</h3>
      <p style="font-size:0.88rem;color:var(--text-soft);margin:0">{L['ib_calc_text']}</p>
      <p class="empty-line">{L['ib_calc_pending']}</p>
    </div>"""


def render_info_page(s, lang):
    L = LABELS[lang]
    code = s["code"]
    title = picker(s["title"], lang)
    section_label = picker(s["section_label"], lang)
    base_url = f"{lang_prefix(lang)}/docencia/{code}/info/"
    parent_url = f"{lang_prefix(lang)}/docencia/{code}/"
    canonical = f"https://alexreyes.es{base_url}"
    es_canon = f"https://alexreyes.es/docencia/{code}/info/"
    ca_canon = f"https://alexreyes.es/ca/docencia/{code}/info/"
    en_canon = f"https://alexreyes.es/en/docencia/{code}/info/"

    # Breadcrumb
    if s.get("extra_breadcrumb"):  # IB
        parent_subject = code.split("/")[0]
        promo = code.split("/")[1]
        breadcrumb = (
            f'<a href="{lang_prefix(lang)}/">{L["home"]}</a>'
            f'<span class="sep">/</span>'
            f'<a href="{lang_prefix(lang)}/docencia/">{L["docencia"]}</a>'
            f'<span class="sep">/</span>'
            f'<a href="{lang_prefix(lang)}/docencia/{parent_subject}/">IB Mathematics AI</a>'
            f'<span class="sep">/</span>'
            f'<a href="{parent_url}">{promo}</a>'
            f'<span class="sep">/</span>'
            f'<span class="current">{L["info_subpage_title"]}</span>'
        )
    else:
        breadcrumb = (
            f'<a href="{lang_prefix(lang)}/">{L["home"]}</a>'
            f'<span class="sep">/</span>'
            f'<a href="{lang_prefix(lang)}/docencia/">{L["docencia"]}</a>'
            f'<span class="sep">/</span>'
            f'<a href="{parent_url}">{title}</a>'
            f'<span class="sep">/</span>'
            f'<span class="current">{L["info_subpage_title"]}</span>'
        )

    # Build content blocks
    if s.get("is_ib"):
        # Replace the placeholder for "May" / "Mai" / "May" word
        exam_word = {"es": "mayo", "ca": "maig", "en": "May"}[lang]
        blocks = render_ib_blocks(s, L).replace("{exam_word}", exam_word)
    else:
        blocks = "\n\n".join([
            render_horari_block(s, L),
            render_aval_block(s, L, lang),
            render_docs_block(s, L),
            f"""    <div class="info-block">
      <h3>🎒 {L['block_mat']}</h3>
      <p class="empty-line">{L['mat_empty']}</p>
    </div>""",
        ])

    # Optional IB level badges
    extra_badges = ""
    if s.get("is_ib"):
        extra_badges = '<span class="level-badge level-hl">HL</span><span class="level-badge level-sl">SL</span>'

    return f"""<!DOCTYPE html>
<html lang="{L['html_lang']}">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{L['info_subpage_title']} — {title}</title>
<meta name="description" content="{L['info_subpage_title']} — {title}.">
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
  .schedule-grid {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(220px,1fr)); gap:1rem; }}
  .schedule-card {{ background:var(--bg); border:1px solid var(--border); border-radius:var(--radius-sm); padding:0.9rem 1.1rem; }}
  .schedule-card h4 {{ margin:0 0 0.6rem; font-size:0.78rem; color:var(--text-soft); text-transform:uppercase; letter-spacing:0.05em; font-weight:600; }}
  .schedule-day {{ display:flex; justify-content:space-between; padding:0.3rem 0; font-size:0.92rem; border-bottom:1px solid var(--border); }}
  .schedule-day:last-child {{ border-bottom:none; }}
  .schedule-day strong {{ font-family:var(--mono); color:var(--text); }}
  .eval-grid {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(280px,1fr)); gap:1rem; }}
  .eval-card {{ background:var(--bg); border:1px solid var(--border); border-radius:var(--radius-sm); padding:1.1rem 1.2rem; }}
  .eval-card h4 {{ display:flex; align-items:baseline; justify-content:space-between; gap:0.6rem; margin:0 0 0.7rem; font-size:0.95rem; }}
  .eval-card h4 .small {{ font-size:0.72rem; color:var(--text-faint); font-weight:400; font-family:var(--mono); }}
  .eval-table {{ width:100%; border-collapse:collapse; font-size:0.86rem; }}
  .eval-table td {{ padding:0.4rem 0; border-bottom:1px dashed var(--border); }}
  .eval-table tr:last-child td {{ border-bottom:none; }}
  .eval-table td.pes {{ text-align:right; font-family:var(--mono); color:var(--text-soft); width:60px; }}
  .eval-table tr.global td {{ font-weight:600; padding-top:0.55rem; border-top:2px solid var(--border); border-bottom:none; }}
  .eval-card .units-line {{ font-size:0.78rem; color:var(--text-faint); margin:-0.3rem 0 0.7rem; }}
  .doc-card {{ display:flex; align-items:center; gap:0.8rem; padding:0.95rem 1.15rem; background:var(--bg); border:1px solid var(--border); border-radius:var(--radius-sm); text-decoration:none; color:inherit; transition:border-color 0.15s; }}
  .doc-card:hover {{ border-color:var(--border-strong); }}
  .doc-card-icon {{ font-size:1.5rem; flex-shrink:0; }}
  .doc-card-title {{ font-weight:500; font-size:0.94rem; color:var(--text); }}
  .doc-card-meta {{ font-size:0.78rem; color:var(--text-faint); margin-top:0.15rem; }}
  .doc-grid {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(260px,1fr)); gap:0.8rem; }}
</style>
</head>
<body>
<nav>
  <div class="nav-inner">
    <a href="{lang_prefix(lang)}/" class="nav-brand">alexreyes.es</a>
    <div class="nav-links">{nav_block(lang)}</div>
    <div class="nav-right">
      <div class="lang-sw">{lang_switch(lang, code)}</div>
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
        <span class="section-label">{section_label}</span>
        {extra_badges}<span class="tag tag-orange">{s['tag_year']}</span>
      </div>
      <h1 style="margin:0.3rem 0 0.6rem">{L['info_subpage_title']}</h1>
      <p style="font-size:0.98rem;color:var(--text-soft)">{title}.</p>
    </div>

{blocks}

    <p style="margin-top:2rem;text-align:center">
      <a href="{parent_url}" style="font-size:0.9rem;color:var(--text-faint);text-decoration:none">← {L['back_hub']}</a>
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
    for s in SUBJECTS:
        for lang in LANGS:
            if lang == "es":
                out = REPO / "docencia" / s["code"] / "info" / "index.html"
            else:
                out = REPO / lang / "docencia" / s["code"] / "info" / "index.html"
            out.parent.mkdir(parents=True, exist_ok=True)
            out.write_text(render_info_page(s, lang), encoding="utf-8")
            print(f"  ✓ {out.relative_to(REPO)}")


if __name__ == "__main__":
    main()
