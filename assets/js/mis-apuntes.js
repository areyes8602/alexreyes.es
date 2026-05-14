/* ============================================================
   /docencia/mis-apuntes/ — compositor d'apunts
   Llegeix la selecció de localStorage ('mis-apuntes') i carrega el
   contingut viu de cada apunte des del seu HTML font. Permet imprimir
   (window.print) → l'usuari guarda com PDF amb qualitat vectorial.
   Anàleg a /docencia/mi-examen/.
   ============================================================ */
(function () {
  'use strict';

  const LANG = (document.documentElement.lang || 'es').slice(0, 2);
  const I18N = {
    es: {
      vacio_titulo: 'Todavía no has añadido apuntes',
      vacio_desc: 'Ve al Banco de apuntes y pulsa "+ Apuntes" en los que quieras incluir.',
      ver_banco: 'Ir al banco de apuntes →',
      total: 'apuntes seleccionados',
      quitar: 'Quitar',
      imprimir: 'Vista / Imprimir',
      vaciar: 'Vaciar',
      generando: 'Preparando…',
      error_pdflib: 'Error al generar el PDF',
      error_fetch: 'Error al cargar el HTML del apunte: ',
      header_brand: 'alexreyes.es',
      title_default: 'Apuntes — alexreyes.es',
      apunte_n: 'Apunte',
    },
    ca: {
      vacio_titulo: 'Encara no has afegit apunts',
      vacio_desc: 'Ves al Banc d\'apunts i prem "+ Apunts" als que vulguis incloure.',
      ver_banco: 'Anar al banc d\'apunts →',
      total: 'apunts seleccionats',
      quitar: 'Treure',
      imprimir: 'Vista / Imprimir',
      vaciar: 'Buidar',
      generando: 'Preparant…',
      error_pdflib: 'Error generant el PDF',
      error_fetch: 'Error carregant l\'HTML de l\'apunt: ',
      header_brand: 'alexreyes.es',
      title_default: 'Apunts — alexreyes.es',
      apunte_n: 'Apunt',
    },
    en: {
      vacio_titulo: "You haven't added any notes yet",
      vacio_desc: 'Go to the Notes bank and click "+ Notes" on the ones you want to include.',
      ver_banco: 'Go to notes bank →',
      total: 'notes selected',
      quitar: 'Remove',
      imprimir: 'View / Print',
      vaciar: 'Clear',
      generando: 'Preparing…',
      error_pdflib: 'Error generating the PDF',
      error_fetch: 'Error fetching note HTML: ',
      header_brand: 'alexreyes.es',
      title_default: 'Notes — alexreyes.es',
      apunte_n: 'Note',
    },
  };
  const STRINGS = I18N[LANG] || I18N.es;
  const t = (k) => STRINGS[k] || k;

  // KaTeX delimiters (inclou `$...$` que el default no té).
  const KATEX_OPTS = {
    delimiters: [
      { left: '$$', right: '$$', display: true },
      { left: '\\[', right: '\\]', display: true },
      { left: '$', right: '$', display: false },
      { left: '\\(', right: '\\)', display: false },
    ],
    throwOnError: false,
  };

  const CART_KEY = 'mis-apuntes';
  const $ = (id) => document.getElementById(id);

  let allIndex = null;

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
  function escAttr(s) { return escHtml(s); }

  async function load() {
    const res = await fetch('/assets/data/apuntes-index.json');
    if (!res.ok) throw new Error('HTTP ' + res.status);
    const idx = await res.json();
    allIndex = {};
    for (const a of idx.apuntes || []) allIndex[a.id] = a;
  }

  // ============================================================
  // Editor view
  // ============================================================
  function render() {
    const ids = loadCart();
    const wrapper = $('mxa-container');
    const emptyBox = $('mxa-empty');
    const summary = $('mxa-summary');
    const apuntes = ids.map((id) => allIndex[id]).filter(Boolean);

    if (!apuntes.length) {
      wrapper.hidden = true;
      summary.hidden = true;
      emptyBox.hidden = false;
      return;
    }
    wrapper.hidden = false;
    summary.hidden = false;
    emptyBox.hidden = true;

    $('mxa-count').textContent = `${apuntes.length} ${t('total')}`;

    wrapper.innerHTML = '';
    apuntes.forEach((a, idx) => {
      const item = document.createElement('div');
      item.className = 'mx-item';

      item.innerHTML = `
        <div class="mx-item-head">
          <div class="mx-item-num">${String(idx + 1).padStart(2, '0')}</div>
          <div class="mx-item-main">
            <h3 class="mx-item-title">${escHtml(a.titulo)}</h3>
            <div class="mx-item-meta">
              <span class="mx-origin">${escHtml(a.materia)}${a.unidad ? ' · ' + escHtml(a.unidad) : ''}${a.section_num ? ' · ' + escHtml(a.section_num) : ''}</span>
              <span style="font-family:var(--mono);font-size:0.75rem;color:var(--text-faint);margin-left:0.4rem">${escHtml(a.lang.toUpperCase())}</span>
            </div>
          </div>
          <div class="mx-item-tools no-print">
            <button class="mx-tool" data-act="up" ${idx === 0 ? 'disabled' : ''}>↑</button>
            <button class="mx-tool" data-act="down" ${idx === apuntes.length - 1 ? 'disabled' : ''}>↓</button>
            <button class="mx-tool mx-tool-danger" data-act="remove">×</button>
          </div>
        </div>
        <div class="mx-item-body">
          <p class="mx-item-desc">${escHtml(a.descripcion || '')}</p>
        </div>
      `;
      item.querySelector('[data-act="up"]').addEventListener('click', () => moveItem(idx, -1));
      item.querySelector('[data-act="down"]').addEventListener('click', () => moveItem(idx, +1));
      item.querySelector('[data-act="remove"]').addEventListener('click', () => removeItem(idx));
      wrapper.appendChild(item);
    });

    if (window.renderMathInElement) {
      try { window.renderMathInElement(wrapper, KATEX_OPTS); } catch (e) {}
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

  // ============================================================
  // Print area assembly
  // ============================================================
  const pageCache = new Map();
  async function fetchPage(url) {
    if (pageCache.has(url)) return pageCache.get(url);
    const res = await fetch(url, { credentials: 'same-origin' });
    if (!res.ok) throw new Error(`HTTP ${res.status} per ${url}`);
    const html = await res.text();
    const doc = new DOMParser().parseFromString(html, 'text/html');

    // Estils inline del head — els apunts en porten un de gran amb tots els
    // .def-box, .exercise, .apart, etc.
    const styles = [];
    doc.querySelectorAll('head style').forEach((s) => {
      const css = s.textContent || '';
      if (css.trim()) styles.push(css);
    });

    const entry = { doc, styles };
    pageCache.set(url, entry);
    return entry;
  }

  /** Extreu el bloc principal d'un apunte. Per a apunts agafem <main> sencer
   *  (excloent nav/footer); per a unitat, idem. */
  async function extractApunteContent(a) {
    const { doc } = await fetchPage(a.url);
    // Probem main > .container, o article, o main, com a contenidor
    let node = doc.querySelector('main .container') || doc.querySelector('main') || doc.querySelector('article');
    if (!node) return null;
    const clone = node.cloneNode(true);

    // Netegem elements de chrome que no volem al PDF
    clone.querySelectorAll('nav, footer, .breadcrumb, .exam-nav, .libro-nav, .no-print, button').forEach(n => n.remove());
    // Obrim tots els <details> per a que les solucions es vegin
    clone.querySelectorAll('details').forEach(d => d.setAttribute('open', ''));
    return clone;
  }

  function buildHeaderHtml(title) {
    return `
      <header class="mxp-header">
        <div class="mxp-brand">${escHtml(t('header_brand'))}</div>
        <div class="mxp-meta">
          <span class="mxp-date">${escHtml(new Date().toISOString().slice(0, 10))}</span>
        </div>
      </header>
      ${title ? `<h1 class="mxp-title">${escHtml(title)}</h1>` : ''}
    `;
  }

  async function buildPrintArea() {
    const ids = loadCart();
    const apuntes = ids.map((id) => allIndex[id]).filter(Boolean);
    const area = $('mxa-print-area');
    if (!area) throw new Error('Falta #mxa-print-area al DOM');

    const title = $('mxa-title')?.value || t('title_default');

    const cssBag = new Set();
    const blocks = [];

    for (let i = 0; i < apuntes.length; i++) {
      const a = apuntes[i];
      try {
        const node = await extractApunteContent(a);
        if (!node) {
          blocks.push({ a, node: null, ok: false });
          continue;
        }
        const cached = pageCache.get(a.url);
        if (cached) cached.styles.forEach(css => cssBag.add(css));
        blocks.push({ a, node, ok: true });
      } catch (e) {
        console.warn('Falla extraient', a.id, e);
        blocks.push({ a, node: null, ok: false, error: e.message });
      }
    }

    area.innerHTML = '';

    // Header global del PDF
    const headerWrap = document.createElement('div');
    headerWrap.className = 'mxp-cover';
    headerWrap.innerHTML = buildHeaderHtml(title);
    area.appendChild(headerWrap);

    // Estils inline injectats al head (com a mi-examen).
    const inlinedStyles = Array.from(cssBag).join('\n\n');
    const prev = document.getElementById('mxa-injected-styles');
    if (prev) prev.remove();
    const styleEl = document.createElement('style');
    styleEl.id = 'mxa-injected-styles';
    styleEl.textContent = inlinedStyles;
    document.head.appendChild(styleEl);

    // Cada apunte com a secció amb salt de pàgina
    blocks.forEach((b, i) => {
      const sec = document.createElement('section');
      sec.className = 'mxp-question'; // reusa el mateix estil de paginació
      const titleHtml = `<h2 class="mxp-q-title">${escHtml(b.a.titulo)}</h2>`;
      const originHtml = `<div class="mxp-q-origin">${escHtml(b.a.materia)}${b.a.unidad ? ' · ' + escHtml(b.a.unidad) : ''} · ${escHtml(b.a.lang.toUpperCase())}</div>`;
      const numHtml = `<div class="mxp-q-num">${t('apunte_n')} ${i + 1}</div>`;

      sec.innerHTML = numHtml + titleHtml + originHtml;
      const body = document.createElement('div');
      body.className = 'mxp-q-body';
      if (b.ok && b.node) {
        body.appendChild(b.node);
      } else {
        body.innerHTML = `<p class="mxp-q-error">${escHtml(t('error_fetch') + (b.error || ''))}</p>`;
      }
      sec.appendChild(body);
      area.appendChild(sec);
    });

    if (window.renderMathInElement) {
      try { window.renderMathInElement(area, KATEX_OPTS); } catch (e) {}
    }
    return area;
  }

  // ============================================================
  // window.print() - vector PDF via diálogo del navegador
  // ============================================================
  async function printPreview() {
    const btn = $('mxa-print');
    const orig = btn ? btn.textContent : '';
    if (btn) { btn.disabled = true; btn.textContent = t('generando'); }
    const cleanup = () => {
      document.body.classList.remove('mx-printing', 'mx-printing-enunciados');
      if (btn) { btn.textContent = orig; btn.disabled = false; }
    };
    try {
      await buildPrintArea();
      // Reuse classes del compositor d'examen perquè el CSS d'impressió ja
      // amaga la UI d'edició quan body té .mx-printing.
      document.body.classList.add('mx-printing', 'mx-printing-enunciados');
      await new Promise(r => setTimeout(r, 250));
      const onAfterPrint = () => { cleanup(); window.removeEventListener('afterprint', onAfterPrint); };
      window.addEventListener('afterprint', onAfterPrint);
      window.print();
      setTimeout(() => {
        if (document.body.classList.contains('mx-printing')) {
          cleanup();
          window.removeEventListener('afterprint', onAfterPrint);
        }
      }, 60_000);
    } catch (e) {
      console.error(e);
      alert(t('error_pdflib') + ': ' + e.message);
      cleanup();
    }
  }

  async function init() {
    if (!$('mxa-container')) return;
    try { await load(); }
    catch (e) {
      $('mxa-container').innerHTML = `<div class="banco-empty">Error: ${escHtml(e.message)}</div>`;
      return;
    }
    const printBtn = $('mxa-print');
    const clearBtn = $('mxa-clear');
    if (printBtn) printBtn.addEventListener('click', printPreview);
    if (clearBtn) clearBtn.addEventListener('click', clearAll);
    const titleInput = $('mxa-title');
    if (titleInput) {
      titleInput.value = localStorage.getItem('mis-apuntes-title') || '';
      titleInput.addEventListener('input', () => localStorage.setItem('mis-apuntes-title', titleInput.value));
    }
    render();
  }

  document.addEventListener('DOMContentLoaded', init);
})();
