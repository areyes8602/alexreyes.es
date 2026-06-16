# Auditoría técnica — alexreyes.es

**Fecha:** 16 jun 2026 · **Método:** revisión directa del repositorio (no del HTML servido).
**Alcance:** SEO, velocidad, accesibilidad, seguridad y calidad general.

Todos los hallazgos de abajo están verificados contra archivos concretos del repo.
Cuando un punto es una decisión deliberada documentada en `AGENTS.md`, se marca como tal.

## Resumen ejecutivo

| Dimensión | Nota | Acción prioritaria |
|---|---|---|
| SEO | 9/10 | Reordenar `<title>` de exámenes (nombre legible primero) |
| Velocidad | 8.5/10 | `loading="lazy"` en figuras + carga condicional de KaTeX |
| Accesibilidad | 7/10 | Cablear el skip-link (ya existe el CSS) + `aria-label` en sliders |
| Seguridad | 9/10 | Endurecer CSP (`unsafe-inline`/`unsafe-eval`) a medio plazo |
| Calidad | 9/10 | Limpieza de archivos sueltos + refrescar `feed.xml` |

**No hay ningún problema crítico.** El sitio está en muy buen estado técnico: HTML/CSS
puro, pipeline de build con CI i18n, SEO multilingüe completo y cabeceras de seguridad
correctas. Lo que queda son pulidos, casi todos de severidad baja.

> Nota sobre la auditoría externa previa: marcaba como 🔴 críticos la ausencia de
> `hreflang`, de cabeceras de seguridad, de Schema.org y un CV vacío. Los cuatro son
> **falsos** — están todos presentes en el repo. Aquella auditoría se hizo sin leer el
> código. Esta sí.

## Estado de los arreglos (16 jun 2026)

Aplicados y verificados en esta sesión:

- ✅ **Skip-link cableado** en las 789 páginas (`<a class="skip-link" href="#main">`
  localizado es/ca/en + `id="main"`). Nuevo script mantenido `scripts/add_skiplink.py`
  (idempotente, auto-localiza) añadido al flujo "PASO FINAL" de `AGENTS.md`.
- ✅ **Sliders del simulador** `fibonacci-collatz` con `aria-label` (4 × 3 idiomas).
- ✅ **SVG informativos** (`grafoG`, `h4svg`) con `role="img"` + `aria-label` (×3 idiomas).
- ✅ **`loading="lazy"`** en 118 figuras de contenido (hero y foto de CV excluidos).
  Nuevo script `scripts/add_lazy_img.py` + paso en `AGENTS.md`.
- ✅ **`<title>` de exámenes** reordenado: nombre legible primero, código fuera
  (`build_exam_pages.py`); 0 títulos empiezan ya por el código interno.
- ✅ **CSP** con `frame-ancestors 'self'` añadido (`_headers`).
- ✅ **`_wtest_delete_me.txt`** borrado.
- ✅ **`build_feed.py` reparado**: no estaba "desfasado" sino **roto** — su regex buscaba
  `<h3 class="news-col-title">` pero la home migró a `<h2>`, así que generaba 0 ítems.
  Corregido a `<h[23]>`; el feed vuelve a 50 ítems.

Verificación: CI `check_i18n.py` sin regresiones nuevas (0); sin skip-links ni `id="main"`
duplicados; títulos bien formados.

Decisión consciente (no aplicado):

- 🔵 **KaTeX condicional**: revisado y **descartado por riesgo/beneficio**. Los hubs
  estáticos sin fórmulas (`/docencia/`, `/cv/`, `/contacto/`, `/aula/`) **ya no** cargan
  KaTeX, y la home **sí** usa matemáticas (`$h_m=4$`). Las páginas restantes que lo
  cargan son contenido con fórmulas o vistas JS-driven (hubs de apuntes/ejercicios) donde
  el math se inyecta dinámicamente y quitarlo a ciegas rompería el render. El reparto
  actual ya es razonable; no se toca.

---

## 1. SEO — 9/10

