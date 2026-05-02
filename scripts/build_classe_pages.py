#!/usr/bin/env python3
"""Genera una pàgina HTML autònoma per cada exercici d'una col·lecció de classe.

Algunes col·leccions (`tipo_coleccion: "practica"`) viuen com a blocs dins de
les pàgines d'apunts (`/aula/<materia>/apuntes/.../*.html`). Per al banc
d'exercicis, però, volem que cada `url_enunciado` apunti a una pàgina pròpia,
no a l'apunt complet. Aquest script:

1. Llegeix cada `assets/data/ejercicios/*.json` amb `tipo_coleccion: "practica"`.
2. Per cada `ejercicio` agafa el camp `source_apunt` (URL+ancora dins
   d'un apunt) i extreu el bloc `<div class="exercise" id="ex-N">…</div>`
   incloent el `<details>` de la solució.
3. Envolta aquest bloc amb el template estàndard de pàgina d'exercici (idiomes
   i breadcrumb segons la materia) i el desa al `url_enunciado` indicat.
4. També genera un `index.html` de la col·lecció.

És idempotent — torneu-lo a executar sempre que toqueu un apunt o un JSON.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
EJ_DIR = REPO / "assets" / "data" / "ejercicios"

# Idiomes per materia
LANG = {
    "ccss-1btl": "ca",
    "ccss-2btl": "ca",
    "eso-1": "ca", "eso-2": "ca", "eso-3": "ca", "eso-4": "ca",
    "ib-ai-hl": "es", "ib-ai-sl": "es",
}

# Etiquetes UI per idioma
UI = {
    "ca": {
        "show_solution": "Mostra la solució",
        "hide_solution": "Amaga la solució",
        "solution_h": "Solució pas a pas",
        "back_to_apunt": "Veure dins de l'apunt original",
        "exercise": "Exercici",
        "home": "Inici",
        "docencia": "Docència",
        "exercicis_classe": "Exercicis de classe",
    },
    "es": {
        "show_solution": "Mostrar solución",
        "hide_solution": "Ocultar solución",
        "solution_h": "Solución paso a paso",
        "back_to_apunt": "Ver dentro del apunte original",
        "exercise": "Ejercicio",
        "home": "Inicio",
        "docencia": "Docencia",
        "exercicis_classe": "Ejercicios de clase",
    },
}

# Breadcrumb per materia
MATERIA_HUB = {
    "ccss-1btl": ("/docencia/ccss-1btl/", "Mat. Aplicades CCSS 1r BTL"),
    "ccss-2btl": ("/docencia/ccss-2btl/", "Mat. Aplicades CCSS 2n BTL"),
    "eso-2": ("/docencia/2eso/", "2n ESO"),
    "ib-ai-hl": ("/docencia/ib-ai/2024-2026/", "IB Mathematics AI HL"),
    "ib-ai-sl": ("/docencia/ib-ai/2024-2026/", "IB Mathematics AI SL"),
}


def extract_exercise_block(apunt_path: Path, anchor: str) -> tuple[str, str] | None:
    """Donat un fitxer d'apunt i una ancora `ex-N`, torna (statement_html, solution_html).

    `statement_html` no inclou la capçalera `<div class="exercise-head">…</div>`,
    sinó només el contingut útil de `<div class="exercise-statement">`.
    `solution_html` és el contingut del `<div class="solution">` dins del
    `<details>`.
    """
    if not apunt_path.exists():
        print(f"  ⚠ apunt no trobat: {apunt_path}")
        return None
    src = apunt_path.read_text(encoding="utf-8")
    pattern = (
        r'<div class="exercise"\s+id="' + re.escape(anchor) + r'">'
        r'(?P<body>.*?)'
        r'</div>\s*(?=<!--|<div class="exercise"|<nav|</article>|</div>\s*</div>\s*</main>)'
    )
    m = re.search(pattern, src, flags=re.DOTALL)
    if not m:
        # Mètode alternatiu: buscar la meitat oberta i parar al següent <div class="exercise" o <nav class="exam-nav"
        start = src.find(f'<div class="exercise" id="{anchor}">')
        if start < 0:
            print(f"  ⚠ ancora no trobada {anchor} a {apunt_path}")
            return None
        # Trobem el següent inici de <div class="exercise" id= o el final de la secció Exercicis
        rest = src[start:]
        nxt_ex = rest.find('<div class="exercise" id="', 1)
        nxt_nav = rest.find('<nav class="exam-nav"')
        ends = [x for x in (nxt_ex, nxt_nav) if x > 0]
        if not ends:
            print(f"  ⚠ no s'ha pogut tancar el bloc {anchor} a {apunt_path}")
            return None
        body = rest[: min(ends)]
    else:
        body = '<div class="exercise" id="' + anchor + '">' + m.group("body") + "</div>"

    # ── Format estàndard: <div class="exercise-statement">…</div> + <details>…<div class="solution">…</div></details>
    stmt = re.search(r'<div class="exercise-statement">(.*?)</div>\s*(?=<details|</div>)', body, flags=re.DOTALL)
    sol = re.search(r'<details>\s*<summary[^>]*>.*?</summary>\s*<div class="solution">(.*?)</div>\s*</details>', body, flags=re.DOTALL)
    if stmt and sol:
        return stmt.group(1).strip(), sol.group(1).strip()

    # ── Format per-apartado (apunt 05): cada apartat és un .apart > details amb summary (enunciat)
    #     i un .apart-solution (solució). Reconstruïm un statement+solution combinats.
    apart_re = re.compile(
        r'<div class="apart">\s*<details>\s*<summary>(?P<sum>.*?)</summary>\s*<div class="apart-solution">(?P<sol>.*?)</div>\s*</details>\s*</div>',
        flags=re.DOTALL,
    )
    aparts = list(apart_re.finditer(body))
    if aparts:
        # Intro opcional (.exercise-intro)
        intro_match = re.search(r'<p class="exercise-intro">(.*?)</p>', body, flags=re.DOTALL)
        intro_html = f'<p class="note">{intro_match.group(1).strip()}</p>' if intro_match else ''

        stmt_items = []
        sol_blocks = []
        for a in aparts:
            summary = a.group('sum').strip()
            sol_html = a.group('sol').strip()
            # El summary porta <span class="letter">a)</span> <span class="stmt">…</span>
            stmt_items.append(f'<li>{summary}</li>')
            sol_blocks.append(
                f'<div class="apartado-sol"><h4>{summary}</h4>{sol_html}</div>'
            )
        statement_html = intro_html + '<ol class="apartados">\n' + '\n'.join(stmt_items) + '\n</ol>'
        solution_html = '\n'.join(sol_blocks)
        return statement_html, solution_html

    return "", ""


PAGE_TPL = """<!DOCTYPE html>
<html lang="{lang}">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{ui_exercise} {numero} · {titulo} — {hub_label}</title>
<meta name="description" content="{descripcion}">
<script>(function(){{var s=localStorage.getItem('theme');if(s)document.documentElement.setAttribute('data-theme',s);else document.documentElement.setAttribute('data-theme','light');}})();</script>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/katex.min.css" integrity="sha384-n8MVd4RsNIU0tAv4ct0nTaAbDJwPJzDEaqSD1odI+WdtXRGWt2kTvGFasHpSy3SV" crossorigin="anonymous">
<script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/katex.min.js" integrity="sha384-XjKyOOlGwcjNTAIQHIpgOno0Hl1YQqzUOEleOLALmuqehneUG+vnGctmUb0ZY0l8" crossorigin="anonymous"></script>
<script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/contrib/auto-render.min.js" integrity="sha384-+VBxd3r6XgURycqtZ117nYw44OOcIax56Z4dCRWbxyPt0Koah1uHoK0o4+/RRE05" crossorigin="anonymous" onload="renderMathInElement(document.body,{{delimiters:[{{left:'$$',right:'$$',display:true}},{{left:'\\\\[',right:'\\\\]',display:true}},{{left:'$',right:'$',display:false}},{{left:'\\\\(',right:'\\\\)',display:false}}],throwOnError:false}})"></script>
<link rel="stylesheet" href="/style.css">
<link rel="stylesheet" href="/assets/css/examenes.css">
<link rel="icon" type="image/svg+xml" href="/favicon.svg">
<link rel="canonical" href="https://alexreyes.es{url_enunciado}">
<style>
.classe-exercise {{ background: var(--bg); border:1px solid var(--border); border-radius:10px; padding:1.2rem 1.4rem; margin: 1.2rem 0 1.4rem; }}
.classe-exercise .exercise-head {{ display:flex; align-items:baseline; gap:0.6rem; margin-bottom:0.8rem; }}
.classe-exercise .exercise-head .num {{ display:inline-flex; align-items:center; justify-content:center; min-width:2.4rem; height:1.7rem; padding:0 0.55rem; background:#10b981; color:#fff; border-radius:99px; font-family:var(--mono); font-size:0.78rem; font-weight:600; }}
.classe-exercise .exercise-head .ttl {{ font-size:0.78rem; color:var(--text-soft); text-transform:uppercase; letter-spacing:0.06em; font-weight:600; }}
.classe-exercise .statement-wrap > p:first-child {{ margin-top:0; }}
.classe-solution {{ margin-top:1rem; border-top:1px dashed var(--border); padding-top:1rem; }}
.classe-solution > p:first-child {{ margin-top:0; }}
.classe-back {{ display:inline-block; margin-top:1.5rem; font-size:0.85rem; color:var(--text-soft); text-decoration:none; border-bottom:1px dashed var(--border); }}
.classe-back:hover {{ color:#6366f1; border-color:#6366f1; }}
</style>
</head>
<body>
<nav>
  <div class="nav-inner">
    <a href="/" class="nav-brand">alexreyes.es</a>
    <div class="nav-links">
      <a href="/docencia/" class="nav-active">{ui_docencia}</a>
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
</nav>

<main>
  <div class="container" style="padding-top:1.5rem;padding-bottom:5rem;max-width:820px">

    <div class="breadcrumb">
      <a href="/">{ui_home}</a>
      <span class="sep">/</span>
      <a href="/docencia/">{ui_docencia}</a>
      <span class="sep">/</span>
      <a href="{hub_url}">{hub_label}</a>
      <span class="sep">/</span>
      <a href="{coleccion_url}">{coleccion_titulo}</a>
      <span class="sep">/</span>
      <span class="current">{ui_exercise} {numero}</span>
    </div>

    <div class="exam-header" style="padding-top:0;border-bottom:none;margin-bottom:1.2rem">
      <div style="display:flex;gap:0.5rem;flex-wrap:wrap;margin-bottom:0.5rem">
        <span class="section-label">{hub_label}</span>
        <span class="tag tag-orange">{ui_exercicis_classe}</span>
      </div>
      <h1 style="margin:0">{ui_exercise} {numero} · {titulo}</h1>
    </div>

    <article class="classe-exercise">
      <div class="exercise-head">
        <span class="num">{numero}</span>
        <span class="ttl">{titulo}</span>
      </div>
      <div class="statement-wrap">
        {statement_html}
      </div>

      <button class="solution-toggle" data-toggles="sol-{numero}" data-show-label="{ui_show_solution}" data-hide-label="{ui_hide_solution}" onclick="toggleSolucion('sol-{numero}')">
        <span class="toggle-label">{ui_show_solution}</span>
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="6 9 12 15 18 9"/></svg>
      </button>

      <section class="classe-solution" id="sol-{numero}" hidden>
        <h3 style="margin:0 0 0.6rem;font-size:1rem">{ui_solution_h}</h3>
        {solution_html}
      </section>

      <a class="classe-back" href="{source_apunt}">{ui_back_to_apunt} →</a>
    </article>

  </div>
</main>

<footer>
  <div class="container">
    <div class="footer-inner">
      <span><strong>Àlex Reyes</strong> &middot; Matemáticas, docencia y doctorado</span>
      <span>Barcelona &middot; &copy; 2026 Àlex Reyes &middot; <a href="/assets/NOTICES.txt" style="color:inherit">Licencias</a></span>
    </div>
  </div>
</footer>

<script src="/assets/js/examenes.js"></script>
<script>
function toggleMenu(){{document.querySelector("nav").classList.toggle("open");}}
function toggleTheme(){{var h=document.documentElement,n=h.getAttribute('data-theme')==='dark'?'light':'dark';h.setAttribute('data-theme',n);localStorage.setItem('theme',n);}}
</script>
</body>
</html>
"""


COLLECTION_INDEX_TPL = """<!DOCTYPE html>
<html lang="{lang}">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{titulo} — {hub_label}</title>
<meta name="description" content="Llistat d'exercicis de classe de {hub_label}: {titulo}.">
<script>(function(){{var s=localStorage.getItem('theme');if(s)document.documentElement.setAttribute('data-theme',s);else document.documentElement.setAttribute('data-theme','light');}})();</script>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/katex.min.css" integrity="sha384-n8MVd4RsNIU0tAv4ct0nTaAbDJwPJzDEaqSD1odI+WdtXRGWt2kTvGFasHpSy3SV" crossorigin="anonymous">
<script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/katex.min.js" integrity="sha384-XjKyOOlGwcjNTAIQHIpgOno0Hl1YQqzUOEleOLALmuqehneUG+vnGctmUb0ZY0l8" crossorigin="anonymous"></script>
<script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/contrib/auto-render.min.js" integrity="sha384-+VBxd3r6XgURycqtZ117nYw44OOcIax56Z4dCRWbxyPt0Koah1uHoK0o4+/RRE05" crossorigin="anonymous" onload="renderMathInElement(document.body,{{delimiters:[{{left:'$$',right:'$$',display:true}},{{left:'\\\\[',right:'\\\\]',display:true}},{{left:'$',right:'$',display:false}},{{left:'\\\\(',right:'\\\\)',display:false}}],throwOnError:false}})"></script>
<link rel="stylesheet" href="/style.css">
<link rel="stylesheet" href="/assets/css/examenes.css">
<link rel="icon" type="image/svg+xml" href="/favicon.svg">
<style>
.ej-list {{ display:flex; flex-direction:column; gap:0.6rem; margin-top:1rem; }}
.ej-list a {{ display:flex; align-items:baseline; gap:0.7rem; padding:0.8rem 1rem; background:var(--bg); border:1px solid var(--border); border-radius:8px; text-decoration:none; color:var(--text); transition:all 0.15s; }}
.ej-list a:hover {{ border-color:#6366f1; transform:translateX(2px); }}
.ej-list .num {{ display:inline-flex; align-items:center; justify-content:center; min-width:2.4rem; height:1.7rem; padding:0 0.55rem; background:#10b981; color:#fff; border-radius:99px; font-family:var(--mono); font-size:0.78rem; font-weight:600; }}
.ej-list .ttl {{ font-weight:500; }}
.ej-list .arr {{ margin-left:auto; color:var(--text-soft); font-size:0.85rem; }}
</style>
</head>
<body>
<nav>
  <div class="nav-inner">
    <a href="/" class="nav-brand">alexreyes.es</a>
    <div class="nav-links">
      <a href="/docencia/" class="nav-active">{ui_docencia}</a>
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
</nav>

<main>
  <div class="container" style="padding-top:1.5rem;padding-bottom:5rem;max-width:820px">

    <div class="breadcrumb">
      <a href="/">{ui_home}</a>
      <span class="sep">/</span>
      <a href="/docencia/">{ui_docencia}</a>
      <span class="sep">/</span>
      <a href="{hub_url}">{hub_label}</a>
      <span class="sep">/</span>
      <span class="current">{titulo}</span>
    </div>

    <div class="exam-header" style="padding-top:0;border-bottom:none;margin-bottom:1.2rem">
      <div style="display:flex;gap:0.5rem;flex-wrap:wrap;margin-bottom:0.5rem">
        <span class="section-label">{hub_label}</span>
        <span class="tag tag-orange">{ui_exercicis_classe}</span>
      </div>
      <h1 style="margin:0">{titulo}</h1>
      <p style="color:var(--text-soft);margin:0.4rem 0 0;font-size:0.95rem">{n_ejercicios} {ui_exercise_plural}.</p>
    </div>

    <div class="ej-list">
      {ej_links}
    </div>

  </div>
</main>

<footer>
  <div class="container">
    <div class="footer-inner">
      <span><strong>Àlex Reyes</strong> &middot; Matemáticas, docencia y doctorado</span>
      <span>Barcelona &middot; &copy; 2026 Àlex Reyes &middot; <a href="/assets/NOTICES.txt" style="color:inherit">Licencias</a></span>
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


def build_for_collection(json_path: Path) -> int:
    data = json.loads(json_path.read_text(encoding="utf-8"))
    if data.get("tipo_coleccion") != "practica":
        return 0
    ejercicios = data.get("ejercicios", [])
    if not ejercicios:
        return 0
    materia = data.get("tags_coleccion", {}).get("materia") or ""
    lang = LANG.get(materia, "ca")
    ui = UI[lang]
    hub_url, hub_label = MATERIA_HUB.get(materia, ("/docencia/", ""))
    coleccion_id = data["id"]
    coleccion_titulo = data.get("titulo", coleccion_id)

    # Per cada ejercicio, comprovem source_apunt + url_enunciado
    n_built = 0
    ej_links_html = []
    for ej in ejercicios:
        source = ej.get("source_apunt")
        url = ej.get("url_enunciado") or ""
        numero = ej.get("numero")
        ej_id = ej.get("id")
        titulo = ej.get("titulo", "")
        if not source:
            print(f"  ⏭  {ej_id}: sense source_apunt, no es genera pàgina")
            continue
        if not url.startswith("/aula/"):
            print(f"  ⚠ {ej_id}: url_enunciado no apunta a /aula/, salto")
            continue
        # Resol l'apunt origen
        if "#" not in source:
            print(f"  ⚠ {ej_id}: source_apunt sense ancora")
            continue
        apunt_url, anchor = source.split("#", 1)
        apunt_path = REPO / apunt_url.lstrip("/")
        out_path = REPO / url.lstrip("/")

        ext = extract_exercise_block(apunt_path, anchor)
        if ext is None:
            continue
        statement_html, solution_html = ext
        if not statement_html:
            print(f"  ⚠ {ej_id}: enunciat buit a {apunt_url}#{anchor}")
            continue

        # Render
        out_path.parent.mkdir(parents=True, exist_ok=True)
        page = PAGE_TPL.format(
            lang=lang,
            ui_exercise=ui["exercise"],
            ui_solution_h=ui["solution_h"],
            ui_show_solution=ui["show_solution"],
            ui_hide_solution=ui["hide_solution"],
            ui_back_to_apunt=ui["back_to_apunt"],
            ui_home=ui["home"],
            ui_docencia=ui["docencia"],
            ui_exercicis_classe=ui["exercicis_classe"],
            numero=numero,
            titulo=titulo,
            descripcion=f"{ui['exercise']} {numero}: {titulo}. {coleccion_titulo}.",
            hub_url=hub_url,
            hub_label=hub_label,
            coleccion_url="/" + str(out_path.parent.relative_to(REPO)).replace("\\", "/") + "/",
            coleccion_titulo=coleccion_titulo,
            statement_html=statement_html,
            solution_html=solution_html,
            source_apunt=source,
            url_enunciado=url,
        )
        out_path.write_text(page, encoding="utf-8")
        n_built += 1
        ej_links_html.append(
            f'    <a href="/{out_path.relative_to(REPO)}"><span class="num">{numero}</span><span class="ttl">{titulo}</span><span class="arr">→</span></a>'
        )

    # Index de la col·lecció (a la mateixa carpeta de les pàgines pN)
    if ej_links_html:
        # Trobem la carpeta comuna
        any_url = next((e["url_enunciado"] for e in ejercicios if e.get("url_enunciado")), None)
        if any_url:
            col_dir = REPO / Path(any_url.lstrip("/")).parent
            col_dir.mkdir(parents=True, exist_ok=True)
            ex_word = ui["exercise"].lower() + ("s" if lang == "ca" else "s")
            (col_dir / "index.html").write_text(
                COLLECTION_INDEX_TPL.format(
                    lang=lang,
                    ui_home=ui["home"],
                    ui_docencia=ui["docencia"],
                    ui_exercicis_classe=ui["exercicis_classe"],
                    ui_exercise_plural=ex_word,
                    titulo=coleccion_titulo,
                    hub_url=hub_url,
                    hub_label=hub_label,
                    n_ejercicios=len(ej_links_html),
                    ej_links="\n".join(ej_links_html),
                ),
                encoding="utf-8",
            )
            print(f"  ✓ Index de col·lecció: {col_dir.relative_to(REPO)}/index.html")
    return n_built


def main():
    total = 0
    for jp in sorted(EJ_DIR.glob("*.json")):
        if jp.name.startswith("_"):
            continue
        try:
            data = json.loads(jp.read_text(encoding="utf-8"))
        except Exception:
            continue
        if data.get("tipo_coleccion") != "practica":
            continue
        if data.get("schema_version") != 3:
            continue
        print(f"\n→ {jp.name}")
        n = build_for_collection(jp)
        total += n
        print(f"  ✓ {n} pàgines individuals generades")
    print(f"\n— Total: {total} pàgines —")


if __name__ == "__main__":
    main()
