#!/usr/bin/env python3
"""Inyecta el buscador global (assets/js/search.js) en todas las páginas HTML
públicas, justo antes de </body>. Idempotente. Ejecutar tras los build_*."""
from pathlib import Path

from _zones_privades import ZONES_PRIVADES

REPO = Path(__file__).resolve().parent.parent
TAG = '<script defer src="/assets/js/search.js"></script>'
# Las zonas privadas (panel, tutoria, mates-2eso…) tienen gate de servidor:
# no llevan SEO, ni buscador, ni nada que las haga descubribles. La lista
# está en scripts/_zones_privades.py, para no repetirla en seis ficheros.
SKIP_DIRS = {"node_modules", ".git", "templates", "editor", "scripts",
             "assets"} | ZONES_PRIVADES


def main():
    added = had = skipped = 0
    for p in REPO.rglob("*.html"):
        if any(part in SKIP_DIRS for part in p.relative_to(REPO).parts[:-1]):
            continue
        try:
            t = p.read_text(encoding="utf-8")
        except Exception:
            skipped += 1
            continue
        if "assets/js/search.js" in t:
            had += 1
            continue
        if "</body>" not in t:
            skipped += 1
            continue
        t = t.replace("</body>", TAG + "\n</body>", 1)
        try:
            p.write_text(t, encoding="utf-8")
            added += 1
        except Exception:
            skipped += 1
    print(f"Buscador añadido: {added}")
    print(f"Ya lo tenían: {had}")
    print(f"Omitidos (no legibles / sin </body>): {skipped}")


if __name__ == "__main__":
    main()
