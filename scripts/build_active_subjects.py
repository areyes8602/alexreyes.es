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
        "ib_blocks_h2": "Buscar por syllabus IB",
        "units_help_regular": "Cada unidad contiene los apuntes de clase, las fichas de ejercicios con sus soluciones, y los exámenes realizados.",
        "ib_blocks_help": "Índice del syllabus oficial: 5 bloques (T1-T5) con sus subtemas NM (común SL/HL) y TANS (solo HL). Útil para revisar de cara al examen — cada subtema lista las unidades didácticas y ejercicios que lo cubren.",
        "ib_units_h2": "Unidades didácticas",
        "ib_units_help": "Las unidades en el orden en que se imparten en clase. Cada unidad agrupa apuntes, ejercicios y materiales de varios subtemas del syllabus IB.",
        "exams_h2": "Exámenes",
        "exams_help": "Listado cronológico de los exámenes oficiales realizados. Cada examen está etiquetado con los subtemas NM/TANS que cubre.",
        "subtema_empty": "Aún no hay material publicado para este subtema",
        "subtema_with_content": "Material disponible",
        "unidad_empty": "Sin contenido publicado todavía",
        "unidad_covers": "Cubre",
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
        "summary_exams_label": "Exámenes",
        "summary_fitxes_label": "Listado",
        "summary_apunts_label": "Apuntes",
        "summary_yes": "Sí",
        "summary_no": "No",
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
        "ib_blocks_h2": "Cercar pel syllabus IB",
        "units_help_regular": "Cada unitat conté els apunts de classe, les fitxes d'exercicis amb les seves solucions, i els exàmens realitzats.",
        "ib_blocks_help": "Índex del syllabus oficial: 5 blocs (T1-T5) amb els seus subtemes NM (comú SL/HL) i TANS (només HL). Útil per repassar de cara a l'examen — cada subtema llista les unitats didàctiques i exercicis que el cobreixen.",
        "ib_units_h2": "Unitats didàctiques",
        "ib_units_help": "Les unitats en l'ordre en què s'imparteixen a classe. Cada unitat agrupa apunts, exercicis i materials de diversos subtemes del syllabus IB.",
        "exams_h2": "Exàmens",
        "exams_help": "Llistat cronològic dels exàmens oficials realitzats. Cada examen està etiquetat amb els subtemes NM/TANS que cobreix.",
        "subtema_empty": "Encara no hi ha material publicat per a aquest subtema",
        "subtema_with_content": "Material disponible",
        "unidad_empty": "Sense contingut publicat encara",
        "unidad_covers": "Cobreix",
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
        "summary_exams_label": "Exàmens",
        "summary_fitxes_label": "Llistat",
        "summary_apunts_label": "Apunts",
        "summary_yes": "Sí",
        "summary_no": "No",
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
        "ib_blocks_h2": "Search by IB syllabus",
        "units_help_regular": "Each unit contains the class notes, exercise sheets with solutions, and the exams from that unit.",
        "ib_blocks_help": "Official syllabus index: 5 topics (T1-T5) with their NM subtopics (shared SL/HL) and TANS (HL only). Useful for exam revision — each subtopic lists the teaching units and exercises that cover it.",
        "ib_units_h2": "Teaching units",
        "ib_units_help": "Units in the order they are taught in class. Each unit groups notes, exercises and resources covering several IB syllabus subtopics.",
        "exams_h2": "Exams",
        "exams_help": "Chronological list of official exams. Each exam is tagged with the NM/TANS subtopics it covers.",
        "subtema_empty": "No content published yet for this subtopic",
        "subtema_with_content": "Content available",
        "unidad_empty": "No content published yet",
        "unidad_covers": "Covers",
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
        "summary_exams_label": "Exams",
        "summary_fitxes_label": "Lists",
        "summary_apunts_label": "Notes",
        "summary_yes": "Yes",
        "summary_no": "No",
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
        "es": "Grupos A y E &middot; Currículum LOMLOE",
        "ca": "Grups A i E &middot; Currículum LOMLOE",
        "en": "Groups A and E &middot; LOMLOE curriculum",
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
        "es": "1&ordm; de Bachillerato &middot; Currículum LOMLOE",
        "ca": "1r de Batxillerat &middot; Currículum LOMLOE",
        "en": "1st year Bachillerato &middot; LOMLOE curriculum",
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
    "materia_filter": "ccss-1btl",
    # Avís temporal (es mostra mentre `new Date() < expire_iso`).
    # `expire_iso` és en hora local del navegador (sense Z), així que l'avís
    # desapareix automàticament a les 00:00 del dia indicat (hora de Barcelona).
    "notice": {
        "text": {
            "es": "📌 <strong>Aviso:</strong> el <strong>22 de mayo de 2026 a las 23:59</strong> es la fecha límite para entregar el trabajo de Estadística al Teams de la asignatura.",
            "ca": "📌 <strong>Avís:</strong> el <strong>22 de maig de 2026 a les 23:59</strong> és la data límit per entregar el treball d'Estadística al Teams de l'assignatura.",
            "en": "📌 <strong>Notice:</strong> <strong>22 May 2026 at 23:59</strong> is the deadline to submit the Statistics project on the subject's Teams.",
        },
        "expire_iso": "2026-05-23T00:00:00",
    },
    # Units in language of instruction (Catalan), descriptions per language.
    # Keep keys aligned with SUBJ_2ESO so the regular hub renderer can use them.
    "units": [
        {"num":"01","slug":"nombres-reals","title":"Nombres reals","llibre":"Baula 1","inici":"16 sep 2025","final":"7 oct 2025","trimestre":"1a",
         "desc_l":{"ca":"Nombres reals, intervals, valor absolut, aproximació i errors.",
                   "es":"Números reales, intervalos, valor absoluto, aproximación y errores.",
                   "en":"Real numbers, intervals, absolute value, approximation and errors."},
         "apunts":"/aula/ccss-1btl/apuntes/u-nombres-reals/"},
        {"num":"02","slug":"polinomis","title":"Polinomis","llibre":"—","inici":"8 oct 2025","final":"28 oct 2025","trimestre":"1a",
         "desc_l":{"ca":"Operacions amb polinomis, divisió, regla de Ruffini i factorització.",
                   "es":"Operaciones con polinomios, división, regla de Ruffini y factorización.",
                   "en":"Polynomial operations, division, Ruffini's rule and factorization."}},
        {"num":"03","slug":"equacions-sistemes","title":"Equacions i sistemes d'equacions","llibre":"Baula 3","inici":"29 oct 2025","final":"11 nov 2025","trimestre":"1a",
         "desc_l":{"ca":"Equacions de 1r i 2n grau, exponencials, logarítmiques i sistemes lineals i no lineals.",
                   "es":"Ecuaciones de primer y segundo grado, exponenciales, logarítmicas y sistemas lineales y no lineales.",
                   "en":"First and second degree, exponential and logarithmic equations and linear/non-linear systems."},
         "fitxes":"/aula/ccss-1btl/fitxes/u-equacions-pol-bi-rac/"},
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

# IB AI HL/SL — Estructura oficial del syllabus IBO (5 bloques · NM/TANS)
# Se carga directamente desde assets/data/tags.json (la única fuente de verdad).
# Los códigos NM (Nivel Medio = SL) aplican a HL y SL.
# Los códigos TANS (Temas Adicionales del Nivel Superior) aplican solo a HL.
def load_ib_temas():
    """Lee tags.json y devuelve la lista de bloques con sus subtemas."""
    tags = json.loads((REPO / "assets/data/tags.json").read_text(encoding="utf-8"))
    bloques = tags["namespaces"]["ambito_iba"]["valores"]
    subtemas = tags["namespaces"]["concepto_iba"]["valores"]
    out = []
    for tcode in ["T1", "T2", "T3", "T4", "T5"]:
        bloque_label = bloques[tcode]["label"]  # dict con es/ca/en
        sub_lista = []
        for code, meta in subtemas.items():
            if meta.get("ambito_iba") != tcode:
                continue
            label = meta["label"]
            es_label = label.get("es", code)
            # Quitar el prefijo del código del título: "NM 1.1 — Notación científica" → "Notación científica"
            title_pure = es_label.split(" — ", 1)[1] if " — " in es_label else es_label
            slug = code.replace(" ", "-").replace(".", "-")  # "NM 1.1" → "NM-1-1"
            nivel = "HL" if code.startswith("TANS") else "NM"  # NM = ambos, TANS = HL
            sub_lista.append({
                "code": code, "slug": slug, "title": title_pure, "nivel": nivel,
            })
        # Ordenar: NM primero (alfanumérico), luego TANS (alfanumérico)
        def sort_key(s):
            parts = s["code"].replace("NM ", "").replace("TANS ", "").split(".")
            tema = int(parts[0])
            num = int(parts[1])
            return (0 if s["code"].startswith("NM") else 1, tema, num)
        sub_lista.sort(key=sort_key)
        out.append({
            "code": tcode,
            "label": bloque_label,
            "subtemas": sub_lista,
        })
    return out

IB_TEMAS = load_ib_temas()


def load_ib_unidades():
    """Lee assets/data/ib-unidades.json: dos listas (HL y SL) de unidades didácticas propias."""
    fp = REPO / "assets/data/ib-unidades.json"
    if not fp.exists():
        return [], []
    data = json.loads(fp.read_text(encoding="utf-8"))
    # Compatibilidad con schema anterior (unidades única) si todavía existe
    if "unidades" in data and "unidades_hl" not in data:
        return data.get("unidades", []), []
    return data.get("unidades_hl", []), data.get("unidades_sl", [])

IB_UNIDADES_HL, IB_UNIDADES_SL = load_ib_unidades()

def make_ib_subject(promo, anyo_examen):
    return {
        "code": f"ib-ai/{promo}",
        "type": "ib",
        "lang_taught": "en",
        "promo": promo,
        "title": {"es": f"Promoción {promo}", "ca": f"Promoció {promo}", "en": f"{promo} Cohort"},
        "subtitle": {
            "es": f"Exámenes oficiales mayo {anyo_examen}",
            "ca": f"Exàmens oficials maig {anyo_examen}",
            "en": f"Official exams May {anyo_examen}",
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
      <span>Barcelona &middot; &copy; 2026 Àlex Reyes &middot; <a href="/assets/NOTICES.txt" style="color:inherit">Licencias</a></span>
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

    # Avís opcional (es mostra fins a la data d'expiració, després s'amaga sol via JS)
    notice_html = ""
    notice = s.get("notice")
    if notice:
        notice_text = picker_lang_value(notice["text"], lang)
        expire_iso = notice["expire_iso"]
        notice_html = (
            '\n    <div id="subject-notice" class="subject-notice" style="display:none;background:rgba(245,158,11,0.10);border:1px solid rgba(245,158,11,0.35);border-left:4px solid #f59e0b;padding:0.85rem 1.1rem;border-radius:8px;margin:1.2rem 0 0;color:var(--text);font-size:0.95rem;line-height:1.45">'
            f'\n      {notice_text}'
            '\n    </div>'
            '\n    <script>(function(){'
            f'var d=new Date("{expire_iso}");'
            'if(new Date()<d){var n=document.getElementById("subject-notice");if(n)n.style.display="block";}'
            '})();</script>\n'
        )

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
{notice_html}
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
const LABELS_JS = {json.dumps({k: L[k] for k in ['exam_questions','exam_question','exam_points','exam_btn_pdf','exam_btn_html','no_exams_unit','exams_unit_title','globals_empty','globals_load_error','section_card_apunts','section_card_fitxes','section_card_solucions','unit_meta_book','unit_meta_dates','unit_meta_trim','examens_count_one','examens_count_many','trimestre_tag','summary_exams_label','summary_fitxes_label','summary_apunts_label','summary_yes','summary_no']}, ensure_ascii=False)};

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
function summaryBadge(label, value, color, hasContent) {{
  const cls = hasContent ? `tag ${{color}}` : 'tag tag-gray';
  const sty = hasContent ? 'font-size:0.65rem;font-weight:500' : 'font-size:0.65rem;font-weight:500;opacity:0.55';
  return `<span class="${{cls}}" style="${{sty}}">${{label}}: ${{value}}</span>`;
}}
function buildUnit(u, examsByUnit) {{
  // Dins d'una unitat ordenem per data ascendent: Parcial 1 abans del Parcial 2, simulacre abans del global, etc.
  const exs = (examsByUnit[u.num]||[]).sort((a,b) => (a.col.fecha||'').localeCompare(b.col.fecha||''));
  const examCount = exs.length;
  const fitxesCount = u.fitxes ? 1 : 0;
  const hasApunts = !!u.apunts;
  const sections = [
    buildSectionCard(u.apunts, '📄', LABELS_JS.section_card_apunts),
    buildSectionCard(u.fitxes, '📝', LABELS_JS.section_card_fitxes),
    buildSectionCard(u.solucions, '✅', LABELS_JS.section_card_solucions),
  ].join('');
  const examsBox = examCount > 0
    ? `<div style="margin-top:1.2rem"><h4 style="font-size:0.85rem;color:var(--text-soft);margin:0 0 0.6rem;text-transform:uppercase;letter-spacing:0.04em;font-weight:600">${{LABELS_JS.exams_unit_title}} (${{examCount}})</h4><div class="exam-list">${{exs.map(({{col,ejs}}) => renderExamCard(col, ejs)).join('')}}</div></div>`
    : `<p style="font-size:0.82rem;color:var(--text-faint);margin:1rem 0 0">${{LABELS_JS.no_exams_unit}}</p>`;
  // Resum visible al header (abans de desplegar): exàmens, llistat d'exercicis i apunts.
  const summaryBadges = [
    summaryBadge(LABELS_JS.summary_exams_label, examCount, 'tag-purple', examCount > 0),
    summaryBadge(LABELS_JS.summary_fitxes_label, fitxesCount, 'tag-orange', fitxesCount > 0),
    summaryBadge(LABELS_JS.summary_apunts_label, hasApunts ? LABELS_JS.summary_yes : LABELS_JS.summary_no, 'tag-green', hasApunts),
  ].join('');
  const headerBadges = `<span class="unit-summary-badges" style="margin-left:auto;display:inline-flex;gap:0.3rem;flex-wrap:wrap;align-items:center">${{summaryBadges}}</span>`;
  const meta = (u.llibre || u.inici) ? `<div class="unit-meta">${{u.llibre?`<span>📖 ${{LABELS_JS.unit_meta_book}} ${{escHtml(u.llibre)}}</span>`:''}}${{u.inici?`<span>📅 ${{escHtml(u.inici)}} → ${{escHtml(u.final||'')}}</span>`:''}}${{u.trimestre?`<span>🎯 ${{u.trimestre}} ${{LABELS_JS.unit_meta_trim}}</span>`:''}}</div>` : '';
  return `<div class="chapter-item"><div class="chapter-header" onclick="toggleChapter(this)"><span class="chapter-num">${{u.num}}</span><span class="chapter-title">${{escHtml(u.title)}}</span>${{headerBadges}}<span class="chapter-arrow">&#9660;</span></div><div class="chapter-body">${{meta}}<p style="font-size:0.88rem;color:var(--text-soft);margin:0 0 1rem">${{escHtml(u.desc)}}</p><div class="chapter-sections">${{sections}}</div>${{examsBox}}</div></div>`;
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

    # Estructura para JS: bloques T1-T5 con sus subtemas NM/TANS
    temas_for_js = []
    for t in IB_TEMAS:
        temas_for_js.append({
            "code": t["code"],
            "label": t["label"].get(lang, t["label"]["es"]),
            "subtemas": t["subtemas"],  # ya tienen code, slug, title, nivel
        })
    temas_json = json.dumps(temas_for_js, ensure_ascii=False)

    # Unidades didácticas propias — dos listas independientes (HL y SL)
    def serialize_unidades(unidades_src):
        out = []
        for u in unidades_src:
            if u.get("promo", "all") not in ("all", promo):
                continue
            out.append({
                "id": u["id"],
                "title": u["title"].get(lang, u["title"]["es"]),
                "intro": u.get("intro", {}).get(lang, u.get("intro", {}).get("es", "")),
                "tags_iba": u.get("tags_iba", []),
                "orden": u.get("orden", 999),
                "trimestre": u.get("trimestre", ""),
                "tier": u.get("tier", "free"),
            })
        out.sort(key=lambda u: u["orden"])
        return out

    unidades_hl_for_js = serialize_unidades(IB_UNIDADES_HL)
    unidades_sl_for_js = serialize_unidades(IB_UNIDADES_SL)
    unidades_hl_json = json.dumps(unidades_hl_for_js, ensure_ascii=False)
    unidades_sl_json = json.dumps(unidades_sl_for_js, ensure_ascii=False)

    # Etiquetas de trimestre (de ib-unidades.json)
    trimestres_data = {}
    try:
        ibu = json.loads((REPO / "assets/data/ib-unidades.json").read_text(encoding="utf-8"))
        for tcode, tinfo in ibu.get("trimestres", {}).items():
            trimestres_data[tcode] = tinfo["label"].get(lang, tinfo["label"]["es"])
    except Exception:
        pass
    trimestres_json = json.dumps(trimestres_data, ensure_ascii=False)

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

    <!-- ━━━ Eje 1: UNIDADES DIDÁCTICAS (pedagógicas, propias) ━━━ -->
    <h2 style="font-size:1.1rem;margin:2.5rem 0 0.4rem">{L['ib_units_h2']}</h2>
    <p style="color:var(--text-soft);font-size:0.92rem;margin-bottom:1rem">{L['ib_units_help']}</p>

    <div class="promo-tabs">
      <button class="promo-tab active" onclick="showNivel('hl', this)">{L['promo_tab_hl']}</button>
      <button class="promo-tab" onclick="showNivel('sl', this)">{L['promo_tab_sl']}</button>
    </div>

    <div id="nivel-hl" class="promo-panel active">
      <div class="chapter-list" id="unidades-hl"></div>
    </div>

    <div id="nivel-sl" class="promo-panel">
      <p style="color:var(--text-soft);font-size:0.92rem;margin-bottom:1rem">{L['promo_sl_intro']}</p>
      <div class="chapter-list" id="unidades-sl"></div>
    </div>

    <!-- ━━━ Eje 2: SYLLABUS IB (referencia, colapsado) ━━━ -->
    <details class="syllabus-section" style="margin-top:2.5rem">
      <summary style="cursor:pointer;font-size:1.1rem;font-weight:600;padding:0.5rem 0;color:var(--text)">
        📚 {L['ib_blocks_h2']}
      </summary>
      <p style="color:var(--text-soft);font-size:0.92rem;margin:0.6rem 0 1rem">{L['ib_blocks_help']}</p>
      <div class="bloque-list" id="bloques-hl"></div>
    </details>

    <section style="margin-top:3rem">
      <div style="display:flex;align-items:baseline;gap:0.6rem;flex-wrap:wrap;margin-bottom:0.4rem">
        <h2 style="font-size:1.2rem;margin:0">{L['exams_h2']}</h2>
        <span class="tag tag-gray" id="exams-count" style="font-size:0.7rem">{L['globals_loading']}</span>
      </div>
      <p style="color:var(--text-soft);font-size:0.92rem;margin-bottom:1rem">{L['exams_help']}</p>
      <div id="exams-list" class="exam-list"></div>
    </section>

  </div>
  <aside class="ibo-disclaimer">
    <p><strong>Aviso · Notice:</strong> Este material ha sido desarrollado de forma independiente y no está aprobado, patrocinado ni endorsado por la International Baccalaureate Organization. <em>This work has been developed independently from and is not endorsed by the International Baccalaureate Organization.</em></p>
    <p class="ibo-disclaimer-marks">"International Baccalaureate®", "IB Diploma Programme®", "Bachillerato Internacional®" y "IB®" son marcas registradas de la International Baccalaureate Organization.</p>
  </aside>
</main>

{footer_html(L)}

<script>
const TEMAS = {temas_json};
const UNIDADES_HL = {unidades_hl_json};
const UNIDADES_SL = {unidades_sl_json};
const TRIMESTRES = {trimestres_json};
const PROMO = {json.dumps(promo)};
const MONTHS = {months_js};
const LABELS_JS = {json.dumps({k: L[k] for k in ['exam_questions','exam_question','exam_points','exam_btn_pdf','exam_btn_html','globals_empty','globals_load_error','examens_count_one','examens_count_many','subtema_empty','subtema_with_content','section_card_apunts','section_card_fitxes','section_card_solucions','section_card_extra','unidad_empty','unidad_covers']}, ensure_ascii=False)};

function fmtFecha(iso) {{ if(!iso) return ''; const [y,m,d]=iso.split('-'); return `${{parseInt(d,10)}} ${{MONTHS[parseInt(m,10)-1]}} ${{y}}`; }}
function escHtml(s) {{ return String(s||'').replace(/[&<>"']/g, c => ({{'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}}[c])); }}
function renderExamCard(col, ejs) {{
  const ptos = ejs.reduce((s,e) => s + (e.puntuacion||0), 0);
  const npreg = ejs.length;
  const pdfBtn = col.pdf_enunciados ? `<a class="exam-card-btn pdf" href="${{escHtml(col.pdf_enunciados)}}" target="_blank" rel="noopener" title="${{LABELS_JS.exam_btn_pdf}}">📄 ${{LABELS_JS.exam_btn_pdf}}</a>` : '';
  const idxBtn = col.url_index ? `<a class="exam-card-btn html" href="${{escHtml(col.url_index)}}">📋 ${{LABELS_JS.exam_btn_html}}</a>` : '';
  return `<article class="exam-card"><div class="exam-card-head"><span class="exam-card-date">${{escHtml(fmtFecha(col.fecha))}}</span>${{col.grupo?`<span class="tag tag-orange" style="font-size:0.7rem">${{escHtml(col.grupo)}}</span>`:''}}</div><h3 class="exam-card-title">${{escHtml(col.titulo||col.id)}}</h3><p class="exam-card-meta">${{npreg}} ${{npreg===1?LABELS_JS.exam_question:LABELS_JS.exam_questions}} &middot; ${{ptos}} ${{LABELS_JS.exam_points}}</p><div class="exam-card-actions">${{idxBtn}}${{pdfBtn}}</div></article>`;
}}

// Card de sección dentro de un subtema (apuntes/ejercicios/soluciones/materiales)
function buildSectionCard(href, icon, label) {{
  if (href) return `<a href="${{href}}" class="chapter-section available" style="text-decoration:none"><span>${{icon}}</span><span>${{label}}</span></a>`;
  return `<div class="chapter-section empty"><span>${{icon}}</span><span>${{label}}</span></div>`;
}}

// Subtema (NM o TANS) — link a /aula/ib-ai-hl/syllabus/#<slug>
function buildSubtema(sub, conceptosConContenido) {{
  const tieneContenido = conceptosConContenido.has(sub.code);
  const url = `/aula/ib-ai-hl/syllabus/#${{sub.slug}}`;
  const nivelClass = `subtema-nivel-${{sub.nivel.toLowerCase()}}`;
  const statusBadge = tieneContenido
    ? `<span class="tag tag-green" style="font-size:0.62rem;margin-left:auto">●</span>`
    : `<span class="tag tag-gray" style="font-size:0.62rem;margin-left:auto;opacity:0.5">○</span>`;
  return `<a href="${{url}}" class="subtema-link ${{nivelClass}}"><span class="chapter-num subtema-num">${{escHtml(sub.code)}}</span><span class="chapter-title">${{escHtml(sub.title)}}</span>${{statusBadge}}<span class="chapter-arrow">→</span></a>`;
}}

// Calcula apuntes, fichas y exámenes asociados a una unidad por solapamiento
// de tags concepto_iba. Devuelve URLs y conteos por tipo.
function getUnidadResources(u, ctx) {{
  const unidadTags = u.tags_iba || [];
  // Apuntes: primer concepto con apuntes en la unidad (con ?from para libro digital)
  let apuntesHref = null;
  let apuntesCount = 0;
  for (const c of (ctx.conceptosApuntes || [])) {{
    if (!unidadTags.includes(c.code)) continue;
    apuntesCount++;
    if (!apuntesHref) {{
      apuntesHref = `/aula/ib-ai-hl/conceptos/${{c.slug}}/?from=${{encodeURIComponent(u.id)}}`;
    }}
  }}
  // Ejercicios (fichas) y exámenes
  const fichasMap = {{}};
  const examenesArr = [];
  for (const e of (ctx.allEjs || [])) {{
    const ejTags = (e.tags && e.tags.concepto_iba) || [];
    if (!unidadTags.some(t => ejTags.includes(t))) continue;
    const tipo = e.coleccion && e.coleccion.tipo;
    if (tipo === 'ficha') {{
      const id = e.coleccion.id;
      if (!fichasMap[id]) fichasMap[id] = {{ id, titulo: e.coleccion.titulo, url: e.coleccion.url_index, count: 0 }};
      fichasMap[id].count++;
    }}
  }}
  const fichas = Object.values(fichasMap);
  const ejerciciosHref = fichas[0] ? fichas[0].url : null;
  const ejerciciosCount = fichas.reduce((acc, f) => acc + f.count, 0);
  return {{
    apuntesHref, apuntesCount,
    ejerciciosHref, ejerciciosCount,
  }};
}}

// Section card con icono + label + opcionalmente meta. Igual al patrón CCSS.
function buildIBSectionCard(href, icon, label, meta) {{
  const metaHtml = meta ? `<span class="chapter-section-meta">${{escHtml(meta)}}</span>` : '';
  if (href) return `<a href="${{escHtml(href)}}" class="chapter-section available" style="text-decoration:none"><span>${{icon}}</span><span>${{escHtml(label)}}</span>${{metaHtml}}</a>`;
  return `<div class="chapter-section empty"><span>${{icon}}</span><span>${{escHtml(label)}}</span></div>`;
}}

// Unidad didáctica (eje pedagógico) — chapter-item plegable con sus 3 section cards
// nivel: 'hl' o 'sl'. Las listas son independientes (HL y SL son currículos distintos).
function buildUnidad(u, nivel, ctx) {{
  const isSL = nivel === 'sl';
  const res = getUnidadResources(u, ctx || {{conceptosApuntes:[], allEjs:[]}});
  const tagsBadges = (u.tags_iba || []).map(t => {{
    const cls = t.startsWith('TANS') ? 'subtema-nivel-hl' : 'subtema-nivel-nm';
    const slug = t.replace(/\\s|\\./g, '-');
    return `<a href="/aula/ib-ai-hl/syllabus/#${{slug}}" class="unidad-tag ${{cls}}">${{escHtml(t)}}</a>`;
  }}).join(' ');
  const intro = u.intro ? `<p class="unidad-intro">${{escHtml(u.intro)}}</p>` : '';
  const tagsBox = tagsBadges
    ? `<div class="unidad-tags"><span class="unidad-tags-label">${{LABELS_JS.unidad_covers}}:</span> ${{tagsBadges}}</div>`
    : '';
  const prefix = isSL ? 'US' : 'U';
  const numero = u.orden ? `<span class="chapter-num unidad-num">${{prefix}}${{String(u.orden).padStart(2,'0')}}</span>` : '';

  // 3 section cards igual que CCSS: Apuntes / Ejercicios / Material extra
  const apuntesMeta = res.apuntesCount > 0 ? `${{res.apuntesCount}} ${{res.apuntesCount === 1 ? 'concepto' : 'conceptos'}}` : '';
  const ejerciciosMeta = res.ejerciciosCount > 0 ? `${{res.ejerciciosCount}} ${{res.ejerciciosCount === 1 ? 'ejercicio' : 'ejercicios'}}` : '';
  const sections = [
    buildIBSectionCard(res.apuntesHref, '📄', LABELS_JS.section_card_apunts, apuntesMeta),
    buildIBSectionCard(res.ejerciciosHref, '📝', LABELS_JS.section_card_fitxes, ejerciciosMeta),
    buildIBSectionCard(null, '🔗', LABELS_JS.section_card_extra, ''),
  ].join('');

  return `<div class="chapter-item unidad-item"><div class="chapter-header" onclick="toggleChapter(this)">${{numero}}<span class="chapter-title">${{escHtml(u.title)}}</span><span class="chapter-arrow">&#9660;</span></div><div class="chapter-body">${{intro}}${{tagsBox}}<div class="chapter-sections">${{sections}}</div></div></div>`;
}}

// Bloque (T1-T5) — chapter-item plegable que contiene los subtemas dentro
function buildBloque(t, nivel, conceptosConContenido) {{
  const subs = t.subtemas.filter(s => nivel === 'hl' || s.nivel === 'NM');
  const subtemasHtml = subs.map(s => buildSubtema(s, conceptosConContenido)).join('');
  const countBadge = `<span class="tag tag-purple" style="font-size:0.65rem;margin-left:auto">${{subs.length}} subtemas</span>`;
  return `<div class="chapter-item bloque-tema"><div class="chapter-header" onclick="toggleChapter(this)"><span class="chapter-num bloque-num">${{t.code}}</span><span class="chapter-title">${{escHtml(t.label)}}</span>${{countBadge}}<span class="chapter-arrow">&#9660;</span></div><div class="chapter-body"><div class="subtemas-stack">${{subtemasHtml}}</div></div></div>`;
}}

function renderBloques(nivel, conceptosConContenido) {{
  // Solo hay un panel de bloques (visible siempre, dentro del details)
  // pero filtramos NM/TANS según el nivel activo.
  const el = document.getElementById('bloques-' + nivel);
  if (el) el.innerHTML = TEMAS.map(t => buildBloque(t, nivel, conceptosConContenido)).join('');
}}
function renderUnidades(nivel, ctx) {{
  // HL y SL son currículos independientes con sus propias listas.
  const lista = nivel === 'sl' ? UNIDADES_SL : UNIDADES_HL;
  const el = document.getElementById('unidades-' + nivel);
  if (!el) return;
  if (lista.length === 0) {{
    el.innerHTML = `<p style="color:var(--text-faint);font-size:0.9rem;padding:1rem 0">${{LABELS_JS.unidad_empty}}</p>`;
    return;
  }}
  // Agrupar por trimestre — insertar header cuando cambia
  let lastT = null;
  const parts = [];
  for (const u of lista) {{
    if (u.trimestre && u.trimestre !== lastT) {{
      const label = TRIMESTRES[u.trimestre] || u.trimestre;
      parts.push(`<h3 class="trimestre-header">${{escHtml(label)}}</h3>`);
      lastT = u.trimestre;
    }}
    parts.push(buildUnidad(u, nivel, ctx));
  }}
  el.innerHTML = parts.join('');
}}
function toggleChapter(h) {{ h.parentElement.classList.toggle('open'); }}
function showNivel(id, btn) {{
  document.querySelectorAll('.promo-panel').forEach(p => p.classList.remove('active'));
  document.querySelectorAll('.promo-tab').forEach(t => t.classList.remove('active'));
  document.getElementById('nivel-' + id).classList.add('active');
  btn.classList.add('active');
}}
function toggleMenu(){{document.querySelector("nav").classList.toggle("open");}}
function toggleTheme(){{var h=document.documentElement,n=h.getAttribute('data-theme')==='dark'?'light':'dark';h.setAttribute('data-theme',n);localStorage.setItem('theme',n);}}

Promise.all([
  fetch('/assets/data/ejercicios-index.json', {{ cache: 'no-cache' }}).then(r => r.ok ? r.json() : Promise.reject(r.status)),
  fetch('/assets/data/conceptos-apuntes.json', {{ cache: 'no-cache' }}).then(r => r.ok ? r.json() : {{conceptos:[]}}).catch(() => ({{conceptos:[]}})),
  fetch('/assets/data/tags.json', {{ cache: 'no-cache' }}).then(r => r.ok ? r.json() : {{namespaces:{{}}}}).catch(() => ({{namespaces:{{}}}})),
])
  .then(([idx, conceptosApuntesRaw, tagsData]) => {{
    const cols = new Map();
    const conceptosConContenido = new Set();
    // Filtrar ejercicios IB (todos, no solo exámenes) para la lista plana de las unidades
    const allEjsIB = [];
    for (const e of (idx.ejercicios || [])) {{
      const c = e.coleccion || {{}};
      const m = e.tags && e.tags.materia;
      if (m !== 'ib-ai-hl' && m !== 'ib-ai-sl') continue;
      // Filtrar por promoción solo cuando aplica (las fichas y apuntes_concepto suelen ser promo='all')
      const promoMatch = (c.promocion === PROMO || c.promocion === 'all' || !c.promocion);
      if (!promoMatch) continue;
      // Para la lista de exámenes globales (más abajo), seguimos solo con tipo=examen + promo específica
      if (c.tipo === 'examen' && c.promocion === PROMO) {{
        if (!cols.has(c.id)) cols.set(c.id, {{ col: c, ejs: [] }});
        cols.get(c.id).ejs.push(e);
      }}
      allEjsIB.push(e);
      // Marcar conceptos IB que tienen al menos un ejercicio
      const cs = (e.tags && e.tags.concepto_iba) || [];
      cs.forEach(x => conceptosConContenido.add(x));
    }}
    // Construir contexto que necesita buildItemsList
    const subtemasInfo = (tagsData && tagsData.namespaces && tagsData.namespaces.concepto_iba && tagsData.namespaces.concepto_iba.valores) || {{}};
    const ctx = {{
      conceptosApuntes: conceptosApuntesRaw.conceptos || [],
      allEjs: allEjsIB,
      subtemasInfo: subtemasInfo,
    }};
    renderBloques('hl', conceptosConContenido);
    renderUnidades('hl', ctx);
    renderUnidades('sl', ctx);
    const params = new URLSearchParams(window.location.search);
    if (params.get('nivel') === 'sl') document.querySelectorAll('.promo-tab')[1].click();

    // Lista de exámenes (ordenados cronológicamente ASC, todos juntos)
    const exams = [...cols.values()].sort((a,b) => (a.col.fecha||'').localeCompare(b.col.fecha||''));
    const cont = document.getElementById('exams-list');
    const count = document.getElementById('exams-count');
    if (exams.length === 0) {{
      count.textContent = '0';
      cont.innerHTML = `<p style="color:var(--text-faint);font-size:0.9rem;padding:1rem 0">${{LABELS_JS.globals_empty}}</p>`;
    }} else {{
      count.textContent = exams.length + (exams.length===1 ? ' ' + LABELS_JS.examens_count_one : ' ' + LABELS_JS.examens_count_many);
      cont.innerHTML = exams.map(({{col,ejs}}) => renderExamCard(col, ejs)).join('');
    }}
  }})
  .catch(err => {{
    renderBloques('hl', new Set());
    renderBloques('sl', new Set());
    document.getElementById('exams-count').textContent = 'error';
    document.getElementById('exams-list').innerHTML = `<p style="color:var(--text-faint);font-size:0.9rem">${{LABELS_JS.globals_load_error}}</p>`;
    console.error('exams:', err);
  }});
</script>
</body>
</html>
"""


def write_with_retry(path, content, max_retries=20, delay=1.5):
    """Escribe con reintentos. Usa write→tmp + os.replace para evitar deadlocks
    del sandbox cuando el archivo destino está siendo accedido por el host."""
    import time, os, tempfile
    for attempt in range(max_retries):
        try:
            # Escribir a un tmp en el mismo directorio (mismo filesystem para os.replace atómico)
            tmp_fd, tmp_path = tempfile.mkstemp(dir=str(path.parent), suffix='.tmp')
            with os.fdopen(tmp_fd, 'w', encoding='utf-8') as f:
                f.write(content)
            os.replace(tmp_path, str(path))
            return
        except OSError as e:
            if attempt == max_retries - 1:
                raise
            try:
                if 'tmp_path' in dir() and os.path.exists(tmp_path):
                    os.unlink(tmp_path)
            except Exception:
                pass
            time.sleep(delay)


def main():
    for s in SUBJECTS:
        for lang in LANGS:
            if lang == "es":
                out = REPO / "docencia" / s["code"] / "index.html"
            else:
                out = REPO / lang / "docencia" / s["code"] / "index.html"
            out.parent.mkdir(parents=True, exist_ok=True)
            content = render_ib_hub(s, lang) if s["type"] == "ib" else render_regular_hub(s, lang)
            write_with_retry(out, content)
            print(f"  ✓ {out.relative_to(REPO)}")


if __name__ == "__main__":
    main()
