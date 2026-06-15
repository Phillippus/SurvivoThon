import streamlit as st
import json

# Function for calculating BSA (Body Surface Area)
def bsa(weight, height):
    bodysurf = (weight**0.425) * (height**0.725) * 0.007184
    rbodysurf = round(bodysurf, 2)
    return rbodysurf

# Function for chemotherapy with Carboplatin (CBDCA)
def ChemoCBDCA(rbodysurf, chemoType):
    """Táto funkcia slúži pre rozpis chemoterapie obsahujúcu karboplatinu"""
    with open('data/' + chemoType, "r") as chemoFile:
        chemoJson = json.loads(chemoFile.read())

    CrCl = st.number_input("Zadajte hodnotu clearance v ml/min", min_value=1, max_value=250, value=None)
    AUC = st.number_input("Zadajte hodnotu AUC 2-6 (INTERLACE: AUC=2)", min_value=2, max_value=6, value=None)

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

# Function for chemotherapy with Cisplatin
def ChemoCISplatin(rbodysurf, chemoType):
    """Táto funkcia slúži pre rozpis chemoterapie s cisplatinou a paclitaxelom"""
    with open('data/' + chemoType, "r") as chemoFile:
        chemoJson = json.loads(chemoFile.read())

    cisplatin_dose = round(80 * rbodysurf, 2)
    st.write(f"Cisplatina 80 mg/m² ........ {cisplatin_dose} mg D1")
    for i in chemoJson["Chemo"]:
        st.write(f"{i['Name']} {i['Dosage']} {i['DosageMetric']} ..... {round(i['Dosage'] * rbodysurf, 2)} mg D{i['Day']}")

    st.write(f"NC {chemoJson['NC']} . deň")

    st.write("D1 - premedikácia:")
    st.write(chemoJson["Day1"]["Premed"]["Note"])

    st.write("D1 - chemoterapia:")

    # Výpis dávok paclitaxelu
    for x in range(len(chemoJson["Chemo"])):
        st.write(f"{chemoJson['Day1']['Instructions'][x]['Name']} {round(chemoJson['Chemo'][x]['Dosage'] * rbodysurf, 2)} mg {chemoJson['Day1']['Instructions'][x]['Inst']}")

    # Výpis cisplatiny po 50 mg
    remaining = cisplatin_dose
    while remaining > 0:
        part = 50 if remaining >= 50 else round(remaining, 2)
        st.write(f"cisplatina {part} mg v 500 ml Ringerovho roztoku (RR)")
        remaining -= part
    st.write("po dotečení cisplatiny Manitol 10% 250ml iv")

# Function for basic chemotherapy
def Chemo(rbodysurf, chemoType):
    """Táto funkcia rozpisuje jednoduché chemoterapie s priamou úmerou"""
    with open('data/' + chemoType, "r") as chemoFile:
        chemoJson = json.loads(chemoFile.read())

    st.write("Rozpis chemoterapie:")
    for i in chemoJson["Chemo"]:
        st.write(f"{i['Name']} {round(i['Dosage'], 2)} {i['DosageMetric']}......... {round(i['Dosage'] * rbodysurf, 2)} mg D{i['Day']}")

    st.write(f"NC {chemoJson['NC']} . deň")

    Day1 = chemoJson["Day1"]["Instructions"]
    C1 = chemoJson["Chemo"]

    st.write("D1 - premedikácia:")
    st.write(chemoJson["Day1"]["Premed"]["Note"])

    st.write("D1 - chemoterapia:")
    for x in range(len(chemoJson["Chemo"])):
        st.write(f"{Day1[x]['Name']} {round(C1[x]['Dosage'] * rbodysurf, 2)} mg {Day1[x]['Inst']}")

# Function for chemotherapy based on weight (e.g. bevacizumab)
def ChemoWeightBased(weight, chemoType):
    """Táto funkcia rozpisuje chemoterapiu podľa hmotnosti (napr. bevacizumab)"""
    with open('data/' + chemoType, "r") as chemoFile:
        chemoJson = json.loads(chemoFile.read())

    st.write("Rozpis chemoterapie:")
    for i in chemoJson["Chemo"]:
        dose = round(i["Dosage"] * weight, 2)
        st.write(f"{i['Name']} {i['Dosage']} {i['DosageMetric']} .......... {dose} mg D{i['Day']}")

    st.write(f"NC {chemoJson['NC']} . deň")

    st.write("D1 - premedikácia:")
    st.write(chemoJson["Day1"]["Premed"]["Note"] or "žiadna premedikácia")

    st.write("D1 - chemoterapia:")
    for x in range(len(chemoJson["Chemo"])):
        dose = round(chemoJson["Chemo"][x]["Dosage"] * weight, 2)
        st.write(f"{chemoJson['Day1']['Instructions'][x]['Name']} {dose} mg {chemoJson['Day1']['Instructions'][x]['Inst']}")

