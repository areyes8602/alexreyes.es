#!/usr/bin/env python3
"""
add-lang-switcher-root.py
=========================

Inyecta <div class="lang-sw"> en el <div class="nav-right"> de TODAS las
páginas del árbol raíz (excluyendo /ca/, /en/, templates, scripts) que
aún no lo tengan. El switcher muestra:

  ES (active) · CA · EN

con URLs calculadas a partir del path: ES→propia URL, CA→/ca + URL, EN→/en + URL.

Es idempotente: páginas que ya tengan `class="lang-sw"` se saltan.
"""
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

# Match: <div class="nav-right"> + algunos whitespaces + <button class="nav-hamburger"
NAV_RIGHT_PATTERN = re.compile(
    r'(<div class="nav-right">[ \t]*\n?[ \t]*)(<button class="nav-hamburger")',
    re.MULTILINE,
)

SKIP_TOP = {"ca", "en", "templates", "scripts", "node_modules", ".git", "outputs"}


def es_url_for(html_path: Path) -> str:
    rel = html_path.relative_to(REPO_ROOT).as_posix()
    url = "/" + rel
    # Para .../index.html, la URL canónica es la carpeta (con / final)
    if url.endswith("/index.html"):
        url = url[: -len("index.html")]
    return url


def make_switcher(es_url: str) -> str:
    ca_url = "/ca" + es_url
    en_url = "/en" + es_url
    return (
        '<div class="lang-sw">\n'
        f'        <a href="{es_url}" class="lang-active">ES</a><span class="lang-sep">&middot;</span>'
        f'<a href="{ca_url}">CA</a><span class="lang-sep">&middot;</span>'
        f'<a href="{en_url}">EN</a>\n'
        "      </div>\n      "
    )


def main():
    n_modified = 0
    n_skipped_already = 0
    n_skipped_no_navright = 0

    for html in REPO_ROOT.rglob("*.html"):
        rel = html.relative_to(REPO_ROOT)
        if rel.parts[0] in SKIP_TOP:
            continue
        try:
            text = html.read_text(encoding="utf-8")
        except Exception as e:
            print(f"  ⚠ {rel}: error leyendo ({e})", file=sys.stderr)
            continue

        if 'class="lang-sw"' in text:
            n_skipped_already += 1
            continue
        if '<div class="nav-right">' not in text:
            n_skipped_no_navright += 1
            continue

        es_url = es_url_for(html)
        switcher = make_switcher(es_url)
        new_text, count = NAV_RIGHT_PATTERN.subn(rf"\1{switcher}\2", text, count=1)
        if count == 0:
            # Estructura inesperada (nav-right pero el patrón no encaja)
            print(f"  ⚠ {rel}: nav-right encontrado pero patrón no encaja, saltando", file=sys.stderr)
            n_skipped_no_navright += 1
            continue
        html.write_text(new_text, encoding="utf-8")
        n_modified += 1
        if n_modified <= 10:
            print(f"  ✓ {rel}")

    print("")
    print("─── Resumen ───")
    print(f"  ✓ Archivos modificados: {n_modified}")
    print(f"  · Saltados (ya tenían lang-sw): {n_skipped_already}")
    print(f"  · Saltados (sin nav-right o estructura no estándar): {n_skipped_no_navright}")


if __name__ == "__main__":
    main()
