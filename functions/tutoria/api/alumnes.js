// GET /tutoria/api/alumnes?grup=2ESO-E — listado de la orla.
//
// Los datos NO viven en el repositorio: se leen de D1 en tiempo de
// petición. El middleware ya ha exigido sesión antes de llegar aquí.
//
// Devuelve también las notas del curso anterior porque las tres vistas
// (orla, lista y fichas) las usan para ordenar y para marcar quién arrastra
// materias. Son 25 filas: cabe de sobra en una sola respuesta.
import { requireSession, unauthorized, json } from "../_auth.js";

export async function onRequestGet(context) {
  const { request, env } = context;
  if (!(await requireSession(request, env))) return unauthorized();
  if (!env.TUTORIA_DB) return json({ error: "no_db", alumnes: [] }, 503);

  const grup = new URL(request.url).searchParams.get("grup") || "2ESO-E";
  let results;
  try {
    ({ results } = await env.TUTORIA_DB
      .prepare(
        `SELECT id, num, grup, curs, cognoms, nom, marca, foto, sexe,
                curs_anterior, notes_anteriors, pendents,
                contacte, notes, entrevistes, incidencies
           FROM tutoria_alumnes
          WHERE grup = ?
          ORDER BY num`
      )
      .bind(grup)
      .all());
  } catch (e) {
    // Casi siempre es la tabla con el esquema antiguo: decirlo, en vez de
    // dejar un "no se han podido cargar las dades" que no lleva a ninguna
    // parte. El mensaje solo lo ve quien ya ha pasado el login.
    return json({ error: "db", detall: String(e && e.message || e) }, 500);
  }

  // El cliente solo necesita saber si hay seguimiento, no su contenido:
  // así la lista no arrastra las notas de tutoría de los 25 en cada carga.
  const alumnes = results.map((a) => {
    const { contacte, notes, entrevistes, incidencies, ...resta } = a;
    return {
      ...resta,
      te_seguiment: Boolean(
        (notes && notes.trim()) || (contacte && contacte.trim()) ||
        (entrevistes && entrevistes !== "[]") || (incidencies && incidencies !== "[]")
      ),
    };
  });

  return json({ grup, total: alumnes.length, alumnes });
}
