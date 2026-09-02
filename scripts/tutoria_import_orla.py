#!/usr/bin/env python3
"""Importa una orla del centro (PDF) a la base de datos de tutoría.

IMPORTANTE — dónde acaban los datos
-----------------------------------
Este script NO escribe nada dentro del repositorio. Los nombres y las fotos
de los alumnos son datos personales de menores y el repositorio es público:
el destino son Cloudflare D1 (fichas) y R2 (fotos), ambos privados y
servidos solo a través de /tutoria/api/, que exige sesión.

El directorio de salida por defecto es un temporal fuera del repo. Si le
pasas uno propio, elígelo también fuera: .gitignore cubre los nombres
habituales, pero no cuentes con ello.

Uso
---
    python3 scripts/tutoria_import_orla.py Orla_2ESO_E.pdf \
        --grup 2ESO-E --curs 2026-27 [--out DIR] [--dry-run]

Genera en DIR:
    alumnes.sql       INSERTs para D1
    fotos/<id>.jpg    una por alumno con foto
    subir.sh          los dos comandos de wrangler que faltan

Después:
    npx wrangler d1 execute tutoria --remote --file=scripts/sql/tutoria_schema.sql
    bash DIR/subir.sh

Formato de orla soportado
-------------------------
La "Orla H" de Untis/SAGA: rejilla de 5 columnas × 6 filas, numerada por
columnas (1-6 la primera, 7-12 la segunda…). Cada celda lleva el nº, el
grupo, los apellidos y el nombre, con la foto a la derecha. Los alumnos
sin foto simplemente no tienen imagen en esa celda.
"""
import argparse
import re
import shutil
import sys
import tempfile
import unicodedata
from pathlib import Path

try:
    from pypdf import PdfReader
except ImportError:
    sys.exit("Falta pypdf:  pip install pypdf")

FILES_PER_COL = 6
COLS = 5


def slug(text):
    """Slug ASCII estable a partir de 'Apellidos Nombre'."""
    t = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode()
    t = re.sub(r"[^a-zA-Z0-9]+", "-", t).strip("-").lower()
    return re.sub(r"-{2,}", "-", t)


def read_cells(page):
    """Devuelve {nº alumno: {'cognoms', 'nom', 'marca'}} leyendo posiciones.

    Cada celda de la orla es: el número de lista a la izquierda y, justo
    debajo, una o más líneas de apellidos y una última con el nombre. Las
    filas están separadas por un paso constante, que deducimos de los
    propios números en vez de fijarlo.
    """
    toks = []

    def visit(text, cm, tm, font, size):
        s = text.strip()
        if s:
            toks.append((round(tm[4]), round(tm[5]), s))

    plano = page.extract_text() or ""
    page.extract_text(visitor_text=visit)
    if not toks:
        sys.exit("No se ha podido leer texto del PDF.")

    # La marca del grupo ("2ESO-E (R)") se dibuja sin posición utilizable,
    # así que la sacamos del texto en orden de lectura: "23 2ESO-E (R)".
    marcas = {int(n): f"({m})"
              for n, m in re.findall(r"(\d{1,2})\s+\S*ESO\S*\s*\((\w)\)", plano)}

    # Números de lista: tokens puramente numéricos dentro del rango de la orla.
    nums = sorted(
        ((x, y, int(t)) for x, y, t in toks
         if t.isdigit() and 1 <= int(t) <= COLS * FILES_PER_COL),
        key=lambda r: r[2],
    )
    if len(nums) < 2:
        sys.exit("No se han encontrado números de alumno; ¿es una orla 'H'?")

    # Paso vertical entre filas: la menor distancia positiva entre dos
    # números de la misma columna.
    ys_por_col = {}
    for x, y, n in nums:
        ys_por_col.setdefault(x, []).append(y)
    saltos = [b - a for ys in ys_por_col.values()
              for a, b in zip(sorted(ys), sorted(ys)[1:]) if b > a]
    paso = min(saltos) if saltos else 3000

    cells = {}
    for nx, ny, n in nums:
        # El nombre cuelga por debajo del número (y creciente) y a su derecha,
        # sin llegar a la columna siguiente.
        linies = sorted(
            ((y, t) for x, y, t in toks
             if nx < x < nx + paso and ny < y < ny + paso and not t.isdigit()),
            key=lambda r: r[0],
        )
        textos = [t for _, t in linies]
        if len(textos) < 2:
            continue
        cells[n] = {
            "cognoms": " ".join(textos[:-1]),
            "nom": textos[-1],
            "marca": marcas.get(n, ""),
        }
    return cells


