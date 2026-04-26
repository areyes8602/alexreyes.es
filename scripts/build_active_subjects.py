#!/usr/bin/env python3
"""Build active subject hubs in 3 languages from a single source.

Generates 12 hub files (4 subjects × 3 languages):
  - 2eso, ccss-1btl, ib-ai/2024-2026, ib-ai/2025-2027

Each subject has its UNITS / CHAPTERS array in the language of instruction.
UI chrome (nav, headings, button labels, descriptions) is translated.

Re-run after editing data/labels to keep all 3 langs in sync.
"""
import json
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
LANGS = ["es", "ca", "en"]


# ─── i18n shared chrome ──────────────────────────────────────────
LABELS = {
    "es": {
        "html_lang": "es",
        "home": "Inicio", "docencia": "Docencia",
        "doctorado_nav": "Doctorado", "notas_nav": "Notas", "cv_nav": "CV", "contacto_nav": "Contacto",
        "info_cta_h": "Información de la asignatura",
        "info_cta_p": "Horario, criterios de evaluación, temario, calendario y material necesario.",
        "year_picker_label": "Curso",
        "year_picker_current": "actual",
        "year_picker_empty": "No hay cursos archivados todavía.",
        "units_h2_regular": "Unidades didácticas",
        "units_h2_chapters": "Capítulos del libro",
        "units_help_regular": "Cada unidad contiene los apuntes de clase, las fichas de ejercicios con sus soluciones, y los exámenes realizados.",
        "units_help_chapters": "Cada capítulo agrupa los apuntes, listas de ejercicios con sus soluciones, recursos extra y los exámenes parciales.",
        "globals_h2": "Exámenes globales",
        "globals_help": "Globales de evaluación, simulacros, recuperaciones y exámenes finales — pruebas que cubren varias unidades.",
        "globals_loading": "cargando…",
        "globals_empty": "No hay exámenes globales publicados todavía.",
        "globals_load_error": "No se ha podido cargar el listado de exámenes.",
        "exams_unit_title": "Exámenes de esta unidad",
        "exam_questions": "preguntas", "exam_question": "pregunta",
        "exam_points": "puntos",
        "exam_btn_pdf": "PDF", "exam_btn_html": "Ver enunciados y correcciones",
        "no_exams_unit": "No hay exámenes publicados de esta unidad todavía.",
        "trimestre_tag": "evaluación",
        "footer_brand": "Matemáticas, docencia y doctorado",
        "promo_tab_hl": "HL — Higher Level",
        "promo_tab_sl": "SL — Standard Level",
        "promo_sl_intro": "El SL comparte la mayoría de capítulos con el HL, con menor profundidad en algunos temas y sin los capítulos exclusivos de HL.",
        "ib_chapter_hlonly": "Este capítulo es exclusivo del nivel HL.",
        "section_card_apunts": "Apuntes",
        "section_card_fitxes": "Lista de ejercicios",
        "section_card_solucions": "Soluciones",
        "section_card_extra": "Recursos extra",
        "unit_meta_book": "Libro",
        "unit_meta_dates": "Fechas",
        "unit_meta_trim": "evaluación",
        "examens_count_one": "examen", "examens_count_many": "exámenes",
    },
    "ca": {
        "html_lang": "ca",
        "home": "Inici", "docencia": "Docència",
        "doctorado_nav": "Doctorat", "notas_nav": "Notes", "cv_nav": "CV", "contacto_nav": "Contacte",
        "info_cta_h": "Informació de l'assignatura",
        "info_cta_p": "Horari, criteris d'avaluació, temari, calendari i material necessari.",
        "year_picker_label": "Curs",
        "year_picker_current": "actual",
        "year_picker_empty": "Encara no hi ha cursos arxivats.",
        "units_h2_regular": "Unitats didàctiques",
        "units_h2_chapters": "Capítols del llibre",
        "units_help_regular": "Cada unitat conté els apunts de classe, les fitxes d'exercicis amb les seves solucions, i els exàmens realitzats.",
        "units_help_chapters": "Cada capítol agrupa els apunts, llistes d'exercicis amb les seves solucions, recursos extra i els exàmens parcials.",
        "globals_h2": "Exàmens globals",
        "globals_help": "Globals d'avaluació, simulacres, recuperacions i exàmens finals — proves que cobreixen diverses unitats.",
        "globals_loading": "carregant…",
        "globals_empty": "Encara no hi ha exàmens globals publicats.",
        "globals_load_error": "No s'ha pogut carregar el llistat d'exàmens.",
        "exams_unit_title": "Exàmens d'aquesta unitat",
        "exam_questions": "preguntes", "exam_question": "pregunta",
        "exam_points": "punts",
        "exam_btn_pdf": "PDF", "exam_btn_html": "Veure enunciats i correccions",
        "no_exams_unit": "No hi ha exàmens publicats d'aquesta unitat encara.",
        "trimestre_tag": "avaluació",
        "footer_brand": "Matemàtiques, docència i doctorat",
        "promo_tab_hl": "HL — Higher Level",
        "promo_tab_sl": "SL — Standard Level",
        "promo_sl_intro": "El SL comparteix la majoria de capítols amb l'HL, amb menor profunditat en alguns temes i sense els capítols exclusius d'HL.",
        "ib_chapter_hlonly": "Aquest capítol és exclusiu del nivell HL.",
        "section_card_apunts": "Apunts",
        "section_card_fitxes": "Llista d'exercicis",
        "section_card_solucions": "Solucions",
        "section_card_extra": "Recursos extra",
        "unit_meta_book": "Llibre",
        "unit_meta_dates": "Dates",
        "unit_meta_trim": "avaluació",
        "examens_count_one": "examen", "examens_count_many": "exàmens",
    },
    "en": {
        "html_lang": "en",
        "home": "Home", "docencia": "Teaching",
        "doctorado_nav": "PhD", "notas_nav": "Notes", "cv_nav": "CV", "contacto_nav": "Contact",
        "info_cta_h": "Subject information",
        "info_cta_p": "Schedule, assessment criteria, syllabus, calendar and required material.",
        "year_picker_label": "Year",
        "year_picker_current": "current",
        "year_picker_empty": "No archived years yet.",
        "units_h2_regular": "Teaching units",
        "units_h2_chapters": "Book chapters",
        "units_help_regular": "Each unit contains the class notes, exercise sheets with solutions, and the exams from that unit.",
        "units_help_chapters": "Each chapter groups the notes, exercise lists with solutions, extra resources and the partial exams.",
        "globals_h2": "Comprehensive exams",
        "globals_help": "Term-final exams, mocks, retakes and final exams — assessments covering several units.",
        "globals_loading": "loading…",
        "globals_empty": "No comprehensive exams published yet.",
        "globals_load_error": "Could not load the exam list.",
        "exams_unit_title": "Exams from this unit",
        "exam_questions": "questions", "exam_question": "question",
        "exam_points": "points",
        "exam_btn_pdf": "PDF", "exam_btn_html": "View questions and solutions",
        "no_exams_unit": "No exams published for this unit yet.",
        "trimestre_tag": "term",
        "footer_brand": "Mathematics, teaching and research",
        "promo_tab_hl": "HL — Higher Level",
        "promo_tab_sl": "SL — Standard Level",
        "promo_sl_intro": "SL shares most chapters with HL, with less depth on some topics and without the HL-exclusive chapters.",
        "ib_chapter_hlonly": "This chapter is exclusive to the HL level.",
        "section_card_apunts": "Notes",
        "section_card_fitxes": "Exercise list",
        "section_card_solucions": "Solutions",
        "section_card_extra": "Extra resources",
        "unit_meta_book": "Book",
        "unit_meta_dates": "Dates",
        "unit_meta_trim": "term",
        "examens_count_one": "exam", "examens_count_many": "exams",
    },
}

