#!/usr/bin/env python3
"""Vuelca el listado de direcciones y teléfonos en las fichas de tutoría.

Lee el «Llistat d'adreces i telèfons dels alumnes» que da el centro y deja
en cada ficha la dirección, los teléfonos y el nombre del padre y la madre.

IMPORTANTE — dónde acaban los datos
-----------------------------------
Son datos de contacto de menores y de sus familias: dirección postal y
teléfonos. Como el resto de scripts de tutoría, este NO escribe dentro del
repositorio, que es público. El destino es Cloudflare D1 y el SQL intermedio
va a un directorio temporal que debes borrar en cuanto lo hayas subido.

Uso
---
    python3 scripts/tutoria_import_contactes.py \\
        --pdf "Llistat d'adreces i telèfons dels alumnes.pdf" \\
        --grup 2ESO-E --curs 2026-27 [--dry-run]

    npx wrangler d1 execute tutoria --remote --file=<el .sql que diga>
    rm -rf <el directorio temporal>

Formato del listado
-------------------
Una fila por alumno, en columnas de posición fija:

    Nº · Alumne/a · D. Naix · Tel 1 · Tel 2 · Mòbil · Pare · Mare ·
    Adreça · C.P · Població · Província

Las columnas se leen por su posición horizontal, no partiendo el texto por
espacios: una dirección lleva espacios dentro y un alumno puede no tener
los tres teléfonos, y contar campos desplazaría los datos de columna. Una
dirección larga se parte en varias líneas y se vuelve a juntar por la fila.
"""
import argparse
import json
import re
import sys
import tempfile
import unicodedata
from pathlib import Path

try:
    import pdfplumber
except ImportError:
    sys.exit("Falta pdfplumber:  pip install pdfplumber")

REPO = Path(__file__).resolve().parent.parent

# Bandas horizontales de cada columna, en puntos. Salen de la cabecera del
# propio PDF; si el centro cambia la plantilla, se ajustan aquí.
COLUMNES = [
    ("num",       18,   40),
    ("alumne",    40,  182),
    ("naixement", 182, 231),
    ("tel1",      231, 283),
    ("tel2",      283, 334),
    ("mobil",     334, 385),
    ("pare",      385, 447),
    ("mare",      447, 509),
    ("adreca",    509, 673),
    ("cp",        673, 712),
    ("poblacio",  712, 775),
    ("provincia", 775, 900),
]
CAPCALERA = 115          # por encima: título y cabecera de columnas
TELEFON = re.compile(r"^\d{6,12}$")


def slug(text):
    """Mismo slug que tutoria_import_orla.py: es la clave de la ficha."""
    t = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode()
    t = re.sub(r"[^a-zA-Z0-9]+", "-", t).strip("-").lower()
    return re.sub(r"-{2,}", "-", t)


def sql_str(v):
    if v is None or v == "":
        return "NULL"
    return "'" + str(v).replace("'", "''") + "'"


def columna(x):
    for nom, x0, x1 in COLUMNES:
        if x0 <= x < x1:
            return nom
    return None


def llegeix(pdf_path):
    """Devuelve una lista de filas, cada una {columna: texto}."""
    files = []
    with pdfplumber.open(pdf_path) as pdf:
        for pagina in pdf.pages:
            linies = {}
            for w in pagina.extract_words():
                if w["top"] < CAPCALERA:
                    continue
                linies.setdefault(round(w["top"] / 3) * 3, []).append(w)

            for y in sorted(linies):
                cel = {}
                for w in sorted(linies[y], key=lambda w: w["x0"]):
                    c = columna(w["x0"])
                    if c:
                        cel[c] = (cel.get(c, "") + " " + w["text"]).strip()
                if not cel:
                    continue
                # Una fila nueva empieza donde hay número de lista; lo demás
                # es continuación de la dirección del alumno anterior.
                if re.fullmatch(r"\d{1,3}", cel.get("num", "")):
                    files.append(cel)
                elif files:
                    for c, v in cel.items():
                        if c == "num":
                            continue
                        files[-1][c] = (files[-1].get(c, "") + " " + v).strip()
    return files


def parteix_nom(alumne):
    """«Cognom Cognom, Nom» → (cognoms, nom). Sin coma, no se inventa."""
    if "," not in alumne:
        return alumne.strip(), ""
    cognoms, nom = alumne.split(",", 1)
    return cognoms.strip(), nom.strip()


def telefons(fila):
    """Los tres teléfonos que haya, sin repetir y sin huecos."""
    vals = []
    for c in ("tel1", "tel2", "mobil"):
        v = re.sub(r"\D", "", fila.get(c, ""))
        if TELEFON.fullmatch(v) and v not in vals:
            vals.append(v)
    return " · ".join(vals)


def adreca_completa(fila):
    trossos = [fila.get("adreca", "").strip()]
    cp_pob = " ".join(x for x in (fila.get("cp", "").strip(),
                                  fila.get("poblacio", "").strip()) if x)
    if cp_pob:
        trossos.append(cp_pob)
    return ", ".join(t for t in trossos if t)


