import streamlit as st
import json

# Mock functions for chemotherapy (replace these with actual implementations)
def Chemo(rbodysurf, chemoType):
    """Táto funkcia rozpisuje jednoduché chemoterapie s priamou umerou"""
    with open('data/' + chemoType, "r") as chemoFile:
        chemoJson = json.loads(chemoFile.read())

    st.write(f"Chemotherapy type: {chemoType}")
    for i in chemoJson["Chemo"]:
        st.write(f"{i['Name']}  {round(i['Dosage'], 2)} {i['DosageMetric']} .......... {round(i['Dosage'] * rbodysurf, 2)} mg D {i['Day']}")

    st.write(f"NC {chemoJson['NC']} . deň")

    Day1 = chemoJson["Day1"]["Instructions"]
    C1 = chemoJson["Chemo"]

    st.write("D1")
    st.write(chemoJson["Day1"]["Premed"]["Note"])

    for x in range(len(chemoJson["Chemo"])):
        st.write(f"{Day1[x]['Name']} {round(C1[x]['Dosage'] * rbodysurf, 2)} mg {Day1[x]['Inst']}")

def ChemoDDP(rbodysurf, chemoType):
    """Táto funkcia slúži pre chemoterapie s DDP"""
    with open('data/' + chemoType, "r") as chemoFile:
        chemoJson = json.loads(chemoFile.read())

    st.write(f"DDP 80mg/m2 ................ {80 * rbodysurf} mg  D1")
    for i in chemoJson["Chemo"]:
        st.write(f"{i['Name']}  {i['Dosage']} {i['DosageMetric']} ..... {round(i['Dosage'] * rbodysurf, 2)} mg D {i['Day']}")

    st.write(f"NC {chemoJson['NC']} . deň")

    st.write("D1")
    st.write(f"1. {chemoJson['Day1']['Premed']['Note']}")

    a = round(80 * rbodysurf, 2)
    b = a // 50
    c = a % 50
    rng = int(b)

    for ordo in range(2, rng + 2):
        st.write(f"{ordo}. Cisplatina 50mg v 500ml RR iv")
    st.write(f"{ordo + 1}. Cisplatina {int(c)} mg v 500ml RR iv")
    st.write(f"{ordo + 2}. Manitol 10% 250ml iv")

    Day1 = chemoJson["Day1"]["Instructions"]
    C1 = chemoJson["Chemo"]

    for x in range(len(chemoJson["Chemo"])):
        st.write(f"{ordo + 2}. {Day1[x]['Name']} {round(C1[x]['Dosage'] * rbodysurf, 2)} mg {Day1[x]['Inst']}")

def ChemoCBDCA(rbodysurf, chemoType):
    """Táto funkcia slúži pre rozpis chemoterapie obsahujúcu karboplatinu"""
    with open('data/' + chemoType, "r") as chemoFile:
        chemoJson = json.loads(chemoFile.read())

    CrCl = st.number_input("Zadajte hodnotu clearance v ml/min", min_value=1, max_value=250, value=None, step=1)
    AUC = st.number_input("Zadajte hodnotu AUC 2-6", min_value=2, max_value=6, value=None, step=1)

    if CrCl is not None and AUC is not None:
        st.write(f"CBDCA AUC {AUC} ............ {(CrCl + 25) * AUC} mg  D1")
        for i in chemoJson["Chemo"]:
            st.write(f"{i['Name']}  {i['Dosage']} {i['DosageMetric']} ..... {i['Dosage'] * rbodysurf} mg D {i['Day']}")

        st.write(f"NC {chemoJson['NC']} . deň")

        st.write("D1")
        st.write(chemoJson["Day1"]["Premed"]["Note"])
        st.write(f"CBDCA {(CrCl + 25) * AUC} mg v 500ml FR iv")
        for x in range(len(chemoJson["Chemo"])):
            st.write(f"{chemoJson['Day1']['Instructions'][x]['Name']} {round(chemoJson['Chemo'][x]['Dosage'] * rbodysurf, 2)} mg {chemoJson['Day1']['Instructions'][x]['Inst']}")
    else:
        st.write("Please enter valid values for both creatinine clearance (CrCl) and AUC.")

def lung(rbodysurf):
    """Tato funkcia ponuka chemoterapie pouzivane v liecbe karcinomu pluc"""
    chemo_options = [
        "Vyberte chemoterapiu", 
        "CBDCA + paclitaxel", 
        "CBDCA + pemetrexed", 
        "DDP + gemcitabine", 
        "CBDCA + gemcitabine", 
        "DDP + etoposide", 
        "Topotecan + G-CSF"
    ]
    lng = st.selectbox("Vyberte chemoterapiu, ktorú chcete podať:", chemo_options)

    if lng != chemo_options[0]:  # Ensure that the default "Vyberte chemoterapiu" is not selected
        if lng == "CBDCA + paclitaxel":
            ChemoCBDCA(rbodysurf, "paclitaxel3weekly.json")
        elif lng == "CBDCA + pemetrexed":
            ChemoCBDCA(rbodysurf, "pemetrexed.json")
        elif lng == "DDP + gemcitabine":
            ChemoDDP(rbodysurf, "gemcitabinDDP.json")
        elif lng == "CBDCA + gemcitabine":
            ChemoCBDCA(rbodysurf, "gemcitabinCBDCA.json")
        elif lng == "DDP + etoposide":
            ChemoDDP(rbodysurf, "etoposide.json")
        elif lng == "Topotecan + G-CSF":
            Chemo(rbodysurf, "topotecan.json")

def bsa(weight, height):
    bodysurf = (weight**0.425) * (height**0.725) * 0.007184
    rbodysurf = round(bodysurf, 2)
    return rbodysurf

def main():
    st.title("          ChemoThon- LungSK v 2.0")
    st.write("""
    Program rozpisuje najbežnejšie chemoterapie podľa povrchu alebo hmotnosti.
    Dávky je nutné upraviť podľa aktuálne dostupných balení liečiv.
    Autor nezodpovedá za prípadné škody spôsobené jeho použitím!
    Pripomienky posielajte na filip.kohutek@fntn.sk
    Program kedykoľvek ukončíte zatvorením okna.
    """)

    # Step 1: Input weight and height
    w = st.number_input("Zadajte hmotnosť (kg):", min_value=1, max_value=250, value=70)
    h = st.number_input("Zadajte výšku (cm):", min_value=1, max_value=250, value=170)

    if st.button("Vypočítať telesný povrch"):
        rbodysurf = bsa(w, h)
        st.session_state.rbodysurf = rbodysurf
        st.session_state.show_chemo = True

    if "rbodysurf" in st.session_state:
        st.write(f"Telesný povrch je: {st.session_state.rbodysurf} m²")

    # Step 2: Select chemotherapy
    if st.session_state.get("show_chemo", False):
        lung(st.session_state.rbodysurf)

if __name__ == "__main__":
    main()