# Months for date formatting per language
MONTHS = {
    "es": ['ene','feb','mar','abr','may','jun','jul','ago','sep','oct','nov','dic'],
    "ca": ['gen','feb','març','abr','maig','juny','jul','ag','set','oct','nov','des'],
    "en": ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'],
}


# ─── Subject configs ─────────────────────────────────────────────

# 2n ESO — language of instruction: Catalan
SUBJ_2ESO = {
    "code": "2eso",
    "type": "regular",
    "lang_taught": "ca",
    "title": {"es": "Matemàtiques 2n ESO", "ca": "Matemàtiques 2n ESO", "en": "Mathematics 2n ESO"},
    "subtitle": {
        "es": "Grupos A y E &middot; Currículum LOMLOE &middot; Maristes Sants&mdash;Les Corts",
        "ca": "Grups A i E &middot; Currículum LOMLOE &middot; Maristes Sants&mdash;Les Corts",
        "en": "Groups A and E &middot; LOMLOE curriculum &middot; Maristes Sants&mdash;Les Corts",
    },
    "section_label": "ESO",
    "tag_year": "2025–26",
    "info_grid": [
        {"label_key": "year_picker_label", "value": "2n ESO"},
        {"label": {"es": "Grupos", "ca": "Grups", "en": "Groups"}, "value": "A &middot; E"},
        {"label": {"es": "Idioma", "ca": "Idioma", "en": "Language"}, "value": {"es":"Català","ca":"Català","en":"Catalan"}, "small": True},
        {"label": {"es": "Unidades", "ca": "Unitats", "en": "Units"}, "value": "10"},
    ],
    "year_current": "2025–26",
    "materia_filter": "eso-2",
    # Units in language of instruction (Catalan), descriptions in language of instruction
    "units": [
        {"num":"01","slug":"fraccions","title":"Nombres fraccionaris","llibre":"U3","inici":"9 set","final":"1 oct","trimestre":"1a",
         "desc_l":{"ca":"Fraccions equivalents, ordenació, operacions amb fraccions, decimals i potències.",
                   "es":"Fracciones equivalentes, ordenación, operaciones con fracciones, decimales y potencias.",
                   "en":"Equivalent fractions, ordering, operations with fractions, decimals and powers."},
         "apunts":"/aula/eso-2/apuntes/u-fraccions/"},
        {"num":"02","slug":"decimals","title":"Nombres decimals","llibre":"U4","inici":"7 oct","final":"17 oct","trimestre":"1a",
         "desc_l":{"ca":"Decimals exactes i periòdics, fracció generatriu, aproximacions.",
                   "es":"Decimales exactos y periódicos, fracción generatriz, aproximaciones.",
                   "en":"Exact and periodic decimals, generating fraction, approximations."}},
        {"num":"03","slug":"probabilitat","title":"Probabilitat","llibre":"U15","inici":"21 oct","final":"7 nov","trimestre":"1a",
         "desc_l":{"ca":"Experiments aleatoris, regla de Laplace i probabilitat.",
                   "es":"Experimentos aleatorios, regla de Laplace y probabilidad.",
                   "en":"Random experiments, Laplace's rule and probability."}},
        {"num":"04","slug":"proporcionalitat","title":"Proporcionalitat","llibre":"U5","inici":"11 nov","final":"28 nov","trimestre":"1a",
         "desc_l":{"ca":"Magnituds proporcionals, regla de tres i percentatges.",
                   "es":"Magnitudes proporcionales, regla de tres y porcentajes.",
                   "en":"Proportional magnitudes, rule of three and percentages."}},
        {"num":"05","slug":"funcions","title":"Funcions i funcions elementals","llibre":"U8–U9","inici":"5 des","final":"23 gen","trimestre":"2a",
         "desc_l":{"ca":"Concepte de funció, funció lineal, afí, quadràtica i de proporcionalitat inversa.",
                   "es":"Concepto de función, función lineal, afín, cuadrática y de proporcionalidad inversa.",
                   "en":"Function concept, linear, affine, quadratic and inverse proportionality functions."}},
        {"num":"06","slug":"pitagores","title":"Pitàgores","llibre":"U10","inici":"27 gen","final":"30 gen","trimestre":"2a",
         "desc_l":{"ca":"Teorema de Pitàgores i les seves aplicacions.",
                   "es":"Teorema de Pitágoras y sus aplicaciones.",
                   "en":"Pythagorean theorem and its applications."}},
        {"num":"07","slug":"poliedres","title":"Poliedres","llibre":"U12","inici":"3 feb","final":"27 feb","trimestre":"2a",
         "desc_l":{"ca":"Prismes, piràmides, àrees i volums.",
                   "es":"Prismas, pirámides, áreas y volúmenes.",
                   "en":"Prisms, pyramids, areas and volumes."}},
        {"num":"08","slug":"cossos-revolucio","title":"Cossos de revolució","llibre":"U13","inici":"3 mar","final":"10 mar","trimestre":"2a",
         "desc_l":{"ca":"Cilindre, con i esfera. Àrees i volums.",
                   "es":"Cilindro, cono y esfera. Áreas y volúmenes.",
                   "en":"Cylinder, cone and sphere. Areas and volumes."}},
        {"num":"09","slug":"algebra","title":"Llenguatge algebraic","llibre":"U6","inici":"17 mar","final":"28 abr","trimestre":"3a",
         "desc_l":{"ca":"Expressions algebraiques, monomis i polinomis.",
                   "es":"Expresiones algebraicas, monomios y polinomios.",
                   "en":"Algebraic expressions, monomials and polynomials."}},
        {"num":"10","slug":"equacions","title":"Equacions i sistemes","llibre":"U7","inici":"29 abr","final":"29 mai","trimestre":"3a",
         "desc_l":{"ca":"Equacions de 1r grau, sistemes 2×2 i resolució de problemes.",
                   "es":"Ecuaciones de 1er grado, sistemas 2×2 y resolución de problemas.",
                   "en":"1st degree equations, 2×2 systems and problem solving."}},
    ],
}

