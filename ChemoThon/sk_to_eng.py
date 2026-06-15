"""
Translation utility: common Slovak medical abbreviations → English.
Used by all ChemoThon ENG apps to translate content from individual JSON files.
"""
import re


def sk_to_eng(text: str) -> str:
    """Translate common Slovak medical terms/abbreviations to English."""
    if not text:
        return text

    # --- Drug / brand name corrections ---
    text = text.replace("Dexametazon", "Dexamethasone")
    text = text.replace("Dexametazón", "Dexamethasone")
    text = text.replace("Nolpaza", "Pantoprazole")
    text = text.replace("Pantoprazol ", "Pantoprazole ")
    text = text.replace("Pantoprazol.", "Pantoprazole.")
    text = text.replace("Pantoprazol,", "Pantoprazole,")
    text = text.replace("Hydrocortison", "Hydrocortisone")
    text = text.replace("Dithiaden", "Chlorphenamine")
    text = text.replace("Bisulepin", "Chlorphenamine")
    text = text.replace("Ondasetron", "Ondansetron")
    text = text.replace("pegfilgrastim", "pegfilgrastim")   # same
    text = text.replace("lipegfilgrastim", "lipegfilgrastim")  # same

    # --- Route / form ---
    text = text.replace("i.v.", "iv").replace("i. v.", "iv")
    text = text.replace(" tbl p.o.", " tab p.o.")
    text = text.replace(" tbl.", " tab.")
    text = text.replace(" tbl ", " tab ")
    text = text.replace(" tbl,", " tab,")

    # --- Solution abbreviations (whole-word) ---
    # FR = Fyziologický Roztok = Normal Saline
    text = re.sub(r'\bFR\b', 'NS', text)
    # RR = Ringer's Roztok
    text = re.sub(r'\bRR\b', "Ringer's", text)
    # G 5%  (glucose) — already recognisable, keep as is

    # --- "v Xml" → "in Xml" (Slovak preposition "v" = English "in") ---
    text = re.sub(r'^v\s+(\d)', r'in \1', text)
    text = re.sub(r'([\s,;/])v\s+(\d)', r'\1in \2', text)

    # --- Infusion schedule phrases ---
    text = text.replace("1.infuzia:", "1st infusion:")
    text = text.replace("1. infuzia:", "1st infusion:")
    text = text.replace("1.infúzia:", "1st infusion:")
    text = text.replace("1. infúzia:", "1st infusion:")
    text = text.replace("infuzia", "infusion")
    text = text.replace("infúzia", "infusion")
    text = text.replace("zacat 50ml/h", "start at 50 ml/h")
    text = text.replace("zacat 50 ml/h", "start at 50 ml/h")
    text = text.replace("začat 50ml/h", "start at 50 ml/h")
    text = text.replace("stupnovite zvysovat", "escalate gradually")
    text = text.replace("stupňovito zvyšovať", "escalate gradually")
    text = text.replace("dalsie cykly:", "subsequent cycles:")
    text = text.replace("dalsie cykly", "subsequent cycles")
    text = text.replace("ďalšie cykly:", "subsequent cycles:")
    text = text.replace("ďalšie cykly", "subsequent cycles")
    text = text.replace("ďalšie:", "subsequent:")
    text = text.replace("ďalšie ", "subsequent ")

    # --- Time ---
    text = re.sub(r'(\d+)\s*hodín', r'\1 hours', text)
    text = re.sub(r'(\d+)\s*hod\b', r'\1 h', text)
    text = text.replace("24hod", "24 h")

    # --- Administration site ---
    text = text.replace("centralny kateter", "central catheter")
    text = text.replace("centrálny katéter", "central catheter")

    # --- Scheduling/frequency ---
    text = text.replace("ráno a večer", "morning and evening")
    text = text.replace("každé 3 týždne", "every 3 weeks")
    text = text.replace("každé 4 týždne", "every 4 weeks")
    text = text.replace("každý týždeň", "every week")
    text = text.replace("každých", "every")
    text = text.replace("každé", "every")
    text = text.replace("denne", "daily")
    text = text.replace("do 2 rokov", "for up to 2 years")
    text = text.replace("týždne", "weeks")
    text = text.replace("týždeň", "week")
    text = text.replace("mesiacov", "months")
    text = text.replace("mesiac", "month")
    text = text.replace("rozostupy", "intervals")
    text = re.sub(r'\bcyklov\b', 'cycles', text)

    # --- Day connectors ---
    text = re.sub(r'\bD(\d+)\s+a\s+D(\d+)', r'D\1 and D\2', text)
    text = text.replace("po dotečení posledného dňa", "after the last-day infusion completes")

    # --- Oral dosing instructions ---
    text = text.replace("S jedlom alebo bez.", "With or without food.")
    text = text.replace("S jedlom alebo bez", "with or without food")
    text = text.replace("s jedlom alebo bez.", "with or without food.")
    text = text.replace("s jedlom alebo bez", "with or without food")
    text = text.replace("s jedlom", "with food")
    text = text.replace("po jedle", "after meals")
    text = text.replace("NALAČNO", "ON AN EMPTY STOMACH")
    text = text.replace("nalačno", "on an empty stomach")
    text = text.replace("rozdeliť na", "divide into")
    text = text.replace("rozdelit na", "divide into")
    text = text.replace("rozdelené do", "divided into")
    text = text.replace("rozdelené", "divided")
    text = text.replace("dávky", "doses")
    text = text.replace("dávok", "doses")
    text = text.replace("davky", "doses")
    text = text.replace("davok", "doses")
    text = text.replace("dávku", "dose")
    text = text.replace("dávka", "dose")
    text = text.replace("nasledne", "then")
    text = text.replace("následne", "then")
    text = text.replace("potom", "then")

    # --- Remainder / first ---
    text = text.replace("zvyšok", "remainder")
    text = text.replace("zvysok", "remainder")
    text = text.replace("Zvyšok", "Remainder")
    text = text.replace("Zvysok", "Remainder")
    text = text.replace("prvých", "first")
    text = text.replace("prvych", "first")
    text = text.replace("prvé", "first")

    # --- Connector words ---
    text = text.replace(" alebo ", " or ")
    text = text.replace(" a ", " and ")
    text = text.replace("pauza", "break")

    # --- Drug names in notes ---
    text = text.replace("Manitol", "Mannitol")
    text = text.replace("manitol", "mannitol")
    text = text.replace("Dakarbazín", "Dacarbazine")
    text = text.replace("dakarbazín", "dacarbazine")
    text = text.replace("Dakarbazin", "Dacarbazine")
    text = text.replace("dakarbazin", "dacarbazine")

    # --- Route / administration ---
    text = text.replace("cca", "approx.")
    text = text.replace("pomalá subkutánna injekcia", "slow subcutaneous injection")
    text = text.replace("bez filtrácie", "without filter")
    text = text.replace("Bez filtrácie", "Without filter")
    text = text.replace("chrániť pred svetlom", "protect from light")
    text = text.replace("Chrániť pred svetlom", "Protect from light")
    text = text.replace("minut", "min")

    # --- Clinical notes ---
    text = text.replace("Bez premedikácie.", "No premedication.")
    text = text.replace("Bez premedikácie", "No premedication")
    text = text.replace("POVINNÁ B12/FOLÁT suplementácia", "MANDATORY B12/FOLATE supplementation")
    text = text.replace("POVINNÁ", "MANDATORY")
    text = text.replace("suplementácia", "supplementation")
    text = text.replace("Redukcia pri", "Dose reduction at")
    text = text.replace("Premedikácia", "Premedication")
    text = text.replace("premedikácia", "premedication")
    text = text.replace("Udržiavacia liečba:", "Maintenance therapy:")
    text = text.replace("Udržiavacia liečba", "Maintenance therapy")
    text = text.replace("Indikácia:", "Indication:")
    text = text.replace("Indikácia", "Indication")
    text = text.replace("neskvamózny NSCLC", "non-squamous NSCLC")
    text = text.replace("skvamózny NSCLC", "squamous NSCLC")
    text = text.replace("Vincristín VYNECHANÝ", "Vincristine OMITTED")
    text = text.replace("VYNECHANÝ", "OMITTED")
    text = text.replace("Alternatíva:", "Alternative:")
    text = text.replace("Alternatíva", "Alternative")
    text = text.replace("alternatíva", "alternative")
    text = text.replace("línia", "line")
    text = text.replace("linia", "line")
    text = text.replace("viď", "see")
    text = text.replace("pred.", "prior.")
    text = text.replace("pred chemo", "before chemo")
    text = text.replace("pred infúziou", "before infusion")
    text = text.replace("pred podaním", "before administration")
    text = text.replace("sc", "sc")  # subcut — same

    # --- Monitoring / warnings ---
    text = text.replace("Monitorovať", "Monitor")
    text = text.replace("Monitorovanie:", "Monitoring:")
    text = text.replace("Monitorovanie", "Monitoring")
    text = text.replace("krvný tlak", "blood pressure")
    text = text.replace("Pozor:", "Warning:")
    text = text.replace("POZOR:", "WARNING:")
    text = text.replace("Pozor", "Warning")
    text = text.replace("POZOR", "WARNING")
    text = text.replace("súbežne s chemoterapiou", "concurrent with chemotherapy")
    text = text.replace("súbežnej rádioterapii", "concurrent radiotherapy")
    text = text.replace("konkomitantná", "concomitant")
    text = text.replace("konkomitantnej", "concomitant")

    # --- Prophylaxis / hydration ---
    text = text.replace("PROFYLAXIA", "PROPHYLAXIS")
    text = text.replace("profylaxia", "prophylaxis")
    text = text.replace("profylakticky", "prophylactically")
    text = text.replace("Hydratácia", "Hydration")
    text = text.replace("hydratácia", "hydration")
    text = text.replace("stomatitídy", "stomatitis")
    text = text.replace("stomatitída", "stomatitis")

    # --- počas (during) — after other replacements to avoid conflicts ---
    text = text.replace("počas", "during")

    # --- Time/day expressions ---
    text = text.replace("kontinuálne", "continuously")
    text = re.sub(r'\b(\d+)\s*dní\b', r'\1 days', text)
    text = re.sub(r'\bdeň\b', 'day', text)
    text = re.sub(r'\bD(\d+)\b', r'D\1', text)   # no-op — keep Dx notation
    text = text.replace("aspoň", "at least")
    text = text.replace("Vždy", "Always")
    text = text.replace("vždy", "always")

    # --- Post-infusion / pre-drug ---
    text = text.replace("po dotečení", "after completion of")
    text = text.replace("po infúzii", "after infusion")
    text = text.replace("po infuzii", "after infusion")

    return text
