/* ───────────────────────────────────────────────────────────────────
   Subject access gate — JS half.
   Pair with /assets/css/gate.css and the inline head check.

   Setup in each subject hub:
     <html lang="..." data-gate-id="2eso" data-gate-name="Matemàtiques 2n ESO" data-gate-pw-sha="HEX">
       <head>
         <script>
         (function(){
           var id=document.documentElement.dataset.gateId;
           if(!id)return;
           try{
             var r=localStorage.getItem('slc-gate-'+id);
             if(r){var t=JSON.parse(r);if(t.exp&&t.exp>Date.now())document.documentElement.classList.add('gate-unlocked');}
           }catch(e){}
         })();
         </script>
         <link rel="stylesheet" href="/assets/css/gate.css">
       </head>
       <body>
         ... gate overlay HTML (see template) ...
         <script src="/assets/js/gate.js" defer></script>
       </body>

   Password is stored as SHA-256 hex in `data-gate-pw-sha`.
   To compute a new hash from a password, run in browser console:
     crypto.subtle.digest('SHA-256', new TextEncoder().encode('mypw'))
       .then(b => [...new Uint8Array(b)].map(x => x.toString(16).padStart(2,'0')).join(''))
       .then(console.log)
   ─────────────────────────────────────────────────────────────────── */

(function () {
  const html = document.documentElement;
  const id = html.dataset.gateId;
  if (!id) return;
  if (html.classList.contains('gate-unlocked')) {
    initLockBadge();
    return;
  }

  const TTL_MS = 30 * 24 * 60 * 60 * 1000; // 30 days
  const STORAGE_KEY = 'slc-gate-' + id;
  const targetHash = (html.dataset.gatePwSha || '').toLowerCase().trim();

  async function sha256(s) {
    const buf = await crypto.subtle.digest('SHA-256', new TextEncoder().encode(s));
    return Array.from(new Uint8Array(buf)).map(b => b.toString(16).padStart(2, '0')).join('');
  }

  function unlock() {
    localStorage.setItem(STORAGE_KEY, JSON.stringify({ exp: Date.now() + TTL_MS }));
    html.classList.add('gate-unlocked');
    const overlay = document.getElementById('gate-overlay');
    if (overlay) overlay.remove();
    initLockBadge();
  }

  function initLockBadge() {
    // Add a small "Tancar sessió" pill so user can re-lock the page
    const slot = document.querySelector('[data-gate-exit-slot]');
    if (!slot || slot.dataset.gateInit) return;
    slot.dataset.gateInit = '1';
    const btn = document.createElement('button');
    btn.className = 'gate-exit';
    btn.type = 'button';
    btn.title = 'Tancar sessió d\'aquesta assignatura';
    btn.innerHTML = '🔓 Tancar sessió';
    btn.addEventListener('click', () => {
      localStorage.removeItem(STORAGE_KEY);
      html.classList.remove('gate-unlocked');
      location.reload();
    });
    slot.appendChild(btn);
  }

  // Wire up form
  const form = document.getElementById('gate-form');
  const pwInput = document.getElementById('gate-pw');
  const errBox = document.getElementById('gate-err');
  const submitBtn = form ? form.querySelector('button[type="submit"]') : null;
  if (!form || !pwInput) return;

  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    if (!targetHash) {
      errBox.textContent = "Aquesta assignatura encara no té contrasenya configurada.";
      return;
    }
    const pw = pwInput.value.trim();
    if (!pw) return;
    submitBtn.disabled = true;
    errBox.textContent = '';
    try {
      const got = await sha256(pw);
      if (got === targetHash) {
        unlock();
      } else {
        errBox.textContent = "Contrasenya incorrecta. Torna a provar-ho.";
        pwInput.select();
      }
    } catch (err) {
      errBox.textContent = "Error en validar la contrasenya.";
      console.error(err);
    } finally {
      submitBtn.disabled = false;
    }
  });

  // Auto-focus password field
  setTimeout(() => pwInput.focus(), 50);
})();
