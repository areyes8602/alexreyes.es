#!/usr/bin/env python3
"""build_bibliografia.py — Genera la bibliografía filtrable del doctorado.

Lee assets/data/bibliografia-doctorado.json, ordena alfabéticamente por autor
(estilo bibtex 'plain'), numera [1], [2]… e inyecta la barra de filtros + la
lista entre los marcadores <!-- BIB:START --> y <!-- BIB:END --> de
doctorado/bibliografia/index.html.

Filtro estilo Cangur: chips agrupados por faceta (Tipo, Área, MSC, Dificultad,
Acceso, Importancia). Clic en una cualidad = ver solo esa bibliografía
(combinable en AND entre grupos, OR dentro del grupo). El CSS y el JS del filtro
viven estáticos en la página; este script solo regenera los datos.

Uso:
    python3 scripts/build_bibliografia.py
"""
import json
import re
import unicodedata
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
DATA = REPO / "assets/data/bibliografia-doctorado.json"
PAGE = REPO / "doctorado/bibliografia/index.html"

DIF_LBL = {"facil": "Accesible", "media": "Media", "dificil": "Difícil"}
ACC_LBL = {"abierto": "Abierto", "pago": "De pago", "biblioteca": "Biblioteca"}
IMP_LBL = {"alta": "Alta", "media": "Media", "baja": "Baja"}


def slug(s):
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")


def sortkey(e):
    return unicodedata.normalize("NFKD", e["cite"]).encode("ascii", "ignore").decode().lower()


def chip(facet, val, label, extra=""):
    return (f'<button class="bib-chip{extra}" data-facet="{facet}" '
            f'data-val="{slug(val)}">{label}</button>')


def build_filters(entries):
    tipos, areas, mscs, difs, accs, imps = [], [], set(), set(), set(), set()
    for e in entries:
        if e["tipo"] not in tipos:
            tipos.append(e["tipo"])
        for a in e["area"]:
            if a not in areas:
                areas.append(a)
        mscs.add(e["msc"]); difs.add(e["dif"]); accs.add(e["acceso"]); imps.add(e["imp"])

    def group(title, facet, items):
        chips = "".join(items)
        return (f'<div class="bib-fgroup"><span class="bib-flabel">{title}</span>'
                f'<div class="bib-fchips">{chips}</div></div>')

    g = []
    g.append(group("Tipo", "tipo", [chip("tipo", t, t) for t in sorted(tipos)]))
    g.append(group("Área", "area", [chip("area", a, a) for a in sorted(areas)]))
    g.append(group("Dificultad", "dif",
                   [chip("dif", d, DIF_LBL[d], f" dif-{d}") for d in ["facil", "media", "dificil"] if d in difs]))
    g.append(group("Acceso", "acceso",
                   [chip("acceso", a, ACC_LBL[a]) for a in ["abierto", "pago", "biblioteca"] if a in accs]))
    g.append(group("Importancia", "imp",
                   [chip("imp", i, IMP_LBL[i]) for i in ["alta", "media", "baja"] if i in imps]))
    g.append(group("MSC", "msc", [chip("msc", m, m) for m in sorted(mscs)]))
    reset = ('<button class="bib-chip bib-chip-all bib-active" data-facet="all" '
             'data-val="all">Todas</button>')
    return (f'<div class="bib-filters">\n{reset}\n' + "\n".join(g) +
            '\n<p class="bib-count" id="bibCount"></p>\n</div>')


def build_list(entries):
    rows = []
    for n, e in enumerate(entries, 1):
        areas_slug = " ".join(slug(a) for a in e["area"])
        tags = []
        tags.append(f'<span class="bib-tag t-tipo">{e["tipo"]}</span>')
        for a in e["area"]:
            tags.append(f'<span class="bib-tag t-area">{a}</span>')
        tags.append(f'<span class="bib-tag t-msc">{e["msc"]}</span>')
        tags.append(f'<span class="bib-tag t-dif dif-{e["dif"]}">{DIF_LBL[e["dif"]]}</span>')
        tags.append(f'<span class="bib-tag t-acc">{ACC_LBL[e["acceso"]]}</span>')
        tags.append(f'<span class="bib-tag t-imp imp-{e["imp"]}">Imp. {IMP_LBL[e["imp"]].lower()}</span>')
        link = (f' <a class="bib-link" href="{e["url"]}" target="_blank" rel="noopener">enlace ↗</a>'
                if e["url"] else "")
        rows.append(
            f'<li class="bib-item" data-tipo="{slug(e["tipo"])}" data-area="{areas_slug}" '
            f'data-msc="{slug(e["msc"])}" data-dif="{e["dif"]}" data-acceso="{e["acceso"]}" '
            f'data-imp="{e["imp"]}">'
            f'<span class="bibnum">[{n}]</span>'
            f'<div class="bib-body"><span class="bib-cite">{e["cite"]}{link}</span>'
            f'<div class="bib-tags">{"".join(tags)}</div></div></li>'
        )
    return '<ol class="bib-list" id="bibList">\n' + "\n".join(rows) + "\n</ol>"


def main():
    data = json.loads(DATA.read_text(encoding="utf-8"))
    entries = sorted(data["entradas"], key=sortkey)
    block = build_filters(entries) + "\n" + build_list(entries)
    html = PAGE.read_text(encoding="utf-8")
    new = re.sub(r"<!-- BIB:START -->.*?<!-- BIB:END -->",
                 f"<!-- BIB:START -->\n{block}\n<!-- BIB:END -->",
                 html, flags=re.S)
    if new == html and "BIB:START" not in html:
        raise SystemExit("No se encontraron los marcadores BIB:START/END en la página.")
    PAGE.write_text(new, encoding="utf-8")
    print(f"✓ bibliografía: {len(entries)} entradas inyectadas en {PAGE.relative_to(REPO)}")


if __name__ == "__main__":
    main()
