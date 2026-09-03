// Distribucions de l'aula.
//
//   GET  /tutoria/api/aula?grup=…      totes les distribucions del grup
//   GET  /tutoria/api/aula?id=…        una, amb les posicions
//   POST /tutoria/api/aula             crear o desar
//   POST /tutoria/api/aula?esborra=id  esborrar
import { requireSession, unauthorized, json } from "../_auth.js";

const SAFE_ID = /^[a-z0-9-]{1,80}$/;

function slug(text) {
  return text.normalize("NFD").replace(/[̀-ͯ]/g, "")
    .toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/^-|-$/g, "").slice(0, 80);
}

export async function onRequestGet(context) {
  const { request, env } = context;
  if (!(await requireSession(request, env))) return unauthorized();
  if (!env.TUTORIA_DB) return json({ error: "no_db", aules: [] }, 503);

  const url = new URL(request.url);
  const id = url.searchParams.get("id");
  try {
    if (id) {
      const row = await env.TUTORIA_DB
        .prepare(`SELECT * FROM tutoria_aules WHERE id = ?`).bind(id).first();
      if (!row) return json({ error: "not_found" }, 404);
      return json({ aula: row });
    }
    const grup = url.searchParams.get("grup") || "2ESO-E";
    const { results } = await env.TUTORIA_DB
      .prepare(`SELECT id, nom, creada, updated_at FROM tutoria_aules
                 WHERE grup = ? ORDER BY creada`)
      .bind(grup).all();
    return json({ aules: results });
  } catch (e) {
    return json({ error: "db", detall: String(e && e.message || e) }, 500);
  }
}

export async function onRequestPost(context) {
  const { request, env } = context;
  if (!(await requireSession(request, env))) return unauthorized();
  if (!env.TUTORIA_DB) return json({ error: "no_db" }, 503);

  const url = new URL(request.url);
  const esborra = url.searchParams.get("esborra");
  try {
    if (esborra) {
      if (!SAFE_ID.test(esborra)) return json({ error: "bad_id" }, 400);
      await env.TUTORIA_DB.prepare(`DELETE FROM tutoria_aules WHERE id = ?`)
        .bind(esborra).run();
      return json({ ok: true });
    }

    let body;
    try { body = await request.json(); } catch (e) { return json({ error: "bad_json" }, 400); }
    const nom = (body.nom || "").toString().trim().slice(0, 120);
    if (!nom) return json({ error: "falta_nom" }, 400);
    const id = SAFE_ID.test(body.id || "") ? body.id : slug(nom);
    if (!id) return json({ error: "bad_id" }, 400);

    // Les posicions es guarden en % i s'acoten: una coordenada fora de rang
    // deixaria una targeta fora del plànol i sense manera d'arrossegar-la.
    const pos = {};
    for (const [alumne, p] of Object.entries(body.posicions || {})) {
      if (!p || typeof p !== "object") continue;
      pos[alumne] = {
        x: Math.min(100, Math.max(0, Number(p.x) || 0)),
        y: Math.min(100, Math.max(0, Number(p.y) || 0)),
      };
    }

    const ara = new Date().toISOString();
    await env.TUTORIA_DB.prepare(
      `INSERT INTO tutoria_aules (id, grup, curs, nom, posicions, creada, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
       ON CONFLICT(id) DO UPDATE SET
            nom = excluded.nom, posicions = excluded.posicions,
            updated_at = excluded.updated_at`
    ).bind(id, (body.grup || "2ESO-E").toString(), (body.curs || "2026-27").toString(),
           nom, JSON.stringify(pos), ara, ara).run();

    return json({ ok: true, id, updated_at: ara });
  } catch (e) {
    return json({ error: "db", detall: String(e && e.message || e) }, 500);
  }
}
