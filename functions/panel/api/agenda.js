// GET /panel/api/agenda — agenda unificada multi-calendario. (redeploy: aplicar GCAL_IDS)
// Fusiona: N calendarios de Google (cuenta de servicio, GCAL_IDS) + N calendarios ICS
// (Hotmail / Outlook corporativo publicados como .ics, ICS_URLS).
// Ventana fija: desde hace 6h hasta +8 días. El cliente filtra por día.
// Caché en KV (PANEL_KV, 5 min) para abrir rápido; ?fresh=1 la salta.
// Tolerante a fallos: si una fuente cae, devuelve el resto + sources[] con el error.
//
// Variables de entorno (alexreyes-web, Producción):
//   GCAL_SA_EMAIL, GCAL_SA_KEY  — cuenta de servicio (igual que gcal.js)
//   GCAL_IDS  — lista separada por comas: "calId" o "calId::Etiqueta"
//               (fallback: GCAL_ID, y si no, el correo de login)
//   ICS_URLS  — lista separada por comas o saltos de línea: "Etiqueta::https://…/calendar.ics"
//               o solo la URL. (Hotmail: Configuración→Calendario→Calendarios compartidos→Publicar;
//               cole: igual desde Outlook web si el admin lo permite.)
import { verifyToken, getCookie } from "../_auth.js";

const TZ = "Europe/Madrid";      // TZID de los ICS se interpretan como hora de Madrid
const CACHE_KEY = "cm_agenda_cache_v1";
const CACHE_TTL = 300e3;         // 5 min

function json(data, status = 200) {
  return new Response(JSON.stringify(data), {
    status, headers: { "content-type": "application/json; charset=utf-8", "cache-control": "no-store" }
  });
}

