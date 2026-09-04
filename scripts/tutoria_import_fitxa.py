#!/usr/bin/env python3
"""Vuelca las respuestas de la ficha del alumno en las fichas de tutoría.

Lee la exportación de Microsoft Forms (el Excel que da «Abrir en Excel», o
un CSV) del formulario que rellenan los alumnos el primer día y deja cada
respuesta en su campo de la ficha.

IMPORTANTE — dónde acaban los datos
-----------------------------------
Hay datos de salud y de situación familiar de menores. Como el resto de
scripts de tutoría, este NO escribe dentro del repositorio, que es público:
el destino es Cloudflare D1 y el SQL intermedio va a un directorio temporal
que debes borrar en cuanto lo hayas subido. Borra también el Excel de Forms.

Uso
---
    python3 scripts/tutoria_import_fitxa.py --respostes fitxa.xlsx \\
        --grup 2ESO-E --curs 2026-27 [--dry-run]

Antes, una sola vez:
    npx wrangler d1 execute tutoria --remote --file=scripts/sql/tutoria_fitxa_inicial.sql

Cómo empareja
-------------
Por nombre y apellidos, que son las dos primeras preguntas del formulario, y
usando el mismo slug que genera tutoria_import_orla.py. Si un alumno los
escribe distinto de como constan en la orla, no se empareja: el script lo
dice por su número de fila para que lo corrijas en el Excel y repitas.
"""
import argparse
import json
import re
import sys
import tempfile
import unicodedata
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent

# Cada pregunta del formulario, en orden, y a qué columna de la ficha va.
# La clave es un trozo distintivo del enunciado en minúsculas y sin acentos:
# Forms usa el texto de la pregunta como cabecera de columna, y así el orden
# puede cambiar sin que se rompa nada.
CAMPS = [
    ("nom",                 "_nom"),
    ("cognoms",             "_cognoms"),
    ("data de naixement",   "naixement"),
    ("ciutat",              "ciutat"),
    ("telefon mobil",       "telefon"),
    ("correu",              "email"),
    ("escola",              "escola_primaria"),
    ("nom del pare",        "_pare"),
    ("nom de la mare",      "_mare"),
    ("situacio familiar",   "situacio_familiar"),
    ("amb qui vius",        "situacio_amb_qui"),
    ("explica com es",      "situacio_nota"),
    ("quants germans",      "germans_nombre"),
    ("com es diuen",        "germans"),
    ("extraescolars",       "extraescolars"),
    ("salut",               "salut"),
    ("amics/amigues de la classe", "amics_classe"),
    ("altres classes",      "amics_nivell"),
    ("se't donen millor",   "mat_millor"),
    ("quines pitjor",       "mat_pitjor"),
    ("virtuts",             "virtuts"),
    ("canviar o millorar",  "millorar"),
]


def net(s):
    """Minúsculas sin acentos, para comparar enunciados y nombres."""
    s = unicodedata.normalize("NFKD", str(s)).encode("ascii", "ignore").decode()
    return re.sub(r"\s+", " ", s).strip().lower()


def slug(text):
    t = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode()
    t = re.sub(r"[^a-zA-Z0-9]+", "-", t).strip("-").lower()
    return re.sub(r"-{2,}", "-", t)


def sql_str(v):
    if v is None or str(v).strip() == "":
        return "NULL"
    return "'" + str(v).strip().replace("'", "''") + "'"


def data_iso(txt):
    """Forms pot tornar dd/mm/aaaa; la fitxa vol ISO."""
    t = str(txt).strip()
    if re.fullmatch(r"\d{4}-\d{2}-\d{2}", t):
        return t
    m = re.fullmatch(r"(\d{1,2})[/-](\d{1,2})[/-](\d{4})", t)
    if m:
        d, mes, a = m.groups()
        return f"{a}-{int(mes):02d}-{int(d):02d}"
    return ""


