-- Esquema de la base de datos de tutoría (Cloudflare D1).
--
-- Estos datos NO viven en el repositorio: se cargan con
-- scripts/tutoria_import_orla.py desde la orla en PDF del centro.
--
--   npx wrangler d1 execute tutoria --remote --file=scripts/sql/tutoria_schema.sql

CREATE TABLE IF NOT EXISTS tutoria_alumnes (
  id         TEXT PRIMARY KEY,   -- slug estable: "acuna-fernandez-clara-gabriela"
  num        INTEGER NOT NULL,   -- nº de lista en la orla
  grup       TEXT    NOT NULL,   -- "2ESO-E"
  curs       TEXT    NOT NULL,   -- "2026-27"
  cognoms    TEXT    NOT NULL,
  nom        TEXT    NOT NULL,
  marca      TEXT,               -- marca de la orla, p. ej. "(R)"
  foto       INTEGER DEFAULT 0,  -- 1 si hay imagen en R2 con clave <id>.jpg
  contacte   TEXT,               -- contacto de familia (lo rellenas tú)
  notes      TEXT,               -- seguimiento de tutoría
  updated_at TEXT
);

CREATE INDEX IF NOT EXISTS idx_tutoria_grup ON tutoria_alumnes (grup, num);
