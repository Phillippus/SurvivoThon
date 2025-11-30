import streamlit as st
import math

# Výpočet BSA
def calculate_bsa(weight, height):
    return math.sqrt((weight * height) / 3600)

# Výpočet dávok liečiv
def calculate_doses(bsa):
    gemcitabine_dose = bsa * 1000  # mg/m²
    cisplatin_dose = bsa * 70  # mg/m²
    return gemcitabine_dose, cisplatin_dose

# Funkcia na generovanie textu dávok
def generate_dose_summary(bsa, gemcitabine_dose, cisplatin_dose):
    return f"""
### Predpis dávok na základe BSA
- **Gemcitabine:** 1000 mg/m² ... {gemcitabine_dose:.2f} mg D1, D8
- **Cisplatina:** 70 mg/m² ... {cisplatin_dose:.2f} mg D1
- **NC:** D22
"""

# Funkcia na generovanie predpisu pre jednotlivé dni
def generate_day_prescription(day, gemcitabine_dose=None, cisplatin_dose=None):
    if day == "D0":
        return """D0 CHT - Hydratácia
1000ml FR 1/1 i.v.
500ml Manitol 10% i.v.
500ml FR 1/1 i.v.
+ 10ml KCl 7,5%
+ 5ml MgSO4 20%"""
    
    elif day == "D1":
        return f"""D1 CHT – dľa Dr.
Omeprazol 20mg tbl 1-0-0
Aprepitant 125mg 1-0-0
250ml FR 1/1 i.v.
+ 12mg DXM
+ 1amp Granisetron
250ml FR 1/1 + {gemcitabine_dose:.2f} mg Gemcitabine i.v. /30 min
500ml FR 1/1 i.v.
+ 10ml KCl 7,5%
+ 5ml MgSO4 20%
500ml FR 1/1 + {cisplatin_dose:.2f} mg Cisplatina i.v. /60 min
500ml Manitol 10%
500ml FR 1/1 i.v.
+ 10ml KCl 7,5%
+ 5ml MgSO4 20%"""
    
    elif day == "D8":
        return f"""D8 CHT – dľa Dr.
Omeprazol 20mg tbl 1-0-0
250ml FR 1/1 i.v.
+ 8mg DXM
250ml FR 1/1 + {gemcitabine_dose:.2f} mg Gemcitabine i.v. /30 min
500ml FR 1/1 i.v.
+ 10ml KCl 7,5%
+ 5ml MgSO4 20%"""

# Výpočet celého režimu
def generate_full_prescription(gemcitabine_dose, cisplatin_dose):
    days = ["D0", "D1", "D8"]
    full_prescription = "\n\n".join(
        generate_day_prescription(day, gemcitabine_dose, cisplatin_dose) for day in days
    )
    return full_prescription

# Nastavenie Streamlit aplikácie
st.title("GC Urotel (NOU Schéma) v1.0 ")
st.write("Zadajte údaje pacienta pre výpočet dávok a generovanie predpisu.")

# Vstupy
weight = st.text_input("Hmotnosť pacienta (kg)", placeholder="Zadajte hmotnosť")
height = st.text_input("Výška pacienta (cm)", placeholder="Zadajte výšku")

if weight and height:
    try:
        weight = float(weight)
        height = float(height)
        if weight > 0 and height > 0:
            bsa = calculate_bsa(weight, height)
            gemcitabine_dose, cisplatin_dose = calculate_doses(bsa)
            dose_summary = generate_dose_summary(bsa, gemcitabine_dose, cisplatin_dose)
            st.write(f"Vypočítané BSA: {bsa:.2f} m²")
            st.markdown(dose_summary)
        else:
            st.warning("Hmotnosť a výška musia byť kladné hodnoty.")
    except ValueError:
        st.error("Prosím, zadajte platné číselné hodnoty pre hmotnosť a výšku.")
else:
    st.info("Zadajte hmotnosť a výšku pacienta na výpočet dávok.")

options = ["D0", "D1", "D8", "Celý režim"]
choice = st.selectbox("Vyberte deň alebo celý režim", options)

if st.button("Generovať predpis"):
    if weight and height and weight > 0 and height > 0:
        if choice == "Celý režim":
            prescription = generate_full_prescription(gemcitabine_dose, cisplatin_dose)
        else:
            prescription = generate_day_prescription(choice, gemcitabine_dose, cisplatin_dose)
        
        st.subheader("Generovaný predpis:")
        st.text(prescription)
    else:
        st.error("Zadajte platnú hmotnosť a výšku na generovanie predpisu.")