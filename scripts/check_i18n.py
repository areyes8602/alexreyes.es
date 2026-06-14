#!/usr/bin/env python3
"""check_i18n.py — Verifica la paridad e integridad del selector de idioma (ES·CA·EN).

Para cada página con <div class="lang-sw"> comprueba:
  C1. Las tres URLs (ES, CA, EN) resuelven a un fichero existente (no 404).
  C2. El idioma marcado como activo (class="lang-active") corresponde al árbol de
      la página: raíz → ES, /ca/ → CA, /en/ → EN.
  C3. Están los tres idiomas (ES, CA, EN), exactamente uno activo.

Pensado para CI: sale con código != 0 si aparece un fallo NUEVO (regresión).

Baseline: los fallos ya conocidos (el hueco i18n histórico de /aula/, solo-ES) se
registran en scripts/i18n-baseline.txt y NO rompen el CI; así el pipeline pasa en
verde y solo falla si introduces un selector roto nuevo. Para regenerar el
baseline tras corregir/ampliar traducciones: `--update-baseline`.

Uso:
    python3 scripts/check_i18n.py [--quiet] [--strict] [--update-baseline]
      --strict           ignora el baseline: falla con CUALQUIER error (auditoría)
      --update-baseline  reescribe i18n-baseline.txt con el estado actual
"""
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SKIP_DIRS = {"node_modules", ".git", "templates", "editor", "scripts", "assets"}
BASELINE = REPO / "scripts" / "i18n-baseline.txt"

SW_BLOCK_RE = re.compile(r'<div class="lang-sw">(.*?)</div>', re.S)
SW_LINK_RE = re.compile(r'<a\s+href="([^"]+)"((?:[^>]*))>\s*(ES|CA|EN)\s*</a>', re.S)


def url_to_file(url):
    """Convierte una URL absoluta del sitio en la ruta de fichero esperada."""
    path = url.split("#")[0].split("?")[0]
    if not path.startswith("/"):
        return None
    rel = path.lstrip("/")
    if rel == "" or rel.endswith("/"):
        rel += "index.html"
    return REPO / rel


def expected_active(rel_path):
    p = rel_path.parts
    if p and p[0] == "ca":
        return "CA"
    if p and p[0] == "en":
        return "EN"
    return "ES"


def load_baseline():
    if not BASELINE.exists():
        return set()
    return {
        ln.strip()
        for ln in BASELINE.read_text(encoding="utf-8").splitlines()
        if ln.strip() and not ln.startswith("#")
    }


def main():
    args = sys.argv[1:]
    quiet = "--quiet" in args
    strict = "--strict" in args
    update = "--update-baseline" in args
    errors = []
    warnings = []
    checked = 0

    for p in REPO.rglob("*.html"):
        parts = p.relative_to(REPO).parts
        if any(d in SKIP_DIRS for d in parts[:-1]):
            continue
        try:
            t = p.read_text(encoding="utf-8")
        except Exception:
            continue
        mb = SW_BLOCK_RE.search(t)
        if not mb:
            continue
        checked += 1
        rel = p.relative_to(REPO)
        links = {}        # label -> href
        active = None
        for href, attrs, label in SW_LINK_RE.findall(mb.group(1)):
            links[label] = href
            if "lang-active" in attrs:
                active = label

        # C3: los tres idiomas, exactamente un activo
        for lang in ("ES", "CA", "EN"):
            if lang not in links:
                errors.append(f"{rel}: falta el enlace {lang} en el selector")
        if active is None:
            errors.append(f"{rel}: ningún idioma marcado como lang-active")

        # C2: el activo corresponde al árbol
        exp = expected_active(rel)
        if active and active != exp:
            errors.append(f"{rel}: activo={active} pero por su ruta debería ser {exp}")

        # C1: cada URL resuelve a un fichero existente
        for lang, href in links.items():
            target = url_to_file(href)
            if target is None:
                errors.append(f"{rel}: URL {lang} no es absoluta: {href}")
            elif not target.exists():
                errors.append(f"{rel}: selector {lang} → {href} NO existe (404)")

    # Regenerar baseline si se pide
    if update:
        header = (
            "# Baseline de paridad i18n — fallos CONOCIDOS y aceptados (hueco /aula/ solo-ES).\n"
            "# El CI los ignora; solo falla ante fallos NUEVOS. Regenerar: check_i18n.py --update-baseline\n"
        )
        BASELINE.write_text(header + "\n".join(sorted(errors)) + "\n", encoding="utf-8")
        print(f"Baseline actualizado: {len(errors)} entradas → {BASELINE.relative_to(REPO)}")
        return 0

    baseline = set() if strict else load_baseline()
    new_errors = [e for e in errors if e not in baseline]
    fixed = baseline - set(errors)

    # Informe
    print(f"Páginas con selector revisadas: {checked}")
    print(f"Errores totales: {len(errors)}  |  conocidos (baseline): {len(errors) - len(new_errors)}  |  nuevos: {len(new_errors)}")
    if fixed and not quiet:
        print(f"\n✓ {len(fixed)} entrada(s) del baseline ya están ARREGLADAS (puedes regenerarlo con --update-baseline).")
    if warnings and not quiet:
        print(f"\nAvisos ({len(warnings)}):")
        for w in warnings:
            print(f"  ⚠ {w}")
    if new_errors:
        print(f"\n✗ Errores NUEVOS ({len(new_errors)}):")
        for e in new_errors:
            print(f"  ✗ {e}")
        print(f"\nFALLO: {len(new_errors)} problema(s) i18n nuevo(s) (regresión).")
        return 1
    if strict and errors:
        print(f"\n✗ [--strict] {len(errors)} error(es) en total.")
        return 1
    print("\n✓ Sin regresiones i18n: ningún selector roto nuevo.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
