#!/usr/bin/env python3
"""[ONE-SHOT] Genera p1..p3 del Global 1a Avaluació de 1BTL MACS (id 2526-1btl-macs-t1t).

Es deixa al repo perquè queda més fàcil tornar-lo a executar si cal regenerar
les pàgines, però la font de veritat un cop pujades són els fitxers HTML
mateixos a /aula/ccss-1btl/examenes/2526-1btl-macs-t1t/.
"""
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
OUT = REPO / "aula" / "ccss-1btl" / "examenes" / "2526-1btl-macs-t1t"

SHELL = """<!DOCTYPE html>
<html lang="ca">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title}</title>
<meta name="description" content="{descripcion}">
<script>(function(){{var s=localStorage.getItem('theme');if(s)document.documentElement.setAttribute('data-theme',s);else document.documentElement.setAttribute('data-theme','light');}})();</script>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/katex.min.css">
<script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/katex.min.js"></script>
<script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/contrib/auto-render.min.js" onload="renderMathInElement(document.body,{{delimiters:[{{left:'$$',right:'$$',display:true}},{{left:'\\\\[',right:'\\\\]',display:true}},{{left:'$',right:'$',display:false}},{{left:'\\\\(',right:'\\\\)',display:false}}],throwOnError:false}})"></script>
<link rel="stylesheet" href="/style.css">
<link rel="stylesheet" href="/assets/css/examenes.css">
<link rel="icon" type="image/svg+xml" href="/favicon.svg">
<link rel="canonical" href="https://alexreyes.es/aula/ccss-1btl/examenes/2526-1btl-macs-t1t/{file}.html">
</head>
<body>
<nav>
  <div class="nav-inner">
    <a href="/" class="nav-brand">alexreyes.es</a>
    <div class="nav-links">
      <a href="/docencia/" class="nav-active">Docencia</a>
      <a href="/doctorado/">Doctorado</a>
      <a href="/notas/">Notas</a>
      <a href="/cv/">CV</a>
      <a href="/contacto/">Contacto</a>
    </div>
    <div class="nav-right">
      <button class="nav-hamburger" onclick="toggleMenu()" aria-label="Menu"><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><line x1="4" y1="7" x2="20" y2="7"/><line x1="4" y1="12" x2="20" y2="12"/><line x1="4" y1="17" x2="20" y2="17"/></svg></button>
      <button class="theme-btn" onclick="toggleTheme()" aria-label="Toggle theme">
        <svg class="icon-sun" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="5"/><line x1="12" y1="1" x2="12" y2="3"/><line x1="12" y1="21" x2="12" y2="23"/><line x1="4.22" y1="4.22" x2="5.64" y2="5.64"/><line x1="18.36" y1="18.36" x2="19.78" y2="19.78"/><line x1="1" y1="12" x2="3" y2="12"/><line x1="21" y1="12" x2="23" y2="12"/><line x1="4.22" y1="19.78" x2="5.64" y2="18.36"/><line x1="18.36" y1="5.64" x2="19.78" y2="4.22"/></svg>
        <svg class="icon-moon" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/></svg>
      </button>
    </div>
  </div>
</nav>

<main>
  <div class="container" style="padding-top:1.5rem;padding-bottom:5rem">

    <div class="breadcrumb">
      <a href="/">Inicio</a>
      <span class="sep">/</span>
      <a href="/docencia/">Docencia</a>
      <span class="sep">/</span>
      <a href="/aula/ccss-1btl/examenes/2526-1btl-macs-t1t/">Global 1a avaluació · 1r BTL MACS</a>
      <span class="sep">/</span>
      <span class="current">P{numero}</span>
    </div>

    <div class="exam-header" style="padding-top:0;border-bottom:none;margin-bottom:0.5rem">
      <div style="display:flex;gap:0.5rem;flex-wrap:wrap;margin-bottom:0.4rem">
        <span class="section-label">1r BTL · MACS</span>
        <span class="tag tag-orange">25/11/2025</span>
      </div>
    </div>

    <nav class="exam-nav" aria-label="Navegació de l'examen">
      {prev_link}
      <a class="index" href="/aula/ccss-1btl/examenes/2526-1btl-macs-t1t/">Índex de l'examen</a>
      {next_link}
    </nav>

    <article class="question-block">
      <h1>Pregunta {numero} &middot; {titol}</h1>
      <p class="question-descriptor">{descriptor}</p>
      <span class="score-pill">Puntuació màxima · {puntuacio}</span>

      <div class="statement">
{enunciat}
      </div>

      <div class="ib-chips">
        <span class="ib-chips-label">Bachillerato CCSS · Bloc {bloc}</span>
        <span class="ib-chip" data-descriptor="{chip_descr}">{chip_label}</span>
      </div>

      <button class="solution-toggle" data-toggles="sol-p{numero}" data-show-label="Mostra la correcció" data-hide-label="Amaga la correcció" onclick="toggleSolucion('sol-p{numero}')">
        <span class="toggle-label">Mostra la correcció</span>
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="6 9 12 15 18 9"/></svg>
      </button>

      <section class="solution" id="sol-p{numero}" hidden>
{solucio}
      </section>
    </article>

    <nav class="exam-nav" aria-label="Navegació de l'examen">
      {prev_link}
      <a class="index" href="/aula/ccss-1btl/examenes/2526-1btl-macs-t1t/">Índex de l'examen</a>
      {next_link}
    </nav>

  </div>
</main>

<footer>
  <div class="container">
    <div class="footer-inner">
      <span><strong>Àlex Reyes</strong> &middot; Matemáticas, docencia y doctorado</span>
      <span>Barcelona &middot; 2026</span>
    </div>
  </div>
</footer>

<script src="/assets/js/examenes.js"></script>
<script>
function toggleMenu(){{document.querySelector("nav").classList.toggle("open");}}
function toggleTheme(){{var h=document.documentElement,n=h.getAttribute('data-theme')==='dark'?'light':'dark';h.setAttribute('data-theme',n);localStorage.setItem('theme',n);}}
</script>
</body>
</html>
"""

