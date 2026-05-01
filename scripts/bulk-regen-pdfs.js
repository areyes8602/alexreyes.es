#!/usr/bin/env node
// Itera sobre todas las carpetas /aula/<materia>/examenes/<id>/ y ejecuta regen-exam-pdf.js
// en cada una. Saltea las que no tengan pN.html.
//
// Uso: node bulk-regen.js <repo-root>

const { execFileSync } = require('child_process');
const fs = require('fs');
const path = require('path');

const repoRoot = path.resolve(process.argv[2] || process.cwd());
const aulaDir = path.join(repoRoot, 'aula');

function findExamDirs() {
  const dirs = [];
  for (const materia of fs.readdirSync(aulaDir)) {
    const examenes = path.join(aulaDir, materia, 'examenes');
    if (!fs.existsSync(examenes)) continue;
    for (const id of fs.readdirSync(examenes)) {
      const examDir = path.join(examenes, id);
      if (fs.statSync(examDir).isDirectory()) {
        const hasPages = fs.readdirSync(examDir).some(f => /^p\d+\.html$/.test(f));
        if (hasPages) dirs.push(path.relative(repoRoot, examDir));
      }
    }
  }
  return dirs.sort();
}

const dirs = findExamDirs();
console.log(`Encontrados ${dirs.length} exámenes con pN.html.\n`);

let ok = 0, fail = 0;
const failures = [];

for (let i = 0; i < dirs.length; i++) {
  const rel = dirs[i];
  console.log(`\n━━━ [${i+1}/${dirs.length}] ${rel} ━━━`);
  try {
    execFileSync('node', [path.join(__dirname, 'regen-exam-pdf.js'), repoRoot, rel], {
      stdio: 'inherit',
      env: { ...process.env, KATEX_LOCAL_DIR: process.env.KATEX_LOCAL_DIR || '/tmp/katex-pkg/package/dist' },
      timeout: 90000,
    });
    ok++;
  } catch (e) {
    fail++;
    failures.push(rel);
    console.error(`  ✗ ERROR en ${rel}`);
  }
}

console.log(`\n\n═══ Resumen ═══`);
console.log(`✓ Éxitos: ${ok}`);
console.log(`✗ Fallos: ${fail}`);
if (failures.length) {
  console.log(`Carpetas con error:`);
  failures.forEach(f => console.log(`  - ${f}`));
}
