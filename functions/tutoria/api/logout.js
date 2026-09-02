// GET/POST /tutoria/api/logout — cierra la sesión.
import { clearCookie, privateHeaders } from "../_auth.js";

export async function onRequest(context) {
  const headers = new Headers(privateHeaders());
  headers.append("Set-Cookie", clearCookie());
  // Volver a la página pública de la asignatura, no al login: cerrar sesión
  // es salir del área privada, no reintentar la entrada.
  headers.set("Location",
    new URL("/docencia/tutoria-2eso/", context.request.url).toString());
  return new Response(null, { status: 303, headers });
}
