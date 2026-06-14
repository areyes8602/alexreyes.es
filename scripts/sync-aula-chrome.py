#!/usr/bin/env python3
"""
sync-aula-chrome.py — Sincroniza nav, footer e IBO disclaimer entre todos los HTML
del repo a partir de los templates canónicos en /templates/_chrome/.

Por qué: cuando cambias el menú de navegación o el footer, modificarlo a mano en
236 archivos es propenso a olvidos. Este script:
  1. Lee los bloques canónicos de /templates/_chrome/{nav.es,nav.ca,footer,ibo-disclaimer}.html
  2. Recorre todos los HTML del repo (excepto /ca/, /en/, .git, node_modules, templates/)
  3. Para cada archivo, detecta <html lang="..."> y aplica el nav matching:
        lang="es" → nav.es.html (label "Docencia")
        lang="ca" → nav.ca.html (label "Docència")
        otros lang → se omite el nav, pero footer/ibo se sincronizan
  4. Sustituye <footer>...</footer> por el footer canónico (siempre español, es el
     patrón consistente en todas las páginas a la raíz)
  5. Sustituye <aside class="ibo-disclaimer">...</aside> por el canónico (sólo si
     ya existe en el archivo: el disclaimer es opcional y específico de páginas IB)
  6. Reporta diff por archivo

Uso:
    python3 scripts/sync-aula-chrome.py [--dry-run] [--only path/to/file.html]

Cuándo correrlo:
  - Después de modificar /templates/_chrome/{nav.es,nav.ca,footer,ibo-disclaimer}.html
  - Antes de commit + push para garantizar consistencia

Flags:
  --dry-run    No escribe, solo reporta qué cambiaría
  --only PATH  Sincroniza solo un archivo (útil para probar)

Reglas:
  - Las páginas en /ca/ y /en/ tienen URLs traducidas y un lang switcher con URLs
    específicas por página, lo cual no se puede unificar con un template estático.
    Para esas, gestión manual o añadir templates multi-idioma en el futuro.
  - El IBO disclaimer SÓLO se sincroniza si el archivo ya tiene un <aside class="ibo-disclaimer">
    existente (no se añade automáticamente, porque solo aplica a páginas IB).
  - El <nav> y el <footer> se sincronizan en TODOS los HTML que ya los tengan.
  - El nav se elige según <html lang="..."> (es o ca). Si el lang es desconocido o
    no se detecta, se omite el nav y se reporta para revisión manual.
"""
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
CHROME_DIR = REPO / "templates" / "_chrome"

LANG_RE = re.compile(r'<html\s+[^>]*lang="([^"]+)"', re.IGNORECASE)


def load_template(name):
    return (CHROME_DIR / name).read_text(encoding='utf-8').rstrip() + "\n"


def detect_lang(text):
    """Devuelve el código de idioma del <html lang="..."> o None si no se encuentra."""
    m = LANG_RE.search(text)
    if not m:
        return None
    return m.group(1).strip().lower().split('-')[0]  # 'es', 'ca', 'en', etc.


# ── nav-active por sección + preservación del selector de idioma ──────────────
# El activo se decide por la SECCIÓN de la página (raíz/aula→Docencia, etc.), no
# por el template. Y el selector de idioma (lang-sw) es PER-PÁGINA: el template
# lleva un marcador <!--LANGSW--> que se sustituye por el lang-sw real de la
# página, para NO borrarlo al sincronizar.
SECTION_HREF = {
    "docencia": "/docencia/",
    "aula": "/docencia/",
    "doctorado": "/doctorado/",
    "notas": "/notas/",
    "cv": "/cv/",
    "contacto": "/contacto/",
}
LANGSW_RE = re.compile(r'<div class="lang-sw">.*?</div>', re.S)


def active_href_for(rel_path):
    parts = rel_path.parts
    if parts and parts[0] in ("ca", "en"):  # ignorar prefijo de idioma
        parts = parts[1:]
    if len(parts) <= 1:  # raíz: index.html, 404.html
        return None
    return SECTION_HREF.get(parts[0])


def build_nav(template, rel_path, page_text):
    """Devuelve el nav del template con (1) el nav-active correcto por sección y
    (2) el selector de idioma real de la página inyectado en <!--LANGSW-->."""
    nav = template.replace(' class="nav-active"', '')
    ah = active_href_for(rel_path)
    if ah:
        nav = nav.replace(f'<a href="{ah}">', f'<a href="{ah}" class="nav-active">', 1)
    m = LANGSW_RE.search(page_text)
    if m:
        nav = nav.replace('<!--LANGSW-->', m.group(0))
    else:
        # sin selector en la página: quitar la línea del marcador
        nav = re.sub(r'[ \t]*<!--LANGSW-->\n', '', nav)
    return nav


