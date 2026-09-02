// Sesión de /tutoria/ — cookie propia, firmada con HMAC-SHA256.
//
// Reutiliza las primitivas criptográficas de /panel/ pero con su PROPIO
// secreto (TUTORIA_SECRET) y su propia cookie: una sesión del panel no
// sirve aquí, ni al revés. La cookie va con Path=/tutoria, así que el
// navegador no la envía a ninguna otra parte del sitio.
import { makeToken, verifyToken, timingEqual, getCookie } from "../panel/_auth.js";

export const COOKIE = "tutoria_session";

// 8 horas: son datos de menores, la sesión no debe quedarse abierta semanas.
export const MAX_AGE = 60 * 60 * 8;

export { makeToken, verifyToken, timingEqual };

export function getSessionCookie(request) {
  return getCookie(request, COOKIE);
}

export function sessionCookie(token) {
  return `${COOKIE}=${token}; Path=/tutoria; HttpOnly; Secure; SameSite=Strict; Max-Age=${MAX_AGE}`;
}

export function clearCookie() {
  return `${COOKIE}=; Path=/tutoria; HttpOnly; Secure; SameSite=Strict; Max-Age=0`;
}

// Cabeceras comunes a todo lo que sale de aquí: nada se cachea, nada se indexa.
export function privateHeaders(extra = {}) {
  return {
    "cache-control": "no-store, no-cache, must-revalidate, private",
    "x-robots-tag": "noindex, nofollow, noarchive",
    "referrer-policy": "no-referrer",
    ...extra,
  };
}

// Sesión válida → devuelve el usuario; si no, null.
export async function requireSession(request, env) {
  if (!env.TUTORIA_SECRET) return null;
  return verifyToken(getSessionCookie(request), env.TUTORIA_SECRET);
}

export function json(data, status = 200) {
  return new Response(JSON.stringify(data), {
    status,
    headers: privateHeaders({ "content-type": "application/json; charset=utf-8" }),
  });
}

export function unauthorized() {
  return json({ error: "unauthorized" }, 401);
}