# Main function for gynecology chemotherapy
def gynecology(rbodysurf):
    """Táto funkcia rozpisuje chemoterapie gynekologických tumorov"""
    chemo_choice = st.selectbox("Akú chemoterapiu chcete podať?", [
        "  ",
        "CBDCA/ paclitaxel",
        "INTERLACE CBDCA/paclitaxel",
        "Cisplatina/ paclitaxel",
        "Topotecan + G-CSF",
        "PEG-doxorubicin",
        "CBDCA/ PEG-doxorubicin",
        "CBDCA/ gemcitabin",
        "Bevacizumab 15 mg/kg"
    ])

    if chemo_choice == "CBDCA/ paclitaxel":
        ChemoCBDCA(rbodysurf, "paclitaxel3weekly.json")
    elif chemo_choice == "INTERLACE CBDCA/paclitaxel":
        ChemoCBDCA(rbodysurf, "paclitaxelweekly.json")
    elif chemo_choice == "Cisplatina/ paclitaxel":
        ChemoCISplatin(rbodysurf, "paclitaxel3weeklyDDP.json")
    elif chemo_choice == "Topotecan + G-CSF":
        Chemo(rbodysurf, "topotecan.json")
    elif chemo_choice == "PEG-doxorubicin":
        Chemo(rbodysurf, "pegdoxo.json")
    elif chemo_choice == "CBDCA/ PEG-doxorubicin":
        ChemoCBDCA(rbodysurf, "PEGdoxo30.json")
    elif chemo_choice == "CBDCA/ gemcitabin":
        ChemoCBDCA(rbodysurf, "gemcitabinCBDCA.json")
    elif chemo_choice == "Bevacizumab 15 mg/kg":
        if 'weight' in st.session_state:
            ChemoWeightBased(st.session_state.weight, "bevacizumab3w15.json")
        else:
            st.error("Najprv zadajte hmotnosť a výšku a stlačte tlačidlo na výpočet telesného povrchu.")

# Main input function for weight and height
def main():
    st.title("        ChemoThon Gynecology v2.1")
    st.write("""
    Program rozpisuje najbežnejšie chemoterapie podľa povrchu alebo hmotnosti.
    Dávky je nutné upraviť podľa aktuálne dostupných balení liečiv.
    Autor nezodpovedá za prípadné škody spôsobené jeho použitím! 
    Pre podanie/ pridanie imunoterapie prejdite na https://immunothon.streamlit.app.
    Pripomienky posielajte na filip.kohutek@fntn.sk
    Program kedykoľvek ukončíte zatvorením okna.
    """)

    # Step 1: Input weight and height
    weight = st.number_input("Zadajte hmotnosť (kg):", min_value=1, max_value=250, value=None)
    height = st.number_input("Zadajte výšku (cm):", min_value=1, max_value=250, value=None)

    if st.button("Vypočítať telesný povrch"):
        rbodysurf = bsa(weight, height)
        st.session_state.rbodysurf = rbodysurf
        st.session_state.weight = weight  # for kg-based regimens like bevacizumab

    # Always display the BSA if it has been calculated
    if 'rbodysurf' in st.session_state:
        st.write(f"Telesný povrch je: {st.session_state.rbodysurf} m²")

    # Step 2: Display chemotherapy options if BSA is calculated
    if 'rbodysurf' in st.session_state:
        st.write("Teraz vyberte chemoterapiu:")
        gynecology(st.session_state.rbodysurf)

if __name__ == "__main__":
    main()



# ===== Zdroje / Sources (pridané 2026-06, aditívne) =====
with st.expander("📚 Zdroje k režimom / Sources"):
    st.markdown("""**Kľúčové referencie – gynekologické nádory**

Guidelines: [ESMO](https://www.esmo.org/guidelines/esmo-clinical-practice-guidelines-gynaecological-cancers) · [NCCN](https://www.nccn.org/guidelines/category_1). Vždy overte podľa aktuálnej verzie guidelines a dostupných balení liečiv. Stav: jún 2026.

- **CBDCA / paklitaxel** — GOG-158 – Ozols et al., J Clin Oncol 2003; ICON3.
- **INTERLACE (indukčná CBDCA/paklitaxel, cervix)** — INTERLACE – McCormack et al., Lancet 2024.
- **Cisplatina / paklitaxel (cervix)** — GOG-240 – Tewari et al., NEJM 2014 (so/bez bevacizumabu).
- **Topotekan + G-CSF** — Topotekan pri relapse ovaria – ten Bokkel Huinink et al., J Clin Oncol 1997.
- **PEG-doxorubicín** — PLD pri rekurentnom ovariu – Gordon et al., J Clin Oncol 2001.
- **CBDCA / PEG-doxorubicín** — CALYPSO – Pujade-Lauraine et al., J Clin Oncol 2010.
- **CBDCA / gemcitabín** — Pfisterer et al., J Clin Oncol 2006 (AGO-OVAR/ICON4-like).
- **Bevacizumab 15 mg/kg** — GOG-218 – Burger et al., NEJM 2011; ICON7 – Perren et al., NEJM 2011.

**Aktuálne štandardy na zváženie (zatiaľ mimo nástroja):**
- PARP inhibítory v udržiavaní (olaparib SOLO-1; niraparib PRIMA) – NEJM 2018/2019.
- Dostarlimab / pembrolizumab + chemo pri endometriálnom karcinóme – RUBY / NRG-GY018, NEJM 2023.
- Mirvetuximab soravtansin pri FRα+ platina-rezistentnom ovariu – MIRASOL, NEJM 2023.""")