### Correcto (verificado)
- Meta `description`, `canonical`, OG completo (`og:image` 1200×630, `og:locale` + alternates), Twitter Card, `theme-color`, manifest, favicons. (`index.html` líneas 7–48)
- `hreflang` **presente** en `<head>`: `es` / `ca` / `en` / `x-default`. Generado por `scripts/add_hreflang.py`, que solo emite idiomas que existen en disco (no apunta a 404).
- **Schema.org / JSON-LD presente y abundante**: `BreadcrumbList` (766), `Person` (1251), `LearningResource` (624 hojas de `/aula/`), `WebSite` (3 homes). Generado por `add_jsonld.py`.
- `sitemap.xml` con 702 URLs, `lastmod` 2026-06-16 (fresco). `robots.txt` correcto, con `Disallow: /editor/` y referencia al sitemap.
- `feed.xml` (RSS 2.0) generado por `build_feed.py`.

### 🟡 Baja — `<title>` de exámenes empieza por el código interno
`aula/cangur/.../index.html`:
```
<title>2526-cangur-copa-junior-fase1-mati · XII Copa Cangur — 1a fase (matí)...</title>
```
Google pondera el principio del title. El código interno (`2526-cangur-...`) no aporta
nada al usuario y empuja el nombre legible fuera del primer plano.
**Fix:** en `scripts/build_exam_pages.py`, emitir `XII Copa Cangur — Júnior · Fase 1 (matí) | Àlex Reyes` y dejar el código solo como `id`/slug interno. Re-generar las páginas de examen.

### 🟡 Baja — `og:image` global única
Todas las páginas comparten `og-image.jpg`. **Es una decisión deliberada** (`AGENTS.md`:
"mejor sin og:image propio que con uno mediocre"). Se deja como aceptada; si en el futuro
hay portadas de calidad (Figma) para notas concretas, darles su propia `og:image`.

### 🔵 Mínima — `theme-color` fijo a oscuro
`<meta name="theme-color" content="#0a0a0a">` pero el tema por defecto es claro. Cosmético
(tinte de la barra del navegador). Opcional: dos `theme-color` con `media="(prefers-color-scheme)"`.

---

## 2. Velocidad / Core Web Vitals — 8.5/10

### Correcto (verificado)
- Sin framework JS. HTML/CSS puro servido por Cloudflare Pages (TTFB bajo, cache en edge).
- **KaTeX ya carga sin bloquear**: CSS con `media="print" onload="this.media='all'"` + JS con `defer`. Fuentes de Google con el mismo patrón diferido. (`index.html` 13–16)
- **Hero LCP bien resuelto**: `<img ... fetchpriority="high" decoding="async" width="800" height="1159" srcset="… 2x">` → sin CLS y con prioridad correcta. Existe `alex.webp`/`alex@2x.webp`.
- Cache-busting de CSS por timestamp (`bump-css-version.py`).

### 🟡 Baja — `loading="lazy"` casi ausente
Solo 9 de 124 `<img>` usan `loading="lazy"`. Las figuras de examen (`fig-pN.png`), que están
claramente below-the-fold, no lo llevan:
```
<img src="/aula/cangur/.../fig-p2.png" alt="Figura del problema 2" style="max-width:240px;...">
```
**Fix:** añadir `loading="lazy"` a las figuras de examen/apuntes en sus build scripts
(`build_exam_pages.py`, `build_apuntes.py`). **No** tocar el hero (debe seguir eager).

### 🟡 Baja — KaTeX en páginas sin matemáticas
Se carga en 702/794 páginas. La mayoría son contenido con fórmulas (justificado), pero la
home y algún hub lo cargan sin necesitarlo (~300 KB de CDN: CSS + 2 JS). 
**Fix:** incluir KaTeX solo si la página tiene `$`/`\(` (flag en el template o detección en
build). Ahorro real en home y hubs.

### 🔵 Mínima — JS inline de los simuladores sin minificar
La nota `fibonacci-collatz` trae 5 simuladores SVG con su JS inline sin minificar. No bloquea
el render del texto (va al final), pero es el contenido más pesado del sitio. Opcional:
minificar el bloque o moverlo a un `.js` con `defer`.

---

## 3. Accesibilidad — 7/10 (la dimensión más mejorable)

