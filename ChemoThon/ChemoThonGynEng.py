import streamlit as st
import json

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

def main():
    st.title("ChemoThon  Gynecology  v 3.0 ENG")
    st.write("""Welcome to ChemoThon!
This application provides assistance in prescribing chemotherapy regimens based on body surface area (BSA), weight, or AUC for carboplatin-based treatments.
Please ensure that doses are adjusted to align with the packaging and protocols available in your country. Users bear full responsibility for applying this tool in clinical practice.

We welcome your feedback to improve this app further. Feel free to reach out at filip.kohutek@fntn.sk.""")

    # Load chemotherapy data
    data = load_chemotherapy_data()
    if not data:
        return

    # User input for weight and height
    with st.container():
        st.subheader("Patient Information")
        weight = st.number_input("Enter weight (kg):", min_value=1, max_value=200, step=1, value=None)
        height = st.number_input("Enter height (cm):", min_value=1, max_value=250, step=1, value=None)

    if not weight or not height:
        st.warning("Please enter valid weight and height to proceed.")
        return

    # Calculate BSA
    bsa = calculate_bsa(weight, height)
    st.success(f"Calculated BSA: {bsa} m²")

    # Select chemotherapy regimen
    st.subheader("Chemotherapy Regimen Selection")
    chemo_names = ["Select a regimen..."] + [protocol["name"] for protocol in data["chemotherapies"]]
    selected_protocol_name = st.selectbox("Select a chemotherapy regimen:", chemo_names, index=0)

    # Ensure a valid regimen is selected
    if selected_protocol_name == "Select a regimen...":
        st.warning("Please select a valid chemotherapy regimen to proceed.")
        return

    # Check if Carboplatin is in the selected regimen
    protocol = next((p for p in data["chemotherapies"] if p["name"] == selected_protocol_name), None)
    crcl, auc = None, None

    if protocol and any(drug["Name"].lower() == "carboplatin" for drug in protocol.get("Chemo", [])):
        st.subheader("Additional Parameters for Carboplatin")
        crcl = st.number_input("Enter Creatinine Clearance (CrCl in mL/min):", min_value=1, max_value=200, step=1, value=None)
        auc = st.number_input("Enter Area Under Curve (AUC, 2-6):", min_value=2, max_value=6, step=1, value=None)

        # Check for platinum ineligibility if CrCl < 30
        if crcl is not None and crcl < 30:
            st.error("The patient seems to be platinum-ineligible!")

    # Display protocol details button
    with st.container():
        st.subheader("Display Chemotherapy Details")
        if st.button("Display Protocol"):
            if protocol:
                display_chemotherapy_details(protocol, bsa, weight, crcl, auc)
            else:
                st.error("Selected protocol not found.")

if __name__ == "__main__":
    main()