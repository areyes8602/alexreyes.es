// Prova de normes de convivència — endpoint PÚBLIC.
//
//   GET  /api/normes?codi=XXXX   ¿existe la sesión y está abierta?
//   POST /api/normes             corrige y guarda una entrega
//
// Este es el único punto de todo el sitio donde algo público escribe en la
// base de datos de tutoría, así que las reglas son estrictas:
//
//   · Solo escribe. No hay ningún GET que devuelva respuestas de nadie:
//     los resultados se leen desde /tutoria/, detrás del gate.
//   · La corrección se hace AQUÍ. La clave nunca llega al navegador; si
//     estuviera en el HTML la prueba no valdría nada.
//   · La corrección pregunta a pregunta solo vuelve al alumno si el profesor
//     la ha abierto para esa sesión. Si no, devolver el detalle al instante
//     convertiría una entrega con nombre inventado en la clave completa.
//   · Sin código de sesión válido y abierto no se acepta nada. El código lo
//     crea el profesor desde /tutoria/normes/ y lo escribe en la pizarra:
//     eso mantiene fuera cualquier envío que no venga de clase.
//   · Todo lo que llega del alumno se valida y se recorta antes de tocar la
//     base de datos.
import { CLAU, VERSIO, TOTAL } from "./_normes-clau.js";

const GRUPS = ["2n ESO A", "2n ESO B", "2n ESO C", "2n ESO D", "2n ESO E"];
const CODI_RE = /^[A-Z0-9]{4,10}$/;
const MAX_NOM = 80;

function json(data, status = 200) {
  return new Response(JSON.stringify(data), {
    status,
    headers: {
      "content-type": "application/json; charset=utf-8",
      "cache-control": "no-store",
      "x-robots-tag": "noindex, nofollow",
    },
  });
}

async function sessio(env, codi) {
  return env.TUTORIA_DB
    .prepare(`SELECT codi, nom, oberta, correccio FROM normes_sessions WHERE codi = ?`)
    .bind(codi).first();
}

export async function onRequestGet(context) {
  const { request, env } = context;
  if (!env.TUTORIA_DB) return json({ error: "no_db" }, 503);

  const codi = (new URL(request.url).searchParams.get("codi") || "").toUpperCase();
  if (!CODI_RE.test(codi)) return json({ error: "no_existeix" }, 404);

  try {
    const s = await sessio(env, codi);
    if (!s) return json({ error: "no_existeix" }, 404);
    if (!s.oberta) return json({ error: "tancada" }, 403);
    // Solo el nombre de la prueba: nada de resultados, ni recuento.
    return json({ ok: true, sessio: { codi: s.codi, nom: s.nom }, versio: VERSIO });
  } catch (e) {
    return json({ error: "db", detall: String((e && e.message) || e) }, 500);
  }
}

export async function onRequestPost(context) {
  const { request, env } = context;
  if (!env.TUTORIA_DB) return json({ error: "no_db" }, 503);

  let body;
  try { body = await request.json(); } catch (e) { return json({ error: "bad_json" }, 400); }

  const codi = (body.codi || "").toString().trim().toUpperCase();
  if (!CODI_RE.test(codi)) return json({ error: "no_existeix" }, 404);

  const nom = (body.nom || "").toString().trim().replace(/\s+/g, " ").slice(0, MAX_NOM);
  if (nom.length < 3) return json({ error: "falta_nom" }, 400);

  const grup = (body.grup || "").toString();
  if (!GRUPS.includes(grup)) return json({ error: "grup_invalid" }, 400);

  const rebudes = body.respostes;
  if (!rebudes || typeof rebudes !== "object" || Array.isArray(rebudes)) {
    return json({ error: "bad_respostes" }, 400);
  }

  try {
    const s = await sessio(env, codi);
    if (!s) return json({ error: "no_existeix" }, 404);
    if (!s.oberta) return json({ error: "tancada" }, 403);

    // ─── Corrección ───────────────────────────────────────────────
    // Se recorre la CLAVE, no lo que manda el alumno: así ni sobran
    // preguntas inventadas ni faltan las que no ha contestado.
    const detall = [];
    let encerts = 0;
    for (const id of Object.keys(CLAU)) {
      const bona = CLAU[id].c;
      const crua = rebudes[id];
      const teva = Number.isInteger(crua) && crua >= 0 && crua <= 9 ? crua : null;
      const ok = teva === bona;
      if (ok) encerts++;
      detall.push({ id, ok, teva, correcta: bona, norma: CLAU[id].norma });
    }
    const total = TOTAL;
    const nota = Math.round((10 * encerts / total) * 100) / 100;

    // Se guardan todos los intentos. El de referencia es el primero, y el
    // panel enseña cuántos lleva cada uno: repetir la prueba se ve.
    const previs = await env.TUTORIA_DB
      .prepare(`SELECT COUNT(*) AS n FROM normes_respostes
                 WHERE codi = ? AND lower(nom) = lower(?) AND grup = ?`)
      .bind(codi, nom, grup).first();
    const intent = ((previs && previs.n) || 0) + 1;

    await env.TUTORIA_DB.prepare(
      `INSERT INTO normes_respostes
         (codi, nom, grup, versio, respostes, encerts, total, nota, intent, enviada)
       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)`
    ).bind(
      codi, nom, grup, VERSIO,
      JSON.stringify(detall.reduce((a, d) => (a[d.id] = d.teva, a), {})),
      encerts, total, nota, intent, new Date().toISOString()
    ).run();

    // La correcció detallada només si el professor l'ha obert. Mentre la prova
    // s'està fent, l'alumne rep la nota i prou: veure quines ha fallat convertiria
    // una entrega amb nom fals en la clau sencera de la prova.
    return s.correccio
      ? json({ ok: true, nota, encerts, total, intent, correccio: true, detall })
      : json({ ok: true, nota, encerts, total, intent, correccio: false });
  } catch (e) {
    return json({ error: "db", detall: String((e && e.message) || e) }, 500);
  }
}
