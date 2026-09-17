#!/usr/bin/env python3
"""
check_nav_apunts.py — Comprova la navegació de llibre digital dels apunts.

Por qué: cuando se publica un apartado nuevo en una unidad que ya existía, el
apartado anterior se queda con el «Apartado siguiente» inactivo y la cadena de
prev/next se corta justo donde empieza el material nuevo. Es un fallo mudo: la
página se ve perfecta y el enlace simplemente no está. Este script lo caza.

Qué revisa, para cada carpeta /aula/*/apuntes/<unidad>/ de los tres árboles de
idioma (raíz, /ca/ y /en/):

  1. Que el `prev` apunte al apartado NN-1 de esa misma carpeta, y el `next` al
     NN+1, según el orden de los ficheros `NN-*.html`.
  2. Que el primer apartado tenga el `prev` inactivo y el último, el `next`.
  3. Que el destino de cada enlace exista en disco.
  4. Que los enlaces se queden dentro de su propio árbol de idioma. Si un
     apartado no está traducido, el enlace se sale a otro idioma: eso se avisa
     como AVÍS, no como error, porque a veces es lo que hay.

Uso:
    python3 scripts/check_nav_apunts.py

Devuelve 1 si encuentra errores, para poder encadenarlo antes de un commit.
"""

import os
import re
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ARBRES = [('', 'es'), ('ca/', 'ca'), ('en/', 'en')]
SECCIO = re.compile(r'^\d\d-.+\.html$')
NAV = re.compile(r'<nav class="exam-nav".*?</nav>', re.S)


def enllac(nav, classe):
    """Torna l'href de prev/next, o None si l'enllaç és inactiu o no hi és."""
    m = re.search(r'class="%s" href="([^"]+)"' % classe, nav)
    return m.group(1) if m else None


def unitats(prefix):
    arrel = os.path.join(REPO, prefix + 'aula')
    if not os.path.isdir(arrel):
        return
    for materia in sorted(os.listdir(arrel)):
        base = os.path.join(arrel, materia, 'apuntes')
        if not os.path.isdir(base):
            continue
        for unitat in sorted(os.listdir(base)):
            carpeta = os.path.join(base, unitat)
            if os.path.isdir(carpeta):
                yield carpeta


def main():
    errors, avisos = [], []

    for prefix, _lang in ARBRES:
        for carpeta in unitats(prefix):
            seccions = sorted(f for f in os.listdir(carpeta) if SECCIO.match(f))
            if not seccions:
                continue
            rel_carpeta = os.path.relpath(carpeta, REPO)
            for i, fitxer in enumerate(seccions):
                cami = os.path.join(carpeta, fitxer)
                with open(cami, encoding='utf-8') as f:
                    nav = NAV.search(f.read())
                if not nav:
                    continue
                nav = nav.group(0)
                rel = os.path.join(rel_carpeta, fitxer)

                for classe, esperat in (
                        ('prev', seccions[i - 1] if i else None),
                        ('next', seccions[i + 1] if i + 1 < len(seccions) else None)):
                    href = enllac(nav, classe)

                    if esperat is None:
                        if not href:
                            continue
                        # Si l'apartat veí no està traduït, sortir a un altre
                        # idioma és millor que un carreró sense sortida: avís.
                        if os.path.exists(os.path.join(REPO, href.lstrip('/'))):
                            avisos.append('%s: %s se\'n va a un altre idioma (%s), '
                                          'perquè aquest apartat no hi és traduït'
                                          % (rel, classe, href))
                        else:
                            errors.append('%s: %s enllaça a %s, que no existeix'
                                          % (rel, classe, href))
                        continue

                    if href is None:
                        errors.append('%s: %s inactiu, però hi ha %s a la carpeta'
                                      % (rel, classe, esperat))
                        continue

                    desti = href.lstrip('/')
                    if not os.path.exists(os.path.join(REPO, desti)):
                        errors.append('%s: %s apunta a %s, que no existeix'
                                      % (rel, classe, href))
                    elif not href.endswith('/' + esperat):
                        errors.append('%s: %s apunta a %s i hauria d\'anar a %s'
                                      % (rel, classe, href, esperat))
                    elif not desti.startswith(prefix + 'aula/'):
                        avisos.append('%s: %s se\'n va a un altre idioma (%s)'
                                      % (rel, classe, href))

    for a in avisos:
        print('  AVÍS  %s' % a)
    for e in errors:
        print('  ERROR %s' % e)

    print('\n─── Resum ───')
    print('  Errors: %d, avisos: %d' % (len(errors), len(avisos)))
    return 1 if errors else 0


if __name__ == '__main__':
    sys.exit(main())
