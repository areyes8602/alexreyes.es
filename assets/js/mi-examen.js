/* ============================================================
   /docencia/mi-examen/ — compositor de examen
   Lee la selección desde localStorage (clave 'mi-examen') y
   la renderiza con opciones de reordenar, quitar, imprimir.
   ============================================================ */
(function () {
  'use strict';

  const LANG = (document.documentElement.lang || 'es').slice(0, 2);
  const I18N = {
    es: {
      vacio_titulo: 'Todavía no has añadido ejercicios',
      vacio_desc: 'Ve al Banco de ejercicios y pulsa "+ Examen" en los que quieras incluir.',
      ver_banco: 'Ir al banco de ejercicios →',
      total_pts: 'puntos totales',
      quitar: 'Quitar', mover_arriba: '↑', mover_abajo: '↓',
      apartados: 'apartados', pts: 'pts', vacio: 'vacío',
      imprimir: 'Imprimir examen', vaciar: 'Vaciar selección',
      exportar_json: 'Exportar JSON', guardar_colec: 'Guardar como colección',
      de: 'De:', sobre: 'sobre',
    },
    ca: {
      vacio_titulo: 'Encara no has afegit exercicis',
      vacio_desc: 'Ves al Banc d\'exercicis i prem "+ Examen" als que vulguis incloure.',
      ver_banco: 'Anar al banc d\'exercicis →',
      total_pts: 'punts totals',
      quitar: 'Treure', mover_arriba: '↑', mover_abajo: '↓',
      apartados: 'apartats', pts: 'pts', vacio: 'buit',
      imprimir: 'Imprimir examen', vaciar: 'Buidar selecció',
      exportar_json: 'Exportar JSON', guardar_colec: 'Desar com a col·lecció',
      de: 'De:', sobre: 'sobre',
    },
    en: {
      vacio_titulo: "You haven't added any exercises yet",
      vacio_desc: 'Go to the Exercise bank and click "+ Exam" on the ones you want to include.',
      ver_banco: 'Go to exercise bank →',
      total_pts: 'total points',
      quitar: 'Remove', mover_arriba: '↑', mover_abajo: '↓',
      apartados: 'parts', pts: 'pts', vacio: 'empty',
      imprimir: 'Print exam', vaciar: 'Clear selection',
      exportar_json: 'Export JSON', guardar_colec: 'Save as collection',
      de: 'From:', sobre: 'out of',
    },
  };
  const STRINGS = I18N[LANG] || I18N.es;
  const t = (k) => STRINGS[k] || k;

  const CART_KEY = 'mi-examen';
  const $ = (id) => document.getElementById(id);

  let allIndex = null;   // from ejercicios-index.json
  let taxonomy = null;

  function loadCart() {
    try {
      const raw = localStorage.getItem(CART_KEY);
      const parsed = raw ? JSON.parse(raw) : [];
      return Array.isArray(parsed) ? parsed : [];
    } catch (e) { return []; }
  }
  function saveCart(ids) {
    localStorage.setItem(CART_KEY, JSON.stringify(ids));
  }

  function escHtml(s) {
    return String(s ?? '').replace(/[&<>"']/g, (c) => ({
      '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;',
    }[c]));
  }

  async function load() {
    const [taxRes, idxRes] = await Promise.all([
      fetch('/assets/data/tags.json'),
      fetch('/assets/data/ejercicios-index.json'),
    ]);
    taxonomy = await taxRes.json();
    const idx = await idxRes.json();
    allIndex = {};
    for (const ej of idx.ejercicios || []) allIndex[ej.id] = ej;
  }

  function render() {
    const ids = loadCart();
    const wrapper = $('mx-container');
    const emptyBox = $('mx-empty');
    const summary = $('mx-summary');

    // Filter to only existing ids (stale ids from removed collections)
    const ejercicios = ids.map((id) => allIndex[id]).filter(Boolean);

    if (!ejercicios.length) {
      wrapper.hidden = true;
      summary.hidden = true;
      emptyBox.hidden = false;
      return;
    }
    wrapper.hidden = false;
    summary.hidden = false;
    emptyBox.hidden = true;

    const totalPts = ejercicios.reduce((s, e) => s + (e.puntuacion || 0), 0);
    $('mx-total').textContent = `${totalPts} ${t('total_pts')}`;
    $('mx-count').textContent = `${ejercicios.length} ${ejercicios.length === 1 ? 'ejercicio' : 'ejercicios'}`;

    wrapper.innerHTML = '';
    ejercicios.forEach((ej, idx) => {
      const item = document.createElement('div');
      item.className = 'mx-item';
      const origin = [ej.coleccion?.titulo, ej.coleccion?.fecha]
        .filter(Boolean).map(escHtml).join(' · ');
      const apartadosHtml = (ej.apartados && ej.apartados.length)
        ? `<ul class="mx-apartados">${ej.apartados.map(a =>
            `<li><strong>${escHtml(a.letra)}.</strong> ${escHtml(a.tarea || '')} <span class="mx-ap-pts">[${a.puntos || 0} ${t('pts')}]</span></li>`
          ).join('')}</ul>`
        : `<p class="mx-no-apartados">${t('vacio')}</p>`;

      item.innerHTML = `
        <div class="mx-item-head">
          <div class="mx-item-num">${String(idx + 1).padStart(2, '0')}</div>
          <div class="mx-item-main">
            <h3 class="mx-item-title">${escHtml(ej.titulo)}</h3>
            <div class="mx-item-meta"><span class="mx-origin">${t('de')} ${origin}</span></div>
          </div>
          <div class="mx-item-pts">${ej.puntuacion || 0} <small>${t('pts')}</small></div>
          <div class="mx-item-tools no-print">
            <button class="mx-tool" data-act="up"     ${idx === 0 ? 'disabled' : ''} aria-label="${t('mover_arriba')}">${t('mover_arriba')}</button>
            <button class="mx-tool" data-act="down"   ${idx === ejercicios.length - 1 ? 'disabled' : ''} aria-label="${t('mover_abajo')}">${t('mover_abajo')}</button>
            <button class="mx-tool mx-tool-danger" data-act="remove" aria-label="${t('quitar')}">×</button>
          </div>
        </div>
        <div class="mx-item-body">${apartadosHtml}</div>
      `;

      item.querySelector('[data-act="up"]').addEventListener('click', () => moveItem(idx, -1));
      item.querySelector('[data-act="down"]').addEventListener('click', () => moveItem(idx, +1));
      item.querySelector('[data-act="remove"]').addEventListener('click', () => removeItem(idx));
      wrapper.appendChild(item);
    });

    // Re-render KaTeX if present
    if (window.renderMathInElement) {
      try { window.renderMathInElement(wrapper, { throwOnError: false }); } catch (e) {}
    }
  }

  function moveItem(idx, delta) {
    const ids = loadCart();
    const target = idx + delta;
    if (target < 0 || target >= ids.length) return;
    [ids[idx], ids[target]] = [ids[target], ids[idx]];
    saveCart(ids);
    render();
  }
  function removeItem(idx) {
    const ids = loadCart();
    ids.splice(idx, 1);
    saveCart(ids);
    render();
  }
  function clearAll() {
    if (!confirm('¿Vaciar la selección?')) return;
    saveCart([]);
    render();
  }
  function exportJSON() {
    const ids = loadCart();
    const ejercicios = ids.map(id => allIndex[id]).filter(Boolean);
    const out = {
      schema_version: 2,
      tipo_coleccion: 'examen_practica',
      titulo: 'Examen personalizado — ' + new Date().toISOString().slice(0, 10),
      fecha: new Date().toISOString().slice(0, 10),
      puntuacion_total: ejercicios.reduce((s, e) => s + (e.puntuacion || 0), 0),
      ejercicios_ref: ejercicios.map((e, i) => ({
        numero: i + 1, id: e.id, titulo: e.titulo, puntuacion: e.puntuacion,
      })),
    };
    const blob = new Blob([JSON.stringify(out, null, 2)], { type: 'application/json' });
    const a = document.createElement('a');
    a.href = URL.createObjectURL(blob);
    a.download = `mi-examen-${new Date().toISOString().slice(0, 10)}.json`;
    document.body.appendChild(a); a.click(); document.body.removeChild(a);
  }

  async function init() {
    try { await load(); }
    catch (e) {
      $('mx-container').innerHTML = `<div class="banco-empty">Error: ${escHtml(e.message)}</div>`;
      return;
    }
    $('mx-print').addEventListener('click', () => window.print());
    $('mx-clear').addEventListener('click', clearAll);
    $('mx-export').addEventListener('click', exportJSON);
    // Dynamic header fields (student name & date) kept in localStorage too
    const dateInput = $('mx-date');
    const titleInput = $('mx-title');
    dateInput.value = new Date().toISOString().slice(0, 10);
    titleInput.value = localStorage.getItem('mi-examen-title') || '';
    titleInput.addEventListener('input', () => localStorage.setItem('mi-examen-title', titleInput.value));
    render();
  }

  document.addEventListener('DOMContentLoaded', init);
})();
