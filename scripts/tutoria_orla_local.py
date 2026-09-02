#!/usr/bin/env python3
"""Genera una orla de tutoría en HTML, para uso LOCAL.

Por qué local
-------------
Los nombres y las fotos de los alumnos son datos personales de menores.
No van a la web ni a ningún servicio: este script produce un único fichero
HTML autocontenido —las fotos van incrustadas dentro— que se abre con doble
clic desde tu propio equipo. Nada sale de la máquina.

El fichero se escribe FUERA del repositorio (el repo es público). Si le
pasas un --out dentro del repo, el script se niega.

Uso
---
    python3 scripts/tutoria_orla_local.py Orla_2ESO_E.pdf \\
        --grup 2ESO-E --curs 2026-27 [--out DIR]

Sin --out escribe en ~/Tutoria (se crea si no existe). Genera ahí
orla-2ESO-E.html: ábrelo en el navegador y verás la orla; al pulsar en un
alumno, su ficha con contacto y seguimiento editables.

Las notas se guardan en el almacenamiento local del navegador. Como eso
puede perderse (borrar datos de navegación, otro equipo, otro navegador),
la ficha lleva botones de exportar e importar: guarda la copia JSON en una
carpeta tuya con el resto de material de tutoría.

Formato de orla soportado
-------------------------
La "Orla H" de Untis/SAGA: rejilla de 5 columnas x 6 filas, numerada por
columnas (1-6 la primera, 7-12 la segunda...). Cada celda lleva el numero,
el grupo, los apellidos y el nombre, con la foto a la derecha. Los alumnos
sin foto simplemente no tienen imagen en esa celda.
"""
import argparse
import base64
import html
import json
import re
import sys
import unicodedata
from collections import Counter
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

    Cada celda es: el número de lista y, justo debajo, una o más líneas de
    apellidos y una última con el nombre. El paso entre filas se deduce de
    los propios números en vez de fijarlo.
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
    # así que se saca del texto en orden de lectura: "23 2ESO-E (R)".
    marcas = {int(n): f"({m})"
              for n, m in re.findall(r"(\d{1,2})\s+\S*ESO\S*\s*\((\w)\)", plano)}

    nums = sorted(
        ((x, y, int(t)) for x, y, t in toks
         if t.isdigit() and 1 <= int(t) <= COLS * FILES_PER_COL),
        key=lambda r: r[2],
    )
    if len(nums) < 2:
        sys.exit("No se han encontrado números de alumno; ¿es una orla 'H'?")

    ys_por_col = {}
    for x, y, n in nums:
        ys_por_col.setdefault(x, []).append(y)
    saltos = [b - a for ys in ys_por_col.values()
              for a, b in zip(sorted(ys), sorted(ys)[1:]) if b > a]
    paso = min(saltos) if saltos else 3000

    cells = {}
    for nx, ny, n in nums:
        linies = sorted(
            ((y, t) for x, y, t in toks
             if nx < x < nx + paso and ny < y < ny + paso and not t.isdigit()),
            key=lambda r: r[0],
        )
        textos = [t for _, t in linies]
        if len(textos) < 2:
            continue
        cells[n] = {"cognoms": " ".join(textos[:-1]),
                    "nom": textos[-1],
                    "marca": marcas.get(n, "")}
    return cells


def read_photos(page):
    """Devuelve {nº alumno: nombre de XObject} usando la posición de cada imagen."""
    raw = page.get_contents().get_data().decode("latin-1")
    placed = re.findall(
        r"q\s+([-\d.]+) 0 0 ([-\d.]+) ([-\d.]+) ([-\d.]+) cm\s*/(\w+) Do", raw)
    if not placed:
        return {}
    boxes = [(float(x), float(y), float(w), abs(float(h)), n) for w, h, x, y, n in placed]
    # El logo del centro tiene otras proporciones: nos quedamos con el tamaño
    # que más se repite, que es el de las fotos de alumno.
    comu = Counter((round(w), round(h)) for _, _, w, h, _ in boxes).most_common(1)[0][0]
    fotos = [b for b in boxes if (round(b[2]), round(b[3])) == comu]
    xs = sorted({round(b[0]) for b in fotos})
    ys = sorted({round(b[1]) for b in fotos})
    out = {}
    for x, y, w, h, name in fotos:
        col = min(range(len(xs)), key=lambda i: abs(xs[i] - x))
        row = min(range(len(ys)), key=lambda i: abs(ys[i] - y))
        out[col * FILES_PER_COL + row + 1] = name
    return out


