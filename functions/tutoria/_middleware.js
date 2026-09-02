// Guarda /tutoria/*: sin sesión válida no se sirve NADA, ni HTML ni fotos.
//
// A diferencia de un gate de cliente, esto corre en el edge de Cloudflare
// antes de entregar el recurso, así que las páginas y las fotos no son
// alcanzables por URL directa sin haber pasado por el login.
import { requireSession, privateHeaders } from "./_auth.js";

export async function onRequest(context) {
  const { request, env, next } = context;
  const url = new URL(request.url);

  // Los endpoints de auth se gestionan solos (login necesita ser público).
  if (url.pathname.startsWith("/tutoria/api/login") ||
      url.pathname.startsWith("/tutoria/api/logout")) {
    return next();
  }

  // Config incompleta → no se expone nada.
  if (!env.TUTORIA_USER || !env.TUTORIA_PASS || !env.TUTORIA_SECRET) {
    return html(setupPage(), 503);
  }

  if (await requireSession(request, env)) return next();

  // El resto de la API responde 401 en JSON; las páginas, con el login.
  if (url.pathname.startsWith("/tutoria/api/")) {
    return new Response(JSON.stringify({ error: "unauthorized" }), {
      status: 401,
      headers: privateHeaders({ "content-type": "application/json; charset=utf-8" }),
    });
  }

  const err = url.searchParams.get("e");
  return html(loginPage(err), err === "1" ? 401 : 200);
}

function html(body, status) {
  return new Response(body, {
    status,
    headers: privateHeaders({ "content-type": "text/html; charset=utf-8" }),
  });
}

function loginPage(err) {
  const msg = err === "1"
    ? '<p class="err">Usuario o contraseña incorrectos.</p>'
    : err === "out" ? '<p class="ok">Sesión cerrada.</p>' : "";
  return `<!DOCTYPE html><html lang="es"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex,nofollow"><title>Tutoría · Acceso</title>
<style>
 :root{color-scheme:light}
 *{box-sizing:border-box}
 body{margin:0;min-height:100vh;display:flex;align-items:center;justify-content:center;
   background:linear-gradient(135deg,#0f766e,#065f46);
   font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif;padding:20px}
 .card{background:#fff;border-radius:18px;padding:30px 26px;width:100%;max-width:340px;
   box-shadow:0 20px 60px rgba(6,40,35,.35);text-align:center}
 .badge{width:64px;height:64px;border-radius:16px;margin:0 auto 14px;font-size:30px;
   background:linear-gradient(135deg,#0f766e,#065f46);display:flex;align-items:center;justify-content:center}
 h1{font-size:19px;margin:0 0 2px}
 .sub{color:#6b7280;font-size:13px;margin:0 0 18px}
 label{display:block;text-align:left;font-size:12px;font-weight:700;color:#374151;margin:10px 0 4px}
 input{width:100%;padding:11px 12px;border:1px solid #e6e8ef;border-radius:10px;font-size:15px}
 input:focus{outline:none;border-color:#0f766e;box-shadow:0 0 0 3px rgba(15,118,110,.15)}
 button{width:100%;margin-top:18px;padding:12px;border:0;border-radius:10px;cursor:pointer;
   background:#0f766e;color:#fff;font-size:15px;font-weight:700}
 button:hover{background:#0b5d56}
 .err{color:#dc2626;font-size:13px;font-weight:600;margin:12px 0 0}
 .ok{color:#059669;font-size:13px;font-weight:600;margin:12px 0 0}
 .foot{margin:16px 0 0;font-size:11px;color:#9ca3af;line-height:1.4}
</style></head><body>
<form class="card" method="POST" action="/tutoria/api/login">
  <div class="badge">🎓</div>
  <h1>Tutoría</h1>
  <p class="sub">Acceso privado</p>
  <label for="user">Usuario</label>
  <input id="user" name="user" type="text" autocomplete="username" autocapitalize="none" required>
  <label for="pass">Contraseña</label>
  <input id="pass" name="pass" type="password" autocomplete="current-password" required>
  <button type="submit">Entrar</button>
  ${msg}
  <p class="foot">Contiene datos personales de menores. No compartas el acceso
  ni dejes la sesión abierta en equipos ajenos.</p>
</form></body></html>`;
}

function setupPage() {
  return `<!DOCTYPE html><html lang="es"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1"><title>Configurar acceso</title>
<style>body{font-family:-apple-system,system-ui,sans-serif;max-width:600px;margin:60px auto;padding:0 20px;color:#1a1c23;line-height:1.55}
code{background:#ecfdf5;padding:2px 6px;border-radius:6px}h1{font-size:20px}</style></head><body>
<h1>Falta configurar el acceso a Tutoría</h1>
<p>En Cloudflare Pages, proyecto <b>alexreyes-web</b> (el que sirve alexreyes.es;
no lo confundas con <i>alexreyes-es</i>) → Settings → Environment variables:</p>
<ul>
<li><code>TUTORIA_USER</code> — usuario</li>
<li><code>TUTORIA_PASS</code> — contraseña <b>larga y aleatoria</b>, de gestor de
contraseñas y usada solo aquí. Es lo único que separa las fotos de los alumnos
de internet: no reutilices ninguna que tengas en otro sitio.</li>
<li><code>TUTORIA_SECRET</code> — otra cadena larga y aleatoria, distinta de la
anterior (firma la cookie de sesión; cambiarla cierra todas las sesiones)</li>
</ul>
<p>Y en el mismo proyecto, Settings → Functions → Bindings:</p>
<ul>
<li><code>TUTORIA_DB</code> — base de datos D1 con las fichas</li>
<li><code>TUTORIA_FOTOS</code> — bucket R2 con las fotos</li>
</ul>
<p>Mientras falte cualquiera de las tres variables, esta sección no sirve nada.</p>
</body></html>`;
}