### Correcto (verificado)
- **Todas** las `<img>` tienen `alt` (0 sin `alt`, 0 con `alt=""`). Las figuras de examen son PNG con alt.
- `<main>` presente como landmark en home y plantillas. `lang` correcto en `<html>`.
- `:focus-visible` con outline visible definido en `style.css`. Iconos SVG dentro de botones llevan `aria-label`.
- **Contraste WCAG AA: pasa.** Calculado sobre las variables reales:
  - Claro: `--text-soft #525252` ≈ 7.1:1, `--text-faint #757575` ≈ 4.6:1 (pasa AA texto normal).
  - Oscuro: `--text-soft #a0a0a0` ≈ 7.6:1, `--text-faint #7a7a7a` ≈ 4.6:1 (pasa AA).
  - `--text-faint` queda **justo** por encima de 4.5:1; vigilar si se usa a <16px en mucho texto.

### 🟠 Media — Skip-link estilado pero NO cableado
`style.css` (líneas 967–984) define `.skip-link` y `main:focus`… pero **ningún** HTML del
sitio contiene el ancla (`0` páginas con `class="skip-link"` / `href="#main"` / `id="main"`).
Es CSS muerto y un requisito AA que falta.
**Fix:** en el chrome/plantillas, justo tras `<body>`:
```html
<a class="skip-link" href="#main">Saltar al contenido</a>
```
y poner `id="main"` en `<main>`. Propagar con `sync-aula-chrome.py` + edición de `/ca/` y `/en/`.

### 🟠 Media — Sliders de los simuladores sin nombre accesible
En `notas/fibonacci-collatz/` los 4 `<input type="range">` (`esc-n`, `mat-k`, `rh-m`, `teo-m`)
no tienen `<label for>` ni `aria-label`. Un lector de pantalla los anuncia como "control
deslizante" sin contexto.
**Fix:** `aria-label` descriptivo en cada uno, p. ej.
`<input type="range" id="esc-n" aria-label="Número de pasos de la escalera" ...>`. Localizar también en `/ca/` y `/en/`.

### 🟡 Baja — SVG interactivos sin rol semántico
La nota tiene 5 `<svg>` (grafo mod 6, etc.) pero solo 2 `aria-label` y 0 `role`. Los SVG que
transmiten información deberían llevar `role="img"` + `<title>` o `aria-label`; los puramente
decorativos, `aria-hidden="true"`.
**Fix:** auditar uno a uno y etiquetar según sea informativo o decorativo.

### 🔵 Mínima — alt genérico en figuras de examen
`alt="Figura del problema 2"` es un fallback correcto pero no describe la geometría.
Aceptable dado el volumen (243 páginas de examen); mejorar solo en figuras clave.

---

## 4. Seguridad — 9/10 (NO 4/10)

### Correcto (verificado en `_headers`, `_redirects`, `.gitignore`)
- **Cabeceras completas** (`_headers`, aplica a `/*`):
  - `Content-Security-Policy` con allowlist por directiva (self + jsDelivr + Stripe + GeoGebra + Cloudflare Insights).
  - `Strict-Transport-Security: max-age=31536000; includeSubDomains; preload`.
  - `X-Frame-Options: SAMEORIGIN`, `X-Content-Type-Options: nosniff`, `Referrer-Policy: strict-origin-when-cross-origin`, `Permissions-Policy` (cámara/micro/geo desactivados).
- `/editor/` bloqueado en el edge (`_redirects` → 404) **y** `noindex` (`X-Robots-Tag`) **y** `Disallow` en robots.txt. Triple cierre.
- `gate.js` está **deprecado y vaciado** a conciencia (cabecera del archivo cita la auditoría interna S-CRIT-01, may 2026: se eliminó un "gate" SHA-256 de cliente que no era control real). Bien resuelto.
- `.gitignore` cubre `.env*`, `*.key`, `*.pem`, `.dev.vars`, `.wrangler/`. **Sin secretos en el repo** (escaneo de api_key/secret/token/BEGIN: 0 reales).
- La lectura pública del banco es **JSON estático** (`/assets/data/*.json`), no una API expuesta. La superficie de ataque del frontend es mínima.

