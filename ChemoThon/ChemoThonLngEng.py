import streamlit as st
import json
from sk_to_eng import sk_to_eng, show_evidence_eng

def calculate_bsa(weight, height):
    """Calculates body surface area using the DuBois formula."""
    return round((weight**0.425) * (height**0.725) * 0.007184, 2)

def Chemo(bsa, filename):
    """Display simple BSA-based chemotherapy from individual JSON file."""
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
        if "mg/m2" in metric:
            calculated = round(dosage * bsa, 2)
            st.write(f"{drug['Name']} {dosage} {metric} ......... {calculated} mg D{drug['Day']}")
        else:
            st.write(f"{drug['Name']} {dosage} {metric} D{drug['Day']}")
    st.write(f"**Next Cycle:** {reg.get('NC', '?')} days")
    premed = reg.get("Day1", {}).get("Premed", {}).get("Note", "")
    if premed:
        st.write("#### D1 - Premedication")
        st.write(sk_to_eng(premed))
    instructions = reg.get("Day1", {}).get("Instructions", [])
    if instructions:
        st.write("#### D1 - Chemotherapy")
        chemo_list = reg.get("Chemo", [])
        for inst in instructions:
            drug_name = inst.get("Name", "")
            inst_text = sk_to_eng(inst.get("Inst", ""))
            drug = next((d for d in chemo_list if d["Name"] == drug_name), None)
            if drug:
                metric = drug.get("DosageMetric", "")
                dosage = drug.get("Dosage", 0)
                calc_dose = round(dosage * bsa, 2) if "mg/m2" in metric else dosage
                st.write(f"{drug_name} {calc_dose} mg {inst_text}")
            else:
                st.write(f"{drug_name} {inst_text}")
    show_evidence_eng(reg)

