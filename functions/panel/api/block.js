// POST /panel/api/block — crea un evento "🎯 Foco" en Google Calendar al iniciar un bloque.
// Usa la cuenta de servicio con scope de escritura (calendar.events).
// El calendario destino (GCAL_WRITE_ID, o el primero de GCAL_IDS/GCAL_ID) debe estar
// compartido con la cuenta de servicio con permiso "Hacer cambios en los eventos".
import { verifyToken, getCookie } from "../_auth.js";

function json(data, status = 200) {
  return new Response(JSON.stringify(data), {
    status, headers: { "content-type": "application/json; charset=utf-8", "cache-control": "no-store" }
  });
}
function b64urlBytes(buf) {
  const bytes = new Uint8Array(buf); let bin = "";
  for (let i = 0; i < bytes.length; i++) bin += String.fromCharCode(bytes[i]);
  return btoa(bin).replace(/\+/g, "-").replace(/\//g, "_").replace(/=+$/, "");
}
function b64urlStr(s) {
  return btoa(unescape(encodeURIComponent(s))).replace(/\+/g, "-").replace(/\//g, "_").replace(/=+$/, "");
}
function pemToDer(pem) {
  const s = pem.replace(/\\n/g, "\n").replace(/-----[^-]*-----/g, "");
  const body = s.replace(/[^A-Za-z0-9+/=]/g, "");
  const bin = atob(body); const der = new Uint8Array(bin.length);
  for (let i = 0; i < bin.length; i++) der[i] = bin.charCodeAt(i);
  return der.buffer;
}
async function getAccessToken(email, keyPem, scope) {
  const now = Math.floor(Date.now() / 1000);
  const header = b64urlStr(JSON.stringify({ alg: "RS256", typ: "JWT" }));
  const claim = b64urlStr(JSON.stringify({ iss: email, scope, aud: "https://oauth2.googleapis.com/token", iat: now, exp: now + 3600 }));
  const input = header + "." + claim;
  const key = await crypto.subtle.importKey("pkcs8", pemToDer(keyPem),
    { name: "RSASSA-PKCS1-v1_5", hash: "SHA-256" }, false, ["sign"]);
  const sig = await crypto.subtle.sign("RSASSA-PKCS1-v1_5", key, new TextEncoder().encode(input));
  const jwt = input + "." + b64urlBytes(sig);
  const r = await fetch("https://oauth2.googleapis.com/token", {
    method: "POST",
    headers: { "content-type": "application/x-www-form-urlencoded" },
    body: "grant_type=urn:ietf:params:oauth:grant-type:jwt-bearer&assertion=" + encodeURIComponent(jwt)
  });
  const j = await r.json().catch(() => ({}));
  if (!r.ok || !j.access_token) throw new Error("token " + r.status);
  return j.access_token;
}

export async function onRequest(context) {
  const { request, env } = context;
  if (request.method !== "POST") return json({ error: "method_not_allowed" }, 405);
  const user = await verifyToken(getCookie(request), env.PANEL_SECRET);
  if (!user) return json({ error: "unauthorized" }, 401);
  if (!env.GCAL_SA_EMAIL || !env.GCAL_SA_KEY) return json({ error: "no_gcal" }, 200);

  let body; try { body = await request.json(); } catch (e) { return json({ error: "bad_json" }, 400); }
  const mins = Math.max(5, Math.min(240, parseInt(body.mins) || 90));
  const frente = String(body.frente || "").slice(0, 24);

  const firstId = (env.GCAL_IDS || env.GCAL_ID || user).split(",")[0].split("::")[0].trim();
  const calId = (env.GCAL_WRITE_ID || firstId).split("::")[0].trim();

  try {
    const token = await getAccessToken(env.GCAL_SA_EMAIL, env.GCAL_SA_KEY.replace(/\\n/g, "\n"),
      "https://www.googleapis.com/auth/calendar.events");
    const start = new Date(), end = new Date(start.getTime() + mins * 60000);
    const r = await fetch(`https://www.googleapis.com/calendar/v3/calendars/${encodeURIComponent(calId)}/events`, {
      method: "POST",
      headers: { Authorization: "Bearer " + token, "content-type": "application/json" },
      body: JSON.stringify({
        summary: "🎯 Foco" + (frente ? ": " + frente : ""),
        description: "Bloque de foco creado desde el Centro de Mando.",
        start: { dateTime: start.toISOString() },
        end: { dateTime: end.toISOString() },
        transparency: "opaque",
        reminders: { useDefault: false }
      })
    });
    if (r.status === 403) return json({ error: "not_shared_write" }, 200);
    if (r.status === 404) return json({ error: "cal_not_found" }, 200);
    const j = await r.json().catch(() => ({}));
    if (!r.ok) return json({ error: "gcal_error", status: r.status }, 200);
    return json({ ok: true, id: j.id, htmlLink: j.htmlLink || "" });
  } catch (e) {
    return json({ error: "gcal_error", detail: String(e && e.message || e).slice(0, 200) }, 200);
  }
}
