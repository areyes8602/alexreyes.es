/* lang-persist.js
   ─────────────────
   Persistencia + redirect automático según el idioma preferido del usuario.

   Comportamiento:
   1. Si el usuario aún no tiene preferencia guardada, se inicializa con el
      lang del documento actual (heurística: la página que está viendo).
   2. Cuando el usuario clica un enlace del lang switcher, se guarda la nueva
      preferencia.
   3. Al cargar cualquier página, si el lang del documento NO coincide con la
      preferencia, se intenta redirigir a la versión equivalente.

   Importante: el redirect se basa en COMPARAR `<html lang>` con la preferencia,
   no en adivinar por el path. Esto permite que algunas páginas raíz (/aula/...)
   tengan contenido catalán (lang="ca") y NO sean redirigidas si pref=ca.

   Si la versión preferida no existe (404), el usuario ve la 404 y puede usar
   el switcher (que actualiza la preferencia).
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
  var docLang = (document.documentElement.lang || '').toLowerCase();
  var stored = getStored();
  if (!stored || SUPPORTED.indexOf(stored) < 0) {
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

  // 3) Si el lang del documento ya coincide con la pref, no redirigir.
  //    Esto cubre el caso de páginas /aula/... raíz que tienen contenido
  //    catalán (lang="ca") y donde pref=ca: el usuario ya ve lo que quiere.
  if (!stored || SUPPORTED.indexOf(stored) < 0) return;
  if (docLang === stored) return;

  // 4) El lang del documento NO coincide con pref → intentar redirigir
  //    a la versión equivalente del árbol prefijado.
  var path = location.pathname;
  var current = getPrefix(path);
  if (current === stored) return; // path ya tiene el prefijo correcto (raro)

  var newPath = stored === 'es' ? cleanPath(path) : '/' + stored + cleanPath(path);
  if (newPath === path) return;

  location.replace(newPath + location.search + location.hash);
})();
