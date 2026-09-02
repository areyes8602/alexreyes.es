#!/usr/bin/env python3
"""Inyecta etiquetas Open Graph / Twitter Card en cualquier página HTML que no las
tenga, derivándolas del <title>, la meta description y el canonical existentes.

Idempotente: si la página ya tiene `property="og:title"`, no la toca. Pensado para
ejecutarse como paso final del pipeline (después de los build_* que generan HTML).
"""
import re
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
BASE = "https://alexreyes.es"
DEFAULT_IMAGE = f"{BASE}/og-image.jpg"
# "panel" y "tutoria" son zonas privadas con gate de servidor: no llevan
# SEO, ni buscador, ni nada que las haga descubribles.
SKIP_DIRS = {"node_modules", ".git", "templates", "editor", "scripts", "assets",
             "panel", "tutoria"}


def esc_attr(s: str) -> str:
    return (s or "").replace('"', "&quot;").strip()


def url_from_path(p: Path) -> str:
    rel = p.relative_to(REPO).as_posix()
    if rel.endswith("index.html"):
        rel = rel[: -len("index.html")]
    return BASE + "/" + rel.lstrip("/")


def main():
    enriched = skipped_has = skipped_err = 0
    for p in REPO.rglob("*.html"):
        if any(part in SKIP_DIRS for part in p.relative_to(REPO).parts[:-1]):
            continue
        try:
            t = p.read_text(encoding="utf-8")
        except Exception:
            skipped_err += 1
            continue
        if 'property="og:title"' in t:
            skipped_has += 1
            continue
        if "</head>" not in t:
            skipped_err += 1
            continue
        mt = re.search(r"<title>(.*?)</title>", t, re.S)
        title = esc_attr(re.sub(r"\s+", " ", mt.group(1)).strip()) if mt else "alexreyes.es"
        md = re.search(r'<meta\s+name="description"\s+content="([^"]*)"', t)
        desc = esc_attr(md.group(1)) if md else ""
        mc = re.search(r'<link\s+rel="canonical"\s+href="([^"]*)"', t)
        url = mc.group(1) if mc else url_from_path(p)
        block = (
            '<meta property="og:type" content="website">\n'
            f'<meta property="og:url" content="{url}">\n'
            f'<meta property="og:title" content="{title}">\n'
            f'<meta property="og:description" content="{desc}">\n'
            f'<meta property="og:image" content="{DEFAULT_IMAGE}">\n'
            '<meta property="og:site_name" content="alexreyes.es">\n'
            '<meta name="twitter:card" content="summary_large_image">\n'
            f'<meta name="twitter:title" content="{title}">\n'
            f'<meta name="twitter:description" content="{desc}">\n'
            f'<meta name="twitter:image" content="{DEFAULT_IMAGE}">\n'
        )
        t = t.replace("</head>", block + "</head>", 1)
        try:
            p.write_text(t, encoding="utf-8")
            enriched += 1
        except Exception:
            skipped_err += 1
    print(f"OG añadido: {enriched}")
    print(f"Ya tenían OG (sin tocar): {skipped_has}")
    print(f"Omitidos (no legibles / sin </head>): {skipped_err}")


if __name__ == "__main__":
    main()
