// Prova de normes — lectura y gestión, detrás del gate de /tutoria/.
//
//   GET  /tutoria/api/normes                    sesiones
//   GET  /tutoria/api/normes?codi=…             resultados + estadísticas
//   GET  /tutoria/api/normes?codi=…&csv=1       exportación
//   POST /tutoria/api/normes                    crear sesión
//   POST /tutoria/api/normes?obre|tanca=CODI    abrir / cerrar
//   POST /tutoria/api/normes?correccio=CODI:0|1 enseñar o no la corrección
//   POST /tutoria/api/normes?esborra=id         borrar una entrega suelta
//
// Las estadísticas se calculan aquí y no en el navegador: la página solo
// recibe números agregados y la tabla de alumnos, sin las respuestas crudas.
import { requireSession, unauthorized, json } from "../_auth.js";
import { CLAU, VERSIO, TOTAL } from "../../api/_normes-clau.js";

const CODI_RE = /^[A-Z0-9]{4,10}$/;
// Sin vocales ni caracteres que se confundan al leerlos de la pizarra
// (0/O, 1/I/L). Cuatro dígitos de este alfabeto son ~1,7 millones de
// combinaciones: nadie lo acierta a ciegas.
const ALFABET = "2345679BCDFGHJKMNPQRSTVWXYZ";

function nouCodi() {
  const b = crypto.getRandomValues(new Uint8Array(4));
  return Array.from(b, x => ALFABET[x % ALFABET.length]).join("");
}

function mediana(xs) {
  if (!xs.length) return 0;
  const s = xs.slice().sort((a, b) => a - b), m = s.length >> 1;
  return s.length % 2 ? s[m] : (s[m - 1] + s[m]) / 2;
}

export async function onRequestGet(context) {
  const { request, env } = context;
  if (!(await requireSession(request, env))) return unauthorized();
  if (!env.TUTORIA_DB) return json({ error: "no_db", sessions: [] }, 503);

  const url = new URL(request.url);
  const codi = (url.searchParams.get("codi") || "").toUpperCase();

  try {
    // ─── Índice de sesiones ──────────────────────────────────────
    if (!codi) {
      const { results } = await env.TUTORIA_DB.prepare(
        `SELECT s.codi, s.nom, s.curs, s.oberta, s.creada, s.tancada,
                (SELECT COUNT(*) FROM normes_respostes r
                  WHERE r.codi = s.codi AND r.intent = 1) AS entregues
           FROM normes_sessions s ORDER BY s.creada DESC`).all();
      return json({ sessions: results || [], versio: VERSIO, total: TOTAL });
    }

    if (!CODI_RE.test(codi)) return json({ error: "bad_codi" }, 400);
    const sess = await env.TUTORIA_DB
      .prepare(`SELECT * FROM normes_sessions WHERE codi = ?`).bind(codi).first();
    if (!sess) return json({ error: "not_found" }, 404);

    const { results } = await env.TUTORIA_DB.prepare(
      `SELECT id, nom, grup, respostes, encerts, total, nota, intent, enviada
         FROM normes_respostes WHERE codi = ? ORDER BY enviada`).bind(codi).all();
    const files = results || [];

    // El primer intento es el que cuenta; los demás solo se señalan.
    const oficials = files.filter(r => r.intent === 1);
    const repeticions = {};
    files.forEach(r => {
      if (r.intent > 1) {
        const k = r.grup + "·" + r.nom.toLowerCase();
        repeticions[k] = Math.max(repeticions[k] || 1, r.intent);
      }
    });

    if (url.searchParams.get("csv")) {
      const cap = "nom;grup;encerts;total;nota;intents;enviada\n";
      const cos = oficials.map(r =>
        [r.nom, r.grup, r.encerts, r.total, String(r.nota).replace(".", ","),
         repeticions[r.grup + "·" + r.nom.toLowerCase()] || 1, r.enviada]
          .map(c => `"${String(c).replace(/"/g, '""')}"`).join(";")).join("\n");
      return new Response(cap + cos, {
        headers: {
          "content-type": "text/csv; charset=utf-8",
          "content-disposition": `attachment; filename="normes-${codi}.csv"`,
          "cache-control": "no-store", "x-robots-tag": "noindex, nofollow",
        },
      });
    }

    // ─── Estadísticas ────────────────────────────────────────────
    const notes = oficials.map(r => r.nota || 0);
    const n = notes.length;
    const mitjana = n ? notes.reduce((a, b) => a + b, 0) / n : 0;

    // Histograma por franjas de 1 punto: [0,1) … [9,10]
    const histograma = Array.from({ length: 10 }, () => 0);
    notes.forEach(x => { histograma[Math.min(9, Math.floor(x))]++; });

    // Acierto por pregunta. Se recorre la CLAVE para que salgan también las
    // que nadie ha respondido, y no queden fuera del recuento.
    const perPregunta = Object.keys(CLAU).map(id => ({ id, encerts: 0, respostes: 0 }));
    const idx = {};
    perPregunta.forEach((p, i) => { idx[p.id] = i; });
    oficials.forEach(r => {
      let res = {};
      try { res = JSON.parse(r.respostes || "{}"); } catch (e) { /* fila malmesa */ }
      for (const id of Object.keys(CLAU)) {
        const p = perPregunta[idx[id]];
        const tria = res[id];
        if (tria === null || tria === undefined) continue;
        p.respostes++;
        if (tria === CLAU[id].c) p.encerts++;
      }
    });
    perPregunta.forEach(p => {
      p.pct = p.respostes ? Math.round(100 * p.encerts / p.respostes) : null;
    });

    // Por grupo
    const grups = {};
    oficials.forEach(r => {
      (grups[r.grup] = grups[r.grup] || []).push(r.nota || 0);
    });
    const perGrup = Object.keys(grups).sort().map(g => ({
      grup: g, n: grups[g].length,
      mitjana: Math.round((grups[g].reduce((a, b) => a + b, 0) / grups[g].length) * 100) / 100,
      aprovats: grups[g].filter(x => x >= 5).length,
    }));

    return json({
      sessio: { codi: sess.codi, nom: sess.nom, curs: sess.curs,
                oberta: sess.oberta, correccio: sess.correccio,
                creada: sess.creada, tancada: sess.tancada },
      versio: VERSIO, total: TOTAL,
      resum: {
        entregues: n,
        mitjana: Math.round(mitjana * 100) / 100,
        mediana: Math.round(mediana(notes) * 100) / 100,
        aprovats: notes.filter(x => x >= 5).length,
        maxima: n ? Math.max(...notes) : 0,
        minima: n ? Math.min(...notes) : 0,
      },
      histograma, perPregunta, perGrup,
      alumnes: oficials.map(r => ({
        id: r.id, nom: r.nom, grup: r.grup, encerts: r.encerts,
        total: r.total, nota: r.nota, enviada: r.enviada,
        intents: repeticions[r.grup + "·" + r.nom.toLowerCase()] || 1,
      })),
    });
  } catch (e) {
    return json({ error: "db", detall: String((e && e.message) || e) }, 500);
  }
}

