# Regenerar los PDFs de un examen

Los exámenes en `/aula/<materia>/examenes/<id>/` tienen tres ficheros PDF:

- `original.pdf` — escaneo histórico (con membrete del centro). **Se conserva por compatibilidad pero ya no se enlaza desde el sitio.**
- `original-enunciados.pdf` — generado desde los HTML, sin membrete del centro, sin soluciones.
- `original-soluciones.pdf` — generado desde los HTML, con las correcciones expandidas y un salto de página por pregunta.

Estos dos últimos los regenera el script `regen-exam-pdf.js`.

## Setup (una vez)

```bash
cd ~/Documents/GitHub/alexreyes.es
npm install playwright pdf-lib
npx playwright install chromium
```

KaTeX se descarga automáticamente del CDN. Si en algún momento no tienes internet, puedes usar un mirror local:

```bash
mkdir -p /tmp/katex-pkg && cd /tmp/katex-pkg
npm pack katex@0.16.9
tar -xzf katex-0.16.9.tgz
export KATEX_LOCAL_DIR=/tmp/katex-pkg/package/dist
```

## Uso — un examen concreto

```bash
node scripts/regen-exam-pdf.js . aula/eso-2/examenes/2526-2eso-u01-a
```

Genera `original-enunciados.pdf` y `original-soluciones.pdf` dentro de la carpeta.

## Uso — todos los exámenes a la vez

```bash
node scripts/bulk-regen-pdfs.js .
```

Itera sobre todas las subcarpetas de `aula/*/examenes/` que contengan ficheros `pN.html` y genera ambos PDFs por examen.

## Cuándo correrlo

- Cuando subes un examen nuevo (después de generar los `pN.html` con `build_exam_pages.py`).
- Cuando editas el contenido de los enunciados o soluciones en los HTML.
- Cuando cambias el branding del footer y quieres que los PDFs se sincronicen.

## Formato de salida

- **Enunciados**: A4, márgenes 18×16 mm, fuentes Inter/KaTeX, las preguntas fluyen continuamente.
- **Soluciones**: mismo formato pero con las correcciones expandidas y `page-break-before` por pregunta.
- Header en cada página: `alexreyes.es · <título del examen> · <fecha>`.
- Footer en cada página: `© 2026 Àlex Reyes · alexreyes.es · Página X de Y`.

## Limitaciones

- El script asume que cada examen tiene `p1.html`, `p2.html`, ... numerados. Si en el futuro la convención cambia, hay que actualizar el regex `^p\d+\.html$` en `regen-exam-pdf.js`.
- Las soluciones se extraen de la sección `.solution` o `.apart-solution`. Si una pregunta no tiene solución redactada, su sección de soluciones del PDF saldrá vacía pero la pregunta no se omite.
- Si modificas el CSS de `examenes.css` (especialmente las reglas dentro de `@media print`), revisa el output de los PDFs por si afecta al layout.
