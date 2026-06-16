import streamlit as st
import json
from sk_to_eng import sk_to_eng, show_evidence_eng

def calculate_bsa(weight, height):
    """Calculates body surface area using the DuBois formula."""
    return round((weight**0.425) * (height**0.725) * 0.007184, 2)

def load_json(filename):
    """Loads a JSON file from the data directory."""
    try:
        with open(f'data/{filename}', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        st.error(f"File not found: data/{filename}")
        return None
    except json.JSONDecodeError:
        st.error(f"Error parsing: {filename}")
        return None

def display_chemotherapy_details(bsa, filename):
    """Display BSA-based chemotherapy from individual JSON file (handles flat/mg/kg/BSA)."""
    weight = st.session_state.get('weight_kg', None)
    reg = load_json(filename)
    if not reg:
        return
    st.write("#### Chemotherapy Drugs")
    for drug in reg.get("Chemo", []):
        metric = drug.get("DosageMetric", "mg/m2")
        if "flat" in metric.lower():
            st.write(f"{drug['Name']} {drug['Dosage']} {metric} D{drug['Day']}")
        elif "mg/kg" in metric:
            if weight:
                dosage = round(drug["Dosage"] * weight, 2)
                st.write(f"{drug['Name']} {drug['Dosage']} {metric} ......... {dosage} mg D{drug['Day']}")
            else:
                st.write(f"{drug['Name']} {drug['Dosage']} {metric} ......... (enter weight) D{drug['Day']}")
        else:
            dosage = round(drug["Dosage"] * bsa, 2)
            st.write(f"{drug['Name']} {drug['Dosage']} {metric} ......... {dosage} mg D{drug['Day']}")
    st.write(f"**Next Cycle:** {reg.get('NC', '?')} days")
    st.write("#### D1 - Premedication")
    st.write(sk_to_eng(reg.get("Day1", {}).get("Premed", {}).get("Note", "")))
    st.write("#### D1 - Chemotherapy")
    chemo_list = reg.get("Chemo", [])
    for inst in reg.get("Day1", {}).get("Instructions", []):
        drug_name = inst.get("Name", "")
        drug = next((d for d in chemo_list if d["Name"] == drug_name), None)
        if drug:
            metric = drug.get("DosageMetric", "mg/m2")
            if "flat" in metric.lower():
                st.write(f"{drug_name} {drug['Dosage']} mg {sk_to_eng(inst.get('Inst', ''))}")
            elif "mg/kg" in metric:
                if weight:
                    calc_dose = round(drug["Dosage"] * weight, 2)
                    st.write(f"{drug_name} {calc_dose} mg {sk_to_eng(inst.get('Inst', ''))}")
                else:
                    st.write(f"{drug_name} {drug['Dosage']} mg/kg {sk_to_eng(inst.get('Inst', ''))}")
            else:
                calc_dose = round(drug["Dosage"] * bsa, 2)
                st.write(f"{drug_name} {calc_dose} mg {sk_to_eng(inst.get('Inst', ''))}")
    show_evidence_eng(reg)

def Flatdoser(bsa, chemo_file, flat_file=None):
    """Display regimen with BSA-based drugs + flat-dose component (e.g. vincristine)."""
    reg = load_json(chemo_file)
    flat = load_json(flat_file) if flat_file else None
    if not reg:
        return
    st.write("#### Chemotherapy Drugs")
    for drug in reg.get("Chemo", []):
        dosage = round(drug["Dosage"] * bsa, 2)
        st.write(f"{drug['Name']} {drug['Dosage']} mg/m² ......... {dosage} mg D{drug['Day']}")
    if flat:
        for drug in flat.get("Chemo", []):
            metric2 = drug.get("DosageMetric", "mg/m2")
            if "mg/m2" in metric2 and "max" in metric2.lower():
                raw = round(drug["Dosage"] * bsa, 2)
                capped = min(raw, 2.0)
                st.write(f"{drug['Name']} {drug['Dosage']} {metric2} ......... {capped} mg D{drug['Day']} (BSA dose: {raw} mg → capped at max 2 mg)")
            else:
                st.write(f"{drug['Name']} {metric2} ......... {drug['Dosage']} mg D{drug['Day']}")
    st.write(f"**Next Cycle:** {reg.get('NC', '?')} days")
    st.write("#### D1 - Premedication")
    st.write(sk_to_eng(reg.get("Day1", {}).get("Premed", {}).get("Note", "")))
    st.write("#### D1 - Chemotherapy")
    chemo_list = reg.get("Chemo", [])
    for inst in reg.get("Day1", {}).get("Instructions", []):
        drug_name = inst.get("Name", "")
        drug = next((d for d in chemo_list if d["Name"] == drug_name), None)
        if drug:
            calc_dose = round(drug["Dosage"] * bsa, 2)
            st.write(f"{drug_name} {calc_dose} mg {sk_to_eng(inst.get('Inst', ''))}")
    if flat:
        flat_chemo = flat.get("Chemo", [])
        for inst in flat.get("Day1", {}).get("Instructions", []):
            flat_drug = next((d for d in flat_chemo if d["Name"] == inst.get("Name", "")), None)
            if flat_drug:
                metric2 = flat_drug.get("DosageMetric", "mg/m2")
                if "mg/m2" in metric2 and "max" in metric2.lower():
                    raw = round(flat_drug["Dosage"] * bsa, 2)
                    capped = min(raw, 2.0)
                    st.write(f"{inst['Name']} {capped} mg {sk_to_eng(inst.get('Inst', ''))}")
                else:
                    st.write(f"{inst['Name']} {flat_drug['Dosage']} mg {sk_to_eng(inst.get('Inst', ''))}")
    show_evidence_eng(reg)
    if flat:
        show_evidence_eng(flat)

def DA_EPOCH(bsa, with_rituximab=False, dose_level=1):
    """(DA-)EPOCH(-R): dose-adjusted EPOCH ± rituximab.
    Etoposide, doxorubicin and vincristine run as a 96h continuous infusion D1-4.
    dose_level scales etoposide/doxorubicin/cyclophosphamide by 1.2^(level-1)
    (Wilson protocol; eviQ: 750→900→1080…). Vincristine and prednisone are fixed."""
    name = "DA-EPOCH-R" if with_rituximab else "DA-EPOCH"
    factor = round(1.2 ** (dose_level - 1), 4)
    st.write(f"### Protocol {name} — dose level {dose_level} ({int(round(factor*100))}% of baseline)")

    etop_pm = round(50 * factor, 2)
    doxo_pm = round(10 * factor, 2)
    cfa_pm = round(750 * factor, 2)
    etop_d = round(etop_pm * bsa, 2);  etop_tot = round(etop_pm * 4 * bsa, 2)
    doxo_d = round(doxo_pm * bsa, 2);  doxo_tot = round(doxo_pm * 4 * bsa, 2)
    cfa = round(cfa_pm * bsa, 2)
    vinc_d = round(0.4 * bsa, 2); vinc_tot = round(1.6 * bsa, 2)
    pred = round(60 * bsa, 2)
    ritux = round(375 * bsa, 2)

    st.write("#### Chemotherapy Drugs")
    if with_rituximab:
        st.write(f"rituximab 375 mg/m² ......... {ritux} mg D1")
    st.write(f"etoposide {etop_pm} mg/m²/day (CIV D1-4) ......... {etop_d} mg/day (total {etop_tot} mg over 96h)")
    st.write(f"doxorubicin {doxo_pm} mg/m²/day (CIV D1-4) ......... {doxo_d} mg/day (total {doxo_tot} mg over 96h)")
    st.write(f"vincristine 0.4 mg/m²/day (CIV D1-4, NO cap) ......... {vinc_d} mg/day (total {vinc_tot} mg over 96h)")
    st.write(f"cyclophosphamide {cfa_pm} mg/m² ......... {cfa} mg D5")
    st.write(f"prednisone 60 mg/m² twice daily ......... {pred} mg BID p.o. D1-5")
    st.write("**Next Cycle:** 21 days")
    st.write("#### D1 - Premedication")
    st.write("Palonosetron 0.5mg/Netupitant 300mg (Akynzeo) p.o. 1h before chemo, Dexamethasone 12 mg i.v., Pantoprazole 40 mg p.o." +
             (" Before rituximab: Hydrocortisone 100 mg i.v., Chlorphenamine 1 amp i.v., Paracetamol 1 g p.o. (1st infusion 50 ml/h, step up; subsequent cycles 100 ml/h)." if with_rituximab else ""))
    st.write("#### Chemotherapy")
    if with_rituximab:
        st.write(f"rituximab {ritux} mg in 500 ml NS i.v. D1")
    st.write("D1-D4 — single 96-hour continuous infusion (one pump/line):")
    st.write(f"  etoposide {etop_tot} mg + doxorubicin {doxo_tot} mg + vincristine {vinc_tot} mg in 1000 ml NS i.v. continuously over 96 hours (D1-4)")
    st.write(f"D5: cyclophosphamide {cfa} mg in 500 ml NS i.v./30-60 min")
    st.write(f"D1-D5: prednisone {pred} mg p.o. twice daily")
    st.write("D6+: G-CSF (filgrastim) s.c. daily until neutrophil recovery")
    st.info("⚠️ **Dose adjustment (Wilson protocol)** — based on PREVIOUS cycle nadir (monitor counts twice weekly):\n"
            "- ANC nadir ≥ 0.5 ×10⁹/L (never below) → **increase by 1 level**\n"
            "- ANC nadir < 0.5 on 1-2 measurements → **same level**\n"
            "- ANC nadir < 0.5 on ≥3 measurements OR platelets < 25 ×10⁹/L → **decrease by 1 level**\n\n"
            "Cycle 1 = always level 1. Only etoposide, doxorubicin and cyclophosphamide are adjusted "
            "(by 20% per level); vincristine and prednisone stay fixed.")

def DHAP(bsa):
    """DHAP: cisplatin + cytarabine + dexamethasone."""
    ddp = round(bsa * 100, 2)
    cycle = int(ddp // 50)
    remnant = round(ddp % 50, 2)
    ara_c = round(2000 * bsa, 2)

    st.write(f"Cisplatin 100 mg/m² ......... {ddp} mg D1")
    st.write(f"Cytarabine 2000 mg/m² BID ......... {ara_c} mg every 12 h D2")
    st.write("Dexamethasone 40 mg flat ......... 40 mg D1–D4")
    st.write("**Next Cycle:** 21 days")
    st.write("#### D1 - Premedication")
    st.write("Palonosetron 0.5mg/Netupitant 300mg (Akynzeo) p.o. 1h before chemo, Dexamethasone 12 mg i.v., Pantoprazole 40 mg p.o.")
    st.write("#### D1 - Chemotherapy")
    item = 1
    for _ in range(cycle):
        st.write(f"{item}. Cisplatin 50 mg in 500 ml normal saline iv")
        item += 1
    if remnant > 0:
        st.write(f"{item}. Cisplatin {round(remnant, 2)} mg in 500 ml normal saline iv")
        item += 1
    st.write(f"{item}. Mannitol 10% 250 ml iv")
    item += 1
    st.write(f"{item}. Dexamethasone 40 mg p.o. (+ pantoprazole 40 mg p.o.)")

def RDHAP(bsa):
    """R-DHAP: rituximab + cisplatin + cytarabine + dexamethasone."""
    ritux = round(375 * bsa, 2)
    ddp = round(bsa * 100, 2)
    cycle = int(ddp // 50)
    remnant = round(ddp % 50, 2)
    ara_c = round(2000 * bsa, 2)

    st.write(f"Rituximab 375 mg/m² ......... {ritux} mg D1")
    st.write(f"Cisplatin 100 mg/m² ......... {ddp} mg D1")
    st.write(f"Cytarabine 2000 mg/m² BID ......... {ara_c} mg every 12 h D2")
    st.write("Dexamethasone 40 mg flat ......... 40 mg D1–D4")
    st.write("**Next Cycle:** 21 days")
    st.write("#### D1 - Premedication")
    st.write("Hydrocortisone 100 mg iv, Chlorphenamine 1 amp iv, Pantoprazole 40 mg p.o., Palonosetron 0.5mg/Netupitant 300mg (Akynzeo) p.o. 1h before chemo, Dexamethasone 12 mg i.v.")
    st.write("#### D1 - Chemotherapy")
    st.write(f"1. Rituximab {ritux} mg in 500 ml NS iv (1st infusion: start 50 ml/h, step up; subsequent cycles: 100 ml/h)")
    ordo = 1
    for _ in range(cycle):
        ordo += 1
        st.write(f"{ordo}. Cisplatin 50 mg in 500 ml normal saline iv")
    if remnant > 0:
        ordo += 1
        st.write(f"{ordo}. Cisplatin {round(remnant, 2)} mg in 500 ml normal saline iv")
        ordo += 1
    else:
        ordo += 1
    st.write(f"{ordo}. Mannitol 10% 250 ml iv")
    ordo += 1
    st.write(f"{ordo}. Dexamethasone 40 mg p.o. (+ pantoprazole 40 mg p.o.)")

def hematology(bsa):
    """Haematology regimen selector."""
    chemo_options = {
        # --- Hodgkin lymphoma ---
        "ABVD": ("ABVD.json", None),
        # --- Aggressive NHL (DLBCL) ---
        "R-CHOP": ("RCHOP.json", "flatvincristin.json"),
        "CHOP (without R)": ("CHOP.json", "flatvincristin.json"),
        "R-miniCHOP (elderly)": ("RminiCHOP.json", "flatminivincristin.json"),
        "miniCHOP (without R)": ("miniCHOP.json", "flatminivincristin.json"),
        # --- Indolent NHL / CLL ---
        "R-CVP": ("RCVP.json", "flatvincristin.json"),
        "R-Bendamustine (BR)": ("BR.json", None),
        "Bendamustine monotherapy (120 mg/m²)": ("bendamustin.json", None),
        # --- Salvage regimens ---
        "R-DHAP": ("RDHAP_special", None),
        "DHAP": ("DHAP_special", None),
        "DA-EPOCH-R (DLBCL/HG-BCL, CIV D1-4)": ("DAEPOCHR_special", None),
        "DA-EPOCH (without R, CIV D1-4)": ("DAEPOCH_special", None),
        "R-GemOx": ("RGemox.json", None),
        "GemOx": ("Gemox.json", None),
        "GDP (Gemcitabine + Cisplatin + Dex)": ("GDP.json", "flatdexametazon.json"),
        # --- Other ---
        "Rituximab (monotherapy)": ("rituximab.json", None),
        # --- New (2026-06) ---
        "Pola-R-CHP (DLBCL 1st line, POLARIX)": ("pola_rchp.json", None),
        "BV-AVD (Hodgkin stage III/IV, ECHELON-1)": ("bv_avd.json", None),
    }

    selected = st.selectbox("Select chemotherapy regimen:", list(chemo_options.keys()))

    # DA-EPOCH dose level selector (outside the button so it persists on recompute)
    da_level = 1
    if selected in ("DA-EPOCH-R (DLBCL/HG-BCL, CIV D1-4)", "DA-EPOCH (without R, CIV D1-4)"):
        da_level = st.number_input(
            "Dose level (1 = baseline; ↑ if ANC nadir ≥0.5, ↓ if ANC<0.5 on ≥3 measurements or platelets <25). "
            "Reductions below level 1 per institutional protocol.",
            min_value=1, max_value=5, value=1, step=1)

    if st.button("Display Protocol"):
        if selected == "DHAP":
            DHAP(bsa)
        elif selected == "R-DHAP":
            RDHAP(bsa)
        elif selected == "DA-EPOCH-R (DLBCL/HG-BCL, CIV D1-4)":
            DA_EPOCH(bsa, with_rituximab=True, dose_level=da_level)
        elif selected == "DA-EPOCH (without R, CIV D1-4)":
            DA_EPOCH(bsa, with_rituximab=False, dose_level=da_level)
        else:
            chemo_file, flat_file = chemo_options[selected]
            if flat_file:
                Flatdoser(bsa, chemo_file, flat_file)
            else:
                display_chemotherapy_details(bsa, chemo_file)

def main():
    st.title("ChemoThon Haematology ENG v 2.3")
    st.write("""Welcome to ChemoThon!
This application provides assistance in prescribing haematological chemotherapy regimens based on body surface area (BSA).
Please ensure doses are adjusted to align with packaging and protocols available in your country. Users bear full responsibility for applying this tool in clinical practice.
Immunotherapy can be found at https://immunothoneng.streamlit.app

We welcome your feedback. Feel free to reach out at filip.kohutek@fntn.sk.""")

    weight = st.number_input("Enter weight (kg):", min_value=1, max_value=250, value=None, step=1)
    height = st.number_input("Enter height (cm):", min_value=1, max_value=250, value=None, step=1)

    if st.button("Calculate BSA") and weight and height:
        bsa_val = calculate_bsa(weight, height)
        st.session_state['bsa'] = bsa_val
        st.session_state['weight_kg'] = weight

    if 'bsa' in st.session_state:
        st.write(f"Body Surface Area (BSA): {st.session_state['bsa']} m²")
        hematology(st.session_state['bsa'])

if __name__ == "__main__":
    main()



# ===== Sources =====
with st.expander("📚 Key References"):
    st.markdown("""**Key references – haematological malignancies**

Guidelines: [ESMO](https://www.esmo.org/guidelines/esmo-clinical-practice-guidelines-haematological-malignancies) · [NCCN](https://www.nccn.org/guidelines/category_1). Always verify against the current guideline version and available drug vial sizes. As of: June 2026.

- **ABVD (Hodgkin)** — Canellos et al., NEJM 1992.
- **R-CHOP (DLBCL)** — Coiffier et al., NEJM 2002; GELA LNH 98-5.
- **R-miniCHOP (elderly ≥80 y)** — Peyrade et al., Lancet Oncol 2011.
- **R-CVP (indolent NHL)** — Marcus et al., J Clin Oncol 2005.
- **R-Bendamustine (BR, indolent/mantle)** — Rummel et al., Lancet 2013; Flinn et al., J Clin Oncol 2014.
- **R-DHAP (salvage, pre-ASCT)** — Philip et al., NEJM 1995 (PARMA).
- **DA-EPOCH-R (DLBCL / HG-BCL / primary mediastinal)** — Wilson et al., Blood 2002; Dunleavy et al., NEJM 2013 (PMBCL); CALGB 50303 – Bartlett et al., J Clin Oncol 2019.
- **R-GemOx (salvage)** — Mounier et al., J Clin Oncol 2013.
- **GDP (salvage)** — Crump et al., J Clin Oncol 2004.
- **Rituximab (monotherapy)** — McLaughlin et al., J Clin Oncol 1998.

**New regimens (2026-06):**
- **Pola-R-CHP (DLBCL 1st line, POLARIX)** — Tilly et al., NEJM 2022 → now in tool.
- **BV-AVD (Hodgkin stage III/IV, ECHELON-1)** — Connors et al., NEJM 2018 → now in tool.""")
