#!/usr/bin/env python3
"""
build_apuntes.py
================

Recorre aula/**/apuntes/**/*.html (también /ca/aula/... y /en/aula/...) y emite
assets/data/apuntes-index.json con los metadatos de cada apunte.

Para cada archivo HTML extrae:
- titulo (de <title>, normalizado quitando sufijos del sitio)
- descripcion (de <meta name="description">)
- lang (de <html lang="..">)
- materia, unidad (inferidos del path)
- tipo:
    - "index_general" si es el índice global (ej. /aula/ib-ai-hl/apuntes/index.html)
    - "index_unidad" si es el índice de una unidad (ej. /aula/.../u-probabilitat/index.html)
    - "seccion"      si es un apartado numerado (ej. /aula/.../u-probabilitat/03-bayes.html)
    - "concepto"     si es un apunte tipo IB por concepto (ej. /aula/ib-ai-hl/apuntes/NM-3-6/index.html)
- section_num, section_slug (si tipo='seccion')
- tags (mergeados con sidecar meta.json opcional en la carpeta del apunte)

Si en la carpeta del apunte (o adyacente al HTML) hay un fichero `meta.json`,
sus claves se incorporan a los tags del registro. Útil para añadir conceptos
curriculares (concepto_iba, concepto_bach, concepto_eso), prerrequisitos, etc.

Genera además un search_text por idioma con título + descripción + materia +
unidad + tags concatenados — para búsqueda libre en el cliente.

Uso:
    python3 scripts/build_apuntes.py

Salida:
    assets/data/apuntes-index.json
"""

import json
import os
import re
import sys
from pathlib import Path
from datetime import datetime, timezone

REPO = Path(__file__).resolve().parent.parent

# Los 3 árboles donde viven apuntes
ROOTS = [
    REPO / "aula",          # canonical
    REPO / "ca" / "aula",   # mirror catalán
    REPO / "en" / "aula",   # mirror inglés
]

OUTPUT = REPO / "assets" / "data" / "apuntes-index.json"

# ---- Regex para extracción rápida sin DOM parser ----
RE_LANG = re.compile(r'<html\s+lang="([^"]+)"', re.IGNORECASE)
RE_TITLE = re.compile(r'<title>\s*([^<]+?)\s*</title>', re.IGNORECASE | re.DOTALL)
RE_DESC = re.compile(
    r'<meta\s+name="description"\s+content="([^"]*)"', re.IGNORECASE
)
RE_CANONICAL = re.compile(
    r'<link\s+rel="canonical"\s+href="([^"]*)"', re.IGNORECASE
)
RE_SECTION_NUMBER = re.compile(r"^(\d{2})-(.+?)\.html$")

# Sufijos típicos del sitio que limpiamos del título para el banco
TITLE_SUFFIXES_TO_STRIP = [
    " — alexreyes.es",
    " · alexreyes.es",
    " — Àlex Reyes",
    " · Àlex Reyes",
]


def strip_title_suffix(title: str) -> str:
    t = title.strip()
    for suf in TITLE_SUFFIXES_TO_STRIP:
        if t.endswith(suf):
            t = t[: -len(suf)].strip()
    return t


def infer_path_meta(html_path: Path):
    """A partir de la ruta del HTML deducir: lang_root (es/ca/en según prefijo),
    materia (segmento después de aula/), unidad (segmento dentro de apuntes/),
    es_index, section_num, section_slug.
    """
    rel = html_path.relative_to(REPO).as_posix()
    parts = rel.split("/")
    # parts[0] o parts[0..1] indican el lang_root
    if parts[0] in ("ca", "en") and len(parts) > 1 and parts[1] == "aula":
        lang_root = parts[0]
        body = parts[2:]   # ['ccss-1btl','apuntes','u-probabilitat','03-bayes.html']
    elif parts[0] == "aula":
        lang_root = "es"   # canonical (lang real puede ser ca/es/en según content)
        body = parts[1:]
    else:
        return None  # no es de apuntes

    if len(body) < 2 or body[1] != "apuntes":
        # Solo nos interesan rutas .../apuntes/...
        return None

    materia = body[0]                       # 'ccss-1btl', 'ib-ai-hl', 'eso-2'
    apuntes_inner = body[2:]                # rest después de 'apuntes/'
    filename = apuntes_inner[-1]
    es_index = filename == "index.html"

    section_num = None
    section_slug = None

    if len(apuntes_inner) == 1:
        # /aula/{materia}/apuntes/index.html → índice general (lista unidades/conceptos)
        unidad = None
        tipo = "index_general"
    elif len(apuntes_inner) >= 2:
        unidad = apuntes_inner[0]
        if es_index:
            # /aula/{materia}/apuntes/{unidad}/index.html
            # En IB AI los conceptos NM-X-Y son el "apunte" en sí (no contienen secciones)
            # Reconocemos por el slug: NM-X-Y, TANS-X-Y → tipo "concepto".
            if re.match(r"^(NM|TANS|SL|HL)-\d", unidad, re.IGNORECASE):
                tipo = "concepto"
            else:
                tipo = "index_unidad"
        else:
            tipo = "seccion"
            m = RE_SECTION_NUMBER.match(filename)
            if m:
                section_num = m.group(1)
                section_slug = m.group(2)

    return {
        "lang_root": lang_root,
        "materia": materia,
        "unidad": unidad,
        "tipo": tipo,
        "section_num": section_num,
        "section_slug": section_slug,
    }


