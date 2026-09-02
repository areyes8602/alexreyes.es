// GET /tutoria/api/alumnes?grup=2ESO-E — listado de la orla.
//
// Los datos NO viven en el repositorio: se leen de D1 en tiempo de
// petición. El middleware ya ha exigido sesión antes de llegar aquí.
import { requireSession, unauthorized, json } from "../_auth.js";

export async function onRequestGet(context) {
  const { request, env } = context;
  if (!(await requireSession(request, env))) return unauthorized();
  if (!env.TUTORIA_DB) return json({ error: "no_db", alumnes: [] }, 503);

  const grup = new URL(request.url).searchParams.get("grup") || "2ESO-E";
  const { results } = await env.TUTORIA_DB
    .prepare(
      `SELECT id, num, grup, cognoms, nom, foto, marca
         FROM tutoria_alumnes
        WHERE grup = ?
        ORDER BY num`
    )
    .bind(grup)
    .all();

  return json({ grup, total: results.length, alumnes: results });
}
