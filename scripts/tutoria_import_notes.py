#!/usr/bin/env python3
"""Vuelca las notas del curso anterior en las fichas de tutoría.

Lee los PDF de «Resum d'avaluació» (juntas de evaluación) que da el centro
y, cruzándolos con la orla del grupo, deja en cada ficha las notas de las
tres evaluaciones y la ordinaria, materia a materia.

Solo toca a TUS alumnos: de los PDF salen todos los grupos del nivel, pero
únicamente se cargan los que aparecen en la orla. Del resto no se guarda
nada. Ejecuta con --dry-run primero para ver a quién ha emparejado.

IMPORTANTE — dónde acaban los datos
-----------------------------------
Como el resto de scripts de tutoría, no escribe dentro del repositorio: el
destino es Cloudflare D1, y el SQL intermedio va a un directorio temporal
que debes borrar al terminar.

Uso
---
    python3 scripts/tutoria_import_notes.py --orla Orla_2ESO_E.pdf \\
        --notes juntes/*.pdf --grup 2ESO-E --curs 2026-27 [--dry-run]

Formato de los boletines
------------------------
«Resum d'avaluació» horizontal: una fila por evaluación y alumno (1, 2, 3 y
0 = ordinaria), una columna por materia. Las materias se identifican por su
posición horizontal en la página, no por el orden de los valores: las celdas
vacías no dejan hueco en el texto y contarlas desplazaría las notas de
materia. Un alumno sin nota en una materia y evaluación simplemente no la
tiene: no se inventa.
"""
import argparse
import glob
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

# Banda vertical donde viven las etiquetas de materia, giradas 90º. Por
# encima está el título con el grupo y el tutor; por debajo, los datos.
CAP_DALT, CAP_BAIX = 88, 152
TOLERANCIA = 9          # pt; media rejilla, de sobra para no confundir columnas

# Clave canónica por palabra clave de la etiqueta, para que la ficha pueda
# destacar Matemàtiques y ordenar igual entre cursos. Lo que no case aquí
# conserva su nombre tal cual: cada curso aparecen materias nuevas (tallers,
# optativas) y no tiene sentido perderlas por no estar en una lista.
CLAUS = [
    ("matematiques", "mates"), ("llenguacatalana", "cat"),
    ("llenguacastellana", "cast"), ("conandoyle", "angles_cd"),
    ("llenguaestrangera", "angles"), ("fisicaiquimica", "fisquim"),
    ("biologiaigeologia", "biogeo"), ("tecnologia", "tecno"),
    ("cienciessocials", "socials"), ("religio", "religio"),
    ("educaciovisual", "visual"), ("musica", "musica"),
    ("educaciofisica", "efisica"), ("alemany", "alemany"),
    ("competenciapersonal", "comp_personal"), ("competenciadigital", "comp_digital"),
    ("competenciaemprenedoria", "comp_emprenedoria"),
    ("competenciaciutadana", "comp_ciutadana"), ("auladacollida", "acollida"),
    ("manati", "manati"), ("projectemaristes", "projecte"),
    ("digitalitzem", "digital"), ("lectura", "lectura"),
    ("lescorts", "les_corts"), ("edatmoderna", "edat_moderna"),
    # Comodín al final: una columna de pendents repite "estrangera" sin el
    # "Llengua" delante, y sin esto se quedaba sin reconocer.
    ("estrangera", "angles"),
]


def slug(text):
    t = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode()
    t = re.sub(r"[^a-zA-Z0-9]+", "-", t).strip("-").lower()
    return re.sub(r"-{2,}", "-", t)


def paraules(text):
    t = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode().lower()
    return set(re.sub(r"[^a-z ]", " ", t).split())


def columna(x, columnes):
    ancla, clau, nom = min(columnes, key=lambda c: abs(c[0] - x))
    return clau if abs(ancla - x) < TOLERANCIA else None


def clau_de(etiqueta):
    """Clave canónica a partir del texto de la etiqueta, o un slug si es nueva."""
    net = unicodedata.normalize("NFKD", etiqueta).encode("ascii", "ignore").decode()
    net = re.sub(r"[^a-z]", "", net.lower())
    for tros, clau in CLAUS:
        if tros in net:
            return clau
    return slug(etiqueta) or "materia"


