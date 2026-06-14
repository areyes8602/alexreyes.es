/* curso-banner.js — Aviso "curso en construcción" para los hubs de Docencia.
   Se inyecta solo y DESAPARECE automáticamente a partir del 2026-09-08
   (inicio del curso 2026–2027 en Catalunya). No requiere limpieza manual:
   pasada esa fecha no pinta nada. */
(function () {
  "use strict";

  // Oculto a partir del 8 de septiembre de 2026 (00:00, hora local).
  var EXPIRA = new Date(2026, 8, 8, 0, 0, 0); // mes 8 = septiembre
  if (new Date() >= EXPIRA) return;

  var lang = (document.documentElement.lang || "es").slice(0, 2).toLowerCase();
  var TXT = {
    es: {
      t: "Curso 2025–2026 finalizado · Curso 2026–2027 en construcción",
      d: "El contenido de las asignaturas se está actualizando y puede no ser correcto todavía."
    },
    ca: {
      t: "Curs 2025–2026 finalitzat · Curs 2026–2027 en construcció",
      d: "El contingut de les assignatures s'està actualitzant i pot no ser correcte encara."
    },
    en: {
      t: "2025–2026 course finished · 2026–2027 course under construction",
      d: "Subject content is being updated and may not be accurate yet."
    }
  };
  var x = TXT[lang] || TXT.es;

  function build() {
    var main = document.querySelector("main");
    if (!main || main.querySelector(".curso-banner")) return;

    var wrap = document.createElement("div");
    wrap.className = "curso-banner-wrap";
    wrap.setAttribute("style",
      "max-width:var(--container,1100px);margin:1.25rem auto 0;padding:0 1.25rem;");

    var box = document.createElement("aside");
    box.className = "curso-banner";
    box.setAttribute("role", "status");
    box.setAttribute("style",
      "display:flex;gap:.75rem;align-items:flex-start;" +
      "padding:.85rem 1rem;border:1px solid var(--border,#e8e8e8);" +
      "border-left:3px solid #f59e0b;border-radius:var(--radius-sm,6px);" +
      "background:var(--bg-subtle,#f9f9f9);");

    box.innerHTML =
      '<span aria-hidden="true" style="font-size:1.1rem;line-height:1.35">🚧</span>' +
      '<span style="font-size:.92rem;line-height:1.45">' +
        '<strong style="display:block;color:var(--text,#0a0a0a);font-weight:600">' +
          esc(x.t) + "</strong>" +
        '<span style="color:var(--text-soft,#525252)">' + esc(x.d) + "</span>" +
      "</span>";

    wrap.appendChild(box);
    main.insertBefore(wrap, main.firstChild);
  }

  function esc(s) {
    return s.replace(/[&<>]/g, function (c) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;" }[c];
    });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", build);
  } else {
    build();
  }
})();
