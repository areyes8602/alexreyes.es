// Sessió de /mates/ — la seva pròpia cookie, amb Path=/mates.
//
// Mateix usuari, mateixa contrasenya i mateix secret que la tutoria: és la
// mateixa persona entrant a dues coses seves. El que no comparteixen és la
// sessió, i és a posta: cada zona s'obre i es tanca per separat, i la cookie
// d'una no viatja mai a l'altra ni a la part pública del lloc.
import { fesSessio } from "../_sessio.js";

export { makeToken, verifyToken, timingEqual, privateHeaders, json, unauthorized, MAX_AGE }
  from "../_sessio.js";

export const COOKIE = "mates_session";
const sessio = fesSessio(COOKIE, "/mates");

export const getSessionCookie = sessio.getSessionCookie;
export const sessionCookie = sessio.sessionCookie;
export const clearCookie = sessio.clearCookie;
export const requireSession = sessio.requireSession;