def detecta_columnes(pagina):
    """[(x, clau, nom)] — una entrada por columna de materia.

    Cada curso cambian las materias —este año hay tallers y Física i Química
    donde el anterior había Biologia i Geologia—, así que las columnas se
    deducen del propio PDF en vez de fijarlas.

    El ancla la dan los propios datos: las notas caen en una rejilla regular
    y esa posición es inequívoca. Las etiquetas de la cabecera van giradas
    90º y una misma etiqueta ocupa varias líneas seguidas, tan juntas entre
    sí como respecto a la etiqueta vecina, así que agruparlas por su cuenta
    no funciona: se asignan a la columna de datos que tienen debajo.
    """
    ws = pagina.extract_words()

    # 1) Anclas: agrupar las x de los valores numéricos del cuerpo.
    xs = sorted(w["x0"] for w in ws
                if w["top"] >= CAP_BAIX and 230 < w["x0"] < 800
                and re.fullmatch(r"\d{1,2}", w["text"]))
    if not xs:
        return []
    grups, actual = [], [xs[0]]
    for x in xs[1:]:
        if x - actual[-1] <= 6:
            actual.append(x)
        else:
            grups.append(actual)
            actual = [x]
    grups.append(actual)
    ancles = [sum(g) / len(g) for g in grups]

    # 2) Etiquetas: cada trozo de la cabecera va a su ancla más próxima.
    trossos = {i: [] for i in range(len(ancles))}
    for w in ws:
        if not (CAP_DALT <= w["top"] < CAP_BAIX) or w["x0"] <= 230:
            continue
        i = min(range(len(ancles)), key=lambda k: abs(ancles[k] - w["x0"]))
        if abs(ancles[i] - w["x0"]) <= 13:
            trossos[i].append(w)

    conegudes = {c for _, c in CLAUS}
    columnes = []
    for i, ancla in enumerate(ancles):
        bloc = trossos[i]
        # Una etiqueta larga ocupa varias líneas, y cada línea es una franja
        # de x propia dentro de la columna. Hay que reconstruir línea a línea:
        # ordenar todo el bloque por `top` de golpe las entremezcla.
        linies = {}
        for w in bloc:
            linies.setdefault(round(w["x0"] / 4), []).append(w)
        ordenades = [linies[k] for k in sorted(linies)]

        def munta(revessa):
            trocos = []
            for linia in ordenades:
                trocos.append(" ".join(
                    w["text"] for w in sorted(linia, key=lambda w: -w["top"] if revessa else w["top"])))
            return " ".join(trocos)

        # Según la rotación los caracteres salen en un sentido o en el otro.
        # Con materias conocidas lo resuelve la tabla de claves; con las que
        # no lo son (tallers, optatives noves) nos guiamos por la forma: una
        # etiqueta bien leída empieza en mayúscula seguida de minúscula.
        directa, inversa = munta(False), munta(True)
        if clau_de(directa) in conegudes:
            etiqueta = directa
        elif clau_de(inversa) in conegudes:
            etiqueta = inversa
        else:
            sembla = lambda t: bool(re.match(r"[A-ZÀ-Ú][a-zà-ú]", t.replace(" ", "")))
            etiqueta = inversa if (sembla(inversa) and not sembla(directa)) else directa
        clau = clau_de(etiqueta)
        columnes.append((ancla, clau, neteja(clau, etiqueta)))
    return columnes