def replace_block(text, start_re, end_marker, new_content):
    """
    Reemplaza el primer bloque que va de `start_re` (regex que matchea la apertura,
    ej. r'<nav>') hasta `end_marker` (string literal de cierre, ej. '</nav>')
    por `new_content` (que ya incluye apertura y cierre).
    Si no encuentra el bloque, devuelve el texto sin cambios + flag False.
    """
    m = re.search(start_re, text)
    if not m:
        return text, False
    start = m.start()
    end_idx = text.find(end_marker, m.end())
    if end_idx < 0:
        return text, False
    end = end_idx + len(end_marker)
    new_block = new_content.rstrip()
    # Conservar la indentación inicial original del bloque (si estaba a nivel 0, se queda igual)
    return text[:start] + new_block + text[end:], True


def sync_file(html_path, navs_by_lang, footer_html, ibo_html, dry_run=False):
    """
    navs_by_lang: dict {'es': nav_es_html, 'ca': nav_ca_html}
    Devuelve (changes_list, lang_detected_or_warning).
    """
    text = html_path.read_text(encoding='utf-8')
    original = text
    changes = []
    warnings = []

    lang = detect_lang(text)

    # Sincronizar <nav>...</nav> sólo si conocemos el idioma.
    # Se preserva el selector de idioma de la página y se fija el nav-active
    # según su sección (ver build_nav).
    if lang in navs_by_lang:
        nav_for_page = build_nav(navs_by_lang[lang], html_path.relative_to(REPO), text)
        text2, changed = replace_block(text, r'<nav>\s*\n', '</nav>', nav_for_page)
        if changed and text2 != text:
            text = text2
            changes.append(f'nav[{lang}]')
    elif lang is None:
        warnings.append('lang-no-detectado')
    else:
        warnings.append(f'lang-desconocido:{lang}')

    # Sincronizar <footer>...</footer> (siempre el español canónico)
    text2, changed = replace_block(text, r'<footer>\s*\n', '</footer>', footer_html)
    if changed and text2 != text:
        text = text2
        changes.append('footer')

    # Sincronizar IBO disclaimer (solo si ya existe en el archivo)
    if 'ibo-disclaimer' in text:
        text2, changed = replace_block(
            text,
            r'<aside class="ibo-disclaimer">\s*\n',
            '</aside>',
            ibo_html,
        )
        if changed and text2 != text:
            text = text2
            changes.append('ibo')

    if text != original:
        if not dry_run:
            html_path.write_text(text, encoding='utf-8')
        return changes, warnings
    return [], warnings


def main():
    args = sys.argv[1:]
    dry_run = '--dry-run' in args
    only = None
    if '--only' in args:
        only_idx = args.index('--only')
        if only_idx + 1 < len(args):
            only = args[only_idx + 1]

    navs_by_lang = {
        'es': load_template('nav.es.html'),
        'ca': load_template('nav.ca.html'),
    }
    footer_html = load_template('footer.html')
    ibo_html = load_template('ibo-disclaimer.html')

    if only:
        files = [REPO / only]
    else:
        files = list(REPO.rglob('*.html'))
        # Filtrar archivos en .git, node_modules, templates/
        files = [f for f in files if not any(p.startswith('.') or p in ('node_modules', 'templates') for p in f.relative_to(REPO).parts)]
        # Excluir /ca/ y /en/: tienen URLs traducidas + lang switcher con URLs por página,
        # no se pueden unificar con un template estático. Gestión manual hasta que añadamos
        # templates multi-idioma reales.
        files = [f for f in files
                 if f.relative_to(REPO).parts[0] not in ('ca', 'en')]

    changed_total = 0
    nav_es_count = nav_ca_count = footer_count = ibo_count = 0
    warning_files = []
    for f in files:
        if not f.exists(): continue
        try:
            changes, warnings = sync_file(f, navs_by_lang, footer_html, ibo_html, dry_run=dry_run)
        except Exception as e:
            print(f'  ✗ ERROR en {f.relative_to(REPO)}: {e}')
            continue
        if warnings:
            warning_files.append((f.relative_to(REPO), warnings))
        if changes:
            changed_total += 1
            nav_es_count += 'nav[es]' in changes
            nav_ca_count += 'nav[ca]' in changes
            footer_count += 'footer' in changes
            ibo_count += 'ibo' in changes
            print(f'  ✓ {f.relative_to(REPO)}: {", ".join(changes)}')

    prefix = '[DRY-RUN] ' if dry_run else ''
    print(f'\n─── Resumen ───')
    print(f'  {prefix}Archivos modificados: {changed_total}')
    print(f'  {prefix}Reemplazos: nav[es]={nav_es_count}, nav[ca]={nav_ca_count}, footer={footer_count}, ibo={ibo_count}')
    if warning_files:
        print(f'\n  ⚠ {len(warning_files)} archivos con warnings (lang no detectado o desconocido):')
        for rel, ws in warning_files[:10]:
            print(f'     - {rel}: {", ".join(ws)}')
        if len(warning_files) > 10:
            print(f'     ... y {len(warning_files) - 10} más')
    if dry_run:
        print(f'\n  Para aplicar los cambios, vuelve a correr sin --dry-run.')


if __name__ == '__main__':
    main()
