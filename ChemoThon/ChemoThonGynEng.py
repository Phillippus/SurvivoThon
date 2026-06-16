import streamlit as st
import json
from sk_to_eng import sk_to_eng, show_evidence_eng

def load_chemotherapy_data():
    """Loads all chemotherapy data from a JSON file."""
    try:
        with open('data/chemotherapyGYNENG.json', 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        st.error("Chemotherapy data file not found. Please ensure the JSON file is in the 'data' directory.")
        return None
    except json.JSONDecodeError:
        st.error("Error decoding JSON. Please check the file format.")
        return None

def calculate_carboplatin_dose(crcl, auc):
    """Calculates Carboplatin dose based on CrCl and AUC."""
    return round((crcl + 25) * auc, 2)

def display_chemotherapy_details(protocol, bsa, weight, crcl=None, auc=None):
    """Displays details of the selected chemotherapy protocol."""
    st.write(f"### Protocol: {protocol['name']}")

    # Display Basic Prescription
    for drug in protocol.get("Chemo", []):
        if drug["Name"].lower() == "carboplatin":
            if auc and crcl:
                dose = calculate_carboplatin_dose(crcl, auc)
            else:
                dose = "Requires AUC and CrCl"
        else:
            dose = round(drug["Dosage"] * bsa, 2) if "Dosage" in drug else "Unknown"
        st.write(f"- {drug['Name']} {drug['Dosage']} {drug['DosageMetric']} ......... {dose} mg D{drug['Day']}")

    st.write(f"**Next Cycle:** {protocol.get('NextCycle', 'Unknown')} days")

    # Premedication
    premed_note = protocol.get("Day1", {}).get("Premed", {}).get("Note", "")
    if premed_note:
        st.write("#### Day 1 - Premedication")
        st.write(premed_note)

    # Day 1 Chemotherapy Instructions
    st.write("#### Day 1 - Chemotherapy")
    for instruction in protocol.get("Day1", {}).get("Instructions", []):
        drug_name = instruction["Name"].lower()
        dose = None

        if drug_name == "carboplatin":
            if auc and crcl:
                dose = f"{calculate_carboplatin_dose(crcl, auc)} mg"  # Add "mg" explicitly
            else:
                dose = "Requires AUC and CrCl"
        else:
            # Calculate dose for other drugs using BSA
            matching_drug = next(
                (drug for drug in protocol.get("Chemo", []) if drug["Name"].lower() == drug_name), None
            )
            if matching_drug and "Dosage" in matching_drug:
                dose = f"{round(matching_drug['Dosage'] * bsa, 2)} mg"

        # Display the instruction with the calculated dose
        if dose:
            st.write(f"{instruction['Name']} - {dose}, {instruction.get('Instruction', 'No instructions available.')}")
        else:
            st.write(f"{instruction['Name']} - {instruction.get('Instruction', 'No instructions available.')}")

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
    st.title("ChemoThon  Gynecology  v 3.2 ENG")
    st.write("""Welcome to ChemoThon!
This application provides assistance in prescribing chemotherapy regimens based on body surface area (BSA), weight, or AUC for carboplatin-based treatments.
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

    if 'bsa' in st.session_state:
        st.write(f"Body Surface Area (BSA): {st.session_state['bsa']} m²")
        bsa = st.session_state['bsa']
        weight_val = st.session_state.get('weight', weight) or weight

        # New regimens (added 2026-06)
        extra_new = [
            "Mirvetuximab soravtansine 6 mg/kg (FRα+ platinum-resistant ovarian, MIRASOL)",
            "Lenvatinib 20 mg/day + Pembrolizumab (endometrial, KEYNOTE-775)",
            "Pembrolizumab + Carboplatin + Paclitaxel (endometrial, NRG-GY018)",
            "Platinum + Paclitaxel + Bevacizumab + Pembrolizumab (endometrial/cervical)",
        ]
        chemo_names = [protocol["name"] for protocol in data["chemotherapies"]]
        selected_protocol_name = st.selectbox("Select a chemotherapy regimen:", chemo_names + extra_new)

        # Check if Carboplatin needed
        protocol = None
        crcl, auc = None, None
        if selected_protocol_name not in extra_new:
            protocol = next((p for p in data["chemotherapies"] if p["name"] == selected_protocol_name), None)
            if protocol and any(drug["Name"].lower() == "carboplatin" for drug in protocol.get("Chemo", [])):
                crcl = st.number_input("Enter Creatinine Clearance (CrCl in mL/min):", min_value=1, max_value=200, step=1, value=None)
                auc = st.number_input("Enter Area Under Curve (AUC, 2-6):", min_value=2, max_value=6, step=1, value=None)
                if crcl is not None and crcl < 30:
                    st.error("The patient seems to be platinum-ineligible!")
        elif selected_protocol_name == "Pembrolizumab + Carboplatin + Paclitaxel (endometrial, NRG-GY018)":
            crcl = st.number_input("Enter Creatinine Clearance (CrCl in mL/min):", min_value=1, max_value=200, step=1, value=None)
            auc = st.number_input("Enter AUC (typically 5):", min_value=2, max_value=6, step=1, value=None)

        if st.button("Display Protocol"):
            if selected_protocol_name == "Mirvetuximab soravtansine 6 mg/kg (FRα+ platinum-resistant ovarian, MIRASOL)":
                display_simple_json("mirvetuximab.json", bsa, weight_val)
            elif selected_protocol_name == "Lenvatinib 20 mg/day + Pembrolizumab (endometrial, KEYNOTE-775)":
                display_simple_json("lenvatinib.json", bsa, weight_val)
                st.write("---")
                st.write("**Pembrolizumab (concurrent with lenvatinib):**")
                st.write("pembrolizumab 200 mg flat dose in 100 ml NaCl i.v./30 min D1 q3w")
                st.write("NC 21 days (pembrolizumab q3w, lenvatinib continuous D1-28)")
            elif selected_protocol_name == "Pembrolizumab + Carboplatin + Paclitaxel (endometrial, NRG-GY018)":
                display_simple_json("pembrolizumab_carboplatin_paclitaxel_gyn.json", bsa, weight_val)
                if crcl and auc:
                    st.write(f"Carboplatin AUC {auc} ......... {(crcl + 25) * auc} mg D1")
            elif selected_protocol_name == "Platinum + Paclitaxel + Bevacizumab + Pembrolizumab (endometrial/cervical)":
                import json as _j
                _bpj = _j.load(open("data/cbdca_taxol_beva_pembro_gyn.json", encoding="utf-8"))
                taxol_dose = round(175 * bsa, 2)
                beva_dose = round(15 * weight_val, 2) if weight_val else "?"
                pt_choice = st.selectbox("Select platinum:", ["Choose", "Carboplatin AUC 5 D1", "Cisplatin 50 mg/m2 D1"], key="pt_bpj_eng")
                if pt_choice == "Carboplatin AUC 5 D1":
                    crcl_b = st.number_input("Creatinine Clearance (ml/min):", min_value=1, max_value=250, value=None, key="crcl_bpj_eng")
                    if crcl_b is not None:
                        cbdca_dose = (crcl_b + 25) * 5
                        st.write("#### Chemotherapy Drugs")
                        st.write(f"pembrolizumab 200 mg flat dose D1")
                        st.write(f"paclitaxel 175 mg/m2 ......... {taxol_dose} mg D1")
                        st.write(f"carboplatin AUC 5 ......... {cbdca_dose} mg D1")
                        st.write(f"bevacizumab 15 mg/kg ......... {beva_dose} mg D1")
                        st.write("**Next Cycle:** 21 days")
                        st.write("#### D1 - Premedication")
                        st.write(sk_to_eng(_bpj["Day1"]["Premed"]["Note"]))
                        st.write("#### D1 - Chemotherapy Instructions")
                        st.write(f"pembrolizumab 200 mg {sk_to_eng(_bpj['Day1']['Instructions'][0]['Inst'])}")
                        st.write(f"paclitaxel {taxol_dose} mg {sk_to_eng(_bpj['Day1']['Instructions'][1]['Inst'])}")
                        st.write(f"carboplatin {cbdca_dose} mg in 500 ml NaCl i.v./60 min")
                        st.write(f"bevacizumab {beva_dose} mg {sk_to_eng(_bpj['Day1']['Instructions'][2]['Inst'])}")
                        show_evidence_eng(_bpj)
                elif pt_choice == "Cisplatin 50 mg/m2 D1":
                    ddp_dose = round(50 * bsa, 2)
                    ddp_vials = int(ddp_dose // 50); ddp_rem = round(ddp_dose % 50, 2)
                    st.write("#### Chemotherapy Drugs")
                    st.write(f"pembrolizumab 200 mg flat dose D1")
                    st.write(f"paclitaxel 175 mg/m2 ......... {taxol_dose} mg D1")
                    st.write(f"cisplatin 50 mg/m2 ......... {ddp_dose} mg D1")
                    st.write(f"bevacizumab 15 mg/kg ......... {beva_dose} mg D1")
                    st.write("**Next Cycle:** 21 days")
                    st.write("#### D1 - Premedication")
                    st.write(sk_to_eng(_bpj["Day1"]["Premed"]["Note"]))
                    st.write("#### D1 - Chemotherapy Instructions")
                    st.write(f"pembrolizumab 200 mg {sk_to_eng(_bpj['Day1']['Instructions'][0]['Inst'])}")
                    st.write(f"paclitaxel {taxol_dose} mg {sk_to_eng(_bpj['Day1']['Instructions'][1]['Inst'])}")
                    for _ in range(ddp_vials):
                        st.write("cisplatin 50 mg in 500 ml normal saline i.v./60 min")
                    if ddp_rem > 0:
                        st.write(f"cisplatin {ddp_rem} mg in 500 ml normal saline i.v./60 min")
                    st.write("Mannitol 10% 250 ml i.v. after cisplatin")
                    st.write(f"bevacizumab {beva_dose} mg {sk_to_eng(_bpj['Day1']['Instructions'][2]['Inst'])}")
                    show_evidence_eng(_bpj)
            elif protocol:
                if selected_protocol_name == "INTERLACE CBDCA/Paclitaxel":
                    st.info("⚠️ INTERLACE: 6 induction cycles of CBDCA/paclitaxel (AUC 2 / 80 mg/m²), then switch to cisplatin 40 mg/m² weekly during radiotherapy (alternative: flat dose cisplatin 50 mg weekly).")
                display_chemotherapy_details(protocol, bsa, weight_val, crcl, auc)
            else:
                st.error("Selected protocol not found.")

if __name__ == "__main__":
    main()



# ===== Zdroje / Sources (pridané 2026-06, aditívne) =====
with st.expander("📚 Zdroje k režimom / Sources"):
    st.markdown("""**Key references – gynaecological cancers**

Guidelines: [ESMO](https://www.esmo.org/guidelines/esmo-clinical-practice-guidelines-gynaecological-cancers) · [NCCN](https://www.nccn.org/guidelines/category_1). Always verify against the current guideline version and available drug vial sizes. As of: June 2026.

- **CBDCA / paklitaxel** — GOG-158 – Ozols et al., J Clin Oncol 2003; ICON3.
- **INTERLACE (indukčná CBDCA/paklitaxel, cervix)** — INTERLACE – McCormack et al., Lancet 2024.
- **Cisplatina / paklitaxel (cervix)** — GOG-240 – Tewari et al., NEJM 2014 (so/bez bevacizumabu).
- **Topotekan + G-CSF** — Topotekan pri relapse ovaria – ten Bokkel Huinink et al., J Clin Oncol 1997.
- **PEG-doxorubicín** — PLD pri rekurentnom ovariu – Gordon et al., J Clin Oncol 2001.
- **CBDCA / PEG-doxorubicín** — CALYPSO – Pujade-Lauraine et al., J Clin Oncol 2010.
- **CBDCA / gemcitabín** — Pfisterer et al., J Clin Oncol 2006 (AGO-OVAR/ICON4-like).
- **Bevacizumab 15 mg/kg** — GOG-218 – Burger et al., NEJM 2011; ICON7 – Perren et al., NEJM 2011.

**Current standards to consider (not yet in tool):**
- PARP inhibítory v udržiavaní (olaparib SOLO-1; niraparib PRIMA) – NEJM 2018/2019.
- **Dostarlimab / pembrolizumab + chemo pri endometriálnom karcinóme** — RUBY / NRG-GY018, NEJM 2023 → pembrolizumab + CBDCA + paklitaxel teraz v nástroji.
- **Mirvetuximab soravtansin pri FRα+ platina-rezistentnom ovariu** — MIRASOL, NEJM 2023 → teraz v nástroji.
- **Lenvatinib + pembrolizumab pri endometriálnom karcinóme** — KEYNOTE-775, NEJM 2022 → teraz v nástroji.""")