# 1r BTL MACS — language of instruction: Spanish
SUBJ_1BTL = {
    "code": "ccss-1btl",
    "type": "regular",
    "lang_taught": "es",
    "title": {"es": "Mat. Aplicadas a las CCSS", "ca": "Mat. Aplicades a les CCSS", "en": "Applied Maths for Social Sciences"},
    "subtitle": {
        "es": "1&ordm; de Bachillerato &middot; Currículum LOMLOE &middot; Maristes Sants&mdash;Les Corts",
        "ca": "1r de Batxillerat &middot; Currículum LOMLOE &middot; Maristes Sants&mdash;Les Corts",
        "en": "1st year Bachillerato &middot; LOMLOE curriculum &middot; Maristes Sants&mdash;Les Corts",
    },
    "section_label": {"es": "Bachillerato", "ca": "Batxillerat", "en": "Bachillerato"},
    "tag_year": "2025–26",
    "info_grid": [
        {"label_key": "year_picker_label", "value": {"es":"1º Bachillerato","ca":"1r Batxillerat","en":"1st Bachillerato"}},
        {"label": {"es":"Modalidad","ca":"Modalitat","en":"Track"}, "value":{"es":"Ciencias Sociales","ca":"Ciències Socials","en":"Social Sciences"}, "small": True},
        {"label": {"es":"Calculadora","ca":"Calculadora","en":"Calculator"}, "value":{"es":"Científica (no gráfica)","ca":"Científica (no gràfica)","en":"Scientific (non-graphic)"}, "small": True},
        {"label": {"es":"Unidades","ca":"Unitats","en":"Units"}, "value":"10"},
    ],
    "year_current": "2025–26",
    "materia_filter": "bach-ccss-1",
    # Units in language of instruction (Catalan), descriptions per language.
    # Keep keys aligned with SUBJ_2ESO so the regular hub renderer can use them.
    "units": [
        {"num":"01","slug":"nombres-reals","title":"Nombres reals","llibre":"Baula 1","inici":"16 sep 2025","final":"7 oct 2025","trimestre":"1a",
         "desc_l":{"ca":"Nombres reals, intervals, valor absolut, aproximació i errors.",
                   "es":"Números reales, intervalos, valor absoluto, aproximación y errores.",
                   "en":"Real numbers, intervals, absolute value, approximation and errors."}},
        {"num":"02","slug":"polinomis","title":"Polinomis","llibre":"—","inici":"8 oct 2025","final":"28 oct 2025","trimestre":"1a",
         "desc_l":{"ca":"Operacions amb polinomis, divisió, regla de Ruffini i factorització.",
                   "es":"Operaciones con polinomios, división, regla de Ruffini y factorización.",
                   "en":"Polynomial operations, division, Ruffini's rule and factorization."}},
        {"num":"03","slug":"equacions-sistemes","title":"Equacions i sistemes d'equacions","llibre":"Baula 3","inici":"29 oct 2025","final":"11 nov 2025","trimestre":"1a",
         "desc_l":{"ca":"Equacions de 1r i 2n grau, exponencials, logarítmiques i sistemes lineals i no lineals.",
                   "es":"Ecuaciones de primer y segundo grado, exponenciales, logarítmicas y sistemas lineales y no lineales.",
                   "en":"First and second degree, exponential and logarithmic equations and linear/non-linear systems."}},
        {"num":"04","slug":"inequacions","title":"Inequacions i sistemes d'inequacions","llibre":"Baula 4","inici":"12 nov 2025","final":"19 nov 2025","trimestre":"1a",
         "desc_l":{"ca":"Inequacions lineals i quadràtiques, sistemes d'inequacions i resolució de problemes.",
                   "es":"Inecuaciones lineales y cuadráticas, sistemas de inecuaciones y resolución de problemas.",
                   "en":"Linear and quadratic inequalities, systems of inequalities and problem solving."}},
        {"num":"05","slug":"funcions-reals","title":"Funcions reals de variable real","llibre":"Baula 5","inici":"2 dic 2025","final":"13 ene 2026","trimestre":"2a",
         "desc_l":{"ca":"Concepte de funció, domini, recorregut, simetries i operacions amb funcions.",
                   "es":"Concepto de función, dominio, recorrido, simetrías y operaciones con funciones.",
                   "en":"Function concept, domain, range, symmetries and operations with functions."}},
        {"num":"06","slug":"representacio-funcions","title":"Estudi i representació de funcions","llibre":"Baula 8","inici":"14 ene 2026","final":"30 ene 2026","trimestre":"2a",
         "desc_l":{"ca":"Estudi analític i representació gràfica de funcions elementals.",
                   "es":"Estudio analítico y representación gráfica de funciones elementales.",
                   "en":"Analytical study and graphical representation of elementary functions."}},
        {"num":"07","slug":"derivades","title":"Derivada d'una funció","llibre":"Baula 7","inici":"3 feb 2026","final":"20 feb 2026","trimestre":"2a",
         "desc_l":{"ca":"Taxa de variació, concepte de derivada, regles de derivació i aplicacions.",
                   "es":"Tasa de variación, concepto de derivada, reglas de derivación y aplicaciones.",
                   "en":"Rate of change, derivative concept, differentiation rules and applications."}},
        {"num":"08","slug":"estadistica","title":"Estadística","llibre":"Baula 9","inici":"3 mar 2026","final":"10 abr 2026","trimestre":"3a",
         "desc_l":{"ca":"Estadística descriptiva, paràmetres i distribucions bidimensionals.",
                   "es":"Estadística descriptiva, parámetros y distribuciones bidimensionales.",
                   "en":"Descriptive statistics, parameters and two-dimensional distributions."}},
        {"num":"09","slug":"probabilitat","title":"Probabilitat","llibre":"Baula 10","inici":"14 abr 2026","final":"15 may 2026","trimestre":"3a",
         "desc_l":{"ca":"Successos, probabilitat condicionada i teorema de Bayes.",
                   "es":"Sucesos, probabilidad condicionada y teorema de Bayes.",
                   "en":"Events, conditional probability and Bayes' theorem."},
         "apunts":"/aula/ccss-1btl/apuntes/u-probabilitat/"},
        {"num":"10","slug":"distribucions","title":"Distribucions discretes i contínues. Distribució binomial i normal","llibre":"Baula 11","inici":"19 may 2026","final":"29 may 2026","trimestre":"3a",
         "desc_l":{"ca":"Distribucions discretes i contínues. Binomial i normal.",
                   "es":"Distribuciones discretas y continuas. Binomial y normal.",
                   "en":"Discrete and continuous distributions. Binomial and normal."}},
    ],
}