def familia(fila, tels):
    """La ficha guarda `familia` como LISTA JSON, no como texto.

    La plantilla de /tutoria/fitxa/ es {nom, relacio, telefon, email, notes}:
    escribir aquí una cadena dejaría la pestaña Família en blanco.

    El listado da los teléfonos en columnas propias (Tel 1, Tel 2, Mòbil) sin
    decir de quién es cada uno, así que no se reparten a ciegas entre padre y
    madre: van juntos al contacto rápido.
    """
    gent = []
    for relacio, camp in (("Pare", "pare"), ("Mare", "mare")):
        v = fila.get(camp, "").strip()
        if v:
            gent.append({"nom": v, "relacio": relacio,
                         "telefon": "", "email": "", "notes": ""})
    return json.dumps(gent, ensure_ascii=False) if gent else ""


def data_iso(txt):
    """dd/mm/aaaa → aaaa-mm-dd, que es lo que espera un <input type="date">."""
    m = re.fullmatch(r"(\d{1,2})/(\d{1,2})/(\d{4})", txt.strip())
    if not m:
        return ""
    d, mes, a = m.groups()
    return f"{a}-{int(mes):02d}-{int(d):02d}"


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--pdf", required=True, help="Llistat d'adreces i telèfons")
    ap.add_argument("--grup", default="2ESO-E")
    ap.add_argument("--curs", default="2026-27")
    ap.add_argument("--out", help="directorio de salida (por defecto, uno temporal)")
    ap.add_argument("--dry-run", action="store_true",
                    help="solo cuenta lo que ha leído; no escribe nada")
    args = ap.parse_args()

    files = llegeix(args.pdf)
    if not files:
        sys.exit("No se ha leído ninguna fila. ¿Es el listado de direcciones?")

    alumnes, sense_nom = [], 0
    for fila in files:
        cognoms, nom = parteix_nom(fila.get("alumne", ""))
        if not cognoms:
            sense_nom += 1
            continue
        tels = telefons(fila)
        alumnes.append({
            "id": slug(f"{cognoms} {nom}"),
            "num": int(fila["num"]),
            "adreca": adreca_completa(fila),
            # Los teléfonos del listado son de la familia, no del alumno: el
            # campo `telefon` de la ficha está etiquetado «telèfon de
            # l'alumne» y meterlos ahí diría algo que no es.
            "contacte": tels,
            "familia": familia(fila, tels),
            "naixement": data_iso(fila.get("naixement", "")),
        })

    # Recuento sin sacar ningún dato por pantalla: los nombres, direcciones y
    # teléfonos no tienen por qué acabar en el historial de la terminal.
    amb_adreca = sum(1 for a in alumnes if a["adreca"])
    amb_telefon = sum(1 for a in alumnes if a["contacte"])
    amb_familia = sum(1 for a in alumnes if a["familia"])
    print(f"Alumnos leídos : {len(alumnes)}")
    print(f"  con dirección: {amb_adreca}")
    print(f"  con teléfono : {amb_telefon}")
    print(f"  con familia  : {amb_familia}")
    if sense_nom:
        print(f"  filas sin nombre descartadas: {sense_nom}")
    buits = [a["num"] for a in alumnes if not (a["adreca"] or a["contacte"])]
    if buits:
        print(f"  sin ningún dato de contacto (nº de lista): {buits}")

    if args.dry_run:
        print("\n--dry-run: no se ha escrito nada.")
        return

    out = Path(args.out) if args.out else Path(tempfile.mkdtemp(prefix="tutoria-contactes-"))
    if REPO in out.resolve().parents or out.resolve() == REPO:
        sys.exit(f"El directorio de salida está dentro del repositorio ({out}).\n"
                 "Elige uno fuera: estos datos no deben acabar en git.")
    out.mkdir(parents=True, exist_ok=True)

    linies = ["-- Generado por scripts/tutoria_import_contactes.py — NO commitear.",
              "-- Datos de contacto de menores. Bórralo en cuanto lo hayas subido."]
    for a in sorted(alumnes, key=lambda a: a["num"]):
        linies.append(
            "UPDATE tutoria_alumnes SET "
            f"adreca = {sql_str(a['adreca'])}, "
            f"contacte = {sql_str(a['contacte'])}, "
            f"familia = {sql_str(a['familia'])}, "
            f"naixement = COALESCE(NULLIF({sql_str(a['naixement'])}, ''), naixement), "
            "updated_at = datetime('now') "
            f"WHERE id = {sql_str(a['id'])} AND grup = {sql_str(args.grup)} "
            f"AND curs = {sql_str(args.curs)};"
        )
    fitxer = out / "contactes.sql"
    fitxer.write_text("\n".join(linies) + "\n", encoding="utf-8")

    print(f"\nSQL escrito en:\n  {fitxer}\n")
    print("Súbelo y borra el rastro:")
    print(f"  npx wrangler d1 execute tutoria --remote --file={fitxer}")
    print(f"  rm -rf {out}")
    print("\nSi algún alumno se queda sin datos, es que su nombre en el listado")
    print("no coincide con el de la orla: el UPDATE no encuentra la ficha.")


if __name__ == "__main__":
    main()