def ChemoDDP(bsa, filename):
    """Display cisplatin-based regimen (split 50 mg per infusion + mannitol)."""
    try:
        with open(f'data/{filename}', 'r') as f:
            reg = json.load(f)
    except Exception as e:
        st.error(f"Error loading {filename}: {e}")
        return
    ddp_dose = round(80 * bsa, 2)
    full_units = int(ddp_dose // 50)
    remainder = round(ddp_dose % 50, 2)
    st.write("#### Chemotherapy Drugs")
    st.write(f"Cisplatin 80 mg/m² ......... {ddp_dose} mg D1")
    for drug in reg.get("Chemo", []):
        calculated = round(drug["Dosage"] * bsa, 2)
        st.write(f"{drug['Name']} {drug['Dosage']} {drug['DosageMetric']} ......... {calculated} mg D{drug['Day']}")
    st.write(f"**Next Cycle:** {reg.get('NC', '?')} days")
    premed = reg.get("Day1", {}).get("Premed", {}).get("Note", "")
    if premed:
        st.write("#### D1 - Premedication")
        st.write(sk_to_eng(premed))
    st.write("#### D1 - Chemotherapy")
    item = 1
    for _ in range(full_units):
        st.write(f"{item}. Cisplatin 50 mg in 500 ml normal saline iv")
        item += 1
    if remainder > 0:
        st.write(f"{item}. Cisplatin {remainder} mg in 500 ml normal saline iv")
        item += 1
    st.write(f"{item}. Mannitol 10% 250 ml iv")
    item += 1
    chemo_list = reg.get("Chemo", [])
    for inst in reg.get("Day1", {}).get("Instructions", []):
        drug_name = inst.get("Name", "")
        drug = next((d for d in chemo_list if d["Name"] == drug_name), None)
        if drug:
            calc_dose = round(drug["Dosage"] * bsa, 2)
            st.write(f"{item}. {drug_name} {calc_dose} mg {sk_to_eng(inst.get('Inst', ''))}") 
            item += 1
    show_evidence_eng(reg)

def ChemoCBDCA(bsa, filename):
    """Display carboplatin-based regimen (AUC-based dosing)."""
    try:
        with open(f'data/{filename}', 'r') as f:
            reg = json.load(f)
    except Exception as e:
        st.error(f"Error loading {filename}: {e}")
        return
    crcl = st.number_input("Enter Creatinine Clearance (CrCl, ml/min):", min_value=1, max_value=250, value=None, step=1)
    auc = st.number_input("Enter AUC (2–6):", min_value=2, max_value=6, value=None, step=1)
    if crcl is not None and auc is not None:
        if crcl < 30:
            st.error("⚠️ Patient may be platinum-ineligible (CrCl < 30 ml/min)!")
        cbdca_dose = (crcl + 25) * auc
        st.write("#### Chemotherapy Drugs")
        st.write(f"Carboplatin AUC {auc} ......... {cbdca_dose} mg D1")
        for drug in reg.get("Chemo", []):
            metric = drug.get("DosageMetric", "mg/m2")
            dose = drug["Dosage"] if "flat" in metric.lower() else round(drug["Dosage"] * bsa, 2)
            st.write(f"{drug['Name']} {drug['Dosage']} {metric} ......... {dose} mg D{drug['Day']}")
        st.write(f"**Next Cycle:** {reg.get('NC', '?')} days")
        premed = reg.get("Day1", {}).get("Premed", {}).get("Note", "")
        if premed:
            st.write("#### D1 - Premedication")
            st.write(sk_to_eng(premed))
        st.write("#### D1 - Chemotherapy")
        st.write(f"Carboplatin {cbdca_dose} mg in 500 ml glucose 5% iv over 30–60 min")
        chemo_list = reg.get("Chemo", [])
        for inst in reg.get("Day1", {}).get("Instructions", []):
            drug_name = inst.get("Name", "")
            drug = next((d for d in chemo_list if d["Name"] == drug_name), None)
            if drug:
                metric = drug.get("DosageMetric", "mg/m2")
                calc_dose = drug["Dosage"] if "flat" in metric.lower() else round(drug["Dosage"] * bsa, 2)
                st.write(f"{drug_name} {calc_dose} mg {sk_to_eng(inst.get('Inst', ''))}")
        show_evidence_eng(reg)

def lung(bsa, weight=None):
    """Lung cancer chemotherapy regimen selector."""
    chemo_choice = st.selectbox("Select chemotherapy:", [
        " ",
        # --- Chemotherapy doublets ---
        "Carboplatin + Paclitaxel",
        "Carboplatin + Pemetrexed (non-squamous NSCLC)",
        "Cisplatin + Gemcitabine",
        "Carboplatin + Gemcitabine",
        "Cisplatin + Etoposide (SCLC)",
        "Topotecan + G-CSF (SCLC 2nd line)",
        # --- Immunotherapy combinations (added 2026-06) ---
        "Pembrolizumab + Pemetrexed + Carboplatin (non-squamous NSCLC, KEYNOTE-189)",
        "Pembrolizumab + Carboplatin + Nab-Paclitaxel (squamous NSCLC, KEYNOTE-407)",
        "Durvalumab 1500 mg flat q4w (stage III NSCLC maintenance after CRT, PACIFIC)",
        "Atezolizumab + Etoposide + Carboplatin (SCLC 1st line, IMpower133)",
        # --- Added 2026-06 ---
        "Platinum + Vinorelbine (adjuvant NSCLC, IALT/ANITA)",
    ])

    if chemo_choice == "Carboplatin + Paclitaxel":
        ChemoCBDCA(bsa, "paclitaxel3weekly.json")
    elif chemo_choice == "Carboplatin + Pemetrexed (non-squamous NSCLC)":
        ChemoCBDCA(bsa, "pemetrexed.json")
    elif chemo_choice == "Cisplatin + Gemcitabine":
        ChemoDDP(bsa, "gemcitabinDDP.json")
    elif chemo_choice == "Carboplatin + Gemcitabine":
        ChemoCBDCA(bsa, "gemcitabinCBDCA.json")
    elif chemo_choice == "Cisplatin + Etoposide (SCLC)":
        ChemoDDP(bsa, "etoposide.json")
    elif chemo_choice == "Topotecan + G-CSF (SCLC 2nd line)":
        Chemo(bsa, "topotecan.json")
    elif chemo_choice == "Pembrolizumab + Pemetrexed + Carboplatin (non-squamous NSCLC, KEYNOTE-189)":
        ChemoCBDCA(bsa, "pembrolizumab_pem_cbdca.json")
    elif chemo_choice == "Pembrolizumab + Carboplatin + Nab-Paclitaxel (squamous NSCLC, KEYNOTE-407)":
        ChemoCBDCA(bsa, "pembrolizumab_cbdca_nab.json")
    elif chemo_choice == "Durvalumab 1500 mg flat q4w (stage III NSCLC maintenance after CRT, PACIFIC)":
        Chemo(bsa, "durvalumab_pacific.json")
    elif chemo_choice == "Atezolizumab + Etoposide + Carboplatin (SCLC 1st line, IMpower133)":
        ChemoCBDCA(bsa, "atezolizumab_ep.json")
    elif chemo_choice == "Platinum + Vinorelbine (adjuvant NSCLC, IALT/ANITA)":
        pt_adj = st.selectbox("Select platinum:", [
            "Choose", "Cisplatin 80 mg/m² D1 (IALT/ANITA standard)", "Carboplatin AUC 5-6 D1 (alternative)"
        ], key="pt_adj_vin")
        if pt_adj == "Cisplatin 80 mg/m² D1 (IALT/ANITA standard)":
            vin_dose = round(25 * bsa, 2)
            ddp_dose = round(80 * bsa, 2)
            ddp_vials = int(ddp_dose // 50)
            ddp_rem = round(ddp_dose % 50, 2)
            import json as _j
            vn = _j.load(open("data/vinorelbine_ddp_adj.json", encoding="utf-8"))
            st.write("#### Chemotherapy Drugs")
            st.write(f"cisplatin 80 mg/m² ......... {ddp_dose} mg D1")
            st.write(f"vinorelbine 25 mg/m² ......... {vin_dose} mg D1, D8")
            st.write("**Next Cycle:** 28 days")
            st.write("#### D1 - Premedication")
            st.write(sk_to_eng(vn["Day1"]["Premed"]["Note"]))
            st.write("#### D1 - Chemotherapy")
            for i in range(ddp_vials):
                st.write(f"cisplatin 50 mg in 500 ml normal saline i.v.")
            if ddp_rem > 0:
                st.write(f"cisplatin {round(ddp_rem, 2)} mg in 500 ml normal saline i.v.")
            st.write("Mannitol 10% 250 ml i.v.")
            st.write(f"vinorelbine {vin_dose} mg in 125 ml NaCl i.v./10 min D1, D8")
            show_evidence_eng(vn)
        elif pt_adj == "Carboplatin AUC 5-6 D1 (alternative)":
            crcl_a = st.number_input("Creatinine Clearance (ml/min):", min_value=1, max_value=250, value=None, key="crcl_adj")
            auc_a = st.number_input("AUC (5 or 6):", min_value=4, max_value=6, value=5, key="auc_adj")
            vin_dose = round(25 * bsa, 2)
            if crcl_a is not None:
                cbdca_dose = (crcl_a + 25) * auc_a
                import json as _j
                vn = _j.load(open("data/vinorelbine_cbdca_adj.json", encoding="utf-8"))
                st.write("#### Chemotherapy Drugs")
                st.write(f"carboplatin AUC {auc_a} ......... {cbdca_dose} mg D1")
                st.write(f"vinorelbine 25 mg/m² ......... {vin_dose} mg D1, D8")
                st.write("**Next Cycle:** 28 days")
                st.write("#### D1 - Premedication")
                st.write(sk_to_eng(vn["Day1"]["Premed"]["Note"]))
                st.write("#### D1 - Chemotherapy")
                st.write(f"carboplatin {cbdca_dose} mg in 500 ml glucose 5% i.v./60 min")
                st.write(f"vinorelbine {vin_dose} mg in 125 ml NaCl i.v./10 min D1, D8")
                show_evidence_eng(vn)

def main():
    st.title("ChemoThon Lung ENG v 2.3")
    st.write("""Welcome to ChemoThon!
This application provides assistance in prescribing chemotherapy regimens based on body surface area (BSA).
Please ensure doses are adjusted to align with packaging and protocols available in your country. Users bear full responsibility for applying this tool in clinical practice.
Immunotherapy can be found at https://immunothoneng.streamlit.app

We welcome your feedback. Feel free to reach out at filip.kohutek@fntn.sk.""")

    weight = st.number_input("Enter weight (kg):", min_value=1, max_value=250, value=None, step=1)
    height = st.number_input("Enter height (cm):", min_value=1, max_value=250, value=None, step=1)

    if st.button("Calculate BSA") and weight and height:
        bsa_val = calculate_bsa(weight, height)
        st.session_state['bsa'] = bsa_val
        st.session_state['weight'] = weight
        st.session_state['show_chemo'] = True

    if 'bsa' in st.session_state:
        st.write(f"Body Surface Area (BSA): {st.session_state['bsa']} m²")

    if st.session_state.get("show_chemo", False):
        lung(st.session_state['bsa'], st.session_state.get('weight'))

if __name__ == "__main__":
    main()



# ===== Sources =====
with st.expander("📚 Key References"):
    st.markdown("""**Key references – lung cancer**

Guidelines: [ESMO](https://www.esmo.org/guidelines/esmo-clinical-practice-guidelines-lung-and-chest-tumours) · [NCCN](https://www.nccn.org/guidelines/category_1). Always verify against the current guideline version and available drug vial sizes. As of: June 2026.

- **Carboplatin / paclitaxel** — ECOG 1594 – Schiller et al., NEJM 2002.
- **Cisplatin / pemetrexed (non-squamous)** — Scagliotti et al., J Clin Oncol 2008.
- **Gemcitabine / cisplatin** — ECOG 1594; standard platinum doublet.
- **Gemcitabine / carboplatin** — Platinum doublet in NSCLC – NCCN NSCLC.
- **Etoposide / platinum (SCLC)** — Standard for SCLC.
- **Topotecan (SCLC 2nd line)** — O'Brien et al., J Clin Oncol 2006.

**New regimens (2026-06):**
- **Pembrolizumab + pemetrexed + carboplatin (KEYNOTE-189)** — Gandhi et al., NEJM 2018 → now in tool.
- **Pembrolizumab + carboplatin + nab-paclitaxel (KEYNOTE-407)** — Paz-Ares et al., NEJM 2018 → now in tool.
- **Durvalumab maintenance stage III NSCLC (PACIFIC)** — Antonia et al., NEJM 2017/2018 → now in tool.
- **Atezolizumab + etoposide + carboplatin (IMpower133)** — Horn et al., NEJM 2018 → now in tool.

Note: For EGFR/ALK/ROS1 and other targetable mutations, targeted therapy takes precedence over chemotherapy (osimertinib, alectinib, etc.).""")
