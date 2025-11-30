import streamlit as st
import json

# Načítanie údajov o imunoterapiách zo súboru JSON
def load_immunotherapy_data(file_path):
    with open(file_path, "r") as file:
        data = json.load(file)
    return data['imunoterapie']

# Funkcia na generovanie predpisu
def generate_prescription(selected_drug, weight=None):
    # Inicializácia reťazca pre predpis
    prescription = ""

    # Kontrola, či je potrebná premedikácia
    if 'premedication' in selected_drug:
        prescription += f"Premedikácia: {selected_drug['premedication']}\n\n"

    # Kontrola, či je dávkovanie závislé na hmotnosti
    if 'mg/kg' in selected_drug['dosage'] and weight:
        dosage_per_kg = float(selected_drug['dosage'].split()[0].replace('mg/kg', '').strip())
        dosage = dosage_per_kg * weight
        if 'max_dose' in selected_drug and dosage > float(selected_drug['max_dose'].split()[0]):
            dosage = float(selected_drug['max_dose'].split()[0])
        dosage_str = f"{dosage} mg"
    else:
        dosage_str = selected_drug['dosage']

    # Generovanie podrobností o predpise
    prescription += f"{selected_drug['name']} {dosage_str} v 500ml FR (fyziologický roztok) / {selected_drug['administration']}\n\n"
    prescription += " " * 5 + f"NC Deň {selected_drug['frequency'].split()[0]}"

    return prescription

# Názov aplikácie
st.title("""ImmunoThon v. 1.0
         
Vitajte v programe ImmunoThon!         
Program rozpisuje najbežnejšie imunoterapie ako flat-dose alebo podľa hmotnosti.
Dávky je nutné upraviť podľa aktuálne dostupných balení liečiv.
Autor nezodpovedá za prípadné škody spôsobené jeho použitím!
Pripomienky posielajte na filip.kohutek@fntn.sk""")

# Načítanie údajov
immunotherapy_data = load_immunotherapy_data("data/Immunotherapy.json")

# Sekcia pre výber imunoterapie
st.header("Výber imunoterapie")

# Rozbaľovací zoznam na výber typu imunoterapie bez predvolenej hodnoty
immunotherapy_choice = st.selectbox(
    "Vyberte režim imunoterapie",
    options=[""] + [drug["regimen name"] for drug in immunotherapy_data],  # Adding empty string for no pre-selection
    index=0  # Ensuring no default selection
)

# Vyhľadanie detailov vybranej drogy
selected_drug = next((drug for drug in immunotherapy_data if drug["regimen name"] == immunotherapy_choice), None)

# Zobrazenie vstupu pre hmotnosť, ak je liek závislý na dávkovaní podľa hmotnosti
weight = None
if selected_drug and 'mg/kg' in selected_drug['dosage']:
    weight = st.number_input("Zadajte hmotnosť pacienta (kg):", min_value=1, max_value=250, step=1, value=None)

# Zobrazenie vybraných detailov o imunoterapii
if selected_drug:
    # Tlačidlo na generovanie predpisu
    if st.button("Generovať predpis"):
        prescription = generate_prescription(selected_drug, weight)
        st.subheader("Predpis imunoterapie:")
        st.markdown(prescription)
