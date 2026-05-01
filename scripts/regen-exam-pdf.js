#!/usr/bin/env node
// Regenera dos PDFs limpios para un examen, a partir de los HTML de cada pregunta:
//   <examen>/original-enunciados.pdf  (sin soluciones)
//   <examen>/original-soluciones.pdf  (con soluciones expandidas)
//
// Uso:
//   node regen-exam-pdf.js <ruta-al-repo> <ruta-relativa-del-examen>
//   KATEX_LOCAL_DIR=/tmp/katex-pkg/package/dist node regen-exam-pdf.js ...
//
// Las preguntas fluyen continuamente (no hay salto de página forzado entre P1, P2…).
// Header/footer en cada página (alexreyes.es / © 2026 Àlex Reyes / Página X de Y).
//
// Requiere: npm install playwright pdf-lib

const fs = require('fs');
const path = require('path');
const http = require('http');
const { chromium } = require('playwright');

const PORT = 8765 + Math.floor(Math.random() * 1000);
const KATEX_LOCAL_DIR = process.env.KATEX_LOCAL_DIR || '';

// ─── Local static server ─────────────────────────────────────────────────
function serveStatic(rootDir) {
  return new Promise((resolve) => {
    const server = http.createServer((req, res) => {
      let urlPath = decodeURIComponent(req.url.split('?')[0]);
      if (urlPath.endsWith('/')) urlPath += 'index.html';
      const filePath = path.join(rootDir, urlPath);
      if (!filePath.startsWith(rootDir)) { res.writeHead(403); res.end('Forbidden'); return; }
      fs.readFile(filePath, (err, data) => {
        if (err) { res.writeHead(404); res.end('Not found: ' + urlPath); return; }
        const ext = path.extname(filePath).toLowerCase();
        const types = {
          '.html':'text/html; charset=utf-8', '.css':'text/css', '.js':'application/javascript',
          '.json':'application/json', '.svg':'image/svg+xml', '.png':'image/png',
          '.jpg':'image/jpeg', '.webp':'image/webp', '.pdf':'application/pdf',
          '.woff':'font/woff', '.woff2':'font/woff2', '.ttf':'font/ttf',
        };
        res.writeHead(200, { 'Content-Type': types[ext] || 'application/octet-stream' });
        res.end(data);
      });
    });
    server.listen(PORT, '127.0.0.1', () => resolve(server));
  });
}

// ─── KaTeX CDN intercept (local mirror) ──────────────────────────────────
function fileForCdnUrl(url) {
  if (!KATEX_LOCAL_DIR) return null;
  const m = url.match(/cdn\.jsdelivr\.net\/npm\/katex@0\.16\.9\/dist\/(.+)$/);
  return m ? path.join(KATEX_LOCAL_DIR, m[1]) : null;
}
function contentTypeForExt(ext) {
  return { '.css':'text/css', '.js':'application/javascript',
           '.woff':'font/woff', '.woff2':'font/woff2', '.ttf':'font/ttf' }[ext] || 'application/octet-stream';
}

// ─── Header / footer for printed PDF ─────────────────────────────────────
function headerTemplate(meta) {
  return `
<style>
  .h { font-family: 'Inter', -apple-system, sans-serif; font-size: 8pt; color: #525252;
       width: 100%; padding: 0 16mm; box-sizing: border-box;
       display: flex; justify-content: space-between; align-items: center; }
  .h .left { font-weight: 600; color: #0a0a0a; }
  .h .right { font-style: italic; }
</style>
<div class="h">
  <span class="left">alexreyes.es</span>
  <span class="right">${esc(meta.titulo || '')}${meta.fecha ? ' · ' + esc(meta.fecha) : ''}${meta.mode === 'soluciones' ? ' · soluciones' : ''}</span>
</div>`;
}
function footerTemplate() {
  return `
<style>
  .f { font-family: 'Inter', -apple-system, sans-serif; font-size: 8pt; color: #525252;
       width: 100%; padding: 0 16mm; box-sizing: border-box;
       display: flex; justify-content: space-between; align-items: center; }
</style>
<div class="f">
  <span>&copy; 2026 Àlex Reyes · alexreyes.es</span>
  <span>Página <span class="pageNumber"></span> de <span class="totalPages"></span></span>
</div>`;
}
function esc(s) {
  return String(s).replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
}

