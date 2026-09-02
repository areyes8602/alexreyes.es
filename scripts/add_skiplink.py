#!/usr/bin/env python3
"""add_skiplink.py — Cablea el "skip-link" de accesibilidad en todas las páginas.

Inserta `<a class="skip-link" href="#main">…</a>` justo tras `<body>` y añade
`id="main"` al `<main>` de cada página HTML. El texto se localiza según el
`<html lang>` de la página (es/ca/en). El CSS de `.skip-link` ya vive en
style.css (oculto hasta recibir foco con Tab).

Idempotente y auto-corrector:
  - No duplica el enlace si ya existe.
  - No duplica `id=` si el `<main>` ya tiene uno.
  - Si el texto del skip-link no coincide con el idioma de la página, lo corrige
    (útil para páginas creadas desde plantilla con texto por defecto).

Uso:
    python3 scripts/add_skiplink.py            # dry-run (no escribe)
    python3 scripts/add_skiplink.py --apply     # aplica los cambios

Cuándo: como PASO FINAL tras crear páginas nuevas (apuntes, ejercicios,
exámenes, notas). Junto a add_og_tags.py / add_jsonld.py / add_hreflang.py.
"""
import re
import sys
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
APPLY = "--apply" in sys.argv

TEXT = {
    "es": "Saltar al contenido",
    "ca": "Salta al contingut",
    "en": "Skip to content",
}
SKIP_RE = re.compile(r'<a class="skip-link" href="#main">([^<]*)</a>')


def process(s):
    """Devuelve el HTML con el skip-link cableado y localizado."""
    if "<body" not in s or "<main" not in s:
        return s
    m = re.search(r'<html[^>]*\blang="([^"]+)"', s)
    lang = m.group(1) if m else "es"
    txt = TEXT.get(lang, TEXT["es"])

    existing = SKIP_RE.search(s)
    if existing:
        # Auto-corrige el texto si no casa con el idioma.
        if existing.group(1) != txt:
            s = SKIP_RE.sub(
                f'<a class="skip-link" href="#main">{txt}</a>', s, count=1
            )
    else:
        s = re.sub(
            r"(<body[^>]*>)",
            r'\1\n<a class="skip-link" href="#main">' + txt + "</a>",
            s,
            count=1,
        )
    # id="main" en el primer <main> que no tenga id.
    s = re.sub(r"<main(?![^>]*\bid=)([^>]*)>", r'<main id="main"\1>', s, count=1)
    return s


def main():
    changed = []
    # "panel" y "tutoria" son zonas privadas: llevan su propio chrome y no
    # pasan por los scripts del sitio público.
    SKIP_TOP = {".git", "panel", "tutoria", "templates", "node_modules"}
    for f in sorted(ROOT.rglob("*.html")):
        if f.relative_to(ROOT).parts[0] in SKIP_TOP:
            continue
        s = f.read_text(encoding="utf-8")
        out = process(s)
        if out != s:
            changed.append(str(f.relative_to(ROOT)))
            if APPLY:
                f.write_text(out, encoding="utf-8")
    verb = "APLICADO" if APPLY else "DRY-RUN (usa --apply para escribir)"
    print(f"{verb}: {len(changed)} archivos")
    for p in changed[:10]:
        print(f"  {p}")
    if len(changed) > 10:
        print(f"  … (+{len(changed) - 10})")


if __name__ == "__main__":
    main()