# IB AI HL/SL — taught in English
IB_CHAPTERS = [
    {"num":"01","title":"Measuring space: accuracy and geometry","hl":True,"sl":True},
    {"num":"02","title":"Representing and describing data: descriptive statistics","hl":True,"sl":True},
    {"num":"03","title":"Dividing up space: coordinate geometry, Voronoi diagrams, vectors, lines","hl":True,"sl":True},
    {"num":"04","title":"Modelling constant rates of change: linear functions and regressions","hl":True,"sl":True},
    {"num":"05","title":"Quantifying uncertainty: probability","hl":True,"sl":True},
    {"num":"06","title":"Modelling relationships with functions: power and polynomial functions","hl":True,"sl":True},
    {"num":"07","title":"Modelling rates of change: exponential and logarithmic functions","hl":True,"sl":True},
    {"num":"08","title":"Modelling periodic phenomena: trigonometric functions and complex numbers","hl":True,"sl":True,
     "note":{"es":"8.3–8.5 solo HL","ca":"8.3–8.5 només HL","en":"8.3–8.5 HL only"}},
    {"num":"09","title":"Modelling with matrices: storing and analysing data","hl":True,"sl":False,
     "note":{"es":"Solo HL","ca":"Només HL","en":"HL only"}},
    {"num":"10","title":"Analyzing rates of change: differential calculus","hl":True,"sl":True},
    {"num":"11","title":"Approximating irregular spaces: integration and differential equations","hl":True,"sl":True},
    {"num":"12","title":"Modelling motion and change in two and three dimensions","hl":True,"sl":False,
     "note":{"es":"Solo HL","ca":"Només HL","en":"HL only"}},
    {"num":"13","title":"Representing multiple outcomes: random variables and probability distributions","hl":True,"sl":True},
    {"num":"14","title":"Testing for validity: Spearman's, hypothesis testing and χ² test","hl":True,"sl":True},
    {"num":"15","title":"Optimizing complex networks: graph theory","hl":True,"sl":False,
     "note":{"es":"Solo HL","ca":"Només HL","en":"HL only"}},
    {"num":"16","title":"Exploration (IA)","hl":True,"sl":True},
]

def make_ib_subject(promo, anyo_examen):
    return {
        "code": f"ib-ai/{promo}",
        "type": "ib",
        "lang_taught": "en",
        "promo": promo,
        "title": {"es": f"Promoción {promo}", "ca": f"Promoció {promo}", "en": f"{promo} Cohort"},
        "subtitle": {
            "es": f"Exámenes oficiales mayo {anyo_examen} &middot; Maristes Sants&mdash;Les Corts",
            "ca": f"Exàmens oficials maig {anyo_examen} &middot; Maristes Sants&mdash;Les Corts",
            "en": f"Official exams May {anyo_examen} &middot; Maristes Sants&mdash;Les Corts",
        },
        "section_label": "IB Mathematics AI",
        "tag_year": promo.replace("-", "–"),
        "info_grid": [
            {"label": {"es":"Libro HL","ca":"Llibre HL","en":"HL textbook"}, "value":"Mathematics: AI HL — Oxford (2019)", "small": True},
            {"label": {"es":"Evaluación","ca":"Avaluació","en":"Assessment"}, "value":"Paper 1, 2, 3 (HL) · Paper 1, 2 (SL) · IA", "small": True},
            {"label": {"es":"Calculadora","ca":"Calculadora","en":"Calculator"}, "value":"Casio CG-50", "small": True},
            {"label": {"es":"Acceso","ca":"Accés","en":"Access"}, "value":{"es":"Alumnos de la promoción","ca":"Alumnes de la promoció","en":"Cohort students"}, "small": True},
        ],
        "year_current": None,  # IB doesn't use year picker (uses promo subfolders)
        "materia_filter": ["ib-ai-hl", "ib-ai-sl"],
        "promo_filter": promo,
    }


SUBJ_IBAI_2426 = make_ib_subject("2024-2026", 2026)
SUBJ_IBAI_2527 = make_ib_subject("2025-2027", 2027)


SUBJECTS = [SUBJ_2ESO, SUBJ_1BTL, SUBJ_IBAI_2426, SUBJ_IBAI_2527]


# ─── Rendering helpers ───────────────────────────────────────────
def lang_prefix(lang):
    return "" if lang == "es" else f"/{lang}"


def lang_switch(lang, code):
    parts = []
    for l in ("es", "ca", "en"):
        href = f"/docencia/{code}/" if l == "es" else f"/{l}/docencia/{code}/"
        cls = ' class="lang-active"' if l == lang else ""
        parts.append(f'<a href="{href}"{cls}>{l.upper()}</a>')
    return '<span class="lang-sep">&middot;</span>'.join(parts)


def nav_block(lang):
    L = LABELS[lang]
    return (
        f'<a href="{lang_prefix(lang)}/docencia/" class="nav-active">{L["docencia"]}</a>'
        f'<a href="{lang_prefix(lang)}/doctorado/">{L["doctorado_nav"]}</a>'
        f'<a href="{lang_prefix(lang)}/notas/">{L["notas_nav"]}</a>'
        f'<a href="{lang_prefix(lang)}/cv/">{L["cv_nav"]}</a>'
        f'<a href="{lang_prefix(lang)}/contacto/">{L["contacto_nav"]}</a>'
    )


def picker_lang_value(field, lang):
    """Resolve a field that may be a string or a {lang: str} dict."""
    if isinstance(field, dict):
        return field.get(lang, field.get("en", ""))
    return field


def info_grid_html(grid, lang):
    L = LABELS[lang]
    cells = []
    for c in grid:
        if "label_key" in c:
            label = L[c["label_key"]]
        else:
            label = picker_lang_value(c["label"], lang)
        value = picker_lang_value(c["value"], lang)
        small = ' style="font-size:0.88rem"' if c.get("small") else ""
        cells.append(f'<div class="info-card"><div class="info-card-label">{label}</div><div class="info-card-value"{small}>{value}</div></div>')
    return "\n      ".join(cells)


def head_block(L, title, desc, code, extra_styles=""):
    es_canon = f"https://alexreyes.es/docencia/{code}/"
    ca_canon = f"https://alexreyes.es/ca/docencia/{code}/"
    en_canon = f"https://alexreyes.es/en/docencia/{code}/"
    canonical = {"es": es_canon, "ca": ca_canon, "en": en_canon}[L["html_lang"]]
    return f"""<!DOCTYPE html>
<html lang="{L['html_lang']}">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title} — Àlex Reyes</title>
<meta name="description" content="{desc}">
<script>(function(){{var s=localStorage.getItem('theme');if(s)document.documentElement.setAttribute('data-theme',s);else document.documentElement.setAttribute('data-theme','light');}})();</script>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
<link rel="stylesheet" href="/style.css">
<link rel="icon" type="image/svg+xml" href="/favicon.svg">
<link rel="canonical" href="{canonical}">
<link rel="alternate" hreflang="es" href="{es_canon}">
<link rel="alternate" hreflang="ca" href="{ca_canon}">
<link rel="alternate" hreflang="en" href="{en_canon}">
<link rel="alternate" hreflang="x-default" href="{es_canon}">
<style>
  .info-cta {{ display:flex; align-items:center; gap:1.2rem; padding:1.2rem 1.5rem; background:var(--bg-subtle); border:1px solid var(--border); border-radius:var(--radius); text-decoration:none; color:inherit; transition:border-color 0.15s, transform 0.15s; margin-bottom:2rem; }}
  .info-cta:hover {{ border-color:var(--border-strong); transform:translateY(-1px); }}
  .info-cta-icon {{ font-size:2rem; flex:0 0 auto; }}
  .info-cta-body {{ flex:1; min-width:0; }}
  .info-cta-body h3 {{ margin:0 0 0.25rem; font-size:1.05rem; font-weight:600; color:var(--text); }}
  .info-cta-body p {{ margin:0; font-size:0.88rem; color:var(--text-soft); }}
  .info-cta-arrow {{ font-size:1.2rem; color:var(--text-faint); flex:0 0 auto; }}
  .unit-meta {{ display:flex; gap:0.7rem; flex-wrap:wrap; font-size:0.75rem; color:var(--text-faint); margin-bottom:0.6rem; }}
  .unit-meta span {{ display:inline-flex; align-items:center; gap:0.3rem; }}
{extra_styles}
</style>
</head>"""


