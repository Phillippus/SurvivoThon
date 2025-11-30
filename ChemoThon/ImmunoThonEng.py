import streamlit as st
import json

# Load immunotherapy data from a JSON file
def load_immunotherapy_data(file_path):
    with open(file_path, "r") as file:
        data = json.load(file)
    return data['imunoterapie']

# Function to generate prescription
def generate_prescription(selected_drug, weight=None):
    # Initialize prescription string
    prescription = ""

    # Check if premedication is required
    if 'premedication' in selected_drug:
        prescription += f"Premedication: {selected_drug['premedication']}\n\n"

    # Check if weight-based dosing is required
    if 'mg/kg' in selected_drug['dosage'] and weight:
        dosage_per_kg = float(selected_drug['dosage'].split()[0].replace('mg/kg', '').strip())
        dosage = dosage_per_kg * weight
        if 'max_dose' in selected_drug and dosage > float(selected_drug['max_dose'].split()[0]):
            dosage = float(selected_drug['max_dose'].split()[0])
        dosage_str = f"{dosage} mg"
    else:
        dosage_str = selected_drug['dosage']

    # Generate prescription details
    prescription += f"{selected_drug['name']} {dosage_str} in 500ml NS (normal saline) / {selected_drug['administration']}\n\n"
    prescription += " " * 5 + f"NC Day {selected_drug['frequency'].split()[0]}"

    return prescription

# Application title
st.title("""ImmunoThonEng v. 1.0
         
Welcome to the ImmunoThon Program!         
This tool generates common immunotherapy prescriptions using flat-dose or weight-based dosing.
Dosages must be adjusted according to the available drug formulations.
The author takes no responsibility for any damages resulting from its use!
Send feedback to filip.kohutek@fntn.sk""")

# Load immunotherapy data
immunotherapy_data = load_immunotherapy_data("data/ImmunotherapyEng.json")

# Section for selecting immunotherapy
st.header("Select Immunotherapy")

# Dropdown menu to select a therapy regimen with no default selection
immunotherapy_choice = st.selectbox(
    "Choose immunotherapy regimen",
    options=[""] + [drug["regimen name"] for drug in immunotherapy_data],  # Adding empty string for no pre-selection
    index=0
)

# Look up details for the selected drug
selected_drug = next((drug for drug in immunotherapy_data if drug["regimen name"] == immunotherapy_choice), None)

# Display weight input if weight-based dosing is used
weight = None
if selected_drug and 'mg/kg' in selected_drug['dosage']:
    weight = st.number_input("Enter patient weight (kg):", min_value=1, max_value=250, step=1, value=None)

# Display prescription if a drug is selected
if selected_drug:
    # Button to generate prescription
    if st.button("Generate Prescription"):
        prescription = generate_prescription(selected_drug, weight)
        st.subheader("Immunotherapy Prescription:")
        st.markdown(prescription)