### 🟡 Baja — CSP con `unsafe-inline` y `unsafe-eval` en `script-src`
Debilitan la protección anti-XSS (se necesitan hoy por los `onload=` inline, KaTeX y
GeoGebra). Es una concesión común, pero conviene tenerla en el radar.
**Fix (medio plazo):** migrar a nonces o hashes por script y retirar `unsafe-inline`;
evaluar si GeoGebra realmente exige `unsafe-eval` o puede aislarse en iframe sandbox.

### 🟡 Baja — Sin `frame-ancestors` en la CSP
El anti-clickjacking depende solo de `X-Frame-Options: SAMEORIGIN`. El equivalente moderno
es `frame-ancestors 'self'` dentro de la CSP (algunos navegadores ya ignoran XFO).
**Fix:** añadir `frame-ancestors 'self'` a la directiva CSP en `_headers`.

### 🔵 A verificar fuera del repo — API de escritura del banco (D1/Worker)
El Worker que escribe en Cloudflare D1 (alta de ejercicios/exámenes) **no vive en este repo**,
así que su CORS y su auth no se pueden auditar aquí. Confirmar por separado: (a) que solo
acepta origen `https://alexreyes.es`, (b) que requiere auth server-side para escrituras.
No encontré ningún directorio `/admin/` en el repo (la auditoría previa lo mencionaba); el
único panel local es `/editor/`, ya bloqueado.

---

## 5. Calidad general — 9/10

### Correcto (verificado)
- **CV con contenido** (`cv/index.html`, 11 KB) + descargables en 3 idiomas (`assets/cv/CV_AlexReyes_{ES,CA,EN}.{pdf,docx}`). La auditoría previa decía "vacío": falso.
- Estructura de URLs limpia y consistente; 794 páginas HTML; mirrors trilingües con lang-switcher.
- Pipeline de build documentado (`AGENTS.md`) con scripts idempotentes y **CI de i18n** (`check_i18n.py`) que verifica que cada selector ES·CA·EN resuelve.
- Exámenes con PDF descargable; banco de ejercicios con índice generado.

### 🟡 Baja — `/contacto/` sin formulario
Solo `mailto:` (×3). **Es diseño deliberado** (`AGENTS.md`: paneles split + copiar-email +
feedback con selects→mailto). Aceptable; un formulario vía Worker (Resend/Mailgun) sería una
mejora de UX opcional, no una carencia.

### 🔵 Mínima — Archivos sueltos en la raíz
`_wtest_delete_me.txt` (8 bytes, claramente temporal) y `auditoria-unificacion.md` conviven
en el root. Los `.fuse_hidden*` ya están en `.gitignore`.
**Fix:** borrar `_wtest_delete_me.txt`; mover auditorías a `/docs/` si se quiere conservarlas.

### 🔵 Mínima — `feed.xml` algo desfasado
`lastBuildDate` = 12 jun 2026, mientras el sitemap es del 16 jun. Re-ejecutar `build_feed.py`
tras publicar para mantenerlos sincronizados.

---

## Plan de acción sugerido (por esfuerzo/impacto)

**Rápidos (<30 min, alto impacto relativo):**
1. Cablear el skip-link en el chrome + `id="main"` (accesibilidad AA). 🟠
2. `aria-label` en los 4 sliders de `fibonacci-collatz` (es/ca/en). 🟠
3. Añadir `frame-ancestors 'self'` a la CSP. 🟡
4. Borrar `_wtest_delete_me.txt` y refrescar `feed.xml`. 🔵

**Medios (toca build scripts):**
5. `loading="lazy"` en figuras de examen/apuntes. 🟡
6. Reordenar `<title>` de exámenes (nombre legible primero). 🟡
7. Carga condicional de KaTeX. 🟡
8. `role`/`<title>` o `aria-hidden` en los SVG de las notas. 🟡

**Largo plazo / verificación externa:**
9. Endurecer CSP (nonces, retirar `unsafe-inline`/`unsafe-eval`). 🟡
10. Confirmar CORS + auth del Worker de escritura del banco (D1). 🔵