# Nombre para mostrar de las materias conocidas. El PDF las escribe girando
# cada carácter, así que reconstruirlas letra a letra da "M at e m àti q u e s":
# legible a duras penas y feo en la ficha. Para las que reconocemos ponemos el
# nombre bueno; las nuevas conservan lo que diga el PDF.
NOMS = {
    "mates": "Matemàtiques", "cat": "Llengua catalana i literatura",
    "cast": "Llengua castellana i literatura", "angles": "Llengua estrangera: Anglès",
    "angles_cd": "Anglès · Conan Doyle", "fisquim": "Física i Química",
    "biogeo": "Biologia i Geologia", "tecno": "Tecnologia",
    "socials": "Ciències Socials: Geografia i Història", "religio": "Religió",
    "visual": "Educació Visual i Plàstica", "musica": "Música",
    "efisica": "Educació física", "alemany": "Alemany", "manati": "Manatí",
    "projecte": "Projecte Maristes", "digital": "Digitalitzem-nos!",
    "acollida": "Aula d'Acollida", "comp_personal": "Competència personal i social",
    "comp_digital": "Competència digital", "comp_emprenedoria": "Competència emprenedoria",
    "comp_ciutadana": "Competència ciutadana",
    "lectura": "Lectura", "les_corts": "Les Corts: present, passat i futur",
    "edat_moderna": "Edat Moderna, comença l'espectacle",
}


def neteja(clau, etiqueta):
    """Nombre legible de una materia."""
    if clau in NOMS:
        return NOMS[clau]
    t = re.sub(r"\s+", " ", etiqueta).strip()
    trossos = t.split(" ")
    # Si el PDF la ha dado carácter a carácter, los espacios son ruido: unir
    # y separar por mayúsculas deja algo legible en vez de "L e s C o rt s".
    if len(trossos) > 4 and sum(1 for x in trossos if len(x) <= 2) / len(trossos) > 0.6:
        junt = "".join(trossos)
        return re.sub(r"(?<=[a-zà-ú])(?=[A-ZÀ-Ú])", " ", junt).replace(":", ": ").strip()
    return re.sub(r"([a-zà-ú])i (l|L)", r"\1 i \2", t)


def files_de(pagina):
    """Agrupa las palabras en filas por proximidad vertical.

    Las palabras de una misma línea no comparten `top` exacto: difieren en
    décimas, así que agrupar por el valor redondeado parte las filas.
    """
    cos = sorted((w for w in pagina.extract_words() if w["top"] >= 150),
                 key=lambda w: w["top"])
    files, actual, ref = [], [], None
    for w in cos:
        if ref is None or w["top"] - ref <= 4:
            actual.append(w)
            ref = w["top"] if ref is None else ref
        else:
            files.append(actual)
            actual, ref = [w], w["top"]
    if actual:
        files.append(actual)
    return files


def llegir_notes(path):
    """{nom complet: {'grup', 'sexe', 'pendents', 'aval': {1|2|3|0: {materia: nota}}}}"""
    alumnes, grup = {}, None
    # `actual` vive fuera del bucle de páginas: las cuatro filas de un alumno
    # pueden partirse entre dos páginas, y reiniciarlo en cada una perdía las
    # que quedaban al otro lado del corte.
    actual = None
    # La tabla no cabe a lo ancho de una página: continúa en páginas
    # posteriores con OTRAS materias, y al final repite algunas — son las
    # pendientes del curso anterior, solo con nota ordinaria. Por eso las
    # columnas se detectan en cada página, y cada juego de columnas es un
    # "bloque": la misma materia en dos bloques distintos no es la misma nota.
    blocs, ordre_blocs = {}, []
    with pdfplumber.open(path) as pdf:
        for pagina in pdf.pages:
            columnes = detecta_columnes(pagina)
            if not columnes:
                continue
            firma = tuple(c for _, c, _ in columnes)
            if firma not in blocs:
                blocs[firma] = len(blocs)
                ordre_blocs.append(columnes)
            bloc = blocs[firma]
            if grup is None:
                tot = " ".join(w["text"] for w in pagina.extract_words())
                m = re.search(r"(\dESO-[A-E])", tot)
                if m:
                    grup = m.group(1)
            for fila in files_de(pagina):
                fila = sorted(fila, key=lambda w: w["x0"])
                # La marca de evaluación va primero: sin ella la fila no es de
                # datos, y mirarle el nombre haría que el pie de página
                # («Pàgina: 1 de 4») pasara por alumno y se llevara las filas
                # que continúan al otro lado del corte.
                aval = next((w["text"] for w in fila if 185 < w["x0"] < 198), None)
                if aval not in ("1", "2", "3", "0"):
                    continue
                nom = " ".join(w["text"] for w in fila if 55 < w["x0"] < 186)
                if nom:
                    actual = nom
                if actual is None:
                    continue
                notes = {}
                for w in fila:
                    if not (235 <= w["x0"] <= 800):
                        continue
                    c = columna(w["x0"], columnes)
                    if c and re.fullmatch(r"\d{1,2}", w["text"]):
                        notes[f"{bloc}:{c}"] = int(w["text"])
                a = alumnes.setdefault(actual, {"grup": grup, "aval": {},
                                                 "blocs": ordre_blocs})
                a["blocs"] = ordre_blocs
                a["aval"].setdefault(aval, {}).update(notes)
                sexe = next((w["text"] for w in fila if w["x0"] > 800), None)
                if sexe:
                    a["sexe"] = sexe
                pend = next((w["text"] for w in fila if 218 < w["x0"] < 232), None)
                if aval == "0" and pend and pend.isdigit():
                    a["pendents"] = int(pend)
    return alumnes


