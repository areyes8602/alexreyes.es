/* lang-persist.js
   ─────────────────
   Recuerda el idioma elegido en el lang switcher y, al cargar cualquier
   página, redirige a la versión correspondiente del árbol /es/, /ca/ o /en/.

   Convenciones del sitio:
   - URL raíz "/..." sirve la versión castellana (excepto algunos hubs CCSS/ESO
     que sirven catalán; el script no lo distingue, simplemente redirige según
     preferencia y la URL que exista en el árbol prefijado).
   - "/ca/..." sirve catalán.
   - "/en/..." sirve inglés.

   Si el usuario tiene preferencia "ca" y entra en "/foo/", se redirige a "/ca/foo/".
   Si la versión "/ca/foo/" no existe (404), el usuario lo ve y puede elegir otro
   idioma con el switcher (que no auto-redirige porque el clic guarda nueva pref).
*/
(function(){
  'use strict';
  var KEY = 'pref_lang';
  var SUPPORTED = ['es','ca','en'];

  // 1) Guardar preferencia cuando el usuario clica el lang switcher
  document.addEventListener('click', function(e){
    var t = e.target;
    if (!t || typeof t.closest !== 'function') return;
    var a = t.closest('.lang-sw a');
    if (!a) return;
    var lang = (a.textContent || '').trim().toLowerCase();
    if (SUPPORTED.indexOf(lang) >= 0) {
      try { localStorage.setItem(KEY, lang); } catch(_){}
    }
  });

  // 2) Al cargar, si hay preferencia y no coincide con la URL actual, redirigir
  try {
    var pref = localStorage.getItem(KEY);
    if (!pref || SUPPORTED.indexOf(pref) < 0) return;

    var path = location.pathname;
    var m = path.match(/^\/(ca|en)(\/.*)?$/);
    var currentPrefix = m ? m[1] : 'es';
    if (currentPrefix === pref) return; // ya estamos en el idioma preferido

    var cleanPath = m ? (m[2] || '/') : path;
    var newPath = pref === 'es' ? cleanPath : '/' + pref + cleanPath;
    if (newPath === path) return; // sin cambios

    location.replace(newPath + location.search + location.hash);
  } catch(_){}
})();
