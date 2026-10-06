/* Simulador de la simetria respecte d'una recta que passa per l'origen.
 *
 * La recta y = (tan θ)·x té la matriu S = (cos 2θ  sin 2θ; sin 2θ  −cos 2θ).
 * La transició mou cada vèrtex en línia recta cap a la seva imatge,
 * P(t) = (1 − t)·P + t·S·P: el camí és perpendicular a la recta i a t = 1/2
 * tots els punts hi són a sobre. És la manera de veure que la simetria «plega»
 * el pla per la recta.
 *
 * Els textos de cada idioma van en data-* del bloc .sim-sim (data-dec és el
 * separador decimal), així el mateix fitxer serveix per a les tres versions.
 */
(function () {
  'use strict';
  var NS = 'http://www.w3.org/2000/svg';
  var QUADRAT = [[1, 1], [4, 1], [4, 4], [1, 4]];

  function el(nom, atr, pare) {
    var e = document.createElementNS(NS, nom);
    for (var k in atr) e.setAttribute(k, atr[k]);
    if (pare) pare.appendChild(e);
    return e;
  }

  function iniciar(arrel) {
    var dec = arrel.dataset.dec || '.';
    var num = function (x, d) {
      var s = (Math.abs(x) < 5e-4 ? 0 : x).toFixed(d);
      s = s.replace('-', '−');
      return dec === ',' ? s.replace('.', ',') : s;
    };
    var svg = arrel.querySelector('svg');
    var cTheta = arrel.querySelector('input[name=theta]');
    var cT = arrel.querySelector('input[name=t]');
    var bPlay = arrel.querySelector('[data-play]');
    var sortida = arrel.querySelector('.sim-resultat');
    var W = 340, H = 340, R = 6;
    var X = function (x) { return W / 2 + x * (W / 2 - 14) / R; };
    var Y = function (y) { return H / 2 - y * (H / 2 - 14) / R; };
    var anim = null;
    // L'angle exacte d'un botó (63,4349° no cap al pas de 0,5° del control).
    var exacte = null;

    function dibuixar() {
      var graus = exacte === null ? +cTheta.value : exacte;
      var th = graus * Math.PI / 180, t = +cT.value;
      var c2 = Math.cos(2 * th), s2 = Math.sin(2 * th);
      var img = QUADRAT.map(function (p) { return [c2 * p[0] + s2 * p[1], s2 * p[0] - c2 * p[1]]; });
      var mig = QUADRAT.map(function (p, i) { return [(1 - t) * p[0] + t * img[i][0], (1 - t) * p[1] + t * img[i][1]]; });
      svg.innerHTML = '';
      for (var g = -R; g <= R; g++) {
        el('line', { x1: X(g), y1: Y(-R), x2: X(g), y2: Y(R), stroke: '#94a3b8', 'stroke-width': 0.4, opacity: 0.45 }, svg);
        el('line', { x1: X(-R), y1: Y(g), x2: X(R), y2: Y(g), stroke: '#94a3b8', 'stroke-width': 0.4, opacity: 0.45 }, svg);
      }
      el('line', { x1: X(-R), y1: Y(0), x2: X(R), y2: Y(0), stroke: '#94a3b8', 'stroke-width': 1.3 }, svg);
      el('line', { x1: X(0), y1: Y(-R), x2: X(0), y2: Y(R), stroke: '#94a3b8', 'stroke-width': 1.3 }, svg);
      // la recta
      var dx = Math.cos(th) * 2 * R, dy = Math.sin(th) * 2 * R;
      el('line', { x1: X(-dx), y1: Y(-dy), x2: X(dx), y2: Y(dy), stroke: '#7c3aed', 'stroke-width': 2.2 }, svg);
      var pts = function (P) { return P.map(function (p) { return X(p[0]).toFixed(1) + ',' + Y(p[1]).toFixed(1); }).join(' '); };
      // camins perpendiculars a la recta
      QUADRAT.forEach(function (p, i) {
        el('line', { x1: X(p[0]), y1: Y(p[1]), x2: X(img[i][0]), y2: Y(img[i][1]), stroke: '#94a3b8', 'stroke-width': 1, 'stroke-dasharray': '3 3' }, svg);
      });
      el('polygon', { points: pts(QUADRAT), fill: 'rgba(100,116,139,0.10)', stroke: '#64748b', 'stroke-width': 1.3, 'stroke-dasharray': '5 4' }, svg);
      el('polygon', { points: pts(img), fill: 'none', stroke: '#ea580c', 'stroke-width': 1, 'stroke-dasharray': '2 3', opacity: 0.7 }, svg);
      el('polygon', { points: pts(mig), fill: 'rgba(234,88,12,0.22)', stroke: '#ea580c', 'stroke-width': 2 }, svg);
      // un vèrtex marcat, per veure que la figura es gira del revés
      el('circle', { cx: X(mig[0][0]), cy: Y(mig[0][1]), r: 4.5, fill: '#ea580c' }, svg);
      el('circle', { cx: X(QUADRAT[0][0]), cy: Y(QUADRAT[0][1]), r: 3.5, fill: '#64748b' }, svg);
      arrel.querySelector('[data-out=theta]').textContent = num(graus, 1) + '°';
      arrel.querySelector('[data-out=t]').textContent = num(t, 2);
      var m = Math.abs(Math.cos(th)) < 1e-9 ? null : Math.tan(th);
      var recta = m === null ? 'x = 0' : (Math.abs(m) < 5e-4 ? 'y = 0' : 'y = ' + num(m, 2) + 'x');
      sortida.innerHTML = arrel.dataset.recta + ' <strong>' + recta + '</strong> &nbsp;·&nbsp; S = ( ' + num(c2, 2) + '  ' + num(s2, 2)
        + ' ; ' + num(s2, 2) + '  ' + num(-c2, 2) + ' ) &nbsp;·&nbsp; det S = −1';
    }

    function aturar() {
      if (anim) { cancelAnimationFrame(anim); anim = null; bPlay.textContent = arrel.dataset.play; }
    }
    function jugar() {
      if (anim) { aturar(); return; }
      var t0 = null, inici = +cT.value >= 1 ? 0 : +cT.value;
      bPlay.textContent = arrel.dataset.stop;
      var pas = function (ts) {
        if (t0 === null) t0 = ts;
        var t = Math.min(1, inici + (ts - t0) / 2200);
        cT.value = t; dibuixar();
        if (t < 1) anim = requestAnimationFrame(pas); else aturar();
      };
      anim = requestAnimationFrame(pas);
    }

    cTheta.addEventListener('input', function () { exacte = null; dibuixar(); });
    cT.addEventListener('input', function () { aturar(); dibuixar(); });
    bPlay.addEventListener('click', jugar);
    arrel.querySelectorAll('[data-theta]').forEach(function (b) {
      b.addEventListener('click', function () { aturar(); cTheta.value = b.dataset.theta; exacte = +b.dataset.theta; cT.value = 0; dibuixar(); jugar(); });
    });
    dibuixar();
  }

  function tots() { document.querySelectorAll('.sim-sim').forEach(iniciar); }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', tots);
  else tots();
})();
