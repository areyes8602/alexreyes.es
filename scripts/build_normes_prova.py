#!/usr/bin/env python3
"""Prova de normes de convivència de l'ESO — banc de preguntes i pàgina.

La primera classe de tutoria es dedica a llegir les normes de convivència.
Això les converteix en una prova: test + situacions on cal decidir si s'ha
incomplert alguna norma o si la sanció del professor s'ajusta a la norma.

Font única: el document oficial NormesESO_2627.docx de Maristes Sants-Les
Corts. Cada pregunta porta la seva `norma`, que és la cita literal que la
justifica; l'alumne la veu en corregir.

Genera tres coses des d'aquest mateix banc, perquè no puguin divergir:

  docencia/tutoria-2eso/normes/index.html   la prova (pública, sense respostes)
  assets/data/normes-preguntes.json         enunciats i opcions, SENSE la clau
  functions/api/_normes-clau.js             la clau i les explicacions

⚠️ La clau NO viatja mai al navegador. La correcció la fa la Function al
servidor: si les respostes correctes fossin al HTML, la prova no valdria res.

Reexecuta després de tocar PREGUNTES.
"""
import hashlib
import json
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
VERSIO = "2026-27"
GRUPS = ["2n ESO A", "2n ESO B", "2n ESO C", "2n ESO D", "2n ESO E"]

