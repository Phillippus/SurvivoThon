import streamlit as st
import math

# Výpočet BSA
def calculate_bsa(weight, height):
    return math.sqrt((weight * height) / 3600)

# Výpočet dávok liečiv
def calculate_doses(bsa):
    paclitaxel_dose = bsa * 250  # mg/m2
    ifosfamid_dose = bsa * 1200  # mg/m2
    cisplatin_dose = bsa * 20  # mg/m2
    mesna_total_dose = ifosfamid_dose * 0.8  # 0.8x dávka Ifosfamidu
    mesna_split_dose = mesna_total_dose / 3  # Rozdelenie na 3 dávky
    return paclitaxel_dose, ifosfamid_dose, cisplatin_dose, mesna_split_dose

# Funkcia na generovanie textu dávok
def generate_dose_summary(bsa, paclitaxel_dose, ifosfamid_dose, cisplatin_dose):
    return f"""
### Predpis dávok na základe BSA
- **Paclitaxel:** 250 mg/m² ... {paclitaxel_dose:.2f} mg D1
- **Ifosfamid:** 1200 mg/m² ... {ifosfamid_dose:.2f} mg D1, D2, D3, D4, D5
- **Cisplatina:** 20 mg/m² ... {cisplatin_dose:.2f} mg D1, D2, D3, D4, D5
- **NC:** D21
"""

# Funkcia na generovanie predpisu pre jednotlivé dni
def generate_day_prescription(day, paclitaxel_dose=None, ifosfamid_dose=None, cisplatin_dose=None, mesna_split_dose=None):
    if day == "D0":
        return """D0 CHT - Hydratácia
1000ml FR 1/1 i.v.
500ml Manitol 10% i.v.
500ml FR 1/1 i.v.
+ 10ml KCl 7,5%
+ 5ml MgSO4 20%
Premedikácia o 22:00 hod:
100ml FR 1/1 i.v.
+ 20mg DXM
+ 1amp Dithiaden
+ 1amp Quamatel"""
    
    elif day == "D1":
        return f"""D1 CHT – dľa Dr.
Omeprazol 20mg tbl 1-0-0
Metoklopramid 3x1 tbl
Aprepitant 125mg cps 1-0-0
FR 500ml 1/1 i.v.
+ 12mg DXM
+ 1amp Granisetron
Quamatel 1amp ivb
Dithiaden 1amp ivb
30 min pauza
Paclitaxel {paclitaxel_dose:.2f} mg + 500ml FR 1/1 i.v. /3hod
Ifosfamid {ifosfamid_dose:.2f} mg + Mesna {mesna_split_dose:.2f} mg + 500ml FR 1/1 i.v.
Po 4 a 8 hod:
500ml FR 1/1 i.v. + Mesna {mesna_split_dose:.2f} mg i.v.
500ml FR 1/1 i.v.
+ 10ml KCl 7.5%
+ 5ml MgSO4 20%
cDDP {cisplatin_dose:.2f} mg + 500ml FR 1/1 i.v. /60 min
10% Manitol 500ml i.v.
500ml GLC 5% i.v.
+ 10ml KCl7,5%
+ 5ml MgSO4 20%"""
    
    elif day in ["D2", "D3", "D4", "D5"]:
        return f"""{day} CHT
Omeprazol 20mg tbl 1-0-0
Metoklopramid 3x1 tbl
Aprepitant 80mg cps 1-0-0
FR 500ml 1/1 i.v.
+ 8mg DXM
+ 1amp Granisetron
Ifosfamid {ifosfamid_dose:.2f} mg + Mesna {mesna_split_dose:.2f} mg + 500ml FR 1/1 i.v.
Po 4 a 8 hod:
500ml FR 1/1 i.v. + Mesna {mesna_split_dose:.2f} mg i.v.
500ml FR 1/1 i.v.
+ 10ml KCl 7.5%
+ 5ml MgSO4 20%
cDDP {cisplatin_dose:.2f} mg + 500ml FR 1/1 i.v. /60 min
10% Manitol 500ml i.v.
500ml GLC 5% i.v.
+ 10ml KCl7,5%
+ 5ml MgSO4 20%"""

    elif day == "D6":
        return """D6 CHT
Aprepitant 80mg cps 1-0-0
Pegfilgrastim inj. 0,6 ml s.c. min. 24 hod po dotečení CHT"""

# Výpočet celého režimu
def generate_full_prescription(paclitaxel_dose, ifosfamid_dose, cisplatin_dose, mesna_split_dose):
    days = ["D0", "D1", "D2", "D3", "D4", "D5", "D6"]
    full_prescription = "\n\n".join(
        generate_day_prescription(day, paclitaxel_dose, ifosfamid_dose, cisplatin_dose, mesna_split_dose) for day in days
    )
    return full_prescription

# Nastavenie Streamlit aplikácie
st.title("TIP (NOU Schéma ) v1.0")
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
            paclitaxel_dose, ifosfamid_dose, cisplatin_dose, mesna_split_dose = calculate_doses(bsa)
            dose_summary = generate_dose_summary(bsa, paclitaxel_dose, ifosfamid_dose, cisplatin_dose)
            st.write(f"Vypočítané BSA: {bsa:.2f} m²")
            st.markdown(dose_summary)
        else:
            st.warning("Hmotnosť a výška musia byť kladné hodnoty.")
    except ValueError:
        st.error("Prosím, zadajte platné číselné hodnoty pre hmotnosť a výšku.")
else:
    st.info("Zadajte hmotnosť a výšku pacienta na výpočet dávok.")

options = ["D0", "D1", "D2", "D3", "D4", "D5", "D6", "Celý režim"]
choice = st.selectbox("Vyberte deň alebo celý režim", options)

if st.button("Generovať predpis"):
    if weight and height and weight > 0 and height > 0:
        if choice == "Celý režim":
            prescription = generate_full_prescription(paclitaxel_dose, ifosfamid_dose, cisplatin_dose, mesna_split_dose)
        else:
            prescription = generate_day_prescription(choice, paclitaxel_dose, ifosfamid_dose, cisplatin_dose, mesna_split_dose)
        
        st.subheader("Generovaný predpis:")
        st.text(prescription)
    else:
        st.error("Zadajte platnú hmotnosť a výšku na generovanie predpisu.")