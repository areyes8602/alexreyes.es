// GET /tutoria/api/documents?grup=2ESO-E — qui ha lliurat què, per nº de llista.
//
// Només els camps del llistat de documents: la fitxa, l'autorització de
// sortides i l'armariet. La combinació del cadenat és del grup del tutor i no
// surt del gate, com la resta de la fitxa.
import { requireSession, unauthorized, json } from "../_auth.js";

export async function onRequestGet(context) {
  const { request, env } = context;
  if (!(await requireSession(request, env))) return unauthorized();
  if (!env.TUTORIA_DB) return json({ error: "no_db", alumnes: [] }, 503);

  const grup = new URL(request.url).searchParams.get("grup") || "2ESO-E";
  try {
    const { results } = await env.TUTORIA_DB
      .prepare(
        `SELECT num, id, nom, cognoms,
                fitxa_inicial, doc_fitxa,
                autoritzacio_sortides, doc_autoritzacio,
                armari, cadenat
           FROM tutoria_alumnes
          WHERE grup = ?
          ORDER BY num`)
      .bind(grup)
      .all();
    return json({ grup, alumnes: results });
  } catch (e) {
    return json({ error: "db", detall: String(e && e.message || e) }, 500);
  }
}
