#!/usr/bin/env python3
"""build_bibliografia.py — Genera la bibliografía filtrable del doctorado (es/ca/en).

Lee assets/data/bibliografia-doctorado.json, ordena alfabéticamente por autor
(bibtex 'plain'), numera [n] e inyecta el selector de filtros + la lista entre
los marcadores <!-- BIB:START --> y <!-- BIB:END --> de cada versión de idioma:

    doctorado/bibliografia/index.html        (es)
    ca/doctorado/bibliografia/index.html     (ca)
    en/doctorado/bibliografia/index.html     (en)

Los slugs de los data-* (para el filtro JS) se derivan SIEMPRE del valor canónico
en español, así el filtrado funciona igual en los tres idiomas; solo cambian las
etiquetas visibles. El CSS y el JS del filtro viven estáticos en cada página.

Uso:
    python3 scripts/build_bibliografia.py
"""
import json
import re
import unicodedata
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
DATA = REPO / "assets/data/bibliografia-doctorado.json"

# ── Etiquetas por idioma (clave = valor canónico en español del JSON) ──────────
L = {
    "es": {
        "page": "doctorado/bibliografia/index.html",
        "filtrar": "Filtrar por", "todas": "Todas", "imp": "Imp.", "enlace": "enlace ↗",
        "grp": {"tipo": "Tipo", "area": "Área", "dif": "Dificultad", "acceso": "Acceso", "imp": "Importancia", "msc": "MSC"},
        "dif": {"facil": "Accesible", "media": "Media", "dificil": "Difícil"},
        "acc": {"abierto": "Abierto", "pago": "De pago", "biblioteca": "Biblioteca"},
        "impv": {"alta": "Alta", "media": "Media", "baja": "Baja"},
        "tipo": {"Artículo": "Artículo", "Libro": "Libro", "Survey": "Survey", "Preprint": "Preprint", "Divulgación": "Divulgación", "Histórico": "Histórico", "Recurso": "Recurso"},
        "area": {"Teoría de números": "Teoría de números", "Dinámica simbólica": "Dinámica simbólica", "Combinatoria": "Combinatoria", "Teoría de grafos": "Teoría de grafos", "Sistemas dinámicos": "Sistemas dinámicos", "Álgebra y palabras": "Álgebra y palabras", "Computación": "Computación", "Análisis y probabilidad": "Análisis y probabilidad", "Historia": "Historia"},
        "count": ("referencia", "referencias", " (filtradas)"),
    },
    "ca": {
        "page": "ca/doctorado/bibliografia/index.html",
        "filtrar": "Filtra per", "todas": "Totes", "imp": "Imp.", "enlace": "enllaç ↗",
        "grp": {"tipo": "Tipus", "area": "Àrea", "dif": "Dificultat", "acceso": "Accés", "imp": "Importància", "msc": "MSC"},
        "dif": {"facil": "Accessible", "media": "Mitjana", "dificil": "Difícil"},
        "acc": {"abierto": "Obert", "pago": "De pagament", "biblioteca": "Biblioteca"},
        "impv": {"alta": "Alta", "media": "Mitjana", "baja": "Baixa"},
        "tipo": {"Artículo": "Article", "Libro": "Llibre", "Survey": "Survey", "Preprint": "Preprint", "Divulgación": "Divulgació", "Histórico": "Històric", "Recurso": "Recurs"},
        "area": {"Teoría de números": "Teoria de nombres", "Dinámica simbólica": "Dinàmica simbòlica", "Combinatoria": "Combinatòria", "Teoría de grafos": "Teoria de grafs", "Sistemas dinámicos": "Sistemes dinàmics", "Álgebra y palabras": "Àlgebra i paraules", "Computación": "Computació", "Análisis y probabilidad": "Anàlisi i probabilitat", "Historia": "Història"},
        "count": ("referència", "referències", " (filtrades)"),
    },
    "en": {
        "page": "en/doctorado/bibliografia/index.html",
        "filtrar": "Filter by", "todas": "All", "imp": "Imp.", "enlace": "link ↗",
        "grp": {"tipo": "Type", "area": "Area", "dif": "Difficulty", "acceso": "Access", "imp": "Importance", "msc": "MSC"},
        "dif": {"facil": "Accessible", "media": "Medium", "dificil": "Hard"},
        "acc": {"abierto": "Open", "pago": "Paywalled", "biblioteca": "Library"},
        "impv": {"alta": "High", "media": "Medium", "baja": "Low"},
        "tipo": {"Artículo": "Article", "Libro": "Book", "Survey": "Survey", "Preprint": "Preprint", "Divulgación": "Outreach", "Histórico": "Historical", "Recurso": "Resource"},
        "area": {"Teoría de números": "Number theory", "Dinámica simbólica": "Symbolic dynamics", "Combinatoria": "Combinatorics", "Teoría de grafos": "Graph theory", "Sistemas dinámicos": "Dynamical systems", "Álgebra y palabras": "Algebra & words", "Computación": "Computation", "Análisis y probabilidad": "Analysis & probability", "Historia": "History"},
        "count": ("reference", "references", " (filtered)"),
    },
}


