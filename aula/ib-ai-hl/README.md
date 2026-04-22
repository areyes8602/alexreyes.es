# /aula/ib-ai-hl/ — banco de exámenes IB Mathematics AI HL

Módulo del sitio donde se publican los exámenes con enunciado, corrección paso a paso y etiquetado curricular. Servirá de semilla para un futuro generador automático de exámenes (phase 2).

## Convención de IDs

Cada examen tiene un identificador único que se usa como:
- carpeta bajo `/aula/ib-ai-hl/examenes/`
- `id` en `examenes.json`
- prefijo de los IDs de preguntas

Formato: `<CURSO>-<GRUPO>-<UNIDAD>`
- `<CURSO>`: cuatro dígitos abreviados del curso académico (p. ej. `2526` = 2025-2026, `2426` = 2024-2026 si se refiere a la promoción).
- `<GRUPO>`: `ib1`, `ib2`, `ccss1`, `2eso`, etc.
- `<UNIDAD>`: `u01`, `u13`, `final`, `rec`, `ia`, etc.

**Ejemplos:**
- `2426-ib2-u13` — examen de la unidad 13 impartido a IB2 durante el curso 2025-26 (promoción 2024-2026)
- `2526-ib1-u05` — examen unidad 5 de IB1 curso 2025-26
- `2526-2eso-final` — examen final 2n ESO curso 2025-26

Los IDs de pregunta se forman añadiendo `-pN`:
- `2426-ib2-u13-p1`, `2426-ib2-u13-p2`, …

## Estructura de archivos de un examen

```
/aula/ib-ai-hl/examenes/<ID>/
├── index.html        Portada: baremo, metadatos, 4 tarjetas de pregunta
├── p1.html           Pregunta 1 (enunciado + corrección en toggle)
├── p2.html
├── p3.html
├── p4.html           …tantas como tenga el examen
└── original.pdf      (opcional) PDF original del examen
```

Los recursos compartidos se mantienen en:
```
/assets/css/examenes.css    estilos del módulo (chips IB, toggle, tablas, print)
/assets/js/examenes.js      toggle de correcciones + re-render KaTeX
/assets/data/examenes.json  base de datos
```

## Cómo añadir un nuevo examen

1. **Decide el ID** según la convención (`<CURSO>-<GRUPO>-<UNIDAD>`).
2. **Crea la carpeta** `/aula/ib-ai-hl/examenes/<ID>/`.
3. **Duplica** un examen existente (p. ej. `2426-ib2-u13`) como plantilla y edita:
   - `index.html`: título, fecha, metadatos, baremo, lista de preguntas con descriptores y chips IB.
   - `pN.html` por cada pregunta: enunciado en LaTeX (KaTeX), etiquetas IB con tooltips, y corrección dentro del `<section class="solution" id="sol-pN" hidden>`.
4. **Actualiza `/assets/data/examenes.json`** añadiendo una entrada al array `examenes` con el mismo esquema. Cada pregunta debe incluir: `id`, `numero`, `descriptor`, `puntuacion`, `apartados` (array con letra, puntos y tarea), `etiquetas_ib`, `tipo`, `dificultad`, `url`.
5. **(Opcional)** copia el PDF original a la carpeta como `original.pdf`; el botón de descarga de la portada ya apunta allí.
6. **Enlaza** el examen desde `/docencia/ib-ai/2024-2026/` (o la promoción que corresponda) en la sección de exámenes anteriores de cada capítulo relevante.

## Etiquetado curricular IB AI HL

Las etiquetas siguen los códigos de la guía oficial del IB (Mathematics: Applications and Interpretation HL). Los descriptores textuales están en `examenes.json` bajo `_descriptores_ib` y se muestran como tooltip al pasar el cursor sobre cada chip.

Códigos usados actualmente (ampliar según se añadan exámenes):
- `TANS 1.14` — Álgebra matricial
- `TANS 1.15` — Valores y vectores propios
- `TANS 3.10` — Vectores: componentes, representación por columnas
- `TANS 3.12` — Vectores aplicados a cinemática; proyectil
- `TANS 5.16` — Método de Euler y sistemas acoplados
- `TANS 5.17` — Retratos de fase y puntos de equilibrio
- `TANS 5.18` — EDOs de 2º orden reducidas a sistema

Al añadir un código nuevo, mete el descriptor en la sección `_descriptores_ib` del JSON y úsalo como valor de `data-descriptor` en el chip HTML para que se muestre el tooltip.

## Renderizado matemático

Las páginas usan **KaTeX** por CDN (coherente con el resto del sitio). Sintaxis soportada:
- inline: `$...$` o `\(...\)`
- display: `$$...$$` o `\[...\]`

El script `examenes.js` re-tipografía el bloque `.solution` la primera vez que se despliega mediante `renderMathInElement(element)`. Si prefieres MathJax en un examen concreto, sustituye los dos `<script defer>` de KaTeX por los de MathJax y cambia la llamada a `MathJax.typesetPromise([sol])` en `toggleSolucion`.

## Interactividad

- **Toggle de corrección**: botón `.solution-toggle` con `data-toggles="sol-pN"` que oculta/muestra la `<section class="solution" id="sol-pN" hidden>`. El texto del botón alterna entre "Mostrar" y "Ocultar".
- **Preferencia persistente** (opcional): `setSolutionsDefault(true)` guarda en `localStorage` que todas las correcciones se desplieguen por defecto al cargar la página. Útil para impresión o revisión masiva.
- **Impresión**: `@media print` muestra todas las correcciones desplegadas y oculta navegación, botones y footer, produciendo un documento listo para imprimir con enunciado + solución de cada pregunta en su propia página.

## Roadmap — hacia el generador de exámenes (phase 2)

El JSON `examenes.json` está diseñado para ser la **semilla de la base de datos** del futuro generador. La progresión prevista:

1. **Inventario** (estado actual): cada pregunta ya está etiquetada con códigos IB, tipo, dificultad, apartados y URL. A partir de unas decenas de exámenes tendremos una base indexable.
2. **Listado dinámico**: página `/aula/ib-ai-hl/banco/` que lee `examenes.json` y genera una tabla filtrable por etiqueta IB, tipo, dificultad, año.
3. **Selector de ejercicios**: a partir del listado, seleccionar preguntas y componer un examen personalizado a partir del enunciado reutilizado.
4. **Generador con plantilla**: cada pregunta del banco lleva asociado un "tipo" (p. ej. "proyectil") y una plantilla parametrizable (ángulo, velocidad, g). El generador instancia la plantilla con valores aleatorios dentro de rangos razonables, produce el enunciado y la corrección automática.
5. **Export LaTeX/PDF**: impresión en formato examen clásico con pie y baremo.

Para que la phase 2 sea factible, al crear cada examen hay que mantener la calidad y detalle de los campos `tipo`, `etiquetas_ib`, `dificultad` y `apartados` del JSON &mdash; son los que permitirán búsquedas eficientes en el banco.

## Convenciones de estilo

- Usar los tokens de color del sitio principal (`var(--text)`, `var(--bg)`, etc.) definidos en `/style.css`. El tema oscuro funciona automáticamente.
- Los chips IB usan un violeta sobrio con tooltip al hacer hover.
- El bloque de corrección lleva borde izquierdo verde (`#059669`) para distinguirlo visualmente del enunciado.
- Título de pregunta con `h1`, apartados dentro de `.apartado-sol` con un `h4` que lleva una "letra" a)/b)/c) tipográfica.
- Formato numérico europeo: comas decimales (`3{,}15`) y puntos como separador de miles donde aplique.