def jpeg_data_uri(page, xname):
    """El JPEG incrustado, tal cual, como data: URI."""
    # El content stream nombra las imágenes sin barra ("X3"); la clave del
    # diccionario de recursos sí la lleva ("/X3").
    xobj = page["/Resources"]["/XObject"][f"/{xname}"].get_object()
    filt = xobj.get("/Filter")
    filt = [filt] if not isinstance(filt, list) else filt
    if "/DCTDecode" not in [str(f) for f in filt]:
        raise ValueError(f"{xname}: se esperaba JPEG, hay {filt}")
    data = xobj.get_data() if hasattr(xobj, "get_data") else xobj._data
    return "data:image/jpeg;base64," + base64.b64encode(data).decode()


PAGINA = """<!DOCTYPE html>
<html lang="ca">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta name="robots" content="noindex, nofollow, noarchive">
<title>Orla __GRUP__ &middot; Tutoria __CURS__</title>
<style>
  :root {
    --bg:#fff; --bg-sub:#f7f7f8; --text:#18181b; --soft:#52525b; --faint:#a1a1aa;
    --border:#e4e4e7; --accent:#0f766e; --warn:#b45309;
  }
  @media (prefers-color-scheme: dark) {
    :root { --bg:#111113; --bg-sub:#18181b; --text:#f4f4f5; --soft:#a1a1aa;
            --faint:#71717a; --border:#27272a; --accent:#2dd4bf; --warn:#fbbf24; }
  }
  * { box-sizing:border-box; }
  body { margin:0; background:var(--bg); color:var(--text); line-height:1.55;
    font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif; }
  .wrap { max-width:1100px; margin:0 auto; padding:2rem 1.25rem 4rem; }
  header { display:flex; justify-content:space-between; align-items:baseline; gap:1rem; flex-wrap:wrap; }
  .lbl { font-size:.72rem; font-weight:600; letter-spacing:.08em; text-transform:uppercase; color:var(--soft); }
  h1 { font-size:1.6rem; margin:.25rem 0 0; }
  .avis { display:flex; gap:.7rem; padding:.8rem 1rem; margin:1.5rem 0; font-size:.88rem;
    border:1px solid var(--border); border-left:3px solid var(--accent);
    border-radius:6px; background:var(--bg-sub); color:var(--soft); }
  .bar { display:flex; gap:.75rem; align-items:center; flex-wrap:wrap; margin-bottom:1.25rem; }
  input[type=search], input[type=text], textarea {
    padding:.55rem .75rem; border:1px solid var(--border); border-radius:6px;
    background:var(--bg); color:var(--text); font:inherit; font-size:.94rem; }
  input[type=search] { flex:1; min-width:200px; }
  .cnt { font-size:.85rem; color:var(--faint); }
  button { padding:.5rem 1rem; border:1px solid var(--border); border-radius:6px;
    background:var(--bg-sub); color:var(--text); font:inherit; font-size:.88rem; cursor:pointer; }
  button:hover { border-color:var(--faint); }
  button.pri { background:var(--accent); border-color:var(--accent); color:#fff; font-weight:600; }
  .orla { display:grid; grid-template-columns:repeat(auto-fill,minmax(138px,1fr)); gap:1rem; }
  .al { text-align:left; padding:0; overflow:hidden; background:var(--bg-sub);
    border:1px solid var(--border); border-radius:8px; cursor:pointer; display:block; width:100%; }
  .al:hover { border-color:var(--accent); }
  .al img, .al .buit { width:100%; aspect-ratio:127/192; object-fit:cover; display:block; }
  .al .buit { display:flex; align-items:center; justify-content:center; font-size:2rem; color:var(--faint); }
  .al .cos { padding:.55rem .7rem; }
  .num { font-family:ui-monospace,SFMono-Regular,Menlo,monospace; font-size:.72rem; color:var(--faint); }
  .marca { font-family:ui-monospace,SFMono-Regular,Menlo,monospace; font-size:.68rem; color:var(--warn); }
  .nom { font-size:.88rem; font-weight:600; margin:.1rem 0 0; }
  .cog { font-size:.79rem; color:var(--soft); }
  .te-notes::after { content:"●"; color:var(--accent); font-size:.7rem; margin-left:.3rem; }
  dialog { border:1px solid var(--border); border-radius:10px; padding:0; background:var(--bg);
    color:var(--text); max-width:760px; width:calc(100% - 2rem); }
  dialog::backdrop { background:rgba(0,0,0,.55); }
  .fitxa { display:grid; grid-template-columns:150px 1fr; gap:1.5rem; padding:1.5rem; }
  @media (max-width:620px) { .fitxa { grid-template-columns:1fr; } }
  .fitxa img, .fitxa .buit { width:100%; aspect-ratio:127/192; object-fit:cover;
    border-radius:8px; border:1px solid var(--border); }
  .fitxa .buit { display:flex; align-items:center; justify-content:center;
    font-size:3rem; color:var(--faint); background:var(--bg-sub); }
  .camp { margin-bottom:1.1rem; }
  .camp label { display:block; font-size:.72rem; font-weight:600; text-transform:uppercase;
    letter-spacing:.05em; color:var(--soft); margin-bottom:.35rem; }
  .camp input, .camp textarea { width:100%; }
  .camp textarea { min-height:170px; resize:vertical; line-height:1.6; }
  .peu { display:flex; gap:.6rem; align-items:center; flex-wrap:wrap; }
  .estat { font-size:.84rem; color:var(--faint); margin-left:auto; }
  footer { margin-top:2.5rem; padding-top:1.25rem; border-top:1px solid var(--border);
    font-size:.8rem; color:var(--faint); }
</style>
</head>
<body>
<div class="wrap">
  <header>
    <div>
      <span class="lbl">Tutoria &middot; Curs __CURS__</span>
      <h1>__GRUP__</h1>
    </div>
    <div class="bar" style="margin:0">
      <button id="exporta">Exportar còpia</button>
      <button id="importa">Importar còpia</button>
    </div>
  </header>

  <div class="avis">
    <span aria-hidden="true">&#128274;</span>
    <span><strong>Fitxer local amb dades de menors.</strong> No el pugis al núvol,
    ni al correu, ni a cap web. Guarda&#39;l xifrat si el portes en un port&agrave;til.</span>
  </div>

  <div class="bar">
    <input id="q" type="search" placeholder="Cerca per nom o cognom&hellip;" autocomplete="off">
    <span class="cnt" id="cnt"></span>
  </div>

  <div class="orla" id="orla"></div>

  <footer>
    Generat des de l&#39;orla del centre. Les notes es desen en aquest navegador;
    fes servir <em>Exportar c&ograve;pia</em> per guardar-les en un fitxer.
  </footer>
</div>

<dialog id="dlg"><div id="dlg-cos"></div></dialog>
<input type="file" id="fitxer" accept="application/json" hidden>

<script>
const ALUMNES = __DADES__;
const CLAU = "tutoria:" + __CLAU__;

const esc = s => String(s ?? "").replace(/[&<>"']/g, c =>
  ({ "&":"&amp;", "<":"&lt;", ">":"&gt;", '"':"&quot;", "'":"&#39;" }[c]));
const norm = s => String(s || "").normalize("NFD").replace(/\\p{Diacritic}/gu, "").toLowerCase();

// ── Persistència ────────────────────────────────────────────────
// localStorage és el que hi ha en un fitxer local. Pot fallar (Safari amb
// file://, navegació privada) i es pot perdre: per això hi ha exportació.
let NOTES = {};
let potDesar = true;
try {
  NOTES = JSON.parse(localStorage.getItem(CLAU) || "{}");
} catch (e) { potDesar = false; }

function desa() {
  if (!potDesar) return false;
  try { localStorage.setItem(CLAU, JSON.stringify(NOTES)); return true; }
  catch (e) { potDesar = false; return false; }
}

// ── Orla ────────────────────────────────────────────────────────
function pinta(list) {
  document.getElementById("cnt").textContent =
    list.length === ALUMNES.length ? list.length + " alumnes"
                                   : list.length + " de " + ALUMNES.length;
  document.getElementById("orla").innerHTML = list.map(a => {
    const n = NOTES[a.id] || {};
    const te = (n.notes || n.contacte) ? " te-notes" : "";
    const img = a.foto ? '<img src="' + a.foto + '" alt="">'
                       : '<div class="buit" aria-hidden="true">&#128100;</div>';
    return '<button class="al" data-id="' + esc(a.id) + '">' + img +
      '<div class="cos"><span class="num">' + a.num + '</span>' +
      (a.marca ? ' <span class="marca">' + esc(a.marca) + '</span>' : '') +
      '<p class="nom' + te + '">' + esc(a.nom) + '</p>' +
      '<div class="cog">' + esc(a.cognoms) + '</div></div></button>';
  }).join("");
}

document.getElementById("orla").addEventListener("click", e => {
  const b = e.target.closest(".al");
  if (b) obreFitxa(b.dataset.id);
});

document.getElementById("q").addEventListener("input", e => {
  const q = norm(e.target.value.trim());
  pinta(!q ? ALUMNES : ALUMNES.filter(a => norm(a.nom + " " + a.cognoms).includes(q)));
});

// ── Fitxa ───────────────────────────────────────────────────────
const dlg = document.getElementById("dlg");

function obreFitxa(id) {
  const a = ALUMNES.find(x => x.id === id);
  if (!a) return;
  const n = NOTES[id] || {};
  const img = a.foto ? '<img src="' + a.foto + '" alt="">'
                     : '<div class="buit" aria-hidden="true">&#128100;</div>';
  document.getElementById("dlg-cos").innerHTML =
    '<div class="fitxa"><div>' + img + '</div><div>' +
      '<span class="lbl">' + esc(a.grup) + ' &middot; n&ordm; ' + a.num +
        (a.marca ? ' &middot; ' + esc(a.marca) : '') + '</span>' +
      '<h2 style="margin:.2rem 0 .1rem;font-size:1.35rem">' + esc(a.nom) + '</h2>' +
      '<p style="margin:0 0 1.2rem;color:var(--soft)">' + esc(a.cognoms) + '</p>' +
      '<div class="camp"><label for="f-contacte">Contacte de la fam&iacute;lia</label>' +
        '<input id="f-contacte" type="text" value="' + esc(n.contacte || "") +
        '" placeholder="Tel&egrave;fon, correu, qui recull&hellip;"></div>' +
      '<div class="camp"><label for="f-notes">Seguiment de tutoria</label>' +
        '<textarea id="f-notes" placeholder="Entrevistes, acords, incid&egrave;ncies, evoluci&oacute;&hellip;">' +
        esc(n.notes || "") + '</textarea></div>' +
      '<div class="peu"><button class="pri" id="f-desa">Desar</button>' +
        '<button id="f-tanca">Tancar</button>' +
        '<span class="estat" id="f-estat">' +
        (n.updated ? "Editat: " + esc(n.updated) : "") + '</span></div>' +
    '</div></div>';

  document.getElementById("f-tanca").onclick = () => dlg.close();
  document.getElementById("f-desa").onclick = () => {
    NOTES[id] = {
      contacte: document.getElementById("f-contacte").value,
      notes: document.getElementById("f-notes").value,
      updated: new Date().toLocaleString("ca-ES", { dateStyle: "short", timeStyle: "short" }),
    };
    const est = document.getElementById("f-estat");
    est.textContent = desa()
      ? "Desat"
      : "No s'ha pogut desar en aquest navegador \\u2014 exporta la c\\u00f2pia";
    pinta(ALUMNES);
  };
  dlg.showModal();
}

// ── Exportar / importar ─────────────────────────────────────────
document.getElementById("exporta").onclick = () => {
  const blob = new Blob([JSON.stringify(NOTES, null, 2)], { type: "application/json" });
  const a = document.createElement("a");
  a.href = URL.createObjectURL(blob);
  a.download = "fitxes-" + __CLAU__ + ".json";
  a.click();
  URL.revokeObjectURL(a.href);
};

document.getElementById("importa").onclick = () => document.getElementById("fitxer").click();
document.getElementById("fitxer").addEventListener("change", e => {
  const f = e.target.files[0];
  if (!f) return;
  const r = new FileReader();
  r.onload = () => {
    try {
      const dades = JSON.parse(r.result);
      // Fusiona: no esborra el que ja hi ha, però la còpia mana en cas de xoc.
      NOTES = Object.assign({}, NOTES, dades);
      desa();
      pinta(ALUMNES);
      alert("Importades " + Object.keys(dades).length + " fitxes.");
    } catch (err) { alert("El fitxer no és una còpia vàlida."); }
  };
  r.readAsText(f);
});

pinta(ALUMNES);
if (!potDesar) {
  document.querySelector(".avis span:last-child").innerHTML +=
    "<br><strong>Aten&ccedil;i&oacute;:</strong> aquest navegador no permet desar en local. " +
    "Fes servir <em>Exportar c&ograve;pia</em> despr&eacute;s de cada edici&oacute;.";
}
</script>
</body>
</html>
"""