def nav_html(lang, code):
    return f"""<nav>
  <div class="nav-inner">
    <a href="{lang_prefix(lang)}/" class="nav-brand">alexreyes.es</a>
    <div class="nav-links">{nav_block(lang)}</div>
    <div class="nav-right">
      <div class="lang-sw">{lang_switch(lang, code)}</div>
      <button class="nav-hamburger" onclick="toggleMenu()" aria-label="Menu"><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><line x1="4" y1="7" x2="20" y2="7"/><line x1="4" y1="12" x2="20" y2="12"/><line x1="4" y1="17" x2="20" y2="17"/></svg></button>
      <button class="theme-btn" onclick="toggleTheme()" aria-label="Toggle theme">
        <svg class="icon-sun" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="5"/><line x1="12" y1="1" x2="12" y2="3"/><line x1="12" y1="21" x2="12" y2="23"/><line x1="4.22" y1="4.22" x2="5.64" y2="5.64"/><line x1="18.36" y1="18.36" x2="19.78" y2="19.78"/><line x1="1" y1="12" x2="3" y2="12"/><line x1="21" y1="12" x2="23" y2="12"/><line x1="4.22" y1="19.78" x2="5.64" y2="18.36"/><line x1="18.36" y1="5.64" x2="19.78" y2="4.22"/></svg>
        <svg class="icon-moon" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/></svg>
      </button>
    </div>
  </div>
</nav>"""


def footer_html(L):
    return f"""<footer>
  <div class="container">
    <div class="footer-inner">
      <span><strong>Àlex Reyes</strong> &middot; {L['footer_brand']}</span>
      <span>Barcelona &middot; 2026</span>
    </div>
  </div>
</footer>"""


