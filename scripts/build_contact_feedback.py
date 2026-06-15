#!/usr/bin/env python3
"""
build_contact_feedback.py — regenera el bloque `var FB={...};` del formulario
"Sobre la web" en /contacto/, /ca/contacto/ y /en/contacto/.

- CURSOS: lista curada y completa (abajo). Incluye también cursos que Àlex no
  imparte ahora mismo; para añadir/quitar uno, edita COURSES.
- NOTAS y PAPERS: se descubren del disco y se leen sus títulos en cada idioma.
  Así el desplegable nunca se queda obsoleto al publicar contenido nuevo.

Uso:  python3 scripts/build_contact_feedback.py [--dry-run]
Idempotente: correrlo dos veces seguidas no cambia nada.
"""
import os, re, json, sys, html

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LANGS = {"es": "", "ca": "ca/", "en": "en/"}

# Etiquetas de sección por idioma
SECTION = {
    "docencia":  {"es": "Docencia",  "ca": "Docència", "en": "Teaching"},
    "notas":     {"es": "Notas",     "ca": "Notes",    "en": "Notes"},
    "doctorado": {"es": "Doctorado", "ca": "Doctorat", "en": "PhD"},
}

# --- CURSOS (lista curada y completa; edita aquí para añadir/quitar) ---
COURSES = [
    {"es": "IB Mathematics AI",            "ca": "IB Mathematics AI",            "en": "IB Mathematics AI"},
    {"es": "Mat. Aplicadas CCSS · 1r BTL", "ca": "Mat. Aplicades CCSS · 1r BTL", "en": "Applied Maths CCSS · 1st BTL"},
    {"es": "Mat. Aplicadas CCSS · 2n BTL", "ca": "Mat. Aplicades CCSS · 2n BTL", "en": "Applied Maths CCSS · 2nd BTL"},
    {"es": "Científico · 1r BTL",          "ca": "Científic · 1r BTL",           "en": "Science track · 1st BTL"},
    {"es": "Científico · 2n BTL",          "ca": "Científic · 2n BTL",           "en": "Science track · 2nd BTL"},
    {"es": "Matemáticas 1.º ESO",          "ca": "Matemàtiques 1r ESO",          "en": "Maths · 1r ESO"},
    {"es": "Matemáticas 2.º ESO",          "ca": "Matemàtiques 2n ESO",          "en": "Maths · 2n ESO"},
    {"es": "Matemáticas 3.º ESO",          "ca": "Matemàtiques 3r ESO",          "en": "Maths · 3r ESO"},
    {"es": "Matemáticas 4.º ESO",          "ca": "Matemàtiques 4t ESO",          "en": "Maths · 4t ESO"},
    {"es": "Cangur",                       "ca": "Cangur",                       "en": "Cangur"},
    {"es": "Selectividad (PAU)",           "ca": "Selectivitat (PAU)",           "en": "University entrance (PAU)"},
]

# Extras fijos del doctorado (además de los papers descubiertos)
DOCTORADO_EXTRA = [
    {"es": "Visualizaciones",   "ca": "Visualitzacions", "en": "Visualizations"},
    {"es": "Líneas de trabajo", "ca": "Línies de treball", "en": "Research lines"},
]

TITLE_RE = re.compile(r"<title>(.*?)</title>", re.S | re.I)
FB_RE = re.compile(r"var FB=\{.*?\};", re.S)


def read_title(rel_path):
    """Devuelve el <title> sin el sufijo ' — Àlex Reyes', o None si no existe."""
    path = os.path.join(ROOT, rel_path)
    if not os.path.isfile(path):
        return None
    with open(path, encoding="utf-8") as f:
        m = TITLE_RE.search(f.read())
    if not m:
        return None
    t = html.unescape(m.group(1)).strip()
    for sep in (" — Àlex Reyes", " — Alex Reyes", "— Àlex Reyes"):
        if t.endswith(sep):
            t = t[: -len(sep)].strip()
            break
    return t


def hub_order(rel_index, base):
    """Slugs en el orden en que aparecen en una página índice (hub)."""
    path = os.path.join(ROOT, rel_index)
    if not os.path.isfile(path):
        return []
    with open(path, encoding="utf-8") as f:
        html = f.read()
    seen, out = set(), []
    for slug in re.findall(r'href="/%s([a-z0-9-]+)/"' % re.escape(base), html):
        if slug not in seen:
            seen.add(slug)
            out.append(slug)
    return out


def discover_slugs(rel_dir, rel_index, base):
    """Carpetas con index.html en rel_dir, ordenadas según el hub y luego alfabético."""
    d = os.path.join(ROOT, rel_dir)
    folders = []
    if os.path.isdir(d):
        for name in sorted(os.listdir(d)):
            if os.path.isfile(os.path.join(d, name, "index.html")):
                folders.append(name)
    order = hub_order(rel_index, base)
    ordered = [s for s in order if s in folders]
    ordered += [s for s in folders if s not in ordered]
    return ordered


def titles_for(slugs, dir_template):
    """Para cada slug, dict {lang: titulo} leyendo cada idioma (con fallback a ES)."""
    items = []
    for slug in slugs:
        es = read_title(dir_template.format(prefix="", slug=slug))
        if not es:
            continue
        row = {}
        for lang, prefix in LANGS.items():
            row[lang] = read_title(dir_template.format(prefix=prefix, slug=slug)) or es
        items.append(row)
    return items


def build_fb(lang, courses, notas, papers):
    doc_items = ["Paper · " + p[lang] for p in papers]
    doc_items += [e[lang] for e in DOCTORADO_EXTRA]
    return {
        "docencia":  {"label": SECTION["docencia"][lang],  "color": "teaching", "items": [c[lang] for c in courses]},
        "notas":     {"label": SECTION["notas"][lang],     "color": "notes",    "items": [n[lang] for n in notas]},
        "doctorado": {"label": SECTION["doctorado"][lang], "color": "research", "items": doc_items},
    }


def main():
    dry = "--dry-run" in sys.argv

    nota_slugs = discover_slugs("notas", "notas/index.html", "notas/")
    notas = titles_for(nota_slugs, "{prefix}notas/{slug}/index.html")

    paper_slugs = discover_slugs("doctorado/papers", "doctorado/index.html", "doctorado/papers/")
    papers = titles_for(paper_slugs, "{prefix}doctorado/papers/{slug}/index.html")

    changed = 0
    for lang, prefix in LANGS.items():
        rel = "%scontacto/index.html" % prefix
        path = os.path.join(ROOT, rel)
        if not os.path.isfile(path):
            print("  ! no existe %s" % rel)
            continue
        with open(path, encoding="utf-8") as f:
            html = f.read()
        fb = build_fb(lang, COURSES, notas, papers)
        new_line = "var FB=" + json.dumps(fb, ensure_ascii=False, separators=(",", ":")) + ";"
        if not FB_RE.search(html):
            print("  ! no encuentro 'var FB={...};' en %s" % rel)
            continue
        new_html = FB_RE.sub(lambda _m: new_line, html, count=1)
        if new_html != html:
            changed += 1
            if not dry:
                with open(path, "w", encoding="utf-8") as f:
                    f.write(new_html)
            print("  %s %s" % ("(dry) " if dry else "✓", rel))
        else:
            print("  = %s (sin cambios)" % rel)

    print("\nCursos: %d  ·  Notas: %d  ·  Papers: %d  ·  Archivos %s: %d"
          % (len(COURSES), len(notas), len(papers),
             "a cambiar" if dry else "actualizados", changed))


if __name__ == "__main__":
    main()