def read_photos(page):
    """Devuelve {nº alumno: nombre de XObject} usando la posición de cada imagen."""
    raw = page.get_contents().get_data().decode("latin-1")
    placed = re.findall(
        r"q\s+([-\d.]+) 0 0 ([-\d.]+) ([-\d.]+) ([-\d.]+) cm\s*/(\w+) Do", raw
    )
    if not placed:
        return {}

    boxes = [(float(x), float(y), float(w), abs(float(h)), n) for w, h, x, y, n in placed]
    # El logo del centro tiene otras proporciones: nos quedamos con el tamaño
    # que más se repite, que es el de las fotos de alumno.
    from collections import Counter
    common = Counter((round(w), round(h)) for x, y, w, h, n in boxes).most_common(1)[0][0]
    photos = [b for b in boxes if (round(b[2]), round(b[3])) == common]

    xs = sorted({round(b[0]) for b in photos})
    ys = sorted({round(b[1]) for b in photos})
    out = {}
    for x, y, w, h, name in photos:
        col = min(range(len(xs)), key=lambda i: abs(xs[i] - x))
        row = min(range(len(ys)), key=lambda i: abs(ys[i] - y))
        out[col * FILES_PER_COL + row + 1] = name
    return out


def extract_image(page, xname, dest):
    """Vuelca el JPEG incrustado tal cual, sin recodificar."""
    # El content stream nombra las imágenes sin la barra ("X3"); en el
    # diccionario de recursos la clave sí la lleva ("/X3").
    xobj = page["/Resources"]["/XObject"][f"/{xname}"].get_object()
    filt = xobj.get("/Filter")
    filt = [filt] if not isinstance(filt, list) else filt
    if "/DCTDecode" not in [str(f) for f in filt]:
        raise ValueError(f"{xname}: se esperaba JPEG, hay {filt}")
    dest.write_bytes(xobj.get_data() if hasattr(xobj, "get_data") else xobj._data)


