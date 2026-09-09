// A quin grup de nivell va cada alumne de la tutoria, matèria per matèria.
//
//   GET /tutoria/api/nivells?origen=2ESO-E
//
// Només llegeix. El quadern de notes és a l'altra zona
// (functions/mates-2eso/api/quadern.js) i no s'hi arriba des d'aquí: amb una
// sessió de tutoria es pot veure a quin grup va cadascú, mai tocar-li una nota.
import { requireSession, unauthorized, json } from "../_auth.js";
import { llegeixNivells } from "../_nivells.js";

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
    return json(await llegeixNivells(env.TUTORIA_DB, curs, origen));
  } catch (e) {
    return json({ error: "db", detall: String((e && e.message) || e) }, 500);
  }
}
