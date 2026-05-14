#!/usr/bin/env python3
"""
add-lang-persist-script.py
==========================

Inyecta <script src="/assets/js/lang-persist.js"></script> en el <head> de TODAS
las páginas HTML del sitio (todos los árboles: raíz, /ca/, /en/) que tengan un
lang switcher (.lang-sw) y aún no tengan el script de persistencia.

Lo coloca justo DESPUÉS del script inline de tema (`localStorage.getItem('theme')`)
para que el redirect se aplique antes de cualquier render visible.

Es idempotente: páginas que ya lo tengan se saltan.
"""
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SKIP_TOP = {"templates", "scripts", "node_modules", ".git", "outputs"}

SCRIPT_TAG = '<script src="/assets/js/lang-persist.js"></script>'

# Insertamos justo después del script inline del theme
THEME_SCRIPT_PATTERN = re.compile(
    r"(<script>\(function\(\)\{var s=localStorage\.getItem\('theme'\)[^<]+</script>)",
    re.MULTILINE,
)


def main():
    n_added = 0
    n_skipped_already = 0
    n_skipped_no_lang_sw = 0

    for html in REPO_ROOT.rglob("*.html"):
        rel = html.relative_to(REPO_ROOT)
        if rel.parts[0] in SKIP_TOP:
            continue
        try:
            text = html.read_text(encoding="utf-8")
        except Exception:
            continue

        # Solo añadimos a páginas con lang-sw (las que tienen el switcher visible)
        if 'class="lang-sw"' not in text:
            n_skipped_no_lang_sw += 1
            continue

        # Si ya tiene el script, saltar
        if 'lang-persist.js' in text:
            n_skipped_already += 1
            continue

        new_text, count = THEME_SCRIPT_PATTERN.subn(
            r"\1\n" + SCRIPT_TAG, text, count=1
        )
        if count == 0:
            # No tiene script de theme inline, intentamos otra inserción: justo antes de </head>
            if "</head>" in new_text:
                new_text = new_text.replace("</head>", SCRIPT_TAG + "\n</head>", 1)
            else:
                continue

        html.write_text(new_text, encoding="utf-8")
        n_added += 1
        if n_added <= 5:
            print(f"  ✓ {rel}")

    print("")
    print("─── Resumen ───")
    print(f"  ✓ Script añadido a: {n_added} archivos")
    print(f"  · Ya lo tenían: {n_skipped_already}")
    print(f"  · Sin lang switcher (saltados): {n_skipped_no_lang_sw}")


if __name__ == "__main__":
    main()
