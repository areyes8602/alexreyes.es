// GET/POST /panel/api/logout — cierra la sesión.
import { clearCookie } from "../_auth.js";

export async function onRequest(context) {
  const { request } = context;
  const headers = new Headers();
  headers.append("Set-Cookie", clearCookie());
  headers.set("Location", new URL("/panel/?e=out", request.url).toString());
  return new Response(null, { status: 303, headers });
}