# ─── Render: regular subject hub (2eso, ccss-1btl) ───────────────
def render_regular_hub(s, lang):
    L = LABELS[lang]
    code = s["code"]
    title = picker_lang_value(s["title"], lang)
    subtitle = picker_lang_value(s["subtitle"], lang)
    section_label = picker_lang_value(s["section_label"], lang)
    info_url = f"{lang_prefix(lang)}/docencia/{code}/info/"

    # Build UNITS JSON for JS (descriptions in current language)
    units_for_js = []
    for u in s["units"]:
        u2 = {k: v for k, v in u.items() if k != "desc_l"}
        u2["desc"] = u["desc_l"][lang]
        units_for_js.append(u2)
    units_json = json.dumps(units_for_js, ensure_ascii=False)

    # Year picker
    if s.get("year_current"):
        year_picker = f"""    <details class="year-picker">
      <summary>📅 {L['year_picker_label']} {s['year_current']}</summary>
      <div class="year-menu">
        <a href="{lang_prefix(lang)}/docencia/{code}/" class="active">{s['year_current']} ({L['year_picker_current']})</a>
        <p class="year-empty">{L['year_picker_empty']}</p>
      </div>
    </details>
"""
    else:
        year_picker = ""

    breadcrumb = (
        f'<a href="{lang_prefix(lang)}/">{L["home"]}</a>'
        f'<span class="sep">/</span>'
        f'<a href="{lang_prefix(lang)}/docencia/">{L["docencia"]}</a>'
        f'<span class="sep">/</span>'
        f'<span class="current">{title}</span>'
    )

    info_grid = info_grid_html(s["info_grid"], lang)
    months_js = json.dumps(MONTHS[lang])

    return f"""{head_block(L, title, subtitle, code)}
<body>
{nav_html(lang, code)}

<main>
  <div class="container" style="padding-top:3rem;padding-bottom:5rem">

    <div class="breadcrumb">{breadcrumb}</div>

{year_picker}    <div class="page-header">
      <div style="display:flex;align-items:center;gap:0.6rem;margin-bottom:0.6rem;flex-wrap:wrap">
        <span class="section-label">{section_label}</span>
        <span class="tag tag-orange">{s['tag_year']}</span>
      </div>
      <h1 style="margin:0.3rem 0 0.6rem">{title}</h1>
      <p style="font-size:0.98rem;color:var(--text-soft)">{subtitle}</p>
    </div>

    <div class="info-grid">
      {info_grid}
    </div>

    <a href="{info_url}" class="info-cta">
      <span class="info-cta-icon">📋</span>
      <div class="info-cta-body">
        <h3>{L['info_cta_h']}</h3>
        <p>{L['info_cta_p']}</p>
      </div>
      <span class="info-cta-arrow">→</span>
    </a>

    <h2 style="font-size:1.1rem;margin:0 0 0.4rem">{L['units_h2_regular']}</h2>
    <p style="color:var(--text-soft);font-size:0.92rem;margin-bottom:1rem">{L['units_help_regular']}</p>
    <div class="chapter-list" id="units-list"></div>

    <section style="margin-top:3rem">
      <div style="display:flex;align-items:baseline;gap:0.6rem;flex-wrap:wrap;margin-bottom:0.4rem">
        <h2 style="font-size:1.2rem;margin:0">{L['globals_h2']}</h2>
        <span class="tag tag-gray" id="globals-count" style="font-size:0.7rem">{L['globals_loading']}</span>
      </div>
      <p style="color:var(--text-soft);font-size:0.92rem;margin-bottom:1rem">{L['globals_help']}</p>
      <div id="globals-list" class="exam-list"></div>
    </section>

  </div>
</main>

{footer_html(L)}

<script>
function toggleMenu(){{document.querySelector("nav").classList.toggle("open");}}
function toggleTheme(){{var h=document.documentElement,n=h.getAttribute('data-theme')==='dark'?'light':'dark';h.setAttribute('data-theme',n);localStorage.setItem('theme',n);}}
function toggleChapter(h){{h.parentElement.classList.toggle('open');}}

const UNITS = {units_json};
const MATERIA = {json.dumps(s['materia_filter'])};
const MONTHS = {months_js};
const LABELS_JS = {json.dumps({k: L[k] for k in ['exam_questions','exam_question','exam_points','exam_btn_pdf','exam_btn_html','no_exams_unit','exams_unit_title','globals_empty','globals_load_error','section_card_apunts','section_card_fitxes','section_card_solucions','unit_meta_book','unit_meta_dates','unit_meta_trim','examens_count_one','examens_count_many','trimestre_tag']}, ensure_ascii=False)};

function unitNumOf(colId) {{ const m=(colId||'').match(/-u(\\d{{1,2}})\\b/); return m ? m[1].padStart(2,'0') : null; }}
function isGlobal(colId) {{ if(!colId) return false; if(unitNumOf(colId)) return false; return /-g\\d+\\b|-final\\b|-rec\\b|-simulacre\\b/.test(colId); }}
function fmtFecha(iso) {{ if(!iso) return ''; const [y,m,d]=iso.split('-'); return `${{parseInt(d,10)}} ${{MONTHS[parseInt(m,10)-1]}} ${{y}}`; }}
function escHtml(s) {{ return String(s||'').replace(/[&<>"']/g, c => ({{'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}}[c])); }}
function renderExamCard(col, ejs) {{
  const ptos = ejs.reduce((s,e) => s + (e.puntuacion||0), 0);
  const npreg = ejs.length;
  const pdfBtn = col.pdf_enunciados ? `<a class="exam-card-btn pdf" href="${{escHtml(col.pdf_enunciados)}}" target="_blank" rel="noopener" title="${{LABELS_JS.exam_btn_pdf}}">📄 ${{LABELS_JS.exam_btn_pdf}}</a>` : '';
  const idxBtn = col.url_index ? `<a class="exam-card-btn html" href="${{escHtml(col.url_index)}}">📋 ${{LABELS_JS.exam_btn_html}}</a>` : '';
  return `<article class="exam-card"><div class="exam-card-head"><span class="exam-card-date">${{escHtml(fmtFecha(col.fecha))}}</span>${{col.grupo?`<span class="tag tag-orange" style="font-size:0.7rem">${{escHtml(col.grupo)}}</span>`:''}}</div><h3 class="exam-card-title">${{escHtml(col.titulo||col.id)}}</h3><p class="exam-card-meta">${{npreg}} ${{npreg===1?LABELS_JS.exam_question:LABELS_JS.exam_questions}} &middot; ${{ptos}} ${{LABELS_JS.exam_points}}</p><div class="exam-card-actions">${{idxBtn}}${{pdfBtn}}</div></article>`;
}}
function buildSectionCard(href, icon, label) {{
  if (href) return `<a href="${{href}}" class="chapter-section available" style="text-decoration:none"><span>${{icon}}</span><span>${{label}}</span></a>`;
  return `<div class="chapter-section empty"><span>${{icon}}</span><span>${{label}}</span></div>`;
}}
const TRIM_CLASS = {{ '1a':'tag-orange', '2a':'tag-purple', '3a':'tag-gray' }};
function buildUnit(u, examsByUnit) {{
  // Dins d'una unitat ordenem per data ascendent: Parcial 1 abans del Parcial 2, simulacre abans del global, etc.
  const exs = (examsByUnit[u.num]||[]).sort((a,b) => (a.col.fecha||'').localeCompare(b.col.fecha||''));
  const examCount = exs.length;
  const sections = [
    buildSectionCard(u.apunts, '📄', LABELS_JS.section_card_apunts),
    buildSectionCard(u.fitxes, '📝', LABELS_JS.section_card_fitxes),
    buildSectionCard(u.solucions, '✅', LABELS_JS.section_card_solucions),
  ].join('');
  const examsBox = examCount > 0
    ? `<div style="margin-top:1.2rem"><h4 style="font-size:0.85rem;color:var(--text-soft);margin:0 0 0.6rem;text-transform:uppercase;letter-spacing:0.04em;font-weight:600">${{LABELS_JS.exams_unit_title}} (${{examCount}})</h4><div class="exam-list">${{exs.map(({{col,ejs}}) => renderExamCard(col, ejs)).join('')}}</div></div>`
    : `<p style="font-size:0.82rem;color:var(--text-faint);margin:1rem 0 0">${{LABELS_JS.no_exams_unit}}</p>`;
  const examBadge = examCount > 0
    ? `<span class="tag tag-purple" style="font-size:0.65rem;margin-left:auto">${{examCount}} ${{examCount===1?LABELS_JS.examens_count_one:LABELS_JS.examens_count_many}}</span>`
    : (u.trimestre ? `<span class="tag ${{TRIM_CLASS[u.trimestre]||'tag-gray'}}" style="font-size:0.65rem;margin-left:auto">${{u.trimestre}} ${{LABELS_JS.trimestre_tag}}</span>` : '');
  const meta = (u.llibre || u.inici) ? `<div class="unit-meta">${{u.llibre?`<span>📖 ${{LABELS_JS.unit_meta_book}} ${{escHtml(u.llibre)}}</span>`:''}}${{u.inici?`<span>📅 ${{escHtml(u.inici)}} → ${{escHtml(u.final||'')}}</span>`:''}}${{u.trimestre?`<span>🎯 ${{u.trimestre}} ${{LABELS_JS.unit_meta_trim}}</span>`:''}}</div>` : '';
  return `<div class="chapter-item"><div class="chapter-header" onclick="toggleChapter(this)"><span class="chapter-num">${{u.num}}</span><span class="chapter-title">${{escHtml(u.title)}}</span>${{examBadge}}<span class="chapter-arrow">&#9660;</span></div><div class="chapter-body">${{meta}}<p style="font-size:0.88rem;color:var(--text-soft);margin:0 0 1rem">${{escHtml(u.desc)}}</p><div class="chapter-sections">${{sections}}</div>${{examsBox}}</div></div>`;
}}

fetch('/assets/data/ejercicios-index.json', {{ cache: 'no-cache' }})
  .then(r => r.ok ? r.json() : Promise.reject(r.status))
  .then(idx => {{
    const cols = new Map();
    for (const e of (idx.ejercicios || [])) {{
      const c = e.coleccion || {{}};
      if (e.tags && e.tags.materia !== MATERIA) continue;
      // Només mostrem exàmens al hub: les pràctiques/exercicis de classe es llisten a /aula/<materia>/apuntes/
      if (c.tipo && c.tipo !== 'examen') continue;
      if (!cols.has(c.id)) cols.set(c.id, {{ col: c, ejs: [] }});
      cols.get(c.id).ejs.push(e);
    }}
    const byUnit = {{}};
    const globals = [];
    for (const entry of cols.values()) {{
      // Si la col·lecció declara `unidades_implicadas`, l'examen apareix sota cadascuna.
      const ui = Array.isArray(entry.col.unidades_implicadas) ? entry.col.unidades_implicadas : null;
      if (ui && ui.length > 0) {{
        for (const num of ui) {{
          const k = String(num).padStart(2,'0');
          (byUnit[k] = byUnit[k] || []).push(entry);
        }}
        continue;
      }}
      const u = unitNumOf(entry.col.id);
      if (u) {{ (byUnit[u] = byUnit[u] || []).push(entry); }}
      else {{ globals.push(entry); }}
    }}
    document.getElementById('units-list').innerHTML = UNITS.map(u => buildUnit(u, byUnit)).join('');
    // Globals també ordenats cronològicament (ASC) perquè Global 1a sortí abans que Global 2a, etc.
    globals.sort((a,b) => (a.col.fecha||'').localeCompare(b.col.fecha||''));
    const cont = document.getElementById('globals-list');
    const count = document.getElementById('globals-count');
    if (globals.length === 0) {{
      count.textContent = '0';
      cont.innerHTML = `<p style="color:var(--text-faint);font-size:0.9rem;padding:1rem 0">${{LABELS_JS.globals_empty}}</p>`;
    }} else {{
      count.textContent = globals.length + (globals.length===1 ? ' ' + LABELS_JS.examens_count_one : ' ' + LABELS_JS.examens_count_many);
      cont.innerHTML = globals.map(({{col,ejs}}) => renderExamCard(col, ejs)).join('');
    }}
  }})
  .catch(err => {{
    document.getElementById('units-list').innerHTML = UNITS.map(u => buildUnit(u, {{}})).join('');
    document.getElementById('globals-count').textContent = 'error';
    document.getElementById('globals-list').innerHTML = `<p style="color:var(--text-faint);font-size:0.9rem">${{LABELS_JS.globals_load_error}}</p>`;
    console.error('exams:', err);
  }});
</script>
</body>
</html>
"""


