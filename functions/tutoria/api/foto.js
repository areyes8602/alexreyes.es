// GET /tutoria/api/foto?id=… — sirve la foto desde R2, solo con sesión.
//
// Las fotos NO son ficheros estáticos del sitio: viven en un bucket R2
// privado y salen únicamente por aquí. Sin cookie de sesión válida no hay
// forma de alcanzarlas por URL.
import { requireSession, unauthorized, json, privateHeaders } from "../_auth.js";

const SAFE_ID = /^[a-z0-9-]{1,120}$/;

export async function onRequestGet(context) {
  const { request, env } = context;
  if (!(await requireSession(request, env))) return unauthorized();
  if (!env.TUTORIA_FOTOS) return json({ error: "no_bucket" }, 503);

  const id = (new URL(request.url).searchParams.get("id") || "").toLowerCase();
  if (!SAFE_ID.test(id)) return json({ error: "bad_id" }, 400);

  const obj = await env.TUTORIA_FOTOS.get(`${id}.jpg`);
  if (!obj) return json({ error: "not_found" }, 404);

  return new Response(obj.body, {
    headers: privateHeaders({
      "content-type": obj.httpMetadata?.contentType || "image/jpeg",
      "content-disposition": "inline",
    }),
  });
}
