import streamlit as st
import json
from sk_to_eng import sk_to_eng, show_evidence_eng

def load_chemotherapy_data():
    """Loads all chemotherapy data from the consolidated JSON file."""
    try:
        with open('data/chemotherapyBRSENG.json', 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        st.error("Chemotherapy data file not found. Please ensure 'chemotherapyBRSENG.json' is in the 'data' directory.")
        return None
    except json.JSONDecodeError:
        st.error("Error decoding JSON. Please check the file format.")
        return None

def calculate_bsa(weight, height):
    """Calculates body surface area using the DuBois formula."""
    return round((weight**0.425) * (height**0.725) * 0.007184, 2)

def display_chemotherapy_details(protocol, bsa, weight):
    """Displays details of the selected chemotherapy protocol."""
    st.write(f"### Protocol: {protocol['name']}")
    
    # Display chemotherapy drugs with calculated doses
    if "Chemo" in protocol and protocol["Chemo"]:
        st.write("#### Chemotherapy Drugs")
        for drug in protocol["Chemo"]:
            if isinstance(drug["Dosage"], str) and "/" in drug["Dosage"]:
                try:
                    dose_parts = [float(part) for part in drug["Dosage"].split("/")]
                    dosage = f"{round(dose_parts[0], 2)}/{round(dose_parts[1], 2)}mg"
                except (ValueError, TypeError, IndexError):
                    dosage = drug["Dosage"]
            elif drug["DosageMetric"] == "mg/m2":
                dosage = round(drug["Dosage"] * bsa, 2)
            elif drug["DosageMetric"] == "mg/kg":
                try:
                    dosage = round(float(drug["Dosage"]) * weight, 2)
                except (KeyError, TypeError, ValueError):
                    dosage = "N/A"
            else:
                try:
                    dosage = round(float(drug["Dosage"]), 2)
                except (TypeError, ValueError):
                    dosage = drug["Dosage"]
            if drug["DosageMetric"] in ["mg/m2", "mg/kg"]:
                st.write(f"{drug['Name']} {drug['Dosage']} {drug['DosageMetric']} ......... {dosage} mg D {drug['Day']}")
            else:
                dose_str = dosage if isinstance(dosage, str) and "mg" in dosage else f"{dosage}mg"
                st.write(f"{drug['Name']} {dose_str} D {drug['Day']}")
    else:
        st.warning("No chemotherapy drugs found for this protocol.")

    # Display Next Cycle
    next_cycle = protocol.get("NextCycle", "Unknown")
    st.write(f"**Next Cycle:** {next_cycle} days")

    # Display Day 1 Premedication and Instructions
    if "Day1" in protocol:
        st.write("#### D1 - Premedication")
        premed_note = protocol["Day1"]["Premed"].get("Note", "No premedication details available.")
        st.write(premed_note.replace("Degan", "metoclopramide"))  # Adjust Degan to metoclopramide
        
        if "Instructions" in protocol["Day1"]:
            st.write("#### D1 - Chemotherapy Instructions")
            for instruction in protocol["Day1"]["Instructions"]:
                instruction_text = instruction.get("Instruction", "No instructions available.").replace("tablet", "pill")
                drug_name = instruction.get("Name", "Unknown")
                # Calculate Day 1 dose
                drug = next((d for d in protocol["Chemo"] if d["Name"] == drug_name), None)
                if drug:
                    if isinstance(drug["Dosage"], str) and "/" in drug["Dosage"]:
                        try:
                            dose_parts = [float(part) for part in drug["Dosage"].split("/")]
                            dose = f"{round(dose_parts[0], 2)}/{round(dose_parts[1], 2)}mg"
                        except (ValueError, TypeError, IndexError):
                            dose = drug["Dosage"]
                    elif drug["DosageMetric"] == "mg/m2":
                        dose = round(drug["Dosage"] * bsa, 2)
                    elif drug["DosageMetric"] == "mg/kg":
                        try:
                            dose = round(float(drug["Dosage"]) * weight, 2)
                        except (KeyError, TypeError, ValueError):
                            dose = "N/A"
                    else:
                        try:
                            dose = round(float(drug["Dosage"]), 2)
                        except (TypeError, ValueError):
                            dose = drug["Dosage"]
                    dose_str = dose if isinstance(dose, str) and "mg" in dose else f"{dose}mg"
                    st.write(f"{drug_name} - {dose_str}, {instruction_text}")
                else:
                    st.write(f"{drug_name} - {instruction_text}")
        else:
            st.warning("No instructions available for Day 1.")
    else:
        st.warning("No details found for Day 1.")


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
    st.title("ChemoThon Breast v. 3.4 ENG")
    st.write("""Welcome to ChemoThon!
This application provides assistance in prescribing chemotherapy regimens based on body surface area (BSA) or weight,
Please ensure that doses are adjusted to align with the packaging and protocols available in your country. Users bear full responsibility for applying this tool in clinical practice.
Immunotherapy can be found at https://immunothoneng.streamlit.app
             
We welcome your feedback to improve this app further. Feel free to reach out at filip.kohutek@fntn.sk.""")

    # Load chemotherapy data
    data = load_chemotherapy_data()
    if not data:
        return

    # User input for weight and height
    weight = st.number_input("Enter weight (kg):", min_value=1, max_value=250, step=1, value=None)
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

        # Sorting logic: non-biological first, then biological
        def is_biological(name):
            name_lower = name.lower()
            return any(keyword in name_lower for keyword in ["trastuzumab", "pertuzumab", "govitecan", "deruxtecan", "td-m1"])

        chemo_names = [protocol["name"] for protocol in data.get("chemotherapies", [])]
        chemo_names_sorted = sorted([name for name in chemo_names if not is_biological(name)])
        bio_names_sorted = sorted([name for name in chemo_names if is_biological(name)])
        # New regimens (added 2026-06)
        extra_new = [
            "Olaparib 300 mg BID (BRCA1/2+, OlympiAD/EMBRACA)",
            "Abemaciclib 150 mg BID + ET (HR+/HER2−, monarchE/MONARCH-2, D1-28 continuous)",
            "Ribociclib (HR+/HER2−, MONALEESA/NATALEE)",
            "Everolimus 10 mg/day + Exemestane 25 mg/day (HR+/HER2−, BOLERO-2)",
            "Capivasertib 400 mg BID 4/3 + fulvestrant (PIK3CA/AKT1/PTEN, CAPItello-291)",
            "Tucatinib 300 mg BID + Capecitabine (HER2+, HER2CLIMB)",
            "Neratinib 240 mg/day + Capecitabine (HER2+, NALA/ExteNET)",
        ]
        sorted_names = chemo_names_sorted + bio_names_sorted + extra_new

        selected_protocol_name = st.selectbox("Select a chemotherapy regimen:", sorted_names)

        # Ribociclib subdialog
        ribo_file = None
        if selected_protocol_name == "Ribociclib (HR+/HER2−, MONALEESA/NATALEE)":
            ribo_option = st.radio(
                "Select ribociclib indication:",
                ["600 mg/day D1-21 (metastatic, MONALEESA)", "400 mg/day D1-21 (adjuvant, NATALEE)"]
            )
            ribo_file = "ribociclib.json" if "600" in ribo_option else "ribociclib400.json"

        if st.button("Display Protocol"):
            if selected_protocol_name == "Olaparib 300 mg BID (BRCA1/2+, OlympiAD/EMBRACA)":
                display_simple_json("olaparib.json", bsa, weight_val)
            elif selected_protocol_name == "Abemaciclib 150 mg BID + ET (HR+/HER2−, monarchE/MONARCH-2, D1-28 continuous)":
                display_simple_json("abemaciclib.json", bsa, weight_val)
            elif selected_protocol_name == "Ribociclib (HR+/HER2−, MONALEESA/NATALEE)":
                if ribo_file:
                    display_simple_json(ribo_file, bsa, weight_val)
            elif selected_protocol_name == "Everolimus 10 mg/day + Exemestane 25 mg/day (HR+/HER2−, BOLERO-2)":
                display_simple_json("everolimus_exemestane.json", bsa, weight_val)
            elif selected_protocol_name == "Capivasertib 400 mg BID 4/3 + fulvestrant (PIK3CA/AKT1/PTEN, CAPItello-291)":
                display_simple_json("capivasertib.json", bsa, weight_val)
            elif selected_protocol_name == "Tucatinib 300 mg BID + Capecitabine (HER2+, HER2CLIMB)":
                display_simple_json("tucatinib.json", bsa, weight_val)
            elif selected_protocol_name == "Neratinib 240 mg/day + Capecitabine (HER2+, NALA/ExteNET)":
                display_simple_json("neratinib.json", bsa, weight_val)
            else:
                protocol = next((p for p in data["chemotherapies"] if p["name"] == selected_protocol_name), None)
                if protocol:
                    display_chemotherapy_details(protocol, bsa, weight_val)
                else:
                    st.error("Selected protocol not found in the data.")

if __name__ == "__main__":
    main()



# ===== Zdroje / Sources (pridané 2026-06, aditívne) =====
with st.expander("📚 Zdroje k režimom / Sources"):
    st.markdown("""**Key references – breast cancer**

Guidelines: [ESMO](https://www.esmo.org/guidelines/esmo-clinical-practice-guidelines-breast-cancer) · [NCCN](https://www.nccn.org/guidelines/category_1). Always verify against the current guideline version and available drug vial sizes. As of: June 2026.

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

**Current standards to consider (not yet in tool):**
- **CDK4/6 inhibítory (palbociklib/ribociklib/abemaciklib) pri HR+/HER2−** — PALOMA/MONALEESA/MONARCH → abemaciklib teraz v nástroji.
- **Capivasertib + fulvestrant (PIK3CA/AKT1/PTEN)** — CAPItello-291, NEJM 2023 → teraz v nástroji.
- **Olaparib pri BRCA1/2-mutovanom mBC** — OlympiAD, NEJM 2017 → teraz v nástroji.
- Trastuzumab-deruxtecan pri HER2-low/ultralow – DESTINY-Breast06, NEJM 2024.""")
