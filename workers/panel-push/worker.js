// panel-push — Worker con cron que despierta las PWA suscritas (Web Push + VAPID).
// No envía payload: el service worker del panel pide el resumen a /panel/api/digest.
// Requiere: binding KV PANEL_KV (namespace panel-cm), var VAPID_PUBLIC, secret VAPID_PRIVATE.

function b64uToBytes(s) {
  const p = "=".repeat((4 - s.length % 4) % 4);
  const bin = atob((s + p).replace(/-/g, "+").replace(/_/g, "/"));
  return Uint8Array.from(bin, c => c.charCodeAt(0));
}
function bytesToB64u(buf) {
  const bytes = new Uint8Array(buf); let s = "";
  for (const b of bytes) s += String.fromCharCode(b);
  return btoa(s).replace(/\+/g, "-").replace(/\//g, "_").replace(/=+$/, "");
}
function b64uStr(s) {
  return btoa(unescape(encodeURIComponent(s))).replace(/\+/g, "-").replace(/\//g, "_").replace(/=+$/, "");
}

async function vapidJwt(aud, env) {
  const header = b64uStr(JSON.stringify({ typ: "JWT", alg: "ES256" }));
  const payload = b64uStr(JSON.stringify({
    aud, exp: Math.floor(Date.now() / 1000) + 12 * 3600, sub: "mailto:areyes8602@gmail.com"
  }));
  const input = header + "." + payload;
  const key = await crypto.subtle.importKey("pkcs8", b64uToBytes(env.VAPID_PRIVATE).buffer,
    { name: "ECDSA", namedCurve: "P-256" }, false, ["sign"]);
  const sig = await crypto.subtle.sign({ name: "ECDSA", hash: "SHA-256" }, key, new TextEncoder().encode(input));
  return input + "." + bytesToB64u(sig);
}

async function sendPush(endpoint, env) {
  const aud = new URL(endpoint).origin;
  const jwt = await vapidJwt(aud, env);
  return fetch(endpoint, {
    method: "POST",
    headers: { TTL: "3600", Urgency: "normal", Authorization: "vapid t=" + jwt + ", k=" + env.VAPID_PUBLIC },
  });
}

async function sendAll(env) {
  const list = await env.PANEL_KV.list({ prefix: "push:" });
  const out = [];
  for (const k of (list.keys || [])) {
    try {
      const rec = await env.PANEL_KV.get(k.name, "json");
      const sub = rec && rec.subscription;
      if (!sub || !sub.endpoint) { await env.PANEL_KV.delete(k.name); continue; }
      const r = await sendPush(sub.endpoint, env);
      if (r.status === 404 || r.status === 410) { await env.PANEL_KV.delete(k.name); out.push(k.name + " → baja (" + r.status + ")"); }
      else out.push(k.name + " → " + r.status);
    } catch (e) { out.push(k.name + " → error " + (e && e.message)); }
  }
  return out;
}

export default {
  async scheduled(event, env, ctx) { ctx.waitUntil(sendAll(env)); },
  // GET manual para probar sin esperar al cron: requiere ?key=<VAPID_PUBLIC>
  async fetch(request, env) {
    const u = new URL(request.url);
    if (u.searchParams.get("key") !== env.VAPID_PUBLIC) return new Response("no", { status: 403 });
    const res = await sendAll(env);
    return new Response(JSON.stringify(res, null, 1), { headers: { "content-type": "application/json" } });
  }
};
