// GET/POST /tutoria/api/logout — cierra la sesión.
import { clearCookie, privateHeaders } from "../_auth.js";

export async function onRequest(context) {
  const headers = new Headers(privateHeaders());
  headers.append("Set-Cookie", clearCookie());
  headers.set("Location", new URL("/tutoria/?e=out", context.request.url).toString());
  return new Response(null, { status: 303, headers });
}
