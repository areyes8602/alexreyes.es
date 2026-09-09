// Agrupaments i optatives dels alumnes de la tutoria.
//
//   GET  /tutoria/api/grups?grup=2ESO-E   columnes, valors i el grup de mates
//   POST /tutoria/api/grups               crear/renombrar/esborrar columna, desar valors
//
// Els grups de nivell —matemàtiques, anglès— no són columnes d'aquí: venen
// del repartiment dels departaments i van de només lectura, tret de l'aula.
// La resta —optatives, desdoblaments— les crea ell, perquè cada curs són
// unes altres.
import { requireSession, unauthorized, json } from "../_auth.js";
import { llegeixNivells } from "../_nivells.js";

const CURS = "2026-27", GRUP = "2ESO-E";
const SAFE_ID = /^[a-z0-9-]{1,80}$/;

export async function onRequestGet(context) {
  const { request, env } = context;
  if (!(await requireSession(request, env))) return unauthorized();
  if (!env.TUTORIA_DB) return json({ error: "no_db" }, 503);

  const url = new URL(request.url);
  const curs = url.searchParams.get("curs") || CURS;
  const grup = url.searchParams.get("grup") || GRUP;
  const db = env.TUTORIA_DB;

  try {
    const { results: alumnes } = await db.prepare(
      `SELECT id, num, nom, cognoms FROM tutoria_alumnes
        WHERE grup = ? AND curs = ? ORDER BY num`).bind(grup, curs).all();
    const { results: columnes } = await db.prepare(
      `SELECT id, nom, ordre FROM tutoria_agrupaments
        WHERE curs = ? AND grup = ? ORDER BY ordre, creada`).bind(curs, grup).all();
    const { results: valors } = await db.prepare(
      `SELECT v.agrupament, v.alumne, v.valor FROM tutoria_agrupament_alumne v
         JOIN tutoria_agrupaments a ON a.id = v.agrupament
        WHERE a.curs = ? AND a.grup = ?`).bind(curs, grup).all();

    // Els grups de nivell venen d'altres taules. Si encara no s'ha carregat
    // cap repartiment, la pàgina s'ha de poder fer servir igual.
    const nivells = await llegeixNivells(db, curs, grup);

    return json({ alumnes, columnes, valors, ...nivells });
  } catch (e) {
    return json({ error: "db", detall: String(e && e.message || e) }, 500);
  }
}

export async function onRequestPost(context) {
  const { request, env } = context;
  if (!(await requireSession(request, env))) return unauthorized();
  if (!env.TUTORIA_DB) return json({ error: "no_db" }, 503);

  let body;
  try { body = await request.json(); } catch (e) { return json({ error: "bad_json" }, 400); }
  const db = env.TUTORIA_DB;
  const curs = (body.curs || CURS).toString();
  const grup = (body.grup || GRUP).toString();
  const ara = new Date().toISOString();

  try {
    switch (body.accio) {
      case "columna": {
        const nom = (body.nom || "").toString().trim().slice(0, 60);
        if (!nom) return json({ error: "falta_nom" }, 400);
        if (body.id) {
          if (!SAFE_ID.test(body.id)) return json({ error: "bad_id" }, 400);
          const r = await db.prepare(`UPDATE tutoria_agrupaments SET nom = ? WHERE id = ?`)
            .bind(nom, body.id).run();
          if (!r.meta || r.meta.changes === 0) return json({ error: "not_found" }, 404);
          return json({ ok: true, id: body.id });
        }
        // L'ordre el marca el segon de creació, però l'identificador porta
        // a més una cua a l'atzar: dues columnes fetes dins del mateix segon
        // xocaven de clau primària i la segona petava.
        const seg = Math.floor(Date.now() / 1000);
        const cua = Math.random().toString(36).slice(2, 6);
        const id = `${curs.replace("-", "")}-${grup.toLowerCase().replace(/[^a-z0-9]+/g, "")}-${seg}${cua}`;
        if (!SAFE_ID.test(id)) return json({ error: "bad_id" }, 400);
        await db.prepare(
          `INSERT INTO tutoria_agrupaments (id, curs, grup, nom, ordre, creada)
                VALUES (?, ?, ?, ?, ?, ?)`).bind(id, curs, grup, nom, seg, ara).run();
        return json({ ok: true, id });
      }

      case "esborra-columna": {
        if (!SAFE_ID.test(body.id || "")) return json({ error: "bad_id" }, 400);
        // Primer els valors: si es quedessin, tornarien a sortir amb una
        // columna nova que reutilitzés l'identificador.
        await db.prepare(`DELETE FROM tutoria_agrupament_alumne WHERE agrupament = ?`)
          .bind(body.id).run();
        await db.prepare(`DELETE FROM tutoria_agrupaments WHERE id = ?`).bind(body.id).run();
        return json({ ok: true });
      }

      // Els valors van tots junts: s'omple la columna sencera i es desa un
      // cop, que anar guardant casella a casella són cent peticions.
      case "valors": {
        const llista = Array.isArray(body.valors) ? body.valors.slice(0, 2000) : [];
        let desats = 0, esborrats = 0;
        for (const v of llista) {
          if (!SAFE_ID.test(v.columna || "") || !SAFE_ID.test(v.alumne || "")) continue;
          const t = (v.valor ?? "").toString().trim().slice(0, 80);
          if (t === "") {
            await db.prepare(
              `DELETE FROM tutoria_agrupament_alumne WHERE agrupament = ? AND alumne = ?`)
              .bind(v.columna, v.alumne).run();
            esborrats++;
          } else {
            await db.prepare(
              `INSERT INTO tutoria_agrupament_alumne (agrupament, alumne, valor, updated_at)
                    VALUES (?, ?, ?, ?)
               ON CONFLICT(agrupament, alumne) DO UPDATE SET
                    valor = excluded.valor, updated_at = excluded.updated_at`)
              .bind(v.columna, v.alumne, t, ara).run();
            desats++;
          }
        }
        return json({ ok: true, desats, esborrats });
      }

      // L'aula d'un grup d'una altra matèria. El professor i el nivell no
      // es toquen des d'aquí: els reparteix el departament. La de mates
      // tampoc, que aquella es posa a /mates-2eso/ i és la mateixa taula que
      // el quadern de notes.
      case "materia-aula": {
        const materia = (body.materia || "").toString().trim().slice(0, 40);
        const gr = (body.grup_nivell || "").toString().trim().slice(0, 80);
        if (!materia || !gr) return json({ error: "falta_grup" }, 400);
        const aula = (body.aula || "").toString().trim().slice(0, 60);
        const r = await db.prepare(
          `UPDATE tutoria_materia_grups SET aula = ?, updated_at = ?
            WHERE curs = ? AND materia = ? AND grup = ?`)
          .bind(aula || null, ara, curs, materia, gr).run();
        if (!r.meta || r.meta.changes === 0) return json({ error: "not_found" }, 404);
        return json({ ok: true });
      }

      default:
        return json({ error: "accio_desconeguda" }, 400);
    }
  } catch (e) {
    return json({ error: "db", detall: String(e && e.message || e) }, 500);
  }
}