export async function onRequestPost(context) {
  const { request, env } = context;
  if (!(await requireSession(request, env))) return unauthorized();
  if (!env.TUTORIA_DB) return json({ error: "no_db" }, 503);

  const url = new URL(request.url);
  const ara = new Date().toISOString();

  try {
    for (const [param, oberta] of [["obre", 1], ["tanca", 0]]) {
      const c = (url.searchParams.get(param) || "").toUpperCase();
      if (!c) continue;
      if (!CODI_RE.test(c)) return json({ error: "bad_codi" }, 400);
      await env.TUTORIA_DB
        .prepare(`UPDATE normes_sessions SET oberta = ?, tancada = ? WHERE codi = ?`)
        .bind(oberta, oberta ? null : ara, c).run();
      return json({ ok: true, codi: c, oberta });
    }

    const corr = url.searchParams.get("correccio");
    if (corr) {
      const [c, val] = corr.split(":");
      if (!CODI_RE.test((c || "").toUpperCase())) return json({ error: "bad_codi" }, 400);
      const on = val === "1" ? 1 : 0;
      await env.TUTORIA_DB
        .prepare(`UPDATE normes_sessions SET correccio = ? WHERE codi = ?`)
        .bind(on, c.toUpperCase()).run();
      return json({ ok: true, correccio: on });
    }

    const esborra = url.searchParams.get("esborra");
    if (esborra) {
      if (!/^\d{1,12}$/.test(esborra)) return json({ error: "bad_id" }, 400);
      await env.TUTORIA_DB.prepare(`DELETE FROM normes_respostes WHERE id = ?`)
        .bind(Number(esborra)).run();
      return json({ ok: true });
    }

    let body;
    try { body = await request.json(); } catch (e) { return json({ error: "bad_json" }, 400); }
    const nom = (body.nom || "").toString().trim().slice(0, 120) || "Prova de normes";

    // Reintenta si el código sorteado ya existe.
    for (let i = 0; i < 6; i++) {
      const codi = nouCodi();
      const hi = await env.TUTORIA_DB
        .prepare(`SELECT codi FROM normes_sessions WHERE codi = ?`).bind(codi).first();
      if (hi) continue;
      await env.TUTORIA_DB.prepare(
        `INSERT INTO normes_sessions (codi, nom, curs, oberta, creada)
         VALUES (?, ?, ?, 1, ?)`
      ).bind(codi, nom, (body.curs || "2026-27").toString(), ara).run();
      return json({ ok: true, codi, nom, oberta: 1, creada: ara });
    }
    return json({ error: "no_codi" }, 500);
  } catch (e) {
    return json({ error: "db", detall: String((e && e.message) || e) }, 500);
  }
}
