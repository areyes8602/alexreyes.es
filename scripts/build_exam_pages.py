#!/usr/bin/env python3
"""Auto-generate the index.html page for each exam collection.

For every collection JSON in assets/data/ejercicios/*.json whose `url_index`
points inside the repo, this script writes that path's index.html with:
  - header with metadata
  - baremo table
  - one card per ejercicio with points, descriptor chips and link
  - download link to the PDF

Run:  python3 scripts/build_exam_pages.py
"""
import json
import os
import sys
from datetime import date
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = REPO_ROOT / "assets" / "data"
TAGS_FILE = DATA_DIR / "tags.json"
EJ_DIR = DATA_DIR / "ejercicios"


def load(p):
    with open(p, encoding="utf-8") as f:
        return json.load(f)


def esc(s):
    return str(s or "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")


def format_fecha(iso, lang='es'):
    """2026-04-07 → 7 abr 2026"""
    if not iso:
        return ""
    meses = {
        "es": ["ene", "feb", "mar", "abr", "may", "jun", "jul", "ago", "sep", "oct", "nov", "dic"],
        "ca": ["gen", "feb", "març", "abr", "maig", "juny", "jul", "ago", "set", "oct", "nov", "des"],
        "en": ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"],
    }[lang]
    try:
        y, m, d = iso.split("-")
        return f"{int(d)} {meses[int(m) - 1]} {y}"
    except Exception:
        return iso


LANGS = {
    "es": {
        "home": "Inicio", "docencia": "Docencia", "doctorado": "Doctorado", "notas": "Notas",
        "cv": "CV", "contacto": "Contacto", "skip": "Saltar al contenido",
        "promocion": "Promoción", "fecha": "Fecha", "total": "Total", "puntos": "puntos",
        "preguntas": "Preguntas", "card_help": "Cada tarjeta abre el enunciado correspondiente.",
        "dl_enun": "Descargar enunciados (PDF)", "dl_sol": "Descargar soluciones (PDF)",
        "baremo": "Baremo de conversión",
        "baremo_help": "Conversión de puntos totales a nota IB (escala 1&ndash;7).",
        "th_puntos": "Puntos", "th_nota": "Nota IB", "examen": "Examen",
        "footer": "Matemáticas, docencia y doctorado", "licencias": "Licencias",
    },
    "ca": {
        "home": "Inici", "docencia": "Docència", "doctorado": "Doctorat", "notas": "Notes",
        "cv": "CV", "contacto": "Contacte", "skip": "Salta al contingut",
        "promocion": "Promoció", "fecha": "Data", "total": "Total", "puntos": "punts",
        "preguntas": "Preguntes", "card_help": "Cada targeta obre l'enunciat corresponent.",
        "dl_enun": "Descarrega els enunciats (PDF)", "dl_sol": "Descarrega les solucions (PDF)",
        "baremo": "Barem de conversió",
        "baremo_help": "Conversió de punts totals a nota IB (escala 1&ndash;7).",
        "th_puntos": "Punts", "th_nota": "Nota IB", "examen": "Examen",
        "footer": "Matemàtiques, docència i doctorat", "licencias": "Llicències",
    },
    "en": {
        "home": "Home", "docencia": "Teaching", "doctorado": "PhD", "notas": "Notes",
        "cv": "CV", "contacto": "Contact", "skip": "Skip to content",
        "promocion": "Cohort", "fecha": "Date", "total": "Total", "puntos": "points",
        "preguntas": "Questions", "card_help": "Each card opens its question.",
        "dl_enun": "Download questions (PDF)", "dl_sol": "Download solutions (PDF)",
        "baremo": "Grade conversion", "baremo_help": "Total points converted to the IB grade (1&ndash;7).",
        "th_puntos": "Points", "th_nota": "IB grade", "examen": "Exam",
        "footer": "Mathematics, teaching and PhD", "licencias": "Licences",
    },
}


def pre(lang):
    """Prefijo de idioma en las rutas: '' para es, '/ca' y '/en' para el resto."""
    return "" if lang == "es" else "/" + lang


def i18n(obj, camp, lang):
    """Valor traducido de un campo si la colección lo trae, y si no el castellano.

    En los JSON de colección la traducción va en '<campo>_i18n': {"ca": ..., "en": ...}.
    Así los ficheros que no la llevan siguen funcionando exactamente igual."""
    if lang != "es":
        tr = (obj.get(camp + "_i18n") or {}).get(lang)
        if tr:
            return tr
    return obj.get(camp)


