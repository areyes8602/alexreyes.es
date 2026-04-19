export const languages = {
  es: 'Español',
  ca: 'Català',
  en: 'English',
};

export const defaultLang = 'es';

export const ui = {
  es: {
    'nav.home': 'Inicio',
    'nav.docencia': 'Docencia',
    'nav.investigacion': 'Investigación',
    'nav.blog': 'Notas',
    'nav.cv': 'CV',
    'nav.contacto': 'Contacto',
    'hero.badge': 'Profesor · Investigador',
    'hero.title': 'Matemáticas que enseño, aprendo e investigo.',
    'hero.description': 'Profesor de matemáticas en Barcelona e investigador independiente. Este es mi espacio de trabajo: materiales docentes, notas de investigación y visualizaciones interactivas.',
    'hero.cta.research': 'Ver investigación',
    'hero.cta.teaching': 'Docencia',
    'section.teaching': 'Docencia',
    'section.research': 'Investigación',
    'section.latest': 'Últimas notas',
    'teaching.description': 'Materiales, exámenes y recursos para las asignaturas que imparto. Algunos son públicos; otros requieren acceso.',
    'research.description': 'Trabajo en curso sobre dinámica modular fractal y la conjetura de Collatz. Paper en preparación para arXiv.',
    'access.public': 'público',
    'access.private': 'privado',
    'access.interactive': 'interactivo',
    'access.soon': 'pronto',
    'access.classroom': 'aula',
    'access.preprint': 'preprint',
    'footer.rights': 'Àlex Reyes · Matemáticas, docencia e investigación · Barcelona',
    'meta.center': 'Col·legi Maristes Sants — Les Corts',
    'meta.since': 'Desde 2010',
    'meta.field': 'Matemáticas',
  },
  ca: {
    'nav.home': 'Inici',
    'nav.docencia': 'Docència',
    'nav.investigacion': 'Recerca',
    'nav.blog': 'Notes',
    'nav.cv': 'CV',
    'nav.contacto': 'Contacte',
    'hero.badge': 'Professor · Investigador',
    'hero.title': 'Matemàtiques que ensenyo, aprenc i investigo.',
    'hero.description': 'Professor de matemàtiques a Barcelona i investigador independent. Aquest és el meu espai de treball: materials docents, notes de recerca i visualitzacions interactives.',
    'hero.cta.research': 'Veure recerca',
    'hero.cta.teaching': 'Docència',
    'section.teaching': 'Docència',
    'section.research': 'Recerca',
    'section.latest': 'Últimes notes',
    'teaching.description': 'Materials, exàmens i recursos per a les assignatures que imparteixo. Alguns són públics; d\'altres requereixen accés.',
    'research.description': 'Treball en curs sobre dinàmica modular fractal i la conjectura de Collatz. Article en preparació per a arXiv.',
    'access.public': 'públic',
    'access.private': 'privat',
    'access.interactive': 'interactiu',
    'access.soon': 'aviat',
    'access.classroom': 'aula',
    'access.preprint': 'preprint',
    'footer.rights': 'Àlex Reyes · Matemàtiques, docència i recerca · Barcelona',
    'meta.center': 'Col·legi Maristes Sants — Les Corts',
    'meta.since': 'Des de 2010',
    'meta.field': 'Matemàtiques',
  },
  en: {
    'nav.home': 'Home',
    'nav.docencia': 'Teaching',
    'nav.investigacion': 'Research',
    'nav.blog': 'Notes',
    'nav.cv': 'CV',
    'nav.contacto': 'Contact',
    'hero.badge': 'Teacher · Researcher',
    'hero.title': 'Mathematics I teach, learn and research.',
    'hero.description': 'Mathematics teacher in Barcelona and independent researcher. This is my workspace: teaching materials, research notes and interactive visualizations.',
    'hero.cta.research': 'See research',
    'hero.cta.teaching': 'Teaching',
    'section.teaching': 'Teaching',
    'section.research': 'Research',
    'section.latest': 'Latest notes',
    'teaching.description': 'Materials, exams and resources for the courses I teach. Some are public; others require access.',
    'research.description': 'Ongoing work on modular fractal dynamics and the Collatz conjecture. Paper in preparation for arXiv.',
    'access.public': 'public',
    'access.private': 'private',
    'access.interactive': 'interactive',
    'access.soon': 'soon',
    'access.classroom': 'classroom',
    'access.preprint': 'preprint',
    'footer.rights': 'Àlex Reyes · Mathematics, teaching and research · Barcelona',
    'meta.center': 'Col·legi Maristes Sants — Les Corts',
    'meta.since': 'Since 2010',
    'meta.field': 'Mathematics',
  },
} as const;

export function getLangFromUrl(url: URL) {
  const [, lang] = url.pathname.split('/');
  if (lang in ui) return lang as keyof typeof ui;
  return defaultLang;
}

export function useTranslations(lang: keyof typeof ui) {
  return function t(key: keyof typeof ui[typeof defaultLang]) {
    return ui[lang][key] || ui[defaultLang][key];
  }
}
