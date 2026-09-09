-- Notes de les reunions de nivell, alumne per alumne.
--
--   npx wrangler d1 execute tutoria --remote --file=scripts/sql/tutoria_reunions.sql
--
-- A la reunió de nivell l'equip docent va passant alumne per alumne. El que
-- s'hi diu acaba en un paper que es perd, i al març ningú recorda què es va
-- acordar al novembre. Aquí queda a la fitxa de cadascú, amb data.
--
-- JSON [{"data","reunio","resum"}], com entrevistes i incidències.
--
-- Si no s'executa no es trenca res: la pestanya surt buida i el desat de la
-- resta de la fitxa no en depèn.

ALTER TABLE tutoria_alumnes ADD COLUMN reunions TEXT;
