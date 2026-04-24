/* ============================================================
   /docencia/mi-examen/ — compositor de examen
   Lee la selección desde localStorage (clave 'mi-examen').
   Usa pdf-lib para generar:
     - PDF de enunciados (páginas extraídas de pdf_enunciados de cada colección)
     - PDF de soluciones (idem de pdf_soluciones, si existe)
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
      quitar: 'Quitar', pts: 'pts', vacio: 'vacío',
      imprimir: 'Vista / Imprimir',
      dl_enunciados: '⤓ Descargar PDF (enunciados)',
      dl_soluciones: '⤓ Descargar PDF (soluciones)',
      sin_sol: 'Sin soluciones disponibles',
      dl_json: '⤓ Exportar JSON',
      vaciar: 'Vaciar selección',
      de: 'De:',
      generando: 'Generando PDF…',
      ok: 'Listo',
      error_pdflib: 'pdf-lib no está cargado',
      error_fetch: 'Error al descargar un PDF: ',
      no_pages: '⚠ Este ejercicio no tiene páginas definidas en el PDF',
    },
    ca: {
      vacio_titulo: 'Encara no has afegit exercicis',
      vacio_desc: 'Ves al Banc d\'exercicis i prem "+ Examen" als que vulguis incloure.',
      ver_banco: 'Anar al banc d\'exercicis →',
      total_pts: 'punts totals',
      quitar: 'Treure', pts: 'pts', vacio: 'buit',
      imprimir: 'Vista / Imprimir',
      dl_enunciados: '⤓ Descarregar PDF (enunciats)',
      dl_soluciones: '⤓ Descarregar PDF (solucions)',
      sin_sol: 'Sense solucions disponibles',
      dl_json: '⤓ Exportar JSON',
      vaciar: 'Buidar selecció',
      de: 'De:',
      generando: 'Generant PDF…',
      ok: 'Fet',
      error_pdflib: 'pdf-lib no està carregat',
      error_fetch: 'Error descarregant un PDF: ',
      no_pages: '⚠ Aquest exercici no té pàgines definides al PDF',
    },
    en: {
      vacio_titulo: "You haven't added any exercises yet",
      vacio_desc: 'Go to the Exercise bank and click "+ Exam" on the ones you want to include.',
      ver_banco: 'Go to exercise bank →',
      total_pts: 'total points',
      quitar: 'Remove', pts: 'pts', vacio: 'empty',
      imprimir: 'View / Print',
      dl_enunciados: '⤓ Download PDF (questions)',
      dl_soluciones: '⤓ Download PDF (solutions)',
      sin_sol: 'No solutions available',
      dl_json: '⤓ Export JSON',
      vaciar: 'Clear selection',
      de: 'From:',
      generando: 'Generating PDF…',
      ok: 'Done',
      error_pdflib: 'pdf-lib not loaded',
      error_fetch: 'Error fetching a PDF: ',
      no_pages: '⚠ This exercise has no pages defined in the PDF',
    },
  };
  const STRINGS = I18N[LANG] || I18N.es;
  const t = (k) => STRINGS[k] || k;

  const CART_KEY = 'mi-examen';
  const $ = (id) => document.getElementById(id);

  let allIndex = null;
  let taxonomy = null;

  function loadCart() {
    try {
      const raw = localStorage.getItem(CART_KEY);
      const parsed = raw ? JSON.parse(raw) : [];
      return Array.isArray(parsed) ? parsed : [];
    } catch (e) { return []; }
  }
  function saveCart(ids) { localStorage.setItem(CART_KEY, JSON.stringify(ids)); }

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
    const ejercicios = ids.map((id) => allIndex[id]).filter(Boolean);

    // Update button availability based on whether solutions exist for all selected
    updateSolutionsButton(ejercicios);

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

      const pagesInfo = (ej.pages_enunciado && ej.pages_enunciado.length)
        ? `<span style="font-family:var(--mono);font-size:0.75rem;color:var(--text-faint);margin-left:0.4rem">pág. ${ej.pages_enunciado.join(',')}</span>`
        : `<span style="font-family:var(--mono);font-size:0.75rem;color:#c23a3a;margin-left:0.4rem">${t('no_pages')}</span>`;

      item.innerHTML = `
        <div class="mx-item-head">
          <div class="mx-item-num">${String(idx + 1).padStart(2, '0')}</div>
          <div class="mx-item-main">
            <h3 class="mx-item-title">${escHtml(ej.titulo)}</h3>
            <div class="mx-item-meta"><span class="mx-origin">${t('de')} ${origin}</span>${pagesInfo}</div>
          </div>
          <div class="mx-item-pts">${ej.puntuacion || 0} <small>${t('pts')}</small></div>
          <div class="mx-item-tools no-print">
            <button class="mx-tool" data-act="up" ${idx === 0 ? 'disabled' : ''}>↑</button>
            <button class="mx-tool" data-act="down" ${idx === ejercicios.length - 1 ? 'disabled' : ''}>↓</button>
            <button class="mx-tool mx-tool-danger" data-act="remove">×</button>
          </div>
        </div>
        <div class="mx-item-body">${apartadosHtml}</div>
      `;

      item.querySelector('[data-act="up"]').addEventListener('click', () => moveItem(idx, -1));
      item.querySelector('[data-act="down"]').addEventListener('click', () => moveItem(idx, +1));
      item.querySelector('[data-act="remove"]').addEventListener('click', () => removeItem(idx));
      wrapper.appendChild(item);
    });

    if (window.renderMathInElement) {
      try { window.renderMathInElement(wrapper, { throwOnError: false }); } catch (e) {}
    }
  }

  function updateSolutionsButton(ejercicios) {
    const btn = $('mx-dl-sol');
    if (!btn) return;
    if (!ejercicios.length) {
      btn.disabled = true;
      btn.textContent = t('dl_soluciones');
      return;
    }
    // Enabled only if every selected ejercicio has solution pages AND its colección has pdf_soluciones
    const allHaveSol = ejercicios.every(e =>
      e.coleccion?.pdf_soluciones && e.pages_solucion && e.pages_solucion.length
    );
    btn.disabled = !allHaveSol;
    btn.title = allHaveSol ? '' : t('sin_sol');
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

  // ---- PDF generation with pdf-lib ----
  // Cache fetched PDFs so we only download each source once.
  const pdfCache = new Map();
  async function fetchPdfBytes(url) {
    if (pdfCache.has(url)) return pdfCache.get(url);
    const res = await fetch(url);
    if (!res.ok) throw new Error(`${res.status} ${url}`);
    const bytes = await res.arrayBuffer();
    pdfCache.set(url, bytes);
    return bytes;
  }

  async function generatePDF(kind) {
    if (!window.PDFLib) { alert(t('error_pdflib')); return; }
    const { PDFDocument } = window.PDFLib;
    const btnId = kind === 'enunciados' ? 'mx-dl-enun' : 'mx-dl-sol';
    const btn = $(btnId);
    const orig = btn.textContent;
    btn.disabled = true;
    btn.textContent = t('generando');
    try {
      const ids = loadCart();
      const ejercicios = ids.map((id) => allIndex[id]).filter(Boolean);
      if (!ejercicios.length) return;

      // Group ejercicios by source PDF URL (colección pdf_enunciados/pdf_soluciones)
      // but preserve the user's order of selection.
      const outPdf = await PDFDocument.create();
      outPdf.setTitle($('mx-title').value || 'Examen personalizado');
      outPdf.setAuthor('Àlex Reyes · alexreyes.es');
      outPdf.setCreator('alexreyes.es / mi-examen');

      for (const ej of ejercicios) {
        const srcUrl = kind === 'enunciados'
          ? ej.coleccion?.pdf_enunciados
          : ej.coleccion?.pdf_soluciones;
        const pages = kind === 'enunciados' ? ej.pages_enunciado : ej.pages_solucion;
        if (!srcUrl || !pages || !pages.length) {
          console.warn('Skipping ejercicio without source', ej.id);
          continue;
        }
        const bytes = await fetchPdfBytes(srcUrl);
        const src = await PDFDocument.load(bytes);
        // pdf-lib uses 0-based page indices
        const indices = pages.map(p => Math.max(0, p - 1));
        const copied = await outPdf.copyPages(src, indices);
        copied.forEach(p => outPdf.addPage(p));
      }

      const bytesOut = await outPdf.save();
      const blob = new Blob([bytesOut], { type: 'application/pdf' });
      const a = document.createElement('a');
      a.href = URL.createObjectURL(blob);
      const date = new Date().toISOString().slice(0, 10);
      const suffix = kind === 'enunciados' ? 'enunciados' : 'soluciones';
      a.download = `mi-examen-${date}-${suffix}.pdf`;
      document.body.appendChild(a); a.click(); document.body.removeChild(a);
      btn.textContent = '✓ ' + t('ok');
      setTimeout(() => { btn.textContent = orig; btn.disabled = false; }, 1500);
    } catch (e) {
      console.error(e);
      alert(t('error_fetch') + e.message);
      btn.textContent = orig;
      btn.disabled = false;
    }
  }

  function exportJSON() {
    const ids = loadCart();
    const ejercicios = ids.map(id => allIndex[id]).filter(Boolean);
    const out = {
      schema_version: 2,
      tipo_coleccion: 'examen_practica',
      titulo: $('mx-title').value || 'Examen personalizado — ' + new Date().toISOString().slice(0, 10),
      fecha: new Date().toISOString().slice(0, 10),
      puntuacion_total: ejercicios.reduce((s, e) => s + (e.puntuacion || 0), 0),
      ejercicios_ref: ejercicios.map((e, i) => ({
        numero: i + 1, id: e.id, titulo: e.titulo, puntuacion: e.puntuacion,
        pages_enunciado: e.pages_enunciado, pages_solucion: e.pages_solucion,
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
    const enun = $('mx-dl-enun');
    if (enun) enun.addEventListener('click', () => generatePDF('enunciados'));
    const sol = $('mx-dl-sol');
    if (sol) sol.addEventListener('click', () => generatePDF('soluciones'));
    const titleInput = $('mx-title');
    const dateInput = $('mx-date');
    dateInput.value = new Date().toISOString().slice(0, 10);
    titleInput.value = localStorage.getItem('mi-examen-title') || '';
    titleInput.addEventListener('input', () => localStorage.setItem('mi-examen-title', titleInput.value));
    render();
  }

  document.addEventListener('DOMContentLoaded', init);
})();
