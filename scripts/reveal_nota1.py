#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Revelado programado de la Nota 1 «El hombre y la nota al margen».

La nota se sube OCULTA (noindex, fuera de sitemap/home/índice) y este script la
hace pública. Es idempotente y está protegido por fecha: no hace nada antes del
22 de junio de 2026, y tampoco si ya se reveló. Pensado para ejecutarse a diario
desde .github/workflows/reveal-nota1.yml; cuando llega la fecha, edita los
ficheros, regenera el sitemap y deja los cambios listos para commit+push.
"""
import os, sys, subprocess, datetime as dt

SLUG = "el-hombre-y-la-nota-al-margen"
REVEAL_DATE = dt.date(2026, 6, 22)
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

NOINDEX = '<meta name="robots" content="noindex, nofollow">\n'

# Configuración por idioma (prefijo de ruta de fichero, prefijo de URL y textos).
LANGS = {
    "es": {
        "pfx": "",      "url": "/notas/",
        "date": "jun 2026", "newsdate": "22 jun 2026",
        "title": "El hombre y la nota al margen",
        "desc": "El origen de la conjetura de Collatz y el hombre que la anotó: Lothar Collatz, un gigante del análisis numérico, no un cazador de acertijos. Con línea de tiempo y órbitas interactivas.",
        "tags": ("Collatz", "Historia", "Interactivo"),
        "datatags": "collatz historia interactivo",
        "news": 'Nueva nota divulgativa: <strong>«El hombre y la nota al margen»</strong>, el origen de la conjetura de Collatz y el hombre que la anotó, con línea de tiempo y órbitas interactivas.',
        "fib": "fibonacci-collatz",
    },
    "ca": {
        "pfx": "ca/",   "url": "/ca/notas/",
        "date": "jun 2026", "newsdate": "22 jun 2026",
        "title": "L’home i la nota al marge",
        "desc": "L’origen de la conjectura de Collatz i l’home que la va anotar: Lothar Collatz, un gegant de l’anàlisi numèrica, no pas un caçador d’endevinalles. Amb línia de temps i òrbites interactives.",
        "tags": ("Collatz", "Història", "Interactiu"),
        "datatags": "collatz historia interactivo",
        "news": 'Nova nota divulgativa: <strong>«L’home i la nota al marge»</strong>, l’origen de la conjectura de Collatz i l’home que la va anotar, amb línia de temps i òrbites interactives.',
        "fib": "fibonacci-collatz",
    },
    "en": {
        "pfx": "en/",   "url": "/en/notas/",
        "date": "Jun 2026", "newsdate": "22 Jun 2026",
        "title": "The man and the marginal note",
        "desc": "The origin of the Collatz conjecture and the man who jotted it down: Lothar Collatz, a giant of numerical analysis rather than a puzzle hunter. With an interactive timeline and orbits.",
        "tags": ("Collatz", "History", "Interactive"),
        "datatags": "collatz historia interactivo",
        "news": 'New general-audience note: <strong>“The man and the marginal note”</strong>, the origin of the Collatz conjecture and the man who jotted it down, with an interactive timeline and orbits.',
        "fib": "fibonacci-collatz",
    },
}


def read(path):
    with open(os.path.join(REPO, path), encoding="utf-8") as f:
        return f.read()


def write(path, s):
    with open(os.path.join(REPO, path), "w", encoding="utf-8") as f:
        f.write(s)


def card_html(c):
    t1, t2, t3 = c["tags"]
    return (
        f'    <div class="flt-item" data-tag="{c["datatags"]}">\n'
        f'      <a href="{c["url"]}{SLUG}/" class="note-item" style="text-decoration:none;display:flex;gap:1.2rem;padding:1.2rem 0;border-bottom:1px solid var(--border)">\n'
        f'        <div class="note-date" style="min-width:5rem;padding-top:.15rem">{c["date"]}</div>\n'
        f'        <div>\n'
        f'          <div class="note-title" style="font-weight:500;margin-bottom:.3rem">{c["title"]}</div>\n'
        f'          <div class="note-desc" style="font-size:.9rem;color:var(--text-soft)">{c["desc"]}</div>\n'
        f'          <div style="margin-top:.5rem;display:flex;gap:.4rem;flex-wrap:wrap">\n'
        f'            <span class="tag tag-purple" style="font-size:.75rem">{t1}</span>\n'
        f'            <span class="tag tag-gray" style="font-size:.75rem">{t2}</span>\n'
        f'            <span class="tag tag-gray" style="font-size:.75rem">{t3}</span>\n'
        f'          </div>\n'
        f'        </div>\n'
        f'      </a>\n'
        f'    </div>\n'
    )


def news_html(c):
    return (
        f'            <li>\n'
        f'              <span class="news-date">{c["newsdate"]}</span>\n'
        f'              <a href="{c["url"]}{SLUG}/" class="news-text">{c["news"]}</a>\n'
        f'            </li>\n'
    )


def reveal_lang(code, c):
    note = f'{c["pfx"]}notas/{SLUG}/index.html'
    idx  = f'{c["pfx"]}notas/index.html'
    home = f'{c["pfx"]}index.html'

    # 1) quitar noindex de la nota
    s = read(note)
    if NOINDEX in s:
        write(note, s.replace(NOINDEX, "", 1))

    # 2) tarjeta en el índice de notas (antes de la de Fibonacci = más reciente arriba)
    s = read(idx)
    if f"{c['url']}{SLUG}/" not in s:
        anchor = f'    <div class="flt-item" data-tag="collatz fibonacci interactivo">'
        if anchor not in s:
            raise SystemExit(f"[{code}] ancla del índice de notas no encontrada en {idx}")
        s = s.replace(anchor, card_html(c) + anchor, 1)
        write(idx, s)

    # 3) noticia en la home: primer <li> de la tarjeta de notas + sube el contador.
    #    La tarjeta abre con `<ul class="news-card-list"><li>` (primer item pegado al
    #    <ul>), así que insertamos justo tras el <ul> en lugar de "antes del <li>".
    s = read(home)
    if f"{c['url']}{SLUG}/" not in s:
        marker = f'{c["url"]}{c["fib"]}/" class="news-text"'
        p = s.find(marker)
        if p < 0:
            raise SystemExit(f"[{code}] noticia de Fibonacci no encontrada en {home}")
        ul = '<ul class="news-card-list">'
        ul_pos = s.rfind(ul, 0, p)
        if ul_pos < 0:
            raise SystemExit(f"[{code}] <ul> de la tarjeta de notas no encontrado en {home}")
        insert_at = ul_pos + len(ul)
        s = s[:insert_at] + news_html(c).strip() + s[insert_at:]
        # sube el contador de la tarjeta (badge inmediatamente anterior al <ul>)
        cnt = '<span class="news-card-count">'
        cp = s.rfind(cnt, 0, ul_pos)
        if cp >= 0:
            j = cp + len(cnt)
            k = j
            while k < len(s) and s[k].isdigit():
                k += 1
            if k > j:
                s = s[:j] + str(int(s[j:k]) + 1) + s[k:]
        write(home, s)


def update_sitemap():
    path = "scripts/build_sitemap.py"
    s = read(path)
    line = f"    '/notas/{SLUG}/',\n"
    if f"/notas/{SLUG}/" not in s:
        anchor = "    '/notas/anillo-de-collatz/', '/notas/fibonacci-collatz/',\n"
        if anchor not in s:
            raise SystemExit("ancla de trilingual_paths no encontrada en build_sitemap.py")
        s = s.replace(anchor, anchor + line, 1)
        write(path, s)
    subprocess.run([sys.executable, "scripts/build_sitemap.py"], cwd=REPO, check=True)


def main():
    today = dt.date.today()
    if today < REVEAL_DATE:
        print(f"Aún no toca (hoy {today} < {REVEAL_DATE}). Sin cambios.")
        return
    # idempotencia: si la nota ES ya no lleva noindex, asumimos revelada
    if NOINDEX not in read(f"notas/{SLUG}/index.html"):
        print("La Nota 1 ya estaba revelada. Sin cambios.")
        return
    for code, c in LANGS.items():
        reveal_lang(code, c)
    update_sitemap()
    print("Nota 1 revelada (ES/CA/EN): noindex quitado, índice + home + sitemap actualizados.")


if __name__ == "__main__":
    main()
