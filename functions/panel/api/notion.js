// GET /panel/api/notion — lee el doctorado desde Notion (API pública).
// Requiere sesión válida y env.NOTION_TOKEN. Degrada si falta el token.
import { verifyToken, getCookie } from "../_auth.js";

// IDs de las bases del doctorado (públicos, no secretos). Se pueden sobreescribir por env.
const TAREAS_DB = "2e8d5bbe-9376-80a5-838b-e914860973e0";
const REUNIONES_DB = "2e8d5bbe-9376-805f-82bf-f27e88375189";
const NV = "2022-06-28";

function json(data, status = 200) {
  return new Response(JSON.stringify(data), {
    status,
    headers: { "content-type": "application/json; charset=utf-8", "cache-control": "no-store" }
  });
}

async function queryDB(token, dbId, body) {
  const r = await fetch(`https://api.notion.com/v1/databases/${dbId}/query`, {
    method: "POST",
    headers: {
      "Authorization": "Bearer " + token,
      "Notion-Version": NV,
      "Content-Type": "application/json"
    },
    body: JSON.stringify(body)
  });
  const j = await r.json().catch(() => ({}));
  if (!r.ok) throw { status: r.status, notion: j };
  return j.results || [];
}

// helpers para leer propiedades con tolerancia
const pTitle = (p) => (p && p.title && p.title.map(t => t.plain_text).join("")) || "";
const pText = (p) => (p && p.rich_text && p.rich_text.map(t => t.plain_text).join("")) || "";
const pSelect = (p) => (p && p.select && p.select.name) || "";
const pMulti = (p) => (p && p.multi_select && p.multi_select.map(o => o.name)) || [];
const pDate = (p) => (p && p.date && p.date.start) || null;

export async function onRequest(context) {
  const { request, env } = context;
  const user = await verifyToken(getCookie(request), env.PANEL_SECRET);
  if (!user) return json({ error: "unauthorized" }, 401);
  if (!env.NOTION_TOKEN) return json({ error: "no_notion" }, 200);

  const tareasDb = env.NOTION_TAREAS_DB || TAREAS_DB;
  const reunionesDb = env.NOTION_REUNIONES_DB || REUNIONES_DB;

  try {
    const [tRows, mRows] = await Promise.all([
      queryDB(env.NOTION_TOKEN, tareasDb, {
        filter: { property: "Estado", select: { does_not_equal: "Hecha" } },
        sorts: [{ property: "Fecha objetivo", direction: "ascending" }],
        page_size: 50
      }),
      queryDB(env.NOTION_TOKEN, reunionesDb, {
        filter: { property: "Estado", select: { equals: "Planificada" } },
        sorts: [{ property: "Fecha", direction: "ascending" }],
        page_size: 8
      })
    ]);

    const tasks = tRows.map(pg => {
      const p = pg.properties || {};
      return {
        title: pTitle(p["Nombre"]),
        estado: pSelect(p["Estado"]),
        prioridad: pSelect(p["Prioridad"]),
        tipo: pSelect(p["Tipo"]),
        tiempo: pSelect(p["Tiempo estimado"]),
        fecha: pDate(p["Fecha objetivo"]),
        url: pg.url
      };
    });

    const meetings = mRows.map(pg => {
      const p = pg.properties || {};
      return {
        title: pTitle(p["Nombre"]),
        fecha: pDate(p["Fecha"]),
        tipo: pSelect(p["Tipo"]),
        personas: pMulti(p["Personas"]),
        objetivo: pMulti(p["Objetivo"]),
        preguntas: pText(p["Preguntas a realizar"]),
        preparada: !!(p["Preparada"] && p["Preparada"].checkbox),
        url: pg.url
      };
    });

    return json({ tasks, meetings, fetchedAt: Date.now() });
  } catch (e) {
    const status = (e && e.status) || 500;
    const msg = status === 404 ? "not_shared" : "notion_error";
    return json({ error: msg, status }, 200);
  }
}