def extract_html_meta(html_path: Path) -> dict:
    text = html_path.read_text(encoding="utf-8", errors="replace")

    lang_match = RE_LANG.search(text)
    title_match = RE_TITLE.search(text)
    desc_match = RE_DESC.search(text)
    canon_match = RE_CANONICAL.search(text)

    return {
        "lang": (lang_match.group(1).strip() if lang_match else "es"),
        "titulo_raw": (title_match.group(1).strip() if title_match else ""),
        "descripcion": (desc_match.group(1).strip() if desc_match else ""),
        "canonical": (canon_match.group(1).strip() if canon_match else ""),
    }


def load_sidecar(html_path: Path) -> dict:
    """Si hay un fichero meta.json en la carpeta del apunte, devuelve sus
    contenidos (dict). Útil para tags adicionales no inferibles del path/HTML.

    Buscamos:
    1. {dir_del_html}/meta.json  (sidecar para todos los apuntes de esa carpeta)
    2. {dir_del_html}/{filename_sin_ext}.meta.json  (sidecar específico de este apunte)
    """
    folder_meta = html_path.parent / "meta.json"
    file_meta = html_path.with_suffix(".meta.json")

    merged = {}
    if folder_meta.exists():
        try:
            merged.update(json.loads(folder_meta.read_text(encoding="utf-8")))
        except Exception as e:
            print(f"  ⚠ meta.json inválido en {folder_meta}: {e}", file=sys.stderr)
    if file_meta.exists():
        try:
            specific = json.loads(file_meta.read_text(encoding="utf-8"))
            # El sidecar específico tiene prioridad sobre el de carpeta
            merged.update(specific)
        except Exception as e:
            print(f"  ⚠ {file_meta.name} inválido: {e}", file=sys.stderr)
    return merged


def make_id(path_meta: dict, lang: str) -> str:
    """ID estable y único para el registro del banco."""
    bits = [
        path_meta["materia"],
        path_meta.get("unidad") or "_root",
    ]
    if path_meta.get("section_num"):
        bits.append(path_meta["section_num"])
        if path_meta.get("section_slug"):
            bits.append(path_meta["section_slug"])
    elif path_meta["tipo"] == "index_unidad":
        bits.append("index")
    elif path_meta["tipo"] == "concepto":
        bits.append("concepto")
    elif path_meta["tipo"] == "index_general":
        bits.append("hub")
    bits.append(lang)
    return "-".join(b for b in bits if b)


def build_search_text(record: dict) -> str:
    parts = [
        record.get("titulo", ""),
        record.get("descripcion", ""),
        record.get("materia", ""),
        record.get("unidad", "") or "",
        record.get("tipo", ""),
    ]
    tags = record.get("tags", {}) or {}
    for ns, val in tags.items():
        if isinstance(val, list):
            parts.extend(str(v) for v in val)
        elif val is not None:
            parts.append(str(val))
    return " · ".join(p for p in parts if p).lower()