def llegir_orla(path):
    """{slug: 'Cognoms Nom'} — reutiliza el lector de la orla."""
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from tutoria_import_orla import read_cells
    from pypdf import PdfReader
    cells = read_cells(PdfReader(path).pages[0])
    return {slug(f"{c['cognoms']} {c['nom']}"): f"{c['cognoms']} {c['nom']}"
            for c in cells.values()}


def emparellar(orla, notes):
    """Cruza por nombre: en la orla van 'Cognoms, Nom' y en las juntas 'Nom Cognoms'."""
    index = {k: paraules(k) for k in notes}
    trobats, sense = {}, []
    for sid, complet in orla.items():
        objectiu = paraules(complet)
        millor, punts = None, 0
        for clau, toks in index.items():
            p = len(objectiu & toks)
            if p > punts:
                millor, punts = clau, p
        # Al menos dos palabras en común: un apellido y un nombre.
        if millor and punts >= 2:
            trobats[sid] = (millor, notes[millor], punts)
        else:
            sense.append(complet)
    return trobats, sense


def sql_str(v):
    return "NULL" if v in (None, "") else "'" + str(v).replace("'", "''") + "'"


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--orla", required=True, help="orla del grupo (PDF)")
    ap.add_argument("--notes", required=True, nargs="+",
                    help="boletines «Resum d'avaluació» (uno o varios PDF)")
    ap.add_argument("--grup", default="2ESO-E")
    ap.add_argument("--curs", default="2026-27")
    ap.add_argument("--db", default="tutoria")
    ap.add_argument("--out", help="directorio de salida (por defecto, un temporal)")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    # El shell suele expandir los comodines antes de llegar aquí. Cuando lo
    # ha hecho, la ruta ya es un fichero y NO hay que volver a pasarla por
    # glob: el butlletí del centro se llama "**Juntes Les Corts…", y esos dos
    # asteriscos son parte del nombre. Interpretarlos como comodines hacía
    # que el fichero dejara de encontrarse.
    fitxers = []
    for patro in args.notes:
        if Path(patro).is_file():
            fitxers.append(patro)
        else:
            fitxers.extend(glob.glob(patro))
    fitxers = sorted(set(fitxers))
    if not fitxers:
        sys.exit("No se ha encontrado ningún boletín en --notes.\n"
                 "Comprueba la ruta:  ls ~/Downloads/*.pdf")

    totes = {}
    for f in sorted(fitxers):
        d = llegir_notes(f)
        g = next(iter(d.values()))["grup"] if d else "?"
        print(f"  {Path(f).name[:44]:<44} {g}  ·  {len(d)} alumnos")
        totes.update(d)
    print(f"\nEn los boletines: {len(totes)} alumnos de todos los grupos.")

    orla = llegir_orla(args.orla)
    print(f"En tu orla: {len(orla)} alumnos.\n")

    trobats, sense = emparellar(orla, totes)
    print(f"Emparejados: {len(trobats)} de {len(orla)}\n")
    for sid, (clau, dades, p) in sorted(trobats.items()):
        aval = dades["aval"]
        # Las notas van con el bloque delante ("0:mates"): la de matemáticas
        # del curso es la del primer bloque donde aparece; las repetidas en
        # bloques posteriores son pendientes y no van en este resumen.
        cel = next((k for k in sorted(
            {k for n in aval.values() for k in n}) if k.endswith(":mates")), None)
        mates = [aval.get(t, {}).get(cel, "·") for t in ("1", "2", "3", "0")] if cel \
            else ["·"] * 4
        print(f"  {sid:<40} [{dades['grup']}]  mates {mates}")
    if sense:
        print("\nSin notas del curso anterior:")
        for s in sense:
            print(f"  · {s}   (normal si repite curso: no estaba en ese nivel)")

    if args.dry_run:
        print("\n--dry-run: no se ha escrito nada.")
        return

    repo = Path(__file__).resolve().parent.parent
    out = Path(args.out).resolve() if args.out else Path(tempfile.mkdtemp(prefix="tutoria-notes-"))
    if out == repo or repo in out.parents:
        sys.exit(f"El directorio de salida está dentro del repositorio ({out}).\n"
                 "Elige uno fuera: estos datos no deben acabar en git.")
    out.mkdir(parents=True, exist_ok=True)

    linies = ["-- Generado por scripts/tutoria_import_notes.py — NO commitear."]
    for sid, (clau, dades, p) in sorted(trobats.items()):
        # Lista ordenada como en el boletín, con el nombre real de cada
        # materia: así la ficha muestra "Taller 1 Robòtica" aunque el año que
        # viene aparezcan asignaturas que hoy no existen. Solo van las que
        # tienen alguna nota.
        #
        # Una materia que reaparece en un bloque posterior es una PENDIENTE
        # del curso anterior: el boletín repite la columna al final y solo la
        # califica en la ordinaria. No es la misma nota, así que va aparte.
        amb_nota = {m for notes in dades["aval"].values() for m in notes}
        taula, vistes = [], set()
        for i, columnes in enumerate(dades.get("blocs", [])):
            for _, clau, nom in columnes:
                cel = f"{i}:{clau}"
                if cel not in amb_nota:
                    continue
                t = {av: dades["aval"][av][cel] for av in ("1", "2", "3", "0")
                     if av in dades["aval"] and cel in dades["aval"][av]}
                pendent = clau in vistes
                vistes.add(clau)
                taula.append({"clau": clau + ("_pendent" if pendent else ""),
                              "nom": nom + (" (pendent del curs anterior)" if pendent else ""),
                              "t": t, **({"pendent": True} if pendent else {})})
        linies.append(
            "UPDATE tutoria_alumnes SET "
            f"curs_anterior = {sql_str(dades['grup'])}, "
            f"notes_anteriors = {sql_str(json.dumps(taula, ensure_ascii=False))}, "
            f"pendents = {dades.get('pendents', 'NULL')}, "
            f"sexe = COALESCE(sexe, {sql_str(dades.get('sexe'))}), "
            f"updated_at = datetime('now') "
            f"WHERE id = {sql_str(sid)} AND grup = {sql_str(args.grup)} "
            f"AND curs = {sql_str(args.curs)};"
        )
    (out / "notes.sql").write_text("\n".join(linies) + "\n", encoding="utf-8")

    (out / "subir.sh").write_text(
        "#!/bin/sh\nset -e\ncd \"$(dirname \"$0\")\"\n"
        f"npx wrangler d1 execute {args.db} --remote --file=notes.sql\n"
        f'echo ""\necho "Listo. Borra este directorio:"\necho "  rm -rf {out}"\n',
        encoding="utf-8")
    (out / "subir.sh").chmod(0o755)

    print(f"\nEscrito en {out}")
    print(f"  notes.sql   ({len(trobats)} alumnos)")
    print(f"  subir.sh    ejecútalo para cargar D1")
    print(f"\nCuando acabes:  rm -rf {out}")


if __name__ == "__main__":
    main()
