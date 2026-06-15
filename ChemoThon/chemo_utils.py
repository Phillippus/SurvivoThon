import streamlit as st
import json


def bsa(weight, height):
    return round((weight**0.425) * (height**0.725) * 0.007184, 2)


def load_json(filename):
    try:
        with open(f'data/{filename}', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        st.error(f"Súbor nenájdený: {filename}. Skontrolujte adresár 'data'.")
        return None
    except json.JSONDecodeError:
        st.error(f"Chyba pri dekódovaní JSON: {filename}")
        return None


def Chemo(rbodysurf, chemoType, weight=None):
    """Jednoduché chemoterapie – BSA, flat dose aj mg/kg."""
    chemoJson = load_json(chemoType)
    if not chemoJson:
        return

    def calc_dose(item):
        metric = item.get('DosageMetric', 'mg/m2')
        if 'flat' in metric.lower():
            return item['Dosage']
        elif 'mg/kg' in metric.lower() and weight is not None:
            return round(item['Dosage'] * weight, 2)
        else:
            return round(item['Dosage'] * rbodysurf, 2)

    st.write("Rozpis chemoterapie:")
    for i in chemoJson["Chemo"]:
        metric = i.get('DosageMetric', 'mg/m2')
        dose = calc_dose(i)
        st.write(f"{i['Name']}  {round(i['Dosage'], 2)} {metric}......... {dose} mg D{i['Day']}")

    st.write(f"NC {chemoJson['NC']} . deň")

    Day1 = chemoJson["Day1"]["Instructions"]
    C1 = chemoJson["Chemo"]

    st.write("D1 - premedikácia:")
    st.write(chemoJson["Day1"]["Premed"]["Note"])

    st.write("D1 - chemoterapia:")
    for x in range(len(chemoJson["Chemo"])):
        dose = calc_dose(C1[x])
        st.write(f"{Day1[x]['Name']} {dose} mg {Day1[x]['Inst']}")


def ChemoCBDCA(rbodysurf, chemoType):
    """Chemoterapia s karboplatinou (Calvertov vzorec)."""
    chemoJson = load_json(chemoType)
    if not chemoJson:
        return

    CrCl = st.number_input("Zadajte hodnotu clearance v ml/min", min_value=1, max_value=250, value=None, step=1)
    AUC = st.number_input("Zadajte hodnotu AUC 2-6", min_value=2, max_value=6, value=None, step=1)

    if CrCl is not None and AUC is not None:
        cbdca_dose = (CrCl + 25) * AUC
        st.write(f"CBDCA AUC {AUC}............ {cbdca_dose} mg  D1")
        for i in chemoJson["Chemo"]:
            metric = i.get('DosageMetric', 'mg/m2')
            dose = i['Dosage'] if 'flat' in metric.lower() else round(i['Dosage'] * rbodysurf, 2)
            st.write(f"{i['Name']} {i['Dosage']} {metric} ..... {dose} mg D{i['Day']}")

        st.write(f"NC {chemoJson['NC']} . deň")
        st.write("D1")
        st.write(chemoJson["Day1"]["Premed"]["Note"])
        st.write(f"CBDCA {cbdca_dose} mg v 500ml FR iv")
        for x in range(len(chemoJson["Chemo"])):
            metric = chemoJson['Chemo'][x].get('DosageMetric', 'mg/m2')
            dose = (chemoJson['Chemo'][x]['Dosage'] if 'flat' in metric.lower()
                    else round(chemoJson['Chemo'][x]['Dosage'] * rbodysurf, 2))
            st.write(f"{chemoJson['Day1']['Instructions'][x]['Name']} {dose} mg "
                     f"{chemoJson['Day1']['Instructions'][x]['Inst']}")


def split_cisplatin(total_dose, start_n=2):
    """Rozdeľuje cisplatinu na 50 mg fľaše + Manitol. Vracia nasledujúce poradové číslo."""
    n = start_n
    remaining = round(total_dose, 2)
    while remaining >= 50:
        st.write(f"{n}. Cisplatina 50mg v 500ml RR iv")
        remaining = round(remaining - 50, 2)
        n += 1
    if remaining > 0.01:
        st.write(f"{n}. Cisplatina {remaining} mg v 500ml RR iv")
        n += 1
    st.write(f"{n}. Manitol 10% 250ml iv")
    return n + 1


def ChemoDDP(rbodysurf, chemoType, ddp_dose=80):
    """Chemoterapia s cisplatinou. ddp_dose: dávka cisplatiny v mg/m2 (default 80)."""
    chemoJson = load_json(chemoType)
    if not chemoJson:
        return

    total = round(ddp_dose * rbodysurf, 2)
    st.write(f"DDP {ddp_dose}mg/m2 ................ {total} mg  D1")
    for i in chemoJson["Chemo"]:
        st.write(f"{i['Name']}  {i['Dosage']} {i['DosageMetric']} ..... "
                 f"{round(i['Dosage'] * rbodysurf, 2)} mg D{i['Day']}")

    st.write(f"NC {chemoJson['NC']} . deň")
    st.write("D1")
    st.write(f"1. {chemoJson['Day1']['Premed']['Note']}")

    next_n = split_cisplatin(total, start_n=2)

    Day1 = chemoJson["Day1"]["Instructions"]
    C1 = chemoJson["Chemo"]
    for x in range(len(chemoJson["Chemo"])):
        st.write(f"{next_n}. {Day1[x]['Name']} {round(C1[x]['Dosage'] * rbodysurf, 2)} mg {Day1[x]['Inst']}")
        next_n += 1


def Chemo5FU(rbodysurf, chemoType):
    """Chemoterapie s kontinuálnym 5-fluorouracilom (FOLFOX, FOLFIRI, FOLFIRINOX, FLOT, mtc5FU)."""
    chemoJson = load_json(chemoType)
    if not chemoJson:
        return

    st.write("Rozpis chemoterapie:")
    for i in chemoJson["Chemo"]:
        st.write(f"{i['Name']}  {round(i['Dosage'], 2)} {i['DosageMetric']}......... "
                 f"{round(i['Dosage'] * rbodysurf, 2)} mg D{i['Day']}")

    if chemoType == "FLOT.json":
        dos5FU, dos15FU, day5FU, day15FU = 2600, 2600, "24 hodín", "24 hodín"
    elif chemoType == "mtc5FU.json":
        dos5FU, dos15FU, day5FU, day15FU = 1000, 1000, "D1-4", "24 hodín"
    else:
        dos5FU, dos15FU, day5FU, day15FU = 2400, 1200, "48 hodín", "24 hodín"

    st.write(f"5-fluoruracil {dos5FU} mg/m2...... {rbodysurf * dos5FU} mg/ {day5FU}")
    st.write(f"NC {chemoJson['NC']} . deň")

    Day1 = chemoJson["Day1"]["Instructions"]
    C1 = chemoJson["Chemo"]

    st.write("D1 - premedikácia:")
    st.write(chemoJson["Day1"]["Premed"]["Note"])

    st.write("D1 - chemoterapia:")
    for x in range(len(chemoJson["Chemo"])):
        st.write(f"{Day1[x]['Name']} {round(C1[x]['Dosage'] * rbodysurf, 2)} mg {Day1[x]['Inst']}")

    st.write(f"5-fluoruracil {rbodysurf * dos15FU} mg/kivi {day15FU}")


def ChemoMass(weight, chemoType):
    """Chemoterapia/biologika dávkovaná podľa hmotnosti (mg/kg)."""
    chemoJson = load_json(chemoType)
    if not chemoJson:
        return

    for chemo in chemoJson["Chemo"]:
        dosage = round(chemo["Dosage"] * weight, 2)
        st.write(f"{chemo['Name']} {chemo['Dosage']} {chemo['DosageMetric']} ......... {dosage} mg D{chemo['Day']}")

    st.write(f"NC {chemoJson['NC']} . deň")
    st.write("D1")
    st.write(chemoJson["Day1"]["Premed"]["Note"])
    for instruction in chemoJson["Day1"]["Instructions"]:
        drug_name = instruction['Name']
        dosage_per_kg = next((item['Dosage'] for item in chemoJson['Chemo'] if item['Name'] == drug_name), None)
        if dosage_per_kg:
            st.write(f"{drug_name} {round(dosage_per_kg * weight, 2)} mg {instruction['Inst']}")
