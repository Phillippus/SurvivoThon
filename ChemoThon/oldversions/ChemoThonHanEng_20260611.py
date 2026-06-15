import streamlit as st
import json

# --- Platinum + 5FU detailed regimen function ---
def platinum_5fu_detailed(rbodysurf):
    st.write("Platinum + 5-FU chemotherapy regimen")
    whichPt = st.selectbox("Select platinum:", ["Select", "Cisplatin", "Carboplatin"])
    if whichPt == "Cisplatin":
        ddp_dose = round(80 * rbodysurf, 2)
        fu_dose = round(1000 * rbodysurf, 2)
        full_units = int(ddp_dose // 50)
        remainder = round(ddp_dose % 50, 2)

        st.write(f"Cisplatin 80 mg/m² .......... {ddp_dose} mg D1")
        st.write(f"5-Fluorouracil 1000 mg/m² .......... {fu_dose} mg D1–D4")
        st.write("Next Cycle: 21 days\n\nD1 - Premedication:")
        st.write("1. Dexametazon 8mg iv, Pantoprazol 40 mg p.o., Ondansetron 8mg in 250ml NS iv")

        item_no = 2
        for i in range(full_units):
            st.write(f"{item_no}. Cisplatina 50mg v 500ml RR iv")
            item_no += 1
        if remainder > 0:
            st.write(f"{item_no}. Cisplatina {remainder} mg v 500ml RR iv")
            item_no += 1

        st.write(f"{item_no}. Manitol 10% 250ml iv")
        item_no += 1
        st.write(f"{item_no}. 5-fluoruracil {fu_dose} mg na 24 hodín/kivi")
    elif whichPt == "Carboplatin":
        CrCl = st.number_input("Enter creatinine clearance (ml/min):", min_value=1, max_value=250, value=None)
        AUC = st.number_input("Enter AUC (2–6):", min_value=2, max_value=6, value=None)
        if CrCl and AUC:
            cbdca_dose = round((CrCl + 25) * AUC, 2)
            fu_dose = round(1000 * rbodysurf, 2)
            st.write(f"Carboplatin AUC {AUC} .......... {cbdca_dose} mg D1")
            st.write(f"5-Fluorouracil 1000 mg/m² .......... {fu_dose} mg D1–D4")
            st.write("Next Cycle: 21 days\n\nD1 - Premedication:\nDexamethasone 8mg i.v., Pantoprazole 40mg p.o., Ondansetron 8mg in 250ml NS i.v.")
            st.write(f"D1 - Chemotherapy:\nCarboplatin {cbdca_dose} mg\n5-FU {fu_dose} mg continuous infusion over 24 hours")

def pt_5fu_cisplatin(bsa, weight):
    ddp_dose = round(80 * bsa, 2)
    fu_dose = round(1000 * bsa, 2)
    st.write("### Protocol: Pt/5-FU cisplatin-based")
    st.write("#### Chemotherapy Drugs")
    st.write(f"cisplatin 80 mg/m2 ......... {ddp_dose} mg D 1")
    st.write(f"fluorouracil 1000 mg/m2 ......... {fu_dose} mg D 1-4")
    st.write("**Next Cycle:** 21 days")
    st.write("#### D1 - Premedication")
    st.write("Dexamethasone 8mg iv, Pantoprazole 40mg p.o., Ondansetron 8mg in 250ml NS iv")
    # Updated D1 - Chemotherapy Instructions
    st.write("#### D1 - Chemotherapy Instructions")
    item_no = 1
    st.write(f"{item_no}. Dexametazón 8mg iv, Pantoprazol 40 mg p.o., Ondansetron 8mg v 250ml FR iv")
    item_no += 1
    full_units = int(ddp_dose // 50)
    remainder = round(ddp_dose % 50, 2)
    for _ in range(full_units):
        st.write(f"{item_no}. Cisplatina 50mg v 500ml RR iv")
        item_no += 1
    if remainder > 0:
        st.write(f"{item_no}. Cisplatina {remainder} mg v 500ml RR iv")
        item_no += 1
    st.write(f"{item_no}. Manitol 10% 250ml iv")
    item_no += 1
    st.write(f"{item_no}. 5-fluoruracil {fu_dose} mg na 24 hodín/kivi")

def pt_5fu_carboplatin(bsa, weight):
    CrCl = st.number_input("Enter creatinine clearance (ml/min):", min_value=1, max_value=250, value=60, step=1)
    AUC = st.number_input("Enter AUC (2–6):", min_value=2, max_value=6, value=5, step=1)
    
    cbdca_dose = round((CrCl + 25) * AUC, 2)
    fu_dose = round(1000 * bsa, 2)
    st.write("### Protocol: Pt/5-FU carboplatin-based")
    st.write("#### Chemotherapy Drugs")
    st.write(f"carboplatin AUC {AUC} ......... {cbdca_dose} mg D 1")
    st.write(f"fluorouracil 1000 mg/m2 ......... {fu_dose} mg D 1-4")
    st.write("**Next Cycle:** 21 days")
    st.write("#### D1 - Premedication")
    st.write("Dexamethasone 8mg iv, Pantoprazole 40mg p.o., Ondansetron 8mg in 250ml NS iv")
    st.write("#### D1 - Chemotherapy Instructions")
    st.write(f"carboplatin - {cbdca_dose}mg")
    st.write(f"fluorouracil - {fu_dose}mg, administered continuously over 24 hours via elastomeric pump")

def load_chemotherapy_data():
    """Loads all chemotherapy data from the consolidated JSON file."""
    try:
        with open('data/chemotherapyHANENG.json', 'r') as file:
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
            if "Dosage" not in drug:
                st.warning(f"Missing dosage for drug: {drug.get('Name', 'Unknown')}")
                continue
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
            # Special handling for Pt/5-FU cisplatin-based regimen
            if protocol["name"] == "Pt/5-FU cisplatin-based":
                # Find cisplatin drug to get dose
                cisplatin_drug = next((d for d in protocol["Chemo"] if d["Name"].lower() == "cisplatin"), None)
                if cisplatin_drug:
                    if isinstance(cisplatin_drug["Dosage"], str) and "/" in cisplatin_drug["Dosage"]:
                        try:
                            dose_parts = [float(part) for part in cisplatin_drug["Dosage"].split("/")]
                            dose = round(dose_parts[0] * bsa, 2)
                        except Exception:
                            dose = "N/A"
                    elif cisplatin_drug["DosageMetric"] == "mg/m2":
                        dose = round(cisplatin_drug["Dosage"] * bsa, 2)
                    elif cisplatin_drug["DosageMetric"] == "mg/kg":
                        try:
                            dose = round(float(cisplatin_drug["Dosage"]) * weight, 2)
                        except Exception:
                            dose = "N/A"
                    else:
                        try:
                            dose = round(float(cisplatin_drug["Dosage"]), 2)
                        except Exception:
                            dose = "N/A"
                else:
                    dose = "N/A"
                st.write(f"cisplatin - {dose}mg, administer 50mg cisplatin in 500ml RR iv repeatedly until full dose is reached; follow final infusion with 250ml Mannitol 10% iv")
                # Also display other instructions if any
                for instruction in protocol["Day1"]["Instructions"]:
                    instruction_text = instruction.get("Instruction", "No instructions available.").replace("tablet", "pill")
                    drug_name = instruction.get("Name", "Unknown")
                    if drug_name.lower() != "cisplatin":
                        st.write(f"{drug_name} - {instruction_text}")
            else:
                for instruction in protocol["Day1"]["Instructions"]:
                    instruction_text = instruction.get("Instruction", "No instructions available.").replace("tablet", "pill")
                    drug_name = instruction.get("Name", "Unknown")
                    # Calculate Day 1 dose
                    drug = next((d for d in protocol["Chemo"] if d["Name"] == drug_name), None)
                    if drug:
                        if "Dosage" not in drug:
                            dose = "N/A"
                        elif isinstance(drug["Dosage"], str) and "/" in drug["Dosage"]:
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
    st.title("ChemoThon Head and Neck v. 3.0 ENG")
    st.write("""Welcome to ChemoThon!
This application provides assistance in prescribing chemotherapy regimens based on body surface area (BSA) or weight.
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
        chemo_list = data if isinstance(data, list) else data.get("chemotherapies", [])
        chemo_names = [protocol["name"] for protocol in chemo_list]

        # Remove "Pt/5-FU cisplatin-based" and "Pt/5-FU carboplatin-based" from chemo_names if present
        chemo_names = [name for name in chemo_names if name not in ["Pt/5-FU cisplatin-based", "Pt/5-FU carboplatin-based"]]

        # Remove individual Cetuximab weekly options if present
        chemo_names = [name for name in chemo_names if name not in ["Cetuximab weekly (first)", "Cetuximab weekly (subsequent)"]]

        # Add manual placeholder names for platinum + 5FU regimens and Cetuximab if not present in data
        if "Pt/5-FU" not in chemo_names:
            chemo_names.append("Pt/5-FU")
        if "Cetuximab weekly" not in chemo_names:
            chemo_names.append("Cetuximab weekly")
        if "Cetuximab biweekly" not in chemo_names:
            chemo_names.append("Cetuximab biweekly")

        # Sorting logic: non-biological first, then biological
        def is_biological(name):
            name_lower = name.lower()
            return any(keyword in name_lower for keyword in ["trastuzumab", "pertuzumab", "govitecan", "deruxtecan", "td-m1"])

        chemo_names_sorted = sorted([name for name in chemo_names if not is_biological(name)])
        bio_names_sorted = sorted([name for name in chemo_names if is_biological(name)])
        sorted_names = chemo_names_sorted + bio_names_sorted

        selected_protocol_name = st.selectbox("Select a chemotherapy regimen:", sorted_names)

        # Add sub-options for specific regimens
        sub_option = None
        if selected_protocol_name == "Cetuximab weekly":
            sub_option = st.radio("Select Cetuximab administration type:", ["First administration (400mg/m²)", "Subsequent administration (250mg/m²)"])
        elif selected_protocol_name == "Pt/5-FU":
            sub_option = st.radio("Select platinum type:", ["Cisplatin", "Carboplatin"])

        if st.button("Display Protocol") and weight:
            if selected_protocol_name == "Pt/5-FU":
                if sub_option == "Cisplatin":
                    pt_5fu_cisplatin(bsa, weight)
                elif sub_option == "Carboplatin":
                    pt_5fu_carboplatin(bsa, weight)
                else:
                    st.error("Please select a platinum type.")
                    return
            else:
                if selected_protocol_name == "Cetuximab weekly":
                    if sub_option:
                        if "First" in sub_option:
                            protocol_name_to_lookup = "Cetuximab weekly (first)"
                        else:
                            protocol_name_to_lookup = "Cetuximab weekly (subsequent)"
                    else:
                        st.error("Please select Cetuximab administration type.")
                        return
                else:
                    protocol_name_to_lookup = selected_protocol_name

                protocol = next((p for p in chemo_list if p["name"] == protocol_name_to_lookup), None)
                if protocol:
                    display_chemotherapy_details(protocol, bsa, weight)
                else:
                    st.error("Selected protocol not found in the data.")
        elif not weight:
            st.error("Please enter a weight to calculate the chemotherapy protocol.")

if __name__ == "__main__":
    main()