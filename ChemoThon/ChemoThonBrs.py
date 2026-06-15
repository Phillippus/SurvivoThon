import streamlit as st
import json

def load_json(filename):
    """Loads JSON data from a specified file with error handling."""
    try:
        with open(f'data/{filename}', 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        st.error(f"Súbor nenájdený: {filename}. Uistite sa, že je v adresári 'data'.")
        return None
    except json.JSONDecodeError:
        st.error("Chyba pri dekódovaní JSON. Skontrolujte formát súboru.")
        return None

def display_chemotherapy_details(rbodysurf, chemoType, weight):
    """Displays detailed information about the chemotherapy regimen using body surface area or weight."""
    chemoJson = load_json(chemoType)
    if chemoJson:
        st.write(f"### Protokol {chemoType.replace('.json', '')}")
        day1_dose = ""
        for chemo in chemoJson["Chemo"]:
            # Fixed dose for X7/7, trastuzumabsc, and pertuzumab combo fixed-dose
            if chemoType in ["capecitabineX77.json", "trastuzumabsc.json", "firstpertuzumab.json", "elsepertuzumab.json",
                              "olaparib.json", "abemaciclib.json", "palbociclib.json", "ribociclib.json", "capivasertib.json"]:
                st.write(f"{chemo['Name']} {chemo['Dosage']} mg D {chemo['Day']}")
                day1_dose = f"{chemo['Name']} {chemo['Dosage']} mg"
            elif chemoType in ["TDM1.json", "TDx.json", "Sacgov.json", "firsttrastuzumabiv.json", "elsetrastuzumabiv.json"]:
                dosage = round(chemo["Dosage"] * weight, 2)
                st.write(f"{chemo['Name']} {chemo['Dosage']} {chemo['DosageMetric']} ......... {dosage} mg D {chemo['Day']}")
                day1_dose = f"{chemo['Name']} {dosage} mg"
            elif chemoType in ["firsttrastupertu.json", "elsetrastupertu.json"]:
                dosage = chemo["Dosage"]
                st.write(f"{chemo['Name']} {dosage} mg D {chemo['Day']}")
                day1_dose = f"{chemo['Name']} {dosage} mg"
            else:
                metric = chemo.get("DosageMetric", "mg/m2")
                if "flat" in metric.lower():
                    st.write(f"{chemo['Name']} {chemo['Dosage']} {metric} D {chemo['Day']}")
                    day1_dose = f"{chemo['Name']} {chemo['Dosage']} mg"
                elif "mg/kg" in metric:
                    dosage = round(chemo["Dosage"] * weight, 2)
                    st.write(f"{chemo['Name']} {chemo['Dosage']} {metric} ......... {dosage} mg D {chemo['Day']}")
                    day1_dose = f"{chemo['Name']} {dosage} mg"
                else:
                    dosage = round(chemo["Dosage"] * rbodysurf, 2)
                    st.write(f"{chemo['Name']} {round(chemo['Dosage'], 2)} {metric} ......... {dosage} mg D {chemo['Day']}")
                    day1_dose = f"{chemo['Name']} {dosage} mg"

        st.write(f"NC {chemoJson['NC']} . deň")
        st.write("D1")
        st.write(chemoJson["Day1"]["Premed"]["Note"])

        for instruction in chemoJson["Day1"]["Instructions"]:
            if instruction["Name"]:
                chemo_entry = next((item for item in chemoJson["Chemo"] if item["Name"] == instruction["Name"]), None)
                if chemo_entry:
                    if chemoType in ["TDM1.json", "TDx.json", "Sacgov.json", "firsttrastuzumabiv.json", "elsetrastuzumabiv.json"]:
                        dosage = round(chemo_entry["Dosage"] * weight, 2)
                        st.write(f"{instruction['Name']} {dosage} mg {instruction['Inst']}")
                    elif chemoType in ["firsttrastupertu.json", "elsetrastupertu.json"]:
                        st.write(f"{instruction['Name']} {instruction['Inst']}")
                    elif chemoType in ["capecitabineX77.json", "trastuzumabsc.json", "firstpertuzumab.json", "elsepertuzumab.json",
                                        "olaparib.json", "abemaciclib.json", "palbociclib.json", "ribociclib.json", "capivasertib.json"]:
                        st.write(f"{instruction['Name']} {instruction['Inst']}")
                    else:
                        metric = chemo_entry.get("DosageMetric", "mg/m2")
                        if "flat" in metric.lower():
                            st.write(f"{instruction['Name']} {chemo_entry['Dosage']} mg {instruction['Inst']}")
                        elif "mg/kg" in metric:
                            dosage = round(chemo_entry["Dosage"] * weight, 2)
                            st.write(f"{instruction['Name']} {dosage} mg {instruction['Inst']}")
                        else:
                            dosage = round(chemo_entry["Dosage"] * rbodysurf, 2)
                            st.write(f"{instruction['Name']} {dosage} mg {instruction['Inst']}")
            else:
                st.write(instruction["Inst"])

def calculate_bsa(weight, height):
    """Calculates body surface area using the DuBois formula."""
    bodysurf = (weight**0.425) * (height**0.725) * 0.007184
    return round(bodysurf, 2)

def main():
    st.title("ChemoThon - BreastSK v. 2.4")
    st.write("Vitajte v programe ChemoThon!")
    st.write("""Program rozpisuje najbežnejšie chemoterapie podľa povrchu alebo hmotnosti. 
    Najskôr si vypočítajte BSA a potom sa Vám sprístupní tlačidlo pre výpočet chemoterapie.
    Dávky je nutné upraviť podľa aktuálne dostupných balení liečiv.
    Autor nezodpovedá za prípadné škody spôsobené jeho použitím!
    Imunoterapiu nájdete na stránke https://immunothon.streamlit.app.
    Pripomienky a požiadavky na úrpavu posielajte na filip.kohutek@fntn.sk""")

    weight = st.number_input("Zadajte hmotnosť (kg):", min_value=1, max_value=250, step=1, value=None)
    height = st.number_input("Zadajte výšku (cm):", min_value=1, max_value=250, step=1, value=None)

    if st.button("Vypočítať BSA") and weight is not None and height is not None:
        rbodysurf = calculate_bsa(weight, height)
        st.session_state['rbodysurf'] = rbodysurf

    if 'rbodysurf' in st.session_state:
        st.write(f"Telesný povrch (BSA): {st.session_state['rbodysurf']} m²")

        chemo_options = {
            # --- Cytostatická liečba ---
            "AC": "AC.json",
            "DD-AC + G-CSF": "dd-AC.json",
            "EC": "EC.json",
            "docetaxel + G-CSF": "docetaxelbreast.json",
            "paclitaxel weekly": "paclitaxelweekly.json",
            "capecitabin": "capecitabine.json",
            "capecitabin X7/7 (metronomický)": "capecitabineX77.json",
            "eribulin (1.23 mg/m²)": "eribulin.json",
            "gemcitabin (1250 mg/m²)": "gemcitabine.json",
            "peg-doxorubicin": "pegdoxo.json",
            "vinorelbin p.o. weekly": "vinorelbinweekly.json",
            # --- Anti-HER2 ---
            "Pertuzumab": "firstpertuzumab.json",
            "TD-M1 (trastuzumab emtansín)": "TDM1.json",
            "Trastuzumab SC": "trastuzumabsc.json",
            "Trastuzumab IV": "firsttrastuzumabiv.json",
            "Trastuzumab-deruxtecan (T-DXd, HER2+/HER2-low)": "TDx.json",
            "Trastuzumab/Pertuzumab SC (Phesgo)": "firsttrastupertu.json",
            # --- Sacituzumab ---
            "Sacituzumab govitecan (TNBC / HR+)": "Sacgov.json",
            # --- Anti-HER2 orálna/kombinácia ---
            "Tucatinib 300mg BID + kapecitabín + trastuzumab (HER2CLIMB)": "tucatinib.json",
            "Neratinib 240mg/deň + kapecitabín (NALA / ExteNET adjuvant)": "neratinib.json",
            # --- Cielená/orálna liečba (flat dose) ---
            "Olaparib 300 mg BID (gBRCA1/2+, KATHERINE/OlympiA)": "olaparib.json",
            "Abemaciclib 150 mg BID D1-28 (HR+/HER2−, monarchE/MONARCH-3)": "abemaciclib.json",
            "Palbociclib 125 mg D1-21 (HR+/HER2−, PALOMA)": "palbociclib.json",
            "Ribociclib (HR+/HER2−, MONALEESA/NATALEE)": "ribociclib.json",
            "Everolimus 10 mg/deň + Exemestan 25 mg/deň (HR+/HER2−, BOLERO-2)": "everolimus_exemestane.json",
            "Capivasertib 400 mg 4on/3off + fulvestrant (PIK3CA/AKT1/PTEN)": "capivasertib.json",
        }

        chemo_name = st.selectbox("Vyberte chemoterapeutický režim:", list(chemo_options.keys()))

        if chemo_name == "Pertuzumab":
            pertuzumab_option = st.radio("Zvoľte typ podania pertuzumabu:", ["Prvé podanie", "Ďalšie podania"])
            selected_filename = "firstpertuzumab.json" if pertuzumab_option == "Prvé podanie" else "elsepertuzumab.json"
        elif chemo_name == "Trastuzumab IV":
            trastuzumab_option = st.radio("Zvoľte typ podania trastuzumabu IV:", ["Prvé podanie", "Ďalšie podania"])
            selected_filename = "firsttrastuzumabiv.json" if trastuzumab_option == "Prvé podanie" else "elsetrastuzumabiv.json"
        elif chemo_name == "Trastuzumab/Pertuzumab SC (Phesgo)":
            combo_option = st.radio("Zvoľte typ podania Phesgo:", ["Prvé podanie", "Ďalšie podania"])
            selected_filename = "firsttrastupertu.json" if combo_option == "Prvé podanie" else "elsetrastupertu.json"
        elif chemo_name == "Ribociclib (HR+/HER2−, MONALEESA/NATALEE)":
            ribo_option = st.radio(
                "Zvoľte indikáciu ribociklibu:",
                ["600 mg/deň D1-21 (metastatická, MONALEESA)", "400 mg/deň D1-21 (adjuvantná, NATALEE)"]
            )
            selected_filename = "ribociclib.json" if "600" in ribo_option else "ribociclib400.json"
        else:
            selected_filename = chemo_options[chemo_name]

        if st.button('Zobraziť protokol chemoterapie') and weight is not None:
            display_chemotherapy_details(
                st.session_state['rbodysurf'], selected_filename, weight
            )
        else:
            if weight is None:
                st.error("Prosím, zadajte hmotnosť na výpočet chemoterapie.")

if __name__ == "__main__":
    main()



# ===== Zdroje / Sources (pridané 2026-06, aditívne) =====
with st.expander("📚 Zdroje k režimom / Sources"):
    st.markdown("""**Kľúčové referencie – karcinóm prsníka**

Guidelines: [ESMO](https://www.esmo.org/guidelines/esmo-clinical-practice-guidelines-breast-cancer) · [NCCN](https://www.nccn.org/guidelines/category_1). Vždy overte podľa aktuálnej verzie guidelines a dostupných balení liečiv. Stav: jún 2026.

- **AC / EC** — Antracyklínový základ; NSABP B-15/B-23; EBCTCG meta-analýza, Lancet 2012.
- **dd-AC (dose-dense) + G-CSF** — CALGB 9741 – Citron et al., J Clin Oncol 2003.
- **Pertuzumab + trastuzumab + docetaxel** — CLEOPATRA – Swain et al., NEJM 2015; adjuvant APHINITY – von Minckwitz et al., NEJM 2017.
- **T-DM1 (trastuzumab emtansín)** — EMILIA – Verma et al., NEJM 2012; adjuvant KATHERINE – von Minckwitz et al., NEJM 2019.
- **Trastuzumab IV/SC** — HERA – Piccart-Gebhart et al., NEJM 2005; SC: HannaH – Ismael et al., Lancet Oncol 2012.
- **Trastuzumab-deruxtecan (T-DXd)** — DESTINY-Breast03 – Cortés et al., NEJM 2022; HER2-low: DESTINY-Breast04 – Modi et al., NEJM 2022.
- **Sacituzumab govitecan** — ASCENT (mTNBC) – Bardia et al., NEJM 2021; TROPiCS-02 (HR+) – Rugo et al., Lancet 2023.
- **Eribulín** — EMBRACE – Cortes et al., Lancet 2011.
- **Paklitaxel weekly** — CALGB 9840 – Seidman et al., J Clin Oncol 2008.
- **Docetaxel** — Štandardný taxán; NCCN Breast Cancer.
- **Kapecitabín / X7/7 (metronomický)** — Kapecitabín monoterapia – NCCN; metronomický režim – inštitucionálny.
- **Gemcitabín** — Paklitaxel/gemcitabín – Albain et al., J Clin Oncol 2008.
- **PEG-doxorubicín (lipozomálny)** — Pegylovaný lipozomálny doxorubicín – O'Brien et al., Ann Oncol 2004.
- **Vinorelbín p.o. weekly** — Perorálny vinorelbín – NCCN Breast Cancer.

**Nové režimy pridané v 2.4 (dávky overené podľa SmPC/eviQ/BCCA):**
- Olaparib 300 mg BID (OlympiA adjuvant; OlympiAD metastatic) — BRCA1/2+, HER2−
- Abemaciclib 150 mg BID (monarchE; MONARCH-3) — HR+/HER2−
- Palbociclib 125 mg (PALOMA-2/3) — HR+/HER2−
- Ribociclib 600 mg (MONALEESA) — HR+/HER2−
- Capivasertib 400 mg 4on/3off + fulvestrant (CAPItello-291, NEJM 2023) — PIK3CA/AKT1/PTEN

**Opravy dávok v 2.4:**
- Eribulin: **1.0 → 1.23 mg/m²** (SmPC; eviQ BCERIB)
- Gemcitabín: **1200 → 1250 mg/m²** (BCCA BCABGEMCIT; eviQ)
- PEG-doxorubicín: doplnená rýchlosť infúzie per SmPC Caelyx
- Trastuzumab IV: doplnená premedikácia 1. podania per SmPC

**Ešte mimo nástroja:**
- Trastuzumab-deruxtecan pri HER2-ultralow — DESTINY-Breast06, NEJM 2024.""")
