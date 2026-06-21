# Auditoría de homogeneidad — alexreyes.es

**Fecha:** 21 jun 2026 · **Método:** escaneo directo del repo (grep/find sobre ~800 HTML), no del HTML servido.
**Alcance:** cosas hechas con estilos o estructuras distintas entre páginas que deberían ser homogéneas.
**Referencia de "lo correcto":** convenciones de `AGENTS.md` y `templates/`.

Toda cifra de este informe es un recuento real de grep. Donde un punto ya figuraba en
`auditoria-unificacion.md` (mayo) se indica si sigue vivo o está resuelto.

## Resumen ejecutivo

El sitio es muy homogéneo en lo "automatizado por scripts" (KaTeX, cache-busting CSS,
charset, viewport, favicon, fuentes, nav/footer, breadcrumb). Las inconsistencias reales
se concentran en lo que se escribe **a mano** en cada página de `/aula/`: el CSS vive
inline y duplicado en lugar de en `aula.css`, conviven dos vocabularios de clases
(español vs inglés) para el mismo componente, y el patrón de soluciones colapsables
canónico es minoritario. Ninguna es un fallo que rompa el sitio; todas son deuda de
homogeneidad que encarece evolucionar la web.

| # | Hallazgo | Severidad | Estado |
|---|---|---|---|
| 1 | `aula.css` casi sin usar; CSS inline duplicado con *drift* | Alta | Vivo |
| 2 | Doble vocabulario de clases: `.ejercicio-*` (es) vs `.exercise-*` (en) | Alta | Vivo |
| 3 | Soluciones colapsables: el patrón canónico es minoritario | Alta | Vivo |
| 4 | Botones/toolbar PDF: 3 familias para la misma acción | Media | Vivo |
| 5 | `lang="es"` en 13 exámenes con contenido catalán | Media | Vivo (de mayo) |
| 6 | Cobertura i18n de `/aula/` muy desigual | Media | Vivo |
| 7 | Naming de PDFs de examen no homogéneo + duplicados sueltos | Baja | Vivo |
| 8 | JSON de ejercicios: 3 en v2, `tipo_coleccion` sin vocabulario, `cient-2btl` huérfano | Baja | Parcial |
| 9 | `ccss-1btl` y `eso-2` sin hub `index.html` propio | Baja | Vivo (de mayo) |
| 10 | Lagunas menores de head (hreflang, og:image, viewport, fonts) | Baja | Vivo |

---

## 1. `aula.css` está casi sin usar; los estilos viven inline y duplicados — ALTA

`AGENTS.md` dice: *"Si modificas estilos visuales, edita `/assets/css/aula.css` (no inline)"*.
En la práctica ocurre lo contrario.

- `assets/css/aula.css` (17 KB) define todas las clases de convención (`.ejercicio`,
  `.seccion-aula`, `.num`, `.solucion`, `.exercise-head`, `.fitxa-toolbar`, …), pero solo
  **9 HTML de todo el sitio lo enlazan** (5 de ellos dentro de `/aula/`, sobre 357). Es,
  de hecho, casi código muerto.
- El CSS que sí cargan las páginas es `style.css` (796 archivos) + `examenes.css` (352) +
  bloques `<style>` inline.
- **210 HTML** llevan un `<style>` en el head; **797 HTML** usan `style="…"` inline
  (7 775 ocurrencias).

**Evidencia de duplicación con *drift*:** la misma regla `.exercise-head` está copiada
inline en **75 archivos** de `/aula/` (y también en `aula.css`), con tres valores
distintos del mismo margen: `margin-bottom:0.8rem` (33 archivos), `0.4rem` (14), `0.5rem`
(5). `.num` se redefine inline en **89 archivos**. Bloques `<style>` grandes que deberían
estar en la hoja: p. ej. `aula/ccss-1btl/apuntes/u-probabilitat/02-operacions-amb-conjunts.html`
(66 líneas) y `aula/ib-ai-hl/syllabus/index.html` (50).

**Decisión a tomar:** o se enlaza `aula.css` en `/aula/` y se borra el inline duplicado,
o se asume el modelo inline y se elimina `aula.css`. Hoy es lo peor de los dos mundos:
una hoja canónica que nadie carga y reglas copiadas con valores divergentes.

## 2. Dos vocabularios de clases para el mismo componente: español vs inglés — ALTA

La convención (`AGENTS.md` + `templates/ejercicio.template.html`) es española: `.ejercicio`,
`.ejercicio-cabecera`, `.num`, `<details class="solucion">` + `.solucion-cuerpo`. Pero una
gran parte del contenido usa nombres ingleses para lo mismo:

