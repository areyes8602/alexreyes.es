/* ============================================================
   /editor/ — Editor visual de colecciones de ejercicios
   Rellenas el formulario, descargas el JSON, lo guardas en
   assets/data/ejercicios/<id>.json y corres build_ejercicios.py.
   ============================================================ */
(function () {
  'use strict';

  let taxonomy = null;
  let state = null;

  // --------------- State model ---------------
  function newState() {
    return {
      schema_version: 2,
      id: '',
      tipo_coleccion: 'examen',
      titulo: '',
      fecha: '',
      grupo: '',
      promocion: '',
      centro: '',
      url_index: '',
      pdf_original: '',
      puntuacion_total: 0,
      baremo: [],
      tags_coleccion: {},
      ejercicios: [],
    };
  }

  function newEjercicio(numero) {
    return {
      id: '',
      numero,
      titulo: '',
      url: '',
      puntuacion: 0,
      apartados: [],
      tags: {},
    };
  }

  function newApartado(idx) {
    return {
      letra: String.fromCharCode(97 + idx),
      puntos: 0,
      tarea: '',
    };
  }

  // --------------- DOM refs ---------------
  const $ = (id) => document.getElementById(id);
  const els = {};

  // --------------- Helpers ---------------
  function esc(s) {
    return String(s ?? '').replace(/[&<>"']/g, (c) => ({
      '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;',
    }[c]));
  }
  function computeEjId(coleccionId, numero) {
    return coleccionId ? `${coleccionId}-p${numero}` : `p${numero}`;
  }
  function sumApartados(ap) {
    return ap.reduce((s, a) => s + (Number(a.puntos) || 0), 0);
  }
  function sumEjercicios(ejs) {
    return ejs.reduce((s, e) => s + (Number(e.puntuacion) || 0), 0);
  }

  // Clean state for export: drop empty fields
  function cleanForExport(st) {
    const out = {
      schema_version: 2,
      id: st.id,
      tipo_coleccion: st.tipo_coleccion,
      titulo: st.titulo,
    };
    if (st.fecha) out.fecha = st.fecha;
    if (st.grupo) out.grupo = st.grupo;
    if (st.promocion) out.promocion = st.promocion;
    if (st.centro) out.centro = st.centro;
    if (st.pdf_original) out.pdf_original = st.pdf_original;
    if (st.url_index) out.url_index = st.url_index;
    out.puntuacion_total = Number(st.puntuacion_total) || 0;
    if (st.baremo && st.baremo.length) {
      out.baremo = st.baremo.map(b => ({
        min: Number(b.min), max: Number(b.max), nota: Number(b.nota)
      }));
    }
    const tc = cleanTags(st.tags_coleccion);
    if (Object.keys(tc).length) out.tags_coleccion = tc;
    out.ejercicios = st.ejercicios.map((e) => {
      const ej = {
        id: e.id || computeEjId(st.id, e.numero),
        numero: Number(e.numero),
        titulo: e.titulo,
      };
      if (e.url) ej.url = e.url;
      ej.puntuacion = Number(e.puntuacion) || 0;
      ej.apartados = e.apartados.map(a => ({
        letra: a.letra,
        puntos: Number(a.puntos) || 0,
        tarea: a.tarea,
      }));
      const et = cleanTags(e.tags);
      if (Object.keys(et).length) ej.tags = et;
      return ej;
    });
    return out;
  }

  function cleanTags(tags) {
    const out = {};
    for (const [ns, v] of Object.entries(tags || {})) {
      if (Array.isArray(v)) {
        if (v.length) out[ns] = v;
      } else if (v !== '' && v !== null && v !== undefined) {
        out[ns] = v;
      }
    }
    return out;
  }

  // --------------- Rendering ---------------
  function render() {
    renderColeccion();
    renderEjercicios();
    renderOutput();
  }

  function renderColeccion() {
    // Simple bind: each input's value → state field
    $('c-id').value = state.id;
    $('c-tipo').value = state.tipo_coleccion;
    $('c-titulo').value = state.titulo;
    $('c-fecha').value = state.fecha;
    $('c-grupo').value = state.grupo;
    $('c-promocion').value = state.promocion;
    $('c-centro').value = state.centro;
    $('c-url-index').value = state.url_index;
    $('c-pdf').value = state.pdf_original;
    $('c-ptotal').value = state.puntuacion_total;
    renderTagsPanel($('c-tags'), state.tags_coleccion, () => {
      render();
    });
    renderBaremo();
  }

  function renderBaremo() {
    const box = $('c-baremo');
    box.innerHTML = '';
    state.baremo.forEach((b, i) => {
      const row = document.createElement('div');
      row.className = 'ed-baremo-row';
      row.innerHTML = `
        <input type="number" value="${esc(b.nota)}" placeholder="nota">
        <input type="number" value="${esc(b.min)}"  placeholder="min">
        <input type="number" value="${esc(b.max)}"  placeholder="max">
        <button class="ed-btn ed-btn-mini ed-btn-danger" data-act="rm-baremo" data-i="${i}">✕</button>
      `;
      const inputs = row.querySelectorAll('input');
      inputs[0].addEventListener('input', (e) => { state.baremo[i].nota = e.target.value; renderOutput(); });
      inputs[1].addEventListener('input', (e) => { state.baremo[i].min  = e.target.value; renderOutput(); });
      inputs[2].addEventListener('input', (e) => { state.baremo[i].max  = e.target.value; renderOutput(); });
      row.querySelector('[data-act="rm-baremo"]').addEventListener('click', () => {
        state.baremo.splice(i, 1); renderBaremo(); renderOutput();
      });
      box.appendChild(row);
    });
  }

  function renderTagsPanel(container, tagsObj, onChange) {
    container.innerHTML = '';
    for (const [ns, def] of Object.entries(taxonomy.namespaces)) {
      const wrap = document.createElement('div');
      wrap.className = 'ed-tags-ns';
      const multi = !!def.multi;
      const cur = tagsObj[ns];
      const selected = multi ? (Array.isArray(cur) ? cur : []) : [cur].filter(Boolean);

      const title = document.createElement('div');
      title.className = 'ed-tags-ns-title';
      title.innerHTML = `${esc(def.label.es)} <small>${multi ? 'multi' : 'único'}</small>`;
      wrap.appendChild(title);

      const opts = document.createElement('div');
      opts.className = 'ed-tag-options';
      for (const [val, vdef] of Object.entries(def.valores)) {
        const lbl = vdef.label.es;
        const isSel = selected.includes(val);
        const chip = document.createElement('label');
        chip.className = 'ed-tag-chip' + (isSel ? ' selected' : '');
        chip.innerHTML = `<input type="${multi ? 'checkbox' : 'radio'}" ${isSel ? 'checked' : ''}> <span>${esc(lbl)}</span>`;
        const input = chip.querySelector('input');
        input.addEventListener('change', () => {
          if (multi) {
            const arr = Array.isArray(tagsObj[ns]) ? tagsObj[ns] : [];
            if (input.checked) { if (!arr.includes(val)) arr.push(val); }
            else { const idx = arr.indexOf(val); if (idx >= 0) arr.splice(idx, 1); }
            tagsObj[ns] = arr;
          } else {
            if (tagsObj[ns] === val) { delete tagsObj[ns]; }
            else { tagsObj[ns] = val; }
          }
          onChange();
        });
        opts.appendChild(chip);
      }
      wrap.appendChild(opts);
      container.appendChild(wrap);
    }
  }

  function renderEjercicios() {
    const box = $('ejercicios-list');
    box.innerHTML = '';
    state.ejercicios.forEach((ej, i) => {
      const div = document.createElement('div');
      div.className = 'ed-ejercicio';
      const computedId = computeEjId(state.id, ej.numero);
      const apSum = sumApartados(ej.apartados);
      const puntuacion = Number(ej.puntuacion) || 0;
      const sumOk = ej.apartados.length === 0 || apSum === puntuacion;
      div.innerHTML = `
        <div class="ed-ejercicio-head">
          <div>
            <span class="ej-num">#${ej.numero}</span>
            <strong style="margin-left:0.5rem">${esc(ej.titulo) || 'Ejercicio sin título'}</strong>
            <div class="ej-id">id: ${esc(computedId)}</div>
          </div>
          <button class="ed-btn ed-btn-danger ed-btn-mini" data-act="rm-ej" data-i="${i}">Eliminar ejercicio</button>
        </div>
        <div class="ed-field-row-3">
          <div class="ed-field"><label>Número</label><input type="number" data-ef="numero" value="${esc(ej.numero)}" min="1"></div>
          <div class="ed-field"><label>Puntuación</label><input type="number" data-ef="puntuacion" value="${esc(puntuacion)}" min="0" step="0.5"></div>
          <div class="ed-field"><label>URL enunciado</label><input type="text" data-ef="url" value="${esc(ej.url || '')}" placeholder="/aula/…/p1.html"></div>
        </div>
        <div class="ed-field">
          <label>Título</label>
          <input type="text" data-ef="titulo" value="${esc(ej.titulo)}" placeholder="P.ej. Movimiento de proyectil en 2D">
        </div>

        <div style="margin-top:1rem">
          <div class="ed-field-inline-label" style="display:flex;justify-content:space-between;align-items:center;margin-bottom:0.4rem">
            <span>APARTADOS</span>
            <span class="ed-sum-note ${ej.apartados.length === 0 ? '' : (sumOk ? 'ok' : 'err')}">
              ${ej.apartados.length === 0 ? 'sin apartados' : `suma = ${apSum} / ${puntuacion}`}
            </span>
          </div>
          <div class="ed-apartados-list"></div>
          <div class="ed-add-row">
            <button class="ed-btn" data-act="add-ap" data-i="${i}">+ Añadir apartado</button>
            <button class="ed-btn ed-btn-mini" data-act="auto-p" data-i="${i}" title="Auto-rellenar puntuación como suma de apartados">= auto</button>
          </div>
        </div>

        <fieldset class="ed-tags-block" style="margin-top:1rem">
          <legend>Tags del ejercicio</legend>
          <div class="ed-ej-tags"></div>
        </fieldset>
      `;

      // Ejercicio field handlers
      div.querySelectorAll('[data-ef]').forEach((inp) => {
        inp.addEventListener('input', (e) => {
          ej[e.target.dataset.ef] = inp.type === 'number' ? Number(e.target.value) : e.target.value;
          renderEjercicios();  // re-render to update computed ID + sums
          renderOutput();
        });
      });

      div.querySelector('[data-act="rm-ej"]').addEventListener('click', () => {
        if (!confirm('¿Eliminar este ejercicio?')) return;
        state.ejercicios.splice(i, 1);
        renumberEjercicios();
        renderEjercicios();
        renderOutput();
      });

      div.querySelector('[data-act="add-ap"]').addEventListener('click', () => {
        ej.apartados.push(newApartado(ej.apartados.length));
        renderEjercicios();
        renderOutput();
      });

      div.querySelector('[data-act="auto-p"]').addEventListener('click', () => {
        ej.puntuacion = sumApartados(ej.apartados);
        renderEjercicios();
        renderOutput();
      });

      // Render apartados
      const apBox = div.querySelector('.ed-apartados-list');
      ej.apartados.forEach((ap, j) => {
        const row = document.createElement('div');
        row.className = 'ed-apartado';
        row.innerHTML = `
          <input class="ap-letra" value="${esc(ap.letra)}" placeholder="a">
          <input class="ap-puntos" type="number" value="${esc(ap.puntos)}" placeholder="pts" step="0.5" min="0">
          <input class="ap-tarea" value="${esc(ap.tarea)}" placeholder="Descripción breve del apartado">
          <button class="ed-btn ed-btn-mini ed-btn-danger">✕</button>
        `;
        const inputs = row.querySelectorAll('input');
        inputs[0].addEventListener('input', (e) => { ap.letra = e.target.value; renderOutput(); });
        inputs[1].addEventListener('input', (e) => { ap.puntos = Number(e.target.value) || 0; renderEjercicios(); renderOutput(); });
        inputs[2].addEventListener('input', (e) => { ap.tarea = e.target.value; renderOutput(); });
        row.querySelector('button').addEventListener('click', () => {
          ej.apartados.splice(j, 1);
          renderEjercicios();
          renderOutput();
        });
        apBox.appendChild(row);
      });

      // Render ejercicio tags
      renderTagsPanel(div.querySelector('.ed-ej-tags'), ej.tags, () => {
        renderOutput();
      });

      box.appendChild(div);
    });
  }

  function renumberEjercicios() {
    state.ejercicios.forEach((e, i) => { e.numero = i + 1; });
  }

  function renderOutput() {
    const exp = cleanForExport(state);
    $('output-json').textContent = JSON.stringify(exp, null, 2);
    renderValidation(exp);
  }

  function renderValidation(exp) {
    const msgs = [];
    // IDs
    if (!exp.id) msgs.push({ k: 'err', m: 'La colección no tiene id' });
    if (!/^[a-z0-9\-]+$/i.test(exp.id || '')) msgs.push({ k: 'warn', m: 'El id de colección debe ser sólo letras/números/guiones' });
    if (!exp.titulo) msgs.push({ k: 'err', m: 'Falta título de la colección' });
    // Unique ejercicio IDs
    const ids = new Map();
    for (const ej of exp.ejercicios || []) {
      if (ids.has(ej.id)) msgs.push({ k: 'err', m: `ID ejercicio duplicado: ${ej.id}` });
      else ids.set(ej.id, true);
    }
    // Sum apartados == puntuacion
    for (const ej of exp.ejercicios || []) {
      const s = (ej.apartados || []).reduce((a, b) => a + (b.puntos || 0), 0);
      if (ej.apartados?.length && s !== (ej.puntuacion || 0)) {
        msgs.push({ k: 'err', m: `#${ej.numero} "${ej.titulo || ej.id}": apartados=${s} ≠ puntuación=${ej.puntuacion}` });
      }
    }
    // Sum ejercicios == puntuacion_total
    const totalEj = sumEjercicios(exp.ejercicios || []);
    if (exp.puntuacion_total && totalEj !== exp.puntuacion_total) {
      msgs.push({ k: 'err', m: `Suma ejercicios=${totalEj} ≠ puntuación_total=${exp.puntuacion_total}` });
    }
    // Tags against taxonomy
    for (const [ns, v] of Object.entries(exp.tags_coleccion || {})) {
      if (!taxonomy.namespaces[ns]) { msgs.push({ k: 'err', m: `Tag de colección: namespace '${ns}' no existe` }); continue; }
      const vs = Array.isArray(v) ? v : [v];
      for (const val of vs) {
        if (!taxonomy.namespaces[ns].valores[val]) msgs.push({ k: 'err', m: `Tag de colección: '${val}' no existe en '${ns}'` });
      }
    }
    for (const ej of exp.ejercicios || []) {
      for (const [ns, v] of Object.entries(ej.tags || {})) {
        if (!taxonomy.namespaces[ns]) { msgs.push({ k: 'err', m: `#${ej.numero}: namespace '${ns}' no existe` }); continue; }
        const vs = Array.isArray(v) ? v : [v];
        for (const val of vs) {
          if (!taxonomy.namespaces[ns].valores[val]) msgs.push({ k: 'err', m: `#${ej.numero}: '${val}' no existe en '${ns}'` });
        }
      }
    }

    const box = $('validation');
    if (!msgs.length) {
      box.innerHTML = '<h3>Validación</h3><ul><li class="ok">✓ Todo correcto — puedes descargar el JSON</li></ul>';
    } else {
      const errs = msgs.filter(m => m.k === 'err').length;
      box.innerHTML = `<h3>Validación (${errs} error${errs === 1 ? '' : 'es'})</h3><ul>` +
        msgs.map(m => `<li class="${m.k}">${m.k === 'err' ? '✗' : '⚠'} ${esc(m.m)}</li>`).join('') +
        '</ul>';
    }
  }

  // --------------- Actions ---------------
  function addEjercicio() {
    const n = state.ejercicios.length + 1;
    state.ejercicios.push(newEjercicio(n));
    renderEjercicios();
    renderOutput();
  }

  function downloadJSON() {
    const exp = cleanForExport(state);
    if (!exp.id) { alert('Pon un id de colección antes de descargar'); return; }
    const blob = new Blob([JSON.stringify(exp, null, 2)], { type: 'application/json' });
    const a = document.createElement('a');
    a.href = URL.createObjectURL(blob);
    a.download = `${exp.id}.json`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
  }

  function copyJSON() {
    const txt = $('output-json').textContent;
    navigator.clipboard.writeText(txt).then(
      () => { const b = $('btn-copy'); const o = b.textContent; b.textContent = '✓ Copiado'; setTimeout(() => b.textContent = o, 1500); },
      () => alert('No se pudo copiar al portapapeles')
    );
  }

  function importJSON() {
    const txt = $('import-area').value.trim();
    if (!txt) return;
    try {
      const parsed = JSON.parse(txt);
      state = { ...newState(), ...parsed };
      // ensure nested structures exist
      state.tags_coleccion = state.tags_coleccion || {};
      state.baremo = state.baremo || [];
      state.ejercicios = (state.ejercicios || []).map((e, i) => ({
        ...newEjercicio(i + 1),
        ...e,
        apartados: e.apartados || [],
        tags: e.tags || {},
      }));
      render();
      $('import-details').open = false;
    } catch (err) {
      alert('JSON inválido: ' + err.message);
    }
  }

  function resetAll() {
    if (!confirm('¿Borrar todo y empezar de cero?')) return;
    state = newState();
    render();
  }

  // --------------- Init ---------------
  async function init() {
    try {
      const res = await fetch('/assets/data/tags.json');
      taxonomy = await res.json();
    } catch (e) {
      document.body.innerHTML = '<div style="padding:2rem;color:red">Error al cargar tags.json: ' + e.message + '</div>';
      return;
    }

    state = newState();

    // Bind collection fields
    const bindSimple = (id, field, type) => {
      $(id).addEventListener('input', (e) => {
        state[field] = type === 'number' ? Number(e.target.value) : e.target.value;
        if (field === 'id') renderEjercicios();  // update computed ej IDs
        renderOutput();
      });
    };
    bindSimple('c-id', 'id', 'text');
    bindSimple('c-tipo', 'tipo_coleccion', 'text');
    bindSimple('c-titulo', 'titulo', 'text');
    bindSimple('c-fecha', 'fecha', 'text');
    bindSimple('c-grupo', 'grupo', 'text');
    bindSimple('c-promocion', 'promocion', 'text');
    bindSimple('c-centro', 'centro', 'text');
    bindSimple('c-url-index', 'url_index', 'text');
    bindSimple('c-pdf', 'pdf_original', 'text');
    bindSimple('c-ptotal', 'puntuacion_total', 'number');

    $('btn-add-ej').addEventListener('click', addEjercicio);
    $('btn-add-baremo').addEventListener('click', () => {
      state.baremo.push({ min: 0, max: 0, nota: 0 });
      renderBaremo();
      renderOutput();
    });
    $('btn-download').addEventListener('click', downloadJSON);
    $('btn-copy').addEventListener('click', copyJSON);
    $('btn-reset').addEventListener('click', resetAll);
    $('btn-import').addEventListener('click', importJSON);
    $('btn-auto-total').addEventListener('click', () => {
      state.puntuacion_total = sumEjercicios(state.ejercicios);
      $('c-ptotal').value = state.puntuacion_total;
      renderOutput();
    });

    render();
  }

  document.addEventListener('DOMContentLoaded', init);
})();