def idiomas_de(col):
    """Idiomas en los que existe esta colección: siempre es, y ca/en si hay traducción."""
    out = ["es"]
    tr = col.get("titulo_i18n") or {}
    for lang in ("ca", "en"):
        if tr.get(lang):
            out.append(lang)
    return out


def breadcrumb_for(col, tags, lang='es'):
    """Breadcrumb built from the url_index + known subjects."""
    asig = col.get("tags_coleccion", {}).get("materia") or col.get("tags_coleccion", {}).get("asignatura") or ""
    materia_ns = tags["namespaces"].get("materia") or tags["namespaces"].get("asignatura") or {}
    asig_label = materia_ns.get("valores", {}).get(asig, {}).get("label", {}).get("es", asig)
    L = LANGS[lang]
    pr = pre(lang)
    parts = [
        f'<a href="{pr}/">{L["home"]}</a>',
        '<span class="sep">/</span>',
        f'<a href="{pr}/docencia/">{L["docencia"]}</a>',
    ]
    # Route into subject hub if IB AI
    if asig == "ib-ai-hl":
        parts += [
            '<span class="sep">/</span>',
            f'<a href="{pr}/docencia/ib-ai/">IB Mathematics AI</a>',
        ]
        if col.get("promocion"):
            parts += [
                '<span class="sep">/</span>',
                f'<a href="{pr}/docencia/ib-ai/{esc(col["promocion"])}/">{L["promocion"]} {esc(col["promocion"])}</a>',
            ]
    parts += [
        '<span class="sep">/</span>',
        f'<span class="current">{esc(i18n(col, "titulo", lang) or col["id"])}</span>',
    ]
    return "".join(parts)


def chips_for(ejercicio, tags):
    """Concept chips for the card. Reads concepto_iba (NM/TANS), concepto_bach, or concepto_eso."""
    ej_tags = ejercicio.get("tags") or {}
    # Pick whichever concept namespace this exercise uses (in order of likelihood)
    for ns in ("concepto_iba", "concepto_bach", "concepto_eso"):
        codes = ej_tags.get(ns) or []
        if codes:
            ns_def = tags["namespaces"].get(ns, {})
            valores = ns_def.get("valores", {})
            out = []
            for code in codes[:4]:
                v = valores.get(code, {})
                label_full = v.get("label", {}).get("es", code)
                safe_desc = label_full.replace('"', "'")
                out.append(f'<span class="ib-chip" title="{esc(safe_desc)}">{esc(code)}</span>')
            return '<div class="question-card-chips">' + dif_chip(ej_tags) + "".join(out) + "</div>"
    d = dif_chip(ej_tags)
    return '<div class="question-card-chips">' + d + "</div>" if d else ""


DIF_LABEL = {"facil": "Fácil", "media": "Media", "dificil": "Difícil"}


def dif_chip(ej_tags):
    """Colored difficulty chip (classes dif-facil/media/dificil in examenes.css)."""
    d = ej_tags.get("dificultad")
    if d not in DIF_LABEL:
        return ""
    return f'<span class="ib-chip dif-{d}">{DIF_LABEL[d]}</span>'


def summary_for(ejercicio, lang='es'):
    """1-2 line summary built from apartados' tareas."""
    aps = ejercicio.get("apartados") or []
    if not aps:
        return ""
    pieces = []
    for a in aps[:3]:
        t = i18n(a, "tarea", lang) or ""
        if t:
            pieces.append(t.rstrip(" ."))
    if not pieces:
        return ""
    summary = "; ".join(pieces)
    if len(aps) > 3:
        summary += "…"
    if len(summary) > 240:
        summary = summary[:237].rstrip() + "…"
    return f'<p style="color:var(--text-soft);font-size:0.88rem">{esc(summary)}</p>'


def render_baremo(baremo, lang='es'):
    if not baremo:
        return ""
    # sort by nota desc
    rows_sorted = sorted(baremo, key=lambda b: b["nota"], reverse=True)
    rows = "".join(
        f'<tr><td>{int(b["min"])} &ndash; {int(b["max"])}</td><td><strong>{int(b["nota"])}</strong></td></tr>'
        for b in rows_sorted
    )
    L = LANGS[lang]
    return f"""    <div class="exam-scale">
      <h2>{L['baremo']}</h2>
      <p style="color:var(--text-soft);font-size:0.88rem;margin-bottom:1rem">{L['baremo_help']}</p>
      <table class="scale-table">
        <thead><tr><th>{L['th_puntos']}</th><th>{L['th_nota']}</th></tr></thead>
        <tbody>{rows}</tbody>
      </table>
    </div>
"""


