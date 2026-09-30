#!/usr/bin/env python3
"""plegar_soluciones.py — Les solucions de docència van SEMPRE plegades, a l'estil de 1r BTL CCSS.

Per què: a /aula/ l'alumnat ha de poder intentar un exercici abans de veure'n la
resolució. Una correcció visible de sortida és un error, igual que un enllaç
trencat. I el plec és el de 1r BTL CCSS: un <details> per apartat, amb la lletra i
l'enunciat a la línia del ▶, i la resolució a sota (.apart / .apart-solution).

Què fa, per a cada pàgina d'apunts o fitxa de /aula/ (arrel, /ca/ i /en/):

  1. Targetes d'exercici (exercise-card / problem-card) amb la solució a la vista
     o plegada amb el botó negre (solution-toggle): les passa a .apart <details>.
     Si l'enunciat és una fórmula, va a la línia del ▶; si és un paràgraf, es
     queda a la vista i el ▶ diu «Veure la solució». Les targetes seguides d'una
     mateixa secció queden dins d'una caixa .exercise.
  2. Caixa d'enunciat (def-box / example-box amb h3 «Enunciado», «Enunciat»,
     «Statement», «Question», «The problem» o «Ejercicio…») seguida de la
     resolució a la vista: la resolució passa a un .apart <details>.
  3. Qualsevol altre botó negre que quedi (reptes, deures…): el mateix, amb
     «Veure la solució».

No es pleguen els exemples de teoria (un «Ejemplo resuelto» o un «Exemple guiat»
formen part de l'explicació) ni el que ja és dins d'un <details>.

Ús:
    python3 scripts/plegar_soluciones.py            # revisa tot /aula/ (es, ca, en)
    python3 scripts/plegar_soluciones.py --apply    # i ho plega
    python3 scripts/plegar_soluciones.py fitxer...  # només aquests fitxers

Sense --apply torna 1 si troba alguna solució a la vista o amb el botó antic,
per poder-lo encadenar abans d'un commit. Els exàmens i la selectivitat tenen
el seu propi plec (per pregunta) i no es toquen. Les pàgines d'exercicis de
classe (build_classe_pages.py) ja surten del generador amb aquest plec.
"""
import glob, os, re, sys

VEURE = {'es': 'Ver la solución', 'ca': 'Veure la solució', 'en': 'See the solution'}
CSS = """<style>/* plec estil CCSS */
.exercise { background: var(--bg); border: 1px solid var(--border); border-radius: 8px; padding: 1rem 1.2rem; margin: 1.2rem 0; }
.exercise-head { display: flex; align-items: baseline; gap: 0.6rem; margin-bottom: 0.4rem; }
.exercise-head .num { display: inline-flex; align-items: center; justify-content: center; min-width: 2rem; height: 1.7rem; padding: 0 0.55rem; background: #10b981; color: #fff; border-radius: 99px; font-family: var(--mono); font-size: 0.78rem; font-weight: 600; }
.exercise-head .ttl { font-size: 0.78rem; color: var(--text-soft); text-transform: uppercase; letter-spacing: 0.06em; font-weight: 600; }
.apart { margin: 0.5rem 0; padding-left: 0.4rem; border-left: 2px solid transparent; transition: border-color 0.15s; }
.apart > details > summary { cursor: pointer; padding: 0.45rem 0.55rem; border-radius: 6px; list-style: none; user-select: none; display: flex; align-items: baseline; gap: 0.5rem; font-size: 0.95rem; transition: background 0.15s; }
.apart > details > summary::-webkit-details-marker { display: none; }
.apart > details > summary::before { content: "▶"; font-size: 0.65em; color: #6366f1; transition: transform 0.15s; display: inline-block; flex-shrink: 0; }
.apart > details[open] > summary::before { transform: rotate(90deg); }
.apart > details > summary:hover { background: rgba(99,102,241,0.06); }
.apart > details[open] { background: rgba(99,102,241,0.04); border-radius: 6px; padding: 0.2rem; }
.apart > details > summary .letter { font-family: var(--mono); font-size: 0.84rem; color: var(--text-soft); flex-shrink: 0; }
.apart > details > summary .stmt { flex: 1; overflow-x: auto; }
.apart-solution { padding: 0.5rem 0.8rem 0.4rem 1.5rem; font-size: 0.92rem; color: var(--text); }
.apart-solution .math-block { background: rgba(16,185,129,0.06); border-left: 3px solid #10b981; padding: 0.4rem 0.7rem; border-radius: 4px; margin: 0.3rem 0; }
.apart-solution p { margin: 0.3rem 0; }
.apart-solution > :first-child { margin-top: 0.2rem; }
[data-theme="dark"] .apart > details[open] { background: rgba(99,102,241,0.10); }
</style>
"""
VOID = {'br', 'img', 'hr', 'input', 'source', 'wbr', 'meta', 'link'}
STMT = re.compile(r'<div class="(?:def-box|example-box)"[^>]*>\s*<h3>(?:Enunciado|Enunciat|Statement|The problem|Question|Ejercicio[^<]*|Exercici[^<]*|Exercise[^<]*)</h3>')
EXAMPLE_H2 = re.compile(r'Ejemplo|Exemple|Example', re.I)
HOMEWORK_H2 = re.compile(r'Deberes|Deures|Homework', re.I)
TOGGLE = re.compile(r'<button class="solution-toggle"[^>]*data-toggles="([^"]+)".*?</button>\s*', re.S)


