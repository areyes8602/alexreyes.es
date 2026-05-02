# Auditoría de unificación — alexreyes.es / aula

**Fecha**: 2 de mayo de 2026
**Alcance**: estructura, plantillas, CSS, JSON y naming bajo `/aula/{materia}/` para `ib-ai-hl`, `ccss-1btl` y `eso-2`.

## Resumen ejecutivo

Las tres materias actuales se han ido construyendo en momentos distintos y con criterios distintos. El resultado es que **el mismo concepto pedagógico (un apunte, una ficha, un ejercicio, una solución) está implementado de tres formas diferentes**, lo que impide compartir templates, scripts y CSS, y obliga a mantener tres ramas paralelas cuando se quiere evolucionar la web.

La buena noticia: las divergencias son **superficiales** (naming, idioma del HTML, ubicación de estilos, esquema de tags), no estructurales. Se pueden unificar en 5 fases incrementales sin tocar el contenido.

La oportunidad: una vez unificado, **añadir una nueva materia** (CCFF, otra promoción de IB, 3º o 4º ESO) será reutilizar templates en lugar de copiar-pegar HTML.

## Estado actual — mapa por materia

|                     | `ib-ai-hl` | `ccss-1btl` | `eso-2` |
|---------------------|------------|-------------|---------|
| **Carpetas**        | `conceptos/`, `fichas/`, `examenes/`, `unidades/`, `syllabus/` | `apuntes/`, `fitxes/`, `examenes/`, `exercicis-classe/` | `apuntes/`, `examenes/` |
| **Idioma carpetas** | español (neutral) | catalán | catalán |
| **Idioma HTML apuntes** | `lang="es"` | `lang="ca"` | `lang="ca"` |
| **Idioma HTML exámenes** | `lang="es"` | `lang="es"` ⚠ (contenido en catalán) | `lang="es"` ⚠ (contenido en catalán) |
| **Hub por materia** | `unidades/` (template universal con hash routing) | no hay | no hay |
| **JSON `tags_coleccion.materia`** | `ib-ai-hl` | `bach-ccss-1` | `eso-2` |
| **Schema JSON ejercicios** | mezcla v2 (exámenes legacy) y v3 (apuntes/ficha nuevos) | v3 (con 1 archivo v2 deprecated) | v3 |
| **Tags curriculares** | `concepto_iba` (NM/TANS) | `concepto_bach` | `concepto_eso` |
| **CSS de exámenes** | `/assets/css/examenes.css` | `/assets/css/examenes.css` | `/assets/css/examenes.css` |
| **CSS de apuntes** | inline en cada `index.html` | inline + `examenes.css` | inline + `examenes.css` |
| **Plantilla de apuntes** | tipo "concepto" (NM 3.6) con secciones Teoría/Ejemplos/GeoGebra/Ejercicios | tipo "unidad" larga (`u-equacions-sistemes`) | tipo "unidad" larga |
| **Plantilla de ficha** | `/fichas/voronoi/` con TOC + 5 ejercicios + soluciones desplegables | `/fitxes/u-…/` con varios ejercicios y soluciones | no existe |
| **Plantilla de ejercicios de clase** | no existe | `/exercicis-classe/2526-1btl-macs-u01-classe/` | no existe |
| **Plantilla de examen** | `/examenes/{exam}/p1.html` (una pregunta por archivo) | `/examenes/{exam}/index.html` (todo en uno) | `/examenes/{exam}/index.html` (todo en uno) |
| **Soluciones** | `<details>` inline en apuntes y fichas; PDFs + HTML por pregunta en exámenes | `<details>` inline en apuntes/fitxes; un solo PDF en exámenes | igual que CCSS |
| **Breadcrumb** | sí (con sep `/`) | sí | sí |
| **IBO disclaimer** | sí | no aplica | no aplica |

## Catálogo de incongruencias

### 1. Naming de carpetas: `fichas` vs `fitxes`, `apuntes` vs `conceptos`

- IB tiene `/conceptos/{NM-3-6}/` (un apunte por subtema del syllabus IB) **y** `/fichas/{voronoi}/` (recopilación temática).
- CCSS tiene `/apuntes/{u-equacions-sistemes}/` (un apunte por unidad) **y** `/fitxes/{u-eq-exponencials-logaritmiques}/`.
- ESO solo tiene `/apuntes/{u-fraccions}/`.

El mismo concepto editorial (recopilación de ejercicios sobre un tema) está en `/fichas/` para IB y en `/fitxes/` para CCSS. Cualquier script que recorra "fichas" se rompe en CCSS.

