// GET/POST /mates-2eso/api/logout — tanca la sessió d'aquesta zona.
// No toca la de tutoria: són sessions separades.
import { clearCookie, privateHeaders } from "../_auth.js";

export async function onRequest(context) {
  const headers = new Headers(privateHeaders());
  headers.append("Set-Cookie", clearCookie());
  // Cap a la pàgina pública de la matèria, no al login: tancar sessió és
  // sortir de la zona privada, no tornar a intentar entrar-hi.
  headers.set("Location",
    new URL("/docencia/2eso/", context.request.url).toString());
  return new Response(null, { status: 303, headers });
}
