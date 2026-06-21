#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Genera, para cada prueba Prova Cangur (colección con `prova_cangur`), las páginas
trilingües: index.html y pN.html en root (UI es), /ca (UI ca) y /en (UI en).
El contenido del enunciado va en catalán (root + /ca) o inglés (/en). Las colecciones
archivadas (schema_version < 3 o archivado=true) reciben stubs noindex que redirigen a
la prueba canónica. Idempotente."""
import json
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
EJ = REPO / "assets" / "data" / "ejercicios"
TAGS = json.load(open(REPO / "assets" / "data" / "tags.json", encoding="utf-8"))
CE = TAGS["namespaces"]["concepto_eso"]["valores"]
V = "202606211432"
CANONICAL_FOR = {"2526-cangur-prova-1eso-b": "2526-cangur-prova-1eso-a",
                 "2526-cangur-prova-2eso-b": "2526-cangur-prova-2eso-a"}

def esc(s):
    return str(s or "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")

LANGS = [
    {"code": "es", "pfx": "", "html": "es"},
    {"code": "ca", "pfx": "/ca", "html": "ca"},
    {"code": "en", "pfx": "/en", "html": "en"},
]
TX = {
 "es": dict(notice_title="Solo en catalán", notice_msg="La Prova Cangur solo está disponible en catalán.", notice_btn="Ver en catalán",
   zoom="Ampliar imagen", doc="Docencia", phd="Doctorado", notes="Notas", contact="Contacto", home="Inicio",
   cangur="Cangur", prova="Prova Cangur", preguntas="Preguntas", pregunta="Pregunta", pts="puntos",
   show="Mostrar respuesta", correct="Respuesta correcta", test="Ponte a prueba",
   prev="Anterior", next="Siguiente", index="Índice", dl="Descargar enunciados (PDF)",
   dlsol="Descargar respuestas (PDF)", pend="La solución razonada paso a paso se añadirá próximamente.",
   practel="Practica esta prueba completa en el", each="Cada tarjeta abre la pregunta con su respuesta.",
   intro="Prueba tipo test con corrección automática y puntuación oficial.", tag="Matemáticas, docencia y doctorado", lic="Licencias"),
 "ca": dict(zoom="Ampliar imatge", doc="Docència", phd="Doctorat", notes="Notes", contact="Contacte", home="Inici",
   cangur="Cangur", prova="Prova Cangur", preguntas="Preguntes", pregunta="Pregunta", pts="punts",
   show="Mostrar resposta", correct="Resposta correcta", test="Posa't a prova",
   prev="Anterior", next="Següent", index="Índex", dl="Baixar enunciats (PDF)",
   dlsol="Baixar respostes (PDF)", pend="La solució raonada pas a pas s'afegirà pròximament.",
   practel="Practica aquesta prova completa al", each="Cada targeta obre la pregunta amb la seva resposta.",
   intro="Prova tipus test amb correcció automàtica i puntuació oficial.", tag="Matemàtiques, docència i doctorat", lic="Llicències"),
 "en": dict(notice_title="Only in Catalan", notice_msg="The Cangur Test is only available in Catalan.", notice_btn="View in Catalan",
   zoom="Enlarge image", doc="Teaching", phd="PhD", notes="Notes", contact="Contact", home="Home",
   cangur="Cangur", prova="Cangur Test", preguntas="Questions", pregunta="Question", pts="points",
   show="Show answer", correct="Correct answer", test="Test yourself",
   prev="Previous", next="Next", index="Index", dl="Download questions (PDF)",
   dlsol="Download answers (PDF)", pend="The full step-by-step solution will be added soon.",
   practel="Practise this whole paper in the", each="Each card opens the question with its answer.",
   intro="Multiple-choice test with auto-marking and official scoring.", tag="Mathematics, teaching and PhD", lic="Licences"),
}
DIF = {"facil": {"es": "Fácil", "ca": "Fàcil", "en": "Easy"},
       "media": {"es": "Media", "ca": "Mitjana", "en": "Medium"},
       "dificil": {"es": "Difícil", "ca": "Difícil", "en": "Hard"}}


def lang_switch(code, url_index_path, fname):
    def a(c, pfx):
        href = pfx + url_index_path + fname
        return f'<a href="{href}" class="lang-active">{c.upper()}</a>' if c == code else f'<a href="{href}">{c.upper()}</a>'
    return a("es", "") + '<span class="lang-sep">&middot;</span>' + a("ca", "/ca") + '<span class="lang-sep">&middot;</span>' + a("en", "/en")


def nav(code, pfx, url_index_path, fname):
    t = TX[code]
    return f'''<nav>
  <div class="nav-inner">
    <a href="/" class="nav-brand">alexreyes.es</a>
    <div class="nav-links">
      <a href="{pfx}/docencia/" class="nav-active">{t["doc"]}</a>
      <a href="{pfx}/doctorado/">{t["phd"]}</a>
      <a href="{pfx}/notas/">{t["notes"]}</a>
      <a href="{pfx}/cv/">CV</a>
      <a href="{pfx}/contacto/">{t["contact"]}</a>
    </div>
    <div class="nav-right">
      <div class="lang-sw">{lang_switch(code, url_index_path, fname)}</div>
      <button class="nav-hamburger" onclick="toggleMenu()" aria-label="Menu"><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><line x1="4" y1="7" x2="20" y2="7"/><line x1="4" y1="12" x2="20" y2="12"/><line x1="4" y1="17" x2="20" y2="17"/></svg></button>
      <button class="theme-btn" onclick="toggleTheme()" aria-label="Toggle theme">
        <svg class="icon-sun" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="5"/><line x1="12" y1="1" x2="12" y2="3"/><line x1="12" y1="21" x2="12" y2="23"/><line x1="4.22" y1="4.22" x2="5.64" y2="5.64"/><line x1="18.36" y1="18.36" x2="19.78" y2="19.78"/><line x1="1" y1="12" x2="3" y2="12"/><line x1="21" y1="12" x2="23" y2="12"/><line x1="4.22" y1="19.78" x2="5.64" y2="18.36"/><line x1="18.36" y1="5.64" x2="19.78" y2="4.22"/></svg>
        <svg class="icon-moon" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/></svg>
      </button>
    </div>
  </div>
</nav>'''


def head(code, html, title, desc, url_index_path, fname, extra=""):
    cn = ("" if code == "es" else "/" + code) + url_index_path + fname
    skip = {"es": "Saltar al contenido", "ca": "Salta al contingut", "en": "Skip to content"}[code]
    return f'''<!DOCTYPE html>
<html lang="{html}">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{esc(title)} | Àlex Reyes</title>
<meta name="description" content="{esc(desc)}">
<meta name="robots" content="index, follow">
<script>(function(){{var s=localStorage.getItem('theme');if(s)document.documentElement.setAttribute('data-theme',s);else document.documentElement.setAttribute('data-theme','light');}})();</script>
<script src="/assets/js/lang-persist.js?v={V}"></script>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap" media="print" onload="this.media='all'"><noscript><link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap"></noscript>
<link rel="stylesheet" href="/style.css?v={V}">
<link rel="stylesheet" href="/assets/css/examenes.css?v={V}">
<link rel="stylesheet" href="/assets/css/prova-test.css?v={V}">{extra}
<link rel="icon" type="image/svg+xml" href="/favicon.svg">
<link rel="canonical" href="https://alexreyes.es{cn}">
<link rel="alternate" hreflang="es" href="https://alexreyes.es{url_index_path}{fname}">
<link rel="alternate" hreflang="ca" href="https://alexreyes.es/ca{url_index_path}{fname}">
<link rel="alternate" hreflang="en" href="https://alexreyes.es/en{url_index_path}{fname}">
<link rel="alternate" hreflang="x-default" href="https://alexreyes.es{url_index_path}{fname}">
</head>
<body>
<a class="skip-link" href="#main">{skip}</a>'''


def footer(code):
    t = TX[code]
    return f'''<footer>
  <div class="container">
    <div class="footer-inner">
      <span><strong>Àlex Reyes</strong> &middot; {t["tag"]}</span>
      <span>Barcelona &middot; &copy; 2026 Àlex Reyes &middot; <a href="/assets/NOTICES.txt" style="color:inherit">{t["lic"]}</a></span>
    </div>
  </div>
</footer>
<script>
function toggleMenu(){{document.querySelector("nav").classList.toggle("open");}}
function toggleTheme(){{var h=document.documentElement,n=h.getAttribute('data-theme')==='dark'?'light':'dark';h.setAttribute('data-theme',n);localStorage.setItem('theme',n);}}
</script>'''


def title_for(col, code):
    return col.get("titulo")   # contenido solo en catalán (modo imagen)

def q_title(ej, code):
    return ej.get("titulo")

def concept_labels(ej, code):
    out = []
    for c in (ej.get("tags") or {}).get("concepto_eso") or []:
        lab = CE.get(c, {}).get("label", {})
        out.append(lab.get(code) or lab.get("ca") or lab.get("es") or c)
    return out


def render_index(col, code):
    t = TX[code]; pfx = "" if code == "es" else "/" + code
    uip = col["url_index"]; ID = col["id"]
    title = title_for(col, code)
    cards = []
    for ej in col["ejercicios"]:
        n = ej["numero"]
        chips = ""
        dif = (ej.get("tags") or {}).get("dificultad")
        if dif in DIF:
            chips += f'<span class="ib-chip dif-{dif}">{DIF[dif][code]}</span>'
        for lab in concept_labels(ej, code):
            chips += f'<span class="ib-chip">{esc(lab)}</span>'
        cards.append(f'''      <a href="{pfx}{uip}p{n}.html" class="question-card">
        <div class="question-card-num">{n:02d}</div>
        <div class="question-card-body"><h3>{esc(q_title(ej, code))}</h3>
          <div class="question-card-chips">{chips}</div></div>
        <div class="question-card-score"><strong>{ej["puntuacion"]}</strong>{t["pts"]}</div>
      </a>''')
    pdf_icon = '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/></svg>'
    body = f'''
{nav(code, pfx, uip, "")}
<main id="main">
  <div class="container" style="padding-top:2rem;padding-bottom:5rem">
    <div class="breadcrumb"><a href="{pfx}/">{t["home"]}</a><span class="sep">/</span><a href="{pfx}/docencia/cangur/">{t["cangur"]}</a><span class="sep">/</span><a href="{pfx}/aula/cangur/prova/">{t["prova"]}</a><span class="sep">/</span><span class="current">{esc(title.split("·")[-1].strip())}</span></div>
    <div class="exam-header">
      <div style="display:flex;gap:0.5rem;flex-wrap:wrap;margin-bottom:0.6rem"><span class="section-label">{t["prova"]}</span><span class="tag tag-blue">1r ESO</span></div>
      <h1 style="font-size:clamp(1.6rem,3vw,2.1rem);margin-bottom:0.5rem">{esc(title)}</h1>
      <p style="color:var(--text-soft);max-width:44rem">{t["intro"]}</p>
      <div style="display:flex;gap:0.6rem;flex-wrap:wrap;margin-top:1rem">
        <a href="{pfx}/aula/cangur/prova/test/?id={ID}" class="pdf-download" style="background:#10b981;color:#fff">📝 {t["test"]}</a>
        <a href="{uip}original.pdf" class="pdf-download" target="_blank" rel="noopener">{pdf_icon} {t["dl"]}</a>
        <a href="{uip}solucions.pdf" class="pdf-download" style="background:var(--bg-subtle);color:var(--text);border:1px solid var(--border)" target="_blank" rel="noopener">{pdf_icon} {t["dlsol"]}</a>
      </div>
    </div>
    <h2 style="font-size:1.2rem;margin-bottom:0.4rem">{t["preguntas"]}</h2>
    <p style="color:var(--text-faint);font-size:0.86rem;margin-bottom:1rem">{t["each"]}</p>
    <div class="question-cards">
{chr(10).join(cards)}
    </div>
  </div>
</main>
{footer(code)}
</body>
</html>'''
    return head(code, LANGS_BY[code]["html"], title, t["intro"], uip, "", "") + body


def render_pn(col, ej, code, n_total):
    t = TX[code]; pfx = "" if code == "es" else "/" + code
    uip = col["url_index"]; ID = col["id"]; n = ej["numero"]
    title = q_title(ej, code); sol = ej.get("solucion", ""); imagen = ej.get("imagen")
    chips = ""
    dif = (ej.get("tags") or {}).get("dificultad")
    if dif in DIF:
        chips += f'<span class="ib-chip dif-{dif}">{DIF[dif][code]}</span>'
    for lab in concept_labels(ej, code):
        chips += f'<span class="ib-chip">{esc(lab)}</span>'
    prev_l = f'<a href="p{n-1}.html" class="exam-nav-btn">← {t["prev"]}</a>' if n > 1 else f'<span class="exam-nav-btn is-off">← {t["prev"]}</span>'
    next_l = f'<a href="p{n+1}.html" class="exam-nav-btn">{t["next"]} →</a>' if n < n_total else f'<span class="exam-nav-btn is-off">{t["next"]} →</span>'
    examname = title_for(col, code).split("·")[-1].strip()
    navrow = f'''<div class="exam-nav" style="display:flex;justify-content:space-between;align-items:center;gap:0.6rem;margin:{{m}}">
      {prev_l}<a href="{pfx}{uip}" class="exam-nav-btn">{t["index"]} · {n}/{n_total}</a>{next_l}
    </div>'''
    body = f'''
{nav(code, pfx, uip, f"p{n}.html")}
<main id="main">
  <div class="container" style="padding-top:2rem;padding-bottom:5rem;max-width:780px">
    <div class="breadcrumb"><a href="{pfx}/">{t["home"]}</a><span class="sep">/</span><a href="{pfx}/aula/cangur/prova/">{t["prova"]}</a><span class="sep">/</span><a href="{pfx}{uip}">{esc(examname)}</a><span class="sep">/</span><span class="current">P{n}</span></div>
    {navrow.format(m="0 0 1.2rem")}
    <div style="display:flex;align-items:center;gap:0.6rem;flex-wrap:wrap;margin-bottom:0.5rem"><span class="section-label">{t["pregunta"]} {n}</span><span class="pt-q-pts">{ej["puntuacion"]} {t["pts"]}</span></div>
    <h1 style="font-size:1.5rem;margin:0.2rem 0 0.8rem">{esc(title)}</h1>
    <div class="ib-chips" style="margin-bottom:1rem">{chips}</div>
    <a class="pt-qfull-wrap" href="{imagen}" target="_blank" rel="noopener" title="{t['zoom']}"><img class="pt-qfull" src="{imagen}" alt="{t['pregunta']} {n}"><span class="pt-zoom">🔍</span></a>
    <button class="solution-toggle" style="margin-top:1rem" onclick="var s=document.getElementById('sol');s.hidden=!s.hidden;this.setAttribute('aria-expanded',!s.hidden);">{t["show"]}</button>
    <section class="solution" id="sol" hidden style="margin-top:1rem">
      <p style="font-size:1.1rem"><strong>{t["correct"]}:</strong> <span class="pt-opt ok sel" style="cursor:default">{sol})</span></p>
      <p class="pt-faint" style="margin-top:0.6rem">{t["practel"]} <a href="{pfx}/aula/cangur/prova/test/?id={ID}">«{t["test"]}»</a>.</p>
    </section>
    {navrow.format(m="2rem 0 0")}
  </div>
</main>
{footer(code)}
</body>
</html>'''
    return head(code, LANGS_BY[code]["html"], f"{title} · {examname}", f"{title} — {examname}", uip, f"p{n}.html", "") + body


def stub(col):
    """Página noindex que redirige a la prueba canónica (para modelos archivados)."""
    canon = CANONICAL_FOR.get(col["id"], "2526-cangur-prova-1eso-a")
    target = f"/aula/cangur/examenes/{canon}/"
    return target


def write_stub_pages(col):
    canon = CANONICAL_FOR.get(col["id"], "2526-cangur-prova-1eso-a")
    base = REPO / col["url_index"].lstrip("/")
    n_total = len(col.get("ejercicios", [])) or 30
    def page(target, title):
        return f'''<!DOCTYPE html><html lang="ca"><head><meta charset="UTF-8">
<meta name="robots" content="noindex, follow">
<link rel="canonical" href="https://alexreyes.es{target}">
<meta http-equiv="refresh" content="0; url={target}">
<title>{title}</title></head><body>
<p>Aquesta versió és la mateixa prova reordenada. Redirigint a <a href="{target}">la prova</a>…</p>
</body></html>'''
    (base / "index.html").write_text(page(f"/aula/cangur/examenes/{canon}/", "Model arxivat"), encoding="utf-8")
    for i in range(1, n_total + 1):
        (base / f"p{i}.html").write_text(page(f"/aula/cangur/examenes/{canon}/p{i}.html", f"P{i}"), encoding="utf-8")
    return n_total + 1


LANGS_BY = {l["code"]: l for l in LANGS}


def notice_page(code, ca_url, fname=""):
    """Página (es/en) avisando de que la Prova Cangur solo está en catalán."""
    t = TX[code]; pfx = "" if code == "es" else "/" + code
    uip = ca_url.replace("/ca", "", 1)
    head_html = f'''<!DOCTYPE html>
<html lang="{LANGS_BY[code]["html"]}">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{esc(t["notice_title"])} — Prova Cangur | Àlex Reyes</title>
<meta name="description" content="{esc(t["notice_msg"])}">
<meta name="robots" content="noindex, follow">
<script>(function(){{var s=localStorage.getItem('theme');if(s)document.documentElement.setAttribute('data-theme',s);else document.documentElement.setAttribute('data-theme','light');}})();</script>
<script src="/assets/js/lang-persist.js?v={V}"></script>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap" media="print" onload="this.media='all'"><noscript><link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap"></noscript>
<link rel="stylesheet" href="/style.css?v={V}">
<link rel="icon" type="image/svg+xml" href="/favicon.svg">
<link rel="canonical" href="https://alexreyes.es{ca_url}{fname}">
</head>
<body>
<a class="skip-link" href="#main">Skip</a>'''
    body = f'''
{nav(code, pfx, uip, fname)}
<main id="main">
  <div class="container" style="padding:5rem 1rem;max-width:560px;text-align:center">
    <div style="font-size:2.2rem;margin-bottom:0.6rem">🗣️</div>
    <h1 style="font-size:1.5rem;margin-bottom:0.6rem">{esc(t["notice_title"])}</h1>
    <p style="color:var(--text-soft);margin-bottom:1.6rem">{esc(t["notice_msg"])}</p>
    <a href="{ca_url}{fname}" class="pdf-download" style="background:#10b981;color:#fff">{esc(t["notice_btn"])} →</a>
  </div>
</main>
{footer(code)}
</body>
</html>'''
    return head_html + body


def main():
    n_pages = 0; n_stub = 0; n_notice = 0
    for jf in sorted(EJ.glob("*.json")):
        col = json.load(open(jf, encoding="utf-8"))
        if not col.get("prova_cangur"):
            continue
        if col.get("schema_version", 1) < 3 or col.get("archivado"):
            n_stub += write_stub_pages(col)
            print(f"  ⏷ {col['id']}: stubs noindex → canónica")
            continue
        uip = col["url_index"]
        ca_index = "/ca" + uip
        for L in LANGS:
            outdir = REPO / (L["pfx"].lstrip("/") + uip).lstrip("/") if L["pfx"] else REPO / uip.lstrip("/")
            outdir.mkdir(parents=True, exist_ok=True)
            if L["code"] == "ca":
                (outdir / "index.html").write_text(render_index(col, "ca"), encoding="utf-8"); n_pages += 1
                for ej in col["ejercicios"]:
                    (outdir / f"p{ej['numero']}.html").write_text(render_pn(col, ej, "ca", len(col["ejercicios"])), encoding="utf-8"); n_pages += 1
            else:  # es / en → aviso "només en català"
                (outdir / "index.html").write_text(notice_page(L["code"], ca_index, ""), encoding="utf-8"); n_notice += 1
                for ej in col["ejercicios"]:
                    (outdir / f"p{ej['numero']}.html").write_text(notice_page(L["code"], ca_index, f"p{ej['numero']}.html"), encoding="utf-8"); n_notice += 1
        print(f"  ✓ {col['id']}: ca (real) + es/en (aviso)")
    print(f"OK — {n_pages} páginas ca, {n_notice} avisos es/en, {n_stub} stubs")


if __name__ == "__main__":
    main()
