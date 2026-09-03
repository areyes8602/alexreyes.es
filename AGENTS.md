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
  bump-css-version.py    ← cache-busting: actualiza ?v={timestamp} en refs de CSS
                            Y de JS (/assets/js/*.js). Correr tras editar cualquier
                            .css o .js para que el CDN/navegador sirva la versión nueva.
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
  build_bibliografia.py  ← bibliografía del doctorado: lee assets/data/bibliografia-doctorado.json,
                            ordena alfabético (bibtex 'plain'), numera [n] e inyecta la lista +
                            filtro por facetas (tipo/área/MSC/dificultad/acceso/importancia) entre
                            los marcadores BIB:START/END de doctorado/bibliografia/index.html.
                            Edita el JSON y re-ejecuta. CSS y JS del filtro viven en la página.
  build_cronologia.py    ← cronología del doctorado: lee assets/data/cronologia-doctorado.json
                            y genera las 3 páginas completas (es/ca/en) de /doctorado/cronologia/
                            con línea del tiempo vertical graduada por años (2026–2033 color
                            principal, 2034–2035 prórroga) y marcador del momento actual.
  build_feed.py          ← genera feed.xml (RSS 2.0) desde las noticias de la home
  check_i18n.py          ← CI: verifica que cada selector ES·CA·EN resuelve (no 404)
                            y es coherente. Usa i18n-baseline.txt (fallos conocidos);
                            solo falla ante regresiones. --strict = auditoría completa.
  build_sitemap.py       ← regenera sitemap.xml con todas las páginas vivas
  build_archived_subjects.py ← landings simples de asignatura (es/ca/en). Cada
                            entrada de SUBJECTS lleva "status": "archived" (por
                            defecto) o "active" + "year" (materia que imparto
                            este curso pero sin temario propio publicado: chip
                            verde con el curso en vez de "Archivada"). Las
                            asignaturas con temario y unidades van en
                            build_active_subjects.py, no aquí.
  build_ejercicios.py    ← reconstruye el índice del banco. Emite DOS ficheros:
                            ejercicios-index.json (búsqueda/filtros, ligero) y
                            ejercicios-apartados.json (los apartados, cargados aparte
                            solo por /docencia/mi-examen/). Commitea ambos.
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

## Workflow: cambiar las asignaturas de un curso académico

Al empezar curso hay que tocar, en este orden:

1. `scripts/build_archived_subjects.py` — mueve asignaturas entre
   `"status": "archived"` y `"status": "active"` (+ `"year"`), y añade las
   nuevas que aún no tengan temario. Ejecútalo.
2. `/docencia/index.html`, `/ca/…`, `/en/…` — la etiqueta `Curso XXXX–YY`, las
   tarjetas de la rejilla de activas y la lista del bloque Archivo. Es HTML a
   mano en los 3 idiomas.
3. `scripts/build_active_subjects.py` — `tag_year` y `year_current` de las
   asignaturas CON temario, más sus unidades y fechas del curso nuevo.
4. `scripts/build_contact_feedback.py` — la lista curada `COURSES`.
5. `scripts/build_sitemap.py` — añade los hubs nuevos a `trilingual_paths`.
6. Home (`index.html` ×3): la línea de "Ahora mismo" con el curso en marcha.
7. Pasos finales de siempre: `add_og_tags.py`, `add_jsonld.py`,
   `add_hreflang.py`, `add_skiplink.py --apply`, `add_search.py`,
   `add-lang-persist-script.py`, `build_sitemap.py`, `check_i18n.py`.

⚠️ Estos scripts corren sobre TODO el repo y arrastran cambios pendientes de
otras pasadas (p. ej. `add_search.py` tocando ~1800 exámenes). Revisa
`git status` y revierte lo que quede fuera del cambio que estás haciendo.

## Workflow: el horario de clase de 2n ESO E

`scripts/build_horari_classe.py` genera `/docencia/tutoria-2eso/horari/` en los
3 idiomas: la rejilla semanal COMPLETA del grupo (todas las materias y su
profesorado), no solo mis horas. Es la parte pública de la tutoría; no hay
ningún dato de alumnos.

- `SUBJECTS` — nombre por idioma + profesorado. `"meu": True` resalta las que
  imparto yo (Matemàtiques, Tutoria, Projectes).
- `GRID` — una entrada por franja: `(ini, fi, [lun…vie])`, o
  `("break", "pati"|"migdia", (ini, fi))` para patio y mediodía.
- `"col"` — pareja de pastel (claro, oscuro) por materia. Se emite como
  variables CSS `--mc-l` / `--mc-d` en cada celda, así no hacen falta 15
  reglas duplicadas por tema.
- Dos vistas opcionales, con casilla y recordadas en `localStorage`:
  destacar mis materias (`h-meu`, por defecto ON) y color por materia
  (`h-colors`, por defecto OFF). Las clases las pone un script del `<head>`
  sobre `<html>`, antes del primer pintado, para que no parpadee.
  ⚠️ `data-theme` vive en ese MISMO `<html>`: para el tema oscuro hace falta
  `.h-colors[data-theme="dark"]` (sin espacio), no un selector descendente.
- El PDF se hace desde el navegador: `@media print` + `window.print()`, igual
  que `/tutoria/imprimir/`. Cabe en una A4 horizontal; si añades filas,
  comprueba que sigue siendo 1 página. En papel se fuerza siempre la paleta
  clara y `print-color-adjust:exact`, se navegue en el tema que se navegue.
- No subir la foto/captura del horario Untis: la rejilla es HTML para que sea
  accesible, traducible y buscable.

El enlace al horario vive en el CUERPO del hub de tutoría (`link-card`), no
como botón de cabecera: la derecha del título queda reservada al área privada.

Si cambia el horario, edita `GRID` y ejecuta el script; y revisa que las horas
de `schedule` en `build_archived_subjects.py` / `build_active_info_pages.py`
sigan cuadrando con la rejilla (son dos fuentes distintas: la hoja Untis del
profesor y la del grupo).

Franjas contiguas del mismo día se muestran fusionadas (`merge_slots()` en
`build_archived_subjects.py`): Projectes son dos sesiones seguidas el viernes y
sale como "Viernes 15:30–17:30", pero cuentan 2 en horas/semana.

⚠️ `.gitignore` tiene `tutoria-*/` como red de seguridad contra volcados de
datos. Está negado para `docencia/tutoria-*/` (y sus `ca/`, `en/`), que es
sitio público generado. Si creas otra subpágina pública ahí, comprueba con
`git check-ignore -v <ruta>` que no queda ignorada.

## Workflow: archivar el curso anterior de una asignatura activa

Las asignaturas con temario (`build_active_subjects.py` + `build_active_info_pages.py`)
guardan sus cursos pasados en la clave `archived_years` de la propia asignatura:

```python
"year_current": "2026–27",
"units": [],                      # el temario del curso vivo
"archived_years": [
    {"year": "2025–26", "slug": "2025-2026", "units": [ ... ]},
],
```

El truco de render es el **`code` compuesto**: la variante archivada se genera
con `code = "2eso/2025-2026"`, y como todas las URLs se construyen igual
(`/docencia/{code}/…`), la página, su `info/`, su canonical y su lang switcher
caen solas en la subcarpeta. Es el mismo esquema que ya usan las promociones IB
(`ib-ai/2024-2026`).

Para archivar un curso al terminarlo:

1. Mueve `units` (y `schedule`/`aval`/`documents` en las info pages) a una
   entrada nueva de `archived_years`, con su `year` y su `slug` (`AAAA-AAAA`,
   sin guion largo: va en una URL).
2. Deja el curso vivo con `units: []` y sube `tag_year` / `year_current`.
3. Ejecuta los dos builders. Generan el curso vivo (con estado "temario aún no
   publicado") y una página por año archivado, con aviso de curso cerrado y el
   selector de curso enlazando ambos.
4. Añade las rutas nuevas a `trilingual_paths` en `build_sitemap.py`.
5. Pasos finales de siempre (OG, JSON-LD, hreflang, skip-link, sitemap).

El material en sí (`/aula/…`) **no se mueve**: las unidades del año archivado
siguen apuntando a las mismas rutas.

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
3. Commit + push. Cloudflare Pages auto-deploya (proyecto `alexreyes-web`).
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

## /tutoria/ — datos personales de menores

Área privada con las fichas de los alumnos de tutoría. Regla que no se
negocia: **los datos NO viven en el repositorio.** Este repo es público y
tiene forks; cualquier cosa commiteada aquí es permanente y pública.

```
functions/tutoria/_middleware.js  gate de servidor: sin sesión no sale NADA
functions/tutoria/_auth.js        cookie propia (8 h) + TUTORIA_SECRET
functions/tutoria/api/            login · logout · alumnes · fitxa · foto
tutoria/index.html                orla; pinta lo que devuelve la API
tutoria/fitxa/index.html          ficha individual, editable
scripts/tutoria_import_orla.py    carga la orla del centro → D1 + R2
scripts/sql/tutoria_schema.sql    esquema de D1
scripts/tutoria_orla_local.py     alternativa offline: un HTML autocontenido
```

Los nombres van a **D1** (`TUTORIA_DB`) y las fotos a **R2**
(`TUTORIA_FOTOS`), ambos privados. Las fotos no son ficheros estáticos:
salen por `/tutoria/api/foto`, que exige sesión. Sin cookie válida no hay
URL que las alcance.

Variables en Cloudflare Pages (proyecto `alexreyes-web`): `TUTORIA_USER`,
`TUTORIA_PASS`, `TUTORIA_SECRET`. Si falta cualquiera, el middleware sirve
una página de setup y nada más — nunca el contenido.

**`TUTORIA_PASS` es el punto débil de todo el diseño.** El resto (gate en
el edge, bucket privado, cookie firmada, noindex) es sólido; una
contraseña reutilizada o corta lo anula entero. Larga, aleatoria, de
gestor, y usada solo aquí. El login frena un segundo por intento fallido,
que ayuda contra fuerza bruta pero no salva a una contraseña mala.

Al empezar curso, o al cambiar la orla:

```
python3 scripts/tutoria_import_orla.py Orla_2ESO_E.pdf --grup 2ESO-E --curs 2026-27 -J eu
bash <dir que te indique>/subir.sh
rm -rf <ese dir>
```

El `-J eu` es obligatorio porque el bucket se creó con jurisdicción europea:
esos buckets viven en un espacio de nombres aparte y, sin el flag, wrangler
responde «the specified bucket does not exist» aunque el bucket se vea en el
panel. El binding de Pages también tiene que llevar la jurisdicción. D1 no
usa jurisdicciones: solo afecta a los comandos de R2.

El importador se niega a escribir dentro del repo.

`subir.sh` mantiene un `_roster.txt` en el bucket con los alumnos de la
última carga. En la siguiente, borra de R2 las fotos de quien ya no está
antes de subir las nuevas: R2 no tiene «borra lo que sobra», y sin esto
las imágenes de alumnos de cursos pasados se acumularían indefinidamente.
Son datos de menores; la retención importa tanto como el acceso.

`scripts/tutoria_orla_local.py` genera, de la misma orla, un HTML
autocontenido en `~/Tutoria` que funciona sin conexión. Sirve como copia
de trabajo o respaldo, pero **cada copia es otro sitio donde hay datos de
menores**: si la generas, no la dejes olvidada ni sin cifrar.

Los scripts de post-proceso (`add_og_tags`, `add_jsonld`, `add_hreflang`,
`add_search`, `add_skiplink`, `add-lang-persist-script`) **saltan** `panel/`
y `tutoria/`. `robots.txt` las excluye y `_headers` les pone `noindex` +
`no-store`.

## Cloudflare: qué es qué

- **Pages `alexreyes-web`** — el proyecto que sirve alexreyes.es y despliega
  este repo en cada push a `main`. Aquí viven las variables de entorno y los
  bindings de las Functions (`/panel/`, `/tutoria/`). Existe otro proyecto
  llamado `alexreyes-es`: **no es este**. Si dudas, mira cuál tiene el dominio
  `alexreyes.es` en Custom domains y un deploy reciente.
- **Worker `panel-push`** — avisos Web Push del Centro de Mando. Se despliega
  aparte con `npx wrangler deploy` desde `workers/panel-push/`.
- **D1 y R2** — `tutoria` (fichas) y `tutoria-fotos` (imágenes), enlazados a
  Pages como `TUTORIA_DB` y `TUTORIA_FOTOS`.

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
