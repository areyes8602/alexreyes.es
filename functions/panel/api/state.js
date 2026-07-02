// GET / PUT /panel/api/state — estado del panel sincronizado en Cloudflare KV.
// v2: revisiones + detección de conflictos + backup diario automático.
// - Envelope en KV: {__env:1, rev:N, state:{...}}  (compat: si es estado plano, rev=0)
// - PUT nuevo: {__sync:1, baseRev:N, state:{...}} → 200 {ok,rev} o {error:"conflict",rev,state}
// - PUT legado (estado plano): last-write-wins, como antes.
// - Backup: primera escritura de cada día (hora Madrid) → "backup:<user>:<YYYY-MM-DD>", TTL 60 días.
//   GET ?backups=1 → lista; GET ?backup=YYYY-MM-DD → snapshot.
// Requiere sesión válida. Si no hay binding KV, degrada (el cliente sigue en local).
import { verifyToken, getCookie } from "../_auth.js";

function json(data, status = 200) {
  return new Response(JSON.stringify(data), {
    status,
    headers: { "content-type": "application/json; charset=utf-8", "cache-control": "no-store" }
  });
}
function madridDate() {
  const p = new Intl.DateTimeFormat("en-CA", { timeZone: "Europe/Madrid", year: "numeric", month: "2-digit", day: "2-digit" }).format(new Date());
  return p; // en-CA → YYYY-MM-DD
}
function unwrap(raw) {
  if (!raw) return { state: null, rev: 0 };
  try {
    const p = JSON.parse(raw);
    if (p && p.__env === 1) return { state: p.state || null, rev: p.rev || 0 };
    return { state: p, rev: 0 };
  } catch (e) { return { state: null, rev: 0 }; }
}

export async function onRequest(context) {
  const { request, env } = context;

  const user = await verifyToken(getCookie(request), env.PANEL_SECRET);
  if (!user) return json({ error: "unauthorized" }, 401);
  if (!env.PANEL_KV) return json({ error: "no_kv" }, 200);

  const key = "state:" + user;
  const url = new URL(request.url);

  if (request.method === "GET") {
    if (url.searchParams.get("backups") === "1") {
      const list = await env.PANEL_KV.list({ prefix: "backup:" + user + ":" });
      return json({ backups: (list.keys || []).map(k => k.name.split(":").pop()).sort().reverse() });
    }
    const bdate = url.searchParams.get("backup");
    if (bdate) {
      const raw = await env.PANEL_KV.get("backup:" + user + ":" + bdate);
      return json({ state: raw ? JSON.parse(raw) : null, backup: bdate });
    }
    const { state, rev } = unwrap(await env.PANEL_KV.get(key));
    return json({ state, rev });
  }

  if (request.method === "PUT" || request.method === "POST") {
    const body = await request.text();
    if (body.length > 800000) return json({ error: "too_large" }, 413);
    let parsed;
    try { parsed = JSON.parse(body); } catch (e) { return json({ error: "bad_json" }, 400); }

    const isSync = parsed && parsed.__sync === 1;
    const newState = isSync ? parsed.state : parsed;
    const baseRev = isSync ? (parsed.baseRev || 0) : null;
    if (!newState || typeof newState !== "object") return json({ error: "bad_state" }, 400);

    const cur = unwrap(await env.PANEL_KV.get(key));
    if (baseRev !== null && cur.state && baseRev !== cur.rev) {
      return json({ error: "conflict", rev: cur.rev, state: cur.state }, 200);
    }
    const rev = cur.rev + 1;
    await env.PANEL_KV.put(key, JSON.stringify({ __env: 1, rev, state: newState }));

    // Backup diario (primera escritura del día, hora Madrid), 60 días de retención.
    try {
      const bkey = "backup:" + user + ":" + madridDate();
      if (!(await env.PANEL_KV.get(bkey))) {
        await env.PANEL_KV.put(bkey, JSON.stringify(cur.state || newState), { expirationTtl: 60 * 86400 });
      }
    } catch (e) {}

    return json({ ok: true, rev });
  }

  return json({ error: "method_not_allowed" }, 405);
}
