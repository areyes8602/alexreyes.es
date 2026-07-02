// GET /panel/api/digest — resumen del día para las notificaciones push.
// Lo llama el service worker al recibir un push (con la cookie de sesión).
// Lee el estado (state:<user>) y la caché de agenda (cm_agenda_cache_v1) de KV.
import { verifyToken, getCookie } from "../_auth.js";

function json(data, status = 200) {
  return new Response(JSON.stringify(data), {
    status, headers: { "content-type": "application/json; charset=utf-8", "cache-control": "no-store" }
  });
}
function madridNow() {
  const p = new Intl.DateTimeFormat("en-GB", {
    timeZone: "Europe/Madrid", hour12: false, year: "numeric", month: "2-digit",
    day: "2-digit", hour: "2-digit", minute: "2-digit", weekday: "short"
  }).formatToParts(new Date());
  const g = {}; p.forEach(x => g[x.type] = x.value);
  return { date: `${g.year}-${g.month}-${g.day}`, hour: +g.hour, weekday: ["Sun","Mon","Tue","Wed","Thu","Fri","Sat"].indexOf(g.weekday) };
}
function isoWeek(dstr) {
  const d = new Date(dstr + "T00:00:00Z");
  const day = (d.getUTCDay() + 6) % 7; d.setUTCDate(d.getUTCDate() - day + 3);
  const first = new Date(Date.UTC(d.getUTCFullYear(), 0, 4));
  const wk = 1 + Math.round(((d - first) / 86400000 - 3 + ((first.getUTCDay() + 6) % 7)) / 7);
  return d.getUTCFullYear() + "-W" + String(wk).padStart(2, "0");
}

export async function onRequest(context) {
  const { request, env } = context;
  const user = await verifyToken(getCookie(request), env.PANEL_SECRET);
  if (!user) return json({ error: "unauthorized" }, 401);
  if (!env.PANEL_KV) return json({ error: "no_kv" }, 200);

  const now = madridNow();
  let state = null;
  try {
    const raw = await env.PANEL_KV.get("state:" + user);
    if (raw) { const p = JSON.parse(raw); state = p && p.__env === 1 ? p.state : p; }
  } catch (e) {}

  const parts = [];
  if (state) {
    const tasks = (state.tasks || []).filter(t => !t.done && t.due);
    const overdue = tasks.filter(t => t.due < now.date).length;
    const today = tasks.filter(t => t.due === now.date);
    if (overdue) parts.push("⚠️ " + overdue + " vencida" + (overdue === 1 ? "" : "s"));
    if (today.length) parts.push("📌 hoy: " + today.slice(0, 3).map(t => t.text).join(" · ") + (today.length > 3 ? " (+" + (today.length - 3) + ")" : ""));
    const wk = isoWeek(now.date);
    const habits = (state.habits || []).filter(h => {
      const due = h.cadence === "weekly" ? h.day === now.weekday : h.cadence === "weekends" ? (now.weekday === 0 || now.weekday === 6) : false;
      return due && !(h.history && h.history[wk]);
    });
    if (habits.length) parts.push("🔁 " + habits.map(h => h.name).join(" · "));
  }
  // Eventos de hoy que quedan (de la caché de agenda, si existe)
  try {
    const c = await env.PANEL_KV.get("cm_agenda_cache_v1", "json");
    const evs = (c && c.payload && c.payload.events || []).filter(e => {
      if (e.allDay) return String(e.start).slice(0, 10) === now.date;
      return String(e.start).slice(0, 10) === now.date && Date.parse(e.end || e.start) > Date.now();
    });
    if (evs.length) {
      const first = evs[0];
      parts.push("🗓️ " + evs.length + " evento" + (evs.length === 1 ? "" : "s") + (first.allDay ? "" : " · próximo: " + first.summary));
    }
  } catch (e) {}

  const evening = now.hour >= 15;
  const title = evening ? "🌙 Repaso del día" : "☀️ Tu día de un vistazo";
  const body = parts.length ? parts.join("\n") : (evening ? "Todo al día. Cierra la tienda. 🎉" : "Nada urgente hoy. Tu tiempo es propio. 🔬");
  return json({ title, body });
}
