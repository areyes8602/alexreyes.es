-- Distribución del aula: dónde se sienta cada alumno.
--
--   npx wrangler d1 execute tutoria --remote --file=scripts/sql/tutoria_aula.sql
--
-- Varias distribuciones por grupo: la de siempre, la de exámenes, la de
-- trabajo en grupo. Las posiciones van en JSON porque son 25 pares de
-- coordenadas que solo se leen y escriben enteras.

CREATE TABLE IF NOT EXISTS tutoria_aules (
  id         TEXT PRIMARY KEY,   -- slug: "habitual", "examens"
  grup       TEXT NOT NULL,
  curs       TEXT NOT NULL,
  nom        TEXT NOT NULL,
  -- JSON {id_alumne: {"x": 0-100, "y": 0-100}} en % del plano, para que
  -- se vea igual en el portátil, en el proyector y en papel.
  posicions  TEXT DEFAULT '{}',
  creada     TEXT,
  updated_at TEXT
);

CREATE INDEX IF NOT EXISTS idx_aules_grup ON tutoria_aules (grup, curs);
