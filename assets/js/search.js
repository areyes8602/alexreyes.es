/* Buscador global de alexreyes.es — overlay tipo ⌘K sobre ejercicios-index.json.
   Autónomo: crea su propio botón flotante y overlay; no necesita tocar el <nav>.
   Multilingüe: detecta el idioma desde <html lang> y enlaza a la versión correcta. */
(function () {
  "use strict";
  var LANG = (document.documentElement.getAttribute("lang") || "es").slice(0, 2);
  var PREFIX = LANG === "ca" ? "/ca" : LANG === "en" ? "/en" : "";
  var T = {
    es: { ph: "Buscar ejercicios, exámenes, temas…", hint: "para buscar", empty: "Sin resultados", min: "Escribe para buscar entre todos los ejercicios y exámenes", aria: "Buscar en la web" },
    ca: { ph: "Cerca exercicis, exàmens, temes…", hint: "per cercar", empty: "Sense resultats", min: "Escriu per cercar entre tots els exercicis i exàmens", aria: "Cerca al web" },
    en: { ph: "Search exercises, exams, topics…", hint: "to search", empty: "No results", min: "Type to search across all exercises and exams", aria: "Search the site" }
  }[LANG] || null;
  var L = T || { ph: "Buscar…", hint: "para buscar", empty: "Sin resultados", min: "Escribe para buscar", aria: "Buscar" };

  function norm(s) {
    return (s || "").toString().toLowerCase().normalize("NFD").replace(/[̀-ͯ]/g, "");
  }

  // ---- estilos ----
  var css = document.createElement("style");
  css.textContent = [
    ".gs-fab{position:fixed;right:1rem;bottom:1rem;z-index:9998;display:flex;align-items:center;gap:.4rem;padding:.55rem .8rem;border-radius:999px;border:1px solid var(--border,#ddd);background:var(--bg-subtle,#f5f5f5);color:var(--text-soft,#555);font:inherit;font-size:.82rem;cursor:pointer;box-shadow:0 2px 10px rgba(0,0,0,.08)}",
    ".gs-fab:hover{border-color:var(--accent,#3b82f6);color:var(--text,#111)}",
    ".gs-fab kbd{font-family:var(--mono,monospace);font-size:.72rem;border:1px solid var(--border,#ccc);border-radius:4px;padding:0 .3rem;background:var(--bg,#fff)}",
    "@media(max-width:560px){.gs-fab span.gs-lbl{display:none}}",
    ".gs-ov{position:fixed;inset:0;z-index:9999;background:rgba(0,0,0,.45);display:none;align-items:flex-start;justify-content:center;padding:10vh 1rem 1rem}",
    ".gs-ov.open{display:flex}",
    ".gs-box{width:100%;max-width:620px;background:var(--bg,#fff);border:1px solid var(--border,#ddd);border-radius:14px;box-shadow:0 20px 60px rgba(0,0,0,.3);overflow:hidden;display:flex;flex-direction:column;max-height:75vh}",
    ".gs-in{border:none;outline:none;padding:1rem 1.1rem;font:inherit;font-size:1rem;background:transparent;color:var(--text,#111);border-bottom:1px solid var(--border,#eee)}",
    ".gs-res{overflow-y:auto;padding:.4rem}",
    ".gs-it{display:block;padding:.6rem .8rem;border-radius:8px;text-decoration:none;color:inherit;cursor:pointer}",
    ".gs-it.sel,.gs-it:hover{background:var(--bg-subtle,#f1f1f1)}",
    ".gs-it b{font-size:.93rem;color:var(--text,#111);font-weight:600;display:block}",
    ".gs-it small{font-size:.78rem;color:var(--text-faint,#888)}",
    ".gs-empty{padding:1.2rem;text-align:center;color:var(--text-faint,#888);font-size:.9rem}"
  ].join("");
  document.head.appendChild(css);

  // ---- DOM ----
  var fab = document.createElement("button");
  fab.className = "gs-fab"; fab.type = "button"; fab.setAttribute("aria-label", L.aria);
  fab.innerHTML = '<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><circle cx="11" cy="11" r="7"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg><span class="gs-lbl"><kbd>⌘K</kbd></span>';

  var ov = document.createElement("div"); ov.className = "gs-ov"; ov.setAttribute("role", "dialog"); ov.setAttribute("aria-modal", "true");
  ov.innerHTML = '<div class="gs-box"><input class="gs-in" type="text" placeholder="' + L.ph + '" aria-label="' + L.aria + '"><div class="gs-res"></div></div>';
  document.addEventListener("DOMContentLoaded", function () {
    document.body.appendChild(fab); document.body.appendChild(ov);
  });

  var input = ov.querySelector(".gs-in"), res = ov.querySelector(".gs-res");
  var DATA = null, items = [], sel = 0, loaded = false;

  function load() {
    if (loaded) return Promise.resolve();
    loaded = true;
    return fetch("/assets/data/ejercicios-index.json", { cache: "force-cache" })
      .then(function (r) { return r.json(); })
      .then(function (d) {
        DATA = (d.ejercicios || []).map(function (ej) {
          var col = ej.coleccion || {}, t = ej.tags || {};
          var concepts = [].concat(t.concepto_bach || [], t.concepto_eso || [], t.concepto_nm || []);
          return {
            titulo: ej.titulo || "",
            col: col.titulo || "",
            url: ej.url_enunciado || col.url_index || "#",
            hay: norm([ej.titulo, col.titulo, concepts.join(" "), t.materia].join(" "))
          };
        });
      })
      .catch(function () { DATA = []; });
  }

  function open() {
    ov.classList.add("open"); load().then(function () { render(input.value); });
    setTimeout(function () { input.focus(); }, 30);
  }
  function close() { ov.classList.remove("open"); }

  function render(q) {
    var nq = norm(q);
    if (!nq) { res.innerHTML = '<div class="gs-empty">' + L.min + "</div>"; items = []; return; }
    var out = (DATA || []).filter(function (x) { return x.hay.indexOf(nq) !== -1; }).slice(0, 40);
    items = out; sel = 0;
    if (!out.length) { res.innerHTML = '<div class="gs-empty">' + L.empty + "</div>"; return; }
    res.innerHTML = out.map(function (x, i) {
      var href = (x.url.charAt(0) === "/" ? PREFIX : "") + x.url;
      return '<a class="gs-it' + (i === 0 ? " sel" : "") + '" href="' + href + '"><b>' +
        esc(x.titulo) + "</b><small>" + esc(x.col) + "</small></a>";
    }).join("");
  }
  function esc(s) { return String(s).replace(/[&<>"]/g, function (c) { return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]; }); }

  function move(d) {
    var nodes = res.querySelectorAll(".gs-it"); if (!nodes.length) return;
    nodes[sel] && nodes[sel].classList.remove("sel");
    sel = (sel + d + nodes.length) % nodes.length;
    nodes[sel].classList.add("sel"); nodes[sel].scrollIntoView({ block: "nearest" });
  }

  fab.addEventListener("click", open);
  ov.addEventListener("click", function (e) { if (e.target === ov) close(); });
  input.addEventListener("input", function () { render(input.value); });
  document.addEventListener("keydown", function (e) {
    if ((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === "k") { e.preventDefault(); ov.classList.contains("open") ? close() : open(); return; }
    if (!ov.classList.contains("open")) return;
    if (e.key === "Escape") close();
    else if (e.key === "ArrowDown") { e.preventDefault(); move(1); }
    else if (e.key === "ArrowUp") { e.preventDefault(); move(-1); }
    else if (e.key === "Enter") { var n = res.querySelectorAll(".gs-it")[sel]; if (n) location.href = n.getAttribute("href"); }
  });
})();