// ─── Render a single combined exam page → PDF ────────────────────────────
async function renderExamPdf(browser, baseUrl, pages, mode, meta) {
  const ctx = await browser.newContext();
  const page = await ctx.newPage();

  if (KATEX_LOCAL_DIR) {
    await page.route('**/cdn.jsdelivr.net/**', async (route) => {
      const local = fileForCdnUrl(route.request().url());
      if (local && fs.existsSync(local)) {
        route.fulfill({ status: 200, contentType: contentTypeForExt(path.extname(local)),
                        body: fs.readFileSync(local) });
      } else { route.continue(); }
    });
  }

  // 1) Cargamos la PRIMERA pN.html como "página base" (trae <head> con todo el CSS+KaTeX)
  await page.goto(baseUrl + pages[0], { waitUntil: 'networkidle' });

  // Esperar libs
  await page.waitForFunction(
    () => typeof window.katex !== 'undefined' && typeof window.renderMathInElement === 'function',
    { timeout: 15000 }
  );

  // 2) Fetch el resto de pN.html, extraer .question-block de cada una y APPEND al main
  await page.evaluate(async ({ baseUrl, pages, mode }) => {
    const main = document.querySelector('main .container');
    if (!main) throw new Error('No se encontró main .container');

    // Quita TODO lo que no sea question-block en la página actual
    Array.from(main.children).forEach(el => {
      if (!el.classList || !el.classList.contains('question-block')) {
        // Conservamos el exam-header si existiera, lo eliminamos para flujo limpio
        if (el.classList && el.classList.contains('exam-header')) el.remove();
        else if (el.classList && el.classList.contains('breadcrumb')) el.remove();
        else if (el.tagName === 'NAV' || el.tagName === 'FOOTER') { /* fuera de main */ }
        else el.remove();
      }
    });

    // Append resto de páginas
    for (let i = 1; i < pages.length; i++) {
      const html = await fetch(baseUrl + pages[i]).then(r => r.text());
      const doc = new DOMParser().parseFromString(html, 'text/html');
      const block = doc.querySelector('.question-block');
      if (block) {
        // Separador minimalista entre preguntas
        const sep = document.createElement('div');
        sep.style.cssText = 'margin:0.5rem 0;';
        main.appendChild(sep);
        main.appendChild(block);
      }
    }

    // En todos los modos: dejar el H1 con solo "Pregunta N" (quitar todo lo que vaya después
    // del separador " · "), eliminar el descriptor y el score-pill.
    document.querySelectorAll('.question-block > h1').forEach(h => {
      // El texto puede contener · (middot) o &middot; ya entitizado. Cortamos en el primer punto medio.
      const t = h.textContent || '';
      const idx = t.indexOf('·');
      if (idx > -1) {
        h.textContent = t.slice(0, idx).trim();
      }
    });

    // Modo enunciados o soluciones — manipulamos DOM directamente
    if (mode === 'enunciados') {
      document.querySelectorAll('.solution, .apart-solution').forEach(el => el.remove());
      document.querySelectorAll('.solution-toggle, [data-toggles]').forEach(el => el.remove());
      document.querySelectorAll('details').forEach(d => {
        if (d.querySelector('.solution, .apart-solution, .final')) d.remove();
      });
    } else {
      document.querySelectorAll('.solution[hidden]').forEach(s => s.removeAttribute('hidden'));
      document.querySelectorAll('.solution').forEach(s => {
        s.style.display = 'block'; s.style.visibility = 'visible'; s.hidden = false;
      });
      document.querySelectorAll('details').forEach(d => d.setAttribute('open', ''));
      document.querySelectorAll('.solution-toggle').forEach(el => el.remove());
    }
  }, { baseUrl, pages, mode });

  // 3) Forzar render KaTeX sobre TODO el body actualizado
  await page.evaluate(() => {
    window.renderMathInElement(document.body, {
      delimiters: [
        { left: '$$', right: '$$', display: true },
        { left: '\\[', right: '\\]', display: true },
        { left: '$',  right: '$',  display: false },
        { left: '\\(', right: '\\)', display: false },
      ],
      throwOnError: false,
    });
  });
  await page.evaluate(() => document.fonts.ready);
  await page.waitForTimeout(800);

  // 4) Inyectar CSS de impresión — formato compacto, sin saltos forzados
  // En soluciones, cada pregunta arranca en página nueva; en enunciados fluyen seguidas.
  const breakRules = mode === 'soluciones'
    ? `.question-block { page-break-before: always !important; break-before: page !important;
                          page-break-after: auto !important; break-after: auto !important;
                          page-break-inside: auto !important; break-inside: auto !important; }
       .question-block:first-of-type { page-break-before: auto !important; break-before: auto !important; }`
    : `.question-block { page-break-before: auto !important; page-break-after: auto !important;
                          page-break-inside: auto !important;
                          break-before: auto !important; break-after: auto !important;
                          break-inside: auto !important; }`;
  await page.addStyleTag({ content: `
    @page { size: A4; margin: 18mm 16mm 18mm 16mm; }
    nav, footer, .breadcrumb, .exam-nav, .lang-sw, .nav-hamburger, .theme-btn,
    .pdf-download, .year-picker, .info-cta, .subject-notice, .exam-header { display: none !important; }
    .section-label, .tag, .ib-chips, .ib-chip, .ib-chips-label,
    .exam-meta, .question-cards, .kicker, .score-pill,
    .question-descriptor { display: none !important; }
    body { background: white !important; color: #000 !important;
           font-size: 10.5pt !important; line-height: 1.45 !important; }
    main { padding: 0 !important; }
    .container { padding: 0 !important; max-width: 100% !important; margin: 0 !important; }
    /* Reglas de salto de página: dependen del modo */
    ${breakRules}
    .question-block { border: none !important; padding: 0 !important;
                       margin: 0 0 0.6rem !important; }
    .question-block h1 { font-size: 1.05rem !important; margin: 0.2rem 0 0.3rem !important;
                          font-weight: 600 !important; }
    .statement, .apartados { margin: 0.2rem 0 0.4rem !important; }
    .apartados li { margin-bottom: 0.25rem !important; }
    h1, h2, h3, h4 { color: #000 !important; }
    .solution { margin-top: 0.5rem !important; padding: 0.6rem 0.8rem !important; }
    .solution h3 { font-size: 0.9rem !important; margin-bottom: 0.4rem !important; }
    .apartado-sol { margin: 0.4rem 0 !important; }
    .apartado-sol h4 { font-size: 0.95rem !important; margin: 0.3rem 0 0.2rem !important; }
    .math-block { margin: 0.3rem 0 !important; padding: 0.2rem 0 !important; }
    /* Solo evitamos romper bloques matemáticos a media línea */
    .katex-display { page-break-inside: avoid; }
  `});
  await page.emulateMedia({ media: 'print' });

  const pdfBytes = await page.pdf({
    format: 'A4',
    printBackground: false,
    margin: { top: '22mm', right: '16mm', bottom: '22mm', left: '16mm' },
    displayHeaderFooter: true,
    headerTemplate: headerTemplate({ ...meta, mode }),
    footerTemplate: footerTemplate(),
  });
  await ctx.close();
  return pdfBytes;
}

