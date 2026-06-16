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
  add-seo-to-hubs.py     ← inyecta canonical + hreflang + OG + Twitter en hubs
  add_og_tags.py         ← PASO FINAL: OG/Twitter en TODA página sin OG (catch-all,
                            idempotente; deriva de <title>/description/canonical).
                            Correr siempre al final tras generar /aula/ (apuntes,
                            ejercicios, exámenes), que no inyectan OG por sí mismos.
  add_jsonld.py          ← PASO FINAL: datos estructurados schema.org (JSON-LD).
                            BreadcrumbList (de cada breadcrumb), LearningResource
                            (hojas de /aula/) y WebSite (homes). Idempotente; correr
                            tras add_og_tags.py. No inventa datos: deriva del HTML.
  add_hreflang.py        ← PASO FINAL: canonical + <link rel=alternate hreflang>.
                            Solo emite hreflang para los idiomas que EXISTEN en disco
                            (+ x-default→ES); las páginas aún sin traducir no apuntan
                            a CA/EN 404. Re-ejecutable: se actualiza al traducir.
  add_skiplink.py        ← PASO FINAL: cablea el skip-link de accesibilidad
                            (<a class="skip-link" href="#main"> tras <body> + id="main"
                            en <main>), localizado es/ca/en. Idempotente y auto-corrige
                            el texto si no casa con el idioma. CSS ya en style.css.
  build_feed.py          ← genera feed.xml (RSS 2.0) desde las noticias de la home
  check_i18n.py          ← CI: verifica que cada selector ES·CA·EN resuelve (no 404)
                            y es coherente. Usa i18n-baseline.txt (fallos conocidos);
                            solo falla ante regresiones. --strict = auditoría completa.
  build_sitemap.py       ← regenera sitemap.xml con todas las páginas vivas
  build_ejercicios.py    ← reconstruye índice del banco
  build_exam_pages.py    ← genera páginas de exámenes desde JSON
  build_contact_feedback.py ← regenera el desplegable "Sobre la web" de /contacto/
                            (es/ca/en). Cursos = lista curada en el script;
                            notas y papers se leen del disco con su título por
                            idioma. Correr tras publicar una nota o un paper.

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

## Workflow: añadir un hub nuevo (página índice de materia o sección)

1. Crea el `index.html` del hub en `/{path}/` (raíz), `/ca/{path}/` y `/en/{path}/`.
2. Añade el path a la lista `HUBS` en `scripts/add-seo-to-hubs.py`.
3. Ejecuta `python3 scripts/add-seo-to-hubs.py` — inyecta canonical + hreflang
   + OG + Twitter en las 3 versiones (lee title y description del propio archivo).
4. Ejecuta `python3 scripts/build_sitemap.py` para incluir el nuevo hub en el
   sitemap (si es trilingual, añádelo también a `trilingual_paths` en el script).
5. Idempotente: re-correr el SEO script no duplica nada.

## Workflow: añadir contenido en /aula/ (apuntes, ejercicios, exámenes)

Los builds de `/aula/` (`build_classe_pages.py`, exámenes, apuntes a mano) **no
inyectan OG por sí mismos**. Tras generarlos, ejecuta SIEMPRE como paso final:

```
python3 scripts/add_og_tags.py    # OG/Twitter en toda página sin OG (idempotente)
python3 scripts/add_jsonld.py     # JSON-LD schema.org (breadcrumbs, learning resource)
python3 scripts/add_hreflang.py   # canonical + hreflang (solo idiomas existentes)
python3 scripts/add_skiplink.py --apply  # skip-link a11y (localizado es/ca/en, idempotente)
python3 scripts/add_lazy_img.py --apply  # loading="lazy" en figuras (excepto hero y foto CV)
python3 scripts/build_sitemap.py
```

## Workflow: regenerar sitemap

Después de cualquier cambio estructural (añadir/quitar páginas, renombrar
carpetas), ejecuta:

```
python3 scripts/build_sitemap.py
```

El script auto-detecta exámenes, apuntes y ejercicios escaneando `aula/*/`.
Las URLs trilingües se mantienen en la lista `trilingual_paths` arriba del
script — añade ahí los hubs nuevos.

## Workflow: bump cache-busting cuando edites CSS

1. Edita `style.css` o `assets/css/*.css`.
2. Ejecuta `python3 scripts/bump-css-version.py` para que todos los HTML
   apunten a la nueva versión.
3. Commit + push. Cloudflare Pages auto-deploya.
4. Si hace falta forzar el purge del CDN: panel Cloudflare → Caché → Purgar todo.

## Workflow: añadir una NOTA divulgativa (/notas/)

