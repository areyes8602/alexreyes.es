// Listas de control de tutoría.
//
//   GET  /tutoria/api/llistes?grup=…       totes, sense les dades
//   GET  /tutoria/api/llistes?id=…         una, amb les dades
//   POST /tutoria/api/llistes              crear o desar
//   POST /tutoria/api/llistes?esborra=id   esborrar
import { requireSession, unauthorized, json } from "../_auth.js";

const SAFE_ID = /^[a-z0-9-]{1,80}$/;

function slug(text) {
  return text.normalize("NFD").replace(/[̀-ͯ]/g, "")
    .toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/^-|-$/g, "").slice(0, 80);
}

export async function onRequestGet(context) {
  const { request, env } = context;
  if (!(await requireSession(request, env))) return unauthorized();
  if (!env.TUTORIA_DB) return json({ error: "no_db", llistes: [] }, 503);

  const url = new URL(request.url);
  const id = url.searchParams.get("id");
  try {
    if (id) {
      const row = await env.TUTORIA_DB
        .prepare(`SELECT * FROM tutoria_llistes WHERE id = ?`).bind(id).first();
      if (!row) return json({ error: "not_found" }, 404);
      return json({ llista: row });
    }
    // El listado no arrastra `dades`: solo cuántos llevan hecho, que es lo
    // que se enseña en el índice.
    const grup = url.searchParams.get("grup") || "2ESO-E";
    const { results } = await env.TUTORIA_DB
      .prepare(`SELECT id, nom, descripcio, dades, creada, updated_at
                  FROM tutoria_llistes WHERE grup = ? ORDER BY creada DESC`)
      .bind(grup).all();
    const llistes = results.map(({ dades, ...r }) => {
      let fets = 0;
      try { fets = Object.values(JSON.parse(dades || "{}")).filter(v => v && v.fet).length; }
      catch (e) { /* dades malmeses: compta zero */ }
      return { ...r, fets };
    });
    return json({ llistes });
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
      await env.TUTORIA_DB.prepare(`DELETE FROM tutoria_llistes WHERE id = ?`)
        .bind(esborra).run();
      return json({ ok: true });
    }

    let body;
    try { body = await request.json(); } catch (e) { return json({ error: "bad_json" }, 400); }

    const nom = (body.nom || "").toString().trim().slice(0, 120);
    if (!nom) return json({ error: "falta_nom" }, 400);
    const id = SAFE_ID.test(body.id || "") ? body.id : slug(nom);
    if (!id) return json({ error: "bad_id" }, 400);

    const ara = new Date().toISOString();
    const dades = JSON.stringify(body.dades && typeof body.dades === "object" ? body.dades : {});

    await env.TUTORIA_DB.prepare(
      `INSERT INTO tutoria_llistes (id, grup, curs, nom, descripcio, dades, creada, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
       ON CONFLICT(id) DO UPDATE SET
            nom = excluded.nom, descripcio = excluded.descripcio,
            dades = excluded.dades, updated_at = excluded.updated_at`
    ).bind(id, (body.grup || "2ESO-E").toString(), (body.curs || "2026-27").toString(),
           nom, (body.descripcio || "").toString().slice(0, 600), dades, ara, ara).run();

    return json({ ok: true, id, updated_at: ara });
  } catch (e) {
    return json({ error: "db", detall: String(e && e.message || e) }, 500);
  }
}
