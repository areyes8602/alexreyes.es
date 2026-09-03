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
    q="Què diu la norma sobre menjar i beure dins de l'aula?",
    o=["Es pot beure aigua, però no es pot menjar res de res",
       "No es pot menjar ni beure mai, xiclets inclosos",
       "Es pot menjar a la classe just abans d'anar al pati",
       "Es pot menjar si el professor hi dona permís"],
    c=1,
    norma="Dins la classe no pots ni menjar ni beure i això inclou xiclets i llaminadures."),

  dict(id="t02", tipus="test", bloc="Treball a classe",
    q="Sortir de l'aula per anar al lavabo durant la classe…",
    o=["Es pot si aixeques la mà i el professor ho autoritza",
       "Es pot una vegada al matí i una a la tarda",
       "No s'autoritza, tret de casos urgents",
       "Depèn del que decideixi cada professor"],
    c=2,
    norma="Per mantenir l'ordre i l'atenció a les classes no s'autoritzarà, tret de casos urgents, la teva sortida per anar al lavabo, rebre encàrrecs, etc."),

  dict(id="t03", tipus="test", bloc="Canvi de classe",
    q="Durant el canvi de classe, on has de ser?",
    o=["Al passadís, esperant que arribi el professor",
       "Dins de la teva aula, preparant el material",
       "On vulguis del centre mentre no facis soroll",
       "Als armariets, canviant els llibres de l'hora"],
    c=1,
    norma="Durant el canvi de classe has d'estar dins de la teva aula, preparant el material de la classe següent."),

  dict(id="t04", tipus="test", bloc="Canvi de classe",
    q="Si el professorat es retarda, qui ha d'avisar secretaria?",
    o=["Qualsevol alumne que s'ofereixi a anar-hi",
       "El delegat o la delegada de la classe",
       "Ningú: cal esperar dins l'aula",
       "El professor de l'aula del costat"],
    c=1,
    norma="En cas que el professorat es retardi el delegat/da ha d'avisar a secretaria."),

  dict(id="t05", tipus="test", bloc="Canvi de classe",
    q="Les portes d'intercomunicació entre aules les pot fer servir…",
    o=["Un alumne que tingui molta pressa",
       "Els delegats i delegades de classe",
       "Només els professors i professores",
       "Els alumnes durant els canvis de classe"],
    c=2,
    norma="Les portes d'intercomunicació entre aules només les poden fer servir els professors/es."),

  dict(id="t06", tipus="test", bloc="Canvi de classe",
    q="Quan es poden obrir els armariets personals?",
    o=["Cada vegada que necessitis alguna cosa que hi tinguis",
       "Només a primera hora del matí i en marxar",
       "A primera hora, al pati, al migdia, a la tarda i en marxar",
       "Al principi i al final de cada hora de classe"],
    c=2,
    norma="Els armariets personals que teniu a la vostra disposició es poden obrir a primera hora del matí, a l'inici i al final del pati, al migdia, a la tarda abans d'entrar a classe i a l'hora de marxar."),

  dict(id="t07", tipus="test", bloc="Agenda",
    q="Per què a l'agenda no s'admeten dibuixos, fotos ni escrits?",
    o=["Perquè és material de l'escola i s'ha de retornar",
       "Perquè és una comunicació oberta amb la família",
       "Perquè es corregeix i s'hi posa una nota",
       "Perquè la fa servir tot el grup classe"],
    c=1,
    norma="L'agenda cada dia va i ve de casa al col·legi, és una comunicació família-escola per la qual cosa és oberta i no privada, per aquest motiu no s'admetran dibuixos, fotos o escrits de cap mena. En aquest cas es demanarà comprar-ne una de nova."),

  dict(id="t08", tipus="test", bloc="Participació",
    q="Qui queda exclòs de poder formar part del consell de classe?",
    o=["Els alumnes que han repetit algun curs",
       "Els alumnes amb notificacions greus",
       "Els alumnes que arriben tard sovint",
       "Ningú: tothom s'hi pot presentar"],
    c=1,
    norma="Els alumnes amb notificacions greus queden exclosos de la possibilitat de formar part d'un consell de classe."),

  dict(id="t09", tipus="test", bloc="Salut i imatge",
    q="Les gorres i els barrets…",
    o=["Es poden dur al pati, però no dins de l'aula",
       "Es poden dur els dies que faci molt sol",
       "No estan permesos mai, enlloc del recinte",
       "Només es permeten a les sortides del centre"],
    c=2,
    norma="No està permesa la utilització de cap tipus de gorres i barrets al recinte de l'escola."),

  dict(id="t10", tipus="test", bloc="Salut i imatge",
    q="Si has de prendre una medicació a l'escola…",
    o=["No se t'administrarà sense recepta o autorització",
       "L'escola te l'administra si la portes de casa",
       "Te la pots prendre tu mateix sense avisar ningú",
       "Cal que la porti la família cada dia al centre"],
    c=0,
    norma="Si has de prendre alguna medicació no se t'administrarà sense recepta mèdica o autorització del pare, la mare o representant legal."),

  dict(id="t11", tipus="test", bloc="Material",
    q="Si malmets material de l'escola intencionadament…",
    o=["Se't posa una notificació d'actitud i prou",
       "T'has d'encarregar de la seva reposició",
       "Ho paga l'assegurança escolar del centre",
       "Has de netejar l'aula durant una setmana"],
    c=1,
    norma="El material de l'escola és responsabilitat de tots: respecta'l i no el malmetis. En cas de malmetre algun material intencionadament, t'hauràs d'encarregar de la seva reposició."),

  dict(id="t12", tipus="test", bloc="Entrades i sortides",
    q="Per sortir de l'escola en horari lectiu cal…",
    o=["Avisar el tutor de paraula abans de marxar",
       "Portar una autorització escrita",
       "Que la família truqui a recepció aquell dia",
       "Que t'acompanyi un company de classe"],
    c=1,
    norma="Per poder sortir de l'escola en horari lectiu cal una autorització escrita."),

  dict(id="t13", tipus="test", bloc="Entrades i sortides",
    q="Els patinets i monopatins…",
    o=["Es poden deixar dins de l'armariet propi",
       "Es poden entrar si són plegables",
       "Cap mitjà de transport no pot entrar al recinte",
       "S'han de deixar a recepció en arribar"],
    c=2,
    norma="Al recinte del Col·legi no poden entrar cap tipus de mitjà de transport (patinets, monopatins, ...)"),

  dict(id="t14", tipus="test", bloc="Mòbils i aparells",
    q="On s'han de deixar els dispositius electrònics i quan?",
    o=["A la motxilla, apagats, durant tota la jornada",
       "A l'armariet, abans de la primera classe",
       "A recepció, en arribar al centre",
       "A la taula del professor a cada classe"],
    c=1,
    norma="Els dispositius electrònics (Mòbils, cascos, reproductors ...) s'han de deixar a l'armariet que cada alumne/a té a la seva disposició abans d'entrar a la primera classe."),

  dict(id="t15", tipus="test", bloc="Mòbils i aparells",
    q="Gravar vídeo o fer fotografies dins del recinte de l'escola…",
    o=["Es pot si les persones que hi surten hi estan d'acord",
       "Es pot al pati i durant les sortides del centre",
       "Està prohibit sempre dins del recinte",
       "Es pot mentre no es pengin a les xarxes"],
    c=2,
    norma="Està prohibit gravar en vídeo, àudio o fer fotografies dins del recinte de l'escola. Fotografiar o filmar sense el consentiment exprés de la persona va en contra del dret a la intimitat i constitueix un fet denunciable amb conseqüències legals."),

  dict(id="t16", tipus="test", bloc="Absències i retards",
    q="Si un dia no pots venir a classe, què ha de passar?",
    o=["Ho justifiques a l'agenda l'endemà quan tornes a classe",
       "La família avisa a recepció i ho justifica a Alexia",
       "Ho comuniques tu mateix al tutor quan tornes",
       "No s'avisa ningú si només és un dia solt"],
    c=1,
    norma="En cas que no puguis assistir a classe la teva mare, pare o representant legal hauran d'avisar personalment o per telèfon a primera hora a la recepció de l'escola, i justificar després l'absència a través de la plataforma Alexia."),

  dict(id="t17", tipus="test", bloc="Faltes de convivència",
    q="Què passa si acumules 3 faltes lleus?",
    o=["Es parla amb la família i no consta enlloc",
       "Una notificació d'actitud de caràcter greu",
       "S'obre directament un expedient disciplinari",
       "Perds les sortides de la resta del curs"],
    c=1,
    norma="En cas d'acumular 3 faltes lleus o bé si comets una falta greu […] rebràs una NOTIFICACIÓ D'ACTITUD DE CARÀCTER GREU, amb les mesures sancionadores corresponents."),

  dict(id="t18", tipus="test", bloc="Faltes de convivència",
    q="Si la conducta negativa persisteix, què es pot obrir?",
    o=["Una reunió del tutor amb la família i el cap d'estudis",
       "Un expedient disciplinari, que arriba al Consell Escolar",
       "Una notificació d'actitud lleu amb avís a la família",
       "Un canvi de grup classe per a la resta del curs"],
    c=1,
    norma="En cas que persisteixi la conducta negativa es pot obrir un EXPEDIENT DISCIPLINARI que pot arribar al Consell Escolar (ESO) […] que, en el cas de l'ESO, poden constar en el teu historial acadèmic."),

  # ── SITUACIONS ─────────────────────────────────────────────────
  dict(id="s01", tipus="situacio", bloc="Canvi de classe",
    q="Sona el timbre de canvi de classe. La Júlia es queda al passadís parlant "
      "amb una amiga d'un altre grup fins que arriba el professor següent.",
    pregunta="El professor li fa una observació. Té raó?",
    o=["No: al passadís no hi ha cap norma que ho impedeixi",
       "Sí: durant el canvi cal ser dins de la pròpia aula",
       "No: només seria falta si arribés tard a la classe",
       "Sí, però només si el professor ja havia arribat"],
    c=1,
    norma="Durant el canvi de classe has d'estar dins de la teva aula, preparant el material de la classe següent."),

  dict(id="s02", tipus="situacio", bloc="Material",
    q="En Pau s'asseu de cop a la cadira i una pota cedeix i es trenca. Ha estat "
      "un accident: no ho ha fet expressament i ho diu de seguida.",
    pregunta="El professor li diu que haurà de pagar la cadira. S'ajusta a la norma?",
    o=["Sí: qui trenca el material del centre l'ha de reposar",
       "No: la norma parla del material malmès expressament",
       "Sí, però només la meitat de l'import de la cadira",
       "No: el material del centre mai no el paga l'alumne"],
    c=1,
    norma="En cas de malmetre algun material intencionadament, t'hauràs d'encarregar de la seva reposició."),

  dict(id="s03", tipus="situacio", bloc="Mòbils i aparells",
    q="La Berta porta el mòbil a la motxilla, apagat, i no el treu en tot el matí. "
      "A tercera hora, en obrir la motxilla per agafar un llibre, el professor el veu.",
    pregunta="Ha incomplert cap norma, la Berta?",
    o=["No: no l'ha fet servir en cap moment de tot el matí",
       "No: només és falta si sona o el treu a classe",
       "Sí: s'havia de deixar a l'armariet abans de classe",
       "Sí, però retirar-li el mòbil no correspon"],
    c=2,
    norma="Els dispositius electrònics […] s'han de deixar a l'armariet […] abans d'entrar a la primera classe. En cas d'usos indeguts, cal retirar el dispositiu a l'alumne i seguir el protocol […] que inclou la custòdia fins al final de la jornada i l'avís a la família."),

  dict(id="s04", tipus="situacio", bloc="Mòbils i aparells",
    q="L'Èric fa una foto de grup al pati. Tots els companys que hi surten li han "
      "dit que sí i ningú no s'hi ha oposat. No la penja enlloc.",
    pregunta="Què diu la norma?",
    o=["No hi ha problema: tenia el consentiment de tothom",
       "No hi ha problema mentre no la pengi a les xarxes",
       "No es poden fer fotos mai dins del recinte",
       "Només li caldria el permís del professor de guàrdia"],
    c=2,
    norma="Està prohibit gravar en vídeo, àudio o fer fotografies dins del recinte de l'escola."),

  dict(id="s05", tipus="situacio", bloc="Mòbils i aparells",
    q="La Nora es queda a dinar. Entre que acaba de menjar i comencen les classes "
      "de la tarda, va a l'armariet i agafa el mòbil una estona.",
    pregunta="Ho pot fer?",
    o=["Sí: al migdia el mòbil ja es pot agafar",
       "Sí, perquè aquesta estona no és horari lectiu ni de classe",
       "No: qui es queda a dinar no el pot fer servir mai",
       "Només si ha de trucar a la seva família"],
    c=2,
    norma="Només es podrà agafar el mòbil quan l'alumne/a marxi cap a casa, ja sigui al migdia o a la tarda. Els alumnes que es queden a dinar tampoc poden utilitzar el mòbil en aquest espai de temps."),

  dict(id="s06", tipus="situacio", bloc="Absències i retards",
    q="La Laia arriba tard tres matins seguits. Els tres dies porta la justificació "
      "signada per la família.",
    pregunta="El tutor li diu que haurà de recuperar les hores. És correcte?",
    o=["No: si estan justificats, els retards no se sancionen",
       "Sí: els retards es justifiquen i a més se sancionen",
       "No: només se sancionen a partir del cinquè retard",
       "Sí, però només els dies que no porti justificació"],
    c=1,
    norma="Els retards també s'han de justificar. Perjudiquen la teva formació i es sancionaran havent de venir a recuperar les hores al centre."),

  dict(id="s07", tipus="situacio", bloc="Absències i retards",
    q="En Guillem ha faltat dos dies per malaltia, degudament justificats. Quan "
      "torna, no porta els deures i diu que no els tenia perquè no era a classe.",
    pregunta="Qui té la responsabilitat de posar-se al dia?",
    o=["El professorat, que li ha de donar la feina ja feta",
       "Ell mateix: ha de demanar els apunts i fer els deures",
       "Ningú: si l'absència és justificada, no es recupera",
       "El delegat de classe, que li passa el que s'ha fet"],
    c=1,
    norma="En cas que no hagis pogut assistir a classe és la teva responsabilitat demanar els apunts i presentar els deures i feines dels dies en què no hi has assistit."),

  dict(id="s08", tipus="situacio", bloc="Esbarjos",
    q="A l'hora del pati comença a ploure fluix. Un grup d'alumnes decideix quedar-se "
      "al pati perquè diuen que amb aquesta pluja no cal entrar.",
    pregunta="Què hauria de passar?",
    o=["Poden quedar-s'hi mentre la pluja no sigui forta",
       "Poden quedar-s'hi si es posen sota el porxo del pati",
       "Cal anar a l'aula i seguir les indicacions",
       "Poden anar cap al vestíbul pel seu compte"],
    c=2,
    norma="A l'hora de l'esbarjo has d'estar al pati assignat al teu curs en l'horari establert. En cas de pluja romandreu a l'aula i seguireu les indicacions del professorat."),

  dict(id="s09", tipus="situacio", bloc="Tracte i llenguatge",
    q="Durant un treball en grup, l'Ivan diu a un company un insult que fa "
      "referència al seu país d'origen. Diu que ho ha dit de broma.",
    pregunta="Com s'ha de valorar?",
    o=["No és falta: era una broma entre companys",
       "És una falta lleu, com xerrar durant la classe",
       "Vulnera el tracte respectuós: pot ser falta greu",
       "Només seria falta si ho hagués dit a un professor"],
    c=2,
    norma="La teva escola educa en la tolerància, així que queda prohibida qualsevol al·lusió irreverent, racista o xenòfoba. […] No insultis ni ofenguis ningú."),

  dict(id="s10", tipus="situacio", bloc="Agenda",
    q="La Marta ha decorat les pàgines de l'agenda amb dibuixos i hi ha enganxat "
      "fotos dels seus amics.",
    pregunta="El tutor li diu que n'haurà de comprar una de nova. S'ajusta a la norma?",
    o=["No: l'agenda és seva i la pot decorar com li sembli millor",
       "Sí: no s'hi admeten dibuixos ni fotos, i se'n compra una",
       "No: n'hi hauria prou d'esborrar-ho i deixar-la neta",
       "Sí, però només si hi hagués escrits ofensius"],
    c=1,
    norma="No s'admetran dibuixos, fotos o escrits de cap mena. En aquest cas es demanarà comprar-ne una de nova."),

  dict(id="s11", tipus="situacio", bloc="Faltes de convivència",
    q="En Marc rep una notificació d'actitud. Com que la sanció la complirà al "
      "centre, pensa que a casa no se n'assabentaran.",
    pregunta="Té raó?",
    o=["Sí: si la sanció es compleix al centre, queda allà",
       "No: la notificació arriba a la família amb la sanció",
       "Sí, mentre no sigui una notificació de caràcter greu",
       "No, però la família només ho sap a final de trimestre"],
    c=1,
    norma="Si no respectes alguna d'aquestes normes farem arribar a la teva família una NOTIFICACIÓ D'ACTITUD amb la sanció que hauràs de complir."),

  dict(id="s12", tipus="situacio", bloc="Medi ambient",
    q="En Roger porta cada dia l'entrepà embolicat amb paper d'alumini i el llença "
      "a la paperera del pati que li queda més a prop, sense mirar de quin tipus és.",
    pregunta="Què hi diu la normativa?",
    o=["Tot correcte: llença les deixalles a la paperera que troba",
       "Només li caldria canviar el tipus d'embolcall que fa servir",
       "Cal reciclar bé i evitar l'alumini i el plàstic",
       "Les papereres del pati no són per a les restes d'entrepà"],
    c=2,
    norma="Utilitza les papereres de reciclatge correctament […] Evita el paper d'alumini i el plàstic per embolicar els entrepans que dus al col·legi. Fent servir embolcalls reutilitzables, contribuiràs a reduir residus."),

  dict(id="s13", tipus="situacio", bloc="Entrades i sortides",
    q="La família de la Cris li envia un missatge dient que aquesta tarda ha de "
      "sortir una hora abans per anar al metge. La Cris l'ensenya al professor.",
    pregunta="N'hi ha prou?",
    o=["Sí: el missatge de la família ja val com a autorització escrita",
       "No: per sortir en horari lectiu cal autorització escrita",
       "Sí, si a més el professor truca a la família",
       "No, però pot marxar si l'acompanya un company"],
    c=1,
    norma="Per poder sortir de l'escola en horari lectiu cal una autorització escrita."),

  dict(id="s14", tipus="situacio", bloc="Sortides del centre",
    q="Hi ha una sortida de curs. En Dani ha tingut un comportament molt irregular "
      "les últimes setmanes i l'equip de professors decideix que no hi participi.",
    pregunta="Poden fer-ho?",
    o=["No: la sortida és un dret de tots els alumnes del grup",
       "Sí: el professorat pot decidir que no hi participi",
       "Només si la família hi està d'acord per escrit",
       "Només si ja té un expedient disciplinari obert"],
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
