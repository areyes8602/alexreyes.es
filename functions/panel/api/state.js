// GET / PUT /panel/api/state — estado del panel sincronizado en Cloudflare KV.
// Requiere sesión válida. Si no hay binding KV, degrada (el cliente sigue en local).
import { verifyToken, getCookie } from "../_auth.js";

function json(data, status = 200) {
  return new Response(JSON.stringify(data), {
    status,
    headers: { "content-type": "application/json; charset=utf-8", "cache-control": "no-store" }
  });
}

export async function onRequest(context) {
  const { request, env } = context;

  const user = await verifyToken(getCookie(request), env.PANEL_SECRET);
  if (!user) return json({ error: "unauthorized" }, 401);

  // Sin binding KV → el cliente se queda en modo local.
  if (!env.PANEL_KV) return json({ error: "no_kv" }, 200);

  const key = "state:" + user;

  if (request.method === "GET") {
    const raw = await env.PANEL_KV.get(key);
    return json({ state: raw ? JSON.parse(raw) : null }, 200);
  }

  if (request.method === "PUT" || request.method === "POST") {
    const body = await request.text();
    if (body.length > 800000) return json({ error: "too_large" }, 413);
    let parsed;
    try { parsed = JSON.parse(body); } catch (e) { return json({ error: "bad_json" }, 400); }
    await env.PANEL_KV.put(key, JSON.stringify(parsed));
    return json({ ok: true }, 200);
  }

  return json({ error: "method_not_allowed" }, 405);
}
