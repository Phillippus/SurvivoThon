import streamlit as st
import json

# Function for calculating BSA (Body Surface Area)
def bsa(weight, height):
    bodysurf = (weight**0.425) * (height**0.725) * 0.007184
    rbodysurf = round(bodysurf, 2)
    return rbodysurf

# Function for displaying basic chemotherapy
def Chemo(rbodysurf, chemoType):
    """Táto funkcia rozpisuje jednoduché chemoterapie s priamou úmerou"""
    with open('data/' + chemoType, "r") as chemoFile:
        chemoJson = json.loads(chemoFile.read())
    
    st.write("Rozpis chemoterapie:")
    for i in chemoJson["Chemo"]:
        st.write(f"{i['Name']}  {round(i['Dosage'], 2)} {i['DosageMetric']}......... {round(i['Dosage'] * rbodysurf, 2)} mg D{i['Day']}")
    
    st.write(f"NC {chemoJson['NC']} . deň")
    
    Day1 = chemoJson["Day1"]["Instructions"]
    C1 = chemoJson["Chemo"]
    
    st.write("D1 - premedikácia:")
    st.write(chemoJson["Day1"]["Premed"]["Note"])
    
    st.write("D1 - chemoterapia:")
    for x in range(len(chemoJson["Chemo"])):
        st.write(f"{Day1[x]['Name']} {round(C1[x]['Dosage'] * rbodysurf, 2)} mg {Day1[x]['Inst']}")

# Function for chemotherapy with DDP
def ChemoDDP(rbodysurf, chemoType):
    """Táto funkcia slúži pre chemoterapie s DDP"""
    with open('data/' + chemoType, "r") as chemoFile:
        chemoJson = json.loads(chemoFile.read())
    
    st.write(f"DDP 80mg/m2................ {80 * rbodysurf} mg  D1")
    for i in chemoJson["Chemo"]:
        st.write(f"{i['Name']} {i['Dosage']} {i['DosageMetric']} ..... {round(i['Dosage'] * rbodysurf, 2)} mg D{i['Day']}")
    
    st.write(f"NC {chemoJson['NC']} . deň")
    
    st.write("D1")
    st.write(f"1. {chemoJson['Day1']['Premed']['Note']}")
    
    a = round(80 * rbodysurf, 2)
    b = a // 50
    c = a % 50
    rng = int(b)
    
    for ordo in range(2, rng + 2):
        st.write(f"{ordo}. Cisplatina 50mg v 500ml RR iv")
    st.write(f"{ordo}. Cisplatina {int(c)} mg v 500ml RR iv")
    st.write(f"{ordo + 1}. Manitol 10% 250ml iv")
    
    Day1 = chemoJson["Day1"]["Instructions"]
    C1 = chemoJson["Chemo"]
    
    for x in range(len(chemoJson["Chemo"])):
        st.write(f"{ordo + 2}. {Day1[x]['Name']} {round(C1[x]['Dosage'] * rbodysurf, 2)} mg {Day1[x]['Inst']}")

# Function for chemotherapy with Carboplatin (CBDCA)
def ChemoCBDCA(rbodysurf, chemoType):
    """Táto funkcia slúži pre rozpis chemoterapie obsahujúcu karboplatinu"""
    with open('data/' + chemoType, "r") as chemoFile:
        chemoJson = json.loads(chemoFile.read())
    
    CrCl = st.number_input("Zadajte hodnotu clearance v ml/min", min_value=1, max_value=250, value=None)
    AUC = st.number_input("Zadajte hodnotu AUC 2-6", min_value=2, max_value=6, value=None)
    
    if CrCl is not None and AUC is not None:
        st.write(f"CBDCA AUC {AUC}............ {(CrCl + 25) * AUC} mg  D1")
        for i in chemoJson["Chemo"]:
            st.write(f"{i['Name']} {i['Dosage']} {i['DosageMetric']} ..... {round(i['Dosage'] * rbodysurf, 2)} mg D{i['Day']}")
        
        st.write(f"NC {chemoJson['NC']} . deň")
        
        st.write("D1")
        st.write(chemoJson["Day1"]["Premed"]["Note"])
        st.write(f"CBDCA {(CrCl + 25) * AUC} mg v 500ml FR iv")
        for x in range(len(chemoJson["Chemo"])):
            st.write(f"{chemoJson['Day1']['Instructions'][x]['Name']} {round(chemoJson['Chemo'][x]['Dosage'] * rbodysurf, 2)} mg {chemoJson['Day1']['Instructions'][x]['Inst']}")