Las notas (ensayos/divulgación, p. ej. `anillo-de-collatz`, `fibonacci-collatz`)
NO van en `/aula/` ni usan sus templates. Convenciones:

- Rutas: `/notas/{slug}/index.html`, `/ca/notas/{slug}/index.html`,
  `/en/notas/{slug}/index.html`. **El slug es el MISMO en los 3 idiomas**
  (no se traduce; p. ej. `fibonacci-collatz` en es/ca/en).
- La nota usa el **chrome del sitio** (nav + breadcrumb + page-header con
  `section-label` "Nota/Note" + `tag` + `<h1>` + fecha + `.nota-body` + footer),
  igual que `notas/anillo-de-collatz/`. Reutiliza nav/footer de esa nota.
- Si la nota lleva matemáticas/interactivos: KaTeX **0.16.9** (misma versión y
  SRI que la home), con delimitadores `$$ \\[ $ \\(`. Para contenido inyectado
  por JS, llamar a `renderMathInElement` sobre el contenedor tras pintarlo.
- CSS propio de la nota va en un `<style>` en su `<head>`, **scopeado** para no
  filtrar al chrome: nada de selectores `body{}`, `main{}`, `h1{}`, `a{}`,
  `footer{}` globales; los de elemento van bajo `.nota-body`. Renombra clases
  que colisionen con el sitio (p. ej. `.pill` → `.rpill`).
- Hub `/notas/index.html` (×3 idiomas): añade el item `note-item` arriba
  (más reciente primero) con su `data-tags` (minúsculas, separadas por espacio).
  El hub tiene **filtro por etiquetas** (`.filter-bar` + `filterNotes()`):
  botón "Todas/Totes/All" + un botón por etiqueta. Añade la etiqueta nueva si
  procede.
- Noticia en la home (ver sección de noticias) y sitemap:
  añade `'/notas/{slug}/'` a `trilingual_paths` en `build_sitemap.py` y re-corre.

## Transcreación i18n (NO traducción literal)

Las versiones /ca/ y /en/ de contenido divulgativo deben **escribirse de forma
nativa**, con la misma calidad que el original — no traducciones literales.
También se localizan **todos** los textos de los interactivos (botones,
leyendas, mensajes dinámicos del JS, tablas).

Terminología matemática:
- **CA**: "resto/residuo" → **residu** (NUNCA *resta*, que es la sustracción);
  graph/vertex/subgraph → **graf / vèrtex / subgraf**; arrow → **fletxa**;
  path → **camí/camins**; número áureo → **nombre auri**; "rodeo" → **marrada**.
- **EN**: remainder; graph/vertex/subgraph; arrow; path(s); **golden ratio**;
  "dos mil trillones" (2·10²¹) → **two sextillion**. Formato numérico inglés:
  `toLocaleString('en-US')` y **decimales con punto** (1.618, no 1{,}618).

## Home: sección de noticias y colores

- Las novedades de la home van en dos columnas (`news-col`): **Docencia** y
  **Doctorado/Doctorat/PhD**. Dentro de cada columna, **una tarjeta `.news-card`
  por tipo**, con cabecera (título + `.news-card-count`) y una lista
  `.news-card-list` con `max-height` + scroll (última noticia visible arriba).
  Tarjetas pueden quedar **vacías** (`.news-card-empty`, p. ej. "Congresos").
- Tipos actuales — Docencia: Copa Cangur · Mat. CCSS 1r BTL · 2n ESO ·
  Selectivitat-PAU. Doctorado: Publicaciones · Notas y divulgación ·
  Congresos · Hitos.
- **Semántica de color (importante):** verde `#10b981` = **Docencia**;
  lila/indigo `#6366f1` = **Doctorado**. Aplica a: puntos `.dot`/`.dot-purple`,
  `.now-dot`/`.now-dot-blue` de "Ahora mismo", y al acento (franja izquierda
  3px) de las `.news-card` por columna (`.news-col:nth-child(1)` verde,
  `nth-child(2)` lila). No cruzar estos colores.
- "Ahora mismo" (`now-section`): un `now-item` por línea de estado; el dot
  define la disciplina (verde docencia / lila doctorado).

## Imágenes de portada / ilustración

- **No usar imágenes autogeneradas por código** (SVG→PNG tipo clip-art): no dan
  la calidad del sitio. Para portada/og:image, usar Figma o encargo a
  ilustrador/a (como el grafo de `anillo-de-collatz`).
- Una nota llena de gráficos interactivos **no necesita** héroe estático; mejor
  sin og:image propio que con uno mediocre (`twitter:card` = `summary`).

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
