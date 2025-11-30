import streamlit as st
import json

# Function for basic chemotherapy
def Chemo(rbodysurf, chemoType):
    """Táto funkcia rozpisuje jednoduché chemoterapie s priamou úmerou"""
    
    if chemoType is None:
        
        return
    
    try:
        with open('data/' + chemoType, "r") as chemoFile:
            chemoJson = json.loads(chemoFile.read())
    except FileNotFoundError:
        st.error(f"File not found: data/{chemoType}")
        return
    except json.JSONDecodeError:
        st.error(f"Error parsing JSON file: {chemoType}")
        return
    
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

# Function for chemotherapy with carboplatin (CBDCA)
def ChemoCBDCA(rbodysurf, chemoType):
    """Táto funkcia slúži pre rozpis chemoterapie obsahujúcu karboplatinu"""
    try:
        with open('data/' + chemoType, "r") as chemoFile:
            chemoJson = json.loads(chemoFile.read())
    except FileNotFoundError:
        st.error(f"File not found: data/{chemoType}")
        return
    except json.JSONDecodeError:
        st.error(f"Error parsing JSON file: {chemoType}")
        return

    CrCl = st.number_input("Zadajte hodnotu clearance v ml/min", min_value=1, max_value=250, value=None)
    AUC = st.number_input("Zadajte hodnotu AUC 2-6 (CROSS režim: AUC=2)", min_value=2, max_value=6, value=None)

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

# Function for chemotherapy with 5FU
def Chemo5FU(rbodysurf, chemoType):
    """Táto funkcia rozpisuje chemoterapie s kontinuálnym 5FU"""
    try:
        with open('data/' + chemoType, "r") as chemoFile:
            chemoJson = json.loads(chemoFile.read())
    except FileNotFoundError:
        st.error(f"File not found: data/{chemoType}")
        return
    except json.JSONDecodeError:
        st.error(f"Error parsing JSON file: {chemoType}")
        return
    
    st.write("Rozpis chemoterapie:")
    for i in chemoJson["Chemo"]:
        st.write(f"{i['Name']}  {round(i['Dosage'], 2)} {i['DosageMetric']}......... {round(i['Dosage'] * rbodysurf, 2)} mg D{i['Day']}")
    
    if chemoType == "FLOT.json":
        dos5FU = 2600
        dos15FU = 2600
        day5FU = "24 hodín"
        day15FU = "24 hodín"
    elif chemoType == "mtc5FU.json":
        dos5FU = 1000
        dos15FU = 1000
        day5FU = "D1-4"
        day15FU = "24 hodín"
    else:
        dos5FU = 2400
        dos15FU = 1200
        day5FU = "48 hodín"
        day15FU = "24 hodín"
        
    st.write(f"5-fluoruracil {dos5FU} mg/m2...... {rbodysurf * dos5FU} mg/ {day5FU}")
    st.write(f"NC {chemoJson['NC']} . deň")
    
    Day1 = chemoJson["Day1"]["Instructions"]
    C1 = chemoJson["Chemo"]
    
    st.write("D1 - premedikácia:")
    st.write(chemoJson["Day1"]["Premed"]["Note"])
    
    st.write("D1 - chemoterapia:")
    for x in range(len(chemoJson["Chemo"])):
        st.write(f"{Day1[x]['Name']} {round(C1[x]['Dosage'] * rbodysurf, 2)} mg {Day1[x]['Inst']}")
    
    st.write(f"5-fluoruracil {rbodysurf * dos15FU} mg/kivi {day15FU}")