def sql_str(v):
    return "NULL" if v is None or v == "" else "'" + str(v).replace("'", "''") + "'"


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("pdf", help="orla en PDF (no la copies dentro del repo)")
    ap.add_argument("--grup", default="2ESO-E")
    ap.add_argument("--curs", default="2026-27")
    ap.add_argument("--db", default="tutoria", help="nombre de la base D1")
    ap.add_argument("--bucket", default="tutoria-fotos", help="nombre del bucket R2")
    ap.add_argument("--out", help="directorio de salida (por defecto, un temporal)")
    ap.add_argument("--dry-run", action="store_true", help="solo listar, no escribir")
    args = ap.parse_args()

    page = PdfReader(args.pdf).pages[0]
    cells = read_cells(page)
    photos = read_photos(page)

    if not cells:
        sys.exit("No se ha reconocido ningún alumno.")

    repo = Path(__file__).resolve().parent.parent
    out = Path(args.out) if args.out else Path(tempfile.mkdtemp(prefix="tutoria-"))
    if repo in out.resolve().parents or out.resolve() == repo:
        sys.exit(f"El directorio de salida está dentro del repositorio ({out}).\n"
                 "Elige uno fuera: estos datos no deben acabar en git.")

    print(f"Alumnos reconocidos: {len(cells)}   ·   con foto: {len(photos)}")
    sin_foto = sorted(set(cells) - set(photos))
    if sin_foto:
        print(f"Sin foto: {', '.join(f'nº{n}' for n in sin_foto)}")

    rows = []
    for n in sorted(cells):
        c = cells[n]
        sid = slug(f"{c['cognoms']} {c['nom']}")
        rows.append((n, sid, c))
        print(f"  {n:>3}  {sid:<44} {c['cognoms']}, {c['nom']} {c['marca']}")

    if args.dry_run:
        print("\n--dry-run: no se ha escrito nada.")
        return

    out.mkdir(parents=True, exist_ok=True)
    fotos_dir = out / "fotos"
    fotos_dir.mkdir(exist_ok=True)

    lines = [
        "-- Generado por scripts/tutoria_import_orla.py — NO commitear.",
        f"DELETE FROM tutoria_alumnes WHERE grup = {sql_str(args.grup)} "
        f"AND curs = {sql_str(args.curs)};",
    ]
    for n, sid, c in rows:
        tiene = 1 if n in photos else 0
        if tiene:
            extract_image(page, photos[n], fotos_dir / f"{sid}.jpg")
        lines.append(
            "INSERT INTO tutoria_alumnes (id, num, grup, curs, cognoms, nom, marca, foto) "
            f"VALUES ({sql_str(sid)}, {n}, {sql_str(args.grup)}, {sql_str(args.curs)}, "
            f"{sql_str(c['cognoms'])}, {sql_str(c['nom'])}, {sql_str(c['marca'])}, {tiene});"
        )
    (out / "alumnes.sql").write_text("\n".join(lines) + "\n", encoding="utf-8")

    # Lista de los alumnos con foto en ESTA carga. Se sube al bucket como
    # _roster.txt para que la próxima ejecución sepa qué había antes y pueda
    # borrar las fotos de quien ya no está: R2 no tiene "borrar lo que sobra",
    # y sin esto las imágenes de alumnos de cursos pasados se quedarían ahí
    # para siempre. Son datos de menores: no deben acumularse.
    con_foto = [sid for n, sid, c in rows if n in photos]
    (out / "_roster.txt").write_text("\n".join(sorted(con_foto)) + "\n", encoding="utf-8")

    subir = [
        "#!/bin/sh", "set -e",
        'cd "$(dirname "$0")"',
        "",
        "# 1) Fichas: el SQL borra primero las filas de este grupo y curso.",
        f"npx wrangler d1 execute {args.db} --remote --file=alumnes.sql",
        "",
        "# 2) Fotos que sobran de la carga anterior. Si no hay _roster.txt en el",
        "#    bucket (primera vez), no hay nada que limpiar y seguimos.",
        f"if npx wrangler r2 object get {args.bucket}/_roster.txt \\",
        "     --file=_roster_previo.txt --remote >/dev/null 2>&1; then",
        '  sobran=$(grep -vxF -f _roster.txt _roster_previo.txt || true)',
        '  for sid in $sobran; do',
        '    echo "  - sobra: $sid"',
        f'    npx wrangler r2 object delete {args.bucket}/$sid.jpg --remote',
        "  done",
        "fi",
        "",
        "# 3) Fotos de esta carga.",
    ]
    for sid in con_foto:
        subir.append(f"npx wrangler r2 object put {args.bucket}/{sid}.jpg "
                     f"--file=fotos/{sid}.jpg --content-type=image/jpeg --remote")
    subir += [
        "",
        "# 4) Dejar constancia de qué hay ahora, para la próxima limpieza.",
        f"npx wrangler r2 object put {args.bucket}/_roster.txt \\",
        "  --file=_roster.txt --content-type=text/plain --remote",
        "",
        'echo ""',
        'echo "Listo. Borra este directorio cuando termines:"',
        f'echo "  rm -rf {out}"',
    ]
    (out / "subir.sh").write_text("\n".join(subir) + "\n", encoding="utf-8")
    (out / "subir.sh").chmod(0o755)

    print(f"\nEscrito en {out}")
    print(f"  alumnes.sql   ({len(rows)} alumnos)")
    print(f"  fotos/        ({len(photos)} imágenes)")
    print(f"  subir.sh      ejecútalo para cargar D1 y R2")
    print(f"\nCuando acabes:  rm -rf {out}")


if __name__ == "__main__":
    main()
