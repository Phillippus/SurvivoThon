import streamlit as st
import math

# Výpočet BSA
def calculate_bsa(weight, height):
    return math.sqrt((weight * height) / 3600)

# Výpočet dávok liečiv
def calculate_doses(bsa):
    etoposid_dose = bsa * 100  # mg/m²
    cisplatin_dose = bsa * 20  # mg/m²
    bleomycin_dose = 30  # Flat dose
    return etoposid_dose, cisplatin_dose, bleomycin_dose

# Funkcia na generovanie textu základných dávok
def generate_dose_summary(bsa, etoposid_dose, cisplatin_dose, bleomycin_dose):
    return f"""
### Predpis základných dávok na základe BSA
- **Bleomycín:** {bleomycin_dose} mg (flat dose) ... {bleomycin_dose} mg D1, D8, D15
- **Etoposid:** 100 mg/m² ... {etoposid_dose:.2f} mg D1, D2, D3, D4, D5
- **Cisplatina:** 20 mg/m² ... {cisplatin_dose:.2f} mg D1, D2, D3, D4, D5
- **NC:** D21
"""

# Funkcia na generovanie predpisu pre jednotlivé dni
def generate_day_prescription(day, etoposid_dose, cisplatin_dose, bleomycin_dose=30):
    if day == "D0":
        return """D0 CHT - Hydratácia
1000ml FR 1/1 i.v.
500ml Manitol 10% i.v.
500ml FR 1/1 i.v.
+ 10ml KCl 7,5%
+ 5ml MgSO4 20%"""
    elif day == "D1":
        return f"""D1 CHT – dľa Dr.
Omeprazol 20mg cps 1-0-0
Metoklopramid 3x1 tbl
Aprepitant 125mg cps 1-0-0
FR 500ml 1/1 i.v.
+ DXM 12mg
+ Granisetron 1amp
Bleomycin {bleomycin_dose} mg
+ FR 100ml i.v.
Etoposid {etoposid_dose:.2f} mg
+ FR 500ml /90min
500ml FR 1/1 i.v.
+ 10ml KCl 7,5%
+ 5ml MgSO4 20%
cDDP {cisplatin_dose:.2f} mg
+ FR 500ml /60 min
10% Manitol 500ml i.v.
500ml GLC 5%
+ 10ml KCl 7,5%
+ 5ml MgSO4 20%"""
    elif day in ["D2", "D3", "D4", "D5"]:
        return f"""{day} CHT
Omeprazol 20mg cps 1-0-0
Metoklopramid 3x1 tbl
Aprepitant 80mg cps 1-0-0
FR 500ml 1/1 i.v.
+ DXM 8mg
+ Granisetron 1amp
Etoposid {etoposid_dose:.2f} mg
+ FR 500ml /90min
500ml FR 1/1 i.v.
+ 10ml KCl 7,5%
+ 5ml MgSO4 20%
cDDP {cisplatin_dose:.2f} mg
+ FR 500ml /60 min
10% Manitol 500ml i.v.
500ml GLC 5%
+ 10ml KCl 7,5%
+ 5ml MgSO4 20%"""
    elif day == "D6":
        return """D6 CHT
Aprepitant 80mg cps 1-0-0
Pegfilgrastim inj. 0,6ml s.c. minimálne 24 hod po dotečení CHT"""
    elif day in ["D8", "D15"]:
        return f"""{day} CHT
Granisetron 2mg p.o.
Bleomycín 30mg
+ 250ml FR i.v.
+ 100ml FR preplach"""
    else:
        return f"Invalid day: {day}"

# Výpočet celého režimu
def generate_full_prescription(etoposid_dose, cisplatin_dose, bleomycin_dose=30):
    days = ["D0", "D1", "D2", "D3", "D4", "D5", "D6", "D8", "D15"]
    full_prescription = "\n\n".join(
        generate_day_prescription(day, etoposid_dose, cisplatin_dose, bleomycin_dose) for day in days
    )
    return full_prescription

# Nastavenie Streamlit aplikácie
st.title("BEP (NOU Schéma) v1.0")
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
            etoposid_dose, cisplatin_dose, bleomycin_dose = calculate_doses(bsa)
            dose_summary = generate_dose_summary(bsa, etoposid_dose, cisplatin_dose, bleomycin_dose)
            st.write(f"Vypočítané BSA: {bsa:.2f} m²")
            st.markdown(dose_summary)
        else:
            st.warning("Hmotnosť a výška musia byť kladné hodnoty.")
    except ValueError:
        st.error("Prosím, zadajte platné číselné hodnoty pre hmotnosť a výšku.")
else:
    st.info("Zadajte hmotnosť a výšku pacienta na výpočet dávok.")

options = ["D0", "D1", "D2", "D3", "D4", "D5", "D6", "D8", "D15", "Celý režim"]
choice = st.selectbox("Vyberte deň alebo celý režim", options)

if st.button("Generovať predpis"):
    if weight and height and weight > 0 and height > 0:
        if choice == "Celý režim":
            prescription = generate_full_prescription(etoposid_dose, cisplatin_dose)
        else:
            prescription = generate_day_prescription(choice, etoposid_dose, cisplatin_dose)
        
        st.subheader("Generovaný predpis:")
        st.text(prescription)
    else:
        st.error("Zadajte platnú hmotnosť a výšku na generovanie predpisu.")