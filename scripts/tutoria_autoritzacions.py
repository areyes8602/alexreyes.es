#!/usr/bin/env python3
"""Puja autoritzacions de sortides noves i refà el PDF amb totes.

Els escanejos porten dades de menors i el DNI de qui signa: no entren mai al
repositori. Aquest script només els porta de l'ordinador al bucket R2 privat i
marca a D1 que s'han lliurat.

Ús:
    python3 scripts/tutoria_autoritzacions.py escaneig.pdf manifest.json [--dry-run]

manifest.json (fora del repo):
    [
      {"busca": "Fineas", "pagines": [1], "lliurament": "2026-09-23",
       "signant": "Nom Cognoms de qui signa"},
      ...
    ]

- `busca`: tros del nom o cognoms. Ha de trobar UN sol alumne del grup, o
  s'atura sense tocar res.
- `pagines`: pàgines de l'escaneig (començant per 1) que són d'aquest alumne.

Fa, per aquest ordre:
  1. Resol cada alumne a D1 i talla les seves pàgines.
  2. Puja documents/autoritzacio/<id>.pdf a R2.
  3. UPDATE a D1: data de lliurament, qui signa i doc_autoritzacio = 1.
  4. Refà documents/autoritzacio/_totes.pdf amb tots els que en tenen, per
     número de llista. Abans en desa una còpia local del que hi havia.

Cal pypdf (pip install pypdf) i wrangler amb sessió (npx wrangler login).
"""
import argparse
import json
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

from pypdf import PdfReader, PdfWriter

BUCKET = "tutoria-fotos"
PREFIX = "documents/autoritzacio"
DB = "tutoria"


def wrangler(*args, captura=False):
    cmd = ["npx", "wrangler", *args]
    print("  $", " ".join(cmd))
    r = subprocess.run(cmd, check=True, text=True,
                       stdout=subprocess.PIPE if captura else None)
    return r.stdout


def sql_str(v):
    return "NULL" if v is None else "'" + str(v).replace("'", "''") + "'"


def consulta(sql):
    """Files d'un SELECT a la D1 remota."""
    out = wrangler("d1", "execute", DB, "--remote", "--json",
                   f"--command={sql}", captura=True)
    return json.loads(out)[0]["results"]


def r2_put(clau, fitxer):
    wrangler("r2", "object", "put", f"{BUCKET}/{clau}", f"--file={fitxer}",
             "--content-type=application/pdf", "-J", "eu", "--remote")


def r2_get(clau, fitxer):
    wrangler("r2", "object", "get", f"{BUCKET}/{clau}", f"--file={fitxer}",
             "-J", "eu", "--remote")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("escaneig")
    ap.add_argument("manifest")
    ap.add_argument("--grup", default="2ESO-E")
    ap.add_argument("--dry-run", action="store_true",
                    help="resol els alumnes i talla els PDF, però no puja res")
    args = ap.parse_args()

    lector = PdfReader(args.escaneig)
    entrades = json.loads(Path(args.manifest).read_text(encoding="utf-8"))
    tmp = Path(tempfile.mkdtemp(prefix="autoritzacions-"))
    print(f"Treball a {tmp}")

    # 1. Resoldre alumnes abans de tocar res
    resolts = []
    for e in entrades:
        patro = "%" + e["busca"].replace("'", "''") + "%"
        files = consulta(
            "SELECT id, num, cognoms, nom FROM tutoria_alumnes "
            f"WHERE grup = {sql_str(args.grup)} "
            f"AND (nom || ' ' || cognoms) LIKE '{patro}'")
        if len(files) != 1:
            sys.exit(f"«{e['busca']}» troba {len(files)} alumnes al grup: "
                     f"{[f['id'] for f in files]}. No s'ha tocat res.")
        a = files[0]
        for p in e["pagines"]:
            if not 1 <= p <= len(lector.pages):
                sys.exit(f"Pàgina {p} fora de l'escaneig ({len(lector.pages)}).")
        w = PdfWriter()
        for p in e["pagines"]:
            w.add_page(lector.pages[p - 1])
        pdf = tmp / f"{a['id']}.pdf"
        with open(pdf, "wb") as f:
            w.write(f)
        print(f"  nº {a['num']} {a['nom']} {a['cognoms']} → {a['id']} "
              f"(pàg. {e['pagines']})")
        resolts.append((a, e, pdf))

    if args.dry_run:
        print("--dry-run: no s'ha pujat res.")
        return

    # 2 i 3. Pujar cada escaneig i marcar-lo a D1
    ara = datetime.now(timezone.utc).isoformat()
    for a, e, pdf in resolts:
        r2_put(f"{PREFIX}/{a['id']}.pdf", pdf)
        wrangler("d1", "execute", DB, "--remote", "--command=" +
                 "UPDATE tutoria_alumnes SET "
                 f"autoritzacio_sortides = {sql_str(e['lliurament'])}, "
                 f"autoritzacio_signant = {sql_str(e.get('signant'))}, "
                 f"doc_autoritzacio = 1, updated_at = {sql_str(ara)} "
                 f"WHERE id = {sql_str(a['id'])} AND grup = {sql_str(args.grup)}")

    # 4. Refer _totes.pdf per número de llista
    try:
        r2_get(f"{PREFIX}/_totes.pdf", tmp / "_totes.anterior.pdf")
    except subprocess.CalledProcessError:
        print("  (no hi havia _totes.pdf anterior)")
    totes = PdfWriter()
    for a in consulta(
            "SELECT id FROM tutoria_alumnes "
            f"WHERE grup = {sql_str(args.grup)} AND doc_autoritzacio = 1 "
            "ORDER BY num"):
        fitxer = tmp / f"{a['id']}.pdf"
        if not fitxer.exists():
            r2_get(f"{PREFIX}/{a['id']}.pdf", fitxer)
        for pag in PdfReader(fitxer).pages:
            totes.add_page(pag)
    with open(tmp / "_totes.pdf", "wb") as f:
        totes.write(f)
    r2_put(f"{PREFIX}/_totes.pdf", tmp / "_totes.pdf")

    print(f"Fet. Còpia del _totes.pdf anterior a {tmp} (esborra la carpeta "
          "quan ho hagis comprovat: hi ha dades d'alumnes).")


if __name__ == "__main__":
    main()