def slug(s):
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")


def sortkey(e):
    return unicodedata.normalize("NFKD", e["cite"]).encode("ascii", "ignore").decode().lower()


def chip(facet, canon, label, extra=""):
    return (f'<button class="bib-chip{extra}" data-facet="{facet}" '
            f'data-val="{slug(canon)}">{label}</button>')


def build_filters(entries, t):
    tipos, areas, mscs, difs, accs, imps = [], [], set(), set(), set(), set()
    for e in entries:
        if e["tipo"] not in tipos:
            tipos.append(e["tipo"])
        for a in e["area"]:
            if a not in areas:
                areas.append(a)
        mscs.add(e["msc"]); difs.add(e["dif"]); accs.add(e["acceso"]); imps.add(e["imp"])

    groups = [
        ("tipo", [chip("tipo", x, t["tipo"][x]) for x in sorted(tipos, key=lambda v: t["tipo"][v])]),
        ("area", [chip("area", x, t["area"][x]) for x in sorted(areas, key=lambda v: t["area"][v])]),
        ("dif", [chip("dif", d, t["dif"][d], f" dif-{d}") for d in ["facil", "media", "dificil"] if d in difs]),
        ("acceso", [chip("acceso", a, t["acc"][a]) for a in ["abierto", "pago", "biblioteca"] if a in accs]),
        ("imp", [chip("imp", i, t["impv"][i]) for i in ["alta", "media", "baja"] if i in imps]),
        ("msc", [chip("msc", m, m) for m in sorted(mscs)]),
    ]
    concepts = [f'<span class="bib-flabel">{t["filtrar"]}</span>']
    for gid, _ in groups:
        concepts.append(
            f'<button class="bib-concept" data-group="{gid}" aria-expanded="false">'
            f'{t["grp"][gid]}<span class="bib-cbadge" hidden></span></button>')
    concepts.append(f'<button class="bib-concept bib-chip-all bib-active" '
                    f'data-facet="all" data-val="all">{t["todas"]}</button>')
    gblocks = [f'<div class="bib-fgroup" data-group="{gid}" hidden>'
               f'<div class="bib-fchips">{"".join(ch)}</div></div>' for gid, ch in groups]
    one, many, filt = t["count"]
    return ('<div class="bib-filters">\n'
            f'<div class="bib-concepts">{"".join(concepts)}</div>\n'
            f'<div class="bib-groups">{"".join(gblocks)}</div>\n'
            f'<p class="bib-count" id="bibCount" data-one="{one}" data-many="{many}" '
            f'data-filt="{filt}"></p>\n</div>')


def build_list(entries, t):
    rows = []
    for n, e in enumerate(entries, 1):
        areas_slug = " ".join(slug(a) for a in e["area"])
        tags = [f'<span class="bib-tag t-tipo">{t["tipo"][e["tipo"]]}</span>']
        for a in e["area"]:
            tags.append(f'<span class="bib-tag t-area">{t["area"][a]}</span>')
        tags.append(f'<span class="bib-tag t-msc">{e["msc"]}</span>')
        tags.append(f'<span class="bib-tag t-dif dif-{e["dif"]}">{t["dif"][e["dif"]]}</span>')
        tags.append(f'<span class="bib-tag t-acc">{t["acc"][e["acceso"]]}</span>')
        tags.append(f'<span class="bib-tag t-imp imp-{e["imp"]}">{t["imp"]} {t["impv"][e["imp"]].lower()}</span>')
        link = (f' <a class="bib-link" href="{e["url"]}" target="_blank" rel="noopener">{t["enlace"]}</a>'
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
    done = []
    for lang, t in L.items():
        page = REPO / t["page"]
        if not page.exists():
            print(f"  ⚠ {t['page']} no existe; omitido")
            continue
        block = build_filters(entries, t) + "\n" + build_list(entries, t)
        html = page.read_text(encoding="utf-8")
        if "BIB:START" not in html:
            print(f"  ⚠ {t['page']} sin marcadores BIB:START/END; omitido")
            continue
        new = re.sub(r"<!-- BIB:START -->.*?<!-- BIB:END -->",
                     f"<!-- BIB:START -->\n{block}\n<!-- BIB:END -->", html, flags=re.S)
        page.write_text(new, encoding="utf-8")
        done.append(lang)
    print(f"✓ bibliografía: {len(entries)} entradas × {len(done)} idiomas ({', '.join(done)})")


if __name__ == "__main__":
    main()