# ─── Banc de preguntes ───────────────────────────────────────────
# tipus: "test" (coneixement directe) · "situacio" (cas pràctic)
# c: índex (0-based) de l'opció correcta
# norma: cita literal del document oficial que justifica la resposta
PREGUNTES = [
  # ── TEST ───────────────────────────────────────────────────────
  dict(id="t01", tipus="test", bloc="Treball a classe",
    q="Dins de l'aula, què no pots fer en cap cas?",
    o=["Beure aigua si fa calor",
       "Menjar i beure, xiclets i llaminadures incloses",
       "Menjar només a l'hora abans del pati",
       "Menjar si el professor t'hi dona permís"],
    c=1,
    norma="Dins la classe no pots ni menjar ni beure i això inclou xiclets i llaminadures."),

  dict(id="t02", tipus="test", bloc="Treball a classe",
    q="Sortir de l'aula per anar al lavabo durant la classe…",
    o=["Es pot sempre que aixequis la mà",
       "Es pot un cop al dia",
       "No s'autoritza, tret de casos urgents",
       "Depèn de cada professor"],
    c=2,
    norma="Per mantenir l'ordre i l'atenció a les classes no s'autoritzarà, tret de casos urgents, la teva sortida per anar al lavabo, rebre encàrrecs, etc."),

  dict(id="t03", tipus="test", bloc="Canvi de classe",
    q="Durant el canvi de classe, on has de ser?",
    o=["Al passadís, esperant el professor següent",
       "Dins de la teva aula, preparant el material de la classe següent",
       "On vulguis mentre no facis soroll",
       "Als armariets, canviant els llibres"],
    c=1,
    norma="Durant el canvi de classe has d'estar dins de la teva aula, preparant el material de la classe següent."),

  dict(id="t04", tipus="test", bloc="Canvi de classe",
    q="Si el professorat es retarda, qui ha d'avisar secretaria?",
    o=["Qualsevol alumne de la classe",
       "El delegat o delegada",
       "Ningú: cal esperar dins l'aula",
       "El professor de l'aula del costat"],
    c=1,
    norma="En cas que el professorat es retardi el delegat/da ha d'avisar a secretaria."),

  dict(id="t05", tipus="test", bloc="Canvi de classe",
    q="Les portes d'intercomunicació entre aules les pot fer servir…",
    o=["Qualsevol alumne si té pressa",
       "Els delegats i delegades",
       "Només el professorat",
       "Tothom durant els canvis de classe"],
    c=2,
    norma="Les portes d'intercomunicació entre aules només les poden fer servir els professors/es."),

  dict(id="t06", tipus="test", bloc="Canvi de classe",
    q="Quan es poden obrir els armariets personals?",
    o=["Sempre que en necessitis alguna cosa",
       "Només a primera hora del matí",
       "A primera hora, a l'inici i al final del pati, al migdia, a la tarda abans d'entrar i en marxar",
       "Només al principi i al final de la jornada"],
    c=2,
    norma="Els armariets personals que teniu a la vostra disposició es poden obrir a primera hora del matí, a l'inici i al final del pati, al migdia, a la tarda abans d'entrar a classe i a l'hora de marxar."),

  dict(id="t07", tipus="test", bloc="Agenda",
    q="Per què a l'agenda no s'admeten dibuixos, fotos ni escrits?",
    o=["Perquè és material de l'escola i s'ha de retornar",
       "Perquè és una comunicació família-escola: és oberta i no privada",
       "Perquè es corregeix i s'hi posa nota",
       "Perquè la fa servir tot el grup classe"],
    c=1,
    norma="L'agenda cada dia va i ve de casa al col·legi, és una comunicació família-escola per la qual cosa és oberta i no privada, per aquest motiu no s'admetran dibuixos, fotos o escrits de cap mena. En aquest cas es demanarà comprar-ne una de nova."),

  dict(id="t08", tipus="test", bloc="Participació",
    q="Qui queda exclòs de poder formar part del consell de classe?",
    o=["Els alumnes que han repetit curs",
       "Els alumnes amb notificacions greus",
       "Els alumnes que arriben tard sovint",
       "Ningú: tothom s'hi pot presentar"],
    c=1,
    norma="Els alumnes amb notificacions greus queden exclosos de la possibilitat de formar part d'un consell de classe."),

  dict(id="t09", tipus="test", bloc="Salut i imatge",
    q="Les gorres i els barrets…",
    o=["Es poden dur al pati, però no a l'aula",
       "Es poden dur si fa molt sol",
       "No estan permesos enlloc del recinte de l'escola",
       "Només es permeten a les sortides"],
    c=2,
    norma="No està permesa la utilització de cap tipus de gorres i barrets al recinte de l'escola."),

  dict(id="t10", tipus="test", bloc="Salut i imatge",
    q="Si has de prendre una medicació a l'escola…",
    o=["No se t'administrarà sense recepta mèdica o autorització de la família",
       "Te l'administra l'escola si la portes de casa",
       "Te la pots prendre tu mateix sense avisar",
       "Cal que la porti la família cada dia"],
    c=0,
    norma="Si has de prendre alguna medicació no se t'administrarà sense recepta mèdica o autorització del pare, la mare o representant legal."),

  dict(id="t11", tipus="test", bloc="Material",
    q="Si malmets material de l'escola intencionadament…",
    o=["Se't posa una notificació i prou",
       "T'has d'encarregar de la seva reposició",
       "Ho paga l'assegurança de l'escola",
       "Has de netejar l'aula una setmana"],
    c=1,
    norma="El material de l'escola és responsabilitat de tots: respecta'l i no el malmetis. En cas de malmetre algun material intencionadament, t'hauràs d'encarregar de la seva reposició."),

  dict(id="t12", tipus="test", bloc="Entrades i sortides",
    q="Per sortir de l'escola en horari lectiu cal…",
    o=["Avisar el tutor de paraula",
       "Una autorització escrita",
       "Una trucada de la família a recepció",
       "Que t'acompanyi un company"],
    c=1,
    norma="Per poder sortir de l'escola en horari lectiu cal una autorització escrita."),

  dict(id="t13", tipus="test", bloc="Entrades i sortides",
    q="Els patinets i monopatins…",
    o=["Es poden deixar a l'armariet",
       "Es poden entrar si són plegables",
       "No poden entrar al recinte del Col·legi",
       "S'han de deixar a recepció"],
    c=2,
    norma="Al recinte del Col·legi no poden entrar cap tipus de mitjà de transport (patinets, monopatins, ...)"),

  dict(id="t14", tipus="test", bloc="Mòbils i aparells",
    q="On s'han de deixar els dispositius electrònics i quan?",
    o=["A la motxilla, apagats, durant tota la jornada",
       "A l'armariet, abans d'entrar a la primera classe",
       "A recepció, en arribar",
       "A la taula del professor a cada classe"],
    c=1,
    norma="Els dispositius electrònics (Mòbils, cascos, reproductors ...) s'han de deixar a l'armariet que cada alumne/a té a la seva disposició abans d'entrar a la primera classe."),

  dict(id="t15", tipus="test", bloc="Mòbils i aparells",
    q="Gravar vídeo o fer fotografies dins del recinte de l'escola…",
    o=["Es pot si les persones que hi surten hi estan d'acord",
       "Es pot al pati i a les sortides",
       "Està prohibit",
       "Es pot si no es pengen a les xarxes"],
    c=2,
    norma="Està prohibit gravar en vídeo, àudio o fer fotografies dins del recinte de l'escola. Fotografiar o filmar sense el consentiment exprés de la persona va en contra del dret a la intimitat i constitueix un fet denunciable amb conseqüències legals."),

  dict(id="t16", tipus="test", bloc="Absències i retards",
    q="Si un dia no pots venir a classe, què ha de passar?",
    o=["N'hi ha prou de justificar-ho a l'agenda l'endemà",
       "La família avisa a recepció a primera hora i després es justifica per Alexia",
       "Ho comuniques tu mateix al tutor quan tornis",
       "No cal avisar si és un sol dia"],
    c=1,
    norma="En cas que no puguis assistir a classe la teva mare, pare o representant legal hauran d'avisar personalment o per telèfon a primera hora a la recepció de l'escola, i justificar després l'absència a través de la plataforma Alexia."),

  dict(id="t17", tipus="test", bloc="Faltes de convivència",
    q="Què passa si acumules 3 faltes lleus?",
    o=["Es parla amb la família i no consta enlloc",
       "Reps una notificació d'actitud de caràcter greu, amb mesures sancionadores",
       "S'obre directament un expedient disciplinari",
       "Perds el dret a anar a les sortides tot el curs"],
    c=1,
    norma="En cas d'acumular 3 faltes lleus o bé si comets una falta greu […] rebràs una NOTIFICACIÓ D'ACTITUD DE CARÀCTER GREU, amb les mesures sancionadores corresponents."),

  dict(id="t18", tipus="test", bloc="Faltes de convivència",
    q="Si la conducta negativa persisteix, què es pot obrir?",
    o=["Una reunió amb el tutor",
       "Un expedient disciplinari que pot arribar al Consell Escolar",
       "Una notificació d'actitud lleu",
       "Un canvi de grup classe"],
    c=1,
    norma="En cas que persisteixi la conducta negativa es pot obrir un EXPEDIENT DISCIPLINARI que pot arribar al Consell Escolar (ESO) […] que, en el cas de l'ESO, poden constar en el teu historial acadèmic."),

  # ── SITUACIONS ─────────────────────────────────────────────────
  dict(id="s01", tipus="situacio", bloc="Canvi de classe",
    q="Sona el timbre de canvi de classe. La Júlia es queda al passadís parlant "
      "amb una amiga d'un altre grup fins que arriba el professor següent. El "
      "professor li fa una observació i li recorda la norma.",
    pregunta="El professor té raó?",
    o=["No: al passadís no hi ha cap norma que ho impedeixi",
       "Sí: durant el canvi de classe cal ser dins de la pròpia aula",
       "No: només és falta si arriba tard a la classe següent",
       "Sí, però només si és a l'hora del pati"],
    c=1,
    norma="Durant el canvi de classe has d'estar dins de la teva aula, preparant el material de la classe següent."),

  dict(id="s02", tipus="situacio", bloc="Material",
    q="En Pau s'asseu de cop a la cadira i una pota cedeix i es trenca. Ha estat "
      "un accident: no ho ha fet expressament i ho diu de seguida. El professor "
      "li comunica que haurà de pagar la cadira.",
    pregunta="La resposta del professor s'ajusta a la norma?",
    o=["Sí: qui trenca el material, el paga",
       "No: la norma parla de reposar el material malmès INTENCIONADAMENT",
       "Sí, però només la meitat de l'import",
       "No: el material mai no el paga l'alumne"],
    c=1,
    norma="En cas de malmetre algun material intencionadament, t'hauràs d'encarregar de la seva reposició."),

  dict(id="s03", tipus="situacio", bloc="Mòbils i aparells",
    q="La Berta porta el mòbil a la motxilla, apagat, i no el treu en tot el matí. "
      "A tercera hora, en obrir la motxilla per agafar un llibre, el professor el "
      "veu i l'hi retira fins al final de la jornada.",
    pregunta="Ha incomplert cap norma, la Berta?",
    o=["No: no l'ha fet servir en cap moment",
       "No: només és falta si sona o el treu a classe",
       "Sí: els dispositius s'han de deixar a l'armariet abans de la primera classe",
       "Sí, però la retirada del mòbil no correspon"],
    c=2,
    norma="Els dispositius electrònics […] s'han de deixar a l'armariet […] abans d'entrar a la primera classe. En cas d'usos indeguts, cal retirar el dispositiu a l'alumne i seguir el protocol […] que inclou la custòdia fins al final de la jornada i l'avís a la família."),

  dict(id="s04", tipus="situacio", bloc="Mòbils i aparells",
    q="L'Èric fa una foto de grup al pati. Tots els companys que hi surten li han "
      "dit que sí i ningú no s'hi ha oposat. No la penja enlloc.",
    pregunta="Què diu la norma?",
    o=["No hi ha problema: tenia el consentiment de tothom",
       "No hi ha problema mentre no la pengi a les xarxes",
       "Està prohibit fer fotografies dins del recinte, hi hagi consentiment o no",
       "Només caldria permís del professorat de guàrdia"],
    c=2,
    norma="Està prohibit gravar en vídeo, àudio o fer fotografies dins del recinte de l'escola."),

  dict(id="s05", tipus="situacio", bloc="Mòbils i aparells",
    q="La Nora es queda a dinar. Entre que acaba de menjar i comencen les classes "
      "de la tarda, va a l'armariet i agafa el mòbil una estona.",
    pregunta="Ho pot fer?",
    o=["Sí: al migdia el mòbil es pot agafar",
       "Sí, perquè no és horari de classe",
       "No: els que es queden a dinar tampoc no poden fer servir el mòbil en aquesta estona",
       "Només si truca a la família"],
    c=2,
    norma="Només es podrà agafar el mòbil quan l'alumne/a marxi cap a casa, ja sigui al migdia o a la tarda. Els alumnes que es queden a dinar tampoc poden utilitzar el mòbil en aquest espai de temps."),

  dict(id="s06", tipus="situacio", bloc="Absències i retards",
    q="La Laia arriba tard tres matins seguits. Els tres dies porta la justificació "
      "signada per la família. El tutor li diu que haurà de venir a recuperar les "
      "hores al centre.",
    pregunta="És correcte, això?",
    o=["No: si estan justificats, els retards no es sancionen",
       "Sí: els retards s'han de justificar I a més se sancionen recuperant hores",
       "No: només se sancionen a partir del cinquè retard",
       "Sí, però només si no els justifica"],
    c=1,
    norma="Els retards també s'han de justificar. Perjudiquen la teva formació i es sancionaran havent de venir a recuperar les hores al centre."),

  dict(id="s07", tipus="situacio", bloc="Absències i retards",
    q="En Guillem ha faltat dos dies per malaltia, degudament justificats. Quan "
      "torna, no porta els deures d'aquests dies i diu que no els tenia perquè no "
      "era a classe.",
    pregunta="Qui té la responsabilitat de posar-se al dia?",
    o=["El professorat, que li ha de donar la feina feta",
       "Ell mateix: ha de demanar els apunts i presentar els deures dels dies que ha faltat",
       "Ningú: si l'absència és justificada, la feina no es recupera",
       "El delegat de classe"],
    c=1,
    norma="En cas que no hagis pogut assistir a classe és la teva responsabilitat demanar els apunts i presentar els deures i feines dels dies en què no hi has assistit."),

  dict(id="s08", tipus="situacio", bloc="Esbarjos",
    q="A l'hora del pati comença a ploure fluix. Un grup d'alumnes decideix quedar-se "
      "al pati perquè diuen que amb aquesta pluja no cal entrar.",
    pregunta="Què hauria de passar?",
    o=["Poden quedar-s'hi mentre no plogui fort",
       "Poden quedar-s'hi si es posen sota el porxo",
       "En cas de pluja cal romandre a l'aula i seguir les indicacions del professorat",
       "Poden anar al vestíbul pel seu compte"],
    c=2,
    norma="A l'hora de l'esbarjo has d'estar al pati assignat al teu curs en l'horari establert. En cas de pluja romandreu a l'aula i seguireu les indicacions del professorat."),

  dict(id="s09", tipus="situacio", bloc="Tracte i llenguatge",
    q="Durant un treball en grup, l'Ivan diu a un company un insult que fa "
      "referència al seu país d'origen. Diu que ho ha dit de broma.",
    pregunta="Com s'ha de valorar?",
    o=["No és falta: era una broma entre amics",
       "És una falta lleu, com parlar a classe",
       "Vulnera el tracte respectuós i la prohibició d'al·lusions racistes o xenòfobes: pot ser falta greu",
       "Només seria falta si ho digués a un professor"],
    c=2,
    norma="La teva escola educa en la tolerància, així que queda prohibida qualsevol al·lusió irreverent, racista o xenòfoba. […] No insultis ni ofenguis ningú."),

  dict(id="s10", tipus="situacio", bloc="Agenda",
    q="La Marta ha decorat les pàgines de l'agenda amb dibuixos i hi ha enganxat "
      "fotos dels seus amics. El tutor li diu que n'haurà de comprar una de nova.",
    pregunta="La mesura s'ajusta a la norma?",
    o=["No: l'agenda és seva i pot decorar-la",
       "Sí: no s'hi admeten dibuixos, fotos ni escrits, i en aquest cas es demana comprar-ne una de nova",
       "No: només caldria esborrar-ho",
       "Sí, però només si hi ha escrits ofensius"],
    c=1,
    norma="No s'admetran dibuixos, fotos o escrits de cap mena. En aquest cas es demanarà comprar-ne una de nova."),

  dict(id="s11", tipus="situacio", bloc="Faltes de convivència",
    q="Un alumne ja té dues notificacions d'actitud lleus. Aquesta setmana en rep "
      "una tercera per no portar el material de manera reiterada.",
    pregunta="Què comporta?",
    o=["Res de nou fins a la cinquena",
       "Una notificació d'actitud de caràcter greu amb les mesures sancionadores corresponents",
       "L'obertura immediata d'un expedient disciplinari",
       "La pèrdua del dret d'assistència durant una setmana"],
    c=1,
    norma="En cas d'acumular 3 faltes lleus […] rebràs una NOTIFICACIÓ D'ACTITUD DE CARÀCTER GREU, amb les mesures sancionadores corresponents."),

  dict(id="s12", tipus="situacio", bloc="Medi ambient",
    q="En Roger porta cada dia l'entrepà embolicat amb paper d'alumini i el llença "
       "a la paperera del pati que li queda més a prop, sense mirar de quin tipus és.",
    pregunta="Què hi diu la normativa?",
    o=["Tot correcte: llença les deixalles a la paperera",
       "Només caldria canviar l'embolcall",
       "Cal fer servir les papereres de reciclatge correctament i evitar l'alumini i el plàstic amb embolcalls reutilitzables",
       "Les papereres del pati no es fan servir per als entrepans"],
    c=2,
    norma="Utilitza les papereres de reciclatge correctament […] Evita el paper d'alumini i el plàstic per embolicar els entrepans que dus al col·legi. Fent servir embolcalls reutilitzables, contribuiràs a reduir residus."),

  dict(id="s13", tipus="situacio", bloc="Entrades i sortides",
    q="La família de la Cris li envia un missatge dient que aquesta tarda ha de "
      "sortir una hora abans per anar al metge. La Cris ensenya el missatge al "
      "professor i li demana marxar.",
    pregunta="N'hi ha prou?",
    o=["Sí: el missatge de la família ja és una autorització",
       "No: per sortir en horari lectiu cal una autorització escrita",
       "Sí, si el professor truca a la família",
       "No, però pot marxar si l'acompanya un company"],
    c=1,
    norma="Per poder sortir de l'escola en horari lectiu cal una autorització escrita."),

  dict(id="s14", tipus="situacio", bloc="Sortides del centre",
    q="Hi ha una sortida de curs. En Dani ha tingut un comportament molt irregular "
      "les últimes setmanes i l'equip de professors decideix que no hi participi.",
    pregunta="Poden fer-ho?",
    o=["No: la sortida és un dret de tots els alumnes",
       "Sí: el professorat pot decidir que un alumne no participi en una sortida si ho considera oportú",
       "Només si la família hi està d'acord",
       "Només si ja té un expedient obert"],
    c=1,
    norma="Tingues present que el professorat pot decidir que no participis en alguna sortida o activitat, si ho consideren oportú."),
]


