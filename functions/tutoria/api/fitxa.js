// GET  /tutoria/api/fitxa?id=…  — ficha completa de un alumno.
// POST /tutoria/api/fitxa       — guarda las notas de seguimiento.
import { requireSession, unauthorized, json } from "../_auth.js";

export async function onRequestGet(context) {
  const { request, env } = context;
  if (!(await requireSession(request, env))) return unauthorized();
  if (!env.TUTORIA_DB) return json({ error: "no_db" }, 503);

  const id = new URL(request.url).searchParams.get("id");
  if (!id) return json({ error: "missing_id" }, 400);

  const row = await env.TUTORIA_DB
    .prepare(`SELECT * FROM tutoria_alumnes WHERE id = ?`)
    .bind(id)
    .first();

  if (!row) return json({ error: "not_found" }, 404);
  return json({ alumne: row });
}

export async function onRequestPost(context) {
  const { request, env } = context;
  const user = await requireSession(request, env);
  if (!user) return unauthorized();
  if (!env.TUTORIA_DB) return json({ error: "no_db" }, 503);

  let body;
  try { body = await request.json(); } catch (e) { return json({ error: "bad_json" }, 400); }

  const id = (body.id || "").toString();
  if (!id) return json({ error: "missing_id" }, 400);

  // Solo se pueden editar los campos de seguimiento; la identidad viene
  // del importador de la orla y no se toca desde el navegador.
  const notes = (body.notes ?? "").toString().slice(0, 20000);
  const contacte = (body.contacte ?? "").toString().slice(0, 2000);

  const res = await env.TUTORIA_DB
    .prepare(
      `UPDATE tutoria_alumnes
          SET notes = ?, contacte = ?, updated_at = ?
        WHERE id = ?`
    )
    .bind(notes, contacte, new Date().toISOString(), id)
    .run();

  if (!res.meta || res.meta.changes === 0) return json({ error: "not_found" }, 404);
  return json({ ok: true });
}
