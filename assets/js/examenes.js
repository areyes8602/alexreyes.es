/* ============================================================
   /aula/ — interacciones de las páginas de exámenes
   - toggle de bloques de corrección
   - re-tipografiado KaTeX al desplegar por primera vez
   - preferencia en localStorage: solutions-default (opcional)
   ============================================================ */

const LS_KEY = 'solutions-default-open';

function toggleSolucion(id) {
  const sol = document.getElementById(id);
  if (!sol) return;
  const btn = document.querySelector(`[data-toggles="${id}"]`);
  const isOpen = !sol.hasAttribute('hidden');

  if (isOpen) {
    sol.setAttribute('hidden', '');
    if (btn) {
      btn.classList.remove('open');
      btn.querySelector('.toggle-label').textContent = btn.dataset.showLabel || 'Mostrar corrección';
    }
  } else {
    sol.removeAttribute('hidden');
    if (btn) {
      btn.classList.add('open');
      btn.querySelector('.toggle-label').textContent = btn.dataset.hideLabel || 'Ocultar corrección';
    }
    // KaTeX auto-render del bloque si está disponible
    if (window.renderMathInElement && !sol.dataset.rendered) {
      try {
        window.renderMathInElement(sol, {
          delimiters: [
            { left: '$$', right: '$$', display: true },
            { left: '\\[', right: '\\]', display: true },
            { left: '$', right: '$', display: false },
            { left: '\\(', right: '\\)', display: false }
          ],
          throwOnError: false
        });
        sol.dataset.rendered = '1';
      } catch (e) { /* ignore */ }
    }
  }
}

// Opcional: recordar preferencia de "todas las correcciones abiertas por defecto"
function setSolutionsDefault(open) {
  if (open) localStorage.setItem(LS_KEY, '1');
  else localStorage.removeItem(LS_KEY);
}

function applySolutionsDefault() {
  if (localStorage.getItem(LS_KEY) !== '1') return;
  document.querySelectorAll('.solution[hidden]').forEach(sol => {
    toggleSolucion(sol.id);
  });
}

// Aplicar preferencia cuando KaTeX haya cargado (para re-render correcto)
document.addEventListener('DOMContentLoaded', () => {
  if (window.renderMathInElement) {
    applySolutionsDefault();
  } else {
    // Esperar al script de auto-render de KaTeX
    window.addEventListener('load', () => setTimeout(applySolutionsDefault, 100));
  }
});
