/* lang-persist.js
   ─────────────────
   Persistencia + redirect automático según el idioma preferido del usuario.

   Comportamiento:
   1. Si el usuario aún no tiene preferencia guardada, se inicializa con el
      lang del documento actual (heurística: la página que está viendo).
   2. Cuando el usuario clica un enlace del lang switcher, se guarda la nueva
      preferencia.
   3. Al cargar cualquier página, si la URL no coincide con el idioma preferido,
      se redirige a la versión equivalente del árbol /es/, /ca/ o /en/.

   Convenciones del sitio:
   - URL raíz "/..." → versión castellana en general (con excepciones que se
     ignoran a propósito: el redirect simplemente intenta la otra versión).
   - "/ca/..." → catalán.
   - "/en/..." → inglés.

   Si la versión preferida no existe (404), el usuario ve la 404 y puede usar
   el switcher (que actualiza la preferencia y redirige).
*/
(function(){
  'use strict';
  var KEY = 'pref_lang';
  var SUPPORTED = ['es','ca','en'];

  function getStored(){
    try { return localStorage.getItem(KEY); } catch(_){ return null; }
  }
  function setStored(v){
    try { localStorage.setItem(KEY, v); } catch(_){}
  }
  function getPrefix(path){
    var m = path.match(/^\/(ca|en)(\/.*)?$/);
    return m ? m[1] : 'es';
  }
  function cleanPath(path){
    var m = path.match(/^\/(ca|en)(\/.*)?$/);
    return m ? (m[2] || '/') : path;
  }

  // 1) Inicializar preferencia con el lang del documento si no había
  var stored = getStored();
  if (!stored || SUPPORTED.indexOf(stored) < 0) {
    var docLang = (document.documentElement.lang || '').toLowerCase();
    if (SUPPORTED.indexOf(docLang) >= 0) {
      setStored(docLang);
      stored = docLang;
    }
  }

  // 2) Guardar nueva preferencia cuando se clica el switcher
  document.addEventListener('click', function(e){
    var t = e.target;
    if (!t || typeof t.closest !== 'function') return;
    var a = t.closest('.lang-sw a');
    if (!a) return;
    var lang = (a.textContent || '').trim().toLowerCase();
    if (SUPPORTED.indexOf(lang) >= 0) setStored(lang);
  });

  // 3) Si la preferencia no coincide con la URL actual, redirigir
  if (!stored || SUPPORTED.indexOf(stored) < 0) return;

  var path = location.pathname;
  var current = getPrefix(path);
  if (current === stored) return; // ya estamos donde queremos

  var newPath = stored === 'es' ? cleanPath(path) : '/' + stored + cleanPath(path);
  if (newPath === path) return;

  location.replace(newPath + location.search + location.hash);
})();
