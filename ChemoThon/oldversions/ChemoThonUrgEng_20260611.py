import streamlit as st
import json

def load_chemotherapy_data():
    try:
        with open('data/chemotherapyUGENG.json', 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        st.error("Chemotherapy data file not found. Please ensure it's in the 'data' directory.")
        return None
    except json.JSONDecodeError:
        st.error("Error decoding JSON. Please check the file format.")
        return None

def calculate_bsa(weight, height):
    return round((weight**0.425) * (height**0.725) * 0.007184, 2)

def calculate_cbdca_dose(auc, crcl):
    return int((crcl + 25) * auc)

def split_cisplatin_dose(total_dose):
    full_doses = int(total_dose) // 50
    remainder = round(total_dose - (full_doses * 50), 1)
    parts = ["50 mg in 500 ml RR iv"] * full_doses
    if remainder > 0:
        parts.append(f"{remainder} mg in 500 ml RR iv")
    return parts

def display_chemotherapy_details(protocol, bsa, weight, auc=None, crcl=None):
    st.write(f"### Protocol: {protocol['name']}")

    st.write("#### Chemotherapy Drugs")
    seen = set()
    for drug in protocol["Chemo"]:
        key = (drug['Name'], drug['Dosage'], drug['DosageMetric'], drug['Day'])
        if key in seen:
            continue
        seen.add(key)
        metric = drug["DosageMetric"]
        dose = drug["Dosage"]
        if "mg/kg" in metric:
            calculated = round(dose * weight, 2)
        elif "mg/m2" in metric:
            calculated = round(dose * bsa, 2)
        elif "AUC" in metric and auc is not None and crcl is not None:
            calculated = calculate_cbdca_dose(auc, crcl)
        else:
            calculated = round(dose, 2)
        st.write(f"{drug['Name']} {dose} {metric} ......... {calculated} mg D {drug['Day']}")

    st.write(f"**Next Cycle:** {protocol.get('NextCycle', 'Unknown')} days")

    if "Day1" in protocol:
        st.write("#### D1 - Premedication")
        st.write(protocol["Day1"]["Premed"].get("Note", "No premedication details available."))

        if "Instructions" in protocol["Day1"]:
            st.write("#### D1 - Chemotherapy Instructions")
            for instr in protocol["Day1"]["Instructions"]:
                name = instr.get("Name", "Unknown")
                text = instr.get("Instruction", "No instructions available.")
                drug = next((d for d in protocol["Chemo"] if d["Name"] == name), None)
                if drug:
                    if "mg/kg" in drug["DosageMetric"]:
                        calc_dose = round(drug["Dosage"] * weight, 2)
                    elif "mg/m2" in drug["DosageMetric"]:
                        calc_dose = round(drug["Dosage"] * bsa, 2)
                    elif "AUC" in drug["DosageMetric"] and auc is not None and crcl is not None:
                        calc_dose = calculate_cbdca_dose(auc, crcl)
                    else:
                        calc_dose = round(drug["Dosage"], 2)

                    if "cisplatin" in name.lower():
                        parts = split_cisplatin_dose(calc_dose)
                        for part in parts:
                            st.write(f"{name} - {part}")
                        st.write("Mannitol 10% 250 ml iv")
                    elif "gemcitabine" in name.lower():
                        st.write(f"{name} - {calc_dose} mg in 500 ml NS iv")
                    elif str(calc_dose) in text:
                        st.write(f"{name} - {text}")
                    else:
                        st.write(f"{name} - {calc_dose} mg, {text}")
                else:
                    st.write(f"{name} - {text}")
        else:
            st.warning("No instructions available for Day 1.")
    else:
        st.warning("No details found for Day 1.")

def main():
    st.title("ChemoThon Urogenital v. 3.0 ENG")
    st.write("""Welcome to ChemoThon! This application provides assistance in prescribing chemotherapy regimens based on body surface area (BSA), weight, or AUC for carboplatin-based treatments. Please ensure that doses are adjusted to align with the packaging and protocols available in your country. Users bear full responsibility for applying this tool in clinical practice.

We welcome your feedback to improve this app further. Feel free to reach out at filip.kohutek@fntn.sk.
""")

    data = load_chemotherapy_data()
    if not data:
        return

    weight = st.number_input("Enter weight (kg):", min_value=1, max_value=250, value=None, step=1)
    height = st.number_input("Enter height (cm):", min_value=1, max_value=250, value=None, step=1)

    bsa = None
    auc = None
    crcl = None

    if weight and height:
        bsa = calculate_bsa(weight, height)
        st.write(f"Body Surface Area: {bsa} m²")

    chemo_names = [protocol["name"] for protocol in data["chemotherapies"]]
    selected_protocol_name = st.selectbox("Select a chemotherapy regimen:", [" "] + chemo_names)

    if "carboplatin" in selected_protocol_name.lower():
        crcl = st.number_input("Enter Creatinine Clearance (ml/min):", min_value=10, max_value=200, value=None, step=1)
        auc = st.number_input("Enter desired AUC (2-6):", min_value=2, max_value=6, value=None, step=1)

    if st.button("Display Protocol") and bsa and selected_protocol_name.strip():
        protocol = next((p for p in data["chemotherapies"] if p["name"] == selected_protocol_name), None)
        if protocol:
            display_chemotherapy_details(protocol, bsa, weight, auc=auc, crcl=crcl)
        else:
            st.error("Selected protocol not found in the data.")

if __name__ == "__main__":
    main()