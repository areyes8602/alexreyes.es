#!/usr/bin/env python3
"""Regenerate sitemap.xml and robots.txt based on the current set of pages."""
import os
from datetime import date
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
BASE = 'https://alexreyes.es'
TODAY = date.today().isoformat()

# Pages that exist in all 3 languages (canonical ES paths).
# Add new pages here and re-run.
trilingual_paths = [
    '/', '/cv/', '/contacto/', '/doctorado/', '/notas/',
    '/docencia/', '/docencia/ejercicios/', '/docencia/apuntes/', '/docencia/mi-examen/', '/docencia/mis-apuntes/',
    '/docencia/ib-ai/', '/docencia/ib-ai/2024-2026/', '/docencia/ib-ai/2025-2027/',
    '/docencia/ccss-1btl/', '/docencia/cangur/', '/docencia/2eso/',
    # Subject info subpages (per asignatura)
    '/docencia/2eso/info/', '/docencia/ccss-1btl/info/',
    '/docencia/ib-ai/2024-2026/info/', '/docencia/ib-ai/2025-2027/info/',
]

# Pages that exist only in ES (aula materials for a specific cohort).
# Exam index pages are auto-detected by scanning aula/.
import os as _os
_REPO = Path(__file__).resolve().parent.parent

def _is_retired(html_path: Path) -> bool:
    """Skip pages marked retired (noindex) so they don't enter the sitemap."""
    try:
        head = html_path.read_text(encoding='utf-8')[:2000]
    except Exception:
        return False
    return 'name="robots" content="noindex' in head

_exam_dirs = sorted(_REPO.glob("aula/*/examenes/*/index.html"))
single_paths = [
    '/' + str(p.parent.relative_to(_REPO)) + '/'
    for p in _exam_dirs
    if not _is_retired(p)
]
# plus the per-pregunta static HTMLs that exist
for p in sorted(_REPO.glob("aula/*/examenes/*/p*.html")):
    if _is_retired(p):
        continue
    single_paths.append('/' + str(p.relative_to(_REPO)))

# Apuntes: índices de unidad y apartados HTML individuales
for p in sorted(_REPO.glob("aula/*/apuntes/*/index.html")):
    if _is_retired(p):
        continue
    single_paths.append('/' + str(p.parent.relative_to(_REPO)) + '/')
for p in sorted(_REPO.glob("aula/*/apuntes/*/*.html")):
    if p.name == "index.html" or _is_retired(p):
        continue
    single_paths.append('/' + str(p.relative_to(_REPO)))

# Ejercicios: fichas temáticas, ejercicios de clase y colecciones de práctica.
# (Antes /fitxes/ y /exercicis-classe/, unificados en /ejercicios/ por F3.)
for p in sorted(_REPO.glob("aula/*/ejercicios/*/index.html")):
    if _is_retired(p):
        continue
    single_paths.append('/' + str(p.parent.relative_to(_REPO)) + '/')
for p in sorted(_REPO.glob("aula/*/ejercicios/*/*.html")):
    if p.name == "index.html" or _is_retired(p):
        continue
    single_paths.append('/' + str(p.relative_to(_REPO)))


def url_tag(base_path, lang):
    loc = BASE + (base_path if lang == 'es' else f'/{lang}' + (base_path if base_path != '/' else '/'))
    alternates = []
    for l in ('es', 'ca', 'en'):
        u = BASE + (base_path if l == 'es' else (f'/{l}' + (base_path if base_path != '/' else '/')))
        alternates.append(f'    <xhtml:link rel="alternate" hreflang="{l}" href="{u}"/>')
    alternates.append(f'    <xhtml:link rel="alternate" hreflang="x-default" href="{BASE + base_path}"/>')
    priority = '1.0' if base_path == '/' else '0.8'
    changefreq = 'weekly' if base_path in ('/', '/docencia/', '/doctorado/', '/docencia/ejercicios/') else 'monthly'
    return (
        '  <url>\n'
        f'    <loc>{loc}</loc>\n'
        f'    <lastmod>{TODAY}</lastmod>\n'
        f'    <changefreq>{changefreq}</changefreq>\n'
        f'    <priority>{priority}</priority>\n'
        + '\n'.join(alternates) + '\n'
        '  </url>'
    )


def single_url_tag(path):
    return (
        '  <url>\n'
        f'    <loc>{BASE + path}</loc>\n'
        f'    <lastmod>{TODAY}</lastmod>\n'
        f'    <changefreq>monthly</changefreq>\n'
        f'    <priority>0.6</priority>\n'
        '  </url>'
    )


def main():
    # Assert every page file actually exists (catches typos in the list above)
    missing = []
    for p in trilingual_paths:
        for lang_prefix in ('', 'ca/', 'en/'):
            fs_path = REPO_ROOT / (lang_prefix + p.strip('/') + '/index.html').lstrip('/')
            if p == '/' and lang_prefix == '':
                fs_path = REPO_ROOT / 'index.html'
            elif p == '/' and lang_prefix:
                fs_path = REPO_ROOT / lang_prefix / 'index.html'
            if not fs_path.exists():
                missing.append(str(fs_path.relative_to(REPO_ROOT)))
    for p in single_paths:
        fs_path = REPO_ROOT / p.lstrip('/')
        if p.endswith('/'):
            fs_path = REPO_ROOT / (p.lstrip('/') + 'index.html')
        if not fs_path.exists():
            missing.append(p)
    if missing:
        print("⚠ Páginas referenciadas pero no encontradas en disco:")
        for m in missing:
            print(f"  {m}")

    entries = []
    for p in trilingual_paths:
        for l in ('es', 'ca', 'en'):
            entries.append(url_tag(p, l))
    for p in single_paths:
        entries.append(single_url_tag(p))

    sitemap = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"\n'
        '        xmlns:xhtml="http://www.w3.org/1999/xhtml">\n'
        + '\n'.join(entries) + '\n'
        '</urlset>\n'
    )
    (REPO_ROOT / 'sitemap.xml').write_text(sitemap, encoding='utf-8')

    robots = (
        'User-agent: *\n'
        'Allow: /\n'
        'Disallow: /editor/\n'
        '\n'
        f'Sitemap: {BASE}/sitemap.xml\n'
    )
    (REPO_ROOT / 'robots.txt').write_text(robots, encoding='utf-8')

    print(f"✓ sitemap.xml: {len(entries)} URLs ({os.path.getsize(REPO_ROOT / 'sitemap.xml')} bytes)")
    print(f"✓ robots.txt written")


if __name__ == "__main__":
    main()