| Concepto | Clase convención (es) | Clase divergente (en) | Recuento (en) |
|---|---|---|---|
| Cabecera de ejercicio | `.ejercicio-header` (76) / `.ejercicio-cabecera` (3) | `.exercise-head` | **244** |
| Enunciado | parte de `.ejercicio-cuerpo` (79) | `.exercise-statement` | **95** |
| Intro | `.ejercicio-intro` | `.exercise-intro` | **78** |
| Tarjeta | `.ejercicio-card` (1) | `.exercise-card` | **28** |
| Cuerpo de solución | `.solucion-cuerpo` (82) | `.solution` | masivo en Cangur |

`.solution` (inglés) se usa en los exámenes Cangur en los **tres** idiomas (~14 por
archivo). No es un tema de i18n —una clase CSS no se traduce—: simplemente conviven dos
nombres para el mismo widget. El catalán no introduce un tercer vocabulario (reutiliza el
inglés/español), así que la divergencia es es-vs-en.

## 3. Soluciones colapsables: el patrón canónico es minoritario — ALTA

`AGENTS.md` cita `<details class="solucion">` como convención.

- `<details class="solucion">` → solo **10 ocurrencias**.
- El patrón dominante es `<details>` **sin clase** + `<summary>Mostrar solució</summary>` +
  `<div class="solution">` ("Mostrar solució" aparece 136 veces; 45 archivos con `<details>`
  sin clase).
- Textos del summary inconsistentes (incluso en el mismo idioma): `Mostrar solució` (129),
  `Show solution` (21), `Mostrar resolución` (7), `Mostrar resolució` (7), `Solución` (5),
  más variantes ad-hoc (`Mostrar solució dels tres apartats`, `…dels apartats clau`).
- Positivo: nadie usa un toggle JS en lugar de `<details>` para las soluciones.

## 4. Botones y toolbar de PDF: tres familias para la misma acción — MEDIA

`AGENTS.md` cita `.fitxa-toolbar` / `.fitxa-btn-primary/secondary`, pero apenas se usa
(`.fitxa-toolbar` → 3 archivos, contando el template). Conviven al menos tres familias de
botón para acciones equivalentes (ver/descargar PDF, abrir visor):

- `.fitxa-btn*` (fichas) — casi sin adopción.
- `.mx-toolbar` / `.mx-btn`, `.mx-btn-primary`, `.mx-btn-danger` (visores
  `/docencia/mi-examen/` y `/docencia/mis-apuntes/`).
- `.pdf-download` (89), `.exam-card-btn pdf` (13), `.viewer-btn cos-btn` (4) para descargar PDF.

## 5. `lang="es"` en exámenes con contenido catalán — MEDIA (ya en mayo)

Persiste el punto #2 de `auditoria-unificacion.md`. **13 exámenes** declaran
`<html lang="es">` con título, enunciados y soluciones en catalán:

- `ccss-1btl`: 11 de 12 (verificado en `2526-1btl-macs-t2p1`: "Parcial 1 — 2a avaluació").
  El único corregido a `lang="ca"` es `2526-1btl-macs-g1`.
- `eso-2`: 2 de 2 ("Fraccions i decimals").

Afecta a accesibilidad (lectores de pantalla) y SEO (clasificación de idioma).

## 6. Cobertura i18n de `/aula/` muy desigual — MEDIA

Las notas y los hubs principales están trilingües completos. El desequilibrio está en
`/aula/` (root 357 · ca 177 · en 158):

| Materia | root | ca | en |
|---|---|---|---|
| cangur | 121 | 121 | 121 |
| selectivitat | 20 | 20 | 20 |
| ccss-1btl | 133 | 21 | 16 |
| eso-2 | 31 | 14 | **0** |
| ib-ai-hl | 52 | 1 | 1 |

`en/aula/` no contiene `eso-2` en absoluto; `ib-ai-hl` está casi sin traducir (1 de 52 por
idioma). Encaja con la nota de memoria sobre la cola i18n bloqueada.

## 7. Naming de PDFs de examen no homogéneo — BAJA

Tras migrar a `index.html` + `pN.html`, los PDFs adjuntos no siguen un único esquema:

- Mayoría: `original-enunciados.pdf` + `original-soluciones.pdf`.
- `2526-1btl-macs-t3p2`: aún un único `original.pdf` sin separar.
- Cangur (los 9): `original.pdf` + `solucions.pdf` (esquema propio en catalán).
- Restos sucios probablemente accidentales: `original 2.pdf` en `2426-ib2-u12`,
  `2526-1btl-macs-g1` y `2526-1btl-macs-t2p1`; `original-clean.pdf` extra en `2526-2eso-u01-a`.

