// Sessions de les zones privades del lloc.
//
// Cada zona té la SEVA cookie, amb Path a la seva carpeta: així el navegador
// no l'envia enlloc més, i una sessió de tutoria no obre les mates ni al
// revés. El que comparteixen són les credencials (TUTORIA_USER, TUTORIA_PASS)
// i el secret que signa el testimoni: és la mateixa persona entrant a dues
// coses seves, no dos usuaris diferents.
//
// La criptografia és la de /panel/, que no es toca.
import { makeToken, verifyToken, timingEqual, getCookie } from "./panel/_auth.js";

export { makeToken, verifyToken, timingEqual };

// 8 hores: són dades de menors, la sessió no s'ha de quedar oberta setmanes.
export const MAX_AGE = 60 * 60 * 8;

// Capçaleres comunes a tot el que surt d'una zona privada.
export function privateHeaders(extra = {}) {
  return {
    "cache-control": "no-store, no-cache, must-revalidate, private",
    "x-robots-tag": "noindex, nofollow, noarchive",
    "referrer-policy": "no-referrer",
    ...extra,
  };
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

// Les peces de sessió d'una zona: nom de cookie i carpeta on val.
export function fesSessio(cookie, base) {
  const comuns = `HttpOnly; Secure; SameSite=Strict`;
  return {
    COOKIE: cookie,
    getSessionCookie: (request) => getCookie(request, cookie),
    sessionCookie: (token) =>
      `${cookie}=${token}; Path=${base}; ${comuns}; Max-Age=${MAX_AGE}`,
    clearCookie: () => `${cookie}=; Path=${base}; ${comuns}; Max-Age=0`,
    // Sessió vàlida → torna l'usuari; si no, null.
    requireSession: async (request, env) => {
      if (!env.TUTORIA_SECRET) return null;
      return verifyToken(getCookie(request, cookie), env.TUTORIA_SECRET);
    },
  };
}
