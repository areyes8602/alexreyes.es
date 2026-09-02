#!/usr/bin/env python3
"""Inyecta el buscador global (assets/js/search.js) en todas las páginas HTML
públicas, justo antes de </body>. Idempotente. Ejecutar tras los build_*."""
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
TAG = '<script defer src="/assets/js/search.js"></script>'
# "panel" es zona privada con gate de servidor: no lleva SEO, ni buscador,
# ni nada que la haga descubrible.
SKIP_DIRS = {"node_modules", ".git", "templates", "editor", "scripts", "assets",
             "panel"}


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