### 2. Lang del HTML mal puesto en exámenes

Los archivos `/aula/ccss-1btl/examenes/*/index.html` y `/aula/eso-2/examenes/*/index.html` declaran `<html lang="es">` pero el contenido está en catalán (títulos, enunciados, soluciones). Esto rompe accesibilidad (lectores de pantalla pronuncian mal) y SEO (Google puede malclasificar el idioma).

### 3. Schema JSON mezclado en IB

Los exámenes IB del banco antiguo (`2426-ib2-u9.json`, `2426-ib2-u10.json`, `2426-ib2-u12.json`, `2426-ib2-g1-p3.json`, `2426-ib2-g2-p1p2.json`) están en `schema_version: 2`, sin `tags_coleccion.materia`, con tags `descriptor_ib` (formato antiguo). Los nuevos (`2426-ib2-u13.json`, `2426-ib2-u14.json`, `2426-ib2-u15.json`, `concepto-nm-3-6.json`, `ficha-voronoi.json`) usan `schema_version: 3` con `concepto_iba`.

El script `build_ejercicios.py` filtra por `sv >= 3`, así que **5 colecciones de exámenes IB no están indexadas** y no aparecen en los listados automáticos del syllabus ni de las unidades.

### 4. CSS duplicado y residual

- `/assets/css/gate.css` sigue en el repo (119 bytes), pese a haberse "borrado" en una sesión anterior junto con `gate.js`. Si `_redirects` bloquea `/editor/`, el CSS de gating es residuo muerto.
- Existen `/assets/css/examenes.css` (11 KB) **y** `/assets/css/mi-examen.css` (11 KB), tamaños casi idénticos. El segundo parece un fork sin uso vivo.
- Los apuntes y fichas de IB (`/conceptos/NM-3-6/` y `/fichas/voronoi/`) tienen ~150 líneas de CSS **inline en `<style>`** dentro del `<head>`. CCSS y ESO no tienen esos estilos: usan clases tipo `.exercise`/`.solution` en `examenes.css`.

### 5. Clases CSS distintas para lo mismo

Comparando un ejercicio en una ficha de IB (`/fichas/voronoi/`) con un ejercicio en una fitxa de CCSS (`/fitxes/u-eq-exponencials-logaritmiques/`):

| Elemento | IB ficha | CCSS fitxa |
|----------|----------|-----------|
| Contenedor del ejercicio | `.ejercicio` | `.exercise` |
| Cabecera | `.ejercicio-header` | `.exercise-head` |
| Número | `.ejercicio-num` | (sin clase, dentro de `<h3>`) |
| Solución | `<details class="solucion">` | `<details>` con `.solution` interna |
| Tags | `.ej-tags` + `.ej-tag` | (no hay sistema de tags en HTML) |

Resultado: dos hojas de estilos paralelas, dos formas de marcar el HTML, ningún componente reutilizable.

### 6. Hub centralizado solo en IB

`/aula/ib-ai-hl/unidades/index.html` es un template universal que carga `ib-unidades.json`, lee `#u02-...` del hash, y renderiza la unidad. Esa misma idea no existe en CCSS ni en ESO: cada unidad tiene su carpeta y `index.html` propio, sin un punto de entrada que liste todas. Para añadir una unidad nueva en CCSS toca crear un HTML nuevo a mano; en IB basta añadir una entrada al JSON.

### 7. Plantillas de examen divergentes

- IB: cada pregunta en su archivo (`p1.html`, `p2.html`...), enlazadas desde `index.html` que es el hub del examen. Permite compartir/enlazar preguntas individuales.
- CCSS y ESO: una sola página `index.html` con todas las preguntas concatenadas. No se puede enlazar a una pregunta concreta y los PDF de soluciones son únicos por examen.

Con la migración reciente (Playwright + `original-enunciados.pdf` / `original-soluciones.pdf`), IB tiene PDFs separados; CCSS y ESO siguen con `original.pdf` único.

### 8. Tags curriculares de tres tipos

- IB: `concepto_iba` (NM 3.5, NM 3.6, TANS 1.12...) — referidos al syllabus IBO oficial.
- CCSS: `concepto_bach` (BACH-numeros-reales...) — esquema propio.
- ESO: `concepto_eso` (ESO-fracciones...) — otro esquema propio.

Es razonable que cada nivel tenga su taxonomía, pero los tres se almacenan en `tags.json` como namespaces independientes y el frontend los trata por separado. No hay un concepto compartido (por ejemplo, "geometría coordenada" cruza IB-NM-3.5, CCSS-BACH-geometria, ESO-geometria) — un alumno o profesor que busca por tema atraviesa fronteras y la web no le ayuda.

