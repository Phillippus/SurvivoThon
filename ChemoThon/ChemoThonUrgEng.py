import streamlit as st
import json
from sk_to_eng import sk_to_eng, show_evidence_eng

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
    st.title("ChemoThon Urogenital v. 3.2 ENG")
    st.write("""Welcome to ChemoThon! This application provides assistance in prescribing chemotherapy regimens based on body surface area (BSA), weight, or AUC for carboplatin-based treatments. Please ensure that doses are adjusted to align with the packaging and protocols available in your country. Users bear full responsibility for applying this tool in clinical practice.

We welcome your feedback to improve this app further. Feel free to reach out at filip.kohutek@fntn.sk.
""")

    data = load_chemotherapy_data()
    if not data:
        return

    weight = st.number_input("Enter weight (kg):", min_value=1, max_value=250, value=None, step=1)
    height = st.number_input("Enter height (cm):", min_value=1, max_value=250, value=None, step=1)

    if st.button("Calculate BSA") and weight and height:
        bsa_val = calculate_bsa(weight, height)
        st.session_state['bsa'] = bsa_val
        st.session_state['weight'] = weight

    if 'bsa' in st.session_state:
        st.write(f"Body Surface Area (BSA): {st.session_state['bsa']} m²")
        bsa = st.session_state['bsa']
        weight_val = st.session_state.get('weight', weight) or weight

        chemo_names = [protocol["name"] for protocol in data["chemotherapies"]]
        # New regimens (added 2026-06)
        extra_new = [
            "Enfortumab Vedotin + Pembrolizumab (EV-302, 1L metastatic urothelial)",
            "Olaparib 300 mg BID (HRR+ mCRPC, PROfound)",
            "Nivolumab 240 mg q2w adjuvant (high-risk urothelial post-cystectomy, CheckMate-274)",
            "Gemcitabine + Split-dose Cisplatin D1+D8 (urothelial)",
            "Paclitaxel weekly (urothelial / other)",
        ]
        selected_protocol_name = st.selectbox("Select a chemotherapy regimen:", [" "] + chemo_names + extra_new)

        auc = None
        crcl = None
        if "carboplatin" in selected_protocol_name.lower():
            crcl = st.number_input("Enter Creatinine Clearance (ml/min):", min_value=10, max_value=200, value=None, step=1)
            auc = st.number_input("Enter desired AUC (2-6):", min_value=2, max_value=6, value=None, step=1)

        if st.button("Display Protocol") and selected_protocol_name.strip():
            if selected_protocol_name == "Enfortumab Vedotin + Pembrolizumab (EV-302, 1L metastatic urothelial)":
                import json as _j
                ev = _j.load(open("data/enfortumab_vedotin.json", encoding="utf-8"))
                ev_dose = min(round(1.25 * weight_val, 2), 125)  # EV-302: cap at 125 mg (patients ≥100 kg)
                pembro_dose = 200
                ev_cap_note = " (capped at max 125 mg)" if 1.25 * weight_val > 125 else ""
                st.write("#### Chemotherapy Drugs")
                st.write(f"enfortumab vedotin 1.25 mg/kg ......... {ev_dose} mg D1, D8{ev_cap_note}")
                st.write(f"pembrolizumab 200 mg flat dose D1")
                st.write(f"**Next Cycle:** 21 days")
                st.write("#### D1 - Premedication")
                st.write(sk_to_eng(ev["Day1"]["Premed"]["Note"]))
                st.write("#### D1 - Chemotherapy Instructions")
                st.write(f"enfortumab vedotin {ev_dose} mg {sk_to_eng(ev['Day1']['Instructions'][0]['Inst'])}")
                st.write(f"pembrolizumab {pembro_dose} mg {sk_to_eng(ev['Day1']['Instructions'][1]['Inst'])}")
                show_evidence_eng(ev)
            elif selected_protocol_name == "Olaparib 300 mg BID (HRR+ mCRPC, PROfound)":
                display_simple_json("olaparib_crpc.json", bsa, weight_val)
            elif selected_protocol_name == "Nivolumab 240 mg q2w adjuvant (high-risk urothelial post-cystectomy, CheckMate-274)":
                display_simple_json("nivolumab_urothelial_adj.json", bsa, weight_val)
            elif selected_protocol_name == "Gemcitabine + Split-dose Cisplatin D1+D8 (urothelial)":
                total = round(70 * bsa, 2)
                half = round(total / 2, 2)
                gem_dose = round(1000 * bsa, 2)
                vials_d1 = int(half // 50)
                rem_d1 = round(half % 50, 2)
                st.write("#### Chemotherapy Drugs")
                st.write(f"gemcitabine 1000 mg/m² ......... {gem_dose} mg D1, D8")
                st.write(f"cisplatin 70 mg/m² total ......... {total} mg — split: {half} mg D1 + {half} mg D8")
                st.write("**Next Cycle:** 21 days")
                st.write("#### D1 - Premedication")
                st.write("Palonosetron 0.5mg/Netupitant 300mg (Akynzeo) p.o. 1h before chemo, Dexamethasone 12 mg i.v., Pantoprazole 40 mg p.o. Hydration: NaCl 500 ml before + 500 ml after. Repeat D8.")
                st.write("#### D1 (and D8) - Chemotherapy")
                st.write(f"gemcitabine {gem_dose} mg in 500 ml normal saline i.v./30 min (D1, D8)")
                for i in range(vials_d1):
                    st.write(f"cisplatin 50 mg in 500 ml normal saline i.v.")
                if rem_d1 > 0:
                    st.write(f"cisplatin {round(rem_d1, 2)} mg in 500 ml normal saline i.v.")
                st.write("Mannitol 10% 250 ml i.v.")
                st.write(f"*(Repeat on D8: gemcitabine {gem_dose} mg + cisplatin {half} mg split the same way)*")
            elif selected_protocol_name == "Paclitaxel weekly (urothelial / other)":
                display_simple_json("paclitaxelweekly.json", bsa, weight_val)
            else:
                protocol = next((p for p in data["chemotherapies"] if p["name"] == selected_protocol_name), None)
                if protocol:
                    display_chemotherapy_details(protocol, bsa, weight_val, auc=auc, crcl=crcl)
                else:
                    st.error("Selected protocol not found in the data.")

if __name__ == "__main__":
    main()



# ===== Zdroje / Sources (pridané 2026-06, aditívne) =====
with st.expander("📚 Zdroje k režimom / Sources"):
    st.markdown("""**Key references – genitourinary cancers**

Guidelines: [ESMO](https://www.esmo.org/guidelines/esmo-clinical-practice-guidelines-genitourinary-cancers) · [NCCN](https://www.nccn.org/guidelines/category_1). Always verify against the current guideline version and available drug vial sizes. As of: June 2026.

- **Docetaxel + prednizón (mCRPC)** — TAX327 – Tannock et al., NEJM 2004.
- **Mitoxantrón + prednizón** — Paliatívny – Tannock et al., J Clin Oncol 1996.
- **Docetaxel + darolutamid (mHSPC)** — ARASENS – Smith et al., NEJM 2022.
- **Kabazitaxel + prednizón** — TROPIC – de Bono et al., Lancet 2010; CARD – de Wit et al., NEJM 2019.
- **Abiraterón + prednizón (CRPC)** — COU-AA-301 – de Bono et al., NEJM 2011; COU-AA-302 – Ryan et al., NEJM 2013.
- **Abiraterón + prednizón (HSPC)** — LATITUDE – Fizazi et al., NEJM 2017; STAMPEDE – James et al., NEJM 2017.
- **Enzalutamid** — PREVAIL – Beer et al., NEJM 2014; ARCHES – Armstrong et al., J Clin Oncol 2019.
- **Darolutamid** — ARAMIS (nmCRPC) – Fizazi et al., NEJM 2019.
- **Apalutamid** — SPARTAN (nmCRPC) – Smith et al., NEJM 2018; TITAN (mHSPC) – Chi et al., NEJM 2019.
- **Cisplatina/karboplatina + gemcitabín (urotel)** — von der Maase et al., J Clin Oncol 2000/2005.
- **Vinflunín (urotel, 2. línia)** — Bellmunt et al., J Clin Oncol 2009.
- **BEP (germinatívne nádory)** — Williams et al., NEJM 1987; Einhorn – štandard.

**Current standards to consider (not yet in tool):**
- **Enfortumab vedotín + pembrolizumab 1. línia** — EV-302, NEJM 2024 → teraz v nástroji.
- Lutéciové [177Lu]Lu-PSMA-617 pri PSMA+ mCRPC – VISION, NEJM 2021.
- **Olaparib pri HRR-mutovanom mCRPC** — PROfound, NEJM 2020 → teraz v nástroji.
- **Nivolumab adjuvantne (vysokorizikový urotelový karcinóm)** — CheckMate-274, NEJM 2021 → teraz v nástroji.""")
