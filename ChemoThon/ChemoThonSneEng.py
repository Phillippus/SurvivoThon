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
    """Display cisplatin-based regimen (80 mg/m², split 50 mg + mannitol)."""
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
    """Display carboplatin-based regimen (AUC dosing)."""
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
            calculated = round(drug["Dosage"] * bsa, 2)
            st.write(f"{drug['Name']} {drug['Dosage']} {drug['DosageMetric']} ......... {calculated} mg D{drug['Day']}")
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
                calc_dose = round(drug["Dosage"] * bsa, 2)
                st.write(f"{drug_name} {calc_dose} mg {sk_to_eng(inst.get('Inst', ''))}") 
        show_evidence_eng(reg)

def ChemoIfo(bsa, dose_per_m2, with_epirubicin):
    """Ifosfamide regimen with MESNA and optional epirubicin."""
    ifo = int(dose_per_m2 * bsa)
    mesna = ifo * 0.8
    ifo_cycles = ifo // 2000
    mesna_init = 1200

    if with_epirubicin:
        st.write(f"Epirubicin 60 mg/m² ......... {round(60 * bsa, 2)} mg D1, D2")
    st.write(f"Ifosfamide {dose_per_m2} mg/m² ......... {ifo} mg D1–D3")
    st.write(f"MESNA (80% ifosfamide) ......... {round(mesna, 2)} mg D1–D3")
    st.write("**Next Cycle:** 21 days")
    st.write("#### D1 - Premedication")
    st.write("Ondansetron 8 mg iv, Dexamethasone 8 mg iv, Pantoprazole 40 mg p.o.")
    st.write("#### D1 - Chemotherapy")
    if with_epirubicin:
        st.write(f"Epirubicin {round(60 * bsa, 2)} mg in 500 ml NS iv")
    st.write(f"MESNA {mesna_init} mg in 100 ml NS iv (loading, before ifosfamide)")
    ifo_remnant = ifo % 2000
    mesnacont = round((mesna - 1200) / max(ifo_cycles, 1), 2)
    for _ in range(ifo_cycles):
        st.write(f"Ifosfamide 2000 mg in 500 ml NS iv")
        st.write(f"MESNA {mesnacont} mg in 100 ml NS iv every 4 h")
    if ifo_remnant > 200:
        st.write(f"Ifosfamide {ifo_remnant} mg in 500 ml NS iv")
        st.write("MESNA 800 mg in 100 ml NS iv every 4 h")

def sarcnet(bsa):
    """Sarcoma, CNS and NET regimen selector."""
    chemo_choice = st.selectbox("Select chemotherapy:", [
        " ",
        # --- Sarcoma ---
        "Ifosfamide + Epirubicin (3000 mg/m²)",
        "Ifosfamide monotherapy (3000 mg/m²)",
        "Trabectedin",
        "Doxorubicin",
        "Paclitaxel weekly (angiosarcoma)",
        "Carboplatin + Paclitaxel",
        # --- CNS / NET ---
        "Cisplatin + Etoposide",
        "Carboplatin + Etoposide",
        "Dacarbazine (5-day)",
        # --- Temozolomide sub-options ---
        "Temozolomide (concurrent with RT, 75 mg/m² daily)",
        "Temozolomide monotherapy 150 mg/m²",
        "Temozolomide monotherapy 200 mg/m²",
        "Lomustine (CCNU)",
        # --- New (2026-06) ---
        "CAPTEM (Capecitabine + Temozolomide, pNET, E2211)",
        "Pazopanib 800 mg/day (STS, PALETTE)",
    ])

    if chemo_choice == "Ifosfamide + Epirubicin (3000 mg/m²)":
        ChemoIfo(bsa, 3000, True)
    elif chemo_choice == "Ifosfamide monotherapy (3000 mg/m²)":
        ChemoIfo(bsa, 3000, False)
    elif chemo_choice == "Trabectedin":
        Chemo(bsa, "trabectedin.json")
    elif chemo_choice == "Doxorubicin":
        Chemo(bsa, "doxorubicin.json")
    elif chemo_choice == "Paclitaxel weekly (angiosarcoma)":
        Chemo(bsa, "paclitaxelweekly.json")
    elif chemo_choice == "Carboplatin + Paclitaxel":
        ChemoCBDCA(bsa, "paclitaxel3weekly.json")
    elif chemo_choice == "Cisplatin + Etoposide":
        ChemoDDP(bsa, "etoposide.json")
    elif chemo_choice == "Carboplatin + Etoposide":
        ChemoCBDCA(bsa, "etoposide.json")
    elif chemo_choice == "Dacarbazine (5-day)":
        Chemo(bsa, "dacarbazine.json")
    elif chemo_choice == "Temozolomide (concurrent with RT, 75 mg/m² daily)":
        Chemo(bsa, "temozolomideRAT.json")
    elif chemo_choice == "Temozolomide monotherapy 150 mg/m²":
        Chemo(bsa, "temozolomide150.json")
    elif chemo_choice == "Temozolomide monotherapy 200 mg/m²":
        Chemo(bsa, "temozolomide200.json")
    elif chemo_choice == "Lomustine (CCNU)":
        Chemo(bsa, "CCNU.json")
    elif chemo_choice == "CAPTEM (Capecitabine + Temozolomide, pNET, E2211)":
        Chemo(bsa, "captem.json")
    elif chemo_choice == "Pazopanib 800 mg/day (STS, PALETTE)":
        Chemo(bsa, "pazopanib_sts.json")

