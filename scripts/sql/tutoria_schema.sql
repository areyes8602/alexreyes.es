-- Esquema de la base de datos de tutoría (Cloudflare D1).
--
-- Estos datos NO viven en el repositorio: se cargan con
--   scripts/tutoria_import_orla.py   (identidad y fotos, desde la orla)
--   scripts/tutoria_import_notes.py  (notas del curso anterior, desde las juntas)
--
--   npx wrangler d1 execute tutoria --remote --file=scripts/sql/tutoria_schema.sql
--
-- Los campos que son listas (familia, entrevistas, incidencias) van como JSON
-- en una columna de texto: D1 es SQLite y así se añaden apartados a la ficha
-- sin migrar la tabla cada vez.

CREATE TABLE IF NOT EXISTS tutoria_alumnes (
  -- ── Identidad (la pone el importador de la orla; no se edita a mano) ──
  id         TEXT PRIMARY KEY,   -- slug estable: "acuna-fernandez-clara-gabriela"
  num        INTEGER NOT NULL,   -- nº de lista
  grup       TEXT    NOT NULL,   -- "2ESO-E"
  curs       TEXT    NOT NULL,   -- "2026-27"
  cognoms    TEXT    NOT NULL,
  nom        TEXT    NOT NULL,
  marca      TEXT,               -- marca de la orla, p. ej. "(R)" repetidor
  foto       INTEGER DEFAULT 0,  -- 1 si hay imagen en R2 con clave <id>.jpg
  sexe       TEXT,               -- "H" / "M", tal como viene del centro

  -- ── Personal ──
  naixement  TEXT,               -- ISO "2012-04-18"
  idioma     TEXT,               -- lengua familiar
  adreca     TEXT,
  telefon    TEXT,               -- del alumno, si tiene
  email      TEXT,

  -- ── Familia ── JSON: [{"nom","relacio","telefon","email","notes"}]
  familia    TEXT,
  recull     TEXT,               -- quién puede recogerlo, autorizaciones

  -- ── Académico ──
  curs_anterior   TEXT,          -- "1ESO-E"
  notes_anteriors TEXT,          -- JSON {materia: {"1":n,"2":n,"3":n,"0":n}}
  pendents        INTEGER,       -- materias pendientes al final del curso anterior
  suport          TEXT,          -- PI, adaptaciones, refuerzos
  repetidor       INTEGER DEFAULT 0,

  -- ── Seguimiento de tutoría ──
  contacte     TEXT,             -- teléfono/correo de contacto rápido
  notes        TEXT,             -- observaciones libres
  entrevistes  TEXT,             -- JSON [{"data","amb","resum"}]
  incidencies  TEXT,             -- JSON [{"data","tipus","descripcio"}]
  acords       TEXT,             -- compromisos vigentes

  -- ── Otros ──
  extraescolars TEXT,
  carrec        TEXT,            -- delegado, subdelegado…
  imatge_ok     INTEGER,         -- autorización de imagen: 1 sí, 0 no, NULL sin dato

  updated_at TEXT
);

CREATE INDEX IF NOT EXISTS idx_tutoria_grup ON tutoria_alumnes (grup, num);