// ─── Main ────────────────────────────────────────────────────────────────
async function main() {
  const repoRoot = path.resolve(process.argv[2] || '.');
  const examRel = process.argv[3];
  if (!examRel) { console.error('Uso: node regen-exam-pdf.js <repo-root> <ruta-relativa-examen>'); process.exit(2); }
  const examDir = path.join(repoRoot, examRel);
  if (!fs.existsSync(examDir)) { console.error('No existe:', examDir); process.exit(2); }

  const examId = path.basename(examDir);
  const jsonPath = path.join(repoRoot, 'assets/data/ejercicios', examId + '.json');
  let meta = { titulo: examId, fecha: '', grupo: '' };
  if (fs.existsSync(jsonPath)) {
    try { const j = JSON.parse(fs.readFileSync(jsonPath));
          meta = { titulo: j.titulo || examId, fecha: j.fecha || '', grupo: j.grupo || '' }; } catch (e) {}
  }

  const pages = fs.readdirSync(examDir)
    .filter(f => /^p\d+\.html$/.test(f))
    .sort((a, b) => parseInt(a.match(/\d+/)[0]) - parseInt(b.match(/\d+/)[0]));
  if (pages.length === 0) { console.error('No hay pN.html en', examDir); process.exit(2); }

  console.log(`Examen: ${examRel}`);
  console.log(`Título: ${meta.titulo}`);
  console.log(`Páginas: ${pages.join(', ')}`);

  const server = await serveStatic(repoRoot);
  const baseUrl = `http://127.0.0.1:${PORT}/${examRel.replace(/\\/g, '/')}/`;
  const browser = await chromium.launch();

  for (const mode of ['enunciados', 'soluciones']) {
    console.log(`\n[modo ${mode}]`);
    const pdfBytes = await renderExamPdf(browser, baseUrl, pages, mode, meta);
    const outPath = path.join(examDir, `original-${mode}.pdf`);
    fs.writeFileSync(outPath, pdfBytes);
    console.log(`  ✓ ${outPath} (${(pdfBytes.length/1024).toFixed(1)} KB)`);
  }

  await browser.close();
  server.close();
}

main().catch(e => { console.error(e); process.exit(1); });