def tagname(s, i):
    return re.match(r'<\s*([a-zA-Z0-9]+)', s[i:]).group(1).lower()


def elem_end(s, i):
    """Posició just després del tancament de l'element que obre a s[i]."""
    t = tagname(s, i)
    first = re.compile(r'<[^>]*>', re.S).match(s, i)
    if t in VOID or first.group(0).endswith('/>'):
        return first.end()
    pat = re.compile(r'<(/?)%s\b[^>]*?(/?)>' % t, re.I | re.S)
    depth = 0
    for m in pat.finditer(s, i):
        if m.group(1):
            depth -= 1
            if depth == 0:
                return m.end()
        elif not m.group(2):
            depth += 1
    raise ValueError('sense tancar: %s a %d' % (t, i))


def next_node(s, i):
    """Salta espais i comentaris; torna la posició del següent '<'."""
    while True:
        i = re.compile(r'\s*').match(s, i).end()
        if s.startswith('<!--', i):
            i = s.index('-->', i) + 3
            continue
        return i


def inner(s, i):
    """Contingut d'un element (sense les etiquetes d'obertura i tancament)."""
    e = elem_end(s, i)
    a = s.index('>', i) + 1
    b = s.rindex('</', i, e)
    return s[a:b]


def apart(summary, body, pad='        '):
    return (f'{pad}<div class="apart"><details>\n{pad}  <summary>{summary}</summary>\n'
            f'{pad}  <div class="apart-solution">\n{body.strip()}\n{pad}  </div>\n{pad}</details></div>')


def lang_of(s):
    return re.search(r'<html lang="([a-z]+)"', s).group(1)


def strip_toggle(body):
    """Treu el botó i la <section class="solution" hidden> d'un tros, i en torna el contingut."""
    m = TOGGLE.search(body)
    if not m:
        return body
    k = m.end()
    assert re.match(r'<section class="[^"]*solution"', body[k:]), body[k:k + 80]
    return body[:m.start()] + inner(body, k) + body[elem_end(body, k):]


def inside_solution(s, i):
    """Cert si la posició i és dins d'un <details> o d'una resolució plegada amb el botó."""
    for m in re.finditer(r'<details|<section class="[^"]*solution"', s[:i]):
        if elem_end(s, m.start()) > i:
            return True
    return False


# ---------------------------------------------------------------- 1. targetes
def card_to_apart(s, a0, L):
    """Torna (html nou, és_fórmula) per a la targeta que obre a s[a0]."""
    e = elem_end(s, a0)
    card = s[a0:e]
    kind = 'problem' if 'problem-card' in card[:40] else 'exercise'
    body = strip_toggle(inner(s, a0))
    lab_m = re.search(r'<span class="(?:ex|pb)-label">(.*?)</span>', body, re.S)
    label = lab_m.group(1).strip() if lab_m else ''
    body = body[:lab_m.start()] + body[lab_m.end():] if lab_m else body
    st = re.search(r'<div class="(?:ex|pb)-statement"[^>]*>', body)
    stmt_html = inner(body, st.start()).strip()
    rest = body[:st.start()] + body[elem_end(body, st.start()):]
    formula = re.fullmatch(r'<div class="math-block">\s*\$\$(.*?)\$\$\s*</div>', stmt_html, re.S)
    if kind == 'exercise' and formula:
        tex = formula.group(1).strip()
        letter = re.sub(r'^.*?·\s*', '', label.replace('&middot;', '·'))
        summ = (f'<span class="letter">{letter})</span> ' if letter else '') + f'<span class="stmt">$\\displaystyle {tex}$</span>'
        return apart(summ, rest), True, label
    # enunciat de paràgraf: es queda a la vista
    head = ''
    if label:
        num, _, ttl = label.replace('&middot;', '·').partition('·')
        head = (f'          <div class="exercise-head"><span class="num">{num.strip()}</span>'
                + (f'<span class="ttl">{ttl.strip()}</span>' if ttl.strip() else '') + '</div>\n')
    html = (f'        <div class="exercise">\n{head}          <div class="pb-statement">{stmt_html}</div>\n'
            + apart(f'<span class="stmt">{VEURE[L]}</span>', rest, '          ') + '\n        </div>')
    return html, False, label


