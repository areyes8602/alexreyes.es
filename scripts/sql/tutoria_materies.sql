-- Els grups de nivell de la resta de matèries (anglès, de moment).
--
--   npx wrangler d1 execute tutoria --remote --file=scripts/sql/tutoria_materies.sql
--
-- Tot són CREATE TABLE IF NOT EXISTS: es pot tornar a passar sense por.
--
-- Per què no van a mates_alumnes: matemàtiques té taules pròpies perquè a
-- sobre hi penja el quadern de notes de /mates-2eso/. D'anglès no en porto
-- les notes: només vull saber a quin grup va cada alumne meu, amb qui i on.
-- Això val per a qualsevol matèria que reparteixi la classe, i per això la
-- taula porta el nom de la matèria a dins en comptes d'una taula per matèria.
--
-- El repartiment el fan els departaments i no viu al repositori, que és
-- públic: aquestes taules es carreguen a part, amb un bloc d'INSERTs.

-- Un grup de nivell d'una matèria. La clau és `grup` i no `nivell` perquè
-- anglès té tres grups «Standard» i dos «Baix»: el nivell sol no distingeix.
CREATE TABLE IF NOT EXISTS tutoria_materia_grups (
  curs       TEXT NOT NULL,       -- "2026-27"
  materia    TEXT NOT NULL,       -- "Anglès"
  grup       TEXT NOT NULL,       -- "angles-std-greer"
  nivell     TEXT,                -- "Standard" — el que se'n diu de cara als alumnes
  professor  TEXT,
  aula       TEXT,
  ordre      INTEGER DEFAULT 0,   -- d'Alt a Baix, no per ordre alfabètic
  updated_at TEXT,
  PRIMARY KEY (curs, materia, grup)
);

-- Qui va a cada grup. `alumne` és el mateix slug que tutoria_alumnes.id
-- ("cognoms nom"), que és el que permet creuar-ho amb la classe.
CREATE TABLE IF NOT EXISTS tutoria_materia_alumne (
  curs       TEXT NOT NULL,
  materia    TEXT NOT NULL,
  alumne     TEXT NOT NULL,
  grup       TEXT NOT NULL,
  updated_at TEXT,
  PRIMARY KEY (curs, materia, alumne)
);
CREATE INDEX IF NOT EXISTS idx_materia_alumne ON tutoria_materia_alumne (curs, alumne);
