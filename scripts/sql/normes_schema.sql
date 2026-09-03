-- Prova de normes de convivència — esquema.
--
-- Executar un cop a la D1 `tutoria`:
--   npx wrangler d1 execute tutoria --remote --file=scripts/sql/normes_schema.sql
--
-- Viu a la mateixa base que les fitxes, però en taules pròpies. L'endpoint
-- públic /api/normes només hi ESCRIU; llegir-ho és cosa de /tutoria/normes/,
-- darrere del gate.

-- Una sessió = una passada de la prova. El codi és el que va a la pissarra.
CREATE TABLE IF NOT EXISTS normes_sessions (
  codi     TEXT PRIMARY KEY,          -- p. ex. "K7M2"
  nom      TEXT NOT NULL,             -- "Tutoria 2n ESO · setembre"
  curs     TEXT    DEFAULT '2026-27',
  oberta   INTEGER DEFAULT 1,         -- 0 = tancada, ja no accepta respostes
  -- 0 mentre es fa la prova: l'alumne veu la nota però no quines ha fallat.
  -- Si es tornés la correcció a l'instant, n'hi hauria prou d'enviar-la un cop
  -- amb un nom inventat per llegir totes les respostes bones i tornar a entrar.
  correccio INTEGER DEFAULT 0,
  creada   TEXT,
  tancada  TEXT
);

-- Una fila per entrega. Es guarden tots els intents; el de referència és
-- intent = 1 i el panell ensenya qui n'ha fet més d'un.
CREATE TABLE IF NOT EXISTS normes_respostes (
  id        INTEGER PRIMARY KEY AUTOINCREMENT,
  codi      TEXT NOT NULL,
  nom       TEXT NOT NULL,
  grup      TEXT NOT NULL,
  versio    TEXT,
  respostes TEXT,                     -- JSON {id_pregunta: opcio_triada}
  encerts   INTEGER,
  total     INTEGER,
  nota      REAL,
  intent    INTEGER DEFAULT 1,
  enviada   TEXT
);

CREATE INDEX IF NOT EXISTS idx_normes_codi  ON normes_respostes (codi);
CREATE INDEX IF NOT EXISTS idx_normes_grup  ON normes_respostes (codi, grup);
CREATE INDEX IF NOT EXISTS idx_normes_alu   ON normes_respostes (codi, nom, grup);
