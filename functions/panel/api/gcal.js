// GET /panel/api/gcal — agenda desde Google Calendar vía cuenta de servicio (JWT RS256).
// Requiere sesión válida y secrets GCAL_SA_EMAIL + GCAL_SA_KEY. Degrada si faltan.
// El calendario (GCAL_ID, por defecto el correo del usuario) debe estar compartido con la cuenta de servicio.
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
  // Tolerante: convierte \n escapados, quita cualquier cabecera -----...----- y
  // TODO carácter que no sea base64 (comillas, comas, espacios, saltos) que puedan
  // haberse colado al copiar desde el JSON.
  const s = pem.replace(/\\n/g, "\n").replace(/-----[^-]*-----/g, "");
  const body = s.replace(/[^A-Za-z0-9+/=]/g, "");
  const bin = atob(body); const der = new Uint8Array(bin.length);
  for (let i = 0; i < bin.length; i++) der[i] = bin.charCodeAt(i);
  return der.buffer;
}
async function getAccessToken(email, keyPem) {
  const now = Math.floor(Date.now() / 1000);
  const header = b64urlStr(JSON.stringify({ alg: "RS256", typ: "JWT" }));
  const claim = b64urlStr(JSON.stringify({
    iss: email,
    scope: "https://www.googleapis.com/auth/calendar.readonly",
    aud: "https://oauth2.googleapis.com/token",
    iat: now, exp: now + 3600
  }));
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
  if (!r.ok || !j.access_token) throw { where: "token", status: r.status, body: j };
  return j.access_token;
}

export async function onRequest(context) {
  const { request, env } = context;
  const user = await verifyToken(getCookie(request), env.PANEL_SECRET);
  if (!user) return json({ error: "unauthorized" }, 401);
  if (!env.GCAL_SA_EMAIL || !env.GCAL_SA_KEY) return json({ error: "no_gcal" }, 200);

  const url = new URL(request.url);
  const now = new Date();
  const timeMin = url.searchParams.get("timeMin") || new Date(now.getTime() - 6 * 3600e3).toISOString();
  const timeMax = url.searchParams.get("timeMax") || new Date(now.getTime() + 8 * 86400e3).toISOString();
  const calId = env.GCAL_ID || user; // el correo de la sesión suele ser el calendario

  try {
    const key = env.GCAL_SA_KEY.replace(/\\n/g, "\n");
    const token = await getAccessToken(env.GCAL_SA_EMAIL, key);
    const api = `https://www.googleapis.com/calendar/v3/calendars/${encodeURIComponent(calId)}/events` +
      `?singleEvents=true&orderBy=startTime&maxResults=50` +
      `&timeMin=${encodeURIComponent(timeMin)}&timeMax=${encodeURIComponent(timeMax)}`;
    const r = await fetch(api, { headers: { Authorization: "Bearer " + token } });
    const j = await r.json().catch(() => ({}));
    if (r.status === 404) return json({ error: "cal_not_found" }, 200);
    if (r.status === 403) return json({ error: "not_shared" }, 200);
    if (!r.ok) throw { where: "events", status: r.status, body: j };
    const events = (j.items || []).filter(e => e.status !== "cancelled").map(e => ({
      summary: e.summary || "(sin título)",
      start: e.start && (e.start.dateTime || e.start.date),
      end: e.end && (e.end.dateTime || e.end.date),
      allDay: !!(e.start && e.start.date && !e.start.dateTime),
      location: e.location || ""
    }));
    return json({ events, fetchedAt: Date.now() });
  } catch (e) {
    let detail = "";
    try {
      if (e && e.body) detail = e.body.error_description || e.body.error || JSON.stringify(e.body);
      else detail = (e && e.message) ? e.message : String(e);
    } catch (_) {}
    return json({ error: "gcal_error", status: (e && e.status) || 500, where: (e && e.where) || "", detail: (detail || "").slice(0, 240) }, 200);
  }
}
