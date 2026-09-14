-- Documents d'inici de curs a la fitxa de tutoria: armariet, autorització de
-- sortides i els escanejos originals.
--
-- Executar un cop a la D1 `tutoria`:
--   npx wrangler d1 execute tutoria --remote --file=scripts/sql/tutoria_documents.sql
--
-- Com a tutoria_fitxa_inicial.sql: D1 no té ALTER TABLE ... IF NOT EXISTS i
-- `execute --file` s'atura al primer error. Si ja s'ha passat, tornar-lo a
-- executar peta a la primera línia i no fa res més.
--
-- Els escanejos NO van a la base de dades ni al repositori: viuen al bucket R2
-- privat `tutoria-fotos`, amb clau documents/<tipus>/<id>.pdf, i només surten
-- per /tutoria/api/document, que exigeix sessió. Aquí només es marca si n'hi ha.

-- Armariet (de la fitxa que omple l'alumne)
ALTER TABLE tutoria_alumnes ADD COLUMN armari            TEXT;
ALTER TABLE tutoria_alumnes ADD COLUMN cadenat           TEXT;

-- Autorització de sortides i activitats.
-- La data de lliurament (ISO); NULL vol dir que no l'ha portada.
ALTER TABLE tutoria_alumnes ADD COLUMN autoritzacio_sortides TEXT;
-- Qui la signa. El DNI NO es transcriu: consta a l'escaneig, que és on cal.
ALTER TABLE tutoria_alumnes ADD COLUMN autoritzacio_signant  TEXT;
-- Atencions especials que declara la família (dieta, medicació, al·lèrgies,
-- què fer en cas d'urgència). Dada sensible: es queda dins del gate.
ALTER TABLE tutoria_alumnes ADD COLUMN atencions         TEXT;

-- 1 si hi ha escaneig a R2
ALTER TABLE tutoria_alumnes ADD COLUMN doc_fitxa         INTEGER DEFAULT 0;
ALTER TABLE tutoria_alumnes ADD COLUMN doc_autoritzacio  INTEGER DEFAULT 0;
