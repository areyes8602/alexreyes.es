// Matemàtiques de 2n d'ESO: grups de nivell i quadern de notes.
//
//   GET  /mates-2eso/api/quadern?nivell=Mig 3   el grup, els seus alumnes i les notes
//   GET  /mates-2eso/api/quadern?grups=1        els sis grups (nivell, professor, aula)
//   POST /mates-2eso/api/quadern                desar aula, activitats i notes
//
// Viu a la zona de mates, no a la de tutoria: les notes són de l'assignatura.
// La tutoria només consulta a quin grup va cada alumne, i ho fa pel seu propi
// endpoint de només lectura (functions/tutoria/api/mates.js): així una sessió
// de tutoria no pot escriure cap nota.
import { requireSession, unauthorized, json } from "../_auth.js";

const CURS = "2026-27";
const SAFE_ID = /^[a-z0-9-]{1,80}$/;

export async function onRequestGet(context) {
  const { request, env } = context;
  if (!(await requireSession(request, env))) return unauthorized();
  if (!env.TUTORIA_DB) return json({ error: "no_db" }, 503);

  const url = new URL(request.url);
  const curs = url.searchParams.get("curs") || CURS;
  const db = env.TUTORIA_DB;

  try {
    // Els sis grups, d'Alt a Baix. També és el que mira la fitxa de tutoria
    // per saber a quina aula es fan les mates.
    if (url.searchParams.get("grups")) {
      const { results } = await db.prepare(
        `SELECT nivell, professor, aula FROM mates_grups
          WHERE curs = ? ORDER BY ordre, nivell`).bind(curs).all();
      return json({ grups: results });
    }

    const nivell = url.searchParams.get("nivell");
    if (!nivell) return json({ error: "falta_nivell" }, 400);

    const grup = await db.prepare(
      `SELECT nivell, professor, aula FROM mates_grups WHERE curs = ? AND nivell = ?`)
      .bind(curs, nivell).first();
    if (!grup) return json({ error: "not_found" }, 404);

    const { results: alumnes } = await db.prepare(
      `SELECT id, cognoms, nom, grup_origen FROM mates_alumnes
        WHERE curs = ? AND nivell = ? ORDER BY cognoms, nom`).bind(curs, nivell).all();
    const { results: activitats } = await db.prepare(
      `SELECT id, nom, data, pes, ordre FROM mates_activitats
        WHERE curs = ? AND nivell = ? ORDER BY ordre, creada`).bind(curs, nivell).all();
    // Només les notes d'aquest grup: la clau de mates_notes és global.
    const { results: notes } = await db.prepare(
      `SELECT n.activitat, n.alumne, n.nota FROM mates_notes n
         JOIN mates_activitats a ON a.id = n.activitat
        WHERE a.curs = ? AND a.nivell = ?`).bind(curs, nivell).all();

    return json({ grup, alumnes, activitats, notes });
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
  const ara = new Date().toISOString();
  const txt = (v, n) => (v ?? "").toString().slice(0, n);

  try {
    switch (body.accio) {
      // L'aula de cada grup: no ve del centre, la va posant ell.
      case "aula": {
        const r = await db.prepare(
          `UPDATE mates_grups SET aula = ?, updated_at = ? WHERE curs = ? AND nivell = ?`)
          .bind(txt(body.aula, 60), ara, curs, txt(body.nivell, 40)).run();
        if (!r.meta || r.meta.changes === 0) return json({ error: "not_found" }, 404);
        return json({ ok: true });
      }

      // Una columna nova del quadern.
      case "activitat": {
        const nom = txt(body.nom, 80).trim();
        if (!nom) return json({ error: "falta_nom" }, 400);
        const nivell = txt(body.nivell, 40);
        // El pes és el percentatge de la nota final que val la columna.
        const pes = Math.min(100, Math.max(0, Number(body.pes) || 0));
        const data = /^\d{4}-\d{2}-\d{2}$/.test(body.data || "") ? body.data : null;
        if (body.id) {
          if (!SAFE_ID.test(body.id)) return json({ error: "bad_id" }, 400);
          const r = await db.prepare(
            `UPDATE mates_activitats SET nom = ?, data = ?, pes = ? WHERE id = ?`)
            .bind(nom, data, pes, body.id).run();
          if (!r.meta || r.meta.changes === 0) return json({ error: "not_found" }, 404);
          return json({ ok: true, id: body.id });
        }
        // L'ordre el marca l'hora de creació: les columnes noves van al final.
        // L'identificador porta a més una cua a l'atzar, que dues activitats
        // fetes dins del mateix segon xocaven de clau primària.
        const seg = Math.floor(Date.now() / 1000);
        const cua = Math.random().toString(36).slice(2, 6);
        const id = `${curs.replace("-", "")}-${nivell.toLowerCase().replace(/[^a-z0-9]+/g, "")}-${seg}${cua}`;
        if (!SAFE_ID.test(id)) return json({ error: "bad_id" }, 400);
        await db.prepare(
          `INSERT INTO mates_activitats (id, curs, nivell, nom, data, pes, ordre, creada)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)`)
          .bind(id, curs, nivell, nom, data, pes, seg, ara).run();
        return json({ ok: true, id });
      }

      case "esborra-activitat": {
        if (!SAFE_ID.test(body.id || "")) return json({ error: "bad_id" }, 400);
        // Primer les notes: si es quedessin, tornarien a sortir amb una
        // activitat nova que reutilitzés l'identificador.
        await db.prepare(`DELETE FROM mates_notes WHERE activitat = ?`).bind(body.id).run();
        await db.prepare(`DELETE FROM mates_activitats WHERE id = ?`).bind(body.id).run();
        return json({ ok: true });
      }

      // Les notes van totes juntes: es tecleja la columna sencera i es desa
      // un cop, que anar guardant casella a casella són cent peticions.
      case "notes": {
        const notes = Array.isArray(body.notes) ? body.notes.slice(0, 2000) : [];
        let desades = 0, esborrades = 0;
        for (const n of notes) {
          if (!SAFE_ID.test(n.activitat || "") || !SAFE_ID.test(n.alumne || "")) continue;
          const v = txt(n.nota, 12).trim();
          if (v === "") {
            await db.prepare(`DELETE FROM mates_notes WHERE activitat = ? AND alumne = ?`)
              .bind(n.activitat, n.alumne).run();
            esborrades++;
          } else {
            await db.prepare(
              `INSERT INTO mates_notes (activitat, alumne, nota, updated_at)
                    VALUES (?, ?, ?, ?)
               ON CONFLICT(activitat, alumne) DO UPDATE SET
                    nota = excluded.nota, updated_at = excluded.updated_at`)
              .bind(n.activitat, n.alumne, v, ara).run();
            desades++;
          }
        }
        return json({ ok: true, desades, esborrades });
      }

      default:
        return json({ error: "accio_desconeguda" }, 400);
    }
  } catch (e) {
    return json({ error: "db", detall: String(e && e.message || e) }, 500);
  }
}
