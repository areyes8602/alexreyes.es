#!/usr/bin/env python3
"""Regenerate sitemap.xml and robots.txt based on the current set of pages."""
import os
from datetime import date
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
BASE = 'https://alexreyes.es'
TODAY = date.today().isoformat()


def _build_git_lastmod_map():
    """Mapa {ruta_relativa: fecha_último_commit} en una sola pasada de git log.
    Es la fecha correcta para <lastmod>: refleja cuándo cambió el contenido,
    no cuándo se clonó el repo (que resetea los mtime)."""
    import subprocess
    m = {}
    try:
        out = subprocess.run(
            ['git', '-C', str(REPO_ROOT), 'log', '--name-only',
             '--format=%cs', '--no-renames'],
            capture_output=True, text=True, timeout=120,
        ).stdout
    except Exception:
        return m
    cur = None
    for line in out.splitlines():
        line = line.strip()
        if not line:
            continue
        if len(line) == 10 and line[4] == '-' and line[7] == '-':
            cur = line  # línea de fecha (%cs = YYYY-MM-DD)
        elif cur and line not in m:
            m[line] = cur  # primera aparición = commit más reciente
    return m


_GIT_LASTMOD = _build_git_lastmod_map()


def _lastmod(fs_path):
    """Fecha del último commit del archivo; si no está en git, cae a mtime y
    finalmente a hoy."""
    fs_path = Path(fs_path)
    try:
        rel = str(fs_path.resolve().relative_to(REPO_ROOT))
        if rel in _GIT_LASTMOD:
            return _GIT_LASTMOD[rel]
    except Exception:
        pass
    try:
        return date.fromtimestamp(fs_path.stat().st_mtime).isoformat()
    except Exception:
        return TODAY

# Pages that exist in all 3 languages (canonical ES paths).
# Add new pages here and re-run.
trilingual_paths = [
    '/', '/cv/', '/contacto/', '/doctorado/', '/doctorado/bibliografia/', '/doctorado/cronologia/', '/notas/',
    '/notas/anillo-de-collatz/', '/notas/fibonacci-collatz/',
    '/notas/el-hombre-y-la-nota-al-margen/',
    '/docencia/', '/docencia/ejercicios/', '/docencia/apuntes/', '/docencia/mi-examen/', '/docencia/mis-apuntes/',
    '/docencia/ib-ai/', '/docencia/ib-ai/2024-2026/', '/docencia/ib-ai/2025-2027/',
    '/docencia/ccss-1btl/', '/docencia/cangur/', '/docencia/2eso/',
    # Asignaturas activas del curso 2026–27 sin temario propio todavía
    '/docencia/eso-3/', '/docencia/eso-4/',
    '/docencia/projectes-2eso/', '/docencia/tutoria-2eso/',
    # Subject info subpages (per asignatura)
    '/docencia/2eso/info/', '/docencia/ccss-1btl/info/',
    '/docencia/ib-ai/2024-2026/info/', '/docencia/ib-ai/2025-2027/info/',
    # Cangur: hub de pruebas Copa y problemas por tema (trilingües)
    '/aula/cangur/copa/', '/aula/cangur/temes/',
    # Cangur: Prova Cangur (info) y "Ponte a prueba" (test interactivo)
    '/aula/cangur/prova/', '/aula/cangur/prova/test/',
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

# Selectivitat (PAU): hub, índices de examen y páginas pN
for p in sorted(_REPO.glob("aula/selectivitat/index.html")):
    if not _is_retired(p):
        single_paths.append('/' + str(p.parent.relative_to(_REPO)) + '/')
for p in sorted(_REPO.glob("aula/selectivitat/*/index.html")):
    if not _is_retired(p):
        single_paths.append('/' + str(p.parent.relative_to(_REPO)) + '/')
for p in sorted(_REPO.glob("aula/selectivitat/*/p*.html")):
    if not _is_retired(p):
        single_paths.append('/' + str(p.relative_to(_REPO)))

# Mirrors /ca/ y /en/ de exámenes y selectivitat (páginas que existen traducidas)
for _pref in ("ca", "en"):
    _hub = _REPO / _pref / "aula" / "selectivitat" / "index.html"
    if _hub.exists() and not _is_retired(_hub):
        single_paths.append('/' + str(_hub.parent.relative_to(_REPO)) + '/')
for _pref in ("ca", "en"):
    for pat in (f"{_pref}/aula/*/examenes/*/index.html", f"{_pref}/aula/selectivitat/*/index.html"):
        for p in sorted(_REPO.glob(pat)):
            if not _is_retired(p):
                single_paths.append('/' + str(p.parent.relative_to(_REPO)) + '/')
    for pat in (f"{_pref}/aula/*/examenes/*/p*.html", f"{_pref}/aula/selectivitat/*/p*.html"):
        for p in sorted(_REPO.glob(pat)):
            if not _is_retired(p):
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
    lang_prefix = '' if lang == 'es' else f'{lang}/'
    if base_path == '/':
        fs_path = REPO_ROOT / lang_prefix / 'index.html'
    else:
        fs_path = REPO_ROOT / (lang_prefix + base_path.strip('/') + '/index.html')
    lastmod = _lastmod(fs_path)
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
        f'    <lastmod>{lastmod}</lastmod>\n'
        f'    <changefreq>{changefreq}</changefreq>\n'
        f'    <priority>{priority}</priority>\n'
        + '\n'.join(alternates) + '\n'
        '  </url>'
    )


def single_url_tag(path):
    fs_path = REPO_ROOT / (path.lstrip('/') + ('index.html' if path.endswith('/') else ''))
    lastmod = _lastmod(fs_path)
    return (
        '  <url>\n'
        f'    <loc>{BASE + path}</loc>\n'
        f'    <lastmod>{lastmod}</lastmod>\n'
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
