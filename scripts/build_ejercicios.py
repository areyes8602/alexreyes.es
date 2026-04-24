#!/usr/bin/env python3
"""
Build ejercicios-index.json from the per-colección JSON files.

Run from the repo root:
    python3 scripts/build_ejercicios.py

What it does:
  1. Loads tags.json (the canonical taxonomy).
  2. Loads every file in assets/data/ejercicios/*.json.
  3. Validates each ejercicio:
     - tags use only known namespaces and known values
     - IDs are unique
     - puntos de los apartados suman la puntuacion del ejercicio
     - puntuaciones de ejercicios suman puntuacion_total de la colección
     - URLs del ejercicio apuntan a ficheros que existen (si son rutas relativas al sitio)
  4. Emits assets/data/ejercicios-index.json — una lista plana y enriquecida lista
     para filtrar en el cliente.

Exit code != 0 si hay cualquier error.
"""
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = REPO_ROOT / "assets" / "data"
TAGS_FILE = DATA_DIR / "tags.json"
EJERCICIOS_DIR = DATA_DIR / "ejercicios"
INDEX_OUT = DATA_DIR / "ejercicios-index.json"


class BuildError(Exception):
    pass


def load_json(path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        raise BuildError(f"JSON inválido en {path}: {e}")
    except FileNotFoundError:
        raise BuildError(f"No existe: {path}")


def validate_tags(tags_dict, taxonomy, context):
    """Validate a tags dict {namespace: value_or_list}. Returns list of errors."""
    errors = []
    namespaces = taxonomy["namespaces"]
    for ns, value in tags_dict.items():
        if ns not in namespaces:
            errors.append(f"{context}: namespace '{ns}' no existe en tags.json")
            continue
        ns_def = namespaces[ns]
        allowed = set(ns_def["valores"].keys())
        multi = ns_def.get("multi", False)

        if multi:
            if not isinstance(value, list):
                errors.append(f"{context}: namespace '{ns}' es multi-valor, debe ser lista (recibido: {type(value).__name__})")
                continue
            for v in value:
                if v not in allowed:
                    errors.append(f"{context}: valor '{v}' no existe en namespace '{ns}'")
        else:
            if isinstance(value, list):
                errors.append(f"{context}: namespace '{ns}' es de valor único, no lista")
                continue
            if value not in allowed:
                errors.append(f"{context}: valor '{value}' no existe en namespace '{ns}'")
    return errors


def validate_url_exists(url, context):
    """Check a site-relative URL points to an existing file. Non-fatal (warning)."""
    if not url.startswith("/"):
        return []  # external URL, skip
    # Try to find the file: /path/ -> /path/index.html, /path.html -> /path.html
    candidates = []
    if url.endswith("/"):
        candidates.append(REPO_ROOT / (url.lstrip("/") + "index.html"))
    else:
        candidates.append(REPO_ROOT / url.lstrip("/"))
    for c in candidates:
        if c.exists():
            return []
    return [f"{context}: URL '{url}' no resuelve a ningún fichero en el repo"]


def build_index_entry(ejercicio, coleccion, taxonomy):
    """Flatten an ejercicio + its colección into a single index entry."""
    # Merge tags: coleccion.tags_coleccion act as defaults for the ejercicio
    # (sin sobrescribir lo que ya trae el ejercicio).
    col_tags = coleccion.get("tags_coleccion", {}) or {}
    ej_tags = ejercicio.get("tags", {}) or {}
    merged_tags = {**col_tags, **ej_tags}

    # Compute tag labels in 3 languages for indexing/search
    label_snippets = {"es": [], "ca": [], "en": []}
    for ns, value in merged_tags.items():
        ns_def = taxonomy["namespaces"].get(ns)
        if not ns_def:
            continue
        values = value if isinstance(value, list) else [value]
        for v in values:
            v_def = ns_def["valores"].get(v)
            if v_def and "label" in v_def:
                for lang in ("es", "ca", "en"):
                    if lang in v_def["label"]:
                        label_snippets[lang].append(v_def["label"][lang])

    return {
        "id": ejercicio["id"],
        "titulo": ejercicio.get("titulo") or ejercicio.get("descriptor") or ejercicio["id"],
        "url": ejercicio.get("url"),
        "numero": ejercicio.get("numero"),
        "puntuacion": ejercicio.get("puntuacion"),
        "apartados_count": len(ejercicio.get("apartados", [])),
        "coleccion": {
            "id": coleccion["id"],
            "titulo": coleccion.get("titulo"),
            "tipo": coleccion.get("tipo_coleccion"),
            "fecha": coleccion.get("fecha"),
            "url_index": coleccion.get("url_index"),
            "grupo": coleccion.get("grupo"),
            "promocion": coleccion.get("promocion"),
        },
        "tags": merged_tags,
        "search_text": {
            "es": " ".join([ejercicio.get("titulo", "")] + label_snippets["es"]).lower(),
            "ca": " ".join([ejercicio.get("titulo", "")] + label_snippets["ca"]).lower(),
            "en": " ".join([ejercicio.get("titulo", "")] + label_snippets["en"]).lower(),
        },
    }


def main():
    errors = []
    warnings = []

    # 1. Load taxonomy
    taxonomy = load_json(TAGS_FILE)
    print(f"✓ Taxonomía cargada: {len(taxonomy['namespaces'])} namespaces")

    # 2. Load colecciones
    if not EJERCICIOS_DIR.exists():
        raise BuildError(f"No existe {EJERCICIOS_DIR}")
    coleccion_files = sorted(EJERCICIOS_DIR.glob("*.json"))
    print(f"✓ Colecciones encontradas: {len(coleccion_files)}")

    all_ids = {}
    index_entries = []

    for cf in coleccion_files:
        col = load_json(cf)
        ctx_col = f"[{cf.name}] coleccion '{col.get('id')}'"

        # Validate colección-level tags
        errors += validate_tags(col.get("tags_coleccion", {}), taxonomy, ctx_col)

        # Suma de puntuaciones por ejercicio = puntuacion_total
        expected_total = col.get("puntuacion_total")
        suma = 0
        for ej in col.get("ejercicios", []):
            ctx_ej = f"[{cf.name}] ejercicio '{ej.get('id')}'"

            # Unique IDs
            if ej["id"] in all_ids:
                errors.append(f"{ctx_ej}: ID duplicado (ya en {all_ids[ej['id']]})")
            else:
                all_ids[ej["id"]] = cf.name

            # Sum apartados puntos = puntuacion
            apart_sum = sum(a.get("puntos", 0) for a in ej.get("apartados", []))
            if "puntuacion" in ej and apart_sum != ej["puntuacion"]:
                errors.append(f"{ctx_ej}: suma de apartados={apart_sum} ≠ puntuacion={ej['puntuacion']}")
            suma += ej.get("puntuacion", 0)

            # Validate ejercicio-level tags
            errors += validate_tags(ej.get("tags", {}), taxonomy, ctx_ej)

            # Validate URL exists (warning, not error)
            if ej.get("url"):
                warnings += validate_url_exists(ej["url"], ctx_ej)

            # Build index entry
            index_entries.append(build_index_entry(ej, col, taxonomy))

        if expected_total is not None and suma != expected_total:
            errors.append(f"{ctx_col}: suma ejercicios={suma} ≠ puntuacion_total={expected_total}")

        if col.get("url_index"):
            warnings += validate_url_exists(col["url_index"], ctx_col)

    # 3. Emit index
    index = {
        "schema_version": 2,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "taxonomy_path": "/assets/data/tags.json",
        "count": len(index_entries),
        "ejercicios": index_entries,
    }

    # Print report
    print(f"\n─── Ejercicios indexados: {len(index_entries)} ───")
    for e in index_entries:
        print(f"  · {e['id']:30s} {e['titulo'][:60]}")

    if warnings:
        print(f"\n⚠ Warnings ({len(warnings)}):")
        for w in warnings:
            print(f"  {w}")

    if errors:
        print(f"\n✗ ERRORES ({len(errors)}):")
        for e in errors:
            print(f"  {e}")
        print("\nBuild abortado. Corrige los errores arriba.")
        sys.exit(1)

    with open(INDEX_OUT, "w", encoding="utf-8") as f:
        json.dump(index, f, ensure_ascii=False, indent=2)

    print(f"\n✓ Índice escrito en {INDEX_OUT.relative_to(REPO_ROOT)} ({os.path.getsize(INDEX_OUT)} bytes)")


if __name__ == "__main__":
    try:
        main()
    except BuildError as e:
        print(f"\n✗ {e}", file=sys.stderr)
        sys.exit(2)
