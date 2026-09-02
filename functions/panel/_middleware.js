// Guarda /panel/*: exige sesión válida; si no, muestra el login.
import { verifyToken, getCookie } from "./_auth.js";

export async function onRequest(context) {
  const { request, env, next } = context;
  const url = new URL(request.url);
  const path = url.pathname;

  // Los endpoints de auth se gestionan solos.
  if (path.startsWith("/panel/api/")) return next();

  // Config incompleta → página de setup (evita exponer el panel sin credenciales).
  if (!env.PANEL_USER || !env.PANEL_PASS || !env.PANEL_SECRET) {
    return html(setupPage(), 503);
  }

  const user = await verifyToken(getCookie(request), env.PANEL_SECRET);
  if (user) return next(); // sesión válida → servir el recurso solicitado

  const err = url.searchParams.get("e");
  return html(loginPage(err), err === "1" ? 401 : 200);
}

function html(body, status) {
  return new Response(body, {
    status,
    headers: {
      "content-type": "text/html; charset=utf-8",
      "cache-control": "no-store",
      "x-robots-tag": "noindex, nofollow"
    }
  });
}

function loginPage(err) {
  const msg = err === "1"
    ? '<p class="err">Usuario o contraseña incorrectos.</p>'
    : err === "out"
    ? '<p class="ok">Sesión cerrada.</p>'
    : "";
  return `<!DOCTYPE html><html lang="es"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex,nofollow"><title>Centro de Mando · Acceso</title>
<link rel="apple-touch-icon" href="/panel/icon-180.png">
<style>
 :root{color-scheme:light}
 *{box-sizing:border-box}
 body{margin:0;min-height:100vh;display:flex;align-items:center;justify-content:center;
   background:linear-gradient(135deg,#4f46e5,#7c3aed);
   font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif;padding:20px}
 .card{background:#fff;border-radius:18px;padding:30px 26px;width:100%;max-width:340px;
   box-shadow:0 20px 60px rgba(20,10,60,.35);text-align:center}
 .badge{width:64px;height:64px;border-radius:16px;margin:0 auto 14px;
   background:linear-gradient(135deg,#4f46e5,#7c3aed);display:flex;align-items:center;justify-content:center}
 .badge svg{width:38px;height:38px}
 h1{font-size:19px;margin:0 0 2px}
 .sub{color:#6b7280;font-size:13px;margin:0 0 18px}
 label{display:block;text-align:left;font-size:12px;font-weight:700;color:#374151;margin:10px 0 4px}
 input{width:100%;padding:11px 12px;border:1px solid #e6e8ef;border-radius:10px;font-size:15px}
 input:focus{outline:none;border-color:#7c3aed;box-shadow:0 0 0 3px rgba(124,58,237,.15)}
 button{width:100%;margin-top:18px;padding:12px;border:0;border-radius:10px;cursor:pointer;
   background:#7c3aed;color:#fff;font-size:15px;font-weight:700}
 button:hover{background:#6d28d9}
 .err{color:#dc2626;font-size:13px;font-weight:600;margin:12px 0 0}
 .ok{color:#059669;font-size:13px;font-weight:600;margin:12px 0 0}
</style></head><body>
<form class="card" method="POST" action="/panel/api/login">
  <div class="badge"><svg viewBox="0 0 100 100" fill="none" stroke="#fff" stroke-width="7">
    <circle cx="50" cy="50" r="30"/><circle cx="50" cy="50" r="16"/><circle cx="50" cy="50" r="4" fill="#fff" stroke="none"/></svg></div>
  <h1>Centro de Mando</h1>
  <p class="sub">Acceso privado</p>
  <label for="user">Usuario</label>
  <input id="user" name="user" type="text" autocomplete="username" autocapitalize="none" required>
  <label for="pass">Contraseña</label>
  <input id="pass" name="pass" type="password" autocomplete="current-password" required>
  <button type="submit">Entrar</button>
  ${msg}
</form></body></html>`;
}

function setupPage() {
  return `<!DOCTYPE html><html lang="es"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1"><title>Configurar acceso</title>
<style>body{font-family:-apple-system,system-ui,sans-serif;max-width:560px;margin:60px auto;padding:0 20px;color:#1a1c23;line-height:1.5}
code{background:#f3f0ff;padding:2px 6px;border-radius:6px}h1{font-size:20px}</style></head><body>
<h1>Falta configurar el acceso</h1>
<p>El panel está desplegado pero necesita sus credenciales. En Cloudflare Pages,
proyecto <b>alexreyes-web</b> (el que sirve alexreyes.es; no lo confundas con
<i>alexreyes-es</i>) → Settings → Environment variables, añade:</p>
<ul>
<li><code>PANEL_USER</code> — tu usuario</li>
<li><code>PANEL_PASS</code> — tu contraseña</li>
<li><code>PANEL_SECRET</code> — una cadena larga y aleatoria (para firmar la sesión)</li>
</ul>
<p>Vuelve a desplegar (o espera al siguiente deploy) y recarga esta página.</p>
</body></html>`;
}
