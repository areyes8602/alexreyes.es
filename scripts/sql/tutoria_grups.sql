-- Agrupaments i optatives dels alumnes de la tutoria.
--
--   npx wrangler d1 execute tutoria --remote --file=scripts/sql/tutoria_grups.sql
--
-- La classe no va junta a tot arreu: es reparteix per nivells a matemàtiques
-- i a anglès, i cadascú tria les seves optatives. El tutor ho ha de tenir en
-- un sol lloc, i com que cada curs canvien les columnes, són dades, no
-- esquema: ell crea "Anglès", "Optativa 1r trimestre" o el que calgui.
--
-- Matemàtiques NO és una columna d'aquí: ve de mates_alumnes, i la pàgina la
-- mostra com a primera columna de només lectura.

-- Una columna: "Anglès", "Optativa 1r trim", "Desdoblament"…
CREATE TABLE IF NOT EXISTS tutoria_agrupaments (
  id     TEXT PRIMARY KEY,       -- "2627-2esoe-1712345678"
  curs   TEXT NOT NULL,
  grup   TEXT NOT NULL,          -- "2ESO-E"
  nom    TEXT NOT NULL,
  ordre  INTEGER DEFAULT 0,
  creada TEXT
);
CREATE INDEX IF NOT EXISTS idx_agrupaments ON tutoria_agrupaments (curs, grup, ordre);

-- Una casella: on va aquest alumne en aquesta columna. Text lliure, que
-- "Grup B", "Robòtica" i "Amb la Núria" són totes respostes vàlides.
CREATE TABLE IF NOT EXISTS tutoria_agrupament_alumne (
  agrupament TEXT NOT NULL,
  alumne     TEXT NOT NULL,
  valor      TEXT,
  updated_at TEXT,
  PRIMARY KEY (agrupament, alumne)
);