def banc():
    """El banc amb les opcions barallades, un cop i per a tothom.

    Escrivint les preguntes la resposta correcta tendeix a caure sempre al
    mateix lloc (aquí, 19 de 32 a la segona opció), i això és endevinable
    sense saber-se les normes. La permutació surt d'un hash de l'id, així que
    és estable: els enunciats públics i la clau del servidor no es poden
    desincronitzar per molt que es reexecuti el script.
    """
    fora = []
    for p in PREGUNTES:
        h = hashlib.sha256(f"{p['id']}·{VERSIO}".encode()).digest()
        ordre = sorted(range(len(p["o"])), key=lambda i: (h[i], i))
        q = dict(p)
        q["o"] = [p["o"][i] for i in ordre]
        q["c"] = ordre.index(p["c"])
        fora.append(q)
    return fora


def preguntes_publiques():
    """El que veu el navegador: enunciats i opcions, mai la clau."""
    return [{k: p[k] for k in ("id", "tipus", "bloc", "q", "pregunta", "o") if k in p}
            for p in banc()]


def clau_js():
    """La clau i la norma que la justifica. Només per a la Function."""
    clau = {p["id"]: {"c": p["c"], "norma": p["norma"]} for p in banc()}
    return (
        "// GENERAT per scripts/build_normes_prova.py — no editar a mà.\n"
        "//\n"
        "// Les respostes correctes de la prova de normes. Viuen AQUÍ, al servidor,\n"
        "// i no al HTML: la correcció la fa la Function i el navegador només rep\n"
        "// el resultat. Si això arribés al client, la prova no valdria res.\n"
        f"export const VERSIO = {json.dumps(VERSIO)};\n"
        f"export const TOTAL = {len(PREGUNTES)};\n"
        f"export const CLAU = {json.dumps(clau, ensure_ascii=False, indent=2)};\n"
    )


def main():
    # 1) Enunciats públics
    out = REPO / "assets" / "data" / "normes-preguntes.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(
        {"versio": VERSIO, "total": len(PREGUNTES), "grups": GRUPS,
         "preguntes": preguntes_publiques()},
        ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(f"  ✓ {out.relative_to(REPO)}")

    # 2) Clau (servidor)
    out = REPO / "functions" / "api" / "_normes-clau.js"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(clau_js(), encoding="utf-8")
    print(f"  ✓ {out.relative_to(REPO)}")

    # 3) Pàgina
    from build_normes_pagina import render_prova
    out = REPO / "docencia" / "tutoria-2eso" / "normes" / "index.html"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(render_prova(VERSIO, len(PREGUNTES)), encoding="utf-8")
    print(f"  ✓ {out.relative_to(REPO)}")

    tests = sum(1 for p in PREGUNTES if p["tipus"] == "test")
    print(f"\n{len(PREGUNTES)} preguntes · {tests} de test · "
          f"{len(PREGUNTES) - tests} de situació · versió {VERSIO}")


if __name__ == "__main__":
    import sys
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    main()