def process_html(html_path: Path):
    pm = infer_path_meta(html_path)
    if pm is None:
        return None

    hm = extract_html_meta(html_path)
    sidecar = load_sidecar(html_path)

    # URL pública: la del path, prefijada con / desde la raíz del repo.
    url = "/" + html_path.relative_to(REPO).as_posix()

    # Título limpio (quitando sufijos del sitio)
    titulo = strip_title_suffix(hm["titulo_raw"])

    # Tags base: materia, idioma, unidad, tipo. Añadimos sidecar.
    tags = {
        "materia": pm["materia"],
        "idioma": hm["lang"],
        "tipo_apunte": pm["tipo"],
    }
    if pm.get("unidad"):
        tags["unidad"] = pm["unidad"]
    # Sidecar (tags curriculares, dificultad, etc.) sobreescribe lo automático.
    for k, v in sidecar.items():
        tags[k] = v

    record = {
        "id": make_id(pm, hm["lang"]),
        "tipo": pm["tipo"],
        "titulo": titulo,
        "descripcion": hm["descripcion"],
        "url": url,
        "lang": hm["lang"],
        "materia": pm["materia"],
        "unidad": pm.get("unidad"),
        "section_num": pm.get("section_num"),
        "section_slug": pm.get("section_slug"),
        "tags": tags,
    }
    record["search_text"] = build_search_text(record)
    return record


def build_concept_inheritance() -> dict:
    """Cruza con los JSON de ejercicios para inferir qué conceptos curriculares
    aplican a cada apunte/unidad. Estrategia:

    1. Recorrer todos los assets/data/ejercicios/*.json (excepto _TEMPLATE).
    2. Para cada ejercicio: extraer concepto_iba/bach/eso de tags Y la URL del
       apunte de origen (campos `source_apunt` o `url_index` de la colección).
    3. Construir dos mapas:
         por_unidad[(materia, unidad)] = set(conceptos)
         por_url[apunte_url_normalizada] = set(conceptos)

    Devuelve {'por_unidad': {...}, 'por_url': {...}} con sets dict por
    namespace ('concepto_iba', 'concepto_bach', 'concepto_eso').
    """
    ejercicios_dir = REPO / "assets" / "data" / "ejercicios"
    if not ejercicios_dir.exists():
        return {"por_unidad": {}, "por_url": {}}

    por_unidad = {}  # (materia, unidad) -> {ns: set(values)}
    por_url = {}     # url -> {ns: set(values)}

    def add(target: dict, ns: str, value):
        if value is None:
            return
        vals = value if isinstance(value, list) else [value]
        target.setdefault(ns, set()).update(str(v) for v in vals if v)

    def url_to_key(url: str):
        """De /aula/ccss-1btl/apuntes/u-probabilitat/03-bayes.html#anchor →
        ('ccss-1btl', 'u-probabilitat', '/aula/ccss-1btl/apuntes/u-probabilitat/03-bayes.html')"""
        if not url:
            return None, None, None
        clean = url.split("#")[0]
        parts = clean.split("/")
        if len(parts) >= 6 and parts[1] == "aula" and parts[3] == "apuntes":
            return parts[2], parts[4], clean
        return None, None, clean

    for jpath in sorted(ejercicios_dir.glob("*.json")):
        if jpath.name.startswith("_") or jpath.stem == "ejercicios-index":
            continue
        try:
            data = json.loads(jpath.read_text(encoding="utf-8"))
        except Exception:
            continue

        coleccion_url = data.get("url_index", "")
        col_mat, col_uni, col_clean = url_to_key(coleccion_url)

        # Recorre los ejercicios
        for ej in data.get("ejercicios", []) or []:
            ns_concepts = {}
            tags = ej.get("tags", {}) or {}
            for ns in ("concepto_iba", "concepto_bach", "concepto_eso"):
                if tags.get(ns):
                    add(ns_concepts, ns, tags[ns])

            # Si el ejercicio no tiene concepto, intentamos heredar del de
            # tags_coleccion (todo el JSON) — algunos JSON tienen concepto
            # general en tags_coleccion.
            if not ns_concepts:
                col_tags = data.get("tags_coleccion", {}) or {}
                for ns in ("concepto_iba", "concepto_bach", "concepto_eso"):
                    if col_tags.get(ns):
                        add(ns_concepts, ns, col_tags[ns])

            if not ns_concepts:
                continue

            # Atribuir al apunte específico (source_apunt o url_enunciado del ej)
            for url_field in ("source_apunt", "url_enunciado"):
                u = ej.get(url_field)
                m, ud, clean = url_to_key(u)
                if clean and "/apuntes/" in clean:
                    target = por_url.setdefault(clean, {})
                    for ns, vs in ns_concepts.items():
                        add(target, ns, list(vs))
                    if m and ud:
                        ut = por_unidad.setdefault((m, ud), {})
                        for ns, vs in ns_concepts.items():
                            add(ut, ns, list(vs))
                    break  # un apunte por ejercicio basta

            # También al apunte coleccion entera (si el JSON apunta a un apunte)
            if col_clean and "/apuntes/" in col_clean:
                target = por_url.setdefault(col_clean, {})
                for ns, vs in ns_concepts.items():
                    add(target, ns, list(vs))
            if col_mat and col_uni:
                ut = por_unidad.setdefault((col_mat, col_uni), {})
                for ns, vs in ns_concepts.items():
                    add(ut, ns, list(vs))

    # Convertir sets a listas ordenadas para serialización limpia
    def freeze(d):
        return {k: sorted(v) for k, v in d.items()}
    return {
        "por_unidad": {k: freeze(v) for k, v in por_unidad.items()},
        "por_url": {k: freeze(v) for k, v in por_url.items()},
    }


