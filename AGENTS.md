# AGENTS.md — alexreyes.es

Guía de trabajo para Claude (y para mí) sobre cómo mantener este repo sin
ensuciarlo. Si vas a crear o modificar páginas, lee esto primero.

## Estructura clave

```
/templates/
  _chrome/
    nav.es.html          ← nav canónico para páginas con html lang="es"
    nav.ca.html          ← nav canónico para páginas con html lang="ca"
    footer.html          ← footer canónico (siempre español, mismo en root)
    ibo-disclaimer.html  ← disclaimer IBO bilingüe (sólo IB)
  apunte.template.html   ← esqueleto para nuevas páginas de apuntes
  ejercicio.template.html← esqueleto para nuevas fichas de ejercicios

/scripts/
  sync-aula-chrome.py    ← sincroniza nav/footer/ibo en todos los HTML
  bump-css-version.py    ← cache-busting: actualiza ?v={timestamp} en CSS refs
  build_ejercicios.py    ← reconstruye índice del banco
  build_exam_pages.py    ← genera páginas de exámenes desde JSON

/aula/
  ib-ai-hl/{apuntes,ejercicios,examenes}/   ← IB lang="es"
  ccss-1btl/{apuntes,ejercicios,examenes}/  ← CCSS lang="ca"
  eso-2/{apuntes,examenes}/                 ← ESO lang="ca"

/ca/, /en/  ← versiones traducidas con URLs propias y lang switcher.
              NO sincronizadas por sync-aula-chrome.py (chrome distinto).
```

## Workflow: añadir un apunte nuevo

1. Copia `templates/apunte.template.html` a la ruta correspondiente:
   ```
   /aula/{materia}/apuntes/{unidad}/{NN-slug}.html
   ```
2. Pon el `<html lang="...">` correcto (`es` para IB, `ca` para CCSS/ESO).
3. Rellena los placeholders `{{...}}` y reemplaza `{{V}}` por el timestamp
   actual (formato `YYYYMMDDhhmm`) o ejecuta `bump-css-version.py` después.
4. Si NO es página IB, borra el bloque `<aside class="ibo-disclaimer">`.
5. Corre `python3 scripts/sync-aula-chrome.py` para asegurar que el nav y
   footer del archivo nuevo quedan sincronizados al canónico.

## Workflow: añadir una ficha de ejercicios

Igual que apuntes pero con `templates/ejercicio.template.html`:

```
/aula/{materia}/ejercicios/{slug}/index.html
```

Después, crea el JSON correspondiente en
`/assets/data/ejercicios/{slug}.json` con etiquetas curriculares y
ejecuta `python3 scripts/build_ejercicios.py` para refrescar el índice.

## Workflow: cambiar nav o footer del sitio entero

1. Edita el template canónico:
   - `templates/_chrome/nav.es.html` — afecta a páginas `lang="es"`
   - `templates/_chrome/nav.ca.html` — afecta a páginas `lang="ca"`
   - `templates/_chrome/footer.html` — afecta a TODAS las páginas (root)
   - `templates/_chrome/ibo-disclaimer.html` — afecta a páginas IB
2. Comprueba qué cambiaría:
   ```
   python3 scripts/sync-aula-chrome.py --dry-run
   ```
3. Aplica los cambios:
   ```
   python3 scripts/sync-aula-chrome.py
   ```
4. Idempotente: correrlo dos veces seguidas no rompe nada.

## Workflow: bump cache-busting cuando edites CSS

1. Edita `style.css` o `assets/css/*.css`.
2. Ejecuta `python3 scripts/bump-css-version.py` para que todos los HTML
   apunten a la nueva versión.
3. Commit + push. Cloudflare Pages auto-deploya.
4. Si hace falta forzar el purge del CDN: panel Cloudflare → Caché → Purgar todo.

## Reglas i18n actual

- El árbol raíz (`/aula/`, `/docencia/`, `/`) tiene contenido español
  (lang="es") o catalán (lang="ca") según la página. La nav y el footer
  son consistentes (script automatiza la elección de "Docencia" vs
  "Docència" según `<html lang>`).
- `/ca/` y `/en/` son árboles paralelos con URLs propias y lang switcher.
  No los toca el sync. Para cambiarlos, edición manual o futuro template
  específico.
- Eventualmente: las 3 lenguas para todas las páginas. No es prioridad
  inmediata.

## Reglas de seguridad recurrentes

- Nada de credenciales en el repo (`.gitignore` ya cubre `.env`, `*.key`).
- Scripts SRI en KaTeX siempre presentes (los templates ya los traen).
- El `_headers` del root mantiene CSP, HSTS, X-Frame, Referrer-Policy.
- `/editor/` está protegido con Cloudflare Access; no quitar.

## Convención visual (CCSS pattern)

- `exam-header` con `section-label` + `tag tag-orange` + `<h1>` + intro.
- Secciones: `<div class="seccion-aula"><h2><span class="num">N</span>Título</h2>`.
- Apartados: `<div class="ejercicio">` con pill `.num` verde (#10b981, border-radius 99px).
- Soluciones colapsables: `<details class="solucion"><summary>Solución</summary>`.
- Toolbar PDF en fichas: `.fitxa-toolbar` con `.fitxa-btn-primary` (purple)
  y `.fitxa-btn-secondary` (white).
- Sin grid en hubs. Sin TOC sticky. Sin "Ver unidad detallada" duplicada.

Si modificas estilos visuales, edita `/assets/css/aula.css` (no inline).
