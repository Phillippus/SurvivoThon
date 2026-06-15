import streamlit as st
import json

# Load immunotherapy data from a JSON file
def load_immunotherapy_data(file_path):
    with open(file_path, "r") as file:
        data = json.load(file)
    return data['imunoterapie']

# Function to generate prescription
def generate_prescription(selected_drug, weight=None):
    import re
    prescription = ""

    if 'premedication' in selected_drug:
        prescription += f"Premedication: {selected_drug['premedication']}\n\n"

    name = selected_drug['name']
    dosage_raw = selected_drug['dosage']
    admin = selected_drug['administration']
    freq = selected_drug['frequency']

    # Detect SC administration
    is_sc = 's.c.' in admin.lower() or name.lower().endswith(' sc')

    if is_sc:
        # SC drug — administration field already contains the full instruction
        prescription += f"{name} / {admin}\n\n"
    elif '+' in dosage_raw and 'mg/kg' in dosage_raw:
        # Combination with multiple mg/kg components (e.g. ipi + nivo)
        parts = dosage_raw.split('+')
        dose_lines = []
        for part in parts:
            part = part.strip()
            nums = re.findall(r'[\d.]+', part)
            abbr_match = re.search(r'\(([^)]+)\)', part)
            abbr = abbr_match.group(1).strip() if abbr_match else ""
            if 'mg/kg' in part and nums and weight:
                calc = round(float(nums[0]) * weight, 1)
                label = abbr.split()[0] if abbr else "drug"
                dose_lines.append(f"{label}: {nums[0]} mg/kg → {calc} mg")
            elif 'mg' in part and 'mg/kg' not in part and nums:
                label = abbr.split()[0] if abbr else ""
                dose_lines.append(f"{label + ': ' if label else ''}{nums[0]} mg flat")
        prescription += f"{name}: {'; '.join(dose_lines)}\n{admin}\n\n"
    elif 'mg/kg' in dosage_raw and weight:
        # Simple mg/kg (e.g. Durvalumab 10 mg/kg)
        nums = re.findall(r'[\d.]+', dosage_raw)
        calc = round(float(nums[0]) * weight, 1)
        if 'max_dose' in selected_drug:
            max_nums = re.findall(r'[\d.]+', selected_drug['max_dose'])
            if max_nums:
                calc = min(calc, float(max_nums[0]))
        prescription += f"{name} {nums[0]} mg/kg → {calc} mg / {admin}\n\n"
    elif '/' in dosage_raw or '+' in dosage_raw:
        # Complex combination dosage (e.g. Relatlimab+Nivo, Tremelimumab+Durvalumab)
        # administration field already contains the full details
        prescription += f"{name}\n{admin}\n\n"
    else:
        # Standard flat-dose IV — administration field already has volume/time
        prescription += f"{name} {dosage_raw} / {admin}\n\n"

    # NC line — use full frequency string (not just first word)
    prescription += " " * 5 + f"NC: {freq}"

    return prescription

# Application title
st.title("""ImmunoThonEng v. 2.1
         
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



# ===== Zdroje / Sources (pridané 2026-06, aditívne) =====
with st.expander("📚 Zdroje k režimom / Sources"):
    st.markdown("""**Key references – immunotherapy**

Guidelines: [ESMO](https://www.esmo.org/guidelines) · [NCCN](https://www.nccn.org/guidelines/category_1). Always verify against the current guideline version and available drug vial sizes. As of: June 2026.

- **Pembrolizumab (3-/6-weekly)** — KEYNOTE-024/189/048 a i.; flat 200 mg q3w / 400 mg q6w – Lala et al., 2020.
- **Nivolumab (2-/4-weekly)** — CheckMate série; flat 240 mg q2w / 480 mg q4w – Zhao et al., Ann Oncol 2017.
- **Atezolizumab (2-/3-/4-weekly)** — OAK/IMpower; 840 q2w / 1200 q3w / 1680 q4w – Morrissey et al., 2019.
- **Durvalumab** — PACIFIC – Antonia et al., NEJM 2017; CASPIAN – Paz-Ares et al., Lancet 2019.
- **Avelumab** — JAVELIN Bladder 100 (udržiavanie) – Powles et al., NEJM 2020.
- **Cemiplimab** — EMPOWER-Lung 1; CSCC – Migden et al., NEJM 2018.
- **Ipilimumab + nivolumab** — CheckMate-067 (melanóm) – Larkin et al., NEJM 2015/2019.
- **Dostarlimab** — RUBY (endometrium) – Mirza et al., NEJM 2023; GARNET.
- **Tremelimumab (STRIDE)** — HIMALAYA (HCC) – Abou-Alfa et al., NEJM Evid 2022.
- **Tislelizumab** — RATIONALE-302/305 – ezofág/gastrický.

**Current standards to consider (not yet in tool):**
- Dávkovanie flat-dose overte podľa SmPC; mg/kg režimy prepočítajte na hmotnosť.
- Nové: nivolumab + ipilimumab pri MSI-H mCRC (CheckMate-8HW, 2024).""")