def main():
    inheritance = build_concept_inheritance()
    apuntes = []
    for root in ROOTS:
        if not root.exists():
            continue
        for html_path in root.rglob("*.html"):
            # Solo nos interesan rutas que pasen por /apuntes/
            if "/apuntes/" not in html_path.as_posix():
                continue
            rec = process_html(html_path)
            if rec:
                # Aplicar conceptos heredados de ejercicios. Los conceptos
                # específicos del apunte (por url) tienen preferencia sobre
                # los de la unidad, pero ambos se mergean.
                inherited = {}
                # Por unidad
                key = (rec.get("materia"), rec.get("unidad"))
                if key in inheritance["por_unidad"]:
                    for ns, vs in inheritance["por_unidad"][key].items():
                        inherited.setdefault(ns, set()).update(vs)
                # Por URL específica
                if rec["url"] in inheritance["por_url"]:
                    for ns, vs in inheritance["por_url"][rec["url"]].items():
                        inherited.setdefault(ns, set()).update(vs)
                # Mergear con tags existentes (sidecar tiene prioridad si
                # ya hay valor; aquí solo añadimos si no estaba)
                for ns, vs in inherited.items():
                    existing = rec["tags"].get(ns)
                    if existing is None:
                        rec["tags"][ns] = sorted(vs)
                    else:
                        ex_list = existing if isinstance(existing, list) else [existing]
                        rec["tags"][ns] = sorted(set(ex_list) | vs)
                # Recalcular search_text con los nuevos tags
                rec["search_text"] = build_search_text(rec)
                apuntes.append(rec)

    # Deduplicación: si dos entries comparten (materia, unidad, section, lang),
    # significa que es el mismo apunte servido desde subtrees distintos
    # (canonical /aula/... vs mirror /ca/aula/... cuando ambos llevan lang=ca).
    # Preferimos siempre el canonical (URL que empieza por /aula/) sobre los
    # mirrors (/ca/aula/, /en/aula/).
    def url_priority(url: str) -> int:
        if url.startswith("/aula/"):
            return 0  # canonical
        if url.startswith("/ca/aula/"):
            return 1
        if url.startswith("/en/aula/"):
            return 2
        return 3
    by_id = {}
    duplicates_dropped = []
    for a in apuntes:
        existing = by_id.get(a["id"])
        if existing is None or url_priority(a["url"]) < url_priority(existing["url"]):
            if existing is not None:
                duplicates_dropped.append(existing["url"])
            by_id[a["id"]] = a
        else:
            duplicates_dropped.append(a["url"])
    apuntes = list(by_id.values())
    if duplicates_dropped:
        print(f"  · Deduplicados {len(duplicates_dropped)} apuntes (mirrors redundantes)")

    # Ordenamos: por materia, unidad, section_num, lang
    def sort_key(r):
        return (
            r.get("materia") or "",
            r.get("unidad") or "",
            r.get("section_num") or "",
            r.get("lang") or "",
        )
    apuntes.sort(key=sort_key)

    out = {
        "schema_version": 1,
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "count": len(apuntes),
        "apuntes": apuntes,
    }
    OUTPUT.write_text(json.dumps(out, ensure_ascii=False, indent=2))
    print(f"✓ {OUTPUT.relative_to(REPO)}: {len(apuntes)} apuntes "
          f"({sum(1 for a in apuntes if a['tipo']=='seccion')} secciones, "
          f"{sum(1 for a in apuntes if a['tipo']=='index_unidad')} índices unidad, "
          f"{sum(1 for a in apuntes if a['tipo']=='concepto')} conceptos IB, "
          f"{sum(1 for a in apuntes if a['tipo']=='index_general')} hubs)")
    # Resumen por materia / lang
    from collections import Counter
    by_mat = Counter(a["materia"] for a in apuntes)
    by_lang = Counter(a["lang"] for a in apuntes)
    print(f"  Por materia: {dict(by_mat)}")
    print(f"  Por idioma:  {dict(by_lang)}")


if __name__ == "__main__":
    main()