# ─── Render: IB AI hub (with HL/SL tabs) ─────────────────────────
def render_ib_hub(s, lang):
    L = LABELS[lang]
    code = s["code"]
    promo = s["promo"]
    title = picker_lang_value(s["title"], lang)
    subtitle = picker_lang_value(s["subtitle"], lang)
    info_url = f"{lang_prefix(lang)}/docencia/{code}/info/"

    chapters_for_js = []
    for ch in IB_CHAPTERS:
        ch2 = {k: v for k, v in ch.items() if k != "note"}
        if "note" in ch:
            ch2["note"] = ch["note"][lang]
        chapters_for_js.append(ch2)
    chapters_json = json.dumps(chapters_for_js, ensure_ascii=False)

    breadcrumb = (
        f'<a href="{lang_prefix(lang)}/">{L["home"]}</a>'
        f'<span class="sep">/</span>'
        f'<a href="{lang_prefix(lang)}/docencia/">{L["docencia"]}</a>'
        f'<span class="sep">/</span>'
        f'<a href="{lang_prefix(lang)}/docencia/ib-ai/">IB Mathematics AI</a>'
        f'<span class="sep">/</span>'
        f'<span class="current">{title}</span>'
    )

    info_grid = info_grid_html(s["info_grid"], lang)
    months_js = json.dumps(MONTHS[lang])

    return f"""{head_block(L, title, subtitle, code)}
<body>
{nav_html(lang, code)}

<main>
  <div class="container" style="padding-top:3rem;padding-bottom:6rem">

    <div class="breadcrumb">{breadcrumb}</div>

    <div class="page-header">
      <div style="display:flex;align-items:center;gap:0.6rem;margin-bottom:0.6rem;flex-wrap:wrap">
        <span class="section-label">{s['section_label']}</span>
        <span class="level-badge level-hl">HL</span>
        <span class="level-badge level-sl">SL</span>
        <span class="tag tag-orange">{s['tag_year']}</span>
      </div>
      <h1 style="margin:0.3rem 0 0.6rem">{title}</h1>
      <p style="font-size:0.98rem;color:var(--text-soft)">{subtitle}</p>
    </div>

    <div class="info-grid">
      {info_grid}
    </div>

    <a href="{info_url}" class="info-cta">
      <span class="info-cta-icon">📋</span>
      <div class="info-cta-body">
        <h3>{L['info_cta_h']}</h3>
        <p>{L['info_cta_p']}</p>
      </div>
      <span class="info-cta-arrow">→</span>
    </a>

    <h2 style="font-size:1.1rem;margin:2.5rem 0 0.4rem">{L['units_h2_chapters']}</h2>
    <p style="color:var(--text-soft);font-size:0.92rem;margin-bottom:1rem">{L['units_help_chapters']}</p>

    <div class="promo-tabs">
      <button class="promo-tab active" onclick="showNivel('hl', this)">{L['promo_tab_hl']}</button>
      <button class="promo-tab" onclick="showNivel('sl', this)">{L['promo_tab_sl']}</button>
    </div>

    <div id="nivel-hl" class="promo-panel active">
      <div class="chapter-list" id="chapters-hl"></div>
    </div>

    <div id="nivel-sl" class="promo-panel">
      <p style="color:var(--text-soft);font-size:0.92rem;margin-bottom:1rem">{L['promo_sl_intro']}</p>
      <div class="chapter-list" id="chapters-sl"></div>
    </div>

    <section style="margin-top:3rem">
      <div style="display:flex;align-items:baseline;gap:0.6rem;flex-wrap:wrap;margin-bottom:0.4rem">
        <h2 style="font-size:1.2rem;margin:0">{L['globals_h2']}</h2>
        <span class="tag tag-gray" id="globals-count" style="font-size:0.7rem">{L['globals_loading']}</span>
      </div>
      <p style="color:var(--text-soft);font-size:0.92rem;margin-bottom:1rem">{L['globals_help']}</p>
      <div id="globals-list" class="exam-list"></div>
    </section>

  </div>
</main>

{footer_html(L)}

<script>
const CHAPTERS = {chapters_json};
const PROMO = {json.dumps(promo)};
const MONTHS = {months_js};
const LABELS_JS = {json.dumps({k: L[k] for k in ['exam_questions','exam_question','exam_points','exam_btn_pdf','exam_btn_html','no_exams_unit','exams_unit_title','globals_empty','globals_load_error','section_card_apunts','section_card_fitxes','section_card_solucions','section_card_extra','examens_count_one','examens_count_many','ib_chapter_hlonly']}, ensure_ascii=False)};

function unitNumOf(colId) {{ const m=(colId||'').match(/-u(\\d{{1,2}})\\b/); return m ? m[1].padStart(2,'0') : null; }}
function fmtFecha(iso) {{ if(!iso) return ''; const [y,m,d]=iso.split('-'); return `${{parseInt(d,10)}} ${{MONTHS[parseInt(m,10)-1]}} ${{y}}`; }}
function escHtml(s) {{ return String(s||'').replace(/[&<>"']/g, c => ({{'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}}[c])); }}
function renderExamCard(col, ejs) {{
  const ptos = ejs.reduce((s,e) => s + (e.puntuacion||0), 0);
  const npreg = ejs.length;
  const pdfBtn = col.pdf_enunciados ? `<a class="exam-card-btn pdf" href="${{escHtml(col.pdf_enunciados)}}" target="_blank" rel="noopener" title="${{LABELS_JS.exam_btn_pdf}}">📄 ${{LABELS_JS.exam_btn_pdf}}</a>` : '';
  const idxBtn = col.url_index ? `<a class="exam-card-btn html" href="${{escHtml(col.url_index)}}">📋 ${{LABELS_JS.exam_btn_html}}</a>` : '';
  return `<article class="exam-card"><div class="exam-card-head"><span class="exam-card-date">${{escHtml(fmtFecha(col.fecha))}}</span>${{col.grupo?`<span class="tag tag-orange" style="font-size:0.7rem">${{escHtml(col.grupo)}}</span>`:''}}</div><h3 class="exam-card-title">${{escHtml(col.titulo||col.id)}}</h3><p class="exam-card-meta">${{npreg}} ${{npreg===1?LABELS_JS.exam_question:LABELS_JS.exam_questions}} &middot; ${{ptos}} ${{LABELS_JS.exam_points}}</p><div class="exam-card-actions">${{idxBtn}}${{pdfBtn}}</div></article>`;
}}
function buildSectionCard(href, icon, label) {{
  if (href) return `<a href="${{href}}" class="chapter-section available" style="text-decoration:none"><span>${{icon}}</span><span>${{label}}</span></a>`;
  return `<div class="chapter-section empty"><span>${{icon}}</span><span>${{label}}</span></div>`;
}}
function buildChapter(ch, nivel, byUnit) {{
  const hlOnly = nivel === 'sl' && !ch.sl;
  // Dins d'una unitat/capítol ordenem per data ascendent (Parcial 1 abans del 2, etc.).
  const exs = (byUnit[ch.num]||[]).sort((a,b) => (a.col.fecha||'').localeCompare(b.col.fecha||''));
  const examCount = exs.length;
  const sections = [
    buildSectionCard(ch.apuntes, '📄', LABELS_JS.section_card_apunts),
    buildSectionCard(ch.fichas, '📝', LABELS_JS.section_card_fitxes),
    buildSectionCard(ch.soluciones, '✅', LABELS_JS.section_card_solucions),
    buildSectionCard(ch.extra, '🔗', LABELS_JS.section_card_extra),
  ].join('');
  const examsBox = examCount > 0
    ? `<div style="margin-top:1.2rem"><h4 style="font-size:0.85rem;color:var(--text-soft);margin:0 0 0.6rem;text-transform:uppercase;letter-spacing:0.04em;font-weight:600">${{LABELS_JS.exams_unit_title}} (${{examCount}})</h4><div class="exam-list">${{exs.map(({{col,ejs}}) => renderExamCard(col, ejs)).join('')}}</div></div>`
    : `<p style="font-size:0.82rem;color:var(--text-faint);margin:1rem 0 0">${{LABELS_JS.no_exams_unit}}</p>`;
  const examBadge = examCount > 0
    ? `<span class="tag tag-purple" style="font-size:0.65rem;margin-left:auto">${{examCount}} ${{examCount===1?LABELS_JS.examens_count_one:LABELS_JS.examens_count_many}}</span>`
    : (ch.note ? `<span class="tag tag-purple" style="font-size:0.65rem;margin-left:auto">${{escHtml(ch.note)}}</span>` : '');
  return `<div class="chapter-item ${{hlOnly?'hl-only':''}}"><div class="chapter-header" onclick="toggleChapter(this)"><span class="chapter-num">${{ch.num}}</span><span class="chapter-title">${{escHtml(ch.title)}}</span>${{examBadge}}<span class="chapter-arrow">&#9660;</span></div><div class="chapter-body">${{hlOnly?`<p style="font-size:0.88rem;color:var(--text-faint);padding:0.5rem 0">${{LABELS_JS.ib_chapter_hlonly}}</p>`:`<div class="chapter-sections">${{sections}}</div>${{examsBox}}`}}</div></div>`;
}}
function renderChapters(nivel, byUnit) {{ document.getElementById('chapters-' + nivel).innerHTML = CHAPTERS.map(ch => buildChapter(ch, nivel, byUnit)).join(''); }}
function toggleChapter(h) {{ h.parentElement.classList.toggle('open'); }}
function showNivel(id, btn) {{
  document.querySelectorAll('.promo-panel').forEach(p => p.classList.remove('active'));
  document.querySelectorAll('.promo-tab').forEach(t => t.classList.remove('active'));
  document.getElementById('nivel-' + id).classList.add('active');
  btn.classList.add('active');
}}
function toggleMenu(){{document.querySelector("nav").classList.toggle("open");}}
function toggleTheme(){{var h=document.documentElement,n=h.getAttribute('data-theme')==='dark'?'light':'dark';h.setAttribute('data-theme',n);localStorage.setItem('theme',n);}}

fetch('/assets/data/ejercicios-index.json', {{ cache: 'no-cache' }})
  .then(r => r.ok ? r.json() : Promise.reject(r.status))
  .then(idx => {{
    const cols = new Map();
    for (const e of (idx.ejercicios || [])) {{
      const c = e.coleccion || {{}};
      const m = e.tags && e.tags.materia;
      if (m !== 'ib-ai-hl' && m !== 'ib-ai-sl') continue;
      if (c.promocion !== PROMO) continue;
      // Només mostrem exàmens al hub: les pràctiques/exercicis de classe es llisten a /aula/<materia>/apuntes/
      if (c.tipo && c.tipo !== 'examen') continue;
      if (!cols.has(c.id)) cols.set(c.id, {{ col: c, ejs: [] }});
      cols.get(c.id).ejs.push(e);
    }}
    const byUnit = {{}};
    const globals = [];
    for (const entry of cols.values()) {{
      const u = unitNumOf(entry.col.id);
      if (u) {{ (byUnit[u] = byUnit[u] || []).push(entry); }}
      else {{ globals.push(entry); }}
    }}
    renderChapters('hl', byUnit);
    renderChapters('sl', byUnit);
    const params = new URLSearchParams(window.location.search);
    if (params.get('nivel') === 'sl') document.querySelectorAll('.promo-tab')[1].click();

    // Globals també ordenats cronològicament (ASC).
    globals.sort((a,b) => (a.col.fecha||'').localeCompare(b.col.fecha||''));
    const cont = document.getElementById('globals-list');
    const count = document.getElementById('globals-count');
    if (globals.length === 0) {{
      count.textContent = '0';
      cont.innerHTML = `<p style="color:var(--text-faint);font-size:0.9rem;padding:1rem 0">${{LABELS_JS.globals_empty}}</p>`;
    }} else {{
      count.textContent = globals.length + (globals.length===1 ? ' ' + LABELS_JS.examens_count_one : ' ' + LABELS_JS.examens_count_many);
      cont.innerHTML = globals.map(({{col,ejs}}) => renderExamCard(col, ejs)).join('');
    }}
  }})
  .catch(err => {{
    renderChapters('hl', {{}});
    renderChapters('sl', {{}});
    document.getElementById('globals-count').textContent = 'error';
    document.getElementById('globals-list').innerHTML = `<p style="color:var(--text-faint);font-size:0.9rem">${{LABELS_JS.globals_load_error}}</p>`;
    console.error('exams:', err);
  }});
</script>
</body>
</html>
"""


def main():
    for s in SUBJECTS:
        for lang in LANGS:
            if lang == "es":
                out = REPO / "docencia" / s["code"] / "index.html"
            else:
                out = REPO / lang / "docencia" / s["code"] / "index.html"
            out.parent.mkdir(parents=True, exist_ok=True)
            if s["type"] == "ib":
                out.write_text(render_ib_hub(s, lang), encoding="utf-8")
            else:
                out.write_text(render_regular_hub(s, lang), encoding="utf-8")
            print(f"  ✓ {out.relative_to(REPO)}")


if __name__ == "__main__":
    main()