def render_card(ej, tags, fallback_pdf, lang='es'):
    # Prefer HTML enunciado if present (shows solution), else PDF page, else fallback.
    url = ej.get("url_enunciado") or ej.get("url_pdf") or ej.get("url") or fallback_pdf or "#"
    chips = chips_for(ej, tags)
    summary = summary_for(ej, lang)
    num = f"{ej.get('numero', 0):02d}"
    titulo = i18n(ej, "titulo", lang) or ej.get("id")
    ptos = ej.get("puntuacion", 0)
    # Integer display if whole
    ptos_disp = int(ptos) if ptos == int(ptos) else ptos
    return f"""      <a href="{esc(url)}" class="question-card">
        <div class="question-card-num">{num}</div>
        <div class="question-card-body">
          <h3>{esc(titulo)}</h3>
          {summary}
          {chips}
        </div>
        <div class="question-card-score"><strong>{ptos_disp}</strong>{LANGS[lang]["puntos"]}</div>
      </a>
"""


def render_page(col, tags, lang='es'):
    tc = col.get("tags_coleccion", {})
    L = LANGS[lang]
    pr = pre(lang)
    title = i18n(col, "titulo", lang) or col["id"]
    total = col.get("puntuacion_total") or sum(e.get("puntuacion", 0) for e in col.get("ejercicios", []))
    # integer display
    total_disp = int(total) if total == int(total) else total
    fecha = format_fecha(col.get("fecha"), lang)
    grupo = col.get("grupo") or ""
    promocion = col.get("promocion") or ""
    pdf_url = col.get("pdf_enunciados") or col.get("pdf_original") or ""
    pdf_sol_url = col.get("pdf_soluciones") or ""
    tipo_col = tc.get("curso_academico") or ""  # yeah not ideal; prefer tipo_coleccion
    # Extract a short id to use as badge (Uxx or Gx)
    col_id = col["id"]
    short_badge = ""
    for part in col_id.split("-"):
        if part.startswith("u") and part[1:].isdigit():
            short_badge = f"U{part[1:]}"
            break
        if part.startswith("g") and part[1:].isdigit():
            short_badge = f"G{part[1:]}"
            break

    # Questions
    # El selector solo ofrece los idiomas que existen: antes prometía CA y EN
    # aunque no se generara ninguna página traducida, y eran 404.
    _idiomas = idiomas_de(col)
    lang_switch = '<span class="lang-sep">&middot;</span>'.join(
        '<a href="%s%s"%s>%s</a>' % (pre(lg), col.get("url_index") or "/",
                                     ' class="lang-active"' if lg == lang else "", lg.upper())
        for lg in _idiomas)
    lang_switch = f'<div class="lang-sw">{lang_switch}</div>' if len(_idiomas) > 1 else ""
    cards = "".join(render_card(ej, tags, pdf_url, lang) for ej in col.get("ejercicios", []))

    meta_chunks = []
    if fecha: meta_chunks.append(f"<span>{L['fecha']} <strong>{esc(fecha)}</strong></span>")
    if grupo: meta_chunks.append(f"<span>Curso <strong>{esc(grupo)}</strong></span>")
    if promocion: meta_chunks.append(f"<span>{L['promocion']} <strong>{esc(promocion)}</strong></span>")
    meta_chunks.append(f"<span>{L['total']} <strong>{total_disp} {L['puntos']}</strong></span>")
    meta_html = "\n        ".join(meta_chunks)

    pdf_icon = '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="12" y1="18" x2="12" y2="12"/><polyline points="9 15 12 12 15 15"/></svg>'
    pdf_buttons = []  # noqa: usa L de render_page
    if pdf_url:
        pdf_buttons.append(f'<a href="{esc(pdf_url)}" class="pdf-download" target="_blank" rel="noopener">{pdf_icon} {L["dl_enun"]}</a>')
    if pdf_sol_url:
        pdf_buttons.append(f'<a href="{esc(pdf_sol_url)}" class="pdf-download" style="background:var(--bg-subtle);color:var(--text);border:1px solid var(--border)" target="_blank" rel="noopener">{pdf_icon} {L["dl_sol"]}</a>')
    pdf_button = '<div style="display:flex;gap:0.6rem;flex-wrap:wrap">' + ''.join(pdf_buttons) + '</div>' if pdf_buttons else ""

    cohort_tag = f'<span class="tag tag-orange">{esc(promocion)}</span>' if promocion else ""
    badge = f'<span class="tag tag-gray">{esc(short_badge)}</span>' if short_badge else ""
    materia_chk = tc.get("materia") or tc.get("asignatura")
    hl_badge = '<span class="level-badge level-hl">HL</span>' if materia_chk == "ib-ai-hl" else ""
    sl_badge = '<span class="level-badge level-sl">SL</span>' if materia_chk == "ib-ai-sl" else ""

    # Short description derived from ejercicios titles
    topics = set()
    for e in col.get("ejercicios", []):
        for t in (e.get("tags") or {}).get("tema") or []:
            topics.add(tags["namespaces"]["tema"]["valores"].get(t, {}).get("label", {}).get("es", t))
    topics = sorted(topics)[:8]
    desc = ", ".join(topics) + "." if topics else ""

    url = col.get("url_index") or f"/aula/ib-ai-hl/examenes/{col_id}/"
    full_url = f"https://alexreyes.es{url}"
    # v3 uses "materia"; older v2 used "asignatura". Try both.
    materia_key = tc.get("materia") or tc.get("asignatura") or ""
    materia_ns = tags["namespaces"].get("materia") or tags["namespaces"].get("asignatura") or {}
    asig_label = materia_ns.get("valores", {}).get(materia_key, {}).get("label", {}).get("es", "")

    html = f"""<!DOCTYPE html>
<html lang="{lang}">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{esc(title)}{" &middot; " + esc(short_badge) if short_badge else ""}{" &middot; " + esc(fecha) if fecha else ""} | Àlex Reyes</title>
<meta name="description" content="{L['examen']} {esc(asig_label)} &mdash; {esc(title)}. {esc(desc)}">
<script>(function(){{var s=localStorage.getItem('theme');if(s)document.documentElement.setAttribute('data-theme',s);else document.documentElement.setAttribute('data-theme','light');}})();</script>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap" media="print" onload="this.media='all'"><noscript><link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap"></noscript>
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/katex.min.css" integrity="sha384-n8MVd4RsNIU0tAv4ct0nTaAbDJwPJzDEaqSD1odI+WdtXRGWt2kTvGFasHpSy3SV" crossorigin="anonymous" media="print" onload="this.media='all'"><noscript><link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/katex.min.css" integrity="sha384-n8MVd4RsNIU0tAv4ct0nTaAbDJwPJzDEaqSD1odI+WdtXRGWt2kTvGFasHpSy3SV" crossorigin="anonymous"></noscript>
<script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/katex.min.js" integrity="sha384-XjKyOOlGwcjNTAIQHIpgOno0Hl1YQqzUOEleOLALmuqehneUG+vnGctmUb0ZY0l8" crossorigin="anonymous"></script>
<script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/contrib/auto-render.min.js" integrity="sha384-+VBxd3r6XgURycqtZ117nYw44OOcIax56Z4dCRWbxyPt0Koah1uHoK0o4+/RRE05" crossorigin="anonymous" onload="renderMathInElement(document.body,{{delimiters:[{{left:'$$',right:'$$',display:true}},{{left:'\\\\[',right:'\\\\]',display:true}},{{left:'$',right:'$',display:false}},{{left:'\\\\(',right:'\\\\)',display:false}}],throwOnError:false}})"></script>
<link rel="stylesheet" href="/style.css">
<link rel="stylesheet" href="/assets/css/examenes.css">
<link rel="icon" type="image/svg+xml" href="/favicon.svg">
<link rel="canonical" href="{full_url}">
<meta property="og:type" content="website">
<meta property="og:url" content="{full_url}">
<meta property="og:title" content="{esc(title)}{" &middot; " + esc(short_badge) if short_badge else ""}">
<meta property="og:description" content="{L['examen']} {esc(asig_label)} &mdash; {esc(title)}.">
<meta property="og:image" content="https://alexreyes.es/og-image.jpg">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:site_name" content="alexreyes.es">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{esc(title)}{" &middot; " + esc(short_badge) if short_badge else ""}">
<meta name="twitter:description" content="{L['examen']} {esc(asig_label)} &mdash; {esc(title)}.">
<meta name="twitter:image" content="https://alexreyes.es/og-image.jpg">
<meta name="robots" content="index, follow">
</head>
<body>
<nav>
  <div class="nav-inner">
    <a href="/" class="nav-brand">alexreyes.es</a>
    <div class="nav-links">
      <a href="{pr}/docencia/" class="nav-active">{L['docencia']}</a>
      <a href="{pr}/doctorado/">{L['doctorado']}</a>
      <a href="{pr}/notas/">{L['notas']}</a>
      <a href="{pr}/cv/">{L['cv']}</a>
      <a href="{pr}/contacto/">{L['contacto']}</a>
    </div>
    <div class="nav-right">
      {lang_switch}
      <button class="theme-btn" onclick="toggleTheme()" aria-label="Toggle theme">
        <svg class="icon-sun" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="5"/><line x1="12" y1="1" x2="12" y2="3"/><line x1="12" y1="21" x2="12" y2="23"/><line x1="4.22" y1="4.22" x2="5.64" y2="5.64"/><line x1="18.36" y1="18.36" x2="19.78" y2="19.78"/><line x1="1" y1="12" x2="3" y2="12"/><line x1="21" y1="12" x2="23" y2="12"/><line x1="4.22" y1="19.78" x2="5.64" y2="18.36"/><line x1="18.36" y1="5.64" x2="19.78" y2="4.22"/></svg>
        <svg class="icon-moon" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/></svg>
      </button>
    </div>
  </div>
</nav>

<main>
  <div class="container" style="padding-top:2rem;padding-bottom:5rem">

    <div class="breadcrumb">
      {breadcrumb_for(col, tags, lang)}
    </div>

    <div class="exam-header">
      <div style="display:flex;gap:0.5rem;flex-wrap:wrap;margin-bottom:0.6rem">
        <span class="section-label">{L['examen']}</span>
        {hl_badge}{sl_badge}
        {cohort_tag}
        {badge}
      </div>
      <h1 style="font-size:clamp(1.7rem,3vw,2.2rem);margin-bottom:0.6rem">{esc(title)}</h1>
      <p style="color:var(--text-soft);font-size:1rem;max-width:44rem">{esc(desc)}</p>
      <div class="exam-meta">
        {meta_html}
      </div>
      {pdf_button}
    </div>

{render_baremo(col.get('baremo'), lang)}
    <h2 style="font-size:1.2rem;margin-bottom:1rem">{L['preguntas']}</h2>
    <p style="color:var(--text-faint);font-size:0.86rem;margin-bottom:1rem">{L['card_help']}</p>
    <div class="question-cards">

{cards}    </div>

  </div>
</main>

<footer>
  <div class="container">
    <div class="footer-inner">
      <span><strong>Àlex Reyes</strong> &middot; {L['footer']}</span>
      <span><a href="/contacto/" style="color:var(--text-faint)">alexreyes@maristes.com</a></span>
    </div>
  </div>
</footer>

<script>
function toggleTheme(){{var h=document.documentElement,n=h.getAttribute('data-theme')==='dark'?'light':'dark';h.setAttribute('data-theme',n);localStorage.setItem('theme',n);}}
</script>
</body>
</html>
"""
    return html


