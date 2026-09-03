#!/usr/bin/env python3
"""La pàgina de la prova de normes (pública, en català).

Separada de build_normes_prova.py per no barrejar el banc de preguntes amb
el bastiment HTML. No s'executa sola: la crida el generador del banc.

La pàgina no conté cap resposta correcta. Carrega els enunciats de
/assets/data/normes-preguntes.json, envia les respostes a /api/normes i
ensenya el que li torna el servidor.
"""
import re
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent


def asset_version():
    ref = REPO / "docencia" / "index.html"
    if ref.exists():
        m = re.search(r"/style\.css\?v=(\d+)", ref.read_text(encoding="utf-8"))
        if m:
            return "?v=" + m.group(1)
    return ""


def render_prova(versio, total):
    v = asset_version()
    url = "/docencia/tutoria-2eso/normes/"
    return f"""<!DOCTYPE html>
<html lang="ca">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Prova de normes de convivència — 2n ESO</title>
<meta name="description" content="Prova de les normes de convivència i funcionament de l'ESO, curs 2026–2027. Maristes Sants-Les Corts.">
<meta name="robots" content="noindex, nofollow">
<script>(function(){{var s=localStorage.getItem('theme');if(s)document.documentElement.setAttribute('data-theme',s);else document.documentElement.setAttribute('data-theme','light');}})();</script>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap" media="print" onload="this.media='all'"><noscript><link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap"></noscript>
<link rel="stylesheet" href="/style.css{v}">
<link rel="icon" type="image/svg+xml" href="/favicon.svg">
<link rel="canonical" href="https://alexreyes.es{url}">
<style>
  .wrap {{ max-width:44rem; margin:0 auto; }}
  .pas {{ display:none; }} .pas.on {{ display:block; }}
  .camp {{ margin:0 0 1.1rem; }}
  .camp label {{ display:block; font-size:0.82rem; font-weight:600; color:var(--text-soft); margin:0 0 0.35rem; }}
  .camp input, .camp select {{ width:100%; padding:0.7rem 0.85rem; font:inherit; font-size:1rem; color:var(--text); background:var(--bg); border:1px solid var(--border-strong); border-radius:var(--radius-sm); }}
  .camp input:focus, .camp select:focus {{ outline:none; border-color:var(--focus); box-shadow:0 0 0 3px color-mix(in srgb, var(--focus) 18%, transparent); }}
  .camp .ajuda {{ font-size:0.78rem; color:var(--text-faint); margin:0.3rem 0 0; }}
  .codi input {{ font-family:var(--mono); font-size:1.5rem; letter-spacing:0.28em; text-align:center; text-transform:uppercase; }}
  .avis {{ padding:0.8rem 1rem; border-radius:var(--radius-sm); font-size:0.9rem; margin:0 0 1.1rem; border:1px solid; }}
  .avis-err {{ color:#b91c1c; background:#fef2f2; border-color:#fecaca; }}
  [data-theme="dark"] .avis-err {{ color:#fca5a5; background:#2a1414; border-color:#5c2626; }}
  .barra {{ position:sticky; top:0; z-index:20; background:var(--bg); border-bottom:1px solid var(--border); padding:0.7rem 0; margin:0 0 1.6rem; display:flex; align-items:center; gap:0.9rem; }}
  .barra-txt {{ font-size:0.85rem; color:var(--text-soft); white-space:nowrap; }}
  .barra-pista {{ flex:1; height:6px; border-radius:3px; background:var(--bg-hover); overflow:hidden; }}
  .barra-fill {{ height:100%; width:0; background:var(--focus); border-radius:3px; transition:width 0.2s; }}
  .preg {{ border:1px solid var(--border); border-radius:var(--radius); padding:1.2rem 1.35rem; margin:0 0 1.1rem; background:var(--bg); }}
  .preg-cap {{ display:flex; align-items:center; gap:0.5rem; margin:0 0 0.7rem; flex-wrap:wrap; }}
  .preg-num {{ font-family:var(--mono); font-size:0.78rem; color:var(--text-faint); }}
  .xip {{ font-size:0.68rem; text-transform:uppercase; letter-spacing:0.05em; font-weight:600; padding:0.15rem 0.45rem; border-radius:4px; background:var(--bg-hover); color:var(--text-soft); }}
  .preg-ctx {{ font-size:0.95rem; color:var(--text-soft); margin:0 0 0.7rem; padding:0 0 0 0.85rem; border-left:3px solid var(--border-strong); }}
  .preg-q {{ font-size:1rem; font-weight:600; margin:0 0 0.9rem; }}
  .opcio {{ display:flex; gap:0.65rem; align-items:flex-start; padding:0.6rem 0.75rem; border:1px solid var(--border); border-radius:var(--radius-sm); margin:0 0 0.45rem; cursor:pointer; font-size:0.93rem; }}
  .opcio:hover {{ border-color:var(--border-strong); background:var(--bg-subtle); }}
  .opcio input {{ margin:0.2rem 0 0; accent-color:var(--focus); flex:none; }}
  .opcio:has(input:checked) {{ border-color:var(--focus); background:color-mix(in srgb, var(--focus) 7%, transparent); }}
  .preg.falta {{ border-color:#f59e0b; }}
  .nota-gran {{ font-family:var(--mono); font-size:3.4rem; font-weight:600; line-height:1; }}
  .res-cap {{ text-align:center; padding:2rem 1rem; background:var(--bg-subtle); border:1px solid var(--border); border-radius:var(--radius); margin:0 0 1.6rem; }}
  .res-sub {{ font-size:0.92rem; color:var(--text-soft); margin:0.6rem 0 0; }}
  .rev {{ border:1px solid var(--border); border-left-width:4px; border-radius:var(--radius-sm); padding:0.9rem 1.1rem; margin:0 0 0.7rem; }}
  .rev-be {{ border-left-color:#059669; }}
  .rev-mal {{ border-left-color:#dc2626; }}
  .rev-q {{ font-size:0.93rem; font-weight:600; margin:0 0 0.45rem; }}
  .rev-l {{ font-size:0.86rem; margin:0.2rem 0; }}
  .rev-l b {{ font-weight:600; }}
  .rev-norma {{ font-size:0.83rem; color:var(--text-soft); font-style:italic; margin:0.55rem 0 0; padding:0.5rem 0.7rem; background:var(--bg-subtle); border-radius:4px; }}
  .peu-acc {{ display:flex; gap:0.7rem; flex-wrap:wrap; margin:1.6rem 0 0; }}
</style>
</head>
<body>
<a class="skip-link" href="#main">Salta al contingut</a>
<nav>
  <div class="nav-inner">
    <a href="/" class="nav-brand">alexreyes.es</a>
    <div class="nav-links"><a href="/docencia/" class="nav-active">Docència</a></div>
    <div class="nav-right">
      <button class="theme-btn" onclick="toggleTheme()" aria-label="Tema">
        <svg class="icon-sun" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="5"/><line x1="12" y1="1" x2="12" y2="3"/><line x1="12" y1="21" x2="12" y2="23"/><line x1="4.22" y1="4.22" x2="5.64" y2="5.64"/><line x1="18.36" y1="18.36" x2="19.78" y2="19.78"/><line x1="1" y1="12" x2="3" y2="12"/><line x1="21" y1="12" x2="23" y2="12"/><line x1="4.22" y1="19.78" x2="5.64" y2="18.36"/><line x1="18.36" y1="5.64" x2="19.78" y2="4.22"/></svg>
        <svg class="icon-moon" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/></svg>
      </button>
    </div>
  </div>
</nav>

<main id="main">
  <div class="container wrap" style="padding-top:2.5rem;padding-bottom:5rem">

    <!-- 1 · Entrada -->
    <section class="pas on" id="pas-entrada">
      <div class="page-header">
        <span class="section-label">Tutoria · 2n ESO</span>
        <h1 style="margin:0.4rem 0 0.6rem">Normes de convivència</h1>
        <p style="font-size:0.98rem;color:var(--text-soft)">
          Prova sobre les normes de convivència i funcionament a l'ESO del curs
          2026&ndash;2027. Hi ha {total} preguntes: unes de resposta directa i
          unes altres amb una situació on has de decidir si s'ha incomplert
          alguna norma o si la mesura del professorat s'hi ajusta.
        </p>
      </div>
      <div id="entrada-err"></div>
      <form id="form-entrada" autocomplete="off">
        <div class="camp codi">
          <label for="codi">Codi de la prova</label>
          <input id="codi" name="codi" maxlength="10" inputmode="latin" required
                 placeholder="····" aria-describedby="codi-ajuda">
          <p class="ajuda" id="codi-ajuda">El que hi ha escrit a la pissarra.</p>
        </div>
        <div class="camp">
          <label for="nom">Nom i cognoms</label>
          <input id="nom" name="nom" maxlength="80" required
                 placeholder="Cognom Cognom, Nom">
        </div>
        <div class="camp">
          <label for="grup">Grup</label>
          <select id="grup" name="grup" required></select>
        </div>
        <button type="submit" class="btn btn-primary" style="width:100%">Comença la prova</button>
      </form>
    </section>

    <!-- 2 · Prova -->
    <section class="pas" id="pas-prova">
      <div class="barra">
        <span class="barra-txt" id="progres">0 de {total}</span>
        <span class="barra-pista"><span class="barra-fill" id="progres-fill"></span></span>
      </div>
      <div id="preguntes"></div>
      <div id="prova-err"></div>
      <button type="button" class="btn btn-primary" id="btn-enviar" style="width:100%;margin-top:1rem">
        Enviar les respostes
      </button>
      <p style="font-size:0.8rem;color:var(--text-faint);margin:0.8rem 0 0;text-align:center">
        Un cop enviada no es pot canviar.
      </p>
    </section>

    <!-- 3 · Resultat -->
    <section class="pas" id="pas-resultat">
      <div class="res-cap">
        <div class="nota-gran" id="res-nota">—</div>
        <p class="res-sub" id="res-sub"></p>
      </div>
      <h2 style="font-size:1.05rem;margin:0 0 1rem" id="titol-correccio">Correcció</h2>
      <div id="revisio"></div>
      <div class="peu-acc">
        <a class="btn btn-secondary" href="/docencia/tutoria-2eso/">Tornar a Tutoria</a>
      </div>
    </section>

  </div>
</main>

<footer>
  <div class="container">
    <div class="footer-inner">
      <span><strong>Àlex Reyes</strong> &middot; Matemàtiques, docència i doctorat</span>
      <span>Barcelona &middot; &copy; 2026 Àlex Reyes</span>
    </div>
  </div>
</footer>

<script>
function toggleTheme(){{var h=document.documentElement,n=h.getAttribute('data-theme')==='dark'?'light':'dark';h.setAttribute('data-theme',n);localStorage.setItem('theme',n);}}

const API = '/api/normes';
const TOTAL = {total};
let BANC = [], ALUMNE = null;

const $ = s => document.querySelector(s);
const esc = s => String(s == null ? '' : s).replace(/[&<>"']/g,
  c => ({{'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}}[c]));

function pas(id) {{
  document.querySelectorAll('.pas').forEach(p => p.classList.toggle('on', p.id === id));
  window.scrollTo(0, 0);
}}
function err(on, msg) {{
  $(on).innerHTML = msg ? '<p class="avis avis-err">' + esc(msg) + '</p>' : '';
}}

// Barreja Fisher-Yates. L'ordre de les preguntes canvia per a cada alumne:
// la correcció va per id, així que no afecta la nota, però mirar la pantalla
// del costat deixa de servir.
function barreja(a) {{
  for (let i = a.length - 1; i > 0; i--) {{
    const j = Math.floor(Math.random() * (i + 1));
    [a[i], a[j]] = [a[j], a[i]];
  }}
  return a;
}}

// ─── Enunciats ───────────────────────────────────────────────────
fetch('/assets/data/normes-preguntes.json', {{ cache: 'no-cache' }})
  .then(r => r.ok ? r.json() : Promise.reject(r.status))
  .then(d => {{
    BANC = d.preguntes || [];
    const sel = $('#grup');
    sel.innerHTML = '<option value="">Tria el teu grup…</option>' +
      (d.grups || []).map(g => '<option>' + esc(g) + '</option>').join('');
  }})
  .catch(e => {{
    err('#entrada-err', 'No s\\'han pogut carregar les preguntes. Recarrega la pàgina.');
    console.error('preguntes:', e);
  }});

// ─── 1 · Entrada ─────────────────────────────────────────────────
$('#form-entrada').addEventListener('submit', async ev => {{
  ev.preventDefault();
  err('#entrada-err', '');
  const codi = $('#codi').value.trim().toUpperCase();
  const nom = $('#nom').value.trim();
  const grup = $('#grup').value;
  if (!codi || !nom || !grup) return err('#entrada-err', 'Omple els tres camps.');
  if (!BANC.length) return err('#entrada-err', 'Encara s\\'estan carregant les preguntes.');

  const btn = ev.submitter || $('#form-entrada button');
  btn.disabled = true; btn.textContent = 'Comprovant…';
  try {{
    const r = await fetch(API + '?codi=' + encodeURIComponent(codi));
    const d = await r.json();
    if (!r.ok || !d.ok) {{
      const m = {{ no_existeix: 'Aquest codi no existeix. Mira bé la pissarra.',
                  tancada: 'Aquesta prova ja està tancada.',
                  no_db: 'El servidor no està disponible ara mateix.' }};
      return err('#entrada-err', m[d.error] || 'No s\\'ha pogut comprovar el codi.');
    }}
    ALUMNE = {{ codi, nom, grup }};
    pintaProva();
    pas('pas-prova');
  }} catch (e) {{
    err('#entrada-err', 'Sense connexió amb el servidor.');
    console.error(e);
  }} finally {{
    btn.disabled = false; btn.textContent = 'Comença la prova';
  }}
}});

// ─── 2 · Prova ───────────────────────────────────────────────────
function pintaProva() {{
  const ordre = barreja(BANC.slice());
  $('#preguntes').innerHTML = ordre.map((p, i) => {{
    const ctx = p.tipus === 'situacio'
      ? '<p class="preg-ctx">' + esc(p.q) + '</p><p class="preg-q">' + esc(p.pregunta || '') + '</p>'
      : '<p class="preg-q">' + esc(p.q) + '</p>';
    const ops = p.o.map((o, j) =>
      '<label class="opcio"><input type="radio" name="' + esc(p.id) + '" value="' + j + '">' +
      '<span>' + esc(o) + '</span></label>').join('');
    return '<div class="preg" data-id="' + esc(p.id) + '">' +
      '<div class="preg-cap"><span class="preg-num">' + (i + 1) + ' / ' + TOTAL + '</span>' +
      '<span class="xip">' + (p.tipus === 'situacio' ? 'Situació' : 'Test') + '</span>' +
      '<span class="xip">' + esc(p.bloc) + '</span></div>' + ctx + ops + '</div>';
  }}).join('');
  $('#preguntes').addEventListener('change', progres);
  progres();
}}

function progres() {{
  const fetes = new Set();
  document.querySelectorAll('#preguntes input:checked').forEach(i => fetes.add(i.name));
  $('#progres').textContent = fetes.size + ' de ' + TOTAL;
  $('#progres-fill').style.width = (100 * fetes.size / TOTAL) + '%';
  document.querySelectorAll('#preguntes .preg').forEach(d => {{
    if (fetes.has(d.dataset.id)) d.classList.remove('falta');
  }});
  return fetes;
}}

$('#btn-enviar').addEventListener('click', async () => {{
  err('#prova-err', '');
  const respostes = {{}};
  document.querySelectorAll('#preguntes input:checked')
    .forEach(i => {{ respostes[i.name] = Number(i.value); }});

  const falten = BANC.filter(p => respostes[p.id] === undefined);
  if (falten.length) {{
    const ids = new Set(falten.map(p => p.id));
    document.querySelectorAll('#preguntes .preg').forEach(d => {{
      if (ids.has(d.dataset.id)) d.classList.add('falta');
    }});
    err('#prova-err', 'Et queden ' + falten.length + ' preguntes per respondre.');
    const primera = document.querySelector('#preguntes .preg.falta');
    if (primera) primera.scrollIntoView({{ behavior: 'smooth', block: 'center' }});
    return;
  }}

  const btn = $('#btn-enviar');
  btn.disabled = true; btn.textContent = 'Enviant…';
  try {{
    const r = await fetch(API, {{
      method: 'POST',
      headers: {{ 'content-type': 'application/json' }},
      body: JSON.stringify({{ ...ALUMNE, respostes }}),
    }});
    const d = await r.json();
    if (!r.ok || !d.ok) {{
      const m = {{ tancada: 'La prova s\\'ha tancat mentre la feies. Avisa el professor.',
                  no_existeix: 'El codi ja no és vàlid.' }};
      err('#prova-err', m[d.error] || 'No s\\'ha pogut enviar. Torna-ho a provar.');
      btn.disabled = false; btn.textContent = 'Enviar les respostes';
      return;
    }}
    pintaResultat(d);
    pas('pas-resultat');
  }} catch (e) {{
    err('#prova-err', 'Sense connexió. Les respostes no s\\'han enviat.');
    console.error(e);
    btn.disabled = false; btn.textContent = 'Enviar les respostes';
  }}
}});

// ─── 3 · Resultat ────────────────────────────────────────────────
function pintaResultat(d) {{
  $('#res-nota').textContent = (Math.round(d.nota * 10) / 10).toString().replace('.', ',');
  $('#res-sub').textContent = d.encerts + ' encerts de ' + d.total +
    ' · ' + ALUMNE.nom + ' · ' + ALUMNE.grup;
  const revisio = $('#revisio'), titol = $('#titol-correccio');
  if (!d.correccio) {{
    // El professor encara no ha obert la correcció: nota i prou.
    titol.style.display = 'none';
    revisio.innerHTML = '<p style="text-align:center;color:var(--text-faint);font-size:.9rem">' +
      'Les respostes ja estan enviades. El professor us ensenyarà la correcció a classe.</p>';
    return;
  }}
  titol.style.display = '';
  const perId = {{}};
  BANC.forEach(p => {{ perId[p.id] = p; }});
  $('#revisio').innerHTML = (d.detall || []).map((r, i) => {{
    const p = perId[r.id];
    if (!p) return '';
    const teva = r.teva != null && p.o[r.teva] != null ? p.o[r.teva] : '(sense resposta)';
    const bona = p.o[r.correcta];
    return '<div class="rev ' + (r.ok ? 'rev-be' : 'rev-mal') + '">' +
      '<p class="rev-q">' + (r.ok ? '✓ ' : '✗ ') +
        esc(p.tipus === 'situacio' ? (p.pregunta || p.q) : p.q) + '</p>' +
      (r.ok
        ? '<p class="rev-l">' + esc(bona) + '</p>'
        : '<p class="rev-l">La teva resposta: ' + esc(teva) + '</p>' +
          '<p class="rev-l"><b>Correcta:</b> ' + esc(bona) + '</p>') +
      '<p class="rev-norma">' + esc(r.norma) + '</p></div>';
  }}).join('');
}}
</script>
</body>
</html>
"""