### 9. Metaetiquetas SEO desiguales

Los exámenes IB tienen `<meta property="og:type">`, `og:url`, `og:title`, `og:description`, `og:image`, `twitter:card`. Los exámenes CCSS no las tienen, los de ESO sí pero con valores genéricos. Lo mismo con `<link rel="canonical">`.

### 10. Naming en `tags_coleccion.materia`

- IB: `ib-ai-hl` (kebab-case con guiones)
- CCSS: `bach-ccss-1` (mismo estilo)
- ESO: `eso-2` (corto)

Pero las **carpetas** son `ib-ai-hl`, `ccss-1btl` (no `bach-ccss-1`), `eso-2`. La materia en JSON y la URL no coinciden en CCSS, lo cual rompe cualquier mapeo automático.

## Esquema unificado propuesto

### Estructura de directorios canónica

```
/aula/{materia}/
  apuntes/                    ← nombre único, no "conceptos" ni "fitxes"
    {slug}/index.html         ← una "página de apunte" por unidad o concepto
  ejercicios/                 ← reemplaza "fichas", "fitxes" y "exercicis-classe"
    {slug}/index.html         ← una "ficha" o "hoja de clase"
  examenes/
    {exam-id}/
      index.html              ← hub del examen
      p1.html, p2.html, ...   ← una pregunta por archivo (estándar IB)
      original-enunciados.pdf
      original-soluciones.pdf
  unidades/index.html         ← hub universal con hash routing (como IB)
  syllabus/index.html         ← solo IB; en otras materias puede no existir
```

Materias: `ib-ai-hl`, `ib-ai-sl` (futuro), `ccss-1btl`, `ccss-2btl` (futuro), `cientific-1btl`, `cientific-2btl`, `eso-2`, `eso-3`, `eso-4`...

### Schema JSON único

`schema_version: 3` para todas las colecciones. Campos obligatorios:

```json
{
  "schema_version": 3,
  "id": "{materia}-{coleccion}",
  "tipo_coleccion": "examen" | "ficha" | "apuntes_concepto" | "apuntes_unidad" | "ejercicios_clase",
  "titulo": "...",
  "fecha": "YYYY-MM-DD",
  "promocion": "all" | "YYYY-YYYY",
  "url_index": "/aula/{materia}/...",
  "puntuacion_total": N,
  "tags_coleccion": {
    "materia": "{materia}",
    "curso_academico": "YYYY-YYYY",
    "idioma": "es" | "ca" | "en",
    "fuente": "propia",
    "origen": "examen" | "classe" | "selectivitat",
    "ambito_iba": "..." (solo IB) | "ambito_bach": "..." | "ambito_eso": "..."
  },
  "ejercicios": [...]
}
```

Migrar los **5 exámenes IB legacy** de v2 a v3 para que entren en el índice automático.

### Plantilla HTML universal

Una sola plantilla por tipo de página (apunte, ficha, pregunta de examen, hub) con estos invariantes:

- `<html lang="{idioma_real_del_contenido}">` (no copiar `es` por defecto)
- Head idéntico: KaTeX 0.16.9 con SRI + `crossorigin`, fonts Google, theme script, `style.css`
- Nav idéntica
- Breadcrumb con la misma estructura: `Inicio / Docencia / {Materia} / {Sección} / {Item}`
- Footer idéntico
- IBO disclaimer **solo** en páginas IB
- OG tags + canonical en todas

### CSS unificado

Crear `/assets/css/aula.css` (~ 4–5 KB) con las clases compartidas:

```
.card-header, .card-meta, .card-tag, .card-title, .card-intro
.seccion (con h2 propio)
.ejercicio, .ejercicio-header, .ejercicio-num, .ejercicio-puntos, .ejercicio-cuerpo
.solucion (sobre <details>), .solucion-cuerpo
.apartado, .apartado-letra, .apartado-pts
.ej-tags, .ej-tag, .ej-tag.dif
.libro-nav, .libro-nav-item
.info-box (variantes amarillo, azul)
```

Eliminar:
- `gate.css` (residual)
- `mi-examen.css` (parece fork muerto, hay que verificar)
- Estilos inline en `/conceptos/NM-3-6/` y `/fichas/voronoi/`: migrarlos a `aula.css`

### Hub universal por materia

`/aula/{materia}/unidades/index.html` con la misma lógica que IB hoy, leyendo `/{materia}-unidades.json`. Para CCSS y ESO crear el equivalente a `ib-unidades.json` con sus unidades y tags curriculares.

### Idioma estructurado

