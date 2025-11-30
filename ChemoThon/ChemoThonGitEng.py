import streamlit as st
import json

def load_chemotherapy_data():
    """Loads all chemotherapy data from a JSON file."""
    try:
        with open('data/chemotherapyGITENG.json', 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        st.error("Chemotherapy data file not found. Please ensure the JSON file is in the 'data' directory.")
        return None
    except json.JSONDecodeError:
        st.error("Error decoding JSON. Please check the file format.")
        return None

def calculate_bsa(weight, height):
    """Calculates body surface area using the DuBois formula."""
    return round((weight ** 0.425) * (height ** 0.725) * 0.007184, 2)

def calculate_cisplatin_doses(total_dose):
    """Calculates the infusion breakdown for cisplatin when the dose exceeds 50 mg."""
    dose_split = []
    while total_dose > 0:
        infusion_dose = min(50, total_dose)
        dose_split.append(infusion_dose)
        total_dose -= infusion_dose
    return dose_split

def display_chemotherapy_details(protocol, bsa, weight, crcl=None, auc=None):
    """Displays details of the selected chemotherapy protocol."""
    st.write(f"### Protocol: {protocol['name']}")

    # Display chemotherapy drugs with calculated doses
    st.write("#### Chemotherapy Drugs")
    calculated_doses = {}
    for drug in protocol.get("Chemo", []):
        if drug["Name"].lower() == "carboplatin":
            # Calculate carboplatin dose if AUC and CrCl are provided
            if auc and crcl:
                dose = round((crcl + 25) * auc, 2)
            else:
                dose = "requires AUC and CrCl"
        elif drug["Name"].lower() == "cisplatin":
            # Calculate cisplatin dose
            dose = round(drug["Dosage"] * (weight if "mg/kg" in drug["DosageMetric"] else bsa), 2)
        elif drug["Name"].lower() == "mitomycin":
            # Calculate mitomycin dose and enforce the cap
            dose = round(drug["Dosage"] * bsa, 2)
            if dose > 20:  # Apply the cap for all Mitomycin regimens
                st.error("⚠️ Dose of Mitomycin must not exceed 20 mg!")
                dose = 20
        else:
            # Calculate dose for other drugs using BSA or weight
            dose = round(drug["Dosage"] * (weight if "mg/kg" in drug["DosageMetric"] else bsa), 2)
        
        calculated_doses[drug["Name"].lower()] = dose
        st.write(f"{drug['Name']} {drug['Dosage']} {drug['DosageMetric']} ......... {dose if isinstance(dose, (int, float)) else dose} mg D{drug['Day']}")

    st.write(f"**Next Cycle:** {protocol.get('NextCycle', 'Unknown')} days")

    # Premedication
    premed_note = protocol.get("Day1", {}).get("Premed", {}).get("Note", "")
    if premed_note:
        st.write("#### Day 1 - Premedication")
        st.write(premed_note)

    # Day 1 Chemotherapy Instructions
    st.write("#### Day 1 - Chemotherapy Instructions")
    for instruction in protocol.get("Day1", {}).get("Instructions", []):
        drug_name = instruction.get("Name", "Unknown").lower()
        calculated_dose = calculated_doses.get(drug_name, "dose unavailable")

        # Display carboplatin dose dynamically
        if drug_name == "carboplatin" and isinstance(calculated_dose, (int, float)):
            st.write(f"{instruction['Name']} - {calculated_dose} mg, {instruction.get('Instruction', 'No instructions available.')}")
        elif drug_name == "carboplatin":
            st.write(f"{instruction['Name']} - requires AUC and CrCl, {instruction.get('Instruction', 'No instructions available.')}")
        
        # Handle cisplatin dose splitting
        elif drug_name == "cisplatin" and isinstance(calculated_dose, (int, float)):
            if calculated_dose > 50:
                cisplatin_split = calculate_cisplatin_doses(calculated_dose)
                for i, dose_split in enumerate(cisplatin_split, start=1):
                    st.write(f"{instruction['Name']} - {dose_split} mg in 500ml normal saline (NS), infusion {i}. {instruction.get('Instruction', '')}")
                # Add Mannitol after the last Cisplatin infusion
                st.write("Mannitol 10% 250 ml IV infusion - Administer after the last Cisplatin infusion.")
            else:
                st.write(f"{instruction['Name']} - {calculated_dose} mg in 500ml normal saline (NS), {instruction.get('Instruction', '')}")
                # Add Mannitol after a single Cisplatin infusion
                st.write("Mannitol 10% 250 ml IV infusion - Administer after the Cisplatin infusion.")
        
        # Handle other drugs
        else:
            st.write(f"{instruction['Name']} - {calculated_dose} mg, {instruction.get('Instruction', 'No instructions available.')}")

def main():
    st.title("ChemoThon Gastrointestinal (Except CRC) v 3.0 ENG")
    st.write("""Welcome to ChemoThon!
This application provides assistance in prescribing chemotherapy regimens based on body surface area (BSA), weight, or AUC for carboplatin-based treatments.
Please ensure that doses are adjusted to align with the packaging and protocols available in your country. Users bear full responsibility for applying this tool in clinical practice.

We welcome your feedback to improve this app further. Feel free to reach out at filip.kohutek@fntn.sk.""")


    # Load chemotherapy data
    data = load_chemotherapy_data()
    if not data:
        return

    # User input for weight and height without default values
    weight = st.number_input("Enter weight (kg):", min_value=1, max_value=200, step=1, value=None, format="%d")
    height = st.number_input("Enter height (cm):", min_value=1, max_value=250, step=1, value=None, format="%d")

    # Ensure inputs are provided before proceeding
    if not weight or not height:
        st.warning("Please enter valid weight and height to proceed.")
        return

    # Calculate BSA
    if "bsa" not in st.session_state:
        st.session_state["bsa"] = None

    if st.button("Calculate BSA"):
        bsa = calculate_bsa(weight, height)
        st.session_state['bsa'] = bsa
        st.success(f"Calculated Body Surface Area (BSA): {bsa:.2f} m²")

    # Show chemotherapy regimen options after BSA is calculated
    if st.session_state["bsa"]:
        st.write(f"**Current BSA:** {st.session_state['bsa']:.2f} m²")
        chemo_names = [protocol["name"] for protocol in data["chemotherapies"]]
        selected_protocol_name = st.selectbox("Select a chemotherapy regimen:", chemo_names)

        # Input CrCl and AUC for carboplatin-based regimens
        crcl = None
        auc = None
        if selected_protocol_name:
            protocol = next((p for p in data["chemotherapies"] if p["name"] == selected_protocol_name), None)
            if protocol and any("carboplatin" in drug["Name"].lower() for drug in protocol.get("Chemo", [])):
                crcl = st.number_input("Enter Creatinine Clearance (CrCl in mL/min):", min_value=1, max_value=200, step=1, value=None, format="%d")
                if crcl is not None and crcl < 30:
                    st.error("⚠️ Your patient seems to be platinum-ineligible!")
                auc = st.number_input("Enter Area Under Curve (AUC, 2-6):", min_value=2, max_value=6, step=1, value=None, format="%d")

                # Specific warning for CROSS regimen
                if selected_protocol_name.lower() == "cross regimen" and auc != 2:
                    st.warning("⚠️ For the CROSS regimen, the AUC value must be set to 2!")

        if st.button("Display Protocol"):
            if protocol:
                display_chemotherapy_details(protocol, st.session_state["bsa"], weight, crcl, auc)
            else:
                st.error("Selected protocol not found in the data.")

if __name__ == "__main__":
    main()