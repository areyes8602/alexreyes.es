/* ============================================================
   /docencia/mi-examen/ — compositor d'examen
   Llegeix la selecció de localStorage ('mi-examen') i la fotografia
   de filtres ('mi-examen-filtros').
   Genera dos PDFs (via window.print() — vector + KaTeX intacte) a partir
   de l'HTML viu de cada pàgina font:
     - PDF d'enunciats: només els enunciats marcats, un rere l'altre.
     - PDF de solucions: els enunciats + la seva correcció pas a pas.
   Cap dels dos és una concatenació dels PDFs originals — tot es fa des de
   l'HTML.
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
      dl_enunciados: '⤓ PDF enunciados',
      dl_soluciones: '⤓ PDF soluciones',
      sin_sol: 'Sin soluciones disponibles',
      dl_json: '⤓ JSON',
      vaciar: 'Vaciar',
      de: 'De:',
      generando: 'Preparando…',
      ok: 'Listo',
      error_pdflib: 'Error al generar el PDF',
      error_fetch: 'Error al cargar el HTML de un ejercicio: ',
      no_pages: '⚠ Sin páginas en el PDF original',
      title_default: 'Examen — alexreyes.es',
      header_brand: 'alexreyes.es',
      filters_label: 'Filtros aplicados',
      no_filters: 'Sin filtros (selección manual)',
      no_solutions_for: 'Solución no disponible para este ejercicio.',
      sol_section: 'Solución',
      pregunta: 'Pregunta',
      contexto_origen: 'De',
    },
    ca: {
      vacio_titulo: "Encara no has afegit exercicis",
      vacio_desc: 'Ves al Banc d\'exercicis i prem "+ Examen" als que vulguis incloure.',
      ver_banco: 'Anar al banc d\'exercicis →',
      total_pts: 'punts totals',
      quitar: 'Treure', pts: 'pts', vacio: 'buit',
      imprimir: 'Vista / Imprimir',
      dl_enunciados: '⤓ PDF enunciats',
      dl_soluciones: '⤓ PDF solucions',
      sin_sol: 'Sense solucions disponibles',
      dl_json: '⤓ JSON',
      vaciar: 'Buidar',
      de: 'De:',
      generando: 'Preparant…',
      ok: 'Fet',
      error_pdflib: 'Error generant el PDF',
      error_fetch: 'Error carregant l\'HTML d\'un exercici: ',
      no_pages: '⚠ Sense pàgines al PDF original',
      title_default: 'Examen — alexreyes.es',
      header_brand: 'alexreyes.es',
      filters_label: 'Filtres aplicats',
      no_filters: 'Sense filtres (selecció manual)',
      no_solutions_for: 'Solució no disponible per a aquest exercici.',
      sol_section: 'Solució',
      pregunta: 'Pregunta',
      contexto_origen: 'De',
    },
    en: {
      vacio_titulo: "You haven't added any exercises yet",
      vacio_desc: 'Go to the Exercise bank and click "+ Exam" on the ones you want to include.',
      ver_banco: 'Go to exercise bank →',
      total_pts: 'total points',
      quitar: 'Remove', pts: 'pts', vacio: 'empty',
      imprimir: 'View / Print',
      dl_enunciados: '⤓ PDF questions',
      dl_soluciones: '⤓ PDF solutions',
      sin_sol: 'No solutions available',
      dl_json: '⤓ JSON',
      vaciar: 'Clear',
      de: 'From:',
      generando: 'Preparing…',
      ok: 'Done',
      error_pdflib: 'Error generating the PDF',
      error_fetch: 'Error fetching exercise HTML: ',
      no_pages: '⚠ No pages in original PDF',
      title_default: 'Exam — alexreyes.es',
      header_brand: 'alexreyes.es',
      filters_label: 'Applied filters',
      no_filters: 'No filters (manual selection)',
      no_solutions_for: 'Solution not available for this exercise.',
      sol_section: 'Solution',
      pregunta: 'Question',
      contexto_origen: 'From',
    },
  };
  const STRINGS = I18N[LANG] || I18N.es;
  const t = (k) => STRINGS[k] || k;

  const CART_KEY = 'mi-examen';
  const FILTERS_KEY = 'mi-examen-filtros';
  const $ = (id) => document.getElementById(id);

  let allIndex = null;
  let taxonomy = null;

  // ----- localStorage helpers -----
  function loadCart() {
    try {
      const raw = localStorage.getItem(CART_KEY);
      const parsed = raw ? JSON.parse(raw) : [];
      return Array.isArray(parsed) ? parsed : [];
    } catch (e) { return []; }
  }
  function saveCart(ids) { localStorage.setItem(CART_KEY, JSON.stringify(ids)); }
  function loadFilters() {
    try {
      const raw = localStorage.getItem(FILTERS_KEY);
      return raw ? JSON.parse(raw) : null;
    } catch (e) { return null; }
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

  // ============================================================
  // Editor view (in-page list of selected exercises)
  // ============================================================
  function render() {
    const ids = loadCart();
    const wrapper = $('mx-container');
    const emptyBox = $('mx-empty');
    const summary = $('mx-summary');
    const ejercicios = ids.map((id) => allIndex[id]).filter(Boolean);

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

      const sourceInfo = ej.url_enunciado
        ? `<span style="font-family:var(--mono);font-size:0.75rem;color:var(--text-faint);margin-left:0.4rem">HTML</span>`
        : `<span style="font-family:var(--mono);font-size:0.75rem;color:#c23a3a;margin-left:0.4rem">${t('no_pages')}</span>`;

      item.innerHTML = `
        <div class="mx-item-head">
          <div class="mx-item-num">${String(idx + 1).padStart(2, '0')}</div>
          <div class="mx-item-main">
            <h3 class="mx-item-title">${escHtml(ej.titulo)}</h3>
            <div class="mx-item-meta"><span class="mx-origin">${t('de')} ${origin}</span>${sourceInfo}</div>
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
      btn.title = t('sin_sol');
      return;
    }
    // Habilitada sempre que tinguem url_enunciado (l'HTML font sol portar la solució).
    // Desactivem només si CAP exercici té URL HTML.
    const anyHtml = ejercicios.some(e => e.url_enunciado);
    btn.disabled = !anyHtml;
    btn.title = anyHtml ? '' : t('sin_sol');
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
  // HTML fetching + extraction
  // ============================================================

  // Caché: una entrada per URL absoluta. Valor: { doc, styles, mainEl }.
  const pageCache = new Map();
  async function fetchPage(url) {
    if (pageCache.has(url)) return pageCache.get(url);
    const res = await fetch(url, { credentials: 'same-origin' });
    if (!res.ok) throw new Error(`HTTP ${res.status} per ${url}`);
    const html = await res.text();
    const doc = new DOMParser().parseFromString(html, 'text/html');

    // Recollim els <style> inline del head (les pàgines d'apunts en porten un
    // de gran amb tots els .def-box, .exercise, .apart, etc.)
    const styles = [];
    doc.querySelectorAll('head style').forEach((s) => {
      const css = s.textContent || '';
      if (css.trim()) styles.push(css);
    });

    const entry = { doc, styles };
    pageCache.set(url, entry);
    return entry;
  }

  // Extreu el bloc HTML d'un exercici i el devolve clonat:
  // - Si la url té #anchor: agafem #anchor (típic d'apunts amb molts exercicis).
  // - Si no: agafem .question-block (o <article> com a fallback) — típic de
  //   pàgines d'examen on cada pregunta té la seva pàgina.
  // Retorna: { node: HTMLElement, sourceUrl, hasSolution }
  async function extractExerciseBlock(ej) {
    const rawUrl = ej.url_enunciado;
    if (!rawUrl) return null;
    const [pageUrl, anchor] = rawUrl.split('#');
    const { doc } = await fetchPage(pageUrl);

    let node = null;
    if (anchor) {
      node = doc.getElementById(anchor);
    }
    if (!node) {
      // Fallback per a pàgines d'examen sense anchor (una pregunta per pàgina)
      node = doc.querySelector('.question-block') || doc.querySelector('article');
    }
    if (!node) return null;

    // Clonem per no contaminar la caché si modifiquem.
    const clone = node.cloneNode(true);

    // Detectem si conté una solució (en algun dels formats coneguts).
    const hasSolution = !!(
      clone.querySelector('.solution') ||
      clone.querySelector('.apart-solution') ||
      clone.querySelector('details > .solution, details .apart-solution')
    );

    return { node: clone, sourceUrl: pageUrl, hasSolution };
  }

  // Ajusta el bloc per al mode triat:
  // - 'enunciados': amaga totes les solucions (closes <details>, hide .solution).
  // - 'soluciones': obre totes les <details> i mostra .solution.
  function applyMode(node, mode) {
    // Treu botons i navegació de l'examen original
    node.querySelectorAll('.solution-toggle').forEach(b => b.remove());
    node.querySelectorAll('.exam-nav').forEach(n => n.remove());
    node.querySelectorAll('.no-print').forEach(n => n.remove());
    // Esborra l'enllaç tornar/anar al següent dels apunts si s'inclou en el clone
    node.querySelectorAll('nav.exam-nav, .breadcrumb').forEach(n => n.remove());

    if (mode === 'enunciados') {
      // Amaga seccions de solució (independent de les classes utilitzades)
      node.querySelectorAll('.solution').forEach(s => { s.hidden = true; s.style.display = 'none'; });
      node.querySelectorAll('.apart-solution').forEach(s => { s.style.display = 'none'; });
      // Tanca <details> (per si la pàgina les tenia obertes per defecte)
      node.querySelectorAll('details').forEach(d => { d.removeAttribute('open'); });
      // Marca les solucions perquè el CSS d'impressió les amagui també
      node.classList.add('mx-mode-enunciados');
    } else {
      // Mostra-ho tot
      node.querySelectorAll('.solution').forEach(s => { s.hidden = false; s.removeAttribute('hidden'); s.style.display = ''; });
      node.querySelectorAll('.apart-solution').forEach(s => { s.style.display = ''; });
      node.querySelectorAll('details').forEach(d => { d.setAttribute('open', ''); });
      node.classList.add('mx-mode-soluciones');
    }
    return node;
  }

  // ============================================================
  // Print area assembly
  // ============================================================

  function todayLabel() {
    const d = new Date();
    const months = {
      es: ['ene','feb','mar','abr','may','jun','jul','ago','sep','oct','nov','dic'],
      ca: ['gen','feb','març','abr','maig','juny','jul','ag','set','oct','nov','des'],
      en: ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'],
    };
    const m = (months[LANG] || months.es)[d.getMonth()];
    return `${String(d.getDate()).padStart(2, '0')} ${m} ${d.getFullYear()}`;
  }

  function buildHeaderHtml(title) {
    return `
      <header class="mxp-header">
        <div class="mxp-brand">${escHtml(t('header_brand'))}</div>
        <div class="mxp-meta">
          <span class="mxp-date">${escHtml(todayLabel())}</span>
        </div>
      </header>
      ${title ? `<h1 class="mxp-title">${escHtml(title)}</h1>` : ''}
    `;
  }

  function buildFiltersHtml() {
    const f = loadFilters();
    if (!f) {
      return `<div class="mxp-filters mxp-filters-empty"><strong>${t('filters_label')}:</strong> <em>${t('no_filters')}</em></div>`;
    }
    const chips = [];
    if (f.labels && f.labels.search_label) {
      chips.push(`<span class="mxp-chip mxp-chip-search">🔎 ${escHtml(f.labels.search_label)}</span>`);
    }
    if (f.labels && Array.isArray(f.labels.filter_chips)) {
      for (const c of f.labels.filter_chips) {
        chips.push(`<span class="mxp-chip"><span class="mxp-chip-ns">${escHtml(c.ns_label || c.ns)}:</span> ${escHtml(c.val_label || c.val)}</span>`);
      }
    }
    if (!chips.length) {
      return `<div class="mxp-filters mxp-filters-empty"><strong>${t('filters_label')}:</strong> <em>${t('no_filters')}</em></div>`;
    }
    return `
      <div class="mxp-filters">
        <strong class="mxp-filters-label">${t('filters_label')}:</strong>
        <div class="mxp-chips">${chips.join('')}</div>
      </div>
    `;
  }

  // Construeix l'àrea imprimible. Retorna el div ja inserit, llest per imprimir.
  async function buildPrintArea(mode) {
    const ids = loadCart();
    const ejercicios = ids.map(id => allIndex[id]).filter(Boolean);
    const area = $('mx-print-area');
    if (!area) throw new Error('Falta #mx-print-area al DOM');

    const title = $('mx-title')?.value || t('title_default');

    // Fetched HTML pages aporten <style> inline propis (cada apunt té el seu).
    // Els ajuntem un sol cop en un <style> dins l'àrea imprimible.
    const cssBag = new Set();
    const blocks = [];

    for (let i = 0; i < ejercicios.length; i++) {
      const ej = ejercicios[i];
      try {
        const extracted = await extractExerciseBlock(ej);
        if (!extracted) {
          blocks.push({ ej, node: null, ok: false });
          continue;
        }
        // Recollim els <style> de la pàgina font (només una vegada per URL).
        const cached = pageCache.get(extracted.sourceUrl);
        if (cached) cached.styles.forEach(css => cssBag.add(css));
        const node = applyMode(extracted.node, mode);
        // Si mode "soluciones" però no n'hi ha cap, deixem una nota.
        const noSolNote = (mode === 'soluciones' && !extracted.hasSolution);
        blocks.push({ ej, node, ok: true, noSolNote, sourceUrl: extracted.sourceUrl });
      } catch (e) {
        console.warn('Falla extraient', ej.id, e);
        blocks.push({ ej, node: null, ok: false, error: e.message });
      }
    }

    // Construeix HTML
    const headerHtml = buildHeaderHtml(title);
    const filtersHtml = buildFiltersHtml();

    // Estils inline (deduped) — embolicats en un wrapper #mxp-scope per evitar
    // que sobreescriguin estils globals si tornen a la vista d'edició.
    const inlinedStyles = Array.from(cssBag).join('\n\n');

    area.innerHTML = '';
    area.classList.toggle('mxp-mode-enunciados', mode === 'enunciados');
    area.classList.toggle('mxp-mode-soluciones', mode === 'soluciones');

    // Capçalera + filtres
    const headerWrap = document.createElement('div');
    headerWrap.className = 'mxp-cover';
    headerWrap.innerHTML = headerHtml + filtersHtml;
    area.appendChild(headerWrap);

    // Estils inline (s'apliquen a tot el document, no només a l'àrea: és la
    // manera més senzilla que .def-box etc. funcionin amb la mateixa especificitat).
    const styleEl = document.createElement('style');
    styleEl.id = 'mxp-injected-styles';
    styleEl.textContent = inlinedStyles;
    // Substituïm l'estil injectat anterior si en queda d'una impressió prèvia.
    const prev = document.getElementById('mxp-injected-styles');
    if (prev) prev.remove();
    document.head.appendChild(styleEl);

    // Preguntes
    const ol = document.createElement('ol');
    ol.className = 'mxp-questions';
    blocks.forEach((b, i) => {
      const li = document.createElement('li');
      li.className = 'mxp-question';
      const numHtml = `<div class="mxp-q-num">${t('pregunta')} ${i + 1}</div>`;
      const titleHtml = `<h2 class="mxp-q-title">${escHtml(b.ej.titulo || '')}${b.ej.puntuacion ? ` <span class="mxp-q-pts">[${b.ej.puntuacion} ${t('pts')}]</span>` : ''}</h2>`;
      const originHtml = b.ej.coleccion?.titulo
        ? `<div class="mxp-q-origin">${t('contexto_origen')}: ${escHtml(b.ej.coleccion.titulo)}${b.ej.coleccion.fecha ? ' · ' + escHtml(b.ej.coleccion.fecha) : ''}</div>`
        : '';
      li.innerHTML = numHtml + titleHtml + originHtml;
      const body = document.createElement('div');
      body.className = 'mxp-q-body';
      if (b.ok && b.node) {
        body.appendChild(b.node);
      } else {
        body.innerHTML = `<p class="mxp-q-error">${escHtml(t('error_fetch') + (b.error || ''))}</p>`;
      }
      if (b.noSolNote) {
        const note = document.createElement('p');
        note.className = 'mxp-q-no-sol';
        note.textContent = t('no_solutions_for');
        body.appendChild(note);
      }
      li.appendChild(body);
      ol.appendChild(li);
    });
    area.appendChild(ol);

    // KaTeX render (amb auto-render carregat al head). Es renderitza ara mateix
    // perquè quan s'obri el diàleg d'impressió ja estigui llest.
    if (window.renderMathInElement) {
      try { window.renderMathInElement(area, { throwOnError: false }); } catch (e) {}
    }

    return area;
  }

  // ============================================================
  // Print trigger
  // ============================================================
  async function generatePDF(mode) {
    const btnId = mode === 'enunciados' ? 'mx-dl-enun' : 'mx-dl-sol';
    const btn = $(btnId);
    const orig = btn.textContent;
    btn.disabled = true;
    btn.textContent = t('generando');

    const bodyClass = mode === 'enunciados' ? 'mx-printing-enunciados' : 'mx-printing-soluciones';

    let cleanup = () => {
      document.body.classList.remove('mx-printing', 'mx-printing-enunciados', 'mx-printing-soluciones');
      btn.textContent = orig;
      btn.disabled = false;
    };

    try {
      await buildPrintArea(mode);

      // Activa el mode imprimible (CSS s'ocupa d'amagar la resta i mostrar només
      // l'àrea imprimible quan body té .mx-printing).
      document.body.classList.add('mx-printing', bodyClass);

      // Donem a KaTeX/ressources un microtick per estabilitzar layout.
      await new Promise((resolve) => setTimeout(resolve, 50));

      // Captura el final de la impressió per restaurar l'UI.
      const onAfterPrint = () => {
        cleanup();
        window.removeEventListener('afterprint', onAfterPrint);
      };
      window.addEventListener('afterprint', onAfterPrint);

      window.print();

      // Fallback: alguns navegadors no disparen afterprint immediatament; restaurem
      // amb un timeout llarg si l'esdeveniment no arriba.
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

  function exportJSON() {
    const ids = loadCart();
    const ejercicios = ids.map(id => allIndex[id]).filter(Boolean);
    const filters = loadFilters();
    const out = {
      schema_version: 3,
      tipo_coleccion: 'examen_practica',
      titulo: $('mx-title').value || 'Examen personalizado — ' + new Date().toISOString().slice(0, 10),
      fecha: new Date().toISOString().slice(0, 10),
      filtros_aplicados: filters || null,
      puntuacion_total: ejercicios.reduce((s, e) => s + (e.puntuacion || 0), 0),
      ejercicios_ref: ejercicios.map((e, i) => ({
        numero: i + 1, id: e.id, titulo: e.titulo, puntuacion: e.puntuacion,
        url_enunciado: e.url_enunciado,
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
    $('mx-print').addEventListener('click', () => generatePDF('enunciados'));
    $('mx-clear').addEventListener('click', clearAll);
    $('mx-export').addEventListener('click', exportJSON);
    const enun = $('mx-dl-enun');
    if (enun) enun.addEventListener('click', () => generatePDF('enunciados'));
    const sol = $('mx-dl-sol');
    if (sol) sol.addEventListener('click', () => generatePDF('soluciones'));
    const titleInput = $('mx-title');
    const dateInput = $('mx-date');
    if (dateInput) dateInput.value = new Date().toISOString().slice(0, 10);
    if (titleInput) {
      titleInput.value = localStorage.getItem('mi-examen-title') || '';
      titleInput.addEventListener('input', () => localStorage.setItem('mi-examen-title', titleInput.value));
    }
    render();
  }

  document.addEventListener('DOMContentLoaded', init);
})();
