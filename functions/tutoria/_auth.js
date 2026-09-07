// Sessió de /tutoria/ — cookie pròpia, signada amb HMAC-SHA256.
//
// Les peces són a functions/_sessio.js, compartides amb /mates/: mateixes
// credencials i mateix secret, però cada zona amb la seva cookie i el seu
// Path, de manera que el navegador no l'envia enlloc més i una sessió de
// mates no obre la tutoria.
import { fesSessio } from "../_sessio.js";

export { makeToken, verifyToken, timingEqual, privateHeaders, json, unauthorized, MAX_AGE }
  from "../_sessio.js";

export const COOKIE = "tutoria_session";
const sessio = fesSessio(COOKIE, "/tutoria");

export const getSessionCookie = sessio.getSessionCookie;
export const sessionCookie = sessio.sessionCookie;
export const clearCookie = sessio.clearCookie;
export const requireSession = sessio.requireSession;
