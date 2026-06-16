import streamlit as st
import json
from sk_to_eng import sk_to_eng, show_evidence_eng

def load_chemotherapy_data():
    """Loads all chemotherapy data from a JSON file."""
    try:
        with open('data/chemotherapyCRCENG.json', 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        st.error("Chemotherapy data file not found. Please ensure the JSON file is in the 'data' directory.")
        return None
    except json.JSONDecodeError:
        st.error("Error decoding JSON. Please check the file format.")
        return None

def display_chemotherapy_details(protocol, bsa, weight, is_initial_dose=None):
    """Displays details of the selected chemotherapy protocol."""
    st.write(f"### Protocol: {protocol['name']}")

    # Display chemotherapy drugs with calculated doses
    st.write("#### Chemotherapy Drugs")
    calculated_doses = {}
    if "Chemo" in protocol and protocol["Chemo"]:
        for drug in protocol["Chemo"]:
            # Handle Cetuximab initial and subsequent doses
            if protocol["name"] == "Cetuximab":
                if is_initial_dose and "initial" in drug["Day"]:
                    dose = round(drug["Dosage"] * bsa, 2)
                elif not is_initial_dose and "subsequent" in drug["Day"]:
                    dose = round(drug["Dosage"] * bsa, 2)
                else:
                    continue
            else:
                dose = round(drug["Dosage"] * (weight if "mg/kg" in drug["DosageMetric"] else bsa), 2)
            calculated_doses[drug["Name"]] = dose
            st.write(f"{drug['Name']} {drug['Dosage']} {drug['DosageMetric']} ......... {dose} mg D{drug['Day']}")
    else:
        st.warning("No chemotherapy drugs found for this protocol.")

    # Display next cycle information
    next_cycle = protocol.get("NextCycle", "Unknown")
    st.write(f"**Next Cycle:** {next_cycle} days")

    # Display premedication details
    if "Day1" in protocol and "Premed" in protocol["Day1"]:
        st.write("#### Day 1 - Premedication")
        premed_note = protocol["Day1"]["Premed"].get("Note", "")
        if premed_note:
            st.write(premed_note)

    # Display Day 1 chemotherapy instructions with calculated doses
    if "Day1" in protocol and "Instructions" in protocol["Day1"]:
        st.write("#### Day 1 - Chemotherapy Instructions")
        for instruction in protocol["Day1"]["Instructions"]:
            drug_name = instruction.get("Name", "Unknown")
            calculated_dose = calculated_doses.get(drug_name, "dose unavailable")
            st.write(f"{drug_name} - {calculated_dose} mg, {instruction.get('Instruction', 'No instructions available.')}")
    else:
        st.warning("No chemotherapy instructions found for Day 1.")

def calculate_bsa(weight, height):
    """Calculates body surface area using the DuBois formula."""
    return round((weight ** 0.425) * (height ** 0.725) * 0.007184, 2)


def display_simple_json(filename, bsa, weight=None):
    """Display regimen from individual JSON file (flat-dose / BSA / weight-based)."""
    try:
        with open(f'data/{filename}', 'r') as f:
            reg = json.load(f)
    except Exception as e:
        st.error(f"Error loading {filename}: {e}")
        return
    st.write("#### Chemotherapy Drugs")
    for drug in reg.get("Chemo", []):
        metric = drug.get("DosageMetric", "")
        dosage = drug.get("Dosage", 0)
        if "mg/kg" in metric and weight:
            calculated = round(dosage * weight, 2)
            st.write(f"{drug['Name']} {dosage} {metric} ......... {calculated} mg D{drug['Day']}")
        elif "mg/m2" in metric:
            calculated = round(dosage * bsa, 2)
            st.write(f"{drug['Name']} {dosage} {metric} ......... {calculated} mg D{drug['Day']}")
        else:
            st.write(f"{drug['Name']} {dosage} {metric} D{drug['Day']}")
    st.write(f"**Next Cycle:** {reg.get('NC', '?' )} days")
    premed = reg.get("Day1", {}).get("Premed", {}).get("Note", "")
    if premed:
        st.write("#### D1 - Premedication")
        st.write(sk_to_eng(premed))
    instructions = reg.get("Day1", {}).get("Instructions", [])
    if instructions:
        st.write("#### D1 - Chemotherapy Instructions")
        chemo_list = reg.get("Chemo", [])
        for inst in instructions:
            drug_name = inst.get("Name", "")
            inst_text = sk_to_eng(inst.get("Inst", ""))
            drug = next((d for d in chemo_list if d["Name"] == drug_name), None)
            if drug:
                metric = drug.get("DosageMetric", "")
                dosage = drug.get("Dosage", 0)
                if "flat" in metric.lower():
                    # flat-dose: instruction text already contains the dose → avoid duplication
                    st.write(f"{drug_name} - {inst_text}")
                else:
                    if "mg/kg" in metric and weight:
                        calc_dose = round(dosage * weight, 2)
                    elif "mg/m2" in metric:
                        calc_dose = round(dosage * bsa, 2)
                    else:
                        calc_dose = dosage
                    st.write(f"{drug_name} - {calc_dose} mg, {inst_text}")
            else:
                st.write(f"{drug_name} - {inst_text}")
    show_evidence_eng(reg)

def main():
    st.title("ChemoThon Colorectal v. 3.2 ENG")
    st.write("""Welcome to ChemoThon!
This application provides assistance in prescribing chemotherapy regimens based on body surface area (BSA) or weight,
Please ensure that doses are adjusted to align with the packaging and protocols available in your country. Users bear full responsibility for applying this tool in clinical practice.

We welcome your feedback to improve this app further. Feel free to reach out at filip.kohutek@fntn.sk.""")

    # Load chemotherapy data
    data = load_chemotherapy_data()
    if not data:
        return

    # User input for weight and height
    weight = st.number_input("Enter weight (kg):", min_value=1, max_value=200, step=1, value=None)
    height = st.number_input("Enter height (cm):", min_value=1, max_value=250, step=1, value=None)

    # Calculate BSA
    if st.button("Calculate BSA") and weight and height:
        bsa_val = calculate_bsa(weight, height)
        st.session_state['bsa'] = bsa_val
        st.session_state['weight'] = weight

    # Display available chemotherapy regimens
    if 'bsa' in st.session_state:
        st.write(f"Body Surface Area (BSA): {st.session_state['bsa']:.2f} m²")
        bsa = st.session_state['bsa']
        weight_val = st.session_state.get('weight', weight) or weight

        chemo_names = [protocol["name"] for protocol in data["chemotherapies"]]
        # New regimens (added 2026-06)
        extra_new = [
            "Encorafenib + Cetuximab (BRAF V600E mCRC, BEACON)",
            "Pembrolizumab 200 mg flat q3w (MSI-H/dMMR, KEYNOTE-177)",
            "Trifluridine/Tipiracil + Bevacizumab 5 mg/kg q2w (SUNLIGHT, 3rd line)",
            "Fruquintinib 5 mg/day (FRESCO-2, ≥3rd line mCRC)",
        ]
        selected_protocol_name = st.selectbox("Select a chemotherapy regimen:", chemo_names + extra_new)

        is_initial_dose = None
        if selected_protocol_name == "Cetuximab":
            is_initial_dose_str = st.radio("Is this the initial dose?", ('Yes', 'No'))
            is_initial_dose = True if is_initial_dose_str == "Yes" else False

        # Encorafenib+cetuximab subdialog
        encora_admin = None
        if selected_protocol_name == "Encorafenib + Cetuximab (BRAF V600E mCRC, BEACON)":
            encora_admin = st.radio("Cetuximab schedule:", [
                "Weekly (1st administration, 400 mg/m²)",
                "Weekly (subsequent, 250 mg/m²)",
                "Biweekly (500 mg/m² q2w)",
            ], key='encora_admin')

        if st.button("Display Protocol"):
            if selected_protocol_name == "Encorafenib + Cetuximab (BRAF V600E mCRC, BEACON)":
                import json as _j
                enc = _j.load(open("data/encorafenib_cetuximab.json", encoding="utf-8"))
                if encora_admin == "Weekly (1st administration, 400 mg/m²)":
                    ctx_dose = round(400 * bsa, 2)
                    ctx_label = f"400 mg/m² = {ctx_dose} mg (initial dose)"
                    ctx_nc = "7 (weekly)"
                elif encora_admin == "Weekly (subsequent, 250 mg/m²)":
                    ctx_dose = round(250 * bsa, 2)
                    ctx_label = f"250 mg/m² = {ctx_dose} mg (subsequent)"
                    ctx_nc = "7 (weekly)"
                else:
                    ctx_dose = round(500 * bsa, 2)
                    ctx_label = f"500 mg/m² = {ctx_dose} mg (biweekly)"
                    ctx_nc = "14 (biweekly)"
                st.write("#### Chemotherapy Drugs")
                st.write(f"encorafenib 300 mg flat dose (oral, daily) D1-28")
                st.write(f"cetuximab {ctx_label}")
                st.write(f"**Next Cycle:** {ctx_nc} days")
                st.write("#### D1 - Premedication")
                st.write(sk_to_eng(enc["Day1"]["Premed"]["Note"]))
                st.write("#### D1 - Chemotherapy Instructions")
                st.write(f"1. cetuximab {ctx_dose} mg – first 100 mg in 500 ml NaCl i.v./60 min, remainder in 500 ml NaCl i.v./90 min")
                st.write(f"2. encorafenib 300 mg p.o. once daily with or without food (continuous)")
                show_evidence_eng(enc)
            elif selected_protocol_name == "Pembrolizumab 200 mg flat q3w (MSI-H/dMMR, KEYNOTE-177)":
                display_simple_json("pembrolizumab_msiH.json", bsa, weight_val)
            elif selected_protocol_name == "Trifluridine/Tipiracil + Bevacizumab 5 mg/kg q2w (SUNLIGHT, 3rd line)":
                import json as _j
                sl = _j.load(open("data/tritipi_bev.json", encoding="utf-8"))
                ttd_dose = round(70 * bsa, 2)
                beva_dose = round(5 * weight_val, 2)
                st.write("#### SUNLIGHT — Trifluridine/Tipiracil + Bevacizumab")
                st.write(f"trifluridine/tipiracil 70 mg/m²/day ......... {ttd_dose} mg D1-5, D8-12")
                st.write(f"bevacizumab 5 mg/kg q2w ......... {beva_dose} mg D1, D15")
                st.write("**Next Cycle:** 28 days")
                st.write("#### D1 - Premedication")
                st.write(sk_to_eng(sl["Day1"]["Premed"]["Note"]))
                st.write("#### D1 - Chemotherapy Instructions")
                st.write(f"trifluridine/tipiracil {ttd_dose} mg {sk_to_eng(sl['Day1']['Instructions'][0]['Inst'])}")
                st.write(f"bevacizumab {beva_dose} mg {sk_to_eng(sl['Day1']['Instructions'][1]['Inst'])}")
                show_evidence_eng(sl)
            elif selected_protocol_name == "Fruquintinib 5 mg/day (FRESCO-2, ≥3rd line mCRC)":
                display_simple_json("fruquitinib.json", bsa, weight_val)
            else:
                protocol = next((p for p in data["chemotherapies"] if p["name"] == selected_protocol_name), None)
                if protocol:
                    if selected_protocol_name == "Cetuximab":
                        display_chemotherapy_details(protocol, bsa, weight_val, is_initial_dose)
                    else:
                        display_chemotherapy_details(protocol, bsa, weight_val)
                else:
                    st.error("Selected protocol not found in the data.")

if __name__ == "__main__":
    main()



# ===== Zdroje / Sources (pridané 2026-06, aditívne) =====
with st.expander("📚 Zdroje k režimom / Sources"):
    st.markdown("""**Key references – colorectal cancer**

Guidelines: [ESMO](https://www.esmo.org/guidelines/esmo-clinical-practice-guidelines-gastrointestinal-cancers) · [NCCN](https://www.nccn.org/guidelines/category_1). Always verify against the current guideline version and available drug vial sizes. As of: June 2026.

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

**Current standards to consider (not yet in tool):**
- **Encorafenib + cetuximab pri BRAF V600E** — BEACON CRC, NEJM 2019 → teraz v nástroji.
- **Pembrolizumab 1. línia pri MSI-H/dMMR** — KEYNOTE-177, NEJM 2020 → teraz v nástroji.
- **TAS-102 + bevacizumab (SUNLIGHT)** — Prager et al., NEJM 2023 → teraz v nástroji.
- Fruquintinib v ďalších líniách – FRESCO-2, Lancet 2023.""")
