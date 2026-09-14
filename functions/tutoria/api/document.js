// GET /tutoria/api/document?tipus=autoritzacio&id=…   — l'escaneig d'un alumne
// GET /tutoria/api/document?tipus=autoritzacio&id=_totes — totes, per nº de llista
//
// Els escanejos (autorització de sortides, fitxa de l'alumne) porten dades de
// menors i el DNI de qui signa. No són fitxers estàtics del lloc: viuen al
// bucket R2 privat, com les fotos, i només surten per aquí, amb sessió.
import { requireSession, unauthorized, json, privateHeaders } from "../_auth.js";

const TIPUS = new Set(["autoritzacio", "fitxa"]);
const SAFE_ID = /^(_totes|[a-z0-9-]{1,120})$/;

export async function onRequestGet(context) {
  const { request, env } = context;
  if (!(await requireSession(request, env))) return unauthorized();
  if (!env.TUTORIA_FOTOS) return json({ error: "no_bucket" }, 503);

  const url = new URL(request.url);
  const tipus = url.searchParams.get("tipus") || "";
  const id = (url.searchParams.get("id") || "").toLowerCase();
  if (!TIPUS.has(tipus)) return json({ error: "bad_tipus" }, 400);
  if (!SAFE_ID.test(id)) return json({ error: "bad_id" }, 400);

  const obj = await env.TUTORIA_FOTOS.get(`documents/${tipus}/${id}.pdf`);
  if (!obj) return json({ error: "not_found" }, 404);

  return new Response(obj.body, {
    headers: privateHeaders({
      "content-type": "application/pdf",
      // inline: s'obre al navegador del mòbil sense descarregar-lo
      "content-disposition": `inline; filename="${tipus}-${id}.pdf"`,
    }),
  });
}
