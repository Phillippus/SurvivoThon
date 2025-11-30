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

def Chemo(rbodysurf, chemoType):
    """ Function to handle simple chemotherapies with direct dosing. """
    chemo_json = load_json('data/' + chemoType)
    if chemo_json:
        st.write(f"### Chemotherapy Protocol: {chemoType.replace('.json', '')}")
        for chemo in chemo_json["Chemo"]:
            dosage = round(chemo["Dosage"] * rbodysurf, 2)
            st.write(f"{chemo['Name']} {chemo['Dosage']} {chemo['DosageMetric']} ......... {dosage} mg D{chemo['Day']}")
        
        st.write(f"NC {chemo_json['NC']} . day")
        st.write("D1")
        st.write(chemo_json["Day1"]["Premed"]["Note"])
        for instruction in chemo_json["Day1"]["Instructions"]:
            drug_name = instruction['Name']
            dosage = next((item['Dosage'] for item in chemo_json['Chemo'] if item['Name'] == drug_name), None)
            if dosage:
                adjusted_dosage = round(dosage * rbodysurf, 2)
                st.write(f"{drug_name} {adjusted_dosage} mg {instruction['Inst']}")

def ChemoMass(weight, chemoType):
    """ Function to handle chemotherapy/biologics based on weight. """
    chemo_json = load_json('data/' + chemoType)  # Ensure the 'data/' prefix is here
    if chemo_json:
        st.write(f"### Chemotherapy Protocol: {chemoType.replace('.json', '')}")
        for chemo in chemo_json["Chemo"]:
            dosage = round(chemo["Dosage"] * weight)
            st.write(f"{chemo['Name']} {chemo['Dosage']} {chemo['DosageMetric']} ......... {dosage} mg D{chemo['Day']}")
        
        st.write(f"NC {chemo_json['NC']} . day")
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

    st.write(f"### Chemotherapy Protocol: {chemoType.replace('.json', '')}")
    
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
    day5FU = "24 hours" if chemoType in ["FLOT.json", "mtc5FU.json"] else "48 hours"
    day15FU = "24 hours"

    st.write(f"5-fluorouracil {dos5FU} mg/m2 ...... {round(rbodysurf * dos5FU)} mg over {day5FU}")
    st.write(f"NC {chemo_json['NC']} . day")
    st.write("D1:")
    st.write(chemo_json["Day1"]["Premed"]["Note"])

    for instruction in chemo_json["Day1"]["Instructions"]:
        drug_name = instruction['Name']
        dosage = dosage_dict.get(drug_name, "dosage not specified")
        if dosage != "dosage not specified":
            st.write(f"{drug_name} {dosage} mg {instruction['Inst']}")
        else:
            st.write(f"{drug_name} dosage not specified {instruction['Inst']}")

    st.write(f" 5-fluorouracil v kontinuálnej pumpe: {round(rbodysurf * dos15FU)} mg over {day15FU}")




def calculate_bsa(weight, height):
    return (weight ** 0.425) * (height ** 0.725) * 0.007184


def main():
    st.title("Colorectal Cancer Chemotherapy Protocols")
    weight = st.number_input("Enter weight (kg):", min_value=1, max_value=200, value=70, step=1, format="%d")
    height = st.number_input("Enter height (cm):", min_value=1, max_value=250, value=170, step=1, format="%d")

    if st.button("Calculate BSA"):
        rbodysurf = calculate_bsa(weight, height)
        st.session_state['rbodysurf'] = rbodysurf
        st.write(f"Calculated Body Surface Area (BSA): {rbodysurf:.2f} m²")
    elif 'rbodysurf' in st.session_state:
        # Ensure BSA is displayed continuously once calculated, only from this condition
        st.write(f"Calculated Body Surface Area (BSA): {st.session_state['rbodysurf']:.2f} m²")

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
        "Irinotecan": "irinotecan.json",
        "FOLFIRINOX": "FOLFIRINOX.json"
    }

    selected_chemo = None
    if 'rbodysurf' in st.session_state:
        selected_chemo = st.selectbox("Select chemotherapy regimen:", list(chemo_options.keys()))

        if selected_chemo == "Cetuximab":
            ctx = st.radio("Is this the first administration of Cetuximab?", ('Yes', 'No'), key='cetuximab_admin')

    def execute_chemotherapy(option, cetuximab_first_admin=None):
        rbodysurf = st.session_state['rbodysurf']
        if option in ["FOLFOX", "FOLFIRI", "FOLFIRINOX"]:
            Chemo5FU(rbodysurf, chemo_options[option])
        elif option == "Cetuximab":
            cetuximab_file = "1cetuximab.json" if cetuximab_first_admin == 'Yes' else "elsecetuximab.json"
            Chemo(rbodysurf, cetuximab_file)
        elif "Bevacizumab" in option:
            ChemoMass(weight, chemo_options[option])
        else:
            Chemo(rbodysurf, chemo_options[option])

    if selected_chemo and st.button("Display Chemotherapy Protocol"):
        if selected_chemo == "Cetuximab":
            execute_chemotherapy(selected_chemo, cetuximab_first_admin=ctx)
        else:
            execute_chemotherapy(selected_chemo)

if __name__ == "__main__":
    main()

