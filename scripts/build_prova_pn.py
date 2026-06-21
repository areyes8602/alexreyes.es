#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Genera las páginas pN.html de las pruebas Prova Cangur (colecciones con bloque
`prova_cangur`). Cada página muestra la imagen oficial de la pregunta, las opciones
A-E y un botón para revelar la respuesta correcta. La solución razonada se marca como
pendiente (flujo "mixto"). Idempotente: regenera todas las páginas en cada ejecución."""
import json
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
EJ = REPO / "assets" / "data" / "ejercicios"
TAGS = json.load(open(REPO / "assets" / "data" / "tags.json", encoding="utf-8"))
CE = TAGS["namespaces"]["concepto_eso"]["valores"]
DIF = {"facil": "Fàcil", "media": "Mitjana", "dificil": "Difícil"}
V = "202606211500"


def esc(s):
    return str(s or "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")


NAV = '''<nav>
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
      <div class="lang-sw">
        <a href="{root}" class="lang-active">ES</a><span class="lang-sep">&middot;</span><a href="/ca{root}">CA</a><span class="lang-sep">&middot;</span><a href="/en{root}">EN</a>
      </div>
      <button class="nav-hamburger" onclick="toggleMenu()" aria-label="Menu"><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><line x1="4" y1="7" x2="20" y2="7"/><line x1="4" y1="12" x2="20" y2="12"/><line x1="4" y1="17" x2="20" y2="17"/></svg></button>
      <button class="theme-btn" onclick="toggleTheme()" aria-label="Toggle theme">
        <svg class="icon-sun" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="5"/><line x1="12" y1="1" x2="12" y2="3"/><line x1="12" y1="21" x2="12" y2="23"/><line x1="4.22" y1="4.22" x2="5.64" y2="5.64"/><line x1="18.36" y1="18.36" x2="19.78" y2="19.78"/><line x1="1" y1="12" x2="3" y2="12"/><line x1="21" y1="12" x2="23" y2="12"/><line x1="4.22" y1="19.78" x2="5.64" y2="18.36"/><line x1="18.36" y1="5.64" x2="19.78" y2="4.22"/></svg>
        <svg class="icon-moon" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/></svg>
      </button>
    </div>
  </div>
</nav>'''


def page(col, ej, idx, n_total):
    base = col["url_index"].rstrip("/")
    num = ej["numero"]
    title = ej.get("titulo") or f"Pregunta {num}"
    pts = ej["puntuacion"]
    sol = ej.get("solucion", "")
    img = ej.get("imagen")
    enun = (ej.get("apartados") or [{}])[0].get("tarea", "")
    tg = ej.get("tags") or {}
    dif = tg.get("dificultad")
    concs = tg.get("concepto_eso") or []
    chips = ""
    if dif in DIF:
        chips += f'<span class="ib-chip dif-{dif}">{DIF[dif]}</span>'
    for c in concs:
        lab = CE.get(c, {}).get("label", {}).get("ca") or CE.get(c, {}).get("label", {}).get("es") or c
        chips += f'<span class="ib-chip">{esc(lab)}</span>'
    prev_l = f'<a href="p{num-1}.html" class="exam-nav-btn">← Anterior</a>' if num > 1 else '<span class="exam-nav-btn is-off">← Anterior</span>'
    next_l = f'<a href="p{num+1}.html" class="exam-nav-btn">Següent →</a>' if num < n_total else '<span class="exam-nav-btn is-off">Següent →</span>'
    opts = "".join(
        f'<div class="pt-opt" data-o="{o}" style="cursor:default">{o}</div>' for o in ["A", "B", "C", "D", "E"]
    )
    enun_html = f'<p style="font-size:0.98rem;line-height:1.7;color:var(--text)">{esc(enun)}</p>' if enun else ""
    return f'''<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{esc(title)} · {esc(col["titulo"])} | Àlex Reyes</title>
<meta name="description" content="Prova Cangur 1r ESO — pregunta {num}: {esc(title)}.">
<meta name="robots" content="index, follow">
<script>(function(){{var s=localStorage.getItem('theme');if(s)document.documentElement.setAttribute('data-theme',s);else document.documentElement.setAttribute('data-theme','light');}})();</script>
<script src="/assets/js/lang-persist.js?v={V}"></script>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap" media="print" onload="this.media='all'"><noscript><link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap"></noscript>
<link rel="stylesheet" href="/style.css?v={V}">
<link rel="stylesheet" href="/assets/css/examenes.css?v={V}">
<link rel="stylesheet" href="/assets/css/prova-test.css?v={V}">
<link rel="icon" type="image/svg+xml" href="/favicon.svg">
<link rel="canonical" href="https://alexreyes.es{base}/p{num}.html">
<link rel="alternate" hreflang="es" href="https://alexreyes.es{base}/p{num}.html">
<link rel="alternate" hreflang="ca" href="https://alexreyes.es/ca{base}/p{num}.html">
<link rel="alternate" hreflang="en" href="https://alexreyes.es/en{base}/p{num}.html">
<link rel="alternate" hreflang="x-default" href="https://alexreyes.es{base}/p{num}.html">
</head>
<body>
<a class="skip-link" href="#main">Saltar al contenido</a>
{NAV.format(root=base + f"/p{num}.html")}
<main id="main">
  <div class="container" style="padding-top:2rem;padding-bottom:5rem;max-width:760px">
    <div class="breadcrumb">
      <a href="/">Inicio</a><span class="sep">/</span><a href="/docencia/cangur/">Cangur</a><span class="sep">/</span><a href="/aula/cangur/prova/">Prova</a><span class="sep">/</span><a href="{base}/">{esc(col["titulo"]).split("·")[-1].strip()}</a><span class="sep">/</span><span class="current">P{num}</span>
    </div>

    <div class="exam-nav" style="display:flex;justify-content:space-between;align-items:center;gap:0.6rem;margin-bottom:1.2rem">
      {prev_l}
      <a href="{base}/" class="exam-nav-btn">Índex · {num}/{n_total}</a>
      {next_l}
    </div>

    <div style="display:flex;align-items:center;gap:0.6rem;flex-wrap:wrap;margin-bottom:0.5rem">
      <span class="section-label">Pregunta {num}</span>
      <span class="pt-q-pts">{pts} punts</span>
    </div>
    <h1 style="font-size:1.5rem;margin:0.2rem 0 0.8rem">{esc(title)}</h1>
    <div class="ib-chips" style="margin-bottom:1rem">{chips}</div>
    {enun_html}

    <img class="pt-q-img" src="{img}" alt="Enunciat de la pregunta {num}" style="margin-top:0.6rem">

    <div class="pt-opts" style="margin:0.4rem 0 1rem">{opts}</div>

    <button class="solution-toggle" onclick="var s=document.getElementById('sol');s.hidden=!s.hidden;this.setAttribute('aria-expanded',!s.hidden);">Mostrar resposta</button>
    <section class="solution" id="sol" hidden style="margin-top:1rem">
      <p style="font-size:1.05rem"><strong>Resposta correcta:</strong> <span class="pt-opt ok sel" style="cursor:default">{sol}</span></p>
      <p class="pt-faint" style="margin-top:0.6rem">La solució raonada pas a pas s'afegirà pròximament. Pots practicar aquesta prova completa al <a href="/aula/cangur/prova/test/?id={col["id"]}">«Ponte a prueba»</a>.</p>
    </section>

    <div class="exam-nav" style="display:flex;justify-content:space-between;align-items:center;gap:0.6rem;margin-top:2rem">
      {prev_l}
      <a href="{base}/" class="exam-nav-btn">Índex</a>
      {next_l}
    </div>
  </div>
</main>
<footer>
  <div class="container">
    <div class="footer-inner">
      <span><strong>Àlex Reyes</strong> &middot; Matemáticas, docencia y doctorado</span>
      <span>Barcelona &middot; &copy; 2026 Àlex Reyes</span>
    </div>
  </div>
</footer>
<script>
function toggleMenu(){{document.querySelector("nav").classList.toggle("open");}}
function toggleTheme(){{var h=document.documentElement,n=h.getAttribute('data-theme')==='dark'?'light':'dark';h.setAttribute('data-theme',n);localStorage.setItem('theme',n);}}
</script>
</body>
</html>
'''


def main():
    n_pages = 0
    for jf in sorted(EJ.glob("*.json")):
        col = json.load(open(jf, encoding="utf-8"))
        if not col.get("prova_cangur"):
            continue
        outdir = REPO / col["url_index"].lstrip("/")
        outdir.mkdir(parents=True, exist_ok=True)
        ejs = col["ejercicios"]
        for idx, ej in enumerate(ejs):
            html = page(col, ej, idx, len(ejs))
            (outdir / f"p{ej['numero']}.html").write_text(html, encoding="utf-8")
            n_pages += 1
        print(f"  ✓ {col['id']}: {len(ejs)} páginas")
    print(f"OK — {n_pages} páginas pN.html")


if __name__ == "__main__":
    main()
