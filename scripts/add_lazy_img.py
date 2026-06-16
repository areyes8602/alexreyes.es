#!/usr/bin/env python3
"""add_lazy_img.py — Añade loading="lazy" a las imágenes de contenido.

Recorre todas las páginas HTML y añade `loading="lazy"` a cada `<img>` que no lo
tenga, EXCEPTO:
  - el hero (`fetchpriority="high"`) — es el LCP, debe cargar eager;
  - la foto de cabecera del CV (`class="cv-header-photo"`) — está above-the-fold.

Idempotente: no duplica el atributo. Pensado para figuras de exámenes/apuntes
(`fig-pN.png`, diagramas) que se insertan a mano y suelen ir below-the-fold.

Uso:
    python3 scripts/add_lazy_img.py            # dry-run
    python3 scripts/add_lazy_img.py --apply     # aplica
"""
import re
import sys
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
APPLY = "--apply" in sys.argv
SKIP = ('fetchpriority="high"', 'class="hero-img"', "cv-header-photo")


def fix_img(tag):
    if "loading=" in tag or any(s in tag for s in SKIP):
        return tag
    return tag.replace("<img", '<img loading="lazy"', 1)


def main():
    changed = 0
    for f in sorted(ROOT.rglob("*.html")):
        if ".git/" in str(f.relative_to(ROOT)):
            continue
        s = f.read_text(encoding="utf-8")
        out = re.sub(r"<img[^>]*>", lambda m: fix_img(m.group(0)), s)
        if out != s:
            changed += 1
            if APPLY:
                f.write_text(out, encoding="utf-8")
    print(("APLICADO" if APPLY else "DRY-RUN") + f": {changed} archivos")


if __name__ == "__main__":
    main()
