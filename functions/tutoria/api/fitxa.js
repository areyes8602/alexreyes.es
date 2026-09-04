// GET  /tutoria/api/fitxa?id=…  — ficha completa de un alumno.
// POST /tutoria/api/fitxa       — guarda los campos editables.
import { requireSession, unauthorized, json } from "../_auth.js";

// Campos que edita el tutor. La identidad (nombre, nº, grupo, foto) y lo
// académico (notas del curso anterior, pendientes) vienen de los
// importadores y no se tocan desde el navegador: si cambian, se recarga la
// orla o los boletines y así el origen del dato sigue siendo el del centro.
const EDITABLES = {
  naixement: 40, idioma: 120, adreca: 400, telefon: 120, email: 200,
  recull: 600, suport: 4000, contacte: 2000, notes: 20000,
  acords: 4000, extraescolars: 600, carrec: 120,
  tutor_anterior: 120, traspas: 20000, derivacio: 60, derivacio_nota: 2000,
  // Fitxa que omple l'alumne el primer dia de tutoria
  ciutat: 120, escola_primaria: 200,
  situacio_familiar: 200, situacio_amb_qui: 200, situacio_nota: 2000,
  germans_nombre: 40, germans: 600, salut: 2000,
  amics_classe: 600, amics_nivell: 600,
  mat_millor: 400, mat_pitjor: 400, virtuts: 600, millorar: 600,
};
// Casillas: se guardan como 0/1 y no como texto.
const BANDERES = ["pi_contingut", "pi_metodologic", "acollida"];
// Campos de lista, guardados como JSON.
const LLISTES = { familia: 40, entrevistes: 400, incidencies: 400 };

export async function onRequestGet(context) {
  const { request, env } = context;
  if (!(await requireSession(request, env))) return unauthorized();
  if (!env.TUTORIA_DB) return json({ error: "no_db" }, 503);

  const id = new URL(request.url).searchParams.get("id");
  if (!id) return json({ error: "missing_id" }, 400);

  let row;
  try {
    row = await env.TUTORIA_DB
      .prepare(`SELECT * FROM tutoria_alumnes WHERE id = ?`)
      .bind(id)
      .first();
  } catch (e) {
    return json({ error: "db", detall: String(e && e.message || e) }, 500);
  }
  if (!row) return json({ error: "not_found" }, 404);

  // Vecinos por nº de lista, para poder pasar de ficha en ficha sin volver.
  const { results: veins } = await env.TUTORIA_DB
    .prepare(`SELECT id, num, nom, cognoms FROM tutoria_alumnes
               WHERE grup = ? AND curs = ? ORDER BY num`)
    .bind(row.grup, row.curs)
    .all();

  return json({ alumne: row, veins });
}

export async function onRequestPost(context) {
  const { request, env } = context;
  if (!(await requireSession(request, env))) return unauthorized();
  if (!env.TUTORIA_DB) return json({ error: "no_db" }, 503);

  let body;
  try { body = await request.json(); } catch (e) { return json({ error: "bad_json" }, 400); }

  const id = (body.id || "").toString();
  if (!id) return json({ error: "missing_id" }, 400);

  const camps = [], valors = [];
  for (const [camp, max] of Object.entries(EDITABLES)) {
    if (!(camp in body)) continue;
    camps.push(`${camp} = ?`);
    valors.push((body[camp] ?? "").toString().slice(0, max));
  }
  for (const [camp, maxItems] of Object.entries(LLISTES)) {
    if (!(camp in body)) continue;
    const llista = Array.isArray(body[camp]) ? body[camp].slice(0, maxItems) : [];
    camps.push(`${camp} = ?`);
    valors.push(JSON.stringify(llista));
  }
  for (const camp of BANDERES) {
    if (!(camp in body)) continue;
    camps.push(`${camp} = ?`);
    valors.push(body[camp] ? 1 : 0);
  }
  if ("imatge_ok" in body) {
    camps.push("imatge_ok = ?");
    valors.push(body.imatge_ok === null ? null : (body.imatge_ok ? 1 : 0));
  }
  if (!camps.length) return json({ error: "res_a_desar" }, 400);

  camps.push("updated_at = ?");
  valors.push(new Date().toISOString());
  valors.push(id);

  let res;
  try {
    res = await env.TUTORIA_DB
      .prepare(`UPDATE tutoria_alumnes SET ${camps.join(", ")} WHERE id = ?`)
      .bind(...valors)
      .run();
  } catch (e) {
    return json({ error: "db", detall: String(e && e.message || e) }, 500);
  }

  if (!res.meta || res.meta.changes === 0) return json({ error: "not_found" }, 404);
  return json({ ok: true, updated_at: valors[valors.length - 2] });
}
