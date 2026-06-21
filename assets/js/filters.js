/* ============================================================
   Filtro compartido — alexreyes.es
   Activa cualquier bloque .flt de la página. Sin dependencias.

   Markup faceteado:
     <div class="flt" data-items=".mi-item" data-count="miCount">
       <div class="flt-concepts">
         <span class="flt-label">Filtrar por</span>
         <button class="flt-concept" data-group="area" aria-expanded="false">Área<span class="flt-badge" hidden></span></button>
         <button class="flt-all is-active" data-val="all">Todas</button>
       </div>
       <div class="flt-groups">
         <div class="flt-group" data-group="area" hidden>
           <div class="flt-chips">
             <button class="flt-chip" data-facet="area" data-val="grafos">Grafos</button>
           </div>
         </div>
       </div>
     </div>

   Markup inline (una dimensión, chips siempre visibles):
     <div class="flt flt-inline" data-items=".note-item">
       <span class="flt-label">Filtrar</span>
       <button class="flt-all is-active" data-val="all">Todas</button>
       <div class="flt-chips">
         <button class="flt-chip c-purple" data-facet="tag" data-val="collatz">Collatz</button>
       </div>
     </div>

   Cada ítem declara sus valores en data-<facet> separados por espacio:
     <article class="note-item" data-tag="collatz fibonacci">…</article>

   Semántica: OR dentro de una faceta, AND entre facetas.

   · Páginas con tarjetas pintadas por JS (async): llama window.fltRefresh()
     después de pintar para que el filtro reescanee los ítems.
   · Tras cada filtrado, cada raíz .flt emite el evento 'flt:change' con
     detail = {shown, total, active}: úsalo para ocultar grupos vacíos,
     actualizar contadores o mostrar un estado "sin resultados".
   · data-count opcional con data-one / data-many / data-filt para el texto.
   ============================================================ */
(function () {
  var applies = [];

  function initRoot(root) {
    var itemsSel = root.getAttribute('data-items') || '.flt-item';
    var allBtn = root.querySelector('.flt-all');
    var countEl = root.getAttribute('data-count')
      ? document.getElementById(root.getAttribute('data-count')) : null;
    var filters = {};

    function updateConcepts() {
      root.querySelectorAll('.flt-concept[data-group]').forEach(function (btn) {
        var g = btn.getAttribute('data-group');
        var n = filters[g] ? filters[g].size : 0;
        btn.classList.toggle('has-filter', n > 0);
        var badge = btn.querySelector('.flt-badge');
        if (badge) { badge.hidden = (n === 0); badge.textContent = n; }
      });
    }

    function apply() {
      var items = Array.prototype.slice.call(document.querySelectorAll(itemsSel));
      var active = Object.keys(filters).filter(function (f) { return filters[f].size > 0; });
      var shown = 0;
      items.forEach(function (it) {
        var ok = active.every(function (f) {
          var vals = (it.getAttribute('data-' + f) || '').split(/\s+/);
          return vals.some(function (v) { return filters[f].has(v); });
        });
        it.classList.toggle('flt-hidden', !ok);
        if (ok) shown++;
      });
      if (allBtn) allBtn.classList.toggle('is-active', active.length === 0);
      if (countEl) {
        var one = countEl.getAttribute('data-one') || '';
        var many = countEl.getAttribute('data-many') || '';
        var filt = countEl.getAttribute('data-filt') || '';
        countEl.textContent = shown + ' ' + (shown === 1 ? one : many) + (active.length ? filt : '');
      }
      updateConcepts();
      root.dispatchEvent(new CustomEvent('flt:change', {
        detail: { shown: shown, total: items.length, active: active.length }
      }));
    }

    function reset() {
      filters = {};
      root.querySelectorAll('.flt-chip.is-active').forEach(function (x) { x.classList.remove('is-active'); });
      root.querySelectorAll('.flt-group').forEach(function (g) { g.setAttribute('hidden', ''); });
      root.querySelectorAll('.flt-concept.open').forEach(function (b) {
        b.classList.remove('open'); b.setAttribute('aria-expanded', 'false');
      });
      apply();
    }

    /* Delegación: soporta chips/conceptos pintados dinámicamente tras el fetch. */
    root.addEventListener('click', function (e) {
      var concept = e.target.closest && e.target.closest('.flt-concept[data-group]');
      if (concept && root.contains(concept)) {
        var g = concept.getAttribute('data-group');
        var grp = root.querySelector('.flt-group[data-group="' + g + '"]');
        if (!grp) return;
        var opening = grp.hasAttribute('hidden');
        if (opening) grp.removeAttribute('hidden'); else grp.setAttribute('hidden', '');
        concept.classList.toggle('open', opening);
        concept.setAttribute('aria-expanded', opening ? 'true' : 'false');
        return;
      }
      var all = e.target.closest && e.target.closest('.flt-all');
      if (all && root.contains(all)) { reset(); return; }
      var chip = e.target.closest && e.target.closest('.flt-chip');
      if (chip && root.contains(chip)) {
        var f = chip.getAttribute('data-facet'), v = chip.getAttribute('data-val');
        if (!filters[f]) filters[f] = new Set();
        if (filters[f].has(v)) { filters[f].delete(v); chip.classList.remove('is-active'); }
        else { filters[f].add(v); chip.classList.add('is-active'); }
        apply();
      }
    });

    applies.push(apply);
    apply();
  }

  function init() { document.querySelectorAll('.flt').forEach(initRoot); }

  window.fltRefresh = function () { applies.forEach(function (fn) { fn(); }); };

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init);
  else init();
})();
