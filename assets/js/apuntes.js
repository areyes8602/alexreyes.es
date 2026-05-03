/* ============================================================
   /docencia/apuntes/ — banc d'apunts (paral·lel al banc d'exercicis)
   - Carrega assets/data/apuntes-index.json
   - Genera facetes a partir dels namespaces presents en els datos
   - Filtra (AND entre namespaces, OR dins) + cerca lliure
   - Sincronitza estat amb URL hash per compartir filtres
   ============================================================ */
(function () {
  'use strict';

  const LANG = (document.documentElement.lang || 'es').slice(0, 2);

  const I18N = {
    es: {
      apunte: 'apunte', apuntes: 'apuntes',
      error_carga: 'Error al cargar los datos',
      btn_abrir: 'Abrir →',
      btn_add: '+ Apuntes',
      btn_added: '✓ Añadido',
      mis_apuntes: 'Mis apuntes',
      mis_apuntes_intro: 'Selecciona apuntes con',
      mis_apuntes_intro2: 'para componer un PDF.',
      todos_filtros: 'Borrar todos los filtros',
      cargando: 'Cargando…',
      ordenar: 'Ordenar por:',
      orden_materia: 'Materia · Unidad',
      orden_titulo: 'Título (A-Z)',
      sin_resultados: 'No hay apuntes que coincidan con los filtros actuales.',
      buscar_placeholder: 'Buscar apuntes…',
      // Labels de namespaces y valores
      ns_materia: 'Materia',
      ns_idioma: 'Idioma',
      ns_unidad: 'Unidad',
      ns_tipo_apunte: 'Tipo',
      ns_concepto_iba: 'Concepto IB',
      ns_concepto_bach: 'Concepto Bachillerato',
      ns_concepto_eso: 'Concepto ESO',
      val_seccion: 'Sección',
      val_index_unidad: 'Índice de unidad',
      val_concepto: 'Concepto IB',
      val_index_general: 'Hub general',
    },
    ca: {
      apunte: 'apunt', apuntes: 'apunts',
      error_carga: 'Error en carregar les dades',
      btn_abrir: 'Obrir →',
      btn_add: '+ Apunts',
      btn_added: '✓ Afegit',
      mis_apuntes: 'Els meus apunts',
      mis_apuntes_intro: 'Selecciona apunts amb',
      mis_apuntes_intro2: 'per compondre un PDF.',
      todos_filtros: 'Esborrar tots els filtres',
      cargando: 'Carregant…',
      ordenar: 'Ordenar per:',
      orden_materia: 'Matèria · Unitat',
      orden_titulo: 'Títol (A-Z)',
      sin_resultados: 'No hi ha apunts que coincideixin amb els filtres actuals.',
      buscar_placeholder: 'Cercar apunts…',
      ns_materia: 'Matèria',
      ns_idioma: 'Idioma',
      ns_unidad: 'Unitat',
      ns_tipo_apunte: 'Tipus',
      ns_concepto_iba: 'Concepte IB',
      ns_concepto_bach: 'Concepte Batxillerat',
      ns_concepto_eso: 'Concepte ESO',
      val_seccion: 'Apartat',
      val_index_unidad: 'Índex d\'unitat',
      val_concepto: 'Concepte IB',
      val_index_general: 'Hub general',
    },
    en: {
      apunte: 'note', apuntes: 'notes',
      error_carga: 'Error loading data',
      btn_abrir: 'Open →',
      btn_add: '+ Notes',
      btn_added: '✓ Added',
      mis_apuntes: 'My notes',
      mis_apuntes_intro: 'Select notes with',
      mis_apuntes_intro2: 'to build a PDF.',
      todos_filtros: 'Clear all filters',
      cargando: 'Loading…',
      ordenar: 'Sort by:',
      orden_materia: 'Subject · Unit',
      orden_titulo: 'Title (A-Z)',
      sin_resultados: 'No notes match the current filters.',
      buscar_placeholder: 'Search notes…',
      ns_materia: 'Subject',
      ns_idioma: 'Language',
      ns_unidad: 'Unit',
      ns_tipo_apunte: 'Type',
      ns_concepto_iba: 'IB concept',
      ns_concepto_bach: 'Bachillerato concept',
      ns_concepto_eso: 'ESO concept',
      val_seccion: 'Section',
      val_index_unidad: 'Unit index',
      val_concepto: 'IB concept',
      val_index_general: 'General hub',
    },
  };
  const STRINGS = I18N[LANG] || I18N.es;
  const t = (k) => STRINGS[k] || k;

  // ---- Cart (localStorage) — per construir un PDF compilat d'apunts a /docencia/mis-apuntes/ ----
  const CART_KEY = 'mis-apuntes';
  function loadCart() {
    try {
      const raw = localStorage.getItem(CART_KEY);
      const parsed = raw ? JSON.parse(raw) : [];
      return Array.isArray(parsed) ? parsed : [];
    } catch (e) { return []; }
  }
  function saveCart(ids) {
    try { localStorage.setItem(CART_KEY, JSON.stringify(ids)); } catch (e) {}
    updateCartBadge();
  }
  function inCart(id) { return loadCart().includes(id); }
  function toggleCart(id) {
    const c = loadCart();
    const idx = c.indexOf(id);
    if (idx >= 0) c.splice(idx, 1); else c.push(id);
    saveCart(c);
  }
  function updateCartBadge() {
    const c = loadCart();
    const badge = document.getElementById('cart-badge-apuntes');
    if (badge) {
      badge.textContent = c.length;
      badge.style.display = c.length ? 'inline-flex' : 'none';
    }
  }

  // KaTeX auto-render NO inclou `$...$` per defecte. Cal passar la llista.
  const KATEX_OPTS = {
    delimiters: [
      { left: '$$', right: '$$', display: true },
      { left: '\\[', right: '\\]', display: true },
      { left: '$', right: '$', display: false },
      { left: '\\(', right: '\\)', display: false },
    ],
    throwOnError: false,
  };

  // Labels específicas para valores conocidos. El resto cae al raw value
  // (slugs como 'u-probabilitat', 'NM-3-6', 'ccss-1btl').
  // Para tags curriculares (concepto_iba, concepto_bach, concepto_eso) que
  // puedan venir desde sidecar meta.json, intentaremos resolver desde
  // tags.json si está cargado.
  const KNOWN_VAL_LABELS = {
    materia: {
      'ib-ai-hl': { es: 'IB AI HL', ca: 'IB AI HL', en: 'IB AI HL' },
      'ib-ai-sl': { es: 'IB AI SL', ca: 'IB AI SL', en: 'IB AI SL' },
      'ccss-1btl': { es: 'CCSS 1º BTL', ca: 'CCSS 1r BTL', en: 'CCSS 1st BTL' },
      'ccss-2btl': { es: 'CCSS 2º BTL', ca: 'CCSS 2n BTL', en: 'CCSS 2nd BTL' },
      'eso-2': { es: '2º ESO', ca: '2n ESO', en: '2nd ESO' },
    },
    idioma: {
      'es': { es: 'Español', ca: 'Castellà', en: 'Spanish' },
      'ca': { es: 'Catalán', ca: 'Català', en: 'Catalan' },
      'en': { es: 'Inglés', ca: 'Anglès', en: 'English' },
    },
    tipo_apunte: {
      'seccion': { es: 'Sección', ca: 'Apartat', en: 'Section' },
      'index_unidad': { es: 'Índice de unidad', ca: 'Índex d\'unitat', en: 'Unit index' },
      'concepto': { es: 'Concepto IB', ca: 'Concepte IB', en: 'IB concept' },
      'index_general': { es: 'Hub general', ca: 'Hub general', en: 'General hub' },
    },
  };

  // Orden manual de namespaces a mostrar como facetas (lo que NO esté aquí
  // se añade al final por orden alfabético).
  const FACET_ORDER = ['materia', 'idioma', 'unidad', 'tipo_apunte', 'concepto_iba', 'concepto_bach', 'concepto_eso'];

  // Labels de namespaces (si no, se cae al id de namespace)
  function getNsLabel(ns) {
    const k = 'ns_' + ns;
    return STRINGS[k] || ns;
  }

  // Label de un valor de un namespace
  function getValLabel(ns, val) {
    const def = KNOWN_VAL_LABELS[ns]?.[val];
    if (def) return def[LANG] || val;
    // Para tipos que no están aquí (unidad, conceptos curriculares), devolvemos
    // el slug crudo. Los slugs son legibles ('u-probabilitat', 'NM-3-6').
    return val;
  }

  const els = {
    search: document.getElementById('apuntes-search'),
    clear: document.getElementById('apuntes-clear'),
    facets: document.getElementById('apuntes-facets'),
    count: document.getElementById('apuntes-count'),
    activeFilters: document.getElementById('apuntes-active-filters'),
    results: document.getElementById('apuntes-results'),
    empty: document.getElementById('apuntes-empty'),
    sort: document.getElementById('apuntes-sort'),
  };

  let allApuntes = [];
  let state = { search: '', filters: {}, sort: 'materia' };
  let availableNamespaces = []; // detected on load

  // ---- URL sync ----
  function serialize() {
    const params = new URLSearchParams();
    if (state.search) params.set('q', state.search);
    for (const [ns, values] of Object.entries(state.filters)) {
      if (values && values.length) params.set(ns, values.join(','));
    }
    if (state.sort && state.sort !== 'materia') params.set('sort', state.sort);
    return params.toString();
  }
  function deserialize(hash) {
    const params = new URLSearchParams(hash.replace(/^#/, ''));
    state.search = params.get('q') || '';
    state.sort = params.get('sort') || 'materia';
    state.filters = {};
    for (const [k, v] of params.entries()) {
      if (k === 'q' || k === 'sort') continue;
      state.filters[k] = v.split(',').filter(Boolean);
    }
  }
  function pushState() {
    const s = serialize();
    history.replaceState(null, '', s ? '#' + s : location.pathname);
  }

  // ---- Data ----
  async function load() {
    const res = await fetch('/assets/data/apuntes-index.json');
    if (!res.ok) throw new Error('HTTP ' + res.status);
    const idx = await res.json();
    allApuntes = idx.apuntes || [];

    // Detectamos los namespaces presentes
    const seen = new Set();
    for (const a of allApuntes) {
      for (const k of Object.keys(a.tags || {})) seen.add(k);
    }
    // Orden: los del FACET_ORDER primero, después el resto alfabético
    const known = FACET_ORDER.filter(ns => seen.has(ns));
    const extra = [...seen].filter(ns => !FACET_ORDER.includes(ns)).sort();
    availableNamespaces = [...known, ...extra];
  }

  // ---- Filter ----
  function matches(a) {
    if (state.search) {
      const q = state.search.toLowerCase();
      const hay = a.search_text || '';
      if (!hay.includes(q)) return false;
    }
    for (const [ns, sel] of Object.entries(state.filters)) {
      if (!sel || !sel.length) continue;
      const v = (a.tags || {})[ns];
      if (v === undefined || v === null) return false;
      const vs = Array.isArray(v) ? v : [v];
      if (!sel.some(s => vs.includes(s))) return false;
    }
    return true;
  }

  function filtered() {
    let list = allApuntes.filter(matches);
    switch (state.sort) {
      case 'titulo':
        list.sort((a, b) => (a.titulo || '').localeCompare(b.titulo || '', LANG));
        break;
      case 'materia':
      default:
        list.sort((a, b) => {
          const ka = (a.materia || '') + '/' + (a.unidad || '') + '/' + (a.section_num || '');
          const kb = (b.materia || '') + '/' + (b.unidad || '') + '/' + (b.section_num || '');
          return ka.localeCompare(kb, LANG);
        });
    }
    return list;
  }

  // ---- Facet counts (excluyendo el namespace propio) ----
  function countsFor(ns) {
    const counts = {};
    for (const a of allApuntes) {
      if (state.search) {
        const q = state.search.toLowerCase();
        if (!(a.search_text || '').includes(q)) continue;
      }
      let ok = true;
      for (const [otherNs, sel] of Object.entries(state.filters)) {
        if (otherNs === ns || !sel || !sel.length) continue;
        const v = (a.tags || {})[otherNs];
        if (v === undefined || v === null) { ok = false; break; }
        const vs = Array.isArray(v) ? v : [v];
        if (!sel.some(s => vs.includes(s))) { ok = false; break; }
      }
      if (!ok) continue;
      const v = (a.tags || {})[ns];
      if (v === undefined || v === null) continue;
      const vs = Array.isArray(v) ? v : [v];
      for (const val of vs) counts[val] = (counts[val] || 0) + 1;
    }
    return counts;
  }

  // ---- Render ----
  function renderFacets() {
    els.facets.innerHTML = '';
    for (const ns of availableNamespaces) {
      const counts = countsFor(ns);
      const sel = state.filters[ns] || [];
      const allValues = new Set([...Object.keys(counts), ...sel]);
      const shown = [...allValues];
      if (!shown.length) continue;

      shown.sort((a, b) => {
        const ca = counts[a] || 0, cb = counts[b] || 0;
        if (cb !== ca) return cb - ca;
        return getValLabel(ns, a).localeCompare(getValLabel(ns, b), LANG);
      });

      const div = document.createElement('div');
      div.className = 'facet';
      const total = shown.reduce((s, v) => s + (counts[v] || 0), 0);
      div.innerHTML = `
        <div class="facet-title">
          <span>${escapeHtml(getNsLabel(ns))}</span>
          <span class="facet-count">${total}</span>
        </div>
        <div class="facet-values"></div>
      `;
      const container = div.querySelector('.facet-values');
      for (const val of shown) {
        const c = counts[val] || 0;
        const id = `f-${ns}-${val.replace(/[^a-zA-Z0-9_-]/g, '_')}`;
        const checked = sel.includes(val) ? 'checked' : '';
        const zeroClass = (c === 0 && !sel.includes(val)) ? 'is-zero' : '';
        const label = document.createElement('label');
        label.className = 'facet-value ' + zeroClass;
        label.innerHTML = `
          <input type="checkbox" id="${id}" data-ns="${escapeAttr(ns)}" data-val="${escapeAttr(val)}" ${checked}>
          <span>${escapeHtml(getValLabel(ns, val))}</span>
          <span class="fv-count">${c}</span>
        `;
        label.querySelector('input').addEventListener('change', onFacetChange);
        container.appendChild(label);
      }
      div.querySelector('.facet-title').addEventListener('click', (e) => {
        if (e.target.tagName === 'INPUT') return;
        div.classList.toggle('collapsed');
      });
      els.facets.appendChild(div);
    }
  }

  function renderResults() {
    const list = filtered();
    els.count.innerHTML = `<strong>${list.length}</strong> ${list.length === 1 ? t('apunte') : t('apuntes')}`;
    els.results.innerHTML = '';
    if (!list.length) { els.empty.hidden = false; return; }
    els.empty.hidden = true;

    // REUSAMOS LAS CLASES DEL BANCO DE EJERCICIOS (.ej-card, .ej-card-*, .ej-btn*)
    // que ya están en banco.css y verificadas. Así garantizamos coherencia
    // visual con el banco de ejercicios y aprovechamos CSS ya estable.
    for (const a of list) {
      const card = document.createElement('div');
      card.className = 'ej-card';
      if (inCart(a.id)) card.classList.add('in-cart');

      const tipoLabel = getValLabel('tipo_apunte', a.tipo);
      const materiaLabel = getValLabel('materia', a.materia);

      // Tags: materia, tipo, idioma + conceptos curriculares (concepto_iba/bach/eso)
      const tagsParts = [
        `<span class="ej-tag" data-ns="materia">${escapeHtml(materiaLabel)}</span>`,
        `<span class="ej-tag" data-ns="tipo_apunte">${escapeHtml(tipoLabel)}</span>`,
        `<span class="ej-tag" data-ns="idioma">${escapeHtml(a.lang.toUpperCase())}</span>`,
      ];
      if (a.unidad) {
        tagsParts.push(`<span class="ej-tag" data-ns="unidad">${escapeHtml(a.unidad)}</span>`);
      }
      for (const ns of ['concepto_iba', 'concepto_bach', 'concepto_eso']) {
        const vals = (a.tags || {})[ns];
        if (!vals) continue;
        const arr = Array.isArray(vals) ? vals : [vals];
        for (const v of arr) {
          tagsParts.push(`<span class="ej-tag" data-ns="${escapeAttr(ns)}">${escapeHtml(v)}</span>`);
        }
      }

      const colMeta = [
        a.materia,
        a.unidad,
        a.section_num ? 'sección ' + a.section_num : '',
      ].filter(Boolean).map(escapeHtml).join('<span class="sep"></span>');

      const added = inCart(a.id);
      const actions = [
        `<a class="ej-btn ej-btn-primary" href="${escapeAttr(a.url)}">${t('btn_abrir')}</a>`,
        `<button class="ej-btn ej-btn-cart ${added ? 'is-added' : ''}" data-cart-id="${escapeAttr(a.id)}">${added ? t('btn_added') : t('btn_add')}</button>`,
      ];

      card.innerHTML = `
        <div class="ej-card-top">
          <div class="ej-card-title">${escapeHtml(a.titulo)}</div>
        </div>
        <div class="ej-card-meta">${colMeta}</div>
        ${a.descripcion ? `<p style="font-size:0.86rem;color:var(--text-soft);margin:0.4rem 0 0.6rem;line-height:1.5">${escapeHtml(a.descripcion)}</p>` : ''}
        <div class="ej-card-tags">${tagsParts.join('')}</div>
        <div class="ej-card-actions">${actions.join('')}</div>
      `;

      const cartBtn = card.querySelector('[data-cart-id]');
      if (cartBtn) {
        cartBtn.addEventListener('click', (e) => {
          e.preventDefault();
          toggleCart(a.id);
          const nowAdded = inCart(a.id);
          cartBtn.textContent = nowAdded ? t('btn_added') : t('btn_add');
          cartBtn.classList.toggle('is-added', nowAdded);
          card.classList.toggle('in-cart', nowAdded);
        });
      }

      els.results.appendChild(card);
    }

    if (window.renderMathInElement) {
      try { window.renderMathInElement(els.results, KATEX_OPTS); } catch (e) {}
    }
  }

  function renderActiveFilters() {
    els.activeFilters.innerHTML = '';
    const chips = [];
    if (state.search) chips.push(makeChip('search', null, `"${state.search}"`));
    for (const [ns, vals] of Object.entries(state.filters)) {
      for (const v of (vals || [])) {
        chips.push(makeChip(ns, v, `${getNsLabel(ns)}: ${getValLabel(ns, v)}`));
      }
    }
    for (const c of chips) els.activeFilters.appendChild(c);
    els.clear.disabled = chips.length === 0;
  }
  function makeChip(ns, val, label) {
    const btn = document.createElement('button');
    btn.className = 'active-chip';
    btn.textContent = label;
    btn.addEventListener('click', () => {
      if (ns === 'search') { state.search = ''; els.search.value = ''; }
      else {
        state.filters[ns] = (state.filters[ns] || []).filter(x => x !== val);
        if (!state.filters[ns].length) delete state.filters[ns];
      }
      afterStateChange();
    });
    return btn;
  }

  // ---- Handlers ----
  function onFacetChange(e) {
    const ns = e.target.dataset.ns;
    const val = e.target.dataset.val;
    if (e.target.checked) {
      state.filters[ns] = state.filters[ns] || [];
      if (!state.filters[ns].includes(val)) state.filters[ns].push(val);
    } else {
      state.filters[ns] = (state.filters[ns] || []).filter(x => x !== val);
      if (!state.filters[ns].length) delete state.filters[ns];
    }
    afterStateChange();
  }
  function onSearch() { state.search = els.search.value.trim(); afterStateChange(); }
  function onSort() { state.sort = els.sort.value; afterStateChange(); }
  function onClear() {
    state.search = ''; state.filters = {};
    els.search.value = '';
    afterStateChange();
  }

  function afterStateChange() {
    renderFacets();
    renderResults();
    renderActiveFilters();
    pushState();
  }

  function syncUIFromState() {
    els.search.value = state.search;
    els.sort.value = state.sort;
  }

  // ---- Helpers ----
  function escapeHtml(s) {
    return String(s ?? '').replace(/[&<>"']/g, (c) => ({
      '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;',
    }[c]));
  }
  function escapeAttr(s) { return escapeHtml(s); }

  let searchTimer;
  function debouncedSearch() {
    clearTimeout(searchTimer);
    searchTimer = setTimeout(onSearch, 120);
  }

  async function init() {
    if (!els.results) return;
    try { await load(); }
    catch (e) {
      els.results.innerHTML = `<div class="banco-empty">${t('error_carga')}: ${escapeHtml(e.message)}</div>`;
      return;
    }
    deserialize(location.hash);
    syncUIFromState();
    els.search.addEventListener('input', debouncedSearch);
    els.clear.addEventListener('click', onClear);
    els.sort.addEventListener('change', onSort);
    window.addEventListener('hashchange', () => {
      deserialize(location.hash);
      syncUIFromState();
      renderFacets();
      renderResults();
      renderActiveFilters();
    });
    renderFacets();
    renderResults();
    renderActiveFilters();
    updateCartBadge();
  }

  document.addEventListener('DOMContentLoaded', init);
})();