PAGES = [
    {
        "numero": 1,
        "titol": "Operacions amb radicals, potències i logaritmes",
        "descriptor": "Simplificació, racionalització i propietats bàsiques de potències i logaritmes.",
        "puntuacio": "3 punts",
        "bloc": "A",
        "chip_label": "Radicals + log",
        "chip_descr": "Simplificació amb radicals, potències racionals i logaritmes",
        "descripcion": "Pregunta 1 del Global 1a Avaluació de 1r BTL MACS: simplificació de sis expressions amb radicals, potències i logaritmes.",
        "enunciat": """
        <div class="context">
          <p>Expressa el resultat, operant pas a pas, de les operacions següents simplificant i/o racionalitzant.</p>
        </div>
        <ol class="apartados">
          <li>$\\dfrac{9\\sqrt{8} - 3\\sqrt{72}}{\\sqrt{2}} + \\sqrt{49} - \\left(27^{1/3}\\right)\\!\\left(8^{2/3}\\right)$ <span class="apartado-puntos">0,5 p</span></li>
          <li>$\\log\\!\\left(\\dfrac{100\\sqrt{10}}{0{,}01}\\right) - \\log(10^{3})$ <span class="apartado-puntos">0,5 p</span></li>
          <li>$\\log_{2} 32 - \\log_{2}\\!\\left(\\dfrac{1}{8}\\right) + \\log_{2}\\!\\left(\\sqrt{2}\\right)$ <span class="apartado-puntos">0,5 p</span></li>
          <li>$\\dfrac{5^{-2} \\cdot \\sqrt{125}}{\\,(1/25)^{1{,}5}\\,}$ <span class="apartado-puntos">0,5 p</span></li>
          <li>$\\log_{3}\\!\\left(\\sqrt[3]{3} \\cdot \\sqrt{27}\\right)$ <span class="apartado-puntos">0,5 p</span></li>
          <li>$\\dfrac{4}{2 - \\sqrt{3}}$ &nbsp;(racionalitza el denominador) <span class="apartado-puntos">0,5 p</span></li>
        </ol>
""",
        "solucio": """
        <h3>Correcció pas a pas</h3>
        <p class="note"><strong>Idea clau:</strong> totes aquestes expressions es resolen passant-ho a base comuna (radicals a $\\sqrt{2}$, potències a $5$ o $3$, logaritmes a la mateixa base) i aplicant les propietats: $a^{m} a^{n} = a^{m+n}$, $\\log_{b}(xy) = \\log_{b} x + \\log_{b} y$, etc.</p>

        <div class="apartado-sol">
          <h4><span class="letra">a)</span> $\\dfrac{9\\sqrt{8} - 3\\sqrt{72}}{\\sqrt{2}} + \\sqrt{49} - \\left(27^{1/3}\\right)\\!\\left(8^{2/3}\\right)$</h4>
          <p>Simplifiquem cada radical: $\\sqrt{8} = 2\\sqrt{2}$, $\\sqrt{72} = 6\\sqrt{2}$, $\\sqrt{49} = 7$, $27^{1/3} = 3$, $8^{2/3} = (2^{3})^{2/3} = 4$.</p>
          <div class="math-block">
            $$\\dfrac{9 \\cdot 2\\sqrt{2} - 3 \\cdot 6\\sqrt{2}}{\\sqrt{2}} = \\dfrac{18\\sqrt{2} - 18\\sqrt{2}}{\\sqrt{2}} = 0.$$
          </div>
          <p>Substituïm: $0 + 7 - 3 \\cdot 4 = 7 - 12$.</p>
          <div class="final">$= -5$.</div>
        </div>

        <div class="apartado-sol">
          <h4><span class="letra">b)</span> $\\log\\!\\left(\\dfrac{100\\sqrt{10}}{0{,}01}\\right) - \\log(10^{3})$</h4>
          <p>Posem-ho tot en base $10$: $100 = 10^{2}$, $\\sqrt{10} = 10^{1/2}$, $0{,}01 = 10^{-2}$.</p>
          <div class="math-block">
            $$\\log\\!\\left(\\dfrac{10^{2} \\cdot 10^{1/2}}{10^{-2}}\\right) = \\log(10^{2+1/2-(-2)}) = \\log(10^{9/2}) = \\tfrac{9}{2}.$$
          </div>
          <p>I $\\log(10^{3}) = 3$. Restem:</p>
          <div class="final">$\\tfrac{9}{2} - 3 = \\tfrac{3}{2}$.</div>
        </div>

        <div class="apartado-sol">
          <h4><span class="letra">c)</span> $\\log_{2} 32 - \\log_{2}\\!\\left(\\tfrac{1}{8}\\right) + \\log_{2}\\!\\left(\\sqrt{2}\\right)$</h4>
          <p>Tot en potències de $2$: $32 = 2^{5}$, $\\tfrac{1}{8} = 2^{-3}$, $\\sqrt{2} = 2^{1/2}$.</p>
          <div class="math-block">
            $$\\log_{2}(2^{5}) - \\log_{2}(2^{-3}) + \\log_{2}(2^{1/2}) = 5 - (-3) + \\tfrac{1}{2} = 8 + \\tfrac{1}{2}.$$
          </div>
          <div class="final">$= \\tfrac{17}{2}$.</div>
        </div>

        <div class="apartado-sol">
          <h4><span class="letra">d)</span> $\\dfrac{5^{-2} \\cdot \\sqrt{125}}{(1/25)^{1{,}5}}$</h4>
          <p>Tot en base $5$: $\\sqrt{125} = 5^{3/2}$ i $(1/25)^{1{,}5} = (5^{-2})^{3/2} = 5^{-3}$.</p>
          <div class="math-block">
            $$\\dfrac{5^{-2} \\cdot 5^{3/2}}{5^{-3}} = 5^{-2 + 3/2 - (-3)} = 5^{5/2}.$$
          </div>
          <p>I $5^{5/2} = 5^{2} \\cdot 5^{1/2} = 25\\sqrt{5}$.</p>
          <div class="final">$= 25\\sqrt{5}$.</div>
        </div>

        <div class="apartado-sol">
          <h4><span class="letra">e)</span> $\\log_{3}\\!\\left(\\sqrt[3]{3} \\cdot \\sqrt{27}\\right)$</h4>
          <p>$\\sqrt[3]{3} = 3^{1/3}$ i $\\sqrt{27} = (3^{3})^{1/2} = 3^{3/2}$. Producte $= 3^{1/3 + 3/2} = 3^{11/6}$.</p>
          <div class="math-block">
            $$\\log_{3}(3^{11/6}) = \\tfrac{11}{6}.$$
          </div>
          <div class="final">$= \\tfrac{11}{6}$.</div>
        </div>

        <div class="apartado-sol">
          <h4><span class="letra">f)</span> $\\dfrac{4}{2 - \\sqrt{3}}$ (racionalitzar)</h4>
          <p>Multipliquem numerador i denominador pel conjugat $2 + \\sqrt{3}$:</p>
          <div class="math-block">
            $$\\dfrac{4}{2 - \\sqrt{3}} \\cdot \\dfrac{2 + \\sqrt{3}}{2 + \\sqrt{3}} = \\dfrac{4(2+\\sqrt{3})}{2^{2} - (\\sqrt{3})^{2}} = \\dfrac{4(2+\\sqrt{3})}{4 - 3} = 4(2+\\sqrt{3}).$$
          </div>
          <div class="final">$= 8 + 4\\sqrt{3}$.</div>
        </div>
""",
    },
    {
        "numero": 2,
        "titol": "Polinomis: factorització, MCD i MCM",
        "descriptor": "Factorització de dues expressions, càlcul de MCD/MCM i una operació amb fraccions algebraiques.",
        "puntuacio": "2 punts",
        "bloc": "D",
        "chip_label": "Polinomis",
        "chip_descr": "Factorització, MCD i MCM de polinomis i operació amb fraccions algebraiques",
        "descripcion": "Pregunta 2 del Global 1a Avaluació de 1r BTL MACS: factorització, MCD/MCM i operació amb fraccions algebraiques.",
        "enunciat": """
        <div class="context">
          <p>Donats els polinomis $p(x) = 3x^{3} - 27x$ i $q(x) = 2x^{2} - 10x + 12$.</p>
        </div>
        <ol class="apartados">
          <li>Factoritza els polinomis $p(x)$ i $q(x)$. <span class="apartado-puntos">0,5 p</span></li>
          <li>Calcula el MCD i el MCM de $p(x)$ i $q(x)$. <span class="apartado-puntos">0,5 p</span></li>
          <li>Calcula i simplifica $\\dfrac{p(x)}{q(x)} - \\dfrac{x^{2} + 2x}{x^{2} - 4}$. <span class="apartado-puntos">1 p</span></li>
        </ol>
""",
        "solucio": """
        <h3>Correcció pas a pas</h3>
        <p class="note"><strong>Idea clau:</strong> traiem primer factor comú (el coeficient i les $x$) i després apliquem productes notables o Ruffini per acabar de factoritzar. Una vegada factoritzats, el MCD és el producte dels factors comuns amb la mínima multiplicitat i el MCM dels factors amb la màxima multiplicitat (incloses les constants amb $\\gcd$ i $\\mathrm{lcm}$).</p>

        <div class="apartado-sol">
          <h4><span class="letra">a)</span> Factorització</h4>
          <p>$p(x) = 3x^{3} - 27x = 3x(x^{2} - 9) = 3x(x-3)(x+3)$ (diferència de quadrats).</p>
          <p>$q(x) = 2x^{2} - 10x + 12 = 2(x^{2} - 5x + 6) = 2(x-2)(x-3)$.</p>
          <div class="final">$p(x) = 3x(x-3)(x+3)$, &nbsp; $q(x) = 2(x-2)(x-3)$.</div>
        </div>

        <div class="apartado-sol">
          <h4><span class="letra">b)</span> MCD i MCM</h4>
          <p>Factor comú: només $(x-3)$. Coeficients: $\\gcd(3,2) = 1$, $\\mathrm{lcm}(3,2) = 6$.</p>
          <ul>
            <li>$\\mathrm{MCD}(p, q) = (x-3)$.</li>
            <li>$\\mathrm{MCM}(p, q) = 6 x (x-3)(x+3)(x-2)$.</li>
          </ul>
          <div class="final">$\\mathrm{MCD} = (x-3)$, &nbsp; $\\mathrm{MCM} = 6x(x-3)(x+3)(x-2)$.</div>
        </div>

        <div class="apartado-sol">
          <h4><span class="letra">c)</span> $\\dfrac{p(x)}{q(x)} - \\dfrac{x^{2} + 2x}{x^{2} - 4}$</h4>
          <p>Substituïm i simplifiquem cada fracció:</p>
          <div class="math-block">
            $$\\dfrac{p(x)}{q(x)} = \\dfrac{3x(x-3)(x+3)}{2(x-2)(x-3)} = \\dfrac{3x(x+3)}{2(x-2)}, \\quad \\dfrac{x^{2}+2x}{x^{2}-4} = \\dfrac{x(x+2)}{(x-2)(x+2)} = \\dfrac{x}{x-2}.$$
          </div>
          <p>Comú denominador $2(x-2)$:</p>
          <div class="math-block">
            $$\\dfrac{3x(x+3)}{2(x-2)} - \\dfrac{2x}{2(x-2)} = \\dfrac{3x^{2} + 9x - 2x}{2(x-2)} = \\dfrac{3x^{2} + 7x}{2(x-2)} = \\dfrac{x(3x+7)}{2(x-2)}.$$
          </div>
          <div class="final">$= \\dfrac{x(3x+7)}{2(x-2)}$ &nbsp; (definida si $x \\neq 2$, $x \\neq 3$).</div>
        </div>
""",
    },
    {
        "numero": 3,
        "titol": "Equacions i sistemes — escollir 5 de 8",
        "descriptor": "Vuit problemes diversos (radicals, exponencials, logarítmiques, valor absolut, biquadrada, racional i dos sistemes); resolts tots amb verificació.",
        "puntuacio": "5 punts",
        "bloc": "D",
        "chip_label": "Equacions + sistemes",
        "chip_descr": "Resolució analítica i verificació de solucions",
        "descripcion": "Pregunta 3 del Global 1a Avaluació de 1r BTL MACS: vuit equacions/sistemes (cal triar-ne 5 a l'examen).",
        "enunciat": """
        <div class="context">
          <p>Resol, verificant les solucions, <strong>5 de les equacions o sistemes següents</strong>. Aquí els tens tots resolts.</p>
        </div>
        <ol class="apartados">
          <li>$\\sqrt{x+5} + \\sqrt{x-4} = 9$ <span class="apartado-puntos">0,625 p</span></li>
          <li>$3^{2x} - 10 \\cdot 3^{x} + 9 = 0$ <span class="apartado-puntos">0,625 p</span></li>
          <li>$2\\log_{5}(x+2) - \\log_{5}(2x-1) = 1 - \\log_{5}(x-2)$ <span class="apartado-puntos">0,625 p</span></li>
          <li>$|3x-9| + 1 = |x|$ <span class="apartado-puntos">0,625 p</span></li>
          <li>$x^{4} + 36 = 13x^{2}$ <span class="apartado-puntos">0,625 p</span></li>
          <li>$\\dfrac{x}{x-2} + \\dfrac{1}{x+2} = 1 - \\dfrac{2}{x^{2}-4}$ <span class="apartado-puntos">0,625 p</span></li>
          <li>Sistema: $\\begin{cases} x^{2} + y^{2} = 25 \\\\ y = x + 1 \\end{cases}$ <span class="apartado-puntos">0,625 p</span></li>
          <li>Sistema: $\\begin{cases} \\log(x) + \\log(y^{2}) = 4 \\\\ \\log(x/y) = 1 \\end{cases}$ <span class="apartado-puntos">0,625 p</span></li>
        </ol>
""",
        "solucio": """
        <h3>Correcció pas a pas</h3>
        <p class="note"><strong>Idea clau:</strong> totes aquestes equacions es resolen aïllant la part "complicada" (radical, exponencial, logaritme, valor absolut o fracció), elevant al quadrat / canvi de variable / aplicant propietats de logaritmes / casos del valor absolut / mínim comú múltiple, i sempre <strong>verificant</strong> les solucions al final perquè aquestes manipulacions poden afegir solucions estranyes.</p>

        <div class="apartado-sol">
          <h4><span class="letra">a)</span> $\\sqrt{x+5} + \\sqrt{x-4} = 9$</h4>
          <p>Sigui $u = \\sqrt{x+5}$, $v = \\sqrt{x-4}$. Tenim $u+v = 9$ i $u^{2} - v^{2} = (x+5) - (x-4) = 9$.</p>
          <p>Però $u^{2} - v^{2} = (u-v)(u+v) = (u-v) \\cdot 9 = 9$, així que $u - v = 1$. Combinant amb $u+v=9$: $u=5$, $v=4$.</p>
          <p>De $u^{2} = x+5 = 25$ surt $x = 20$. Verificació: $\\sqrt{25} + \\sqrt{16} = 5 + 4 = 9$ ✓.</p>
          <div class="final">$x = 20$.</div>
        </div>

        <div class="apartado-sol">
          <h4><span class="letra">b)</span> $3^{2x} - 10 \\cdot 3^{x} + 9 = 0$</h4>
          <p>Canvi de variable: $y = 3^{x} > 0$. L'equació esdevé $y^{2} - 10y + 9 = 0$ amb solucions $y = 9$ o $y = 1$.</p>
          <p>$3^{x} = 9 \\Rightarrow x = 2$, &nbsp; $3^{x} = 1 \\Rightarrow x = 0$. Verificació: $3^{4} - 10 \\cdot 3^{2} + 9 = 81 - 90 + 9 = 0$ ✓; $1 - 10 + 9 = 0$ ✓.</p>
          <div class="final">$x = 0$ i $x = 2$.</div>
        </div>

        <div class="apartado-sol">
          <h4><span class="letra">c)</span> $2\\log_{5}(x+2) - \\log_{5}(2x-1) = 1 - \\log_{5}(x-2)$</h4>
          <p>Domini: $x+2>0$, $2x-1>0$, $x-2>0$ → $x > 2$. Reagrupant logaritmes a un costat:</p>
          <div class="math-block">
            $$\\log_{5}\\!\\left(\\dfrac{(x+2)^{2}(x-2)}{2x-1}\\right) = 1 \\;\\Longleftrightarrow\\; \\dfrac{(x+2)^{2}(x-2)}{2x-1} = 5.$$
          </div>
          <p>Desenvolupant: $(x+2)^{2}(x-2) = (x^{2}+4x+4)(x-2) = x^{3} + 2x^{2} - 4x - 8$, i $5(2x-1) = 10x - 5$. Igualant:</p>
          <div class="math-block">
            $$x^{3} + 2x^{2} - 14x - 3 = 0.$$
          </div>
          <p>Provant $x = 3$: $27 + 18 - 42 - 3 = 0$ ✓. Dividint per $(x-3)$ (Ruffini): $x^{3} + 2x^{2} - 14x - 3 = (x-3)(x^{2} + 5x + 1)$. L'altra factor té arrels $x = \\dfrac{-5 \\pm \\sqrt{21}}{2}$, ambdues fora del domini ($\\approx -0{,}21$ i $\\approx -4{,}79$).</p>
          <p>Verificació de $x = 3$: $2\\log_{5} 5 - \\log_{5} 5 = 2 - 1 = 1$, i $1 - \\log_{5} 1 = 1 - 0 = 1$ ✓.</p>
          <div class="final">$x = 3$.</div>
        </div>

        <div class="apartado-sol">
          <h4><span class="letra">d)</span> $|3x - 9| + 1 = |x|$</h4>
          <p>Punts on canvien els signes: $3x-9 = 0 \\Rightarrow x = 3$ i $x = 0$. Estudiem cada zona:</p>
          <ul>
            <li><strong>$x \\ge 3$:</strong> $3x-9 \\ge 0$ i $x \\ge 0$. L'equació $\\to (3x-9)+1 = x \\Rightarrow 2x = 8 \\Rightarrow x = 4$ ✓.</li>
            <li><strong>$0 \\le x < 3$:</strong> $3x-9 < 0$, $x \\ge 0$. $\\to (9-3x)+1 = x \\Rightarrow 10 = 4x \\Rightarrow x = \\tfrac{5}{2}$ ✓.</li>
            <li><strong>$x < 0$:</strong> $3x-9 < 0$, $x < 0$. $\\to (9-3x)+1 = -x \\Rightarrow 10 = 2x \\Rightarrow x = 5$ ✗ (no és $<0$).</li>
          </ul>
          <p>Verificació: $|3 \\cdot 4 - 9|+1 = 3+1 = 4 = |4|$ ✓; $|3 \\cdot \\tfrac{5}{2} - 9|+1 = \\tfrac{3}{2}+1 = \\tfrac{5}{2} = |\\tfrac{5}{2}|$ ✓.</p>
          <div class="final">$x = 4$ i $x = \\tfrac{5}{2}$.</div>
        </div>

        <div class="apartado-sol">
          <h4><span class="letra">e)</span> $x^{4} + 36 = 13x^{2}$</h4>
          <p>Equació biquadrada: $y = x^{2}$. $y^{2} - 13y + 36 = 0 \\Rightarrow y = \\dfrac{13 \\pm 5}{2} = 9$ o $4$.</p>
          <p>$x^{2} = 9 \\Rightarrow x = \\pm 3$, &nbsp; $x^{2} = 4 \\Rightarrow x = \\pm 2$.</p>
          <div class="final">$x \\in \\{-3, -2, 2, 3\\}$.</div>
        </div>

        <div class="apartado-sol">
          <h4><span class="letra">f)</span> $\\dfrac{x}{x-2} + \\dfrac{1}{x+2} = 1 - \\dfrac{2}{x^{2}-4}$</h4>
          <p>Domini: $x \\neq \\pm 2$. Multipliquem per $x^{2} - 4 = (x-2)(x+2)$:</p>
          <div class="math-block">
            $$x(x+2) + (x-2) = (x^{2} - 4) - 2.$$
          </div>
          <p>Desenvolupem: $x^{2} + 2x + x - 2 = x^{2} - 6 \\;\\Longleftrightarrow\\; x^{2} + 3x - 2 = x^{2} - 6 \\;\\Longleftrightarrow\\; 3x = -4$.</p>
          <p>Verificació: $x = -\\tfrac{4}{3}$ no anul·la cap denominador.</p>
          <div class="final">$x = -\\dfrac{4}{3}$.</div>
        </div>

        <div class="apartado-sol">
          <h4><span class="letra">g)</span> Sistema: $x^{2} + y^{2} = 25$, $y = x + 1$</h4>
          <p>Substituïm $y = x+1$ a la primera: $x^{2} + (x+1)^{2} = 25 \\Rightarrow 2x^{2} + 2x - 24 = 0 \\Rightarrow x^{2} + x - 12 = 0$.</p>
          <p>$x = \\dfrac{-1 \\pm 7}{2} = 3$ o $-4$. Llavors $y = x+1$ dona $4$ o $-3$.</p>
          <p>Verificació: $9+16 = 25$ ✓ i $16+9 = 25$ ✓.</p>
          <div class="final">$(x, y) = (3, 4)$ &nbsp; i &nbsp; $(x, y) = (-4, -3)$.</div>
        </div>

        <div class="apartado-sol">
          <h4><span class="letra">h)</span> Sistema: $\\log(x) + \\log(y^{2}) = 4$, $\\log(x/y) = 1$</h4>
          <p>De la segona: $x/y = 10 \\Rightarrow x = 10y$. De la primera: $\\log(xy^{2}) = 4 \\Rightarrow xy^{2} = 10^{4}$.</p>
          <p>Substituïm $x = 10y$: $10y \\cdot y^{2} = 10y^{3} = 10\\,000 \\Rightarrow y^{3} = 1\\,000 \\Rightarrow y = 10$. Llavors $x = 100$.</p>
          <p>Verificació: $\\log 100 + \\log 100 = 2 + 2 = 4$ ✓; $\\log(100/10) = \\log 10 = 1$ ✓.</p>
          <div class="final">$(x, y) = (100, 10)$.</div>
        </div>
""",
    },
]


