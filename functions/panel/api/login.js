// POST /panel/api/login — valida credenciales y abre sesión.
import { makeToken, sessionCookie, timingEqual } from "../_auth.js";

export async function onRequestPost(context) {
  const { request, env } = context;
  let user = "", pass = "";
  try {
    const form = await request.formData();
    user = (form.get("user") || "").toString();
    pass = (form.get("pass") || "").toString();
  } catch (e) { /* body vacío */ }

  const ok =
    env.PANEL_USER && env.PANEL_PASS && env.PANEL_SECRET &&
    timingEqual(user, env.PANEL_USER) &&
    timingEqual(pass, env.PANEL_PASS);

  const headers = new Headers();
  if (!ok) {
    headers.set("Location", new URL("/panel/?e=1", request.url).toString());
    return new Response(null, { status: 303, headers });
  }
  const token = await makeToken(user, env.PANEL_SECRET);
  headers.append("Set-Cookie", sessionCookie(token));
  headers.set("Location", new URL("/panel/", request.url).toString());
  return new Response(null, { status: 303, headers });
}

export async function onRequestGet(context) {
  return new Response(null, {
    status: 303,
    headers: { Location: new URL("/panel/", context.request.url).toString() }
  });
}
