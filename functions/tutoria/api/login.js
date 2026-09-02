// POST /tutoria/api/login — valida credenciales y abre sesión.
import { makeToken, sessionCookie, timingEqual, privateHeaders } from "../_auth.js";

export async function onRequestPost(context) {
  const { request, env } = context;
  let user = "", pass = "";
  try {
    const form = await request.formData();
    user = (form.get("user") || "").toString();
    pass = (form.get("pass") || "").toString();
  } catch (e) { /* body vacío */ }

  const ok =
    env.TUTORIA_USER && env.TUTORIA_PASS && env.TUTORIA_SECRET &&
    timingEqual(user, env.TUTORIA_USER) &&
    timingEqual(pass, env.TUTORIA_PASS);

  const headers = new Headers(privateHeaders());
  if (!ok) {
    // Freno al probado de contraseñas: un segundo por intento fallido baja
    // un ataque de fuerza bruta a ~86.000 pruebas al día por conexión, que
    // frente a una contraseña larga y aleatoria no lleva a ninguna parte.
    // No sustituye a esa contraseña: la complementa.
    await new Promise((r) => setTimeout(r, 1000));
    headers.set("Location", new URL("/tutoria/?e=1", request.url).toString());
    return new Response(null, { status: 303, headers });
  }
  headers.append("Set-Cookie", sessionCookie(await makeToken(user, env.TUTORIA_SECRET)));
  headers.set("Location", new URL("/tutoria/", request.url).toString());
  return new Response(null, { status: 303, headers });
}

export async function onRequestGet(context) {
  return new Response(null, {
    status: 303,
    headers: { Location: new URL("/tutoria/", context.request.url).toString() },
  });
}
