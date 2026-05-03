/* ============================================================
   /docencia/ejercicios/ — lógica del banco
   - Carga tags.json + ejercicios-index.json
   - Genera facetas a partir de los namespaces
   - Filtra (AND entre namespaces, OR dentro)
   - Sincroniza estado con URL hash para URLs compartibles
   ============================================================ */
(function () {
  'use strict';

  const LANG = (document.documentElement.lang || 'es').slice(0, 2);
  const I18N = {
    es: {
      ejercicio: 'ejercicio', ejercicios: 'ejercicios', pts: 'pts',
      error_carga: 'Error al cargar los datos',
      btn_enunciado: 'Enunciado', btn_pdf: 'PDF', btn_add: '+ Examen',
      btn_added: '✓ Añadido', examen_link: 'Mi examen',
    },
    ca: {
      ejercicio: 'exercici', ejercicios: 'exercicis', pts: 'pts',
      error_carga: 'Error en carregar les dades',
      btn_enunciado: 'Enunciat', btn_pdf: 'PDF', btn_add: '+ Examen',
      btn_added: '✓ Afegit', examen_link: 'El meu examen',
    },
    en: {
      ejercicio: 'exercise', ejercicios: 'exercises', pts: 'pts',
      error_carga: 'Error loading data',
      btn_enunciado: 'View', btn_pdf: 'PDF', btn_add: '+ Exam',
      btn_added: '✓ Added', examen_link: 'My exam',
    },
  };
  const STRINGS = I18N[LANG] || I18N.es;
  const t = (k) => STRINGS[k] || k;

  // KaTeX auto-render NO inclou `$...$` als delimitadors per defecte. El nostre
  // contingut sí l'usa, així que cal passar la llista completa cada cop.
  const KATEX_OPTS = {
    delimiters: [
      { left: '$$', right: '$$', display: true },
      { left: '\\[', right: '\\]', display: true },
      { left: '$', right: '$', display: false },
      { left: '\\(', right: '\\)', display: false },
    ],
    throwOnError: false,
  };

  // ---- Cart (localStorage) ----
  const CART_KEY = 'mi-examen';
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
    // També actualitzem la fotografia de filtres: així si l'usuari afegeix
    // exercicis amb filtres concrets, /docencia/mi-examen/ els mostrarà.
    if (typeof persistFiltersSnapshot === 'function') persistFiltersSnapshot();
  }
  function updateCartBadge() {
    const c = loadCart();
    const badge = document.getElementById('cart-badge');
    if (badge) {
      badge.textContent = c.length;
      badge.style.display = c.length ? 'inline-flex' : 'none';
    }
  }

  const els = {
    search: document.getElementById('banco-search'),
    clear: document.getElementById('banco-clear'),
    facets: document.getElementById('banco-facets'),
    count: document.getElementById('banco-count'),
    activeFilters: document.getElementById('banco-active-filters'),
    results: document.getElementById('banco-results'),
    empty: document.getElementById('banco-empty'),
    sort: document.getElementById('banco-sort'),
  };

  let taxonomy = null;
  let allEjercicios = [];
  let state = { search: '', filters: {}, sort: 'fecha_desc' };

  // ---- URL sync ----
  function serialize() {
    const params = new URLSearchParams();
    if (state.search) params.set('q', state.search);
    for (const [ns, values] of Object.entries(state.filters)) {
      if (values && values.length) params.set(ns, values.join(','));
    }
    if (state.sort && state.sort !== 'fecha_desc') params.set('sort', state.sort);
    return params.toString();
  }
  function deserialize(hash) {
    const params = new URLSearchParams(hash.replace(/^#/, ''));
    state.search = params.get('q') || '';
    state.sort = params.get('sort') || 'fecha_desc';
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

  // ---- Data load ----
  async function load() {
    const [taxRes, idxRes] = await Promise.all([
      fetch('/assets/data/tags.json'),
      fetch('/assets/data/ejercicios-index.json'),
    ]);
    taxonomy = await taxRes.json();
    const idx = await idxRes.json();
    allEjercicios = idx.ejercicios || [];
  }

  // ---- Filtering ----
  function ejercicioMatches(ej) {
    // search
    if (state.search) {
      const q = state.search.toLowerCase();
      const hay = (ej.search_text && ej.search_text[LANG]) || '';
      if (!hay.includes(q)) return false;
    }
    // filters: AND across namespaces, OR within a namespace
    for (const [ns, selected] of Object.entries(state.filters)) {
      if (!selected || !selected.length) continue;
      const ejValue = ej.tags ? ej.tags[ns] : undefined;
      if (ejValue === undefined || ejValue === null) return false;
      const ejValues = Array.isArray(ejValue) ? ejValue : [ejValue];
      const anyMatch = selected.some((s) => ejValues.includes(s));
      if (!anyMatch) return false;
    }
    return true;
  }

  function filtered() {
    let list = allEjercicios.filter(ejercicioMatches);
    switch (state.sort) {
      case 'fecha_desc':
        list.sort((a, b) => (b.coleccion?.fecha || '').localeCompare(a.coleccion?.fecha || ''));
        break;
      case 'fecha_asc':
        list.sort((a, b) => (a.coleccion?.fecha || '').localeCompare(b.coleccion?.fecha || ''));
        break;
      case 'puntuacion_desc':
        list.sort((a, b) => (b.puntuacion || 0) - (a.puntuacion || 0));
        break;
      case 'dificultad':
        list.sort((a, b) => dificOrder(a) - dificOrder(b));
        break;
      case 'titulo':
        list.sort((a, b) => (a.titulo || '').localeCompare(b.titulo || '', LANG));
        break;
    }
    return list;
  }
  function dificOrder(ej) {
    const d = ej.tags && ej.tags.dificultad;
    const def = taxonomy.namespaces.dificultad.valores[d];
    return def && def.orden ? def.orden : 99;
  }

  // ---- Facet counts (dynamic, based on current filters except the namespace itself) ----
  function countsForNamespace(ns) {
    const counts = {};
    for (const ej of allEjercicios) {
      // Apply all filters EXCEPT this namespace, plus search
      if (state.search) {
        const q = state.search.toLowerCase();
        const hay = (ej.search_text && ej.search_text[LANG]) || '';
        if (!hay.includes(q)) continue;
      }
      let ok = true;
      for (const [otherNs, selected] of Object.entries(state.filters)) {
        if (otherNs === ns || !selected || !selected.length) continue;
        const ejValue = ej.tags ? ej.tags[otherNs] : undefined;
        if (ejValue === undefined || ejValue === null) { ok = false; break; }
        const ejValues = Array.isArray(ejValue) ? ejValue : [ejValue];
        if (!selected.some((s) => ejValues.includes(s))) { ok = false; break; }
      }
      if (!ok) continue;
      const v = ej.tags ? ej.tags[ns] : undefined;
      if (v === undefined || v === null) continue;
      const vs = Array.isArray(v) ? v : [v];
      for (const val of vs) counts[val] = (counts[val] || 0) + 1;
    }
    return counts;
  }

  // ---- Render ----
  function getLabel(ns, value) {
    const def = taxonomy.namespaces[ns]?.valores?.[value];
    return (def?.label?.[LANG]) || value;
  }
  function getNsLabel(ns) {
    return taxonomy.namespaces[ns]?.label?.[LANG] || ns;
  }

  function renderFacets() {
    const nsOrder = Object.keys(taxonomy.namespaces);
    els.facets.innerHTML = '';
    for (const ns of nsOrder) {
      const nsDef = taxonomy.namespaces[ns];
      const counts = countsForNamespace(ns);
      const values = Object.keys(nsDef.valores);
      // only show values that appear OR are currently selected
      const selected = state.filters[ns] || [];
      const shown = values.filter((v) => counts[v] > 0 || selected.includes(v));
      if (!shown.length) continue;

      const div = document.createElement('div');
      div.className = 'facet';
      const totalForNs = shown.reduce((s, v) => s + (counts[v] || 0), 0);
      div.innerHTML = `
        <div class="facet-title">
          <span>${escapeHtml(getNsLabel(ns))}</span>
          <span class="facet-count">${totalForNs}</span>
        </div>
        <div class="facet-values"></div>
      `;
      const container = div.querySelector('.facet-values');
      // Sort values by count desc, then by orden (for difficulty), then by label
      shown.sort((a, b) => {
        const ca = counts[a] || 0, cb = counts[b] || 0;
        if (cb !== ca) return cb - ca;
        const oa = nsDef.valores[a].orden ?? 99;
        const ob = nsDef.valores[b].orden ?? 99;
        if (oa !== ob) return oa - ob;
        return getLabel(ns, a).localeCompare(getLabel(ns, b), LANG);
      });
      for (const val of shown) {
        const c = counts[val] || 0;
        const id = `f-${ns}-${val.replace(/[^a-zA-Z0-9_-]/g, '_')}`;
        const checked = selected.includes(val) ? 'checked' : '';
        const zeroClass = c === 0 && !selected.includes(val) ? 'is-zero' : '';
        const label = document.createElement('label');
        label.className = 'facet-value ' + zeroClass;
        label.innerHTML = `
          <input type="checkbox" id="${id}" data-ns="${escapeAttr(ns)}" data-val="${escapeAttr(val)}" ${checked}>
          <span>${escapeHtml(getLabel(ns, val))}</span>
          <span class="fv-count">${c}</span>
        `;
        label.querySelector('input').addEventListener('change', onFacetChange);
        container.appendChild(label);
      }
      // collapse if the namespace has no active selection and we have many facets
      div.querySelector('.facet-title').addEventListener('click', (e) => {
        if (e.target.tagName === 'INPUT') return;
        div.classList.toggle('collapsed');
      });
      els.facets.appendChild(div);
    }
  }

  function renderResults() {
    const list = filtered();
    els.count.innerHTML = `<strong>${list.length}</strong> ${list.length === 1 ? t('ejercicio') : t('ejercicios')}`;
    els.results.innerHTML = '';
    if (!list.length) {
      els.empty.hidden = false;
      return;
    }
    els.empty.hidden = true;
    for (const ej of list) {
      const div = document.createElement('div');
      div.className = 'ej-card';
      if (inCart(ej.id)) div.classList.add('in-cart');
      const tagsHtml = renderEjTags(ej);
      const colMeta = [ej.coleccion?.titulo, ej.coleccion?.fecha, ej.coleccion?.grupo]
        .filter(Boolean)
        .map(escapeHtml)
        .join('<span class="sep"></span>');

      // Action buttons
      const actions = [];
      if (ej.url_enunciado) {
        actions.push(`<a class="ej-btn ej-btn-primary" href="${escapeAttr(ej.url_enunciado)}">${t('btn_enunciado')}</a>`);
      }
      if (ej.url_pdf) {
        actions.push(`<a class="ej-btn" href="${escapeAttr(ej.url_pdf)}" target="_blank" rel="noopener">${t('btn_pdf')}</a>`);
      }
      const added = inCart(ej.id);
      actions.push(`<button class="ej-btn ej-btn-cart ${added ? 'is-added' : ''}" data-cart-id="${escapeAttr(ej.id)}">${added ? t('btn_added') : t('btn_add')}</button>`);

      div.innerHTML = `
        <div class="ej-card-top">
          <div class="ej-card-title">${escapeHtml(ej.titulo)}</div>
          <div class="ej-card-puntos">${ej.puntuacion || 0} ${t('pts')}</div>
        </div>
        <div class="ej-card-meta">${colMeta}</div>
        <div class="ej-card-tags">${tagsHtml}</div>
        <div class="ej-card-actions">${actions.join('')}</div>
      `;

      // Wire cart button
      const cartBtn = div.querySelector('[data-cart-id]');
      if (cartBtn) {
        cartBtn.addEventListener('click', (e) => {
          e.preventDefault();
          toggleCart(ej.id);
          const nowAdded = inCart(ej.id);
          cartBtn.textContent = nowAdded ? t('btn_added') : t('btn_add');
          cartBtn.classList.toggle('is-added', nowAdded);
          div.classList.toggle('in-cart', nowAdded);
        });
      }

      els.results.appendChild(div);
    }
    // KaTeX in titles if present
    if (window.renderMathInElement) {
      try { window.renderMathInElement(els.results, KATEX_OPTS); } catch (e) {}
    }
  }

  function renderEjTags(ej) {
    if (!ej.tags) return '';
    const parts = [];
    // Priorizar dificultad, descriptor_ib, tema, habilidad
    const preferredOrder = ['dificultad', 'descriptor_ib', 'tema', 'habilidad', 'formato'];
    const keys = preferredOrder.filter((k) => k in ej.tags)
      .concat(Object.keys(ej.tags).filter((k) => !preferredOrder.includes(k)));
    for (const ns of keys) {
      const v = ej.tags[ns];
      const vs = Array.isArray(v) ? v : [v];
      for (const val of vs) {
        parts.push(
          `<span class="ej-tag" data-ns="${escapeAttr(ns)}" data-val="${escapeAttr(val)}">${escapeHtml(getLabel(ns, val))}</span>`
        );
      }
    }
    return parts.join('');
  }

  function renderActiveFilters() {
    els.activeFilters.innerHTML = '';
    const chips = [];
    if (state.search) {
      chips.push(makeChip('search', null, `"${state.search}"`));
    }
    for (const [ns, vals] of Object.entries(state.filters)) {
      for (const v of (vals || [])) {
        chips.push(makeChip(ns, v, `${getNsLabel(ns)}: ${getLabel(ns, v)}`));
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
      if (ns === 'search') {
        state.search = '';
        els.search.value = '';
      } else {
        state.filters[ns] = (state.filters[ns] || []).filter((x) => x !== val);
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
      state.filters[ns] = (state.filters[ns] || []).filter((x) => x !== val);
      if (!state.filters[ns].length) delete state.filters[ns];
    }
    afterStateChange();
  }
  function onSearch() {
    state.search = els.search.value.trim();
    afterStateChange();
  }
  function onSort() {
    state.sort = els.sort.value;
    afterStateChange();
  }
  function onClear() {
    state.search = '';
    state.filters = {};
    els.search.value = '';
    afterStateChange();
  }

  function afterStateChange() {
    renderFacets();
    renderResults();
    renderActiveFilters();
    pushState();
    persistFiltersSnapshot();
  }

  // Persisteix l'estat actual de filtres a localStorage perquè /docencia/mi-examen/
  // pugui mostrar el bloc "Filtres aplicats" del PDF generat.
  function persistFiltersSnapshot() {
    try {
      const snapshot = {
        search: state.search || '',
        filters: state.filters || {},
        sort: state.sort || 'fecha_desc',
        // labels resoltes amb la taxonomia (per si l'usuari neteja l'idioma)
        labels: {
          search_label: state.search ? `"${state.search}"` : '',
          filter_chips: Object.entries(state.filters || {}).flatMap(([ns, vals]) =>
            (vals || []).map((v) => ({
              ns, val: v,
              ns_label: getNsLabel(ns),
              val_label: getLabel(ns, v),
              full: `${getNsLabel(ns)}: ${getLabel(ns, v)}`,
            }))
          ),
        },
        saved_at: new Date().toISOString(),
        lang: LANG,
      };
      localStorage.setItem('mi-examen-filtros', JSON.stringify(snapshot));
    } catch (e) { /* ignora quota / disabled */ }
  }

  // ---- Init ----
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

  // Debounce search
  let searchTimer;
  function debouncedSearch() {
    clearTimeout(searchTimer);
    searchTimer = setTimeout(onSearch, 120);
  }

  async function init() {
    try {
      await load();
    } catch (e) {
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
    persistFiltersSnapshot();
  }

  document.addEventListener('DOMContentLoaded', init);
})();
