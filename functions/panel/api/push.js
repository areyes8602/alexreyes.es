// POST/DELETE /panel/api/push — alta/baja de suscripciones Web Push.
// Guarda en KV: "push:<user>:<hash(endpoint)>" = {subscription, created}
// Las lee el Worker `panel-push` (cron) para enviar los avisos.
import { verifyToken, getCookie } from "../_auth.js";

function json(data, status = 200) {
  return new Response(JSON.stringify(data), {
    status, headers: { "content-type": "application/json; charset=utf-8", "cache-control": "no-store" }
  });
}
async function endpointHash(endpoint) {
  const d = await crypto.subtle.digest("SHA-256", new TextEncoder().encode(endpoint));
  return [...new Uint8Array(d)].slice(0, 12).map(b => b.toString(16).padStart(2, "0")).join("");
}

export async function onRequest(context) {
  const { request, env } = context;
  const user = await verifyToken(getCookie(request), env.PANEL_SECRET);
  if (!user) return json({ error: "unauthorized" }, 401);
  if (!env.PANEL_KV) return json({ error: "no_kv" }, 200);

  if (request.method === "POST") {
    let body; try { body = await request.json(); } catch (e) { return json({ error: "bad_json" }, 400); }
    const sub = body && body.subscription;
    if (!sub || !sub.endpoint || !/^https:\/\//.test(sub.endpoint)) return json({ error: "bad_subscription" }, 400);
    const key = "push:" + user + ":" + await endpointHash(sub.endpoint);
    await env.PANEL_KV.put(key, JSON.stringify({ subscription: sub, created: Date.now() }));
    return json({ ok: true });
  }

  if (request.method === "DELETE") {
    let body; try { body = await request.json(); } catch (e) { return json({ error: "bad_json" }, 400); }
    if (!body || !body.endpoint) return json({ error: "bad_request" }, 400);
    await env.PANEL_KV.delete("push:" + user + ":" + await endpointHash(body.endpoint));
    return json({ ok: true });
  }

  if (request.method === "GET") {
    const list = await env.PANEL_KV.list({ prefix: "push:" + user + ":" });
    return json({ count: (list.keys || []).length });
  }

  return json({ error: "method_not_allowed" }, 405);
}