/* ---------- Google (cuenta de servicio, igual que gcal.js) ---------- */
function b64urlBytes(buf) {
  const bytes = new Uint8Array(buf); let bin = "";
  for (let i = 0; i < bytes.length; i++) bin += String.fromCharCode(bytes[i]);
  return btoa(bin).replace(/\+/g, "-").replace(/\//g, "_").replace(/=+$/, "");
}
function b64urlStr(s) {
  return btoa(unescape(encodeURIComponent(s))).replace(/\+/g, "-").replace(/\//g, "_").replace(/=+$/, "");
}
function pemToDer(pem) {
  const s = pem.replace(/\\n/g, "\n").replace(/-----[^-]*-----/g, "");
  const body = s.replace(/[^A-Za-z0-9+/=]/g, "");
  const bin = atob(body); const der = new Uint8Array(bin.length);
  for (let i = 0; i < bin.length; i++) der[i] = bin.charCodeAt(i);
  return der.buffer;
}
async function getAccessToken(email, keyPem) {
  const now = Math.floor(Date.now() / 1000);
  const header = b64urlStr(JSON.stringify({ alg: "RS256", typ: "JWT" }));
  const claim = b64urlStr(JSON.stringify({
    iss: email, scope: "https://www.googleapis.com/auth/calendar.readonly",
    aud: "https://oauth2.googleapis.com/token", iat: now, exp: now + 3600
  }));
  const input = header + "." + claim;
  const key = await crypto.subtle.importKey("pkcs8", pemToDer(keyPem),
    { name: "RSASSA-PKCS1-v1_5", hash: "SHA-256" }, false, ["sign"]);
  const sig = await crypto.subtle.sign("RSASSA-PKCS1-v1_5", key, new TextEncoder().encode(input));
  const jwt = input + "." + b64urlBytes(sig);
  const r = await fetch("https://oauth2.googleapis.com/token", {
    method: "POST",
    headers: { "content-type": "application/x-www-form-urlencoded" },
    body: "grant_type=urn:ietf:params:oauth:grant-type:jwt-bearer&assertion=" + encodeURIComponent(jwt)
  });
  const j = await r.json().catch(() => ({}));
  if (!r.ok || !j.access_token) throw new Error("token " + r.status + " " + (j.error_description || j.error || ""));
  return j.access_token;
}
async function fetchGoogle(calId, label, token, timeMin, timeMax) {
  const api = `https://www.googleapis.com/calendar/v3/calendars/${encodeURIComponent(calId)}/events` +
    `?singleEvents=true&orderBy=startTime&maxResults=250` +
    `&timeMin=${encodeURIComponent(timeMin)}&timeMax=${encodeURIComponent(timeMax)}`;
  const r = await fetch(api, { headers: { Authorization: "Bearer " + token } });
  if (r.status === 404) throw new Error("cal_not_found");
  if (r.status === 403) throw new Error("not_shared");
  const j = await r.json().catch(() => ({}));
  if (!r.ok) throw new Error("google " + r.status);
  return (j.items || []).filter(e => e.status !== "cancelled").map(e => ({
    summary: e.summary || "(sin título)",
    start: e.start && (e.start.dateTime || e.start.date),
    end: e.end && (e.end.dateTime || e.end.date),
    allDay: !!(e.start && e.start.date && !e.start.dateTime),
    location: e.location || "",
    cal: label, kind: "google"
  }));
}

/* ---------- ICS (Outlook/Hotmail publicados) ---------- */
// Hora de pared en TZ para un instante UTC (ms) — para calcular el offset.
function wallInTz(ts) {
  const p = new Intl.DateTimeFormat("en-GB", {
    timeZone: TZ, hour12: false, year: "numeric", month: "2-digit",
    day: "2-digit", hour: "2-digit", minute: "2-digit", second: "2-digit"
  }).formatToParts(new Date(ts));
  const g = {}; p.forEach(x => g[x.type] = x.value);
  return Date.UTC(+g.year, +g.month - 1, +g.day, (+g.hour) % 24, +g.minute, +g.second);
}
function madridToUtc(y, mo, d, h, mi, s) {
  const guess = Date.UTC(y, mo - 1, d, h, mi, s);
  return guess - (wallInTz(guess) - guess);
}
// Devuelve {ts, allDay, dateStr}
function parseIcsDate(val, isDateOnly) {
  if (isDateOnly || /^\d{8}$/.test(val)) {
    const y = +val.slice(0, 4), mo = +val.slice(4, 6), d = +val.slice(6, 8);
    return { ts: madridToUtc(y, mo, d, 0, 0, 0), allDay: true, dateStr: `${val.slice(0, 4)}-${val.slice(4, 6)}-${val.slice(6, 8)}` };
  }
  const m = val.match(/^(\d{4})(\d{2})(\d{2})T(\d{2})(\d{2})(\d{2})(Z?)$/);
  if (!m) return null;
  const [, y, mo, d, h, mi, s, z] = m;
  const ts = z ? Date.UTC(+y, +mo - 1, +d, +h, +mi, +s) : madridToUtc(+y, +mo, +d, +h, +mi, +s);
  return { ts, allDay: false };
}
function unfoldIcs(text) {
  return text.replace(/\r\n[ \t]/g, "").replace(/\n[ \t]/g, "").split(/\r?\n/);
}
function icsUnescape(s) {
  return (s || "").replace(/\\n/gi, " · ").replace(/\\([,;\\])/g, "$1");
}
function parseVevents(text) {
  const lines = unfoldIcs(text);
  const evs = []; let cur = null;
  for (const line of lines) {
    if (line === "BEGIN:VEVENT") { cur = { exdates: [] }; continue; }
    if (line === "END:VEVENT") { if (cur) evs.push(cur); cur = null; continue; }
    if (!cur) continue;
    const i = line.indexOf(":"); if (i < 0) continue;
    const left = line.slice(0, i), val = line.slice(i + 1);
    const [prop, ...paramArr] = left.split(";");
    const params = {}; paramArr.forEach(p => { const [k, v] = p.split("="); params[k] = v; });
    const dateOnly = params.VALUE === "DATE";
    switch (prop) {
      case "SUMMARY": cur.summary = icsUnescape(val); break;
      case "LOCATION": cur.location = icsUnescape(val); break;
      case "STATUS": cur.cancelled = /CANCELLED/i.test(val); break;
      case "UID": cur.uid = val; break;
      case "DTSTART": cur.start = parseIcsDate(val, dateOnly); break;
      case "DTEND": cur.end = parseIcsDate(val, dateOnly); break;
      case "RRULE": cur.rrule = val; break;
      case "RECURRENCE-ID": { const p = parseIcsDate(val, dateOnly); if (p) cur.recurrenceId = p.ts; break; }
      case "EXDATE": val.split(",").forEach(v => { const p = parseIcsDate(v.trim(), dateOnly); if (p) cur.exdates.push(p.ts); }); break;
    }
  }
  return evs;
}
const ICAL_DAYS = { SU: 0, MO: 1, TU: 2, WE: 3, TH: 4, FR: 5, SA: 6 };
// Expansión limitada de RRULE (DAILY/WEEKLY/MONTHLY/YEARLY, INTERVAL, UNTIL, COUNT, BYDAY semanal).
function expandRrule(ev, winStart, winEnd) {
  const rule = {}; ev.rrule.split(";").forEach(kv => { const [k, v] = kv.split("="); rule[k] = v; });
  const freq = rule.FREQ, interval = Math.max(1, +(rule.INTERVAL || 1));
  const count = rule.COUNT ? +rule.COUNT : Infinity;
  let until = Infinity;
  if (rule.UNTIL) { const u = parseIcsDate(rule.UNTIL, /^\d{8}$/.test(rule.UNTIL)); if (u) until = u.ts + (u.allDay ? 86400e3 : 0); }
  const dur = ev.end ? ev.end.ts - ev.start.ts : 3600e3;
  const out = []; let made = 0;
  const push = (ts) => {
    if (ts >= until || made >= count) return false;
    made++;
    if (ts + dur > winStart && ts < winEnd && !ev.exdates.some(x => Math.abs(x - ts) < 1000)) out.push(ts);
    return true;
  };
  const DAY = 86400e3;
  if (freq === "DAILY") {
    for (let ts = ev.start.ts, i = 0; ts < winEnd && i < 1000; ts += interval * DAY, i++) if (!push(ts)) break;
  } else if (freq === "WEEKLY") {
    const bydays = (rule.BYDAY ? rule.BYDAY.split(",").map(d => ICAL_DAYS[d.slice(-2)]) : [new Date(ev.start.ts).getUTCDay()]).filter(d => d !== undefined);
    // Semana base = lunes de la semana de DTSTART (en UTC, aproximación suficiente).
    const d0 = new Date(ev.start.ts);
    const weekStart = ev.start.ts - ((d0.getUTCDay() + 6) % 7) * DAY;
    const tod = ev.start.ts - (weekStart + ((d0.getUTCDay() + 6) % 7) * DAY); // hora del día
    outer:
    for (let w = weekStart, i = 0; w < winEnd && i < 400; w += interval * 7 * DAY, i++) {
      for (const bd of bydays.slice().sort((a, b) => ((a + 6) % 7) - ((b + 6) % 7))) {
        const ts = w + ((bd + 6) % 7) * DAY + tod;
        if (ts < ev.start.ts) continue;
        if (!push(ts)) break outer;
      }
    }
  } else if (freq === "MONTHLY" || freq === "YEARLY") {
    const s = new Date(ev.start.ts);
    for (let i = 0; i < 400; i++) {
      const k = i * interval;
      const dt = freq === "MONTHLY"
        ? Date.UTC(s.getUTCFullYear(), s.getUTCMonth() + k, +(rule.BYMONTHDAY || s.getUTCDate()), s.getUTCHours(), s.getUTCMinutes(), s.getUTCSeconds())
        : Date.UTC(s.getUTCFullYear() + k, s.getUTCMonth(), s.getUTCDate(), s.getUTCHours(), s.getUTCMinutes(), s.getUTCSeconds());
      if (dt >= winEnd) break;
      if (!push(dt)) break;
    }
  }
  return out.map(ts => ({ start: ts, end: ts + dur }));
}
async function fetchIcs(url, label, timeMinIso, timeMaxIso) {
  const winStart = Date.parse(timeMinIso), winEnd = Date.parse(timeMaxIso);
  const r = await fetch(url, { headers: { "user-agent": "alexreyes-panel/1.0" }, redirect: "follow" });
  if (!r.ok) throw new Error("ics " + r.status);
  const text = await r.text();
  if (!/BEGIN:VCALENDAR/.test(text)) throw new Error("ics_invalid");
  const raw = parseVevents(text);
  // Overrides de instancias recurrentes (RECURRENCE-ID) por uid+ts
  const overrides = new Set();
  raw.forEach(e => { if (e.recurrenceId && e.uid) overrides.add(e.uid + "@" + e.recurrenceId); });
  const out = [];
  for (const e of raw) {
    if (!e.start || e.cancelled) continue;
    const base = {
      summary: e.summary || "(sin título)", location: e.location || "",
      allDay: !!e.start.allDay, cal: label, kind: "ics"
    };
    if (e.rrule && !e.recurrenceId) {
      for (const inst of expandRrule(e, winStart, winEnd)) {
        if (e.uid && overrides.has(e.uid + "@" + inst.start)) continue; // instancia movida: la trae su override
        out.push({ ...base, start: new Date(inst.start).toISOString(), end: new Date(inst.end).toISOString() });
      }
    } else {
      const endTs = e.end ? e.end.ts : e.start.ts + (e.start.allDay ? 86400e3 : 3600e3);
      if (endTs <= winStart || e.start.ts >= winEnd) continue;
      out.push({
        ...base,
        start: e.start.allDay ? e.start.dateStr : new Date(e.start.ts).toISOString(),
        end: e.end && e.end.allDay ? e.end.dateStr : new Date(endTs).toISOString()
      });
    }
  }
  return out;
}

/* ---------- Config de fuentes ---------- */
function parseSources(env, user) {
  const google = [];
  const idsRaw = env.GCAL_IDS || env.GCAL_ID || user || "";
  idsRaw.split(",").map(s => s.trim()).filter(Boolean).forEach(entry => {
    const [id, label] = entry.split("::").map(s => s.trim());
    google.push({ id, label: label || (id.includes("@group.calendar") ? "Google" : id.split("@")[0]) });
  });
  const ics = [];
  (env.ICS_URLS || "").split(/[\n,]/).map(s => s.trim()).filter(Boolean).forEach(entry => {
    const i = entry.indexOf("::");
    if (i > 0 && !/^https?:/i.test(entry)) ics.push({ label: entry.slice(0, i).trim(), url: entry.slice(i + 2).trim() });
    else ics.push({ label: "Outlook", url: entry });
  });
  return { google, ics };
}

/* ---------- Handler ---------- */
export async function onRequest(context) {
  const { request, env } = context;
  const user = await verifyToken(getCookie(request), env.PANEL_SECRET);
  if (!user) return json({ error: "unauthorized" }, 401);

  const url = new URL(request.url);
  const fresh = url.searchParams.get("fresh") === "1";

  // Caché KV
  if (!fresh && env.PANEL_KV) {
    try {
      const c = await env.PANEL_KV.get(CACHE_KEY, "json");
      if (c && Date.now() - c.ts < CACHE_TTL) return json({ ...c.payload, cached: true });
    } catch (_) {}
  }

  const now = Date.now();
  const timeMin = new Date(now - 6 * 3600e3).toISOString();
  const timeMax = new Date(now + 8 * 86400e3).toISOString();

  const { google, ics } = parseSources(env, user);
  const sources = []; let events = [];
  const jobs = [];

  if (google.length && env.GCAL_SA_EMAIL && env.GCAL_SA_KEY) {
    jobs.push((async () => {
      let token;
      try { token = await getAccessToken(env.GCAL_SA_EMAIL, env.GCAL_SA_KEY.replace(/\\n/g, "\n")); }
      catch (e) { google.forEach(g => sources.push({ label: g.label, kind: "google", ok: false, error: String(e.message || e).slice(0, 120) })); return; }
      await Promise.all(google.map(async g => {
        try {
          const evs = await fetchGoogle(g.id, g.label, token, timeMin, timeMax);
          events = events.concat(evs);
          sources.push({ label: g.label, kind: "google", ok: true, count: evs.length });
        } catch (e) {
          sources.push({ label: g.label, kind: "google", ok: false, error: String(e.message || e).slice(0, 120) });
        }
      }));
    })());
  } else if (google.length) {
    google.forEach(g => sources.push({ label: g.label, kind: "google", ok: false, error: "no_gcal" }));
  }

  jobs.push(...ics.map(async s => {
    try {
      const evs = await fetchIcs(s.url, s.label, timeMin, timeMax);
      events = events.concat(evs);
      sources.push({ label: s.label, kind: "ics", ok: true, count: evs.length });
    } catch (e) {
      sources.push({ label: s.label, kind: "ics", ok: false, error: String(e.message || e).slice(0, 120) });
    }
  }));

  await Promise.all(jobs);

  if (!sources.length) return json({ error: "no_sources" }, 200);

  events.sort((a, b) => String(a.start).localeCompare(String(b.start)));
  const payload = { events, sources, timeMin, timeMax, fetchedAt: Date.now() };

  const anyOk = sources.some(s => s.ok);
  if (anyOk && env.PANEL_KV) {
    try { await env.PANEL_KV.put(CACHE_KEY, JSON.stringify({ ts: Date.now(), payload }), { expirationTtl: 3600 }); } catch (_) {}
  }
  if (!anyOk && env.PANEL_KV) {
    // Todo caído: sirve la última caché aunque esté caducada.
    try {
      const c = await env.PANEL_KV.get(CACHE_KEY, "json");
      if (c) return json({ ...c.payload, cached: true, stale: true, sources });
    } catch (_) {}
  }
  return json(payload);
}
