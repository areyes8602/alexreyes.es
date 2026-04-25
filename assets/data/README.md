# Base de datos de ejercicios — guía rápida

Versión actual del esquema: **`schema_version: 3`**.

## Estructura

```
assets/data/
├── tags.json                     # Taxonomía de etiquetas (la fuente de verdad)
├── ejercicios/
│   ├── _TEMPLATE.json.disabled   # Plantilla para nuevos exámenes (ignorada por el build)
│   ├── 2426-ib2-u9.json          # ⏭ Ignorada (schema_version 2, anticuada)
│   └── ...
└── ejercicios-index.json         # Generado por scripts/build_ejercicios.py
```

El build **ignora** colecciones con `schema_version < 3` (las generadas previamente con etiquetas inventadas). Quedan en disco como referencia/backup hasta que decidas borrarlas o migrarlas.

## Filosofía de etiquetas

Cada ejercicio tiene **una materia** (ej. `ib-ai-hl`, `bach-ccss-1`, `eso-2`...). Según la materia, se usan los namespaces de **ámbito** y **concepto** correspondientes:

| Materia | Ámbito | Concepto |
|---|---|---|
| IB AI HL/SL | `ambito_iba` (5 temas oficiales) | `concepto_iba` (NM/TANS) |
| Bachillerato (LOMLOE) | `ambito_bach` (Sentido numérico, algebraico, …) | `concepto_bach` (Ecuaciones de 1º grado, Derivadas, …) |
| ESO (LOMLOE) | `ambito_eso` (Sentido numérico, …) | `concepto_eso` (Pitágoras, Sistemas, …) |

Etiquetas **comunes a todas las materias**: `dificultad`, `habilidad`, `formato`, `idioma`, `fuente`, `curso_academico`.

Cada ejercicio puede tener **varios conceptos** (un problema de cinemática IB puede tener `TANS 3.10`, `TANS 3.12` y `TANS 5.10`). Eso permite filtros del tipo "ejercicios con autovalores **y** Markov" o "ejercicios fáciles de derivadas que sean problemas aplicados".

## Cómo añadir un examen

1. Copia `_TEMPLATE.json.disabled` a `<id-coleccion>.json` (ej. `2526-2eso-u4.json`).
2. Rellena los campos. Para los enunciados, escribe el **texto real completo** del problema en `tarea` (no resúmenes).
3. Pon todas las etiquetas que apliquen, especialmente `materia`, `ambito_*` y `concepto_*`.
4. Coloca el PDF original (si lo tienes) en `aula/<carpeta>/original.pdf`.
5. Si vas a hacer páginas de enunciado HTML por pregunta (`p1.html`, `p2.html`...), crea la carpeta y los archivos.
6. Ejecuta:
   ```bash
   python3 scripts/build_ejercicios.py    # valida y genera el índice
   python3 scripts/build_exam_pages.py    # genera el index.html del examen
   python3 scripts/build_sitemap.py       # actualiza sitemap
   ```
7. Commit + push.

## Códigos NM y TANS oficiales del IB

Están en `tags.json` bajo `concepto_iba`. NM = Nivel Medio (= SL), TANS = Temas Adicionales del Nivel Superior (HL extra). Consulta el syllabus oficial para descripciones detalladas.

## Conceptos LOMLOE de Bachillerato y ESO

Definidos en `tags.json` bajo `concepto_bach` y `concepto_eso`. Se incluyen los conceptos estándar del currículo. Si te falta alguno, añádelo a `tags.json` y vuelve a ejecutar el build.

## Validaciones automáticas del build

- IDs de ejercicios únicos
- Suma de puntos de apartados = `puntuacion` del ejercicio
- Suma de `puntuacion` de ejercicios = `puntuacion_total` de la colección
- Tags usados existen en la taxonomía
- URLs apuntan a ficheros existentes (warnings)