def llegeix(path):
    """Devuelve (cabeceras, filas) de un .xlsx o un .csv."""
    p = Path(path)
    if p.suffix.lower() in (".csv", ".txt"):
        import csv
        # Forms exporta en UTF-8 con BOM
        with open(p, encoding="utf-8-sig", newline="") as f:
            files = list(csv.reader(f))
        return files[0], files[1:]
    try:
        from openpyxl import load_workbook
    except ImportError:
        sys.exit("Para leer .xlsx hace falta openpyxl:  pip3 install openpyxl\n"
                 "O exporta el Excel a CSV y pásame el CSV.")
    ws = load_workbook(p, read_only=True, data_only=True).active
    files = [[("" if c is None else c) for c in fila] for fila in ws.values]
    return files[0], files[1:]


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--respostes", required=True, help="Excel o CSV de Forms")
    ap.add_argument("--grup", default="2ESO-E")
    ap.add_argument("--curs", default="2026-27")
    ap.add_argument("--out")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    capceleres, files = llegeix(args.respostes)
    caps = [net(c) for c in capceleres]

    # Forms afegeix columnes pròpies abans de les preguntes (Id, hores, el
    # correu i el nom de qui respon). "Nom" com a text encaixava amb "Nombre"
    # i es quedava amb la columna equivocada, buida: cap resposta s'emparellava.
    # Per això primer es busca pel número de pregunta, que Forms conserva a la
    # capçalera, i només si no hi és s'intenta pel text, saltant les seves.
    METADADES = ("id", "hora de inicio", "hora de finalizacion", "start time",
                 "completion time", "correo electronico", "email", "nombre", "name",
                 "hora de finalitzacio", "correu electronic")
    útils = [i for i, c in enumerate(caps) if c not in METADADES]

    col = {}
    for n, (tros, destí) in enumerate(CAMPS, start=1):
        for i, c in enumerate(caps):
            if re.match(rf"^{n}\s*[.)]", c):
                col[destí] = i
                break
        else:
            for i in útils:
                if net(tros) in caps[i]:
                    col[destí] = i
                    break
    falten = [d for _, d in CAMPS if d not in col]
    if falten:
        print("Preguntas que no he encontrado en la exportación:")
        for f in falten:
            print("   ", f)
        print("Revisa que sea el fichero del formulario correcto.\n")
    if "_nom" not in col or "_cognoms" not in col:
        sys.exit("Sin las columnas de nombre y apellidos no puedo emparejar a nadie.")

    def cel(fila, destí):
        i = col.get(destí)
        return "" if i is None or i >= len(fila) else str(fila[i]).strip()

    alumnes, sense_nom = [], []
    for n, fila in enumerate(files, start=2):      # fila 1 = cabeceras
        nom, cognoms = cel(fila, "_nom"), cel(fila, "_cognoms")
        if not nom or not cognoms:
            if any(str(c).strip() for c in fila):
                sense_nom.append(n)
            continue
        a = {"id": slug(f"{cognoms} {nom}"), "fila": n}
        for _, destí in CAMPS:
            if destí.startswith("_"):
                continue
            a[destí] = cel(fila, destí)
        a["naixement"] = data_iso(a.get("naixement", ""))
        # El pare i la mare van a la llista `familia`, que és JSON.
        gent = []
        for relacio, k in (("Pare", "_pare"), ("Mare", "_mare")):
            v = cel(fila, k)
            if v:
                gent.append({"nom": v, "relacio": relacio,
                             "telefon": "", "email": "", "notes": ""})
        a["familia"] = json.dumps(gent, ensure_ascii=False) if gent else ""
        alumnes.append(a)

    print(f"Respuestas leídas : {len(alumnes)}")
    if sense_nom:
        print(f"  filas sin nombre o apellidos (no se cargan): {sense_nom}")
    for etiqueta, k in (("con salud", "salut"), ("con situación familiar", "situacio_familiar"),
                        ("con amistades", "amics_classe")):
        print(f"  {etiqueta:24}: {sum(1 for a in alumnes if a.get(k))}")
    rep = [a["fila"] for a in alumnes
           if sum(1 for b in alumnes if b["id"] == a["id"]) > 1]
    if rep:
        print(f"  ¡ojo! respuestas repetidas del mismo alumno, filas: {sorted(set(rep))}")
        print("  se cargará la última de cada uno.")

    if args.dry_run:
        print("\n--dry-run: no se ha escrito nada.")
        return

    out = Path(args.out) if args.out else Path(tempfile.mkdtemp(prefix="tutoria-fitxa-"))
    if REPO in out.resolve().parents or out.resolve() == REPO:
        sys.exit(f"El directorio de salida está dentro del repositorio ({out}).\n"
                 "Elige uno fuera: estos datos no deben acabar en git.")
    out.mkdir(parents=True, exist_ok=True)

    camps_sql = [d for _, d in CAMPS if not d.startswith("_")]
    linies = ["-- Generado por scripts/tutoria_import_fitxa.py — NO commitear.",
              "-- Datos de salud y situación familiar de menores. Bórralo al subirlo."]
    for a in alumnes:                              # el último de cada id manda
        # COALESCE: una pregunta en blanco no borra lo que ya hubiera.
        sets = [f"{c} = COALESCE(NULLIF({sql_str(a.get(c))}, ''), {c})"
                for c in camps_sql]
        # `familia` es la excepción: el alumno solo da los nombres, así que
        # escribirla encima dejaría sin teléfonos ni correos una lista que el
        # tutor puede haber completado. Solo se rellena si está vacía.
        sets.append(
            f"familia = CASE WHEN familia IS NULL OR familia IN ('', '[]') "
            f"THEN NULLIF({sql_str(a.get('familia'))}, '') ELSE familia END")
        sets = ", ".join(sets)
        linies.append(
            f"UPDATE tutoria_alumnes SET {sets}, "
            "fitxa_inicial = datetime('now'), updated_at = datetime('now') "
            f"WHERE id = {sql_str(a['id'])} AND grup = {sql_str(args.grup)} "
            f"AND curs = {sql_str(args.curs)};"
        )
    fitxer = out / "fitxa-inicial.sql"
    fitxer.write_text("\n".join(linies) + "\n", encoding="utf-8")

    print(f"\nSQL escrito en:\n  {fitxer}\n")
    print("Súbelo y borra el rastro:")
    print(f"  npx wrangler d1 execute tutoria --remote --file={fitxer}")
    print(f"  rm -rf {out}")
    print("\nY borra también el Excel de Forms cuando ya no lo necesites.")
    print("\nDespués, para ver quién no la ha rellenado:")
    print("  npx wrangler d1 execute tutoria --remote --command \\")
    print(f"    \"SELECT num, cognoms, nom FROM tutoria_alumnes WHERE grup='{args.grup}' "
          "AND fitxa_inicial IS NULL ORDER BY num\"")


if __name__ == "__main__":
    main()