def main():
    st.title("ChemoThon Sarcoma, CNS and NET ENG v 2.2")
    st.write("""Welcome to ChemoThon!
This application provides assistance in prescribing chemotherapy regimens for sarcomas, CNS tumours, and neuroendocrine tumours (NETs) based on body surface area (BSA).
Please ensure doses are adjusted to align with packaging and protocols available in your country. Users bear full responsibility for applying this tool in clinical practice.

We welcome your feedback. Feel free to reach out at filip.kohutek@fntn.sk.""")

    weight = st.number_input("Enter weight (kg):", min_value=1, max_value=250, value=None, step=1)
    height = st.number_input("Enter height (cm):", min_value=1, max_value=250, value=None, step=1)

    if st.button("Calculate BSA") and weight and height:
        bsa_val = calculate_bsa(weight, height)
        st.session_state['bsa'] = bsa_val

    if 'bsa' in st.session_state:
        st.write(f"Body Surface Area (BSA): {st.session_state['bsa']} m²")
        sarcnet(st.session_state['bsa'])

if __name__ == "__main__":
    main()



# ===== Sources =====
with st.expander("📚 Key References"):
    st.markdown("""**Key references – sarcomas, CNS and NETs**

Guidelines: [ESMO](https://www.esmo.org/guidelines/esmo-clinical-practice-guidelines-sarcoma-and-gist) · [NCCN](https://www.nccn.org/guidelines/category_1). Always verify against the current guideline version and available drug vial sizes. As of: June 2026.

- **Doxorubicin (1st line STS)** — Judson et al., Lancet Oncol 2014 (EORTC 62012).
- **Ifosfamide / doxorubicin (epirubicin)** — EORTC 62012 – Judson et al., Lancet Oncol 2014.
- **Ifosfamide high-dose** — Salvage STS – ESMO sarcoma guideline.
- **Trabectedin** — Demetri et al., J Clin Oncol 2016 (liposarcoma/leiomyosarcoma).
- **Paclitaxel weekly (angiosarcoma)** — Penel et al., J Clin Oncol 2008 (ANGIOTAX).
- **Carboplatin / paclitaxel** — ESMO – selected indications.
- **Cisplatin / etoposide; Carboplatin / etoposide (NET G3 / SCLC-like)** — Moertel et al.; NORDIC NEC – Sorbye et al., Ann Oncol 2013.
- **Dacarbazine (5-day)** — DTIC in leiomyosarcoma/melanoma – ESMO.
- **Temozolomide** — Stupp et al., NEJM 2005 (glioblastoma, +RT).
- **Lomustine (CCNU)** — Recurrent glioblastoma – Wick et al., NEJM 2017 (control arm).

**New regimens (2026-06):**
- **CAPTEM (capecitabine + temozolomide, pNET)** — Kunz et al., J Clin Oncol 2023 (ECOG-ACRIN E2211) → now in tool.
- **Pazopanib 800 mg/day (STS, PALETTE)** — Van der Graaf et al., Lancet 2012 → now in tool.
- **Ifosfamide high-dose (2000 mg/m² D1–5)** — Salvage STS – ESMO → now in tool.""")
