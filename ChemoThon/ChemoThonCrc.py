import streamlit as st
import json

def load_json(filename):
    """ Load JSON data from a specified file with error handling. """
    try:
        with open(filename, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        st.error(f"File not found: {filename}. Make sure it is in the correct directory.")
        return None
    except json.JSONDecodeError:
        st.error("Error decoding JSON. Check the file format.")
        return None

def Chemo(rbodysurf, chemoType, weight=None):
    """ Function to handle simple chemotherapies – BSA, flat dose aj mg/kg. """
    chemo_json = load_json('data/' + chemoType)
    if chemo_json:
        def calc_dose(item):
            metric = item.get('DosageMetric', 'mg/m2')
            if 'flat' in metric.lower():
                return item['Dosage']
            elif 'mg/kg' in metric.lower() and weight is not None:
                return round(item['Dosage'] * weight, 2)
            else:
                return round(item['Dosage'] * rbodysurf, 2)

        st.write(f"### Protokol: {chemoType.replace('.json', '')}")
        for chemo in chemo_json["Chemo"]:
            dose = calc_dose(chemo)
            st.write(f"{chemo['Name']} {chemo['Dosage']} {chemo['DosageMetric']} ......... {dose} mg D{chemo['Day']}")

        st.write(f"NC {chemo_json['NC']} . deň")
        st.write("D1")
        st.write(chemo_json["Day1"]["Premed"]["Note"])
        chemo_list = chemo_json["Chemo"]
        for instruction in chemo_json["Day1"]["Instructions"]:
            drug_name = instruction['Name']
            item = next((d for d in chemo_list if d['Name'] == drug_name), None)
            if item:
                dose = calc_dose(item)
                st.write(f"{drug_name} {dose} mg {instruction['Inst']}")

def ChemoMass(weight, chemoType):
    """ Function to handle chemotherapy/biologics based on weight. """
    chemo_json = load_json('data/' + chemoType)  # Ensure the 'data/' prefix is here
    if chemo_json:
        st.write(f"### Protokol: {chemoType.replace('.json', '')}")
        for chemo in chemo_json["Chemo"]:
            dosage = round(chemo["Dosage"] * weight)
            st.write(f"{chemo['Name']} {chemo['Dosage']} {chemo['DosageMetric']} ......... {dosage} mg D{chemo['Day']}")
        
        st.write(f"NC {chemo_json['NC']} . deň")
        st.write("D1")
        st.write(chemo_json["Day1"]["Premed"]["Note"])
        for instruction in chemo_json["Day1"]["Instructions"]:
            drug_name = instruction['Name']
            dosage = next((item['Dosage'] for item in chemo_json['Chemo'] if item['Name'] == drug_name), None)
            if dosage:
                adjusted_dosage = round(dosage * weight)
                st.write(f"{drug_name} {adjusted_dosage} mg {instruction['Inst']}")
    else:
        st.error("Failed to load chemotherapy data.")



def Chemo5FU(rbodysurf, chemoType):
    """ Function to handle chemotherapies with continuous 5FU. """
    chemo_json = load_json('data/' + chemoType)
    if not chemo_json:
        st.error("Failed to load chemotherapy data.")
        return

    st.write(f"### Protokol: {chemoType.replace('.json', '')}")
    
    # Prepare a dictionary for easy dosage retrieval
    dosage_dict = {chemo['Name']: round(chemo['Dosage'] * rbodysurf) for chemo in chemo_json["Chemo"]}
    
    for chemo_name, dosage in dosage_dict.items():
        chemo = next((item for item in chemo_json['Chemo'] if item['Name'] == chemo_name), None)
        if chemo:
            st.write(f"{chemo_name} {chemo['Dosage']} {chemo['DosageMetric']} ......... {dosage} mg D{chemo['Day']}")

    if chemoType == "FLOT.json":
        dos5FU = 2600
    elif chemoType == "mtc5FU.json":
        dos5FU = 1000
    else:
        dos5FU = 2400
    
    dos15FU = dos5FU if chemoType == "FLOT.json" else dos5FU / 2
    day5FU = "24 hodín" if chemoType in ["FLOT.json", "mtc5FU.json"] else "48 hodín"
    day15FU = "24 hodín"

    st.write(f"5-fluorouracil {dos5FU} mg/m2 ...... {round(rbodysurf * dos5FU)} mg počas {day5FU}")
    st.write(f"NC {chemo_json['NC']} . deň")
    st.write("D1:")
    st.write(chemo_json["Day1"]["Premed"]["Note"])

    for instruction in chemo_json["Day1"]["Instructions"]:
        drug_name = instruction['Name']
        dosage = dosage_dict.get(drug_name, "dosage not specified")
        if dosage != "dosage not specified":
            st.write(f"{drug_name} {dosage} mg {instruction['Inst']}")
        else:
            st.write(f"{drug_name} dosage not specified {instruction['Inst']}")

    st.write(f" 5-fluorouracil v kontinuálnej pumpe: {round(rbodysurf * dos15FU)} mg počas {day15FU}")




def calculate_bsa(weight, height):
    return (weight ** 0.425) * (height ** 0.725) * 0.007184


def main():
    st.title("ChemoThon - ColorectalSK v. 2.2")
    st.write(" ")
    st.write("         Vitajte v programe ChemoThon!")
    st.write("""Program rozpisuje najbežnejšie chemoterapie podľa povrchu alebo hmotnosti. 
    Najskôr si vypočítajte BSA a potom sa Vám sprístupní tlačidlo pre výpočet chemoterapie.
    Dávky je nutné upraviť podľa aktuálne dostupných balení liečiv.
    Autor nezodpovedá za prípadné škody spôsobené jeho použitím!
    Pripomienky a požiadavky na úpravu posielajte na filip.kohutek@fntn.sk""")
    weight = st.number_input("Zadajte váhu (kg):", min_value=1, max_value=200, value=70, step=1, format="%d")
    height = st.number_input("Zadajte výšku (cm):", min_value=1, max_value=250, value=170, step=1, format="%d")

    if st.button("Vypočítajte BSA"):
        rbodysurf = calculate_bsa(weight, height)
        st.session_state['rbodysurf'] = rbodysurf
        st.write(f"Vypočítaná plocha povrchu tela (BSA): {rbodysurf:.2f} m²")
    elif 'rbodysurf' in st.session_state:
        st.write(f"Vypočítaná plocha povrchu tela (BSA): {st.session_state['rbodysurf']:.2f} m²")

    chemo_options = {
        "FOLFOX": "FOLFOX.json",
        "FOLFIRI": "FOLFIRI.json",
        "CapOX": "Capox.json",
        "CapIri": "Capiri.json",
        "Capecitabine": "capecitabine.json",
        "Bevacizumab (3 weeks)": "bevacizumab3w.json",
        "Bevacizumab (2 weeks)": "bevacizumab2w.json",
        "Cetuximab": "Cetuximab",  # Special handling required
        "Panitumumab": "panitumumab.json",
        "Trifluridine/Tipiracil": "tritipi.json",
        "Trifluridine/Tipiracil + Bevacizumab (SUNLIGHT)": "tritipi_bev.json",
        "Irinotecan": "irinotecan.json",
        "FOLFIRINOX": "FOLFIRINOX.json",
        "MiXe": "MiXe.json",
        # --- Nové (2026-06) ---
        "Encorafenib + Cetuximab (BRAF V600E, BEACON CRC)": "encorafenib_cetuximab.json",
        "Pembrolizumab (MSI-H/dMMR, KEYNOTE-177)": "pembrolizumab_msiH.json",
        "Fruquitinib 5 mg/deň (FRESCO-2, ≥3. línia mCRC)": "fruquitinib.json",
    }

    selected_chemo = None
    if 'rbodysurf' in st.session_state:
        selected_chemo = st.selectbox("Vyberte režim chemoterapie:", list(chemo_options.keys()))

        if selected_chemo == "Cetuximab":
            ctx = st.radio("Je to prvá dávka cetuximabu?", ('Áno', 'Nie'), key='cetuximab_admin')
        elif selected_chemo == "Encorafenib + Cetuximab (BRAF V600E, BEACON CRC)":
            encora_ctx = st.radio("Schéma cetuximabu:", ["Weekly (1. podanie)", "Weekly (ďalšie podania)", "Biweekly (500 mg/m2 q2w)"], key='encora_admin')

    def execute_chemotherapy(option, cetuximab_first_admin=None, encora_admin=None):
        rbodysurf = st.session_state['rbodysurf']
        if option in ["FOLFOX", "FOLFIRI", "FOLFIRINOX"]:
            Chemo5FU(rbodysurf, chemo_options[option])
        elif option == "Cetuximab":
            cetuximab_file = "1cetuximab.json" if cetuximab_first_admin == 'Áno' else "elsecetuximab.json"
            Chemo(rbodysurf, cetuximab_file)
        elif option == "Encorafenib + Cetuximab (BRAF V600E, BEACON CRC)":
            encora_dose_ctx = encora_admin or "Weekly (1. podanie)"
            ctx_dose = round(400 * rbodysurf, 2) if "1. podanie" in encora_dose_ctx else (round(250 * rbodysurf, 2) if "Weekly" in encora_dose_ctx else round(500 * rbodysurf, 2))
            ctx_label = "400 mg/m2 (1. dávka)" if "1. podanie" in encora_dose_ctx else ("250 mg/m2 weekly" if "Weekly" in encora_dose_ctx else "500 mg/m2 biweekly")
            ctx_nc = "7" if "Weekly" in encora_dose_ctx else "14"
            import json as _j
            enc = _j.load(open("data/encorafenib_cetuximab.json", encoding="utf-8"))
            st.write(f"### Encorafenib + Cetuximab (BEACON CRC) — {encora_dose_ctx}")
            st.write(f"encorafenib 300 mg flat dose ......... 300 mg D1-28 (denne)")
            st.write(f"cetuximab {ctx_label} ......... {ctx_dose} mg D1")
            st.write(f"NC {ctx_nc} . deň")
            st.write("D1 - premedikácia:")
            st.write(enc["Day1"]["Premed"]["Note"])
            st.write("D1 - chemoterapia:")
            st.write(f"encorafenib 300 mg p.o. 1× denne kontinuálne")
            st.write(f"cetuximab {ctx_dose} mg – prvých 100 mg v 500ml FR iv/60 min, zvyšok v 500ml FR iv/90 min")
        elif option == "Fruquitinib 5 mg/deň (FRESCO-2, ≥3. línia mCRC)":
            import json as _j
            fr = _j.load(open("data/fruquitinib.json", encoding="utf-8"))
            st.write("### Fruquitinib (FRESCO-2)")
            st.write("fruquitinib 5 mg flat dose D1-21 (pauza D22-28, NC=28)")
            st.write(fr["Day1"]["Premed"]["Note"])
            for inst in fr["Day1"]["Instructions"]:
                st.write(f"{inst['Name']} {inst['Inst']}")
        elif option == "Trifluridine/Tipiracil + Bevacizumab (SUNLIGHT)":
            import json as _j
            sl = _j.load(open("data/tritipi_bev.json", encoding="utf-8"))
            ttd_dose = round(70 * rbodysurf, 2)
            beva_dose = round(5 * weight, 2)
            st.write("### SUNLIGHT — Trifluridín/Tipiracil + Bevacizumab")
            st.write(f"trifluridín/tipiracil 70 mg/m2/deň ......... {ttd_dose} mg D1-5, D8-12")
            st.write(f"bevacizumab 5 mg/kg q2w ......... {beva_dose} mg D1, D15")
            st.write("NC 28. deň")
            st.write("D1 - premedikácia:")
            st.write(sl["Day1"]["Premed"]["Note"])
            st.write("D1 - chemoterapia:")
            st.write(f"trifluridín/tipiracil {ttd_dose} mg {sl['Day1']['Instructions'][0]['Inst']}")
            st.write(f"bevacizumab {beva_dose} mg {sl['Day1']['Instructions'][1]['Inst']}")
        elif "Bevacizumab" in option:
            ChemoMass(weight, chemo_options[option])
        else:
            Chemo(rbodysurf, chemo_options[option], weight=weight)

    if selected_chemo and st.button("Zobraziť protokol chemoterapie"):
        if selected_chemo == "Cetuximab":
            execute_chemotherapy(selected_chemo, cetuximab_first_admin=ctx)
        elif selected_chemo == "Encorafenib + Cetuximab (BRAF V600E, BEACON CRC)":
            execute_chemotherapy(selected_chemo, encora_admin=encora_ctx)
        else:
            execute_chemotherapy(selected_chemo)

if __name__ == "__main__":
    main()



# ===== Zdroje / Sources (pridané 2026-06, aditívne) =====
with st.expander("📚 Zdroje k režimom / Sources"):
    st.markdown("""**Kľúčové referencie – kolorektálny karcinóm**

Guidelines: [ESMO](https://www.esmo.org/guidelines/esmo-clinical-practice-guidelines-gastrointestinal-cancers) · [NCCN](https://www.nccn.org/guidelines/category_1). Vždy overte podľa aktuálnej verzie guidelines a dostupných balení liečiv. Stav: jún 2026.

- **FOLFOX** — de Gramont et al., J Clin Oncol 2000; adjuvant MOSAIC – André et al., NEJM 2004.
- **FOLFIRI** — Douillard et al., Lancet 2000.
- **CapOX (XELOX)** — NO16968 – Schmoll et al., J Clin Oncol 2011.
- **CapIRI** — Fuchs et al., J Clin Oncol 2007 (BICC-C).
- **Kapecitabín** — X-ACT – Twelves et al., NEJM 2005.
- **FOLFIRINOX** — Použitie pri agresívnom mCRC; analogicky Conroy et al., NEJM 2011.
- **Bevacizumab** — Hurwitz et al., NEJM 2004.
- **Cetuximab (RAS wt)** — CRYSTAL – Van Cutsem et al., NEJM 2009.
- **Panitumumab (RAS wt)** — PRIME – Douillard et al., J Clin Oncol 2010.
- **Trifluridín/tipiracil (TAS-102)** — RECOURSE – Mayer et al., NEJM 2015; +bevacizumab SUNLIGHT – Prager et al., NEJM 2023.
- **Irinotekan** — Monoterapia 2. línia – Cunningham et al., Lancet 1998.
- **MiXe (mitomycín/kapecitabín)** — Inštitucionálny záchranný režim; ESMO mCRC guideline.

**Aktuálne štandardy na zváženie (zatiaľ mimo nástroja):**
- **Encorafenib + cetuximab pri BRAF V600E – BEACON CRC (Kopetz, NEJM 2019) → teraz v nástroji.**
- **Pembrolizumab pri MSI-H/dMMR – KEYNOTE-177 (André, NEJM 2020) → teraz v nástroji.**
- **TAS-102 + bevacizumab – SUNLIGHT (Prager, NEJM 2023) → teraz v nástroji.** Fruquintinib – FRESCO-2, Lancet 2023.""")
