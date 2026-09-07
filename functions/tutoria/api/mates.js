// A quin grup de matemàtiques va cada alumne de la tutoria.
//
//   GET /tutoria/api/mates?origen=2ESO-E
//
// Només llegeix. El quadern de notes és a l'altra zona
// (functions/mates/api/quadern.js) i no s'hi arriba des d'aquí: amb una
// sessió de tutoria es pot veure a quin grup va cadascú, mai tocar-li una nota.
import { requireSession, unauthorized, json } from "../_auth.js";

const CURS = "2026-27";

export async function onRequestGet(context) {
  const { request, env } = context;
  if (!(await requireSession(request, env))) return unauthorized();
  if (!env.TUTORIA_DB) return json({ error: "no_db" }, 503);

  const url = new URL(request.url);
  const curs = url.searchParams.get("curs") || CURS;
  const origen = url.searchParams.get("origen");
  if (!origen) return json({ error: "falta_origen" }, 400);

  try {
    // Una sola consulta per a tota la classe: la llista de tutoria en demana
    // vint-i-set d'un cop, no un per alumne.
    const { results } = await env.TUTORIA_DB.prepare(
      `SELECT a.id, a.nivell, g.professor, g.aula
         FROM mates_alumnes a LEFT JOIN mates_grups g
           ON g.curs = a.curs AND g.nivell = a.nivell
        WHERE a.curs = ? AND a.grup_origen = ?`).bind(curs, origen).all();
    return json({ alumnes: results });
  } catch (e) {
    // Si encara no s'han creat les taules de mates, la fitxa i la llista
    // s'han de poder pintar igual: millor sense el grup que no pas trencades.
    if (/no such table/i.test(String(e && e.message || e)))
      return json({ alumnes: [] });
    return json({ error: "db", detall: String(e && e.message || e) }, 500);
  }
}
