/* Navegació anterior / índex / següent dels apunts d'IB.
 *
 * Abans cada pàgina portava aquest codi enganxat i ordenava per codi NM/TANS,
 * i això només funcionava amb un apartat per codi. Ara un concepte pot tenir
 * diversos apartats (una entrada per pàgina a conceptos-apuntes.json), així
 * que l'ordre es fa per slug: el d'apuntes_orden de la unitat, que admet slugs
 * o codis, i el que no hi surti va al final en l'ordre del fitxer.
 *
 * La pàgina diu qui és amb data-slug al <nav id="apunt-nav">, i data-pre és el
 * prefix d'idioma ('', '/ca' o '/en'). La unitat surt de ?from= o, si no n'hi
 * ha, de les molles de pa.
 */
(async function () {
  'use strict';
  var nav = document.getElementById('apunt-nav');
  if (!nav) return;
  var slug = nav.dataset.slug, pre = nav.dataset.pre || '';
  var lang = (document.documentElement.lang || 'es').slice(0, 2);
  var bc = document.getElementById('bc-apunts');
  var unit = new URLSearchParams(location.search).get('from')
    || (bc ? decodeURIComponent(bc.getAttribute('href').split('#')[1] || '') : '');
  if (!unit) return;
  try {
    var r = await Promise.all([
      fetch('/assets/data/ib-unidades.json').then(function (x) { return x.json(); }),
      fetch('/assets/data/conceptos-apuntes.json').then(function (x) { return x.json(); })
    ]);
    var U = r[0], C = r[1].conceptos || [];
    var u = [].concat(U.unidades_hl || [], U.unidades_sl || [], U.unidades || [])
      .find(function (x) { return x.id === unit; });
    if (!u) return;
    var orden = u.apuntes_orden || [], tags = u.tags_iba || [];
    var pos = function (e) {
      var i = orden.indexOf(e.slug);
      if (i >= 0) return i;
      i = orden.indexOf(e.code);
      return i >= 0 ? i : Infinity;
    };
    var llista = C.map(function (e, k) { return { e: e, k: k, p: pos(e) }; })
      .filter(function (x) { return tags.indexOf(x.e.code) >= 0; })
      .sort(function (a, b) { return (a.p === b.p ? 0 : (a.p < b.p ? -1 : 1)) || (a.k - b.k); })
      .map(function (x) { return x.e; });
    var i = llista.findIndex(function (e) { return e.slug === slug; });
    if (i < 0) return;
    [['prev', llista[i - 1]], ['next', llista[i + 1]]].forEach(function (p) {
      if (!p[1]) return;
      var el = nav.querySelector('.' + p[0]);
      var a = document.createElement('a');
      a.className = p[0];
      a.href = pre + '/aula/ib-ai-hl/apuntes/' + p[1].slug + '/?from=' + encodeURIComponent(unit);
      a.title = (p[1].titulo && (p[1].titulo[lang] || p[1].titulo.es)) || p[1].code;
      a.innerHTML = el.innerHTML;
      el.replaceWith(a);
    });
    var idx = nav.querySelector('.index');
    idx.href = idx.getAttribute('href').split('#')[0] + '#' + encodeURIComponent(unit);
  } catch (e) {}
})();
