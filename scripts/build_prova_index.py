#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Genera assets/data/prova-cangur-index.json: manifiesto ligero curso→modelos
para el motor 'Ponte a prova'. Escanea las colecciones examen con bloque
`prova_cangur`. Idempotente."""
import json
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
EJ = REPO / "assets" / "data" / "ejercicios"
OUT = REPO / "assets" / "data" / "prova-cangur-index.json"

CURSO_LABEL = {
    "5prim": {"es": "5º Primaria", "ca": "5è Primària", "en": "Year 5 (Primary)"},
    "6prim": {"es": "6º Primaria", "ca": "6è Primària", "en": "Year 6 (Primary)"},
    "1eso": {"es": "1º ESO", "ca": "1r ESO", "en": "Year 7 (1 ESO)"},
    "2eso": {"es": "2º ESO", "ca": "2n ESO", "en": "Year 8 (2 ESO)"},
    "3eso": {"es": "3º ESO", "ca": "3r ESO", "en": "Year 9 (3 ESO)"},
    "4eso": {"es": "4º ESO", "ca": "4t ESO", "en": "Year 10 (4 ESO)"},
    "1btl": {"es": "1º Bachillerato", "ca": "1r Batxillerat", "en": "Year 11 (1 BTL)"},
    "2btl": {"es": "2º Bachillerato", "ca": "2n Batxillerat", "en": "Year 12 (2 BTL)"},
}
CURSO_ORDER = list(CURSO_LABEL.keys())


def main():
    courses = {}
    for jf in sorted(EJ.glob("*.json")):
        try:
            col = json.load(open(jf, encoding="utf-8"))
        except Exception:
            continue
        pc = col.get("prova_cangur")
        if not pc or col.get("tipo_coleccion") != "examen":
            continue
        if col.get("schema_version", 1) < 3 or col.get("archivado"):
            continue  # modelos archivados (p.ej. variantes reordenadas de la misma prueba)
        curso = pc.get("curso")
        if not curso:
            continue
        courses.setdefault(curso, [])
        courses[curso].append({
            "id": col["id"],
            "modelo": pc.get("modelo", ""),
            "titulo": col.get("titulo", col["id"]),
            "fecha": col.get("fecha"),
            "num_preguntas": pc.get("num_preguntas", len(col.get("ejercicios", []))),
            "tiempo_min": pc.get("tiempo_min"),
            "puntuacion_total": col.get("puntuacion_total"),
            "json": f"/assets/data/ejercicios/{col['id']}.json",
            "url_index": col.get("url_index"),
        })
    ordered = []
    for c in CURSO_ORDER:
        if c in courses:
            models = sorted(courses[c], key=lambda m: m.get("modelo", ""))
            ordered.append({"curso": c, "label": CURSO_LABEL[c], "models": models})
    out = {
        "generated_for": "prova-cangur",
        "puntuacion": {"penalizacion": "1/4", "blanco": 0,
                       "valor": {"3": list(range(1, 11)), "4": list(range(11, 21)), "5": list(range(21, 31))}},
        "courses": ordered,
    }
    json.dump(out, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    total_models = sum(len(c["models"]) for c in ordered)
    print(f"✓ {OUT.relative_to(REPO)}  ({len(ordered)} cursos, {total_models} modelos)")


if __name__ == "__main__":
    main()