def render(p):
    n = p["numero"]
    prev_link = (
        f'<a class="prev" href="/aula/ccss-1btl/examenes/2526-1btl-macs-t1t/p{n-1}.html">&larr; Pregunta anterior</a>'
        if n > 1
        else '<span class="disabled prev">&larr; Pregunta anterior</span>'
    )
    next_link = (
        f'<a class="next" href="/aula/ccss-1btl/examenes/2526-1btl-macs-t1t/p{n+1}.html">Pregunta següent &rarr;</a>'
        if n < 3
        else '<span class="disabled next">Pregunta següent &rarr;</span>'
    )
    return SHELL.format(
        title=f"P{n} · {p['titol']} — 1r BTL MACS",
        descripcion=p["descripcion"],
        file=f"p{n}",
        numero=n,
        prev_link=prev_link,
        next_link=next_link,
        titol=p["titol"],
        descriptor=p["descriptor"],
        puntuacio=p["puntuacio"],
        bloc=p["bloc"],
        chip_label=p["chip_label"],
        chip_descr=p["chip_descr"],
        enunciat=p["enunciat"],
        solucio=p["solucio"],
    )


def main():
    for p in PAGES:
        out = OUT / f"p{p['numero']}.html"
        out.write_text(render(p), encoding="utf-8")
        print(f"  ✓ {out.relative_to(REPO)}")


if __name__ == "__main__":
    main()
