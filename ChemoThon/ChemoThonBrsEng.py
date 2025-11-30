import streamlit as st
import json

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

def main():
    st.title("ChemoThon Breast v. 3.2 ENG")
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
        bsa = calculate_bsa(weight, height)
        st.session_state['bsa'] = bsa
        st.write(f"Body Surface Area: {bsa} m²")

    if not weight or not height:
        st.warning("Please enter both weight and height to calculate BSA.")
        return

    # Select chemotherapy regimen
    if 'bsa' in st.session_state:
        bsa = st.session_state['bsa']
        chemo_names = [protocol["name"] for protocol in data.get("chemotherapies", [])]
        # Sorting logic: non-biological first, then biological
        def is_biological(name):
            name_lower = name.lower()
            return any(keyword in name_lower for keyword in ["trastuzumab", "pertuzumab", "govitecan", "deruxtecan", "td-m1"])

        chemo_names = [protocol["name"] for protocol in data.get("chemotherapies", [])]
        chemo_names_sorted = sorted([name for name in chemo_names if not is_biological(name)])
        bio_names_sorted = sorted([name for name in chemo_names if is_biological(name)])
        sorted_names = chemo_names_sorted + bio_names_sorted

        selected_protocol_name = st.selectbox("Select a chemotherapy regimen:", sorted_names)

        if st.button("Display Protocol") and weight:
            protocol = next((p for p in data["chemotherapies"] if p["name"] == selected_protocol_name), None)
            if protocol:
                display_chemotherapy_details(protocol, bsa, weight)
            else:
                st.error("Selected protocol not found in the data.")
        elif not weight:
            st.error("Please enter a weight to calculate the chemotherapy protocol.")

if __name__ == "__main__":
    main()