-- Matemàtiques de 2n d'ESO: els grups per nivell i el quadern de notes.
--
--   npx wrangler d1 execute tutoria --remote --file=scripts/sql/mates_schema.sql
--
-- Els cinc grups-classe de 2n es reparteixen en sis grups de nivell, cadascun
-- amb el seu professor. Viu a la mateixa base que la tutoria perquè les dues
-- coses es miren juntes: de cada alumne de 2n ESO E vull saber a quin grup de
-- mates va, amb qui i a quina aula.
--
-- Aquestes dades NO viuen al repositori: es carreguen amb
--   scripts/mates_import_nivells.py

-- Un grup de nivell: qui el fa i on. L'aula la va omplint el professor des de
-- la pàgina, que al setembre encara no se sap.
CREATE TABLE IF NOT EXISTS mates_grups (
  curs       TEXT NOT NULL,       -- "2026-27"
  nivell     TEXT NOT NULL,       -- "Alt", "Mig 1", "Mig 2", "Mig 3", "Baix 1", "Baix 2"
  professor  TEXT,
  aula       TEXT,
  ordre      INTEGER DEFAULT 0,   -- per llistar-los d'Alt a Baix, no per ordre alfabètic
  updated_at TEXT,
  PRIMARY KEY (curs, nivell)
);

-- Qui va a cada grup. `id` és el mateix slug que a tutoria_alumnes
-- ("cognoms nom"), que és el que permet creuar les dues taules.
CREATE TABLE IF NOT EXISTS mates_alumnes (
  curs        TEXT NOT NULL,
  id          TEXT NOT NULL,
  nivell      TEXT NOT NULL,
  grup_origen TEXT,               -- "2ESO-E", la seva classe
  cognoms     TEXT NOT NULL,
  nom         TEXT NOT NULL,
  updated_at  TEXT,
  PRIMARY KEY (curs, id)
);
CREATE INDEX IF NOT EXISTS idx_mates_nivell ON mates_alumnes (curs, nivell);
CREATE INDEX IF NOT EXISTS idx_mates_origen ON mates_alumnes (curs, grup_origen);

-- Una columna del quadern: una prova, un lliurament, el que sigui.
CREATE TABLE IF NOT EXISTS mates_activitats (
  id         TEXT PRIMARY KEY,    -- "2627-mig3-1712345678"
  curs       TEXT NOT NULL,
  nivell     TEXT NOT NULL,
  nom        TEXT NOT NULL,
  data       TEXT,                -- ISO, opcional
  pes        REAL DEFAULT 1,
  ordre      INTEGER DEFAULT 0,
  creada     TEXT
);
CREATE INDEX IF NOT EXISTS idx_activitats ON mates_activitats (curs, nivell, ordre);

-- Una casella. `nota` és text a posta: hi ha d'entrar un 7,5 i també un "NP"
-- o un "A". La mitjana només compta les que són números, i la pàgina diu
-- quantes n'ha comptat, que amagar-ho seria pitjor que no fer-la.
CREATE TABLE IF NOT EXISTS mates_notes (
  activitat  TEXT NOT NULL,
  alumne     TEXT NOT NULL,
  nota       TEXT,
  updated_at TEXT,
  PRIMARY KEY (activitat, alumne)
);