## 8. JSON de ejercicios: schema y vocabulario — BAJA (parcial)

46 ficheros en `assets/data/ejercicios/`. La unificación de mayo está casi completa
(`tags_coleccion.materia` ya casa con la carpeta; `bach-ccss-1` desapareció), pero quedan:

- **3 en `schema_version: 2`** (excluidos del índice): `2426-ib2-u14.json` y
  `2426-ib2-u15.json` (v2 real, con `descriptor_ib` antiguo y sin `tags_coleccion.materia`)
  y `2526-1btl-macs-g1.json` (stub deprecado a propósito). Nota: mayo listaba u14/u15 como
  v3 — hoy están en v2 (reclasificación o regresión).
- `tipo_coleccion` sin vocabulario controlado: conviven `examen`, `examen_practica`,
  `practica`, `deures`, `ficha`, `apuntes_concepto`.
- Abreviatura nueva `cient-2btl` (en `pau-2026-mate-s1.json`) que **no casa con ninguna
  carpeta** y rompe el patrón de identificadores.

## 9. `ccss-1btl` y `eso-2` sin hub propio — BAJA (ya en mayo)

IB tiene `unidades/`, `syllabus/`, `apuntes/index.html`; selectivitat y cangur tienen hub
propio. Pero `ccss-1btl` y `eso-2` siguen sin un `index.html` que liste sus unidades.

## 10. Lagunas menores del `<head>` — BAJA

- **hreflang**: 38 páginas tienen bloque `es`+`ca`+`x-default` pero **sin `hreflang="en"`**
  (no existe su espejo `/en/`): `aula/ccss-1btl/apuntes/u-probabilitat/` y
  `aula/eso-2/apuntes/{u-cossos-revolucio,u-fraccions}/`, duplicadas en `/ca/`.
- **og:image** ausente en las notas `fibonacci-collatz` y `el-hombre-y-la-nota-al-margen`
  (las 3 versiones de cada una). En el caso de `fibonacci-collatz` es decisión documentada
  en `AGENTS.md` (nota sin héroe de calidad); conviene confirmar si la otra también lo es.
- **viewport outlier**: `doctorado/visualizaciones/mod3-preview.html` usa `initial-scale=1`
  frente a `initial-scale=1.0` del resto.
- **Google Fonts reducida**: 2 páginas cargan solo `Inter` (sin `JetBrains Mono`) frente al
  set estándar de 1 589.
- **Páginas técnicas incompletas** (no de contenido, pero conviene saberlo):
  `editor/index.html` (sin canonical/og:title/og:image/twitter:card/description) y
  `doctorado/visualizaciones/mod3-preview.html` (sin description ni rel=icon).
- **Doc stale**: `aula/ib-ai-hl/README.md` describe un `examenes.json` único que ya no
  existe (hoy es un JSON por examen + índice generado).

---

## Qué NO es inconsistencia (verificado y limpio)

- **KaTeX**: versión única `0.16.9`, CDN único (`cdn.jsdelivr.net`), SRI correcto; carga
  simétrica (705 páginas cargan css = js = auto-render).
- **Cache-busting CSS**: un único `?v=202606162226` en todo el sitio.
- **charset / viewport / favicon**: uniformes (salvo los outliers de §10).
- **Breadcrumb**: 790 archivos con `class="breadcrumb"`, separador `/` único (2 760×).
- **nav / footer**: homogéneos incluso entre root, `/ca/` y `/en/`.
- **Naming de carpetas y plantilla de examen**: unificados desde mayo (`apuntes/ejercicios/
  examenes` en todas las materias; todos los exámenes en `index.html` + `pN.html`).

## Orden de ataque sugerido

1. Resolver §1 (decidir `aula.css` vs inline) — desbloquea poder unificar el resto desde un
   sitio único en vez de en cientos de páginas.
2. §2 y §3 juntos: normalizar `.exercise-*`/`.solution` ↔ `.ejercicio-*`/`.solucion` y el
   texto del `<summary>`. Es donde más páginas (sobre todo Cangur) divergen.
3. §5 (lang en 13 exámenes) y §7 (PDFs sueltos `original 2.pdf`): arreglos rápidos y acotados.
4. §6 (cobertura i18n) es el más grande pero es trabajo de contenido, no de homogeneidad de
   código; tratarlo aparte.
