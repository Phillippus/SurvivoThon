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
    
    st.write("DDP 80mg/m2................", 80 * rbodysurf, "mg  D1")
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
        ordo += 1
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

# Function for chemotherapy with Ifosfamid (Ifo)
def ChemoIfo(rbodysurf, dose, otherCHT):
    ifo = int(dose * rbodysurf)
    mesna = ifo * 0.8
    ifocycle = ifo // 2000
    mesnacycle = ifocycle + 1
    iforemnant = ifo % 2000
    mesnainit = 1200
    mesnaend = 800
    
    if otherCHT:
        st.write(f"Epirubicin 60mg/m2........ {60 * rbodysurf} mg D1, D2")
        st.write(f"Ifosfamid 3000mg/m2.......... {ifo} mg D1,D2,D3")
        st.write(f"Mesna 0.8 x ifosfamid........ {mesna} mg D1,D2,D3")
        st.write("NC 21. deň")
        st.write("D1")
        st.write("Ondasetron 8mg iv, Dexametazon 8mg iv, Pantoprazol 40mg p.o.")
        st.write(f"Epirubicin {60 * rbodysurf} mg v 500ml FR iv")
        st.write(f"MESNA {mesnainit} mg v 100ml FR /4hodiny")
        if iforemnant > 200:
            mesnacont = (mesna - 2000) // ifocycle
            for cycifo in range(0, ifocycle):
                st.write("Ifosfamid 2000mg v 500ml FR iv")
                st.write(f"MESNA {mesnacont} mg v 100ml FR iv/ 4 hodiny")
            st.write(f"Ifosfamid {iforemnant} mg 500ml FR iv")
            st.write("MESNA 800mg v 100ml FR iv/ 4 hodiny")   
        else: 
            mesnacont = (mesna - 1200) // ifocycle
            for cycifo in range(0, ifocycle):
                st.write("Ifosfamid 2000mg v 500ml FR iv")
                st.write(f"MESNA {mesnacont} mg v 100ml FR iv/ 4 hodiny")
    
    else:
        st.write(f"Ifosfamid 3000mg/m2.......... {ifo} mg D1,D2,D3")
        st.write(f"Mesna 0.8 x ifosfamid........ {mesna} mg D1,D2,D3")
        st.write("NC 21. deň")
        st.write("D1")
        st.write("Ondasetron 8mg iv, Dexametazon 8mg iv, Pantoprazol 40mg p.o.")
        st.write(f"MESNA {mesnainit} mg v 100ml FR /4hodiny")
        if iforemnant > 200:
            mesnacont = (mesna - 2000) // ifocycle
            for cycifo in range(0, ifocycle):
                st.write("Ifosfamid 2000mg v 500ml FR iv")
                st.write(f"MESNA {mesnacont} mg v 100ml FR iv/ 4 hodiny")
            st.write(f"Ifosfamid {iforemnant} mg 500ml FR iv")
            st.write("MESNA 800mg v 100ml FR iv/ 4 hodiny")   
        else: 
            mesnacont = (mesna - 1200) // ifocycle
            for cycifo in range(0, ifocycle):
                st.write("Ifosfamid 2000mg v 500ml FR iv")
                st.write(f"MESNA {mesnacont} mg v 100ml FR iv/ 4 hodiny")

# Main function for sarcomas, CNS, and neuroendocrine tumors
def sarcnet(rbodysurf):
    """Táto funkcia rozpisuje chemoterapie a biologickú liečbu sarkómov a CNS a neuroendokrinnych tumorov"""
    chemo_choice = st.selectbox("Vyberte chemoterapiu:", ["Vyberte chemoterapiu", "Ifosfamid/ Epirubicin", "Ifosfamid", "Trabectedin", "Doxorubicin", "Paclitaxel weekly", "CBDCA/ Paclitaxel", "DDP/ Etoposid", "CBDCA/ Etoposid", "Dakarbazin 5 dňový", "Temozolomid", "Lomustine (CCNU)"])

    if chemo_choice == "Ifosfamid/ Epirubicin":
        ChemoIfo(rbodysurf, 3000, True)
    elif chemo_choice == "Ifosfamid":
        ChemoIfo(rbodysurf, 3000, False)
    elif chemo_choice == "Trabectedin":
        Chemo(rbodysurf, "trabectedin.json")
    elif chemo_choice == "Doxorubicin":
        Chemo(rbodysurf, "doxorubicin.json")
    elif chemo_choice == "Paclitaxel weekly":
        Chemo(rbodysurf, "paclitaxelweekly.json")
    elif chemo_choice == "CBDCA/ Paclitaxel":
        ChemoCBDCA(rbodysurf, "paclitaxel3weekly.json")
    elif chemo_choice == "DDP/ Etoposid":
        ChemoDDP(rbodysurf, "etoposide.json")
    elif chemo_choice == "CBDCA/ Etoposid":
        ChemoCBDCA(rbodysurf, "etoposide.json")
    elif chemo_choice == "Dakarbazin 5 dňový":
        Chemo(rbodysurf, "dacarbazine.json")
    elif chemo_choice == "Temozolomid":
        temozolomide_choice = st.selectbox("Temozolomid je:", ["Vyberte možnosť", "v rámci chemoRAT", "solo 150mg/m2", "solo 200mg/m2"])
        if temozolomide_choice == "v rámci chemoRAT":
            Chemo(rbodysurf, "temozolomideRAT.json")
        elif temozolomide_choice == "solo 150mg/m2":
            Chemo(rbodysurf, "temozolomide150.json")
        elif temozolomide_choice == "solo 200mg/m2":
            Chemo(rbodysurf, "temozolomide200.json")
    elif chemo_choice == "Lomustine (CCNU)":
        Chemo(rbodysurf, "CCNU.json")

# Main input function for weight and height
def main():
    st.title("ChemoThon Sarcoma, CNS and NET SK v2.0")
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
        rbodysurf = bsa(weight, height)
        st.session_state.rbodysurf = rbodysurf

    # Always display the BSA if it has been calculated
    if 'rbodysurf' in st.session_state:
        st.write(f"Telesný povrch je: {st.session_state.rbodysurf} m²")

    # Step 2: Display chemotherapy options if BSA is calculated
    if 'rbodysurf' in st.session_state:
        st.write("Teraz vyberte chemoterapiu:")
        sarcnet(st.session_state.rbodysurf)

if __name__ == "__main__":
    main()