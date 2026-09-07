// POST /mates-2eso/api/login — valida credencials i obre sessió.
// Les credencials són les de la tutoria: la mateixa persona, dues zones.
import { makeToken, sessionCookie, timingEqual, privateHeaders } from "../_auth.js";

export async function onRequestPost(context) {
  const { request, env } = context;
  let user = "", pass = "";
  try {
    const form = await request.formData();
    user = (form.get("user") || "").toString();
    pass = (form.get("pass") || "").toString();
  } catch (e) { /* cos buit */ }

  const ok =
    env.TUTORIA_USER && env.TUTORIA_PASS && env.TUTORIA_SECRET &&
    timingEqual(user, env.TUTORIA_USER) &&
    timingEqual(pass, env.TUTORIA_PASS);

  const headers = new Headers(privateHeaders());
  if (!ok) {
    // Fre al provat de contrasenyes, com a la tutoria: un segon per intent
    // fallat. No substitueix una contrasenya llarga i aleatòria, la completa.
    await new Promise((r) => setTimeout(r, 1000));
    headers.set("Location", new URL("/mates-2eso/?e=1", request.url).toString());
    return new Response(null, { status: 303, headers });
  }
  headers.append("Set-Cookie", sessionCookie(await makeToken(user, env.TUTORIA_SECRET)));
  headers.set("Location", new URL("/mates-2eso/", request.url).toString());
  return new Response(null, { status: 303, headers });
}

export async function onRequestGet(context) {
  return new Response(null, {
    status: 303,
    headers: { Location: new URL("/mates-2eso/", context.request.url).toString() },
  });
}
