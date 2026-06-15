import streamlit as st
import json

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

def main():
    st.title("ChemoThon Colorectal v. 3.1 ENG")
    st.write("""Welcome to ChemoThon!
This application provides assistance in prescribing chemotherapy regimens based on body surface area (BSA) or weight,
Please ensure that doses are adjusted to align with the packaging and protocols available in your country. Users bear full responsibility for applying this tool in clinical practice.

We welcome your feedback to improve this app further. Feel free to reach out at filip.kohutek@fntn.sk.""")

    # Load chemotherapy data
    data = load_chemotherapy_data()
    if not data:
        return

    # User input for weight and height with default values
    weight = st.number_input("Enter weight (kg):", min_value=1, max_value=200, step=1, value=70)
    height = st.number_input("Enter height (cm):", min_value=1, max_value=250, step=1, value=180)

    # Calculate BSA
    if st.button("Calculate BSA") and weight and height:
        bsa = calculate_bsa(weight, height)
        st.session_state['bsa'] = bsa
        st.write(f"Calculated Body Surface Area (BSA): {bsa:.2f} m²")

    # Display available chemotherapy regimens
    if 'bsa' in st.session_state:
        bsa = st.session_state['bsa']
        chemo_names = [protocol["name"] for protocol in data["chemotherapies"]]
        selected_protocol_name = st.selectbox("Select a chemotherapy regimen:", chemo_names)

        if selected_protocol_name == "Cetuximab":
            is_initial_dose = st.radio("Is this the initial dose?", ('Yes', 'No'))
            is_initial_dose = True if is_initial_dose == "Yes" else False

        if st.button("Display Protocol") and weight:
            protocol = next((p for p in data["chemotherapies"] if p["name"] == selected_protocol_name), None)
            if protocol:
                if selected_protocol_name == "Cetuximab":
                    display_chemotherapy_details(protocol, bsa, weight, is_initial_dose)
                else:
                    display_chemotherapy_details(protocol, bsa, weight)
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
- Encorafenib + cetuximab pri BRAF V600E – BEACON CRC, NEJM 2019.
- Pembrolizumab 1. línia pri MSI-H/dMMR – KEYNOTE-177, NEJM 2020.
- Fruquintinib v ďalších líniách – FRESCO-2, Lancet 2023.""")
