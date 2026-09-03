-- Listas de control de tutoría: entregas, autorizaciones, asistencia.
--
--   npx wrangler d1 execute tutoria --remote --file=scripts/sql/tutoria_llistes.sql
--
-- Una lista por cosa que hay que ir marcando ("Normes de convivència
-- signades", "Autorització de sortides"). El estado de los 25 alumnos cabe
-- de sobra en una columna JSON: son 25 filas, no hace falta una tabla de
-- cruce ni las consultas que arrastraría.

CREATE TABLE IF NOT EXISTS tutoria_llistes (
  id         TEXT PRIMARY KEY,   -- slug: "normes-convivencia"
  grup       TEXT NOT NULL,      -- "2ESO-E"
  curs       TEXT NOT NULL,      -- "2026-27"
  nom        TEXT NOT NULL,
  descripcio TEXT,
  -- JSON {id_alumne: {"fet": 1, "data": "2026-09-15", "nota": "…"}}
  -- Ausente = no entregado. Así una lista recién creada no ocupa nada.
  dades      TEXT DEFAULT '{}',
  creada     TEXT,
  updated_at TEXT
);

CREATE INDEX IF NOT EXISTS idx_llistes_grup ON tutoria_llistes (grup, curs);