def convert_cards(s, L):
    n = 0
    while True:
        # només les targetes de primer nivell (no les de dins d'una resolució)
        cards = []
        for m in re.finditer(r'<div class="(?:exercise-card|problem-card)"[^>]*>', s):
            if inside_solution(s, m.start()):
                continue
            if re.search(r'class="(?:ex|pb)-statement"', s[m.start():elem_end(s, m.start())]):
                cards.append(m.start())
        if not cards:
            return s, n
        # agrupa les targetes seguides
        a0 = cards[0]
        group = [a0]
        j = elem_end(s, a0)
        while True:
            k = next_node(s, j)
            if k in cards:
                group.append(k); j = elem_end(s, k)
            else:
                break
        parts, formulas = [], []
        for g in group:
            html, f, _ = card_to_apart(s, g, L)
            parts.append(html); formulas.append(f)
        if all(formulas):
            new = '<div class="exercise">\n' + '\n'.join(parts) + '\n        </div>'
        else:
            new = '\n'.join(p if not f else '<div class="exercise">\n' + p + '\n        </div>' for p, f in zip(parts, formulas)).lstrip()
        s = s[:a0] + new + s[j:]
        n += len(group)


# ------------------------------------------------------- 2. caixes d'enunciat
def convert_statement_boxes(s, L):
    n = 0
    pos = 0
    while True:
        m = STMT.search(s, pos)
        if not m:
            return s, n
        pos = m.end()
        pre = s[:m.start()]
        if inside_solution(s, m.start()):
            continue
        h2s = list(re.finditer(r'<h2[^>]*>(.*?)</h2>', pre, re.S))
        h2t = re.sub('<[^>]+>', '', h2s[-1].group(1)) if h2s else ''
        if EXAMPLE_H2.search(h2t) and not HOMEWORK_H2.search(h2t):
            continue
        j = elem_end(s, m.start())
        a = b = None
        while True:
            k = next_node(s, j)
            if s.startswith('</', k) or s.startswith('<h2', k) or s.startswith('<nav', k) or STMT.match(s, k):
                break
            t = tagname(s, k)
            if a is None and t in ('svg', 'figure'):
                j = elem_end(s, k)
                continue
            if a is None:
                a = k
            j = b = elem_end(s, k)
        if a is None or s.startswith('<div class="apart">', a):
            continue
        region = strip_toggle(s[a:b])
        s = s[:a] + apart(f'<span class="stmt">{VEURE[L]}</span>', region).lstrip() + s[b:]
        n += 1


# --------------------------------------------------------- 3. botons que queden
def convert_toggles(s, L):
    n = 0
    while True:
        m = TOGGLE.search(s)
        if not m:
            return s, n
        k = m.end()
        assert re.match(r'<section class="[^"]*solution"', s[k:]), s[k:k + 80]
        e = elem_end(s, k)
        body = inner(s, k)
        # si la resolució comença amb un títol («Solució pas a pas»), fa de text del ▶
        h = re.match(r'\s*<h3[^>]*>(.*?)</h3>', body, re.S)
        summ = h.group(1).strip() if h else VEURE[L]
        body = body[h.end():] if h else body
        s = s[:m.start()] + apart(f'<span class="stmt">{summ}</span>', body).lstrip() + s[e:]
        n += 1


def fix_css(s):
    # els estils de les targetes també han de valer fora de la targeta
    st = re.search(r'<style>.*?</style>', s, re.S)
    if st:
        blk = st.group(0)
        new = blk.replace('.exercise-card .ex-', ':is(.exercise-card, .apart-solution) .ex-').replace(
            '.problem-card .pb-', ':is(.problem-card, .exercise, .apart-solution) .pb-')
        s = s.replace(blk, new, 1)
    s = re.sub(r'<style>/\* solucions plegades \*/.*?</style>\n', '', s, flags=re.S)
    if 'plec estil CCSS' not in s and '.apart > details > summary' not in s:
        assert s.count('</head>') == 1
        s = s.replace('</head>', CSS + '</head>')
    return s


def process(path, apply):
    s0 = s = open(path, encoding='utf-8').read()
    L = lang_of(s)
    s, n1 = convert_cards(s, L)
    s, n2 = convert_statement_boxes(s, L)
    s, n3 = convert_toggles(s, L)
    n = n1 + n2 + n3
    if not n:
        return 0
    s = fix_css(s)
    if apply:
        open(path, 'w', encoding='utf-8').write(s)
    print(f'{n:3d} (targetes {n1}, enunciats {n2}, botons {n3}) {path}')
    return n


if __name__ == '__main__':
    os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    apply = '--apply' in sys.argv
    files = [p for p in sys.argv[1:] if p != '--apply']
    if not files:
        files = sorted(f for arrel in ('', 'ca/', 'en/')
                       for f in glob.glob(arrel + 'aula/*/**/*.html', recursive=True)
                       if '/examenes/' not in f and '/selectivitat/' not in f)
    tot = sum(process(p, apply) for p in files)
    if apply:
        print('Plegades: %d solucions.' % tot)
    elif tot:
        print('ERROR: %d solucions a la vista o amb el botó antic. Plega-les amb --apply.' % tot)
        sys.exit(1)
    else:
        print('✓ Totes les solucions plegades amb el ▶ de 1r BTL CCSS.')
