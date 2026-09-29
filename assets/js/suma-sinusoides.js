/* Simulador de la suma de dues sinusoïdals de la mateixa freqüència.
 *
 * Cada bloc .sim-sinus porta els textos del seu idioma en atributs data-*
 * (data-dec és el separador decimal), així el mateix fitxer serveix per a
 * les tres versions de l'apunt. Dibuixa les dues ones i la suma, i al costat
 * els dos fasors posats l'un darrere l'altre amb la resultant: la mateixa
 * suma de complexos que es fa a mà als apunts.
 */
(function () {
  'use strict';
  var NS = 'http://www.w3.org/2000/svg';

  function el(nom, atr, pare) {
    var e = document.createElementNS(NS, nom);
    for (var k in atr) e.setAttribute(k, atr[k]);
    if (pare) pare.appendChild(e);
    return e;
  }

  function iniciar(arrel) {
    var dec = arrel.dataset.dec || '.';
    var num = function (x, d) {
      var s = (Math.abs(x) < 1e-9 ? 0 : x).toFixed(d);
      return dec === ',' ? s.replace('.', ',') : s;
    };
    var ctl = {};
    arrel.querySelectorAll('input[type=range]').forEach(function (i) { ctl[i.name] = i; });
    var ona = arrel.querySelector('.sim-ona');
    var fas = arrel.querySelector('.sim-fasors');
    var sortida = arrel.querySelector('.sim-resultat');

    // Ones: x de 0 a 4π; fasors: pla complex centrat.
    var W = 560, H = 260, M = 30;
    var FW = 260, FH = 260;

    function valors() {
      return {
        A1: +ctl.A1.value, p1: +ctl.p1.value * Math.PI / 12,
        A2: +ctl.A2.value, p2: +ctl.p2.value * Math.PI / 12,
        b: +ctl.b.value
      };
    }

    // Fase en múltiples de π/12 → text amb π, que és com surt a classe.
    function fase(n) {
      if (n === 0) return '0';
      var g = function (a, c) { return c ? g(c, a % c) : a; };
      var d = g(Math.abs(n), 12), p = n / d, q = 12 / d;
      var s = (p < 0 ? '−' : '') + (Math.abs(p) === 1 ? '' : Math.abs(p)) + 'π';
      return q === 1 ? s : s + '/' + q;
    }

    function dibuixar() {
      var v = valors();
      var re = v.A1 * Math.cos(v.p1) + v.A2 * Math.cos(v.p2);
      var im = v.A1 * Math.sin(v.p1) + v.A2 * Math.sin(v.p2);
      var R = Math.hypot(re, im), al = Math.atan2(im, re);

      arrel.querySelector('[data-out=A1]').textContent = num(v.A1, 1);
      arrel.querySelector('[data-out=A2]').textContent = num(v.A2, 1);
      arrel.querySelector('[data-out=p1]').textContent = fase(+ctl.p1.value);
      arrel.querySelector('[data-out=p2]').textContent = fase(+ctl.p2.value);
      arrel.querySelector('[data-out=b]').textContent = v.b;

      // --- les ones
      ona.innerHTML = '';
      var ymax = Math.max(v.A1 + v.A2, 1) * 1.1;
      var X = function (x) { return M + (W - 2 * M) * x / (4 * Math.PI); };
      var Y = function (y) { return H / 2 - (H / 2 - 12) * y / ymax; };
      el('line', { x1: M, y1: Y(0), x2: W - M, y2: Y(0), stroke: '#94a3b8', 'stroke-width': 1 }, ona);
      el('line', { x1: M, y1: 8, x2: M, y2: H - 8, stroke: '#94a3b8', 'stroke-width': 1 }, ona);
      for (var k = 1; k <= 4; k++) {
        el('line', { x1: X(k * Math.PI), y1: Y(0) - 4, x2: X(k * Math.PI), y2: Y(0) + 4, stroke: '#94a3b8' }, ona);
        var t = el('text', { x: X(k * Math.PI), y: Y(0) + 16, 'text-anchor': 'middle', 'font-size': 11,
          'font-family': 'JetBrains Mono,monospace', fill: '#94a3b8' }, ona);
        t.textContent = (k === 1 ? '' : k) + 'π';
      }
      [[-R, '#047857'], [R, '#047857']].forEach(function (p) {
        el('line', { x1: M, y1: Y(p[0]), x2: W - M, y2: Y(p[0]), stroke: p[1], 'stroke-width': 0.8,
          'stroke-dasharray': '4 4', opacity: 0.6 }, ona);
      });
      var corba = function (f, color, gruix, guions) {
        var d = [];
        for (var i = 0; i <= 400; i++) {
          var x = 4 * Math.PI * i / 400;
          d.push((i ? 'L' : 'M') + X(x).toFixed(1) + ',' + Y(f(x)).toFixed(1));
        }
        var a = { d: d.join(' '), fill: 'none', stroke: color, 'stroke-width': gruix };
        if (guions) a['stroke-dasharray'] = guions;
        el('path', a, ona);
      };
      corba(function (x) { return v.A1 * Math.sin(v.b * x + v.p1); }, '#1d4ed8', 1.6, '6 4');
      corba(function (x) { return v.A2 * Math.sin(v.b * x + v.p2); }, '#d97706', 1.6, '6 4');
      corba(function (x) { return v.A1 * Math.sin(v.b * x + v.p1) + v.A2 * Math.sin(v.b * x + v.p2); }, '#047857', 2.8);

      // --- els fasors
      fas.innerHTML = '';
      var esc = (FW / 2 - 18) / Math.max(v.A1 + v.A2, 1);
      var cx = FW / 2, cy = FH / 2;
      var P = function (x, y) { return [cx + esc * x, cy - esc * y]; };
      el('line', { x1: 8, y1: cy, x2: FW - 8, y2: cy, stroke: '#94a3b8' }, fas);
      el('line', { x1: cx, y1: 8, x2: cx, y2: FH - 8, stroke: '#94a3b8' }, fas);
      var te = el('text', { x: FW - 10, y: cy - 6, 'text-anchor': 'end', 'font-size': 11, fill: '#94a3b8',
        'font-family': 'Inter,sans-serif' }, fas); te.textContent = 'Re';
      var ti = el('text', { x: cx + 6, y: 18, 'font-size': 11, fill: '#94a3b8', 'font-family': 'Inter,sans-serif' }, fas);
      ti.textContent = 'Im';
      var fletxa = function (a, b, color, gruix) {
        el('line', { x1: a[0], y1: a[1], x2: b[0], y2: b[1], stroke: color, 'stroke-width': gruix,
          'stroke-linecap': 'round' }, fas);
        var ang = Math.atan2(b[1] - a[1], b[0] - a[0]), l = 9;
        if (Math.hypot(b[0] - a[0], b[1] - a[1]) < 4) return;
        el('path', { d: 'M' + b[0] + ',' + b[1] + ' L' + (b[0] - l * Math.cos(ang - 0.4)) + ',' + (b[1] - l * Math.sin(ang - 0.4))
          + ' L' + (b[0] - l * Math.cos(ang + 0.4)) + ',' + (b[1] - l * Math.sin(ang + 0.4)) + ' Z', fill: color }, fas);
      };
      var z1 = [v.A1 * Math.cos(v.p1), v.A1 * Math.sin(v.p1)];
      fletxa(P(0, 0), P(z1[0], z1[1]), '#1d4ed8', 2.2);
      fletxa(P(z1[0], z1[1]), P(re, im), '#d97706', 2.2);
      fletxa(P(0, 0), P(re, im), '#047857', 3);

      // Amb R = 0 l'argument no existeix: la suma és zero i prou.
      if (R < 0.005) {
        sortida.innerHTML = arrel.dataset.suma + ' <strong>0</strong> &nbsp;·&nbsp; ' + arrel.dataset.anul;
      } else {
        sortida.innerHTML = arrel.dataset.suma + ' <strong>' + num(R, 2) + '</strong>&thinsp;sin('
          + (v.b === 1 ? '' : v.b) + 'x ' + (al < 0 ? '−' : '+') + ' <strong>' + num(Math.abs(al), 2) + '</strong>)'
          + ' &nbsp;·&nbsp; R = ' + num(R, 2) + ', α = ' + num(al, 2) + ' rad (' + num(al * 180 / Math.PI, 1) + '°)';
      }
    }

    arrel.querySelectorAll('input[type=range]').forEach(function (i) { i.addEventListener('input', dibuixar); });
    arrel.querySelectorAll('[data-preset]').forEach(function (b) {
      b.addEventListener('click', function () {
        var p = b.dataset.preset.split(',');
        ['A1', 'p1', 'A2', 'p2', 'b'].forEach(function (k, j) { ctl[k].value = p[j]; });
        dibuixar();
      });
    });
    dibuixar();
  }

  function tots() { document.querySelectorAll('.sim-sinus').forEach(iniciar); }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', tots);
  else tots();
})();