def main():
    tags = load(TAGS_FILE)
    colecciones = sorted(EJ_DIR.glob("*.json"))
    if not colecciones:
        print("No hay colecciones en assets/data/ejercicios/")
        return
    for cf in colecciones:
        col = load(cf)
        sv = col.get("schema_version", 1)
        if sv < 3:
            print(f"  ⏭  {cf.name:30s}  (schema_version={sv}, se omite)")
            continue
        # Les col·leccions de tipus "practica" tenen el seu propi build (build_classe_pages.py)
        if col.get("tipo_coleccion") == "practica":
            print(f"  ⏭  {cf.name:30s}  (tipo=practica, gestionat per build_classe_pages.py)")
            continue
        # Les proves Cangur (prova_cangur) es generen trilingües amb build_prova.py
        if col.get("prova_cangur"):
            print(f"  ⏭  {cf.name:30s}  (prova_cangur, gestionat per build_prova.py)")
            continue
        url_index = col.get("url_index")
        if not url_index:
            print(f"  - {cf.name}: sin url_index (se omite)")
            continue
        # Col·leccions "inline" (deures o exercicis dins d'un apunt) apunten el seu
        # url_index a un fitxer .html ja existent, no a una carpeta pròpia: no se'ls
        # genera index.html.
        if url_index.rstrip("/").endswith(".html"):
            print(f"  ⏭  {cf.name:30s}  (url_index és un fitxer, no una carpeta; se omite)")
            continue
        try:
            # Una página por idioma en el que exista la colección. El castellano
            # siempre; ca/en solo si el JSON trae las traducciones.
            for lang in idiomas_de(col):
                out_path = (REPO_ROOT / pre(lang).lstrip("/")
                            / url_index.lstrip("/") / "index.html")
                out_path.parent.mkdir(parents=True, exist_ok=True)
                out_path.write_text(render_page(col, tags, lang), encoding="utf-8")
            langs = "+".join(idiomas_de(col))
            print(f"  ✓ {cf.name:30s}  →  {url_index}  [{langs}]")
        except Exception as e:
            print(f"  ⚠  {cf.name:30s}  (omès per error: {e})")
            continue


if __name__ == "__main__":
    main()
