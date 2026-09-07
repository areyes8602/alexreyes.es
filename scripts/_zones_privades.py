"""Las zonas privadas del sitio, en un solo sitio.

Cada una tiene su gate de servidor en functions/<zona>/_middleware.js: sus
páginas no son alcanzables sin sesión, llevan su propio chrome y no quieren
nada de lo que reparte el post-proceso (OG, JSON-LD, hreflang, skip-link,
buscador, lang-persist). Tampoco se indexan ni entran en el sitemap.

Al añadir una asignatura nueva basta con ponerla aquí: los seis scripts de
post-proceso y el robots.txt que genera build_sitemap.py leen esta lista.
Lo único que queda a mano es su bloque en `_headers`.

El nombre es <materia>-<curso>, para que escale: mates-2eso, mates-3eso…
"""

ZONES_PRIVADES = {
    "panel",       # el panel de administración del sitio
    "tutoria",     # tutoría de 2n ESO E
    "mates-2eso",  # matemáticas de 2º de ESO: grupos de nivel y notas
}
