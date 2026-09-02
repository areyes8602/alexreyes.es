#!/usr/bin/env python3
"""add_hreflang.py — Inyecta/actualiza canonical + hreflang en todas las páginas.

Para cada página deriva sus URLs ES/CA/EN del esquema de rutas (raíz=ES, /ca/, /en/)
y emite:
  - <link rel="canonical">  (su propia URL), si falta.
  - <link rel="alternate" hreflang="..">  SOLO para los idiomas cuyo fichero EXISTE
    en disco (+ x-default → ES). Así las páginas que aún no están traducidas no
    apuntan a CA/EN inexistentes (evita errores de hreflang en Google).

Re-ejecutable: regenera el bloque hreflang cada vez (borra el anterior y lo rehace),
así que a medida que se añaden traducciones, volver a correrlo actualiza todo.
Pensado como paso final del pipeline, junto a add_og_tags.py / add_jsonld.py.

Uso:
    python3 scripts/add_hreflang.py [--dry-run]
"""
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
BASE = "https://alexreyes.es"
# "panel" es zona privada con gate de servidor: no lleva SEO, ni buscador,
# ni nada que la haga descubrible.
SKIP_DIRS = {"node_modules", ".git", "templates", "editor", "scripts", "assets",
             "panel"}

HREFLANG_LINE_RE = re.compile(r'[ \t]*<link\s+rel="alternate"\s+hreflang="[^"]*"[^>]*>\n?')
CANON_RE = re.compile(r'<link\s+rel="canonical"\s+href="[^"]*"\s*/?>')


def es_path_of(rel_posix):
    """Ruta 'ES' (sin prefijo de idioma) a partir de la ruta del fichero."""
    if rel_posix.startswith("ca/"):
        return rel_posix[3:]
    if rel_posix.startswith("en/"):
        return rel_posix[3:]
    return rel_posix


def url_for(es_path, lang):
    """URL pública para un es_path en el idioma dado."""
    if lang == "es":
        prefix = ""
    else:
        prefix = lang + "/"
    p = prefix + es_path
    if p.endswith("index.html"):
        p = p[: -len("index.html")]
    return BASE + "/" + p.lstrip("/")


def file_for(es_path, lang):
    if lang == "es":
        return REPO / es_path
    return REPO / lang / es_path


def main():
    dry = "--dry-run" in sys.argv[1:]
    changed = skipped = 0
    added_canon = 0

    for p in REPO.rglob("*.html"):
        rel = p.relative_to(REPO)
        if any(d in SKIP_DIRS for d in rel.parts[:-1]):
            continue
        try:
            t = p.read_text(encoding="utf-8")
        except Exception:
            continue
        if "</head>" not in t:
            continue

        rel_posix = rel.as_posix()
        es_path = es_path_of(rel_posix)
        # idiomas cuyo fichero existe
        existing = [lang for lang in ("es", "ca", "en") if file_for(es_path, lang).exists()]

        own_lang = "ca" if rel_posix.startswith("ca/") else "en" if rel_posix.startswith("en/") else "es"
        own_url = url_for(es_path, own_lang)

        # construir bloque
        lines = []
        # canonical (solo si no hay ya uno)
        has_canon = CANON_RE.search(t) is not None
        if not has_canon:
            lines.append(f'<link rel="canonical" href="{own_url}">')
            added_canon += 1
        # hreflang solo si hay 2+ versiones reales
        if len(existing) >= 2:
            for lang in existing:
                lines.append(f'<link rel="alternate" hreflang="{lang}" href="{url_for(es_path, lang)}">')
            if "es" in existing:
                lines.append(f'<link rel="alternate" hreflang="x-default" href="{url_for(es_path, "es")}">')

        # quitar hreflang antiguos (regenerar)
        new_t = HREFLANG_LINE_RE.sub("", t)

        if not lines:
            # nada que añadir (página monolingüe sin hreflang previo)
            if new_t != t:
                # había hreflang colgando (p.ej. apuntaba a versiones borradas) → limpiar
                if not dry:
                    p.write_text(new_t, encoding="utf-8")
                changed += 1
            else:
                skipped += 1
            continue

        block = "\n".join(lines) + "\n"
        # insertar tras canonical si existe, si no antes de </head>
        if has_canon:
            new_t = CANON_RE.sub(lambda m: m.group(0) + "\n" + block.rstrip("\n"), new_t, count=1)
        else:
            new_t = new_t.replace("</head>", block + "</head>", 1)

        if new_t != t:
            if not dry:
                p.write_text(new_t, encoding="utf-8")
            changed += 1
        else:
            skipped += 1

    pfx = "[DRY-RUN] " if dry else ""
    print(f"{pfx}Páginas actualizadas (canonical/hreflang): {changed}")
    print(f"  canonical añadidos: {added_canon}")
    print(f"  sin cambios: {skipped}")


if __name__ == "__main__":
    main()
