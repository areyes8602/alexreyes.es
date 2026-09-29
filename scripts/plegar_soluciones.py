#!/usr/bin/env python3
"""plegar_soluciones.py — Les solucions de docència van SEMPRE plegades.

Per què: a /aula/ l'alumnat ha de poder intentar un exercici abans de veure'n la
resolució. Una correcció visible de sortida és un error, igual que un enllaç
trencat. Aquest script les caça i, amb --apply, les plega amb el botó
«Mostra la solució» (toggleSolucion, de /assets/js/examenes.js).

Dos patrons:
  1. Targetes d'exercici (exercise-card / problem-card): tot el que ve després de
     l'enunciat (ex-statement / pb-statement) queda dins d'un bloc plegat.
  2. Caixa d'enunciat (def-box / example-box / theorem-box amb h3 «Enunciado»,
     «Enunciat», «Statement» o «Ejercicio…») seguida de la resolució: els germans
     que vénen després (llevat de la figura de l'enunciat) queden plegats, fins al
     final de la secció. No es toca si el h2 de la secció és un «Ejemplo».

No es pleguen els exemples de teoria (un «Ejemplo resuelto» o un «Exemple guiat»
formen part de l'explicació) ni el que ja està dins d'un <details> o d'un bloc
.solution[hidden].

Ús:
    python3 scripts/plegar_soluciones.py            # revisa tot /aula/ (es, ca, en)
    python3 scripts/plegar_soluciones.py --apply    # i les plega
    python3 scripts/plegar_soluciones.py fitxer...  # només aquests fitxers

Sense --apply torna 1 si troba alguna solució visible, per poder-lo encadenar
abans d'un commit.
"""
import re, sys

LABELS = {'es': ('Mostrar la solución', 'Ocultar la solución'),
          'ca': ('Mostra la solució', 'Amaga la solució'),
          'en': ('Show solution', 'Hide solution')}
CSS = """<style>/* solucions plegades */
.exercise-card .solution, .problem-card .solution { padding: 1rem 1.2rem; margin-top: 0.6rem; background: var(--bg); }
.exercise-card .solution-toggle, .problem-card .solution-toggle { margin: 0.4rem 0 0; }
.solution > .step:first-child, .solution > .example-box:first-child { margin-top: 0; }
</style>
"""
SVG = '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="6 9 12 15 18 9"/></svg>'
VOID = {'br', 'img', 'hr', 'input', 'source', 'wbr', 'meta', 'link'}
STMT = re.compile(r'<div class="(?:def-box|example-box)"[^>]*>\s*<h3>(?:Enunciado|Enunciat|Statement|The problem|Question|Ejercicio[^<]*|Exercici[^<]*|Exercise[^<]*)</h3>')
EXAMPLE_H2 = re.compile(r'Ejemplo|Exemple|Example', re.I)
HOMEWORK_H2 = re.compile(r'Deberes|Deures|Homework', re.I)


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
        m = re.compile(r'\s*').match(s, i); i = m.end()
        if s.startswith('<!--', i):
            i = s.index('-->', i) + 3
            continue
        return i


def lang_of(s):
    return re.search(r'<html lang="([a-z]+)"', s).group(1)


def wrap(s, a, b, sid, L):
    show, hide = LABELS[L]
    btn = (f'<button class="solution-toggle" data-toggles="{sid}" data-show-label="{show}" '
           f'data-hide-label="{hide}" onclick="toggleSolucion(\'{sid}\')"><span class="toggle-label">{show}</span>{SVG}</button>\n'
           f'<section class="solution" id="{sid}" hidden>\n')
    return s[:a] + btn + s[a:b] + '\n</section>' + s[b:]


def find_regions(s):
    regs = []
    # 1. targetes
    for m in re.finditer(r'<div class="(exercise-card|problem-card)"[^>]*>', s):
        a0 = m.start(); e = elem_end(s, a0)
        card = s[a0:e]
        if 'solution-toggle' in card:
            continue
        st = re.compile(r'<div class="(?:ex-statement|pb-statement)"[^>]*>').search(s, a0, e)
        if not st:
            continue
        a = next_node(s, elem_end(s, st.start()))
        b = s.rindex('</div>', a0, e)
        inner = s[a:b]
        if not re.search(r'class="(?:ex-steps|ex-final|pb-steps|pb-final)"', inner):
            continue
        b = len(s[:b].rstrip()) if s[:b].rstrip().endswith('>') else b
        regs.append((a, b, 'targeta'))
    # 2. caixes d'enunciat
    for m in STMT.finditer(s):
        h2s = [x for x in re.finditer(r'<h2[^>]*>(.*?)</h2>', s[:m.start()], re.S)]
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
        if a is None or 'solution-toggle' in s[a:b]:
            continue
        regs.append((a, b, 'enunciat'))
    return sorted(regs)


def absorb_notes(s):
    """Fica dins la targeta les notes que la segueixen i que en donen la solució."""
    for m in reversed(list(re.finditer(r'<div class="(?:exercise-card|problem-card)"', s))):
        e = elem_end(s, m.start()); k = next_node(s, e)
        if not (s.startswith('<p class="note">', k) or s.startswith('<div class="tip-box">', k)):
            continue
        ke = elem_end(s, k); node = s[k:ke]
        if not re.search(r'Comprobación|Comprovació|Check:|<strong>34g</strong>', node):
            continue
        close = s.rindex('</div>', m.start(), e)
        s = s[:close] + '  ' + node + '\n        ' + s[close:e] + s[e:k].rstrip(' ') + s[ke:].lstrip('\n')
    return s


def process(path, apply):
    s = open(path, encoding='utf-8').read()
    s = absorb_notes(s)
    L = lang_of(s)
    regs = find_regions(s)
    if not regs:
        return 0
    used = set(re.findall(r'id="([^"]+)"', s))
    n = 0
    for a, b, kind in reversed(regs):
        k = len(regs) - n
        sid = 'sol-p%d' % k
        while sid in used:
            k += 100; sid = 'sol-p%d' % k
        used.add(sid)
        s = wrap(s, a, b, sid, L)
        n += 1
    if 'solucions plegades' not in s:
        assert s.count('</head>') == 1
        s = s.replace('</head>', CSS + '</head>')
    if '/assets/js/examenes.js' not in s:
        anc = '<script defer src="/assets/js/search.js'
        if s.count(anc) != 1:
            anc = '</body>'
        assert s.count(anc) == 1, path
        s = s.replace(anc, '<script src="/assets/js/examenes.js?v=202609121757"></script>\n' + anc)
    if apply:
        open(path, 'w', encoding='utf-8').write(s)
    kinds = {}
    for r in regs: kinds[r[2]] = kinds.get(r[2], 0) + 1
    print(f'{n:3d} {kinds} {path}')
    return n


if __name__ == '__main__':
    import glob, os
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
        print('ERROR: %d solucions visibles. Plega-les amb --apply.' % tot)
        sys.exit(1)
    else:
        print('✓ Cap solució visible.')
