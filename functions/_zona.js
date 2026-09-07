// El porter de les zones privades: /tutoria/ i /mates/.
//
// Corre a l'edge de Cloudflare abans de lliurar res, o sigui que ni les
// pàgines ni les fotos són abastables per URL directa sense haver passat pel
// login. Les dues zones fan servir el mateix usuari i la mateixa contrasenya
// (TUTORIA_USER / TUTORIA_PASS) però cadascuna té la seva cookie: entrar a
// una no obre l'altra, i tancar-ne una no tanca l'altra.
import { privateHeaders } from "./_sessio.js";

export function html(body, status) {
  return new Response(body, {
    status,
    headers: privateHeaders({ "content-type": "text/html; charset=utf-8" }),
  });
}

// `zona` porta: base ("/tutoria"), titol, subtitol, emoji, requireSession.
export async function porta(context, zona) {
  const { request, env, next } = context;
  const url = new URL(request.url);

  // El login i el logout es gestionen sols: el login ha de ser públic.
  if (url.pathname.startsWith(`${zona.base}/api/login`) ||
      url.pathname.startsWith(`${zona.base}/api/logout`)) {
    return next();
  }

  // Configuració incompleta → no s'exposa res.
  if (!env.TUTORIA_USER || !env.TUTORIA_PASS || !env.TUTORIA_SECRET) {
    return html(setupPage(zona), 503);
  }

  if (await zona.requireSession(request, env)) return next();

  // La resta de l'API respon 401 en JSON; les pàgines, amb el login.
  if (url.pathname.startsWith(`${zona.base}/api/`)) {
    return new Response(JSON.stringify({ error: "unauthorized" }), {
      status: 401,
      headers: privateHeaders({ "content-type": "application/json; charset=utf-8" }),
    });
  }

  const err = url.searchParams.get("e");
  return html(loginPage(zona, err), err === "1" ? 401 : 200);
}

function loginPage(zona, err) {
  const msg = err === "1"
    ? '<p class="err">Usuario o contraseña incorrectos.</p>'
    : err === "out" ? '<p class="ok">Sesión cerrada.</p>' : "";
  return `<!DOCTYPE html><html lang="es"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex,nofollow"><title>${zona.titol} · Acceso</title>
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
</style></head><body>
<form class="card" method="POST" action="${zona.base}/api/login">
  <div class="badge">${zona.emoji}</div>
  <h1>${zona.titol}</h1>
  <p class="sub">${zona.subtitol}</p>
  <label for="user">Usuario</label>
  <input id="user" name="user" type="text" autocomplete="username" autocapitalize="none" required>
  <label for="pass">Contraseña</label>
  <input id="pass" name="pass" type="password" autocomplete="current-password" required>
  <button type="submit">Entrar</button>
  ${msg}
</form></body></html>`;
}

function setupPage(zona) {
  return `<!DOCTYPE html><html lang="es"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1"><title>Configurar acceso</title>
<style>body{font-family:-apple-system,system-ui,sans-serif;max-width:600px;margin:60px auto;padding:0 20px;color:#1a1c23;line-height:1.55}
code{background:#ecfdf5;padding:2px 6px;border-radius:6px}h1{font-size:20px}</style></head><body>
<h1>Falta configurar el acceso a ${zona.titol}</h1>
<p>Las dos zonas privadas (<code>/tutoria/</code> y <code>/mates/</code>) usan las
mismas credenciales, así que esto se configura una sola vez.</p>
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