# Function for chemotherapy with flat dosages
def Flatdoser(rbodysurf, chemoType, chemoFlat=None):
    with open('data/' + chemoType, "r") as chemoFile:
        chemoJson = json.loads(chemoFile.read())
    
    # Initialize chemoJson2 to avoid UnboundLocalError
    chemoJson2 = None

    # Only load chemoFlat if it is provided
    if chemoFlat:
        with open('data/' + chemoFlat, "r") as chemoFile2:
            chemoJson2 = json.loads(chemoFile2.read())
    
    st.write("Rozpis chemoterapie:")
    for i in chemoJson["Chemo"]:
        st.write(f"{i['Name']} {round(i['Dosage'], 2)} {i['DosageMetric']}......... {round(i['Dosage'] * rbodysurf, 2)} mg D{i['Day']}")

    # Only display information from chemoJson2 if it is loaded
    if chemoJson2:
        for i in chemoJson2["Chemo"]:
            st.write(f"{i['Name']} {round(i['Dosage'], 2)} {i['DosageMetric']}......... {round(i['Dosage'], 2)} mg D{i['Day']}")
        
    st.write(f"NC {chemoJson['NC']} . deň")
    
    Day1 = chemoJson["Day1"]["Instructions"]
    C1 = chemoJson["Chemo"]

    st.write("D1")
    st.write(chemoJson["Day1"]["Premed"]["Note"])

    for x in range(len(chemoJson["Chemo"])):
        st.write(f"{Day1[x]['Name']} {round(C1[x]['Dosage'] * rbodysurf, 2)} mg {Day1[x]['Inst']}")

    # Process additional instructions if chemoJson2 is loaded
    if chemoJson2:
        DayF1 = chemoJson2["Day1"]["Instructions"]
        CF = chemoJson2["Chemo"]
        for y in range(len(chemoJson2["Chemo"])):
            st.write(f"{DayF1[y]['Name']} {round(CF[y]['Dosage'], 2)} mg {DayF1[y]['Inst']}")

# Main function for urogenital tumors
def urogenital(rbodysurf):
    """Táto funkcia rozpisuje chemoterapie urogenitálnych tumorov"""
    chemo_choice = st.selectbox("Vyberte chemoterapiu:", [" ", "Docetaxel + Prednison", "Mitoxantron + Prednison","Docetaxel + Darolutamid", "Cabazitaxel + Prednison", "Abirateron (CRPC) + Prednison","Abirateron (HSPC) + Prednison","Enzalutamid","Darolutamid","Apalutamid","Pt/ Gemcitabin", "Vinflunin", "BEP"])
    
    if chemo_choice == "Docetaxel + Prednison":
        Flatdoser(rbodysurf, "docetaxelprostate.json", "flatprednison3w.json")
    elif chemo_choice == "Mitoxantron + Prednison":
        Flatdoser(rbodysurf, "mitoxantrone.json", "flatprednison3w.json")    
    elif chemo_choice == "Docetaxel + Darolutamid":
        Flatdoser(rbodysurf, "docetaxelprostate.json", "flatdarolutamide3w.json")    
    elif chemo_choice == "Cabazitaxel + Prednison":
        Flatdoser(rbodysurf, "cabazitaxel.json", "flatprednison3w.json")
    elif chemo_choice == "Abirateron (CRPC) + Prednison":
        Flatdoser(1, "flatabirateron.json", "flatprednison4w.json")
    elif chemo_choice == "Abirateron (HSPC) + Prednison":
        Flatdoser(1, "flatabirateron.json", "flatprednisonHSPC4w.json")
    elif chemo_choice == "Enzalutamid":
        Flatdoser(1, "flatenzalutamide4w.json", None)  # Provide None explicitly
    elif chemo_choice == "Apalutamid":
        Flatdoser(1, "flatapalutamide4w.json", None)  # Provide None explicitly    
    elif chemo_choice == "Darolutamid":
        Flatdoser(1, "flatdarolutamide4w.json", None)
    elif chemo_choice == "Pt/ Gemcitabin":
        Ptdecis = st.selectbox("Ktorá platina?", ["Vyberte platinu", "Cisplatina", "Karboplatina"])
        if Ptdecis == "Cisplatina":
            ChemoDDP(rbodysurf, "gemcitabin4w.json")
        elif Ptdecis == "Karboplatina":
            ChemoCBDCA(rbodysurf, "gemcitabin4w.json")
    elif chemo_choice == "Vinflunin":
        Chemo(rbodysurf, "vinflunine.json")
    elif chemo_choice == "BEP":
        Flatdoser(rbodysurf, "BEP.json", "flatbleomycin.json")

# Main input function for weight and height
def main():
    st.title("ChemoThon UrogenitalSK v 2.0")
    st.write("""
    Program rozpisuje najbežnejšie chemoterapie podľa povrchu alebo hmotnosti.
    Dávky je nutné upraviť podľa aktuálne dostupných balení liečiv.
    Autor nezodpovedá za prípadné škody spôsobené jeho použitím!
    Pripomienky posielajte na filip.kohutek@fntn.sk
    Program kedykoľvek ukončíte zatvorením okna.
    """)

    # Step 1: Input weight and height
    weight = st.number_input("Zadajte hmotnosť (kg):", min_value=1, max_value=250, value=None)
    height = st.number_input("Zadajte výšku (cm):", min_value=1, max_value=250, value=None)

    if st.button("Vypočítať telesný povrch"):
        if weight and height:
            rbodysurf = bsa(weight, height)
            st.session_state.rbodysurf = rbodysurf
        else:
            st.error("Prosím, zadajte hmotnosť a výšku pre výpočet telesného povrchu.")

    # Always display the BSA if it has been calculated
    if 'rbodysurf' in st.session_state:
        st.write(f"Telesný povrch je: {st.session_state.rbodysurf} m²")

    # Step 2: Display chemotherapy options if BSA is calculated
    if 'rbodysurf' in st.session_state:
        st.write("Teraz vyberte chemoterapiu:")
        urogenital(st.session_state.rbodysurf)

if __name__ == "__main__":
    main()
