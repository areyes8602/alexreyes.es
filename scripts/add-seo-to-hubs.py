#!/usr/bin/env python3
"""
add-seo-to-hubs.py — Añade los bloques SEO faltantes a las páginas de hub.

Procesa las 3 versiones de cada hub: español (raíz), catalán (/ca/) e inglés (/en/).
Cada versión recibe:
  - <link rel="canonical"> apuntando a SU URL
  - <link rel="alternate" hreflang="..."> a las 3 versiones (es, ca, en, x-default)
  - <meta property="og:..."> con og:locale del idioma de la página y los otros
    como og:locale:alternate
  - <meta name="twitter:..."> con título y descripción de la página

Detecta qué partes faltan y añade solo esas. Idempotente.

El title y description se leen del propio archivo para mantener coherencia
lingüística (cada versión ya tiene su título y descripción traducidos).

Uso:
    python3 scripts/add-seo-to-hubs.py [--dry-run]

Solo aplica a hubs específicos (lista HUBS abajo). NO toca exámenes individuales,
apuntes individuales ni fichas — esas tienen su propio ciclo de creación.
"""
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
BASE = 'https://alexreyes.es'

# Hubs a procesar. Cada uno se procesará en raíz, /ca/ y /en/.
HUBS = [
    'docencia/ib-ai/2024-2026',
    'docencia/ib-ai/2025-2027',
    'docencia/ccss-1btl',
    'docencia/2eso',
    'docencia/cangur',
    'docencia/mi-examen',
    'contacto',
]

# Mapeo idioma → og:locale
LOCALES = {'es': 'es_ES', 'ca': 'ca_ES', 'en': 'en_US'}


def lang_url(lang, path):
    """URL canónica para una variante de idioma."""
    if lang == 'es':
        return f'{BASE}/{path}/'
    return f'{BASE}/{lang}/{path}/'


def extract_title_desc(text):
    title_m = re.search(r'<title>([^<]+)</title>', text)
    desc_m = re.search(r'<meta\s+name="description"\s+content="([^"]+)"', text)
    title = title_m.group(1).strip() if title_m else ''
    desc = desc_m.group(1).strip() if desc_m else ''
    return title, desc


def build_canonical_block(lang, path):
    own = lang_url(lang, path)
    es = lang_url('es', path)
    ca = lang_url('ca', path)
    en = lang_url('en', path)
    return (
        f'<link rel="canonical" href="{own}">\n'
        f'<link rel="alternate" hreflang="es" href="{es}">\n'
        f'<link rel="alternate" hreflang="ca" href="{ca}">\n'
        f'<link rel="alternate" hreflang="en" href="{en}">\n'
        f'<link rel="alternate" hreflang="x-default" href="{es}">'
    )


def build_og_twitter_block(lang, path, title, desc):
    own = lang_url(lang, path)
    img = f'{BASE}/og-image.jpg'
    primary_locale = LOCALES[lang]
    alt_locales = [LOCALES[l] for l in ('es', 'ca', 'en') if l != lang]
    locale_alts = '\n'.join(
        f'<meta property="og:locale:alternate" content="{l}">' for l in alt_locales
    )
    return (
        f'<meta property="og:type" content="website">\n'
        f'<meta property="og:url" content="{own}">\n'
        f'<meta property="og:title" content="{title}">\n'
        f'<meta property="og:description" content="{desc}">\n'
        f'<meta property="og:image" content="{img}">\n'
        f'<meta property="og:image:width" content="1200">\n'
        f'<meta property="og:image:height" content="630">\n'
        f'<meta property="og:locale" content="{primary_locale}">\n'
        f'{locale_alts}\n'
        f'<meta property="og:site_name" content="alexreyes.es">\n'
        f'<meta name="twitter:card" content="summary_large_image">\n'
        f'<meta name="twitter:title" content="{title}">\n'
        f'<meta name="twitter:description" content="{desc}">\n'
        f'<meta name="twitter:image" content="{img}">'
    )


def insert_after(text, anchor_re, content):
    """Inserta `content` después del primer match de anchor_re. Devuelve nuevo texto."""
    m = re.search(anchor_re, text)
    if not m:
        return None
    insert_at = m.end()
    return text[:insert_at] + '\n' + content + text[insert_at:]


def read_with_retry(html_path, attempts=5, delay=1):
    """Lee el archivo con reintentos para sobrellevar Resource deadlock del FUSE."""
    import time
    last_err = None
    for i in range(attempts):
        try:
            return html_path.read_text(encoding='utf-8')
        except OSError as e:
            last_err = e
            time.sleep(delay * (i + 1))
    raise last_err


def process_file(html_path, lang, path, dry_run=False):
    text = read_with_retry(html_path)
    original = text
    actions = []

    title, desc = extract_title_desc(text)
    if not title:
        return 'error', 'no <title> encontrado'
    if not desc:
        desc = f'{title} en alexreyes.es'

    has_canonical = 'rel="canonical"' in text
    has_og = 'og:title' in text

    if not has_canonical:
        block = build_canonical_block(lang, path)
        new_text = insert_after(text, r'<link\s+rel="icon"[^>]*>', block)
        if new_text is None:
            return 'error', 'no <link rel="icon"> encontrado'
        text = new_text
        actions.append('canonical+hreflang')

    if not has_og:
        block = build_og_twitter_block(lang, path, title, desc)
        m = list(re.finditer(r'<link\s+rel="alternate"[^>]*>', text))
        if m:
            insert_at = m[-1].end()
            text = text[:insert_at] + '\n' + block + text[insert_at:]
        else:
            new_text = insert_after(text, r'<link\s+rel="icon"[^>]*>', block)
            if new_text is None:
                return 'error', 'no anchor para inyectar og'
            text = new_text
        actions.append('og+twitter')

    if not actions:
        return 'skip', 'ya completo'

    if not dry_run and text != original:
        html_path.write_text(text, encoding='utf-8')

    return 'ok', ', '.join(actions)


def main():
    dry_run = '--dry-run' in sys.argv[1:]
    ok = skip = err = missing = 0
    for path in HUBS:
        for lang in ('es', 'ca', 'en'):
            if lang == 'es':
                f = REPO / path / 'index.html'
            else:
                f = REPO / lang / path / 'index.html'
            label = f'[{lang}] {path}'
            if not f.exists():
                print(f'  - {label}: archivo no existe (saltando)')
                missing += 1
                continue
            try:
                status, msg = process_file(f, lang, path, dry_run=dry_run)
            except Exception as e:
                print(f'  ✗ {label}: ERROR {e}')
                err += 1
                continue
            sym = {'ok': '✓', 'skip': '·', 'error': '✗'}[status]
            print(f'  {sym} {label}: {msg}')
            if status == 'ok':
                ok += 1
            elif status == 'skip':
                skip += 1
            else:
                err += 1

    prefix = '[DRY-RUN] ' if dry_run else ''
    print(f'\n─── Resumen ───')
    print(f'  {prefix}Procesados: {ok}, Saltados: {skip}, Errores: {err}, No existen: {missing}')


if __name__ == '__main__':
    main()