def main():
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("pdf", help="orla en PDF (no la copies dentro del repo)")
    ap.add_argument("--grup", default="2ESO-E")
    ap.add_argument("--curs", default="2026-27")
    ap.add_argument("--out", help="directorio de salida (por defecto, ~/Tutoria)")
    ap.add_argument("--dry-run", action="store_true", help="solo listar, no escribir")
    args = ap.parse_args()

    page = PdfReader(args.pdf).pages[0]
    cells = read_cells(page)
    fotos = read_photos(page)
    if not cells:
        sys.exit("No se ha reconocido ningún alumno.")

    print(f"Alumnos reconocidos: {len(cells)}   ·   con foto: {len(fotos)}")
    sin = sorted(set(cells) - set(fotos))
    if sin:
        print("Sin foto: " + ", ".join(f"nº{n}" for n in sin))

    alumnes = []
    for n in sorted(cells):
        c = cells[n]
        alumnes.append({
            "id": slug(f"{c['cognoms']} {c['nom']}"),
            "num": n,
            "grup": args.grup,
            "curs": args.curs,
            "cognoms": c["cognoms"],
            "nom": c["nom"],
            "marca": c["marca"],
            "foto": jpeg_data_uri(page, fotos[n]) if n in fotos else "",
        })
        print(f"  {n:>3}  {c['cognoms']}, {c['nom']} {c['marca']}")

    if args.dry_run:
        print("\n--dry-run: no se ha escrito nada.")
        return

    repo = Path(__file__).resolve().parent.parent
    # Por defecto, ~/Tutoria: es un fichero que se usa todo el curso, así que
    # no puede vivir en un temporal que el sistema limpia.
    out = Path(args.out).resolve() if args.out else (Path.home() / "Tutoria")
    if out == repo or repo in out.parents:
        sys.exit(f"El directorio de salida está dentro del repositorio ({out}).\n"
                 "Elige uno fuera: estos datos no deben acabar en git.")
    out.mkdir(parents=True, exist_ok=True)

    clau = f"{args.grup}-{args.curs}"
    pagina = (PAGINA
              .replace("__GRUP__", html.escape(args.grup))
              .replace("__CURS__", html.escape(args.curs))
              .replace("__CLAU__", json.dumps(clau))
              .replace("__DADES__", json.dumps(alumnes, ensure_ascii=False)))

    dest = out / f"orla-{args.grup}.html"
    dest.write_text(pagina, encoding="utf-8")

    mida = dest.stat().st_size / 1024
    print(f"\nEscrito: {dest}  ({mida:.0f} KB)")
    print("\nÁbrelo con doble clic. Las fotos van dentro del propio fichero, así que")
    print("puedes moverlo o copiarlo y sigue funcionando, también sin conexión.")
    print("\nLas notas se guardan en el navegador con que lo abras: usa siempre el")
    print("mismo, y de vez en cuando pulsa «Exportar còpia» para tener un respaldo.")
    print("\nNo lo subas a la web, ni al correo, ni a ninguna nube.")


if __name__ == "__main__":
    main()