# Function for platinum + 5FU chemotherapy
def platinum5FU(rbodysurf):
    """Táto chemoterapia slúži na rozpis chemoterapie s platinou a 5FU"""
    
    a = 80 * rbodysurf
    b = a // 50
    c = a % 50
    rng = int(b)
    
    # Updated selectbox with no default selection
    whichPt = st.selectbox("Ktorá platina?", ["Vyberte platinu", "Cisplatina", "Karboplatina"])
    
    if whichPt == "Cisplatina":
        st.write(f"DDP 80mg/m2................ {80 * rbodysurf} mg  D1")
        st.write(f"5-fluoruracil 1000mg/m2......... {1000 * rbodysurf} mg D1-D4")
        st.write("""
                                             NC 21. deň
                                                          
                                             D1
        """)
        st.write("1. Dexametazón 8mg iv, Pantoprazol 40 mg p.o., Ondansetron 8mg v 250ml FR iv")
        for ordo in range(2, rng + 2):
            st.write(f"{ordo}. Cisplatina 50mg v 500ml RR iv")
        st.write(f"{ordo}. Cisplatina {int(c)} mg v 500ml RR iv")
        st.write(f"{ordo + 1}. Manitol 10% 250ml iv")
        st.write(f"{ordo + 2}. 5-fluoruracil {rbodysurf * 1000} mg na 24 hodín/kivi")
        
    elif whichPt == "Karboplatina":
        CrCl = st.number_input("Zadajte hodnotu clearance v ml/min", min_value=1, max_value=250, value=None)
        AUC = st.number_input("Zadajte hodnotu AUC 2-6", min_value=2, max_value=6, value=None)
        
        if CrCl is not None and AUC is not None:
            st.write(f"CBDCA AUC {AUC}............ {(CrCl + 25) * AUC} mg  D1")
            st.write(f"5-fluoruracil 1000mg/m2.............. {rbodysurf * 1000} mg  D1-D4")     
            st.write("""
                                                 NC 21. deň
                                                              
                                                 D1
            """)
            st.write("Dexametazón 8mg iv, Pantoprazol 40 mg p.o., Ondansetron 8mg v 250ml FR iv")
            st.write(f"CBDCA AUC {AUC}............ {(CrCl + 25) * AUC} mg  D1") 
            st.write(f"5-fluoruracil {rbodysurf * 1000} mg na 24 hodín/kivi")
        else:
            st.error("Prosím, zadajte platnú hodnotu clearance (CrCl) a AUC pred pokračovaním.")
    else:
        st.warning("Prosím, vyberte platinu pre pokračovanie.")

# Main function for gastrointestinal malignancies
def gastrointestinal(rbodysurf):
    """Táto funkcia rozpisuje chemoterapie používané v liečbe gastrointestinálnych malignít"""

    chemo_options = {
        " ": None,
        "Pt/5-FU": platinum5FU,
        "FLOT": "FLOT.json",
        "EOX": "EOX.json",
        "Paclitaxel weekly": "paclitaxelweekly.json",
        "CROSS režim": "paclitaxel50weekly.json",
        "FOLFIRINOX": "FOLFIRINOX.json",
        "Gemcitabin/ Capecitabine": "gemcap.json",
        "Gemcitabin/ Nab-Paclitaxel": "gemnabpcl.json",
        "NALIRI/ 5-FU": "peglipiri5FU.json",
        "NALIRIFOX": "NALIRIFOX.json",
        "Gemcitabin": "gemcitabin4w.json",
        "Mitomycin/ 5-FU": "mtc5FU.json"
    }
    
    chemo_choice = st.selectbox("Vyberte chemoterapiu:", list(chemo_options.keys()))

    if chemo_choice and chemo_choice != "Vyberte chemoterapiu":
        if chemo_choice == "Pt/5-FU":
            platinum5FU(rbodysurf)
        else:
            chemo_file = chemo_options[chemo_choice]
            if chemo_choice in ["FLOT", "FOLFIRINOX", "NALIRI/ 5-FU", "NALIRIFOX", "Mitomycin/ 5-FU"]:
                Chemo5FU(rbodysurf, chemo_file)
            elif chemo_choice in ["CROSS režim"]:
                ChemoCBDCA(rbodysurf, chemo_file)
            else:
                Chemo(rbodysurf, chemo_file)

# Function to calculate Body Surface Area (BSA)
def bsa(weight, height):
    bodysurf = (weight**0.425) * (height**0.725) * 0.007184
    rbodysurf = round(bodysurf, 2)
    return rbodysurf

# Main input function for weight and height
def main():
    st.title("ChemoThon - GastrointestinalSK (excl. CrC) v2.0")
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
        st.session_state.show_chemo_selection = True

    # Display the BSA if it's already calculated, and only once
    if 'rbodysurf' in st.session_state:
        st.write(f"Telesný povrch je: {st.session_state.rbodysurf} m²")

    # Step 2: Chemotherapy selection if BSA is calculated
    if st.session_state.get("show_chemo_selection", False):
        st.write("Teraz vyberte chemoterapiu:")
        gastrointestinal(st.session_state.rbodysurf)

if __name__ == "__main__":
    main()
       