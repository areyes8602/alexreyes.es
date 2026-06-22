#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Regenera los chips del filtro de /notas/ (ES/CA/EN) a partir de los tags reales.

Cada tarjeta de nota declara sus etiquetas en `data-tag="..."`. Este script escanea
esas etiquetas y reescribe el bloque `<div class="flt-chips">…</div>` de cada idioma
para que los chips del filtro estén siempre sincronizados con las notas publicadas.

Uso: ejecutar tras añadir o revelar una nota.
    python3 scripts/build_notas_filter.py

· Solo se emiten chips para etiquetas REGISTRADAS en TAGS y que estén presentes en
  alguna nota. El orden de los chips es el de TAGS.
· Las etiquetas de SKIP (p. ej. "interactivo": un formato, no un tema) no llevan chip.
· Si una nota usa una etiqueta que no está ni en TAGS ni en SKIP, el script aborta y
  te dice cuál: añádela a TAGS (con su color y traducciones) o a SKIP.
"""
import os, re, sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

FILES = {"es": "notas/index.html", "ca": "ca/notas/index.html", "en": "en/notas/index.html"}

# Registro de etiquetas-tema -> (clase de color, etiquetas por idioma).
# Colores disponibles: c-purple c-amber c-teal c-blue c-green c-pink c-red c-slate
TAGS = [
    ("collatz",   "c-purple", {"es": "Collatz",   "ca": "Collatz",   "en": "Collatz"}),
    ("fibonacci", "c-amber",  {"es": "Fibonacci", "ca": "Fibonacci", "en": "Fibonacci"}),
    ("tolkien",   "c-teal",   {"es": "Tolkien",   "ca": "Tolkien",   "en": "Tolkien"}),
    ("historia",  "c-blue",   {"es": "Historia",  "ca": "Història",  "en": "History"}),
]

# Etiquetas que aparecen en las notas pero que NO son temas filtrables (sin chip).
SKIP = {"interactivo"}

ORDER  = [t for t, _, _ in TAGS]
COLOR  = {t: c for t, c, _ in TAGS}
LABEL  = {t: l for t, _, l in TAGS}
KNOWN  = set(ORDER) | SKIP

BLOCK_RE = re.compile(r'<div class="flt-chips">.*?</div></div>', re.S)
TAG_RE   = re.compile(r'class="flt-item"\s+data-tag="([^"]*)"')


def read(path):
    with open(os.path.join(REPO, path), encoding="utf-8") as f:
        return f.read()


def write(path, s):
    with open(os.path.join(REPO, path), "w", encoding="utf-8") as f:
        f.write(s)


def main():
    errors = []
    for lang, path in FILES.items():
        s = read(path)

        tokens = set()
        for m in TAG_RE.finditer(s):
            tokens.update(m.group(1).split())

        unknown = sorted(tokens - KNOWN)
        if unknown:
            errors.append(f"{path}: etiqueta(s) sin registrar {unknown} "
                          f"(añádela a TAGS con color+traducciones o a SKIP)")
            continue

        present = [t for t in ORDER if t in tokens]
        chips = "".join(
            f'\n          <button class="flt-chip {COLOR[t]}" '
            f'data-facet="tag" data-val="{t}">{LABEL[t][lang]}</button>'
            for t in present
        )
        block = '<div class="flt-chips">' + chips + '\n        </div></div>'

        if not BLOCK_RE.search(s):
            errors.append(f"{path}: bloque .flt-chips no encontrado")
            continue
        s = BLOCK_RE.sub(lambda _m: block, s, count=1)
        write(path, s)
        print(f"✓ {lang}: chips = {present}")

    if errors:
        print("\n⚠ No se pudo completar:")
        for e in errors:
            print("  -", e)
        sys.exit(1)
    print("Filtro de notas sincronizado (ES/CA/EN).")


if __name__ == "__main__":
    main()
