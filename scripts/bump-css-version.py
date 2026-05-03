#!/usr/bin/env python3
"""
bump-css-version.py — Añade/actualiza el cache-busting ?v={timestamp} a las
referencias de los CSS principales en TODOS los HTML del repo.

Por qué: Cloudflare cachea /assets/css/* durante max-age=3600 (1h). Cuando se
cambia un CSS, los navegadores y el CDN siguen sirviendo la versión vieja hasta
que el caché expire. Solución: cada referencia al CSS lleva un query string
?v=<timestamp> que cambia con cada bump → URL distinta para el CDN/browser →
fetch de versión nueva inmediato.

Uso:
    python3 scripts/bump-css-version.py

Esto:
  1. Genera un timestamp YYYYMMDDhhmm de "ahora".
  2. Recorre TODOS los .html del repo.
  3. Para cada referencia /assets/css/{aula,examenes,banco,style}.css con o sin
     ?v={cualquier} lo reemplaza por /assets/css/{X}.css?v={timestamp_nuevo}.
     Lo mismo con /style.css en la raíz.
  4. Reporta cuántos archivos cambió.

Cuándo correrlo:
  - Después de modificar cualquier CSS bajo /assets/css/ o /style.css
  - Antes de hacer commit + push
"""
import re
import time
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent

# Patrones de CSS a versionar. Cada entrada es (regex_path, replacement_template).
# El regex captura la URL completa (con o sin ?v=...), el reemplazo usa el nuevo timestamp.
CSS_TARGETS = [
    r'/assets/css/aula\.css',
    r'/assets/css/examenes\.css',
    r'/assets/css/banco\.css',
    r'/assets/css/mi-examen\.css',
    r'/style\.css',
]


def main():
    timestamp = time.strftime("%Y%m%d%H%M")
    print(f"─── Bumping CSS version → ?v={timestamp} ───\n")

    # Construir patrón compuesto: para cada CSS, capturar opcionalmente el ?v=...
    # Reemplazo: la URL base + nuevo ?v=
    archivos_cambiados = 0
    cambios_total = 0

    for html in REPO.rglob("*.html"):
        # Saltar archivos en .git, node_modules, etc.
        partes = html.relative_to(REPO).parts
        if any(p.startswith('.') for p in partes):
            continue
        if 'node_modules' in partes:
            continue

        try:
            text = html.read_text(encoding='utf-8')
        except Exception:
            continue
        original = text

        for pattern_base in CSS_TARGETS:
            # Matchear la URL completa (con posible ?v=...) cuando aparece dentro de un atributo href
            # Ej: href="/assets/css/aula.css" o href="/assets/css/aula.css?v=20260503"
            full_pattern = re.compile(
                r'(href=["\'])(' + pattern_base + r')(\?v=\d+)?(["\'])'
            )

            def replace_with_version(m):
                return f'{m.group(1)}{m.group(2)}?v={timestamp}{m.group(4)}'

            text, n = full_pattern.subn(replace_with_version, text)
            cambios_total += n

        if text != original:
            html.write_text(text, encoding='utf-8')
            archivos_cambiados += 1

    print(f"✓ Archivos modificados: {archivos_cambiados}")
    print(f"✓ Reemplazos totales: {cambios_total}")
    print(f"\nLos navegadores y Cloudflare CDN servirán la versión nueva al instante.")
    print(f"Recuerda hacer commit + push para que el deploy de Cloudflare Pages aplique.")


if __name__ == "__main__":
    main()
