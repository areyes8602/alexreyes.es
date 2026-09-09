// A quin grup de nivell va cada alumne de la classe, matèria per matèria.
//
// Ho miren dues pàgines —la fitxa d'un alumne i la graella de grups— i les
// dues ho demanen per a la classe sencera d'una sola vegada: són vint-i-set
// alumnes, i vint-i-set peticions per pintar una taula no tenen cap sentit.
//
// Matemàtiques va a part perquè viu a les seves taules, les que fan servir
// també el quadern de notes de /mates-2eso/. La resta de matèries van totes
// a tutoria_materia_*.

const senseTaula = (e) => /no such table/i.test(String((e && e.message) || e));

export async function llegeixNivells(db, curs, origen) {
  let mates = [];
  try {
    const r = await db.prepare(
      `SELECT a.id, a.nivell, g.professor, g.aula
         FROM mates_alumnes a LEFT JOIN mates_grups g
           ON g.curs = a.curs AND g.nivell = a.nivell
        WHERE a.curs = ? AND a.grup_origen = ?`).bind(curs, origen).all();
    mates = r.results;
  } catch (e) {
    // Si encara no s'han creat les taules, val més la pàgina sense el grup
    // que no pas la pàgina trencada.
    if (!senseTaula(e)) throw e;
  }

  let materies = [], assignacions = [];
  try {
    const g = await db.prepare(
      `SELECT materia, grup, nivell, professor, aula, ordre
         FROM tutoria_materia_grups WHERE curs = ?
        ORDER BY materia, ordre, grup`).bind(curs).all();
    materies = g.results;
    const a = await db.prepare(
      `SELECT m.alumne, m.materia, m.grup
         FROM tutoria_materia_alumne m
         JOIN tutoria_alumnes t ON t.id = m.alumne AND t.curs = m.curs
        WHERE m.curs = ? AND t.grup = ?`).bind(curs, origen).all();
    assignacions = a.results;
  } catch (e) {
    if (!senseTaula(e)) throw e;
  }

  return { mates, materies, assignacions };
}