- Carpetas en español (neutral): `apuntes`, `ejercicios`, `examenes`. Ya son lengua-neutras.
- Atributo `<html lang>` siempre coherente con el contenido del archivo.
- Título visible y meta descripción en el idioma del contenido.

## Plan de migración por fases

### Fase 1 — Limpieza (1 sesión, no rompe nada)

1. Borrar `/assets/css/gate.css`.
2. Verificar si `mi-examen.css` se usa en alguna página; si no, borrar.
3. Migrar los 5 exámenes IB de schema v2 a v3 (añadir `tags_coleccion.materia: "ib-ai-hl"` + reformatear `descriptor_ib` → `concepto_iba` + `puntuacion_total`).
4. Corregir `<html lang="ca">` en exámenes CCSS y ESO cuyo contenido sea catalán.
5. Renombrar `tags_coleccion.materia` de CCSS de `bach-ccss-1` a `ccss-1btl` (alinear con la URL).
6. Re-correr `build_ejercicios.py` y verificar que los 5 exámenes IB legacy entran al índice.

### Fase 2 — CSS unificado (1 sesión)

1. Crear `/assets/css/aula.css` con las clases compartidas.
2. Migrar los estilos inline de `/conceptos/NM-3-6/` y `/fichas/voronoi/` a `aula.css`.
3. Renombrar clases de CCSS (`.exercise` → `.ejercicio`, `.solution` → `.solucion`, `.exercise-head` → `.ejercicio-header`) con un script de búsqueda y reemplazo en HTML y en `examenes.css`.
4. Verificar que todas las páginas siguen renderizando idénticas (smoke test visual).

### Fase 3 — Renombrado de carpetas y schema (1–2 sesiones)

1. Renombrar `/aula/ccss-1btl/fitxes/` → `/aula/ccss-1btl/ejercicios/`. Actualizar `url_index` y `url_enunciado` en los JSON afectados. Añadir 301 en `_redirects`.
2. Renombrar `/aula/ccss-1btl/exercicis-classe/` → `/aula/ccss-1btl/ejercicios/` (fusión con la anterior, IDs siguen únicos).
3. Renombrar `/aula/ib-ai-hl/fichas/` → `/aula/ib-ai-hl/ejercicios/`. Idem redirects.
4. Renombrar `/aula/ib-ai-hl/conceptos/` → `/aula/ib-ai-hl/apuntes/`. Idem redirects.
5. Re-correr `build_ejercicios.py`.

### Fase 4 — Templates universales (2–3 sesiones)

1. Construir el template universal de "página de apunte" en `/aula/{materia}/apuntes/{slug}/index.html` con la misma estructura semántica para los tres tipos (concepto IB, unidad CCSS, unidad ESO).
2. Templates universales de "ficha" y "página de pregunta de examen".
3. Construir hub universal `/aula/{materia}/unidades/index.html` para CCSS y ESO.
4. Crear `/assets/data/ccss-1btl-unidades.json` y `/assets/data/eso-2-unidades.json` con la estructura de cada materia.

### Fase 5 — i18n y SEO (1 sesión)

1. Añadir OG tags + canonical a todas las páginas de CCSS.
2. Establecer `<html lang>` correcto en todas las páginas.
3. (Opcional) Versiones `/ca/` y `/en/` de las páginas IB existentes (ya hay `/ca/` y `/en/` en docencia, pero no en aula).

## Decisiones que necesitan tu OK

Antes de empezar, conviene que decidas:

1. **¿`fichas` o `ejercicios` como nombre canónico de carpeta?** Mi recomendación: `ejercicios/` (más descriptivo y unificable con `exercicis-classe`).
2. **¿`apuntes` o `conceptos` como nombre canónico?** Mi recomendación: `apuntes/` (más estándar; en IB el slug puede ser `NM-3-6` sin que la carpeta padre sea "conceptos").
3. **¿Migramos los 5 exámenes IB legacy a v3, o los dejamos invisibles al índice automático?** Recomendación: migrar.
4. **¿Mantenemos `mi-examen.css`?** Necesito que confirmes para borrarlo.
5. **¿Apoyamos `/ca/` para las páginas de aula?** Solo si tiene sentido pedagógicamente (alumnos catalanes), no por completar features.
6. **Orden de fases**: ¿quieres ejecutar las 5 en serie, o priorizar lo que tenga más impacto inmediato (fase 1 + 2 desbloquean la mayoría de los problemas con bajo riesgo)?

Una vez me confirmes 1–6, ejecuto la fase 1 sin tocar nada más, te enseño el diff, y avanzamos por fases